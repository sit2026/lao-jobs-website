"""
Billing models for subscriptions and payments.
"""
import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.core.utils import generate_invoice_number, generate_payment_reference


class SubscriptionPlan(TimeStampedModel):
    """
    Subscription plan model.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=100,
        verbose_name='ຊື່ແພັກເກດ'
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='ລາຄາ (LAK)'
    )
    duration_days = models.PositiveIntegerField(
        verbose_name='ໄລຍະເວລາ (ມື້)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='ລາຍລະອຽດ'
    )
    features = models.JSONField(
        default=list,
        verbose_name='ຄຸນສົມບັດ'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='ໃຊ້ງານຢູ່'
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name='ລຳດັບ'
    )

    class Meta:
        verbose_name = 'ແພັກເກດ'
        verbose_name_plural = 'ແພັກເກດ'
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.name} - {self.price:,.0f} LAK'


class Subscription(TimeStampedModel):
    """
    Company subscription model.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'ໃຊ້ງານໄດ້'
        EXPIRED = 'expired', 'ໝົດອາຍຸ'
        SUSPENDED = 'suspended', 'ຖືກລະງັບ'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='ບໍລິສັດ'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='ແພັກເກດ'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name='ສະຖານະ'
    )
    starts_at = models.DateTimeField(
        verbose_name='ວັນທີເລີ່ມ'
    )
    expires_at = models.DateTimeField(
        db_index=True,
        verbose_name='ວັນທີໝົດອາຍຸ'
    )

    class Meta:
        verbose_name = 'ສະມາຊິກ'
        verbose_name_plural = 'ສະມາຊິກ'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['status', 'expires_at']),
        ]

    def __str__(self):
        return f'{self.company.company_name} - {self.status}'

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def days_remaining(self):
        if self.is_expired:
            return 0
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)


class Invoice(TimeStampedModel):
    """
    Invoice model for payments.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'ລໍຖ້າຊຳລະ'
        PAID = 'paid', 'ຊຳລະແລ້ວ'
        EXPIRED = 'expired', 'ໝົດອາຍຸ'
        CANCELLED = 'cancelled', 'ຍົກເລີກ'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='ເລກໃບແຈ້ງໜີ້'
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name='ບໍລິສັດ'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='ແພັກເກດ'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='ຈຳນວນເງິນ'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name='ສະຖານະ'
    )

    # Payment info
    payment_reference = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='ລະຫັດອ້າງອີງ'
    )
    qr_code_url = models.URLField(
        blank=True,
        verbose_name='QR Code URL'
    )
    qr_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='QR ໝົດອາຍຸ'
    )

    # Payment completion
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='ວັນທີຊຳລະ'
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Transaction ID'
    )

    class Meta:
        verbose_name = 'ໃບແຈ້ງໜີ້'
        verbose_name_plural = 'ໃບແຈ້ງໜີ້'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['payment_reference']),
        ]

    def __str__(self):
        return f'{self.invoice_number} - {self.status}'

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = generate_invoice_number()
        if not self.payment_reference:
            self.payment_reference = generate_payment_reference()
        super().save(*args, **kwargs)

    @property
    def is_qr_expired(self):
        if not self.qr_expires_at:
            return True
        return timezone.now() > self.qr_expires_at


class Payment(TimeStampedModel):
    """
    Payment transaction model.
    """

    class Status(models.TextChoices):
        INITIATED = 'initiated', 'ເລີ່ມຕົ້ນ'
        PROCESSING = 'processing', 'ກຳລັງດຳເນີນການ'
        COMPLETED = 'completed', 'ສຳເລັດ'
        FAILED = 'failed', 'ລົ້ມເຫຼວ'
        REFUNDED = 'refunded', 'ຄືນເງິນ'

    class Gateway(models.TextChoices):
        BCEL = 'bcel', 'BCEL One'
        ONEPAY = 'onepay', 'OnePay'
        MANUAL = 'manual', 'Manual'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='ໃບແຈ້ງໜີ້'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='ຈຳນວນເງິນ'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INITIATED,
        verbose_name='ສະຖານະ'
    )
    gateway = models.CharField(
        max_length=50,
        choices=Gateway.choices,
        verbose_name='ຊ່ອງທາງຊຳລະ'
    )
    gateway_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Gateway Transaction ID'
    )
    idempotency_key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Idempotency Key'
    )
    gateway_response = models.JSONField(
        default=dict,
        verbose_name='Gateway Response'
    )

    class Meta:
        verbose_name = 'ການຊຳລະ'
        verbose_name_plural = 'ການຊຳລະ'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.invoice.invoice_number} - {self.status}'
