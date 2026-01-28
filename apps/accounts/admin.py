"""
Account admin configuration.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PhoneVerification, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'user_type', 'is_active', 'is_phone_verified', 'created_at']
    list_filter = ['user_type', 'is_active', 'is_phone_verified', 'is_staff']
    search_fields = ['email']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('ຂໍ້ມູນສ່ວນຕົວ', {'fields': ('user_type',)}),
        ('ສິດທິ', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_phone_verified', 'groups', 'user_permissions')}),
        ('ວັນທີສຳຄັນ', {'fields': ('last_login', 'last_login_ip', 'created_at', 'updated_at')}),
    )

    readonly_fields = ['created_at', 'updated_at', 'last_login', 'last_login_ip']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type'),
        }),
    )


@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'status', 'attempts', 'created_at']
    list_filter = ['status']
    search_fields = ['user__email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['email', 'ip_address', 'success', 'created_at']
    list_filter = ['success']
    search_fields = ['email', 'ip_address']
    readonly_fields = ['created_at']
