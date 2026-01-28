"""
Jobs API views.
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from .models import JobPost, JobApplication, SavedJob, JobAlert
from apps.core.validators import normalize_phone_number


@require_http_methods(['GET'])
def job_list_api(request):
    """
    API endpoint for job listing.
    """
    jobs = JobPost.objects.filter(
        status='published',
        is_deleted=False
    ).select_related('company', 'category', 'province').order_by('-published_at')

    # Apply filters
    q = request.GET.get('q')
    category = request.GET.get('category')
    province = request.GET.get('province')
    job_type = request.GET.get('job_type')
    salary_min = request.GET.get('salary_min')

    if q:
        jobs = jobs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(company__company_name__icontains=q)
        )

    if category:
        jobs = jobs.filter(category_id=category)

    if province:
        jobs = jobs.filter(province_id=province)

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    if salary_min:
        jobs = jobs.filter(
            Q(salary_max__gte=salary_min) |
            Q(salary_min__gte=salary_min)
        )

    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(jobs, per_page)
    jobs_page = paginator.get_page(page)

    # Serialize
    results = []
    for job in jobs_page:
        results.append({
            'id': str(job.id),
            'title': job.title,
            'company': {
                'id': str(job.company.id),
                'name': job.company.company_name,
                'logo': job.company.logo.url if job.company.logo else None,
            },
            'category': {
                'id': job.category.id if job.category else None,
                'name': job.category.name if job.category else None,
            },
            'province': {
                'id': job.province.id if job.province else None,
                'name': job.province.name if job.province else None,
            },
            'job_type': job.job_type,
            'job_type_display': job.get_job_type_display(),
            'salary_display': job.get_salary_display(),
            'days_remaining': job.days_remaining,
            'view_count': job.view_count,
            'published_at': job.published_at.isoformat() if job.published_at else None,
        })

    return JsonResponse({
        'count': paginator.count,
        'page': page,
        'total_pages': paginator.num_pages,
        'results': results,
    })


@require_http_methods(['GET'])
def job_detail_api(request, job_id):
    """
    API endpoint for job detail.
    """
    job = get_object_or_404(
        JobPost.objects.select_related('company', 'category', 'province'),
        id=job_id,
        status='published',
        is_deleted=False
    )

    return JsonResponse({
        'id': str(job.id),
        'title': job.title,
        'description': job.description,
        'requirements': job.requirements,
        'benefits': job.benefits,
        'company': {
            'id': str(job.company.id),
            'name': job.company.company_name,
            'logo': job.company.logo.url if job.company.logo else None,
            'description': job.company.description,
        },
        'category': {
            'id': job.category.id if job.category else None,
            'name': job.category.name if job.category else None,
        },
        'province': {
            'id': job.province.id if job.province else None,
            'name': job.province.name if job.province else None,
        },
        'job_type': job.job_type,
        'job_type_display': job.get_job_type_display(),
        'positions_count': job.positions_count,
        'salary_min': float(job.salary_min) if job.salary_min else None,
        'salary_max': float(job.salary_max) if job.salary_max else None,
        'salary_negotiable': job.salary_negotiable,
        'salary_display': job.get_salary_display(),
        'contact_email': job.contact_email,
        'contact_phone': job.contact_phone,
        'contact_whatsapp': job.contact_whatsapp,
        'contact_messenger': job.contact_messenger,
        'days_remaining': job.days_remaining,
        'view_count': job.view_count,
        'published_at': job.published_at.isoformat() if job.published_at else None,
    })


@csrf_exempt
@require_http_methods(['POST'])
def job_apply_api(request, job_id):
    """
    API endpoint for quick apply.
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

    full_name = data.get('full_name', '').strip()
    phone_number = data.get('phone_number', '').strip()
    email = data.get('email', '').strip()
    cover_message = data.get('cover_message', '').strip()

    # Validation
    if not full_name:
        return JsonResponse({'error': 'ກະລຸນາໃສ່ຊື່'}, status=400)

    if not phone_number:
        return JsonResponse({'error': 'ກະລຸນາໃສ່ເບີໂທ'}, status=400)

    try:
        phone_normalized = normalize_phone_number(phone_number)
    except Exception:
        return JsonResponse({'error': 'ເບີໂທບໍ່ຖືກຕ້ອງ'}, status=400)

    # Check for duplicate application
    existing = JobApplication.objects.filter(
        job_post=job,
        phone_normalized=phone_normalized
    ).exists()

    if existing:
        return JsonResponse({'error': 'ທ່ານໄດ້ສະໝັກວຽກນີ້ແລ້ວ'}, status=400)

    # Create application
    application = JobApplication.objects.create(
        job_post=job,
        full_name=full_name,
        phone_number=phone_number,
        phone_normalized=phone_normalized,
        email=email,
        cover_message=cover_message,
    )

    return JsonResponse({
        'success': True,
        'message': 'ສະໝັກວຽກສຳເລັດ!',
        'application_id': str(application.id),
    }, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def save_job_api(request, job_id):
    """
    API endpoint for saving/unsaving a job.
    """
    job = get_object_or_404(
        JobPost,
        id=job_id,
        status='published',
        is_deleted=False
    )

    # Get or create session key
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # Toggle save
    saved, created = SavedJob.objects.get_or_create(
        job_post=job,
        session_key=session_key,
    )

    if not created:
        saved.delete()
        return JsonResponse({
            'saved': False,
            'message': 'ລົບອອກຈາກລາຍການບັນທຶກ'
        })

    return JsonResponse({
        'saved': True,
        'message': 'ບັນທຶກວຽກສຳເລັດ'
    })


@csrf_exempt
@require_http_methods(['POST'])
def create_job_alert_api(request):
    """
    API endpoint for creating job alerts.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    phone_number = data.get('phone_number', '').strip()
    keywords = data.get('keywords', '').strip()
    category_id = data.get('category_id')
    province_id = data.get('province_id')
    channel = data.get('channel', 'whatsapp')
    frequency = data.get('frequency', 'instant')

    # Validation
    if not phone_number:
        return JsonResponse({'error': 'ກະລຸນາໃສ່ເບີໂທ'}, status=400)

    try:
        phone_normalized = normalize_phone_number(phone_number)
    except Exception:
        return JsonResponse({'error': 'ເບີໂທບໍ່ຖືກຕ້ອງ'}, status=400)

    # Create or update alert
    alert, created = JobAlert.objects.update_or_create(
        phone_normalized=phone_normalized,
        defaults={
            'phone_number': phone_number,
            'keywords': keywords,
            'category_id': category_id,
            'province_id': province_id,
            'channel': channel,
            'frequency': frequency,
            'is_active': True,
        }
    )

    return JsonResponse({
        'success': True,
        'created': created,
        'message': 'ສ້າງການແຈ້ງເຕືອນສຳເລັດ!',
        'alert_id': str(alert.id),
    }, status=201 if created else 200)
