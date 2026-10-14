# Ralyn's International — Cross-Border Shipping & E-Commerce Platform

A production-grade web application combining **cross-border freight logistics & cargo importation** with a **modern e-commerce retail storefront**, built with **Django 5.x**, **Tailwind CSS**, and **HTMX**, fully containerized with **Docker**, **PostgreSQL 16**, **Redis 7**, and **Celery**.

Developed by **[Vextech Limited](https://vextechafrica.com/)**.

---

## 🎨 Brand Identity & Color Palette

Extracted directly from the brand logo:
- **`brand-navy`** (`#10182C`): Corporate authority, primary headers, executive command center
- **`brand-orange`** (`#D87808`): Energetic logistics accent, CTA buttons, active badges
- **`brand-steel`** (`#344054`): Secondary typography & cards
- **`brand-slate`** (`#64748C`): Muted labels, breadcrumbs, unselected states

---

## 👑 Owner's Executive Command Center (`/owner/`)

A dedicated executive portal separate from Django admin, designed specifically for the business owner to oversee and control the entire application:
- **Live Business KPIs**: Gross logistics waybill revenue ($ USD), e-commerce sales revenue (₦ NGN), active shipments, customer counts, and route counts.
- **Moderator & Staff Governance**: Provision new moderators with departmental roles (Logistics, Warehouse, Store, Support) and toggle permissions (`can_manage_routes`, `can_update_shipments`, `can_manage_products`, `can_manage_orders`). Suspend or reactivate staff anytime.
- **Dynamic Trade Corridors Manager**: Create, edit, and adjust rates per KG, rates per CBM, clearance fees, handling surcharges, and departure schedules.
- **Global Receiving Hubs Manager**: Manage overseas warehouses in Guangzhou (China), London (UK), Frankfurt (Germany), and Lagos (Nigeria).
- **Cargo Waybill Oversight**: Global view of all consignments with status override and automatic customer Resend email notifications.
- **E-Commerce Catalog & Orders**: Create and edit products with automatic WebP conversion and Cloudinary storage, manage stock, and advance order fulfillment.
- **Customer Directory**: View all clients, emails, phone numbers, and auto-generated `RAL-XXXX` cargo codes.
- **Live Staff Audit Trail**: Real-time audit log of every operational change made by moderators.

---

## ⚡ Automated WebP Image Compressor & Cloudinary

All uploaded product and shipment images are automatically processed through the compression engine (`apps/core/image_compressor.py`):
- **WebP Conversion**: Uploaded JPEGs, PNGs, and HEICs are converted into high-efficiency `.webp` format.
- **Quality Preservation with ~75-95% File Size Reduction**: Strips unnecessary EXIF metadata, applies LANCZOS downsampling if dimensions exceed 1600px, and retains transparency.
- **Cloudinary Storage**: Seamlessly stores media on Cloudinary when API credentials are provided in `.env` (falls back gracefully to local media storage if credentials are not configured).

---

## 💎 Modern Django Admin with `django-unfold` (`/admin/`)

The native Django admin has been upgraded with **Django Unfold**:
- Sleek dark/light theme styled with Ralyn's palette (`#D87808` orange primary and `#10182C` navy sidebar)
- Modern cards, filters, and tabular inlines
- Fast search across all models and UUID primary keys

---

## 📧 Resend Email Pipeline & Celery Async Queuing

Automated email notifications handled asynchronously through Redis and Celery:
- **Account Registration & OTP**: 6-digit verification code with 15-minute expiration and customer cargo mailbox code (`RAL-XXXX`).
- **Shipment Waybill Booking**: Confirmation email with tracking number, route details, and origin warehouse packaging marks.
- **Shipment Status Updates**: Real-time checkpoint alerts whenever staff update the cargo milestone.
- **E-Commerce Order Receipt**: Item breakdown, variant details, shipping method, and payment summary.

---

## 🐳 Docker Services (`docker-compose.yml`)

1. **`web`**: Django 5.x application on port `8000`
2. **`db`**: PostgreSQL 16 Alpine on port `5432` (healthcheck enabled)
3. **`redis`**: Redis 7 Alpine on port `6379` (message broker & cache)
4. **`celery_worker`**: Celery worker consuming background email queues

---

## 🔑 Pre-Seeded Accounts

| Role | Email | Password | Access / Portal |
| :--- | :--- | :--- | :--- |
| **Business Owner** | `admin@ralyns.com` | `AdminRalyns2026!` | **Owner's Command Center** (`/owner/`) & **Unfold Admin** (`/admin/`) |
| **Operations Moderator** | `moderator@ralyns.com` | `Moderator2026!` | **Staff Operations Portal** (`/moderation/`) |
| **Customer** | `customer@ralyns.com` | `Customer2026!` | **Unified Dashboard** (`/accounts/dashboard/`) |

---

## 🌐 Key URLs

- **Public Homepage**: [http://localhost:8000/](http://localhost:8000/)
- **Owner's Executive Dashboard**: [http://localhost:8000/owner/](http://localhost:8000/owner/)
- **Owner Moderator Management**: [http://localhost:8000/owner/moderators/](http://localhost:8000/owner/moderators/)
- **Django Unfold Admin**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- **Staff Operations Portal**: [http://localhost:8000/moderation/](http://localhost:8000/moderation/)
- **Live Shipping Calculator**: [http://localhost:8000/logistics/calculator/](http://localhost:8000/logistics/calculator/)
- **Cargo Tracking**: [http://localhost:8000/logistics/tracking/?tracking_number=RAL-2026-889021](http://localhost:8000/logistics/tracking/?tracking_number=RAL-2026-889021)
- **Store Catalog**: [http://localhost:8000/store/](http://localhost:8000/store/)

---

© 2026 Ralyn's International. Developed by [Vextech Limited](https://vextechafrica.com/).
