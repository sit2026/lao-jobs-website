"""
Account Celery tasks.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def cleanup_expired_otp():
    """
    Clean up expired OTP records older than 24 hours.
    """
    from .models import PhoneVerification

    cutoff = timezone.now() - timedelta(hours=24)

    deleted, _ = PhoneVerification.objects.filter(
        created_at__lt=cutoff
    ).delete()

    return {'deleted': deleted}


@shared_task
def cleanup_login_attempts():
    """
    Clean up login attempts older than 30 days.
    """
    from .models import LoginAttempt

    cutoff = timezone.now() - timedelta(days=30)

    deleted, _ = LoginAttempt.objects.filter(
        created_at__lt=cutoff
    ).delete()

    return {'deleted': deleted}
