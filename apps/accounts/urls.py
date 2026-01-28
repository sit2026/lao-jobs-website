"""
Account URL configuration.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('verify-phone/', views.verify_phone_view, name='verify_phone'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('change-password/', views.change_password_view, name='change_password'),
]
