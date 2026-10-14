from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import StaffActionLog
from .forms import RouteForm, CreateModeratorForm, ShipmentUpdateForm
from apps.accounts.models import CustomUser, ModeratorProfile
from apps.logistics.models import Route, Shipment, ShipmentCheckpoint
from apps.store.models import Order, Product
from apps.core.emails import send_shipment_status_update_email

def is_moderator_check(user):
    return user.is_authenticated and (user.is_moderator or user.is_superuser)

def is_admin_check(user):
    return user.is_authenticated and (user.is_admin_user or user.is_superuser)


@login_required
@user_passes_test(is_moderator_check, login_url='accounts:login')
def dashboard_view(request):
    """
    Staff / Moderator overview hub.
    """
    total_shipments = Shipment.objects.count()
    active_shipments = Shipment.objects.exclude(status=Shipment.Status.DELIVERED).count()
    total_orders = Order.objects.count()
    total_routes = Route.objects.count()
    recent_shipments = Shipment.objects.select_related('customer', 'route')[:8]
    recent_orders = Order.objects.select_related('customer')[:8]
    moderators_count = CustomUser.objects.filter(role=CustomUser.Role.MODERATOR).count()

    context = {
        'total_shipments': total_shipments,
        'active_shipments': active_shipments,
        'total_orders': total_orders,
        'total_routes': total_routes,
        'recent_shipments': recent_shipments,
        'recent_orders': recent_orders,
        'moderators_count': moderators_count,
    }
    return render(request, 'moderation/dashboard.html', context)


@login_required
@user_passes_test(is_moderator_check, login_url='accounts:login')
def routes_list_view(request):
    """
    Manage dynamic shipping routes.
    """
    routes = Route.objects.all().order_by('-created_at')
    return render(request, 'moderation/routes_list.html', {'routes': routes})


@login_required
@user_passes_test(is_moderator_check, login_url='accounts:login')
def route_create_view(request):
    """
    Create a new dynamic shipping route (Admin / Moderator).
    """
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save()
            StaffActionLog.objects.create(
                staff_user=request.user,
                action_type="ROUTE_CREATED",
                target_reference=str(route),
                details=f"Created route {route.origin_city} -> {route.destination_city} at ${route.rate_per_kg}/kg"
            )
            messages.success(request, f"New shipping route '{route}' added successfully!")
            return redirect('moderation:routes_list')
    else:
        form = RouteForm()

    return render(request, 'moderation/route_form.html', {'form': form, 'title': 'Add New Shipping Route'})


@login_required
@user_passes_test(is_moderator_check, login_url='accounts:login')
def route_edit_view(request, route_id):
    """
    Edit an existing shipping route.
    """
    route = get_object_or_404(Route, id=route_id)
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            StaffActionLog.objects.create(
                staff_user=request.user,
                action_type="ROUTE_UPDATED",
                target_reference=str(route),
                details=f"Updated rates and settings for {route}"
            )
            messages.success(request, f"Route '{route}' updated successfully!")
            return redirect('moderation:routes_list')
    else:
        form = RouteForm(instance=route)

    return render(request, 'moderation/route_form.html', {'form': form, 'title': f'Edit Route: {route}'})


@login_required
@user_passes_test(is_admin_check, login_url='accounts:login')
def create_moderator_view(request):
    """
    Admin tool to provision new staff & moderator accounts.
    """
    if request.method == 'POST':
        form = CreateModeratorForm(request.POST)
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
                action_type="MODERATOR_CREATED",
                target_reference=f"Staff: {user.email}",
                details=f"Provisioned moderator {user.full_name} in {form.cleaned_data['department']}"
            )

            messages.success(request, f"Moderator account for {user.full_name} ({user.email}) created successfully!")
            return redirect('moderation:moderator_list')
    else:
        form = CreateModeratorForm()

    return render(request, 'moderation/create_moderator.html', {'form': form})


@login_required
@user_passes_test(is_admin_check, login_url='accounts:login')
def moderator_list_view(request):
    """
    List all staff and moderators.
    """
    moderators = CustomUser.objects.filter(role=CustomUser.Role.MODERATOR).select_related('moderator_profile')
    return render(request, 'moderation/moderator_list.html', {'moderators': moderators})


@login_required
@user_passes_test(is_moderator_check, login_url='accounts:login')
def shipments_list_view(request):
    """
    Logistics operations list with fast filter.
    """
    shipments = Shipment.objects.select_related('customer', 'route').order_by('-created_at')
    return render(request, 'moderation/shipments_list.html', {'shipments': shipments})


@login_required
@user_passes_test(is_moderator_check, login_url='accounts:login')
def shipment_update_view(request, shipment_id):
    """
    Update cargo status checkpoint and automatically dispatch notification email.
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
                action_type="SHIPMENT_STATUS_UPDATE",
                target_reference=shipment.tracking_number,
                details=f"Advanced status to {new_status} at {location}"
            )

            # Trigger async customer email via Resend & Celery
            send_shipment_status_update_email(shipment, checkpoint)

            messages.success(request, f"Shipment #{shipment.tracking_number} updated to {checkpoint.get_status_display()}! Notification queued.")
            return redirect('moderation:shipments_list')
    else:
        form = ShipmentUpdateForm(initial={'status': shipment.status})

    return render(request, 'moderation/shipment_update.html', {'form': form, 'shipment': shipment})
