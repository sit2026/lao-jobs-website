"""
Billing Celery tasks.
"""
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import timedelta


@shared_task
def expire_subscriptions():
    """
    Expire subscriptions that have passed their expiry date.
    """
    from .models import Subscription

    now = timezone.now()

    with transaction.atomic():
        expired = Subscription.objects.filter(
            status='active',
            expires_at__lt=now
        ).select_for_update()

        count = 0
        for sub in expired:
            sub.status = 'expired'
            sub.save(update_fields=['status', 'updated_at'])
            count += 1

            # Create audit log
            from apps.audit.models import AuditLog
            AuditLog.objects.create(
                actor_type='system',
                action='expire',
                target_type='Subscription',
                target_id=str(sub.id),
            )

    return {'expired': count}


@shared_task
def purge_expired_invoices():
    """
    Purge expired invoices older than 90 days.
    """
    from .models import Invoice

    cutoff = timezone.now() - timedelta(days=90)

    deleted, _ = Invoice.objects.filter(
        status='expired',
        created_at__lt=cutoff
    ).delete()

    return {'purged': deleted}


@shared_task
def send_expiry_reminders():
    """
    Send subscription expiry reminders.
    Sends reminders at 30, 7, and 1 day before expiry.
    """
    from .models import Subscription

    now = timezone.now()
    reminder_days = [30, 7, 1]

    total_sent = 0

    for days in reminder_days:
        target_date = now + timedelta(days=days)
        start = target_date.replace(hour=0, minute=0, second=0)
        end = target_date.replace(hour=23, minute=59, second=59)

        subscriptions = Subscription.objects.filter(
            status='active',
            expires_at__gte=start,
            expires_at__lte=end
        ).select_related('company', 'company__user')

        for sub in subscriptions:
            # TODO: Send reminder via email/WhatsApp
            # send_expiry_reminder_email.delay(sub.company.user.email, days)
            total_sent += 1

    return {'reminders_sent': total_sent}


@shared_task
def expire_pending_invoices():
    """
    Expire invoices that have been pending for too long.
    """
    from .models import Invoice

    # Expire invoices with expired QR codes
    now = timezone.now()

    expired = Invoice.objects.filter(
        status='pending',
        qr_expires_at__lt=now
    ).update(status='expired')

    return {'expired': expired}
