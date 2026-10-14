from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Category, Product, ProductVariant, Cart, CartItem, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

class ProductVariantInline(TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('title', 'category', 'base_price', 'currency', 'is_featured', 'is_in_stock', 'stock_count')
    list_filter = ('category', 'is_featured', 'is_in_stock')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductVariantInline]

class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_title', 'variant_title', 'quantity', 'unit_price', 'subtotal')

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'total_amount', 'currency', 'delivery_method', 'created_at')
    list_filter = ('status', 'delivery_method')
    search_fields = ('order_number', 'customer__email', 'customer__full_name', 'recipient_name')
    readonly_fields = ('order_number', 'created_at')
    inlines = [OrderItemInline]

@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'created_at')
