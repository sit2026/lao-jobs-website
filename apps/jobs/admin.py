"""
Jobs admin configuration.
"""
from django.contrib import admin
from .models import (
    Province, Category, JobPost, JobApplication,
    SavedJob, JobAlert, QuickFilter, JobTemplate
)


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'slug', 'sort_order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['sort_order', 'is_active']
    search_fields = ['name', 'name_en']
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'slug', 'icon', 'sort_order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['sort_order', 'is_active', 'icon']
    search_fields = ['name', 'name_en']
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'status', 'job_type', 'view_count', 'published_at', 'expires_at']
    list_filter = ['status', 'job_type', 'category', 'province', 'is_deleted']
    search_fields = ['title', 'company__company_name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'view_count']
    raw_id_fields = ['company', 'category', 'province']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('ຂໍ້ມູນຫຼັກ', {
            'fields': ('company', 'title', 'category', 'province')
        }),
        ('ລາຍລະອຽດ', {
            'fields': ('description', 'requirements', 'benefits')
        }),
        ('ເງິນເດືອນ & ປະເພດ', {
            'fields': ('salary_min', 'salary_max', 'salary_negotiable', 'job_type', 'positions_count')
        }),
        ('ຕິດຕໍ່', {
            'fields': ('contact_email', 'contact_phone', 'contact_whatsapp', 'contact_messenger')
        }),
        ('ສະຖານະ', {
            'fields': ('status', 'published_at', 'expires_at', 'is_deleted', 'deleted_at')
        }),
        ('ສະຖິຕິ', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return JobPost.all_objects.all()


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'job_post', 'phone_number', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['full_name', 'phone_number', 'email', 'job_post__title']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['job_post']


@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'keywords', 'category', 'province', 'channel', 'is_active', 'is_verified']
    list_filter = ['is_active', 'is_verified', 'channel', 'frequency']
    search_fields = ['phone_number', 'keywords']
    readonly_fields = ['created_at', 'updated_at', 'last_sent_at']


@admin.register(QuickFilter)
class QuickFilterAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'sort_order', 'is_active']
    list_editable = ['sort_order', 'is_active']


@admin.register(JobTemplate)
class JobTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'category', 'sort_order', 'is_active']
    list_filter = ['template_type', 'is_active']
    list_editable = ['sort_order', 'is_active']
    raw_id_fields = ['company', 'category']
