"""
Audit admin configuration.
"""
from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'actor_type', 'action', 'target_type', 'target_id']
    list_filter = ['actor_type', 'action', 'target_type']
    search_fields = ['actor_id', 'target_id', 'action']
    readonly_fields = [
        'id', 'created_at', 'actor_type', 'actor_id', 'action',
        'target_type', 'target_id', 'details', 'ip_address', 'user_agent'
    ]
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
