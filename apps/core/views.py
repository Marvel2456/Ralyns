from django.shortcuts import render
from apps.logistics.models import Route, Warehouse, Shipment
from apps.store.models import Product, Category

def home_view(request):
    """
    Main landing page showcasing cross-border logistics,
    quick tracking, live calculator, and curated e-commerce drops.
    """
    routes = Route.objects.filter(is_active=True)[:6]
    warehouses = Warehouse.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_featured=True, is_in_stock=True)[:8]
    categories = Category.objects.filter(is_active=True)[:6]

    context = {
        'routes': routes,
        'warehouses': warehouses,
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'pages/home.html', context)


def about_view(request):
    return render(request, 'pages/about.html')


def contact_view(request):
    return render(request, 'pages/contact.html')
