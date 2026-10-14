from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from .models import Category, Product, ProductVariant, Cart, CartItem, Order, OrderItem
from apps.core.emails import send_order_confirmation_email

def _get_or_create_cart(request):
    """
    Helper to get the current cart from user or session.
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def catalog_view(request):
    """
    Product storefront with live HTMX filtering and category pills.
    """
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_in_stock=True)

    category_slug = request.GET.get('category')
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'featured')

    selected_category = None
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug).first()
        if selected_category:
            products = products.filter(category=selected_category)

    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if sort_by == 'price_low':
        products = products.order_by('base_price')
    elif sort_by == 'price_high':
        products = products.order_by('-base_price')
    else:
        products = products.order_by('-is_featured', '-created_at')

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'sort_by': sort_by,
        'cart': _get_or_create_cart(request),
    }

    if request.headers.get('HX-Request'):
        return render(request, 'store/partials/product_grid.html', context)

    return render(request, 'store/catalog.html', context)


def product_detail_view(request, slug):
    """
    Product detail page with variants and add-to-cart controls.
    """
    product = get_object_or_404(Product, slug=slug)
    variants = product.variants.all()
    cart = _get_or_create_cart(request)

    context = {
        'product': product,
        'variants': variants,
        'cart': cart,
    }
    return render(request, 'store/product_detail.html', context)


def cart_drawer_view(request):
    """
    Returns the slide-over cart drawer partial for HTMX.
    """
    cart = _get_or_create_cart(request)
    return render(request, 'store/partials/cart_drawer_content.html', {'cart': cart})


def add_to_cart_view(request, product_id):
    """
    HTMX endpoint to add product/variant to cart and return drawer.
    """
    cart = _get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))

    variant = None
    if variant_id:
        variant = ProductVariant.objects.filter(id=variant_id, product=product).first()

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    response = render(request, 'store/partials/cart_drawer_content.html', {'cart': cart})
    # HTMX trigger to update the navbar cart badge counter
    response['HX-Trigger'] = 'cartUpdated'
    return response


def buy_now_view(request, product_id):
    """
    Direct 'Buy Now' flow: adds item to cart and immediately redirects to checkout.
    """
    cart = _get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    variant_id = request.POST.get('variant_id') or request.GET.get('variant_id')
    try:
        quantity = int(request.POST.get('quantity', request.GET.get('quantity', 1)))
    except (ValueError, TypeError):
        quantity = 1

    variant = None
    if variant_id:
        variant = ProductVariant.objects.filter(id=variant_id, product=product).first()

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect('store:checkout')


def update_cart_item_view(request, item_id):
    """
    HTMX endpoint to adjust item quantity or delete from cart.
    """
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    action = request.POST.get('action')

    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    elif action == 'remove':
        item.delete()

    response = render(request, 'store/partials/cart_drawer_content.html', {'cart': cart})
    response['HX-Trigger'] = 'cartUpdated'
    return response


@login_required
def checkout_view(request):
    """
    Customer checkout page and order creation with email dispatch.
    """
    cart = _get_or_create_cart(request)

    if cart.items.count() == 0:
        messages.warning(request, "Your cart is currently empty.")
        return redirect('store:catalog')

    if request.method == 'POST':
        recipient_name = request.POST.get('recipient_name')
        recipient_phone = request.POST.get('recipient_phone')
        shipping_address = request.POST.get('shipping_address')
        delivery_method = request.POST.get('delivery_method', Order.DeliveryMethod.DOOR_DELIVERY)

        shipping_fee = Decimal('2500.00') if delivery_method == Order.DeliveryMethod.DOOR_DELIVERY else Decimal('0.00')
        subtotal = cart.total_amount
        total_amount = subtotal + shipping_fee

        order = Order.objects.create(
            customer=request.user,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            shipping_address=shipping_address,
            delivery_method=delivery_method,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
            status=Order.Status.CONFIRMED,
            payment_status='PAID_DEMO'
        )

        for item in cart.items.all():
            variant_title = item.variant.name if item.variant else ''
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_title=item.product.title,
                variant_title=variant_title,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal
            )

        # Clear cart
        cart.items.all().delete()

        # Send order confirmation email via Resend & Celery
        send_order_confirmation_email(order)

        messages.success(request, f"Order #{order.order_number} confirmed! A receipt was sent to {request.user.email}.")
        return redirect('accounts:dashboard')

    context = {
        'cart': cart,
        'user': request.user,
    }
    return render(request, 'store/checkout.html', context)
