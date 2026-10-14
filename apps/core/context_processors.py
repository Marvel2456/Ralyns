from django.conf import settings

def brand_context(request):
    """
    Expose brand metadata and colors extracted from the Ralyn's International logo.
    """
    return {
        'BRAND_NAME': "Ralyn's International",
        'BRAND_TAGLINE': "Global Importation, Freight Logistics & Curated E-Commerce",
        'BRAND_COLORS': {
            'navy': '#10182C',
            'orange': '#D87808',
            'steel': '#344054',
            'slate': '#64748C',
        },
        'SUPPORT_EMAIL': getattr(settings, 'SUPPORT_EMAIL', 'support@ralyns.com'),
        'SUPPORT_PHONE': '+234 800 725 9677',
        'WAREHOUSE_HUBS': [
            {'code': 'GZ-CN', 'city': 'Guangzhou', 'country': 'China', 'tag': 'Main Procurement & Air/Sea Hub'},
            {'code': 'LDN-UK', 'city': 'London', 'country': 'United Kingdom', 'tag': 'Europe Express Hub'},
            {'code': 'FRA-DE', 'city': 'Frankfurt', 'country': 'Germany', 'tag': 'EU Cargo Hub'},
            {'code': 'LOS-NG', 'city': 'Lagos', 'country': 'Nigeria', 'tag': 'Central Distribution Hub'},
        ]
    }
