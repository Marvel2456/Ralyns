from django import forms
from django.contrib.auth import authenticate
from .models import CustomUser

class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-slate-800'
        }),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-slate-800'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'e.g. Johnathan Adeyemi',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-slate-800'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'john@example.com',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-slate-800'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+234 801 234 5678',
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-slate-800'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'your-email@example.com',
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-slate-800'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-slate-800'
        })
    )


class OTPVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': '123456',
            'class': 'w-full text-center tracking-[0.5em] text-2xl font-bold font-mono px-4 py-4 rounded-xl border-2 border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#D87808] focus:border-transparent transition text-slate-900',
            'maxlength': '6',
            'autocomplete': 'one-time-code',
            'autofocus': 'autofocus'
        })
    )
