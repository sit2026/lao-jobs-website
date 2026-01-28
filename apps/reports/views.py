"""
Report views.
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Report, ReportReason
from apps.jobs.models import JobPost


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
@require_http_methods(['POST'])
def report_job_view(request, job_id):
    """
    Submit a report for a job post.
    """
    job = get_object_or_404(
        JobPost,
        id=job_id,
        status='published',
        is_deleted=False
    )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    reason_id = data.get('reason_id')
    description = data.get('description', '').strip()
    reporter_phone = data.get('phone', '').strip()

    if not reason_id:
        return JsonResponse({'error': 'ກະລຸນາເລືອກເຫດຜົນ'}, status=400)

    reason = ReportReason.objects.filter(id=reason_id, is_active=True).first()
    if not reason:
        return JsonResponse({'error': 'ເຫດຜົນບໍ່ຖືກຕ້ອງ'}, status=400)

    # Create report
    report = Report.objects.create(
        job_post=job,
        reason=reason,
        description=description,
        reporter_phone=reporter_phone,
        reporter_ip=get_client_ip(request),
    )

    return JsonResponse({
        'success': True,
        'message': 'ສົ່ງລາຍງານສຳເລັດ. ຂອບໃຈທີ່ຊ່ວຍແຈ້ງ.',
        'report_id': str(report.id),
    }, status=201)


def report_reasons_view(request):
    """
    Get list of report reasons.
    """
    reasons = ReportReason.active_objects.all()

    return JsonResponse({
        'reasons': [
            {'id': r.id, 'name': r.name}
            for r in reasons
        ]
    })
