"""
Company admin configuration.
"""
from django.contrib import admin
from .models import Company, CompanyContact


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'phone_number', 'status', 'created_at']
    list_filter = ['status', 'province']
    search_fields = ['company_name', 'email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'province']

    fieldsets = (
        ('ຂໍ້ມູນຫຼັກ', {
            'fields': ('user', 'company_name', 'email', 'phone_number', 'phone_normalized')
        }),
        ('ຂໍ້ມູນເພີ່ມເຕີມ', {
            'fields': ('description', 'address', 'province', 'website', 'logo')
        }),
        ('ສະຖານະ', {
            'fields': ('status', 'is_deleted', 'deleted_at')
        }),
        ('ວັນທີ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CompanyContact)
class CompanyContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'phone_number', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['name', 'company__company_name', 'phone_number']
    raw_id_fields = ['company']
