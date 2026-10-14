from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import CustomUser, EmailOTP
from .forms import CustomerRegistrationForm, LoginForm, OTPVerificationForm
from apps.core.emails import send_account_otp_email
from apps.logistics.models import Shipment, Warehouse
from apps.store.models import Order

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = CustomUser.Role.CUSTOMER
            user.is_active = True
            user.is_email_verified = False
            user.save()

            # Create and dispatch 6-digit OTP via Celery / Resend
            otp = EmailOTP.create_otp(user=user, purpose=EmailOTP.Purpose.REGISTRATION)
            send_account_otp_email(user, otp.code)

            request.session['pending_verification_user_id'] = str(user.id)
            messages.success(request, f"Account created! We've sent a 6-digit verification code to {user.email}.")
            return redirect('accounts:verify_otp')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def verify_otp_view(request):
    user_id = request.session.get('pending_verification_user_id')
    if not user_id:
        messages.warning(request, "No pending registration session found. Please register or log in.")
        return redirect('accounts:register')

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            input_code = form.cleaned_data['code'].strip()
            otp = EmailOTP.objects.filter(
                user=user,
                code=input_code,
                purpose=EmailOTP.Purpose.REGISTRATION,
                is_used=False
            ).first()

            if otp and otp.is_valid():
                otp.is_used = True
                otp.save()

                user.is_email_verified = True
                user.save()

                # Clean session & log user in
                del request.session['pending_verification_user_id']
                login(request, user)
                messages.success(request, f"Welcome to Ralyn's International, {user.full_name}! Your account is verified.")
                return redirect('accounts:dashboard')
            else:
                messages.error(request, "Invalid or expired verification code. Please try again or request a new code.")
    else:
        form = OTPVerificationForm()

    return render(request, 'accounts/verify_otp.html', {'form': form, 'user_email': user.email})


def resend_otp_view(request):
    user_id = request.session.get('pending_verification_user_id')
    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect('accounts:register')

    user = get_object_or_404(CustomUser, id=user_id)
    otp = EmailOTP.create_otp(user=user, purpose=EmailOTP.Purpose.REGISTRATION)
    send_account_otp_email(user, otp.code)
    messages.info(request, f"A fresh verification code has been dispatched to {user.email}.")
    return redirect('accounts:verify_otp')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account has been deactivated. Please contact support.")
                elif not user.is_email_verified:
                    # Resend OTP and redirect to verify
                    request.session['pending_verification_user_id'] = str(user.id)
                    otp = EmailOTP.create_otp(user=user, purpose=EmailOTP.Purpose.REGISTRATION)
                    send_account_otp_email(user, otp.code)
                    messages.warning(request, "Please verify your email address to access your account.")
                    return redirect('accounts:verify_otp')
                else:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.full_name}!")
                    
                    if user.is_moderator:
                        return redirect('moderation:dashboard')
                    return redirect('accounts:dashboard')
            else:
                messages.error(request, "Invalid email address or password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('core:home')


@login_required
def dashboard_view(request):
    user = request.user
    shipments = Shipment.objects.filter(customer=user).select_related('route')
    orders = Order.objects.filter(customer=user).prefetch_related('items')
    warehouses = Warehouse.objects.filter(is_active=True, is_receiving_hub=True)

    context = {
        'shipments': shipments[:10],
        'orders': orders[:10],
        'warehouses': warehouses,
        'active_shipments_count': shipments.exclude(status=Shipment.Status.DELIVERED).count(),
        'delivered_count': shipments.filter(status=Shipment.Status.DELIVERED).count(),
        'orders_count': orders.count(),
    }
    return render(request, 'accounts/dashboard.html', context)
