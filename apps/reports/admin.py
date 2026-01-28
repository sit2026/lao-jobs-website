"""
Reports admin configuration.
"""
from django.contrib import admin
from django.utils import timezone
from .models import ReportReason, Report


@admin.register(ReportReason)
class ReportReasonAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order', 'is_active']
    list_editable = ['sort_order', 'is_active']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['job_post', 'reason', 'status', 'reporter_phone', 'created_at']
    list_filter = ['status', 'reason']
    search_fields = ['job_post__title', 'reporter_phone', 'description']
    readonly_fields = ['created_at', 'updated_at', 'reporter_ip']
    raw_id_fields = ['job_post', 'reason', 'resolved_by']

    fieldsets = (
        ('ຂໍ້ມູນລາຍງານ', {
            'fields': ('job_post', 'reason', 'description')
        }),
        ('ຜູ້ລາຍງານ', {
            'fields': ('reporter_phone', 'reporter_ip')
        }),
        ('ສະຖານະ', {
            'fields': ('status', 'resolved_at', 'resolved_by', 'resolution_note')
        }),
        ('ວັນທີ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_resolved', 'mark_dismissed']

    def mark_resolved(self, request, queryset):
        queryset.update(
            status='resolved',
            resolved_at=timezone.now(),
            resolved_by=request.user
        )
    mark_resolved.short_description = 'ໝາຍເປັນແກ້ໄຂແລ້ວ'

    def mark_dismissed(self, request, queryset):
        queryset.update(
            status='dismissed',
            resolved_at=timezone.now(),
            resolved_by=request.user
        )
    mark_dismissed.short_description = 'ໝາຍເປັນຍົກເລີກ'
