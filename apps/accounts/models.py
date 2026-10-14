import random
import string
import uuid
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from apps.core.models import BaseUUIDModel

class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.Role.ADMIN)
        extra_fields.setdefault('is_email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser, BaseUUIDModel):
    """
    Unified User model for both Logistics (Cargo/Warehousing) and E-Commerce.
    Uses UUID as the primary key.
    """
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer (Logistics & E-Commerce)'
        MODERATOR = 'MODERATOR', 'Moderator / Operations Staff'
        ADMIN = 'ADMIN', 'Super Administrator'

    username = None
    email = models.EmailField('Email Address', unique=True, db_index=True)
    full_name = models.CharField('Full Name', max_length=255)
    phone = models.CharField('Phone / WhatsApp Number', max_length=30, blank=True)
    role = models.CharField('Role', max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    
    # Auto-generated mailbox/cargo routing code (e.g. RAL-8492)
    customer_code = models.CharField('Customer Shipping Code', max_length=30, unique=True, blank=True, db_index=True)
    is_email_verified = models.BooleanField('Email Verified', default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.customer_code or self.email})"

    def save(self, *args, **kwargs):
        if not self.customer_code:
            self.customer_code = self._generate_unique_customer_code()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_unique_customer_code(cls):
        while True:
            digits = ''.join(random.choices(string.digits, k=5))
            code = f"RAL-{digits}"
            if not cls.objects.filter(customer_code=code).exists():
                return code

    @property
    def is_moderator(self):
        return self.role in [self.Role.MODERATOR, self.Role.ADMIN] or self.is_staff

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser


class EmailOTP(BaseUUIDModel):
    """
    Time-limited 6-digit One-Time Password for email verification.
    """
    class Purpose(models.TextChoices):
        REGISTRATION = 'REGISTRATION', 'Account Registration'
        PASSWORD_RESET = 'PASSWORD_RESET', 'Password Reset'
        LOGIN_2FA = 'LOGIN_2FA', 'Two-Factor Login'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6, db_index=True)
    purpose = models.CharField(max_length=30, choices=Purpose.choices, default=Purpose.REGISTRATION)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Email OTP'
        verbose_name_plural = 'Email OTPs'
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.user.email} [{self.purpose}]: {self.code}"

    @classmethod
    def create_otp(cls, user, purpose=Purpose.REGISTRATION, validity_minutes=15):
        # Invalidate previous unused OTPs for this purpose
        cls.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)
        code = f"{random.randint(100000, 999999)}"
        expires_at = timezone.now() + timedelta(minutes=validity_minutes)
        return cls.objects.create(user=user, code=code, purpose=purpose, expires_at=expires_at)

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at


class ModeratorProfile(BaseUUIDModel):
    """
    Granular permission profile for moderators created by Admin.
    """
    class Department(models.TextChoices):
        LOGISTICS = 'LOGISTICS', 'Freight & Shipping Operations'
        WAREHOUSE = 'WAREHOUSE', 'Warehouse Hub Management'
        STORE = 'STORE', 'E-Commerce Store & Inventory'
        SUPPORT = 'SUPPORT', 'Customer Support & Inquiries'

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='moderator_profile')
    department = models.CharField(max_length=50, choices=Department.choices, default=Department.LOGISTICS)
    can_manage_routes = models.BooleanField('Can Manage Routes & Rates', default=True)
    can_update_shipments = models.BooleanField('Can Update Cargo Tracking & Checkpoints', default=True)
    can_manage_products = models.BooleanField('Can Manage Store Products', default=True)
    can_manage_orders = models.BooleanField('Can Fulfill Store Orders', default=True)

    def __str__(self):
        return f"Moderator Profile: {self.user.full_name} ({self.get_department_display()})"


class UserAddress(BaseUUIDModel):
    """
    Saved delivery addresses for customer checkout or hub deliveries.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    recipient_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=30)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'User Address'
        verbose_name_plural = 'User Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.recipient_name} - {self.city}, {self.state}"
