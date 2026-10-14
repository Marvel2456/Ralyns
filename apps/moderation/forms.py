from django import forms
from apps.logistics.models import Route, Shipment, ShipmentCheckpoint
from apps.accounts.models import CustomUser, ModeratorProfile

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = [
            'origin_country', 'origin_city', 'destination_country', 'destination_city',
            'freight_type', 'currency', 'rate_per_kg', 'rate_per_cbm',
            'clearance_fee', 'handling_fee', 'min_weight_kg',
            'min_transit_days', 'max_transit_days', 'departure_schedule', 'is_active'
        ]
        widgets = {
            'origin_country': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'origin_city': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'destination_country': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'destination_city': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'freight_type': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'currency': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'rate_per_kg': forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'rate_per_cbm': forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'clearance_fee': forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'handling_fee': forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'min_weight_kg': forms.NumberInput(attrs={'step': '0.1', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'min_transit_days': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'max_transit_days': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
            'departure_schedule': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
        }


class CreateModeratorForm(forms.Form):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Sarah Odu', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'staff@ralyns.com', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+234 800 000 0000', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Initial password', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'}),
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


class ShipmentUpdateForm(forms.Form):
    status = forms.ChoiceField(
        choices=Shipment.Status.choices,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'})
    )
    location = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Guangzhou Baiyun Customs or Lagos Port', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'})
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional internal or customer checkpoint note...', 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#D87808] text-slate-800'})
    )
