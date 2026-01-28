"""
Billing admin configuration.
"""
from django.contrib import admin
from .models import SubscriptionPlan, Subscription, Invoice, Payment


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_days', 'is_active', 'sort_order']
    list_editable = ['is_active', 'sort_order']
    list_filter = ['is_active']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['company', 'plan', 'status', 'starts_at', 'expires_at', 'days_remaining']
    list_filter = ['status', 'plan']
    search_fields = ['company__company_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['company', 'plan']

    def days_remaining(self, obj):
        return obj.days_remaining
    days_remaining.short_description = 'ມື້ທີ່ເຫຼືອ'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'company', 'amount', 'status', 'paid_at', 'created_at']
    list_filter = ['status']
    search_fields = ['invoice_number', 'payment_reference', 'company__company_name']
    readonly_fields = ['invoice_number', 'payment_reference', 'created_at', 'updated_at', 'paid_at']
    raw_id_fields = ['company', 'plan']

    fieldsets = (
        ('ຂໍ້ມູນຫຼັກ', {
            'fields': ('invoice_number', 'company', 'plan', 'amount', 'status')
        }),
        ('ການຊຳລະ', {
            'fields': ('payment_reference', 'qr_code_url', 'qr_expires_at', 'paid_at', 'transaction_id')
        }),
        ('ວັນທີ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'gateway', 'status', 'created_at']
    list_filter = ['status', 'gateway']
    search_fields = ['invoice__invoice_number', 'gateway_transaction_id']
    readonly_fields = ['idempotency_key', 'created_at', 'updated_at']
    raw_id_fields = ['invoice']
