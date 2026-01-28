"""
Company models.
"""
import uuid
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel, SoftDeleteModel
from apps.core.validators import validate_image_size, validate_image_extension


def company_logo_path(instance, filename):
    """Generate upload path for company logo."""
    ext = filename.split('.')[-1]
    return f'companies/{instance.id}/logo.{ext}'


class Company(TimeStampedModel, SoftDeleteModel):
    """
    Company profile model.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'ລໍຖ້າອະນຸມັດ'
        ACTIVE = 'active', 'ໃຊ້ງານໄດ້'
        SUSPENDED = 'suspended', 'ຖືກລະງັບ'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='company',
        verbose_name='ຜູ້ໃຊ້'
    )

    # Required fields
    company_name = models.CharField(
        max_length=150,
        verbose_name='ຊື່ບໍລິສັດ'
    )
    email = models.EmailField(
        verbose_name='ອີເມວຕິດຕໍ່'
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name='ເບີໂທ'
    )
    phone_normalized = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name='ເບີໂທ (normalized)'
    )

    # Optional fields
    description = models.TextField(
        blank=True,
        verbose_name='ລາຍລະອຽດບໍລິສັດ'
    )
    address = models.TextField(
        blank=True,
        verbose_name='ທີ່ຢູ່'
    )
    province = models.ForeignKey(
        'jobs.Province',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='ແຂວງ'
    )
    website = models.URLField(
        blank=True,
        verbose_name='ເວັບໄຊ'
    )
    logo = models.ImageField(
        upload_to=company_logo_path,
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_extension],
        verbose_name='ໂລໂກ້'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name='ສະຖານະ'
    )

    class Meta:
        verbose_name = 'ບໍລິສັດ'
        verbose_name_plural = 'ບໍລິສັດ'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'company_name']),
            models.Index(fields=['province', 'status']),
        ]

    def __str__(self):
        return self.company_name

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property
    def active_subscription(self):
        """Get active subscription if exists."""
        return self.subscriptions.filter(
            status='active',
            expires_at__gt=timezone.now()
        ).first()

    @property
    def has_active_subscription(self):
        """Check if company has an active subscription."""
        return self.active_subscription is not None

    def can_create_job(self):
        """
        Check if company can create a new job post.
        Returns: (can_create, error_message)
        """
        if self.status != self.Status.ACTIVE:
            return False, 'ບໍລິສັດຍັງບໍ່ໄດ້ຮັບການອະນຸມັດ'

        if not self.has_active_subscription:
            return False, 'ສະມາຊິກໝົດອາຍຸ. ກະລຸນາຕໍ່ອາຍຸສະມາຊິກ.'

        return True, None

    def get_published_jobs_count(self):
        """Get count of published jobs."""
        return self.job_posts.filter(status='published').count()

    def get_total_views(self):
        """Get total views across all jobs."""
        from django.db.models import Sum
        result = self.job_posts.aggregate(total=Sum('view_count'))
        return result['total'] or 0


class CompanyContact(TimeStampedModel):
    """
    Additional contact persons for a company.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name='ບໍລິສັດ'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='ຊື່'
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ຕຳແໜ່ງ'
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name='ເບີໂທ'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='ອີເມວ'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name='ເປັນຜູ້ຕິດຕໍ່ຫຼັກ'
    )

    class Meta:
        verbose_name = 'ຜູ້ຕິດຕໍ່'
        verbose_name_plural = 'ຜູ້ຕິດຕໍ່'
        ordering = ['-is_primary', 'name']

    def __str__(self):
        return f'{self.name} - {self.company.company_name}'
