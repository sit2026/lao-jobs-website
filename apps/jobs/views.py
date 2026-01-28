"""
Public job views.
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.http import require_http_methods

from .models import JobPost, Category, Province, QuickFilter
from .forms import JobSearchForm


def home_view(request):
    """
    Homepage view.
    """
    # Get recent published jobs
    recent_jobs = JobPost.objects.filter(
        status='published',
        is_deleted=False
    ).select_related('company', 'category', 'province').order_by('-published_at')[:10]

    # Get categories with job counts
    categories = Category.active_objects.annotate(
        job_count=Count('job_posts', filter=Q(job_posts__status='published'))
    ).order_by('sort_order')[:8]

    # Get provinces with job counts
    provinces = Province.active_objects.annotate(
        job_count=Count('job_posts', filter=Q(job_posts__status='published'))
    ).filter(job_count__gt=0).order_by('-job_count')[:8]

    # Get quick filters
    quick_filters = QuickFilter.active_objects.all()[:8]

    # Statistics
    total_jobs = JobPost.objects.filter(status='published', is_deleted=False).count()
    total_companies = JobPost.objects.filter(
        status='published', is_deleted=False
    ).values('company').distinct().count()

    context = {
        'recent_jobs': recent_jobs,
        'categories': categories,
        'provinces': provinces,
        'quick_filters': quick_filters,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
    }

    return render(request, 'jobs/home.html', context)


def job_list_view(request):
    """
    Job listing with search and filters.
    """
    form = JobSearchForm(request.GET)

    jobs = JobPost.objects.filter(
        status='published',
        is_deleted=False
    ).select_related('company', 'category', 'province').order_by('-published_at')

    # Apply filters
    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        province = form.cleaned_data.get('province')
        job_type = form.cleaned_data.get('job_type')
        salary_min = form.cleaned_data.get('salary_min')

        if q:
            jobs = jobs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(company__company_name__icontains=q)
            )

        if category:
            jobs = jobs.filter(category=category)

        if province:
            jobs = jobs.filter(province=province)

        if job_type:
            jobs = jobs.filter(job_type=job_type)

        if salary_min:
            jobs = jobs.filter(
                Q(salary_max__gte=salary_min) |
                Q(salary_min__gte=salary_min)
            )

    # Pagination
    paginator = Paginator(jobs, 20)
    page = request.GET.get('page', 1)
    jobs_page = paginator.get_page(page)

    # Get categories and provinces for filter sidebar
    categories = Category.active_objects.annotate(
        job_count=Count('job_posts', filter=Q(job_posts__status='published'))
    ).order_by('sort_order')

    provinces = Province.active_objects.annotate(
        job_count=Count('job_posts', filter=Q(job_posts__status='published'))
    ).order_by('sort_order')

    context = {
        'jobs': jobs_page,
        'form': form,
        'categories': categories,
        'provinces': provinces,
        'total_results': paginator.count,
    }

    return render(request, 'jobs/job_list.html', context)


def job_detail_view(request, job_id):
    """
    Job detail view.
    """
    job = get_object_or_404(
        JobPost.objects.select_related('company', 'category', 'province'),
        id=job_id,
        status='published',
        is_deleted=False
    )

    # Increment view count
    job.increment_view()

    # Get similar jobs
    similar_jobs = JobPost.objects.filter(
        status='published',
        is_deleted=False,
        category=job.category
    ).exclude(id=job.id).order_by('-published_at')[:4]

    context = {
        'job': job,
        'similar_jobs': similar_jobs,
    }

    return render(request, 'jobs/job_detail.html', context)


def category_jobs_view(request, slug):
    """
    Jobs filtered by category.
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)

    jobs = JobPost.objects.filter(
        status='published',
        is_deleted=False,
        category=category
    ).select_related('company', 'province').order_by('-published_at')

    # Pagination
    paginator = Paginator(jobs, 20)
    page = request.GET.get('page', 1)
    jobs_page = paginator.get_page(page)

    context = {
        'category': category,
        'jobs': jobs_page,
        'total_results': paginator.count,
    }

    return render(request, 'jobs/category_jobs.html', context)


def province_jobs_view(request, slug):
    """
    Jobs filtered by province.
    """
    province = get_object_or_404(Province, slug=slug, is_active=True)

    jobs = JobPost.objects.filter(
        status='published',
        is_deleted=False,
        province=province
    ).select_related('company', 'category').order_by('-published_at')

    # Pagination
    paginator = Paginator(jobs, 20)
    page = request.GET.get('page', 1)
    jobs_page = paginator.get_page(page)

    context = {
        'province': province,
        'jobs': jobs_page,
        'total_results': paginator.count,
    }

    return render(request, 'jobs/province_jobs.html', context)


def company_jobs_view(request, company_id):
    """
    Jobs from a specific company.
    """
    from apps.companies.models import Company

    company = get_object_or_404(Company, id=company_id, status='active')

    jobs = JobPost.objects.filter(
        status='published',
        is_deleted=False,
        company=company
    ).select_related('category', 'province').order_by('-published_at')

    # Pagination
    paginator = Paginator(jobs, 20)
    page = request.GET.get('page', 1)
    jobs_page = paginator.get_page(page)

    context = {
        'company': company,
        'jobs': jobs_page,
        'total_results': paginator.count,
    }

    return render(request, 'jobs/company_jobs.html', context)


def all_categories_view(request):
    """
    All categories page.
    """
    categories = Category.active_objects.annotate(
        job_count=Count('job_posts', filter=Q(job_posts__status='published'))
    ).order_by('sort_order')

    return render(request, 'jobs/all_categories.html', {'categories': categories})


def all_provinces_view(request):
    """
    All provinces page.
    """
    provinces = Province.active_objects.annotate(
        job_count=Count('job_posts', filter=Q(job_posts__status='published'))
    ).order_by('sort_order')

    return render(request, 'jobs/all_provinces.html', {'provinces': provinces})
