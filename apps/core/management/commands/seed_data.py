from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser, ModeratorProfile
from apps.logistics.models import Warehouse, Route, Shipment, ShipmentCheckpoint
from apps.store.models import Category, Product, ProductVariant

class Command(BaseCommand):
    help = "Seeds initial brand data, admin/moderator accounts, routes, hubs, and e-commerce products."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting database seeding for Ralyn's International..."))

        # 1. Admin Account
        admin_user, created = CustomUser.objects.get_or_create(
            email='admin@ralyns.com',
            defaults={
                'full_name': "Ralyn's Super Admin",
                'phone': '+234 800 725 9677',
                'role': CustomUser.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_email_verified': True,
            }
        )
        if created:
            admin_user.set_password('AdminRalyns2026!')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("✓ Admin created: admin@ralyns.com (pwd: AdminRalyns2026!)"))
        else:
            self.stdout.write("Admin already exists.")

        # 2. Moderator Account
        moderator_user, created = CustomUser.objects.get_or_create(
            email='moderator@ralyns.com',
            defaults={
                'full_name': "Sarah Odu (Logistics Lead)",
                'phone': '+234 802 111 2233',
                'role': CustomUser.Role.MODERATOR,
                'is_staff': True,
                'is_email_verified': True,
            }
        )
        if created:
            moderator_user.set_password('Moderator2026!')
            moderator_user.save()
            ModeratorProfile.objects.create(
                user=moderator_user,
                department=ModeratorProfile.Department.LOGISTICS,
                can_manage_routes=True,
                can_update_shipments=True,
                can_manage_products=True,
                can_manage_orders=True
            )
            self.stdout.write(self.style.SUCCESS("✓ Moderator created: moderator@ralyns.com (pwd: Moderator2026!)"))

        # 3. Demo Customer Account
        customer_user, created = CustomUser.objects.get_or_create(
            email='customer@ralyns.com',
            defaults={
                'full_name': "Emeka Okonkwo",
                'phone': '+234 803 999 8877',
                'role': CustomUser.Role.CUSTOMER,
                'is_email_verified': True,
            }
        )
        if created:
            customer_user.set_password('Customer2026!')
            customer_user.save()
            self.stdout.write(self.style.SUCCESS(f"✓ Customer created: customer@ralyns.com (Code: {customer_user.customer_code})"))

        # 4. Warehouses
        wh_gz, _ = Warehouse.objects.get_or_create(
            name="Guangzhou Baiyun International Cargo Hub",
            country="China",
            city="Guangzhou",
            defaults={
                'address_line': "Building B4, International Logistics Park, Baiyun District, Guangzhou, Guangdong, China",
                'contact_person': "Mr. Chen / Ralyn's Receiving Desk",
                'contact_phone': "+86 138 2233 4455",
                'marking_instructions': "Name: [Customer Full Name] + [RAL-CODE]\nPhone: +86 138 2233 4455\nMarking on Cartons: [RAL-CODE]",
                'is_receiving_hub': True,
                'is_active': True,
            }
        )

        wh_uk, _ = Warehouse.objects.get_or_create(
            name="London Heathrow Cargo Terminal",
            country="United Kingdom",
            city="London",
            defaults={
                'address_line': "Unit 7, Airlink Express Freight Center, Scylla Road, Heathrow Airport, TW6 3FE, UK",
                'contact_person': "David Evans",
                'contact_phone': "+44 20 8759 4000",
                'marking_instructions': "Name: [Customer Full Name] / [RAL-CODE]\nAirlink Terminal / Ralyn's Unit 7",
                'is_receiving_hub': True,
                'is_active': True,
            }
        )

        wh_de, _ = Warehouse.objects.get_or_create(
            name="Frankfurt Airport Cargo City Hub",
            country="Germany",
            city="Frankfurt",
            defaults={
                'address_line': "Gebäude 451, CargoCity Süd, Frankfurt Airport, 60549 Frankfurt am Main, Germany",
                'contact_person': "Klaus Becker",
                'contact_phone': "+49 69 6900",
                'marking_instructions': "Ralyn's International / [Customer Name] + [RAL-CODE]",
                'is_receiving_hub': True,
                'is_active': True,
            }
        )

        wh_ng, _ = Warehouse.objects.get_or_create(
            name="Lagos Ikeja Central Hub",
            country="Nigeria",
            city="Lagos",
            defaults={
                'address_line': "Plot 12, Commercial Avenue, Ikeja Industrial Estate, Lagos, Nigeria",
                'contact_person': "Chinedu / Dispatch Manager",
                'contact_phone': "+234 800 725 9677",
                'marking_instructions': "Ralyn's Central Sorting & Customer Pickup Terminal",
                'is_receiving_hub': False,
                'is_active': True,
            }
        )
        self.stdout.write(self.style.SUCCESS("✓ 4 Global Warehouses initialized."))

        # 5. Dynamic Corridors / Routes
        routes_data = [
            # China to Nigeria
            {
                'origin_country': 'China', 'origin_city': 'Guangzhou',
                'destination_country': 'Nigeria', 'destination_city': 'Lagos',
                'freight_type': Route.FreightType.AIR_EXPRESS,
                'rate_per_kg': Decimal('8.50'), 'rate_per_cbm': Decimal('0.00'),
                'clearance_fee': Decimal('15.00'), 'handling_fee': Decimal('5.00'),
                'min_weight_kg': Decimal('1.00'), 'min_transit_days': 3, 'max_transit_days': 5,
                'departure_schedule': 'Daily Departures (Mon - Fri)',
            },
            {
                'origin_country': 'China', 'origin_city': 'Guangzhou',
                'destination_country': 'Nigeria', 'destination_city': 'Lagos',
                'freight_type': Route.FreightType.AIR_NORMAL,
                'rate_per_kg': Decimal('6.00'), 'rate_per_cbm': Decimal('0.00'),
                'clearance_fee': Decimal('10.00'), 'handling_fee': Decimal('5.00'),
                'min_weight_kg': Decimal('3.00'), 'min_transit_days': 7, 'max_transit_days': 10,
                'departure_schedule': 'Tuesdays & Fridays',
            },
            {
                'origin_country': 'China', 'origin_city': 'Guangzhou',
                'destination_country': 'Nigeria', 'destination_city': 'Lagos',
                'freight_type': Route.FreightType.SEA_LCL,
                'rate_per_kg': Decimal('0.00'), 'rate_per_cbm': Decimal('190.00'),
                'clearance_fee': Decimal('30.00'), 'handling_fee': Decimal('15.00'),
                'min_weight_kg': Decimal('1.00'), 'min_transit_days': 35, 'max_transit_days': 45,
                'departure_schedule': 'Every Saturday Sailing',
            },
            # Europe to Nigeria
            {
                'origin_country': 'United Kingdom', 'origin_city': 'London',
                'destination_country': 'Nigeria', 'destination_city': 'Lagos',
                'freight_type': Route.FreightType.AIR_EXPRESS,
                'rate_per_kg': Decimal('7.50'), 'rate_per_cbm': Decimal('0.00'),
                'clearance_fee': Decimal('10.00'), 'handling_fee': Decimal('5.00'),
                'min_weight_kg': Decimal('1.00'), 'min_transit_days': 4, 'max_transit_days': 6,
                'departure_schedule': 'Wednesdays & Saturdays',
            },
            {
                'origin_country': 'Germany', 'origin_city': 'Frankfurt',
                'destination_country': 'Nigeria', 'destination_city': 'Lagos',
                'freight_type': Route.FreightType.AIR_NORMAL,
                'rate_per_kg': Decimal('6.80'), 'rate_per_cbm': Decimal('0.00'),
                'clearance_fee': Decimal('10.00'), 'handling_fee': Decimal('5.00'),
                'min_weight_kg': Decimal('2.00'), 'min_transit_days': 5, 'max_transit_days': 8,
                'departure_schedule': 'Thursdays',
            },
            # Nigeria Outbound / Exports
            {
                'origin_country': 'Nigeria', 'origin_city': 'Lagos',
                'destination_country': 'United States', 'destination_city': 'New York',
                'freight_type': Route.FreightType.AIR_EXPRESS,
                'rate_per_kg': Decimal('10.50'), 'rate_per_cbm': Decimal('0.00'),
                'clearance_fee': Decimal('20.00'), 'handling_fee': Decimal('10.00'),
                'min_weight_kg': Decimal('2.00'), 'min_transit_days': 5, 'max_transit_days': 7,
                'departure_schedule': 'Tuesdays & Fridays',
            },
            {
                'origin_country': 'Nigeria', 'origin_city': 'Lagos',
                'destination_country': 'China', 'destination_city': 'Guangzhou',
                'freight_type': Route.FreightType.AIR_NORMAL,
                'rate_per_kg': Decimal('9.00'), 'rate_per_cbm': Decimal('0.00'),
                'clearance_fee': Decimal('15.00'), 'handling_fee': Decimal('10.00'),
                'min_weight_kg': Decimal('5.00'), 'min_transit_days': 7, 'max_transit_days': 10,
                'departure_schedule': 'Weekly Departures',
            },
            {
                'origin_country': 'Nigeria', 'origin_city': 'Lagos',
                'destination_country': 'United Kingdom', 'destination_city': 'London',
                'freight_type': Route.FreightType.AIR_EXPRESS,
                'rate_per_kg': Decimal('8.00'), 'rate_per_cbm': Decimal('0.00'),
                'clearance_fee': Decimal('15.00'), 'handling_fee': Decimal('5.00'),
                'min_weight_kg': Decimal('1.00'), 'min_transit_days': 4, 'max_transit_days': 6,
                'departure_schedule': 'Mondays & Thursdays',
            },
        ]

        for rd in routes_data:
            Route.objects.get_or_create(
                origin_city=rd['origin_city'],
                origin_country=rd['origin_country'],
                destination_city=rd['destination_city'],
                destination_country=rd['destination_country'],
                freight_type=rd['freight_type'],
                defaults=rd
            )
        self.stdout.write(self.style.SUCCESS(f"✓ {len(routes_data)} Dynamic Routes configured."))

        # 6. E-Commerce Categories & Products
        cat_electronics, _ = Category.objects.get_or_create(
            name="Consumer Electronics & Gadgets",
            defaults={'description': "High-grade gadgets, wireless chargers, drones, and smart peripherals directly from verified Shenzhen factories."}
        )
        cat_fashion, _ = Category.objects.get_or_create(
            name="Luxury & Fashion Accessories",
            defaults={'description': "Imported designer bags, precision chronographs, and curated wardrobe essentials."}
        )
        cat_industrial, _ = Category.objects.get_or_create(
            name="Industrial Spares & Solar Components",
            defaults={'description': "Commercial inverter accessories, solar panels, and hardware spares."}
        )

        p1, _ = Product.objects.get_or_create(
            title="Shenzhen Ultra-Fast 65W GaN Multi-Port Charger Hub",
            category=cat_electronics,
            defaults={
                'description': "Universal 3-port compact gallium nitride fast charger for MacBooks, laptops, iPhones, and Android devices.",
                'base_price': Decimal('28500.00'),
                'image_url': 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop&q=80',
                'is_featured': True,
                'is_in_stock': True,
                'stock_count': 45,
                'origin_country': 'Guangdong, China',
            }
        )
        ProductVariant.objects.get_or_create(product=p1, name="Matte Black / UK Plug", defaults={'price_adjustment': Decimal('0.00')})
        ProductVariant.objects.get_or_create(product=p1, name="Pearl White / UK Plug", defaults={'price_adjustment': Decimal('0.00')})

        p2, _ = Product.objects.get_or_create(
            title="Studio Pro Wireless Active Noise Cancelling Headphones",
            category=cat_electronics,
            defaults={
                'description': "Hi-Res spatial audio headphones with 40h battery endurance, transparency mode, and ultra-plush memory foam earcups.",
                'base_price': Decimal('68000.00'),
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80',
                'is_featured': True,
                'is_in_stock': True,
                'stock_count': 20,
                'origin_country': 'Shenzhen, China',
            }
        )
        ProductVariant.objects.get_or_create(product=p2, name="Midnight Navy", defaults={'price_adjustment': Decimal('0.00')})
        ProductVariant.objects.get_or_create(product=p2, name="Slate Grey", defaults={'price_adjustment': Decimal('0.00')})

        p3, _ = Product.objects.get_or_create(
            title="Ralyn's Curated Genuine Leather Weekender Duffel",
            category=cat_fashion,
            defaults={
                'description': "Handcrafted full-grain leather travel bag with waterproof lining, shoe compartment, and heavy-duty brass zippers.",
                'base_price': Decimal('95000.00'),
                'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=80',
                'is_featured': True,
                'is_in_stock': True,
                'stock_count': 15,
                'origin_country': 'Europe (Italy/UK)',
            }
        )

        p4, _ = Product.objects.get_or_create(
            title="Pure Sine Wave 3000W Smart Hybrid Solar Inverter System",
            category=cat_industrial,
            defaults={
                'description': "High efficiency MPPT solar inverter with Wi-Fi real-time remote monitoring and smart battery charging logic.",
                'base_price': Decimal('345000.00'),
                'image_url': 'https://images.unsplash.com/photo-1509391365360-2e959784a276?w=600&auto=format&fit=crop&q=80',
                'is_featured': True,
                'is_in_stock': True,
                'stock_count': 8,
                'origin_country': 'Guangzhou, China',
            }
        )
        self.stdout.write(self.style.SUCCESS("✓ Products & Categories seeded."))

        # 7. Sample Waybill Shipment
        gz_route = Route.objects.filter(origin_city='Guangzhou', freight_type=Route.FreightType.AIR_EXPRESS).first()
        if gz_route and customer_user:
            demo_shipment, s_created = Shipment.objects.get_or_create(
                tracking_number="RAL-2026-889021",
                defaults={
                    'customer': customer_user,
                    'route': gz_route,
                    'origin_warehouse': wh_gz,
                    'cargo_description': "2 Cartons - Smart electronics accessories & sample components",
                    'weight_kg': Decimal('12.50'),
                    'pieces_count': 2,
                    'total_cost': Decimal('126.25'),
                    'currency': 'USD',
                    'status': Shipment.Status.IN_TRANSIT,
                    'payment_status': Shipment.PaymentStatus.PAID,
                    'receiver_name': "Emeka Okonkwo",
                    'receiver_phone': "+234 803 999 8877",
                    'receiver_address': "15 Victoria Island Blvd, Lagos, Nigeria",
                }
            )
            if s_created:
                ShipmentCheckpoint.objects.create(
                    shipment=demo_shipment,
                    status=Shipment.Status.BOOKING_SUBMITTED,
                    location="Online System Booking",
                    remarks="Cargo waybill created by client.",
                    created_by=admin_user
                )
                ShipmentCheckpoint.objects.create(
                    shipment=demo_shipment,
                    status=Shipment.Status.RECEIVED_ORIGIN,
                    location="Guangzhou Baiyun Cargo Hub, China",
                    remarks="Cartons received, weighed (12.50 KG), repackaged and labeled.",
                    created_by=moderator_user
                )
                ShipmentCheckpoint.objects.create(
                    shipment=demo_shipment,
                    status=Shipment.Status.IN_TRANSIT,
                    location="Guangzhou Baiyun Airport (Flight CZ-3021)",
                    remarks="Departed Guangzhou hub, in international air transit to Lagos.",
                    created_by=moderator_user
                )
                self.stdout.write(self.style.SUCCESS(f"✓ Sample shipment created: {demo_shipment.tracking_number}"))

        self.stdout.write(self.style.SUCCESS("\n🎉 Database successfully seeded with all initial data!"))
