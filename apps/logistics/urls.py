from django.urls import path
from . import views

app_name = 'logistics'

urlpatterns = [
    path('calculator/', views.calculator_view, name='calculator'),
    path('tracking/', views.track_shipment_view, name='tracking'),
    path('book/', views.book_shipment_view, name='book_shipment'),
    path('routes/', views.routes_directory_view, name='routes_directory'),
]
