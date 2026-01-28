"""
Core abstract models for the Lao Jobs project.
"""
import uuid
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract model with created_at and updated_at fields.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='ວັນທີສ້າງ'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='ວັນທີອັບເດດ'
    )

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Manager that filters out soft-deleted objects.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    """
    Abstract model for soft delete functionality.
    """
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='ຖືກລົບ'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='ວັນທີລົບ'
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        """Soft delete the object."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])


class UUIDModel(models.Model):
    """
    Abstract model with UUID as primary key.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    Combined abstract model with UUID, timestamps, and soft delete.
    """
    class Meta:
        abstract = True


class ActiveManager(models.Manager):
    """
    Manager that filters only active objects.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class ActiveModel(models.Model):
    """
    Abstract model with is_active field.
    """
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name='ໃຊ້ງານຢູ່'
    )

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        abstract = True


class SortableModel(models.Model):
    """
    Abstract model with sort_order field.
    """
    sort_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name='ລຳດັບ'
    )

    class Meta:
        abstract = True
        ordering = ['sort_order']
