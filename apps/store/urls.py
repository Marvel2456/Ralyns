from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('cart/drawer/', views.cart_drawer_view, name='cart_drawer'),
    path('cart/add/<uuid:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/item/<uuid:item_id>/update/', views.update_cart_item_view, name='update_cart_item'),
    path('checkout/', views.checkout_view, name='checkout'),
]
