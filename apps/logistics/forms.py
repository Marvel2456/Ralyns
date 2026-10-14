from django import forms
from .models import Shipment, Route, Warehouse

class ShipmentBookingForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = [
            'route', 'origin_warehouse', 'cargo_description',
            'weight_kg', 'volume_cbm', 'pieces_count',
            'receiver_name', 'receiver_phone', 'receiver_address'
        ]
        widgets = {
            'route': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-base sm:text-sm text-slate-800'
            }),
            'origin_warehouse': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-base sm:text-sm text-slate-800'
            }),
            'cargo_description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'List items, brands, carton descriptions, quantity...',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-base sm:text-sm text-slate-800'
            }),
            'weight_kg': forms.NumberInput(attrs={
                'step': '0.1',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-base sm:text-sm text-slate-800'
            }),
            'volume_cbm': forms.NumberInput(attrs={
                'step': '0.001',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-base sm:text-sm text-slate-800'
            }),
            'pieces_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-base sm:text-sm text-slate-800'
            }),
            'receiver_name': forms.TextInput(attrs={
                'placeholder': 'Full Name of recipient in destination city',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-base sm:text-sm text-slate-800'
            }),
            'receiver_phone': forms.TextInput(attrs={
                'placeholder': '+234 801 234 5678',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-base sm:text-sm text-slate-800'
            }),
            'receiver_address': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Delivery address or preferred Ralyn’s pickup hub',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-base sm:text-sm text-slate-800'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['route'].queryset = Route.objects.filter(is_active=True)
        self.fields['origin_warehouse'].queryset = Warehouse.objects.filter(is_active=True, is_receiving_hub=True)
