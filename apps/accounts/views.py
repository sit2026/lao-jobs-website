"""
Account views for authentication.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta

from .forms import LoginForm, EmployerRegistrationForm, OTPVerificationForm, ChangePasswordForm
from .models import User, PhoneVerification, LoginAttempt
from apps.core.utils import generate_otp


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """
    Login view for all users.
    """
    if request.user.is_authenticated:
        return redirect('employer:dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        # Record login attempt
        ip = get_client_ip(request)

        if form.is_valid():
            user = form.get_user()

            # Check remember me
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)

            # Update last login IP
            user.last_login_ip = ip
            user.save(update_fields=['last_login_ip'])

            # Log successful attempt
            LoginAttempt.objects.create(
                email=user.email,
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True
            )

            login(request, user)

            # Redirect based on user type
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            if user.is_admin:
                return redirect('admin:index')
            return redirect('employer:dashboard')
        else:
            # Log failed attempt
            LoginAttempt.objects.create(
                email=request.POST.get('email', ''),
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=False
            )
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


@require_http_methods(['POST'])
def logout_view(request):
    """
    Logout view.
    """
    logout(request)
    messages.success(request, 'ອອກຈາກລະບົບສຳເລັດ')
    return redirect('jobs:home')


@require_http_methods(['GET', 'POST'])
def register_view(request):
    """
    Employer registration view.
    """
    if request.user.is_authenticated:
        return redirect('employer:dashboard')

    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create company profile
            from apps.companies.models import Company
            Company.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                email=user.email,
                phone_number=form.cleaned_data['phone_number'],
                phone_normalized=form.cleaned_data['phone_number'],
                status=Company.Status.PENDING
            )

            # Login the user
            login(request, user)

            # Mark phone as verified (skip OTP for now - no SMS service)
            user.is_phone_verified = True
            user.save(update_fields=['is_phone_verified'])

            messages.success(request, 'ລົງທະບຽນສຳເລັດ!')
            return redirect('employer:dashboard')
    else:
        form = EmployerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
@require_http_methods(['GET', 'POST'])
def verify_phone_view(request):
    """
    Phone number OTP verification view.
    """
    from django.conf import settings

    user = request.user

    if user.is_phone_verified:
        messages.info(request, 'ເບີໂທໄດ້ຢືນຢັນແລ້ວ')
        return redirect('employer:dashboard')

    # Get company phone number
    company = getattr(user, 'company', None)
    if not company:
        messages.error(request, 'ບໍ່ພົບຂໍ້ມູນບໍລິສັດ')
        return redirect('employer:dashboard')

    phone_number = company.phone_number

    # Get or create verification
    verification = PhoneVerification.objects.filter(
        user=user,
        status=PhoneVerification.Status.PENDING
    ).first()

    # Create new verification if needed
    if not verification or verification.is_expired:
        otp_expiry_minutes = settings.LAO_JOBS.get('OTP_EXPIRY_MINUTES', 5)

        verification = PhoneVerification.objects.create(
            user=user,
            phone_number=phone_number,
            phone_normalized=phone_number,
            otp_code=generate_otp(),
            otp_expires_at=timezone.now() + timedelta(minutes=otp_expiry_minutes)
        )

        # TODO: Send OTP via SMS/WhatsApp
        # For now, display in development
        if settings.DEBUG:
            messages.info(request, f'[DEV] OTP Code: {verification.otp_code}')

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            success, error = verification.verify(form.cleaned_data['otp_code'])
            if success:
                messages.success(request, 'ຢືນຢັນເບີໂທສຳເລັດ!')
                return redirect('billing:choose_plan')
            else:
                form.add_error('otp_code', error)
    else:
        form = OTPVerificationForm()

    return render(request, 'accounts/verify_phone.html', {
        'form': form,
        'phone_number': phone_number,
        'expires_at': verification.otp_expires_at,
    })


@login_required
@require_http_methods(['POST'])
def resend_otp_view(request):
    """
    Resend OTP code.
    """
    from django.conf import settings
    from django.http import JsonResponse

    user = request.user
    company = getattr(user, 'company', None)

    if not company:
        return JsonResponse({'error': 'ບໍ່ພົບຂໍ້ມູນບໍລິສັດ'}, status=400)

    # Check rate limit (1 per minute)
    recent = PhoneVerification.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(minutes=1)
    ).exists()

    if recent:
        return JsonResponse({'error': 'ກະລຸນາລໍຖ້າ 1 ນາທີ'}, status=429)

    # Create new verification
    otp_expiry_minutes = settings.LAO_JOBS.get('OTP_EXPIRY_MINUTES', 5)

    verification = PhoneVerification.objects.create(
        user=user,
        phone_number=company.phone_number,
        phone_normalized=company.phone_number,
        otp_code=generate_otp(),
        otp_expires_at=timezone.now() + timedelta(minutes=otp_expiry_minutes)
    )

    # TODO: Send OTP via SMS/WhatsApp

    return JsonResponse({
        'success': True,
        'message': 'ສົ່ງລະຫັດ OTP ໃໝ່ແລ້ວ',
        'expires_at': verification.otp_expires_at.isoformat(),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def change_password_view(request):
    """
    Change password view.
    """
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'ປ່ຽນລະຫັດຜ່ານສຳເລັດ')
            return redirect('employer:settings')
    else:
        form = ChangePasswordForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
