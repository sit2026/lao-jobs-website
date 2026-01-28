"""
Billing views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import json

from .models import SubscriptionPlan, Invoice, Subscription
from .services import create_invoice, process_payment
from apps.companies.views import employer_required


@employer_required
def choose_plan_view(request):
    """
    View to choose subscription plan.
    """
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order')

    return render(request, 'billing/choose_plan.html', {
        'plans': plans,
        'company': request.user.company,
    })


@employer_required
@require_http_methods(['POST'])
def create_invoice_view(request):
    """
    Create invoice for selected plan.
    """
    plan_id = request.POST.get('plan_id')

    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    company = request.user.company

    # Create invoice
    invoice = create_invoice(company, plan)

    return redirect('billing:payment', invoice_id=invoice.id)


@employer_required
def payment_view(request, invoice_id):
    """
    Payment page with QR code.
    """
    company = request.user.company
    invoice = get_object_or_404(Invoice, id=invoice_id, company=company)

    # Check if already paid
    if invoice.status == 'paid':
        messages.success(request, 'ໃບແຈ້ງໜີ້ນີ້ຊຳລະແລ້ວ')
        return redirect('employer:dashboard')

    # Check if expired
    if invoice.status == 'expired':
        messages.error(request, 'ໃບແຈ້ງໜີ້ນີ້ໝົດອາຍຸ. ກະລຸນາສ້າງໃໝ່.')
        return redirect('billing:choose_plan')

    return render(request, 'billing/payment.html', {
        'invoice': invoice,
        'company': company,
    })


@employer_required
@require_http_methods(['POST'])
def verify_payment_view(request, invoice_id):
    """
    Manual payment verification trigger.
    """
    company = request.user.company
    invoice = get_object_or_404(Invoice, id=invoice_id, company=company)

    if invoice.status == 'paid':
        return JsonResponse({
            'status': 'already_paid',
            'message': 'ໃບແຈ້ງໜີ້ນີ້ຊຳລະແລ້ວ'
        })

    # In production, this would call the payment gateway to verify
    # For now, we just return the current status
    return JsonResponse({
        'status': invoice.status,
        'message': 'ກຳລັງກວດສອບ... ກະລຸນາລໍຖ້າ'
    })


@require_http_methods(['POST'])
def webhook_view(request):
    """
    Payment gateway webhook handler.
    """
    # Verify webhook signature (implement based on gateway)
    # signature = request.headers.get('X-Signature')
    # if not verify_signature(request.body, signature):
    #     return JsonResponse({'error': 'Invalid signature'}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    event = data.get('event')
    payment_reference = data.get('payment_reference')
    transaction_id = data.get('transaction_id')

    if event == 'payment.completed' and payment_reference:
        result = process_payment(payment_reference, transaction_id, data)
        return JsonResponse(result)

    return JsonResponse({'status': 'ignored'})


@employer_required
def subscription_view(request):
    """
    View current subscription status.
    """
    company = request.user.company
    subscription = company.active_subscription
    invoices = company.invoices.order_by('-created_at')[:10]

    return render(request, 'billing/subscription.html', {
        'company': company,
        'subscription': subscription,
        'invoices': invoices,
    })


@employer_required
def invoice_detail_view(request, invoice_id):
    """
    View invoice details.
    """
    company = request.user.company
    invoice = get_object_or_404(Invoice, id=invoice_id, company=company)

    return render(request, 'billing/invoice_detail.html', {
        'invoice': invoice,
        'company': company,
    })
