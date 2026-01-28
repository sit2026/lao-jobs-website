"""
URL configuration for Lao Jobs project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Main pages
    path('', include('apps.jobs.urls.public', namespace='jobs')),

    # Authentication
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),

    # Employer portal
    path('employer/', include('apps.companies.urls', namespace='employer')),

    # Billing
    path('billing/', include('apps.billing.urls', namespace='billing')),

    # Reports
    path('reports/', include('apps.reports.urls', namespace='reports')),

    # API
    path('api/v1/', include('apps.core.api_urls', namespace='api')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'
