from django import forms
from apps.accounts.models import CustomUser, ModeratorProfile
from apps.logistics.models import Route, Warehouse, Shipment, ShipmentCheckpoint
from apps.store.models import Product, Category

class OwnerModeratorForm(forms.Form):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'e.g. David Alabi', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'staff@ralyns.com', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+234 800 000 0000', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Temporary password', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
        min_length=8
    )
    department = forms.ChoiceField(
        choices=ModeratorProfile.Department.choices,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'})
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


class OwnerWarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'country', 'city', 'address_line', 'contact_person', 'contact_phone', 'marking_instructions', 'is_receiving_hub', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'country': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'address_line': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'contact_person': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'contact_phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'marking_instructions': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800 font-mono text-xs'}),
        }


class OwnerProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'category', 'description', 'base_price', 'discount_price', 'currency', 'image', 'image_url', 'stock_count', 'origin_country', 'is_featured', 'is_in_stock']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'base_price': forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'discount_price': forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'currency': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://...', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'stock_count': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'origin_country': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
        }
