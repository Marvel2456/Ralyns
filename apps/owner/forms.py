from django import forms
from apps.accounts.models import CustomUser, ModeratorProfile
from apps.logistics.models import Route, Warehouse, Shipment, ShipmentCheckpoint
from apps.store.models import Product, Category

class OwnerModeratorForm(forms.Form):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'e.g. David Alabi', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'staff@ralyns.com', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+234 800 000 0000', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Temporary password', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
        min_length=8
    )
    department = forms.ChoiceField(
        choices=ModeratorProfile.Department.choices,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'})
    )
    can_manage_routes = forms.BooleanField(required=False, initial=True)
    can_update_shipments = forms.BooleanField(required=False, initial=True)
    can_manage_products = forms.BooleanField(required=False, initial=True)
    can_manage_orders = forms.BooleanField(required=False, initial=True)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email


class OwnerModeratorEditForm(forms.Form):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. David Alabi',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'staff@ralyns.com',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '+234 800 000 0000',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'
        })
    )
    department = forms.ChoiceField(
        choices=ModeratorProfile.Department.choices,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'
        })
    )
    is_active = forms.BooleanField(
        required=False,
        label="Account Active",
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 rounded text-[#D87808] focus:ring-[#D87808] border-slate-400 bg-white'
        })
    )
    new_password = forms.CharField(
        required=False,
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Leave blank to preserve current password',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'
        }),
        help_text="Only enter a password if you wish to reset this moderator's password (min 8 characters)."
    )
    can_manage_routes = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded text-[#D87808] focus:ring-[#D87808] border-slate-400 bg-white'})
    )
    can_update_shipments = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded text-[#D87808] focus:ring-[#D87808] border-slate-400 bg-white'})
    )
    can_manage_products = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded text-[#D87808] focus:ring-[#D87808] border-slate-400 bg-white'})
    )
    can_manage_orders = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded text-[#D87808] focus:ring-[#D87808] border-slate-400 bg-white'})
    )

    def __init__(self, *args, user_instance=None, **kwargs):
        self.user_instance = user_instance
        if user_instance and 'initial' not in kwargs:
            profile = getattr(user_instance, 'moderator_profile', None)
            kwargs['initial'] = {
                'full_name': user_instance.full_name,
                'email': user_instance.email,
                'phone': user_instance.phone,
                'is_active': user_instance.is_active,
                'department': profile.department if profile else ModeratorProfile.Department.LOGISTICS,
                'can_manage_routes': profile.can_manage_routes if profile else True,
                'can_update_shipments': profile.can_update_shipments if profile else True,
                'can_manage_products': profile.can_manage_products if profile else True,
                'can_manage_orders': profile.can_manage_orders if profile else True,
            }
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        query = CustomUser.objects.filter(email=email)
        if self.user_instance:
            query = query.exclude(id=self.user_instance.id)
        if query.exists():
            raise forms.ValidationError("Another user with this email address already exists.")
        return email

    def save(self):
        user = self.user_instance
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone', '')
        user.is_active = self.cleaned_data.get('is_active', True)

        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)

        user.save()

        profile, _ = ModeratorProfile.objects.get_or_create(user=user)
        profile.department = self.cleaned_data['department']
        profile.can_manage_routes = self.cleaned_data.get('can_manage_routes', False)
        profile.can_update_shipments = self.cleaned_data.get('can_update_shipments', False)
        profile.can_manage_products = self.cleaned_data.get('can_manage_products', False)
        profile.can_manage_orders = self.cleaned_data.get('can_manage_orders', False)
        profile.save()

        return user


class OwnerWarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'country', 'city', 'address_line', 'contact_person', 'contact_phone', 'marking_instructions', 'is_receiving_hub', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'country': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'address_line': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'contact_person': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'contact_phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'marking_instructions': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800 font-mono text-xs'}),
        }


class OwnerProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'category', 'description', 'base_price', 'discount_price', 'currency', 'image', 'image_url', 'stock_count', 'origin_country', 'is_featured', 'is_in_stock']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'base_price': forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'discount_price': forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'currency': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://...', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'stock_count': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
            'origin_country': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-base sm:text-sm text-slate-800'}),
        }
