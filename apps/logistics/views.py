from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Route, Warehouse, Shipment, ShipmentCheckpoint
from .forms import ShipmentBookingForm
from apps.core.emails import send_shipment_created_email

def calculator_view(request):
    """
    Live shipping freight calculator supporting full-page and HTMX partial responses.
    """
    routes = Route.objects.filter(is_active=True)
    selected_route = None
    estimated_cost = None
    weight_kg = Decimal('1.0')
    volume_cbm = Decimal('0.0')

    route_id = request.GET.get('route_id')
    raw_weight = request.GET.get('weight_kg', '1.0')
    raw_volume = request.GET.get('volume_cbm', '0.0')

    try:
        weight_kg = Decimal(str(raw_weight)) if raw_weight else Decimal('1.0')
    except Exception:
        weight_kg = Decimal('1.0')

    try:
        volume_cbm = Decimal(str(raw_volume)) if raw_volume else Decimal('0.0')
    except Exception:
        volume_cbm = Decimal('0.0')

    if route_id:
        selected_route = Route.objects.filter(id=route_id, is_active=True).first()
        if selected_route:
            estimated_cost = selected_route.calculate_cost(weight_kg, volume_cbm)

    context = {
        'routes': routes,
        'selected_route': selected_route,
        'weight_kg': weight_kg,
        'volume_cbm': volume_cbm,
        'estimated_cost': estimated_cost,
    }

    # If requested by HTMX, return just the dynamic calculation card snippet
    if request.headers.get('HX-Request'):
        return render(request, 'logistics/partials/calculator_result.html', context)

    return render(request, 'logistics/calculator.html', context)


def track_shipment_view(request):
    """
    Live public package & cargo tracking lookup.
    """
    tracking_number = request.GET.get('tracking_number', '').strip().upper()
    shipment = None
    error = None

    if tracking_number:
        shipment = Shipment.objects.filter(tracking_number=tracking_number).select_related('route', 'origin_warehouse').first()
        if not shipment:
            error = f"No cargo found for tracking number '{tracking_number}'. Please check the format (e.g. RAL-2026-XXXXXX)."

    context = {
        'shipment': shipment,
        'tracking_number': tracking_number,
        'error': error,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'logistics/partials/tracking_result.html', context)

    return render(request, 'logistics/tracking.html', context)


@login_required
def book_shipment_view(request):
    """
    Customer portal view to create a new waybill shipment booking.
    """
    if request.method == 'POST':
        form = ShipmentBookingForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.customer = request.user
            shipment.save()

            # Create initial milestone checkpoint
            ShipmentCheckpoint.objects.create(
                shipment=shipment,
                status=Shipment.Status.BOOKING_SUBMITTED,
                location=f"{shipment.route.origin_city}, {shipment.route.origin_country}",
                remarks="Booking received online. Awaiting cargo intake at warehouse.",
                created_by=request.user
            )

            # Send confirmation email via Celery & Resend
            send_shipment_created_email(shipment)

            messages.success(request, f"Shipment booked successfully! Tracking Code: {shipment.tracking_number}")
            return redirect('accounts:dashboard')
    else:
        form = ShipmentBookingForm()

    return render(request, 'logistics/book_shipment.html', {'form': form})


def routes_directory_view(request):
    """
    Directory of all active international routes and pricing.
    """
    routes = Route.objects.filter(is_active=True).order_by('origin_country', 'destination_country')
    warehouses = Warehouse.objects.filter(is_active=True)
    return render(request, 'logistics/routes.html', {'routes': routes, 'warehouses': warehouses})
