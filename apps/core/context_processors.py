"""
Context processors for Lao Jobs project.
"""
from django.conf import settings


def site_settings(request):
    """
    Add site settings to template context.
    """
    lao_jobs_settings = getattr(settings, 'LAO_JOBS', {})

    return {
        'SITE_NAME': lao_jobs_settings.get('SITE_NAME', 'ຫາວຽກລາວ'),
        'SITE_URL': lao_jobs_settings.get('SITE_URL', ''),
        'DEBUG': settings.DEBUG,
    }
