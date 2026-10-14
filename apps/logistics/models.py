import random
import string
import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from apps.core.models import BaseUUIDModel
from apps.accounts.models import CustomUser

class Warehouse(BaseUUIDModel):
    """
    Physical handling warehouses and receiving hubs across China, Europe, USA & Nigeria.
    """
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address_line = models.TextField()
    postal_code = models.CharField(max_length=30, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    marking_instructions = models.TextField(
        default="Recipient: [Your Name] + [RAL-CODE]\nWarehouse Tel: [Warehouse Contact]\nShipping Mark on Carton: [RAL-CODE]"
    )
    is_receiving_hub = models.BooleanField(default=True, help_text="Can customers send packages here?")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Warehouse Hub'
        verbose_name_plural = 'Warehouse Hubs'
        ordering = ['country', 'city']

    def __str__(self):
        return f"{self.name} ({self.city}, {self.country})"


class Route(BaseUUIDModel):
    """
    Dynamic shipping routes configured by Admin.
    Allows adding routes like China -> Nigeria, Europe -> Nigeria, Nigeria -> USA/China/Europe.
    """
    class FreightType(models.TextChoices):
        AIR_EXPRESS = 'AIR_EXPRESS', 'Air Cargo (Express 3-5 Business Days)'
        AIR_NORMAL = 'AIR_NORMAL', 'Air Cargo (Standard 7-10 Days)'
        SEA_LCL = 'SEA_LCL', 'Sea Freight (LCL Shared Container)'
        SEA_FCL = 'SEA_FCL', 'Sea Freight (Full Container Load)'

    origin_country = models.CharField(max_length=100)
    origin_city = models.CharField(max_length=100)
    destination_country = models.CharField(max_length=100)
    destination_city = models.CharField(max_length=100)
    freight_type = models.CharField(max_length=30, choices=FreightType.choices, default=FreightType.AIR_NORMAL)
    
    currency = models.CharField(max_length=10, default='USD')
    rate_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Cost per KG")
    rate_per_cbm = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Cost per CBM (for Sea)")
    clearance_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Fixed customs clearance fee")
    handling_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Documentation / handling surcharge")
    min_weight_kg = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('1.00'))
    
    min_transit_days = models.PositiveIntegerField(default=3)
    max_transit_days = models.PositiveIntegerField(default=7)
    departure_schedule = models.CharField(max_length=150, default='Weekly Departures (Tuesdays & Fridays)')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Shipping Route'
        verbose_name_plural = 'Shipping Routes'
        ordering = ['origin_country', 'destination_country', 'freight_type']

    def __str__(self):
        return f"{self.origin_city}, {self.origin_country} → {self.destination_city}, {self.destination_country} ({self.get_freight_type_display()})"

    def calculate_cost(self, weight_kg=Decimal('1.0'), volume_cbm=Decimal('0.0')):
        weight_kg = max(Decimal(str(weight_kg)), self.min_weight_kg)
        volume_cbm = Decimal(str(volume_cbm))

        if 'SEA' in self.freight_type and volume_cbm > Decimal('0.0'):
            freight_cost = volume_cbm * self.rate_per_cbm
        else:
            freight_cost = weight_kg * self.rate_per_kg

        total = freight_cost + self.clearance_fee + self.handling_fee
        return total.quantize(Decimal('0.01'))


class Shipment(BaseUUIDModel):
    """
    Waybill cargo shipment tracked from booking to delivery.
    """
    class Status(models.TextChoices):
        BOOKING_SUBMITTED = 'BOOKING_SUBMITTED', 'Booking Submitted'
        RECEIVED_ORIGIN = 'RECEIVED_ORIGIN', 'Received at Origin Warehouse'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit / Departed Origin'
        CUSTOMS_CLEARANCE = 'CUSTOMS_CLEARANCE', 'Customs Clearance in Progress'
        ARRIVED_DESTINATION = 'ARRIVED_DESTINATION', 'Arrived at Destination Hub'
        OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', 'Out for Delivery / Ready for Pickup'
        DELIVERED = 'DELIVERED', 'Delivered & Received'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Payment Pending'
        PAID = 'PAID', 'Paid'
        WAIVED = 'WAIVED', 'Waived / On Account'

    tracking_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shipments')
    route = models.ForeignKey(Route, on_delete=models.PROTECT, related_name='shipments')
    origin_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='origin_shipments')
    
    cargo_description = models.TextField(help_text="Detailed item breakdown, contents, cartons count")
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))
    volume_cbm = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal('0.0000'))
    pieces_count = models.PositiveIntegerField(default=1)
    
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=10, default='USD')
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.BOOKING_SUBMITTED, db_index=True)
    
    receiver_name = models.CharField(max_length=255)
    receiver_phone = models.CharField(max_length=50)
    receiver_address = models.TextField()
    estimated_arrival = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Shipment / Waybill'
        verbose_name_plural = 'Shipments / Waybills'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tracking_number} - {self.customer.full_name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = self._generate_tracking_number()
        if not self.total_cost or self.total_cost == Decimal('0.00'):
            self.total_cost = self.route.calculate_cost(self.weight_kg, self.volume_cbm)
            self.currency = self.route.currency
        super().save(*args, **kwargs)

    @classmethod
    def _generate_tracking_number(cls):
        while True:
            year = timezone.now().year
            rand_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            num = f"RAL-{year}-{rand_code}"
            if not cls.objects.filter(tracking_number=num).exists():
                return num

    @property
    def progress_percentage(self):
        status_weights = {
            self.Status.BOOKING_SUBMITTED: 15,
            self.Status.RECEIVED_ORIGIN: 35,
            self.Status.IN_TRANSIT: 55,
            self.Status.CUSTOMS_CLEARANCE: 75,
            self.Status.ARRIVED_DESTINATION: 88,
            self.Status.OUT_FOR_DELIVERY: 95,
            self.Status.DELIVERED: 100,
            self.Status.CANCELLED: 0,
        }
        return status_weights.get(self.status, 10)


class ShipmentCheckpoint(BaseUUIDModel):
    """
    Audit trail and timeline milestones for a shipment.
    """
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='checkpoints')
    status = models.CharField(max_length=40, choices=Shipment.Status.choices)
    location = models.CharField(max_length=255, help_text="e.g. Guangzhou Baiyun Cargo Airport or Lagos Ikeja Hub")
    remarks = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Shipment Checkpoint'
        verbose_name_plural = 'Shipment Checkpoints'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.shipment.tracking_number} @ {self.location} - {self.get_status_display()}"
