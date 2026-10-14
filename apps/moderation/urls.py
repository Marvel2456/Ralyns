from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('routes/', views.routes_list_view, name='routes_list'),
    path('routes/new/', views.route_create_view, name='route_create'),
    path('routes/<uuid:route_id>/edit/', views.route_edit_view, name='route_edit'),
    path('moderators/', views.moderator_list_view, name='moderator_list'),
    path('moderators/new/', views.create_moderator_view, name='create_moderator'),
    path('shipments/', views.shipments_list_view, name='shipments_list'),
    path('shipments/<uuid:shipment_id>/update/', views.shipment_update_view, name='shipment_update'),
]
