"""
Report models for content moderation.
"""
import uuid
from django.db import models
from apps.core.models import TimeStampedModel, ActiveModel, SortableModel


class ReportReason(TimeStampedModel, ActiveModel, SortableModel):
    """
    Predefined report reasons.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=100,
        verbose_name='ເຫດຜົນ'
    )

    class Meta:
        verbose_name = 'ເຫດຜົນລາຍງານ'
        verbose_name_plural = 'ເຫດຜົນລາຍງານ'
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class Report(TimeStampedModel):
    """
    User report for job posts.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'ລໍຖ້າ'
        REVIEWING = 'reviewing', 'ກຳລັງກວດສອບ'
        RESOLVED = 'resolved', 'ແກ້ໄຂແລ້ວ'
        DISMISSED = 'dismissed', 'ຍົກເລີກ'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    job_post = models.ForeignKey(
        'jobs.JobPost',
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='ໂພສວຽກ'
    )
    reason = models.ForeignKey(
        ReportReason,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='ເຫດຜົນ'
    )
    description = models.TextField(
        blank=True,
        verbose_name='ລາຍລະອຽດເພີ່ມເຕີມ'
    )

    # Reporter info (optional - anonymous reports allowed)
    reporter_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='ເບີໂທຜູ້ລາຍງານ'
    )
    reporter_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Address'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name='ສະຖານະ'
    )

    # Resolution
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='ວັນທີແກ້ໄຂ'
    )
    resolved_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='resolved_reports',
        verbose_name='ແກ້ໄຂໂດຍ'
    )
    resolution_note = models.TextField(
        blank=True,
        verbose_name='ບັນທຶກການແກ້ໄຂ'
    )

    class Meta:
        verbose_name = 'ການລາຍງານ'
        verbose_name_plural = 'ການລາຍງານ'
        ordering = ['-created_at']

    def __str__(self):
        return f'Report: {self.job_post.title} - {self.status}'
