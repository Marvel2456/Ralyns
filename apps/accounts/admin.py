from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin, TabularInline
from .models import CustomUser, EmailOTP, ModeratorProfile, UserAddress

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    model = CustomUser
    list_display = ('email', 'full_name', 'customer_code', 'role', 'is_email_verified', 'is_staff', 'created_at')
    list_filter = ('role', 'is_email_verified', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name', 'customer_code', 'phone')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone', 'customer_code')}),
        ('Permissions & Roles', {'fields': ('role', 'is_email_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('customer_code', 'date_joined', 'last_login')

@admin.register(EmailOTP)
class EmailOTPAdmin(ModelAdmin):
    list_display = ('user', 'code', 'purpose', 'expires_at', 'is_used', 'created_at')
    list_filter = ('purpose', 'is_used')
    search_fields = ('user__email', 'code')

@admin.register(ModeratorProfile)
class ModeratorProfileAdmin(ModelAdmin):
    list_display = ('user', 'department', 'can_manage_routes', 'can_update_shipments', 'can_manage_products')
    list_filter = ('department',)

@admin.register(UserAddress)
class UserAddressAdmin(ModelAdmin):
    list_display = ('recipient_name', 'user', 'city', 'state', 'country', 'is_default')
    list_filter = ('state', 'country', 'is_default')
