from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from .forms import OwnerModeratorForm, OwnerModeratorEditForm, OwnerWarehouseForm, OwnerProductForm
from apps.moderation.forms import RouteForm, ShipmentUpdateForm
from apps.accounts.models import CustomUser, ModeratorProfile
from apps.logistics.models import Route, Warehouse, Shipment, ShipmentCheckpoint
from apps.store.models import Product, Category, Order, OrderItem
from apps.moderation.models import StaffActionLog
from apps.core.emails import send_shipment_status_update_email

def is_owner(user):
    return user.is_authenticated and (user.is_admin_user or user.is_superuser)

owner_guard = user_passes_test(is_owner, login_url='accounts:login')


@login_required
@owner_guard
def dashboard_view(request):
    """
    Executive Owner Dashboard overview with top-level financial & operational KPIs.
    """
    # Logistics metrics
    total_shipments = Shipment.objects.count()
    active_shipments = Shipment.objects.exclude(status=Shipment.Status.DELIVERED).count()
    delivered_shipments = Shipment.objects.filter(status=Shipment.Status.DELIVERED).count()
    logistics_rev = Shipment.objects.filter(payment_status=Shipment.PaymentStatus.PAID).aggregate(Sum('total_cost'))['total_cost__sum'] or Decimal('0.00')

    # Store metrics
    total_orders = Order.objects.count()
    store_rev = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    total_products = Product.objects.count()

    # User & Staff metrics
    total_customers = CustomUser.objects.filter(role=CustomUser.Role.CUSTOMER).count()
    total_moderators = CustomUser.objects.filter(role=CustomUser.Role.MODERATOR).count()
    total_routes = Route.objects.count()
    total_warehouses = Warehouse.objects.count()

    recent_shipments = Shipment.objects.select_related('customer', 'route')[:6]
    recent_orders = Order.objects.select_related('customer')[:6]
    recent_logs = StaffActionLog.objects.select_related('staff_user')[:8]

    context = {
        'total_shipments': total_shipments,
        'active_shipments': active_shipments,
        'delivered_shipments': delivered_shipments,
        'logistics_rev': logistics_rev,
        'total_orders': total_orders,
        'store_rev': store_rev,
        'total_products': total_products,
        'total_customers': total_customers,
        'total_moderators': total_moderators,
        'total_routes': total_routes,
        'total_warehouses': total_warehouses,
        'recent_shipments': recent_shipments,
        'recent_orders': recent_orders,
        'recent_logs': recent_logs,
    }
    return render(request, 'owner/dashboard.html', context)


@login_required
@owner_guard
def moderators_view(request):
    """
    Owner management of operations moderators and staff permissions.
    """
    moderators = CustomUser.objects.filter(role=CustomUser.Role.MODERATOR).select_related('moderator_profile')

    if request.method == 'POST':
        form = OwnerModeratorForm(request.POST)
        if form.is_valid():
            user = CustomUser.objects.create_user(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                full_name=form.cleaned_data['full_name'],
                phone=form.cleaned_data.get('phone', ''),
                role=CustomUser.Role.MODERATOR,
                is_staff=True,
                is_email_verified=True
            )

            ModeratorProfile.objects.create(
                user=user,
                department=form.cleaned_data['department'],
                can_manage_routes=form.cleaned_data.get('can_manage_routes', True),
                can_update_shipments=form.cleaned_data.get('can_update_shipments', True),
                can_manage_products=form.cleaned_data.get('can_manage_products', True),
                can_manage_orders=form.cleaned_data.get('can_manage_orders', True),
            )

            StaffActionLog.objects.create(
                staff_user=request.user,
                action_type="OWNER_CREATED_MODERATOR",
                target_reference=f"Staff: {user.email}",
                details=f"Owner created moderator {user.full_name} ({form.cleaned_data['department']})"
            )

            messages.success(request, f"Moderator {user.full_name} created successfully!")
            return redirect('owner:moderators')
    else:
        form = OwnerModeratorForm()

    return render(request, 'owner/moderators.html', {'moderators': moderators, 'form': form})


@login_required
@owner_guard
def toggle_moderator_status(request, user_id):
    """
    Deactivate or reactivate a moderator account.
    """
    user = get_object_or_404(CustomUser, id=user_id, role=CustomUser.Role.MODERATOR)
    user.is_active = not user.is_active
    user.save()

    status_str = "activated" if user.is_active else "deactivated"
    StaffActionLog.objects.create(
        staff_user=request.user,
        action_type="OWNER_TOGGLE_MODERATOR",
        target_reference=f"Staff: {user.email}",
        details=f"Moderator {user.full_name} was {status_str} by Owner"
    )

    messages.info(request, f"Moderator account for {user.full_name} has been {status_str}.")
    return redirect('owner:moderators')


@login_required
@owner_guard
def moderator_edit_view(request, user_id):
    """
    Owner editing of moderator account credentials, contact, and granular operational permissions.
    """
    moderator_user = get_object_or_404(CustomUser, id=user_id, role=CustomUser.Role.MODERATOR)
    # Ensure profile exists
    ModeratorProfile.objects.get_or_create(user=moderator_user)

    if request.method == 'POST':
        form = OwnerModeratorEditForm(request.POST, user_instance=moderator_user)
        if form.is_valid():
            form.save()
            dept_name = moderator_user.moderator_profile.get_department_display() if hasattr(moderator_user, 'moderator_profile') else 'Staff'
            StaffActionLog.objects.create(
                staff_user=request.user,
                action_type="OWNER_UPDATED_MODERATOR",
                target_reference=f"Staff: {moderator_user.email}",
                details=f"Owner modified account and permissions for moderator {moderator_user.full_name} ({dept_name})"
            )
            messages.success(request, f"Moderator {moderator_user.full_name} ({moderator_user.email}) updated successfully!")
            return redirect('owner:moderators')
    else:
        form = OwnerModeratorEditForm(user_instance=moderator_user)

    context = {
        'form': form,
        'moderator_user': moderator_user,
        'title': f"Edit Moderator: {moderator_user.full_name}",
    }
    return render(request, 'owner/moderator_form.html', context)


@login_required
@owner_guard
def routes_view(request):
    """
    Manage dynamic shipping corridors and rates.
    """
    routes = Route.objects.all().order_by('-created_at')
    return render(request, 'owner/routes.html', {'routes': routes})


@login_required
@owner_guard
def route_create_view(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save()
            StaffActionLog.objects.create(
                staff_user=request.user,
                action_type="OWNER_CREATED_ROUTE",
                target_reference=str(route),
                details=f"Owner created route {route.origin_city} -> {route.destination_city}"
            )
            messages.success(request, f"Route {route} created successfully!")
            return redirect('owner:routes')
    else:
        form = RouteForm()

    return render(request, 'owner/route_form.html', {'form': form, 'title': 'Create New Shipping Corridor'})


@login_required
@owner_guard
def route_edit_view(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            StaffActionLog.objects.create(
                staff_user=request.user,
                action_type="OWNER_UPDATED_ROUTE",
                target_reference=str(route),
                details=f"Owner modified route parameters for {route}"
            )
            messages.success(request, f"Route {route} updated!")
            return redirect('owner:routes')
    else:
        form = RouteForm(instance=route)

    return render(request, 'owner/route_form.html', {'form': form, 'title': f'Edit Route: {route}'})


@login_required
@owner_guard
def warehouses_view(request):
    """
    Manage global receiving hubs.
    """
    warehouses = Warehouse.objects.all().order_by('country', 'city')
    if request.method == 'POST':
        form = OwnerWarehouseForm(request.POST)
        if form.is_valid():
            wh = form.save()
            messages.success(request, f"Warehouse hub '{wh.name}' added successfully!")
            return redirect('owner:warehouses')
    else:
        form = OwnerWarehouseForm()

    return render(request, 'owner/warehouses.html', {'warehouses': warehouses, 'form': form})


@login_required
@owner_guard
def warehouse_edit_view(request, warehouse_id):
    wh = get_object_or_404(Warehouse, id=warehouse_id)
    if request.method == 'POST':
        form = OwnerWarehouseForm(request.POST, instance=wh)
        if form.is_valid():
            form.save()
            messages.success(request, f"Warehouse '{wh.name}' updated successfully!")
            return redirect('owner:warehouses')
    else:
        form = OwnerWarehouseForm(instance=wh)

    return render(request, 'owner/warehouse_form.html', {'form': form, 'warehouse': wh})


@login_required
@owner_guard
def shipments_view(request):
    """
    Full oversight of all waybill cargo across the platform.
    """
    search_q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    shipments = Shipment.objects.select_related('customer', 'route', 'origin_warehouse').order_by('-created_at')

    if search_q:
        shipments = shipments.filter(
            Q(tracking_number__icontains=search_q) |
            Q(customer__full_name__icontains=search_q) |
            Q(customer__customer_code__icontains=search_q) |
            Q(receiver_name__icontains=search_q)
        )

    if status_filter:
        shipments = shipments.filter(status=status_filter)

    return render(request, 'owner/shipments.html', {
        'shipments': shipments,
        'search_q': search_q,
        'status_filter': status_filter,
        'status_choices': Shipment.Status.choices,
    })


@login_required
@owner_guard
def shipment_update_view(request, shipment_id):
    """
    Owner status update and milestone checkpoint generator.
    """
    shipment = get_object_or_404(Shipment, id=shipment_id)
    if request.method == 'POST':
        form = ShipmentUpdateForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            location = form.cleaned_data['location']
            remarks = form.cleaned_data.get('remarks', '')

            shipment.status = new_status
            shipment.save()

            checkpoint = ShipmentCheckpoint.objects.create(
                shipment=shipment,
                status=new_status,
                location=location,
                remarks=remarks,
                created_by=request.user
            )

            StaffActionLog.objects.create(
                staff_user=request.user,
                action_type="OWNER_SHIPMENT_UPDATE",
                target_reference=shipment.tracking_number,
                details=f"Owner advanced shipment to {new_status} at {location}"
            )

            # Dispatch notification email via Resend & Celery
            send_shipment_status_update_email(shipment, checkpoint)

            messages.success(request, f"Shipment #{shipment.tracking_number} updated to {checkpoint.get_status_display()}!")
            return redirect('owner:shipments')
    else:
        form = ShipmentUpdateForm(initial={'status': shipment.status})

    return render(request, 'owner/shipment_update.html', {'form': form, 'shipment': shipment})


@login_required
@owner_guard
def products_view(request):
    """
    Manage e-commerce products with automated WebP conversion & Cloudinary uploads.
    """
    products = Product.objects.select_related('category').order_by('-created_at')

    if request.method == 'POST':
        form = OwnerProductForm(request.POST, request.FILES)
        if form.is_valid():
            prod = form.save()
            messages.success(request, f"Product '{prod.title}' created and optimized!")
            return redirect('owner:products')
    else:
        form = OwnerProductForm()

    return render(request, 'owner/products.html', {'products': products, 'form': form})


@login_required
@owner_guard
def product_edit_view(request, product_id):
    prod = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = OwnerProductForm(request.POST, request.FILES, instance=prod)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{prod.title}' updated successfully!")
            return redirect('owner:products')
    else:
        form = OwnerProductForm(instance=prod)

    return render(request, 'owner/product_form.html', {'form': form, 'product': prod})


@login_required
@owner_guard
def orders_view(request):
    """
    Manage store orders and fulfillment.
    """
    orders = Order.objects.select_related('customer').prefetch_related('items').order_by('-created_at')
    return render(request, 'owner/orders.html', {'orders': orders})


@login_required
@owner_guard
def order_update_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.Status.choices):
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.order_number} status updated to {order.get_status_display()}!")
    return redirect('owner:orders')


@login_required
@owner_guard
def customers_view(request):
    """
    Customer accounts directory with unique cargo mailbox codes.
    """
    customers = CustomUser.objects.filter(role=CustomUser.Role.CUSTOMER).annotate(
        shipments_count=Count('shipments'),
        orders_count=Count('orders')
    ).order_by('-created_at')

    return render(request, 'owner/customers.html', {'customers': customers})


@login_required
@owner_guard
def audit_logs_view(request):
    """
    Audit log of all actions taken by moderators and admins.
    """
    logs = StaffActionLog.objects.select_related('staff_user').order_by('-created_at')[:100]
    return render(request, 'owner/audit_logs.html', {'logs': logs})
