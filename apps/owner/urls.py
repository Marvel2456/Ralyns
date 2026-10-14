from django.urls import path
from . import views

app_name = 'owner'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('moderators/', views.moderators_view, name='moderators'),
    path('moderators/<uuid:user_id>/edit/', views.moderator_edit_view, name='moderator_edit'),
    path('moderators/<uuid:user_id>/toggle/', views.toggle_moderator_status, name='toggle_moderator'),
    path('routes/', views.routes_view, name='routes'),
    path('routes/new/', views.route_create_view, name='route_create'),
    path('routes/<uuid:route_id>/edit/', views.route_edit_view, name='route_edit'),
    path('warehouses/', views.warehouses_view, name='warehouses'),
    path('warehouses/<uuid:warehouse_id>/edit/', views.warehouse_edit_view, name='warehouse_edit'),
    path('shipments/', views.shipments_view, name='shipments'),
    path('shipments/<uuid:shipment_id>/update/', views.shipment_update_view, name='shipment_update'),
    path('products/', views.products_view, name='products'),
    path('products/<uuid:product_id>/edit/', views.product_edit_view, name='product_edit'),
    path('orders/', views.orders_view, name='orders'),
    path('orders/<uuid:order_id>/status/', views.order_update_status, name='order_update_status'),
    path('customers/', views.customers_view, name='customers'),
    path('audit-logs/', views.audit_logs_view, name='audit_logs'),
]
