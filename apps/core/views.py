from django.shortcuts import render
from apps.logistics.models import Route, Warehouse, Shipment
from apps.store.models import Product, Category

def home_view(request):
    """
    Main landing page showcasing cross-border logistics,
    quick tracking, live calculator, top selling e-commerce drops, and freight corridors.
    """
    routes = Route.objects.filter(is_active=True)[:6]
    warehouses = Warehouse.objects.filter(is_active=True)
    best_sellers = Product.objects.filter(is_in_stock=True).order_by('-is_featured', '-discount_price', '-created_at')[:8]
    categories = Category.objects.filter(is_active=True)[:6]

    context = {
        'routes': routes,
        'warehouses': warehouses,
        'best_sellers': best_sellers,
        'featured_products': best_sellers,
        'categories': categories,
    }
    return render(request, 'pages/home.html', context)


def about_view(request):
    return render(request, 'pages/about.html')


def contact_view(request):
    return render(request, 'pages/contact.html')
