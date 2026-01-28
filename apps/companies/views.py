"""
Company views (Employer Portal).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Sum

from .models import Company
from .forms import CompanyProfileForm
from apps.jobs.models import JobPost
from apps.jobs.forms import JobPostForm


def employer_required(view_func):
    """Decorator to ensure user is an employer with a company."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'company'):
            messages.error(request, 'ບໍ່ພົບຂໍ້ມູນບໍລິສັດ')
            return redirect('accounts:register')
        return view_func(request, *args, **kwargs)
    return wrapper


@employer_required
def dashboard_view(request):
    """
    Employer dashboard view.
    """
    company = request.user.company
    subscription = company.active_subscription

    # Get job statistics
    jobs = company.job_posts.filter(is_deleted=False)
    published_count = jobs.filter(status='published').count()
    draft_count = jobs.filter(status='draft').count()
    expired_count = jobs.filter(status='expired').count()
    total_views = jobs.aggregate(total=Sum('view_count'))['total'] or 0

    # Get expiring soon jobs (within 3 days)
    from django.utils import timezone
    from datetime import timedelta
    expiring_soon = jobs.filter(
        status='published',
        expires_at__lte=timezone.now() + timedelta(days=3),
        expires_at__gt=timezone.now()
    ).count()

    # Recent jobs
    recent_jobs = jobs.order_by('-created_at')[:5]

    context = {
        'company': company,
        'subscription': subscription,
        'published_count': published_count,
        'draft_count': draft_count,
        'expired_count': expired_count,
        'total_views': total_views,
        'expiring_soon': expiring_soon,
        'recent_jobs': recent_jobs,
    }

    return render(request, 'employer/dashboard.html', context)


@employer_required
@require_http_methods(['GET', 'POST'])
def profile_view(request):
    """
    Company profile edit view.
    """
    company = request.user.company

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'ບັນທຶກຂໍ້ມູນບໍລິສັດສຳເລັດ')
            return redirect('employer:profile')
    else:
        form = CompanyProfileForm(instance=company)

    return render(request, 'employer/profile.html', {
        'form': form,
        'company': company,
    })


@employer_required
def my_jobs_view(request):
    """
    List all jobs for the company.
    """
    company = request.user.company

    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '')

    jobs = company.job_posts.filter(is_deleted=False)

    if status_filter:
        jobs = jobs.filter(status=status_filter)

    if search:
        jobs = jobs.filter(title__icontains=search)

    jobs = jobs.order_by('-created_at')

    # Pagination
    paginator = Paginator(jobs, 10)
    page = request.GET.get('page', 1)
    jobs_page = paginator.get_page(page)

    context = {
        'jobs': jobs_page,
        'status_filter': status_filter,
        'search': search,
        'company': company,
    }

    return render(request, 'employer/my_jobs.html', context)


@employer_required
@require_http_methods(['GET', 'POST'])
def job_create_view(request):
    """
    Create a new job post.
    """
    company = request.user.company

    # Check if can create
    can_create, error = company.can_create_job()
    if not can_create:
        messages.error(request, error)
        return redirect('billing:choose_plan')

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.save()
            messages.success(request, 'ສ້າງໂພສວຽກສຳເລັດ')
            return redirect('employer:job_edit', job_id=job.id)
    else:
        form = JobPostForm()

    return render(request, 'employer/job_form.html', {
        'form': form,
        'company': company,
        'is_edit': False,
    })


@employer_required
@require_http_methods(['GET', 'POST'])
def job_edit_view(request, job_id):
    """
    Edit an existing job post.
    """
    company = request.user.company
    job = get_object_or_404(JobPost, id=job_id, company=company, is_deleted=False)

    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'ບັນທຶກການແກ້ໄຂສຳເລັດ')
            return redirect('employer:my_jobs')
    else:
        form = JobPostForm(instance=job)

    return render(request, 'employer/job_form.html', {
        'form': form,
        'job': job,
        'company': company,
        'is_edit': True,
    })


@employer_required
@require_http_methods(['POST'])
def job_publish_view(request, job_id):
    """
    Publish a job post.
    """
    company = request.user.company
    job = get_object_or_404(JobPost, id=job_id, company=company, is_deleted=False)

    # Check subscription
    can_create, error = company.can_create_job()
    if not can_create:
        messages.error(request, error)
        return redirect('billing:choose_plan')

    if job.status == 'draft':
        job.publish()
        messages.success(request, 'ເຜີຍແຜ່ໂພສວຽກສຳເລັດ')
    else:
        messages.warning(request, 'ບໍ່ສາມາດເຜີຍແຜ່ໂພສນີ້ໄດ້')

    return redirect('employer:my_jobs')


@employer_required
@require_http_methods(['POST'])
def job_close_view(request, job_id):
    """
    Close a job post.
    """
    company = request.user.company
    job = get_object_or_404(JobPost, id=job_id, company=company, is_deleted=False)

    if job.status == 'published':
        job.status = 'closed'
        job.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'ປິດໂພສວຽກສຳເລັດ')
    else:
        messages.warning(request, 'ບໍ່ສາມາດປິດໂພສນີ້ໄດ້')

    return redirect('employer:my_jobs')


@employer_required
@require_http_methods(['POST'])
def job_delete_view(request, job_id):
    """
    Soft delete a job post.
    """
    company = request.user.company
    job = get_object_or_404(JobPost, id=job_id, company=company, is_deleted=False)

    job.soft_delete()
    messages.success(request, 'ລົບໂພສວຽກສຳເລັດ')

    return redirect('employer:my_jobs')


@employer_required
@require_http_methods(['POST'])
def job_duplicate_view(request, job_id):
    """
    Duplicate a job post.
    """
    company = request.user.company
    original = get_object_or_404(JobPost, id=job_id, company=company, is_deleted=False)

    # Create copy
    job = JobPost.objects.create(
        company=company,
        category=original.category,
        province=original.province,
        title=f'{original.title} (ສຳເນົາ)',
        description=original.description,
        requirements=original.requirements,
        benefits=original.benefits,
        salary_min=original.salary_min,
        salary_max=original.salary_max,
        salary_negotiable=original.salary_negotiable,
        job_type=original.job_type,
        positions_count=original.positions_count,
        contact_email=original.contact_email,
        contact_phone=original.contact_phone,
        contact_whatsapp=original.contact_whatsapp,
        contact_messenger=original.contact_messenger,
        status='draft',
    )

    messages.success(request, 'ສຳເນົາໂພສວຽກສຳເລັດ')
    return redirect('employer:job_edit', job_id=job.id)


@employer_required
def settings_view(request):
    """
    Account settings view.
    """
    return render(request, 'employer/settings.html', {
        'user': request.user,
        'company': request.user.company,
    })
