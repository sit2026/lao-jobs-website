"""
Core Celery tasks.
"""
from celery import shared_task
from django.conf import settings


@shared_task
def generate_sitemap():
    """
    Generate sitemap.xml for SEO.
    """
    from apps.jobs.models import JobPost, Category, Province

    # Get all published jobs
    jobs = JobPost.objects.filter(status='published').order_by('-published_at')[:1000]
    categories = Category.active_objects.all()
    provinces = Province.active_objects.all()

    site_url = settings.LAO_JOBS.get('SITE_URL', 'https://laojobs.la')

    # Build sitemap XML
    urls = []

    # Static pages
    urls.append({'loc': f'{site_url}/', 'priority': '1.0', 'changefreq': 'daily'})
    urls.append({'loc': f'{site_url}/jobs/', 'priority': '0.9', 'changefreq': 'hourly'})

    # Categories
    for category in categories:
        urls.append({
            'loc': f'{site_url}/jobs/category/{category.slug}/',
            'priority': '0.8',
            'changefreq': 'daily'
        })

    # Provinces
    for province in provinces:
        urls.append({
            'loc': f'{site_url}/jobs/province/{province.slug}/',
            'priority': '0.8',
            'changefreq': 'daily'
        })

    # Jobs
    for job in jobs:
        urls.append({
            'loc': f'{site_url}/jobs/{job.id}/',
            'priority': '0.7',
            'changefreq': 'weekly',
            'lastmod': job.updated_at.strftime('%Y-%m-%d')
        })

    # Generate XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in urls:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url["loc"]}</loc>\n'
        xml_content += f'    <priority>{url["priority"]}</priority>\n'
        xml_content += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        if 'lastmod' in url:
            xml_content += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
        xml_content += '  </url>\n'

    xml_content += '</urlset>'

    # Save sitemap
    import os
    sitemap_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR / 'static', 'sitemap.xml')
    os.makedirs(os.path.dirname(sitemap_path), exist_ok=True)

    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    return {'status': 'success', 'urls_count': len(urls)}
