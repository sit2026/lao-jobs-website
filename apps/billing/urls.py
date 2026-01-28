"""
Billing URL configuration.
"""
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Plan selection
    path('plans/', views.choose_plan_view, name='choose_plan'),
    path('create-invoice/', views.create_invoice_view, name='create_invoice'),

    # Payment
    path('payment/<uuid:invoice_id>/', views.payment_view, name='payment'),
    path('payment/<uuid:invoice_id>/verify/', views.verify_payment_view, name='verify_payment'),

    # Webhook
    path('webhook/', views.webhook_view, name='webhook'),

    # Subscription management
    path('subscription/', views.subscription_view, name='subscription'),
    path('invoice/<uuid:invoice_id>/', views.invoice_detail_view, name='invoice_detail'),
]
