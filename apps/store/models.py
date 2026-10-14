import random
import string
import uuid
from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from apps.core.models import BaseUUIDModel
from apps.accounts.models import CustomUser

class Category(BaseUUIDModel):
    """
    E-Commerce product categories (Electronics, Fashion, Gadgets, Industrial Spares, etc.)
    """
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon_name = models.CharField(max_length=50, default='package', help_text="Lucide icon name")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(BaseUUIDModel):
    """
    Imported products sold directly on Ralyn's International store.
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    base_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price in NGN")
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='NGN')
    
    image = models.ImageField(upload_to='products/', null=True, blank=True, help_text="Upload image (automatically converted to WebP)")
    image_url = models.URLField(max_length=500, blank=True, help_text="Direct product image URL fallback")
    is_featured = models.BooleanField(default=False)
    is_in_stock = models.BooleanField(default=True)
    stock_count = models.PositiveIntegerField(default=10)
    origin_country = models.CharField(max_length=100, default='Imported (China / Europe)')

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.title} - ₦{self.current_price:,.2f}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Convert uploaded image to WebP with size reduction
        if self.image and hasattr(self.image, 'file'):
            if not self.image.name.lower().endswith('.webp'):
                from apps.core.image_compressor import compress_and_convert_to_webp
                compressed = compress_and_convert_to_webp(self.image)
                if compressed:
                    self.image.save(compressed.name, compressed, save=False)

        super().save(*args, **kwargs)

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.base_price

    @property
    def discount_amount(self):
        if self.discount_price and self.base_price and self.base_price > self.discount_price:
            return self.base_price - self.discount_price
        return Decimal('0.00')

    @property
    def discount_percent(self):
        if self.discount_price and self.base_price and self.base_price > self.discount_price:
            percent = ((self.base_price - self.discount_price) / self.base_price) * 100
            return int(round(percent))
        return 0

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return None


class ProductVariant(BaseUUIDModel):
    """
    Product variations (e.g. Color, Size, Storage capacity).
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=150, help_text="e.g. 256GB Midnight Black")
    sku = models.CharField(max_length=100, unique=True, blank=True)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    stock_quantity = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.product.title} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.sku:
            rand_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            self.sku = f"RAL-{rand_code}"
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        return self.product.current_price + self.price_adjustment


class Cart(BaseUUIDModel):
    """
    Shopping cart bound to an authenticated user or anonymous session key.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=60, null=True, blank=True, db_index=True)

    def __str__(self):
        return f"Cart {self.id} (User: {self.user or self.session_key})"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(BaseUUIDModel):
    """
    Individual product line inside a Cart.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product', 'variant')

    @property
    def unit_price(self):
        if self.variant:
            return self.variant.final_price
        return self.product.current_price

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class Order(BaseUUIDModel):
    """
    Confirmed customer e-commerce order.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Order Placed / Payment Pending'
        CONFIRMED = 'CONFIRMED', 'Payment Verified / Processing'
        DISPATCHED = 'DISPATCHED', 'Dispatched for Delivery'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class DeliveryMethod(models.TextChoices):
        DOOR_DELIVERY = 'DOOR_DELIVERY', 'Doorstep Nationwide Delivery'
        HUB_PICKUP = 'HUB_PICKUP', "Pickup at Ralyn's Distribution Hub"

    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    delivery_method = models.CharField(max_length=30, choices=DeliveryMethod.choices, default=DeliveryMethod.DOOR_DELIVERY)
    
    recipient_name = models.CharField(max_length=255)
    recipient_phone = models.CharField(max_length=50)
    shipping_address = models.TextField()
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=10, default='NGN')
    payment_status = models.CharField(max_length=20, default='PENDING')

    class Meta:
        verbose_name = 'Store Order'
        verbose_name_plural = 'Store Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer.full_name} (₦{self.total_amount:,.2f})"

    def save(self, *args, **kwargs):
        if not self.order_number:
            year = timezone.now().year
            rand_code = ''.join(random.choices(string.digits, k=6))
            self.order_number = f"RLO-{year}-{rand_code}"
        super().save(*args, **kwargs)


class OrderItem(BaseUUIDModel):
    """
    Line item snapshot inside an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_title = models.CharField(max_length=255)
    variant_title = models.CharField(max_length=150, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_title} in Order #{self.order.order_number}"
