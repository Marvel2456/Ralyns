from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Warehouse, Route, Shipment, ShipmentCheckpoint

@admin.register(Warehouse)
class WarehouseAdmin(ModelAdmin):
    list_display = ('name', 'city', 'country', 'contact_phone', 'is_receiving_hub', 'is_active')
    list_filter = ('country', 'is_receiving_hub', 'is_active')
    search_fields = ('name', 'city', 'country', 'address_line')

@admin.register(Route)
class RouteAdmin(ModelAdmin):
    list_display = ('origin_city', 'origin_country', 'destination_city', 'destination_country', 'freight_type', 'rate_per_kg', 'rate_per_cbm', 'currency', 'is_active')
    list_filter = ('freight_type', 'origin_country', 'destination_country', 'is_active')
    search_fields = ('origin_city', 'destination_city')

class CheckpointInline(TabularInline):
    model = ShipmentCheckpoint
    extra = 1

@admin.register(Shipment)
class ShipmentAdmin(ModelAdmin):
    list_display = ('tracking_number', 'customer', 'route', 'weight_kg', 'total_cost', 'currency', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'route__freight_type')
    search_fields = ('tracking_number', 'customer__email', 'customer__full_name', 'receiver_name')
    inlines = [CheckpointInline]
    readonly_fields = ('tracking_number',)

@admin.register(ShipmentCheckpoint)
class ShipmentCheckpointAdmin(ModelAdmin):
    list_display = ('shipment', 'status', 'location', 'timestamp', 'created_by')
    list_filter = ('status', 'timestamp')
    search_fields = ('shipment__tracking_number', 'location', 'remarks')
