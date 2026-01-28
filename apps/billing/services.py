"""
Billing services for payment processing.
"""
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from .models import Invoice, Payment, Subscription


@transaction.atomic
def process_payment(payment_reference, gateway_transaction_id, gateway_response):
    """
    Process a payment (idempotent).

    Args:
        payment_reference: The invoice payment reference
        gateway_transaction_id: Transaction ID from payment gateway
        gateway_response: Full response from gateway

    Returns:
        dict: Result with status and subscription if successful
    """
    # Lock invoice row
    try:
        invoice = Invoice.objects.select_for_update().get(
            payment_reference=payment_reference
        )
    except Invoice.DoesNotExist:
        return {'status': 'error', 'message': 'Invoice not found'}

    # Already paid? Skip (idempotent)
    if invoice.status == 'paid':
        return {'status': 'already_processed'}

    # Check if invoice expired
    if invoice.status == 'expired':
        return {'status': 'error', 'message': 'Invoice expired'}

    # Create payment with idempotency key
    idempotency_key = f'{payment_reference}-{gateway_transaction_id}'

    payment, created = Payment.objects.get_or_create(
        idempotency_key=idempotency_key,
        defaults={
            'invoice': invoice,
            'amount': invoice.amount,
            'status': 'completed',
            'gateway': 'bcel',  # Determine from gateway_response
            'gateway_transaction_id': gateway_transaction_id,
            'gateway_response': gateway_response,
        }
    )

    if not created:
        # Payment already processed
        return {'status': 'already_processed'}

    # Update invoice
    invoice.status = 'paid'
    invoice.paid_at = timezone.now()
    invoice.transaction_id = gateway_transaction_id
    invoice.save()

    # Activate subscription
    subscription = activate_subscription(invoice)

    # Update company status
    company = invoice.company
    if company.status == 'pending':
        company.status = 'active'
        company.save(update_fields=['status', 'updated_at'])

    # Create audit log
    from apps.audit.models import AuditLog
    AuditLog.objects.create(
        actor_type='system',
        action='payment',
        target_type='Invoice',
        target_id=str(invoice.id),
        details={
            'payment_reference': payment_reference,
            'transaction_id': gateway_transaction_id,
            'amount': float(invoice.amount),
        }
    )

    return {'status': 'success', 'subscription': subscription}


def activate_subscription(invoice):
    """
    Create or extend subscription based on invoice.

    Args:
        invoice: The paid invoice

    Returns:
        Subscription: The new or extended subscription
    """
    company = invoice.company
    plan = invoice.plan

    if not plan:
        # Use default duration
        duration_days = 365
    else:
        duration_days = plan.duration_days

    # Check for existing active subscription
    existing = Subscription.objects.filter(
        company=company,
        status='active',
        expires_at__gt=timezone.now()
    ).first()

    if existing:
        # Extend existing subscription
        existing.expires_at = existing.expires_at + timedelta(days=duration_days)
        existing.save(update_fields=['expires_at', 'updated_at'])
        return existing
    else:
        # Create new subscription
        now = timezone.now()
        subscription = Subscription.objects.create(
            company=company,
            plan=plan,
            status='active',
            starts_at=now,
            expires_at=now + timedelta(days=duration_days)
        )
        return subscription


def create_invoice(company, plan):
    """
    Create a new invoice for subscription.

    Args:
        company: The company
        plan: The subscription plan

    Returns:
        Invoice: The created invoice
    """
    from django.conf import settings

    qr_expiry_hours = settings.LAO_JOBS.get('QR_EXPIRY_HOURS', 24)

    invoice = Invoice.objects.create(
        company=company,
        plan=plan,
        amount=plan.price,
        qr_expires_at=timezone.now() + timedelta(hours=qr_expiry_hours)
    )

    # Generate QR code (implement based on payment gateway)
    # invoice.qr_code_url = generate_qr_code(invoice)
    # invoice.save()

    return invoice


def verify_payment_manual(invoice, verified_by):
    """
    Manually verify a payment (admin action).

    Args:
        invoice: The invoice to verify
        verified_by: The admin user

    Returns:
        dict: Result
    """
    if invoice.status == 'paid':
        return {'status': 'already_paid'}

    result = process_payment(
        invoice.payment_reference,
        f'MANUAL-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        {'verified_by': str(verified_by.id), 'method': 'manual'}
    )

    if result['status'] == 'success':
        # Log admin action
        from apps.audit.models import AuditLog
        AuditLog.objects.create(
            actor_type='user',
            actor_id=str(verified_by.id),
            action='manual_verify_payment',
            target_type='Invoice',
            target_id=str(invoice.id),
        )

    return result
