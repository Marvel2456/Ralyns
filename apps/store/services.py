from decimal import Decimal
from django.db import transaction
from .models import Cart, CartItem

def merge_session_cart(user, session_key):
    """
    Transfers all items from an anonymous session cart to the authenticated user's cart.
    If the user already has items in their cart, matching products/variants are combined
    (quantities summed), and unique items are reassigned to the user's cart.
    The empty guest cart is cleaned up.
    """
    if not user or not user.is_authenticated or not session_key:
        return None

    guest_cart = Cart.objects.filter(session_key=session_key).exclude(user=user).first()
    if not guest_cart:
        return None

    with transaction.atomic():
        user_cart, _ = Cart.objects.get_or_create(user=user)

        for item in list(guest_cart.items.all()):
            existing_item = CartItem.objects.filter(
                cart=user_cart,
                product=item.product,
                variant=item.variant
            ).first()

            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save(update_fields=['quantity'])
                item.delete()
            else:
                item.cart = user_cart
                item.save(update_fields=['cart'])

        # Delete the guest cart after transferring all items
        guest_cart.delete()

    return user_cart
