"""
Audit log model for tracking all system actions.
"""
import uuid
from django.db import models
from apps.core.models import TimeStampedModel


class AuditLog(models.Model):
    """
    Audit log for tracking all important actions in the system.
    """

    class ActorType(models.TextChoices):
        SYSTEM = 'system', 'ລະບົບ'
        USER = 'user', 'ຜູ້ໃຊ້'
        ADMIN = 'admin', 'ແອດມິນ'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='ເວລາ'
    )

    # Actor info
    actor_type = models.CharField(
        max_length=20,
        choices=ActorType.choices,
        verbose_name='ປະເພດຜູ້ກະທຳ'
    )
    actor_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name='ID ຜູ້ກະທຳ'
    )

    # Action info
    action = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='ການກະທຳ'
    )

    # Target info
    target_type = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='ປະເພດເປົ້າໝາຍ'
    )
    target_id = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='ID ເປົ້າໝາຍ'
    )

    # Additional details
    details = models.JSONField(
        default=dict,
        verbose_name='ລາຍລະອຽດ'
    )

    # Request info
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Address'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )

    class Meta:
        verbose_name = 'ບັນທຶກ'
        verbose_name_plural = 'ບັນທຶກ'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['actor_type', 'actor_id']),
            models.Index(fields=['target_type', 'target_id']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        return f'{self.actor_type}:{self.actor_id} - {self.action} - {self.target_type}:{self.target_id}'


def log_action(
    action,
    target_type,
    target_id,
    actor_type='system',
    actor_id='',
    details=None,
    request=None
):
    """
    Helper function to create audit log entries.

    Args:
        action: The action performed (e.g., 'create', 'update', 'delete', 'expire')
        target_type: The type of object affected (e.g., 'JobPost', 'Invoice')
        target_id: The ID of the affected object
        actor_type: Who performed the action ('system', 'user', 'admin')
        actor_id: The ID of the actor (user ID if applicable)
        details: Additional details dict
        request: Django request object (for IP and user agent)

    Returns:
        AuditLog: The created audit log entry
    """
    ip_address = None
    user_agent = ''

    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        user_agent = request.META.get('HTTP_USER_AGENT', '')

    return AuditLog.objects.create(
        actor_type=actor_type,
        actor_id=str(actor_id) if actor_id else '',
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )
