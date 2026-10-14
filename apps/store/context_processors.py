from .models import Cart

def cart_context(request):
    """
    Exposes the active shopping cart and cart_item_count globally across all templates.
    Avoids creating empty carts for passive visitors on GET requests.
    """
    cart = None
    item_count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        elif request.session.session_key:
            cart = Cart.objects.filter(session_key=request.session.session_key).first()

        if cart:
            item_count = cart.item_count
    except Exception:
        pass

    return {
        'cart': cart,
        'cart_item_count': item_count,
    }
