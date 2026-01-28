"""
API URL configuration for Lao Jobs project.
"""
from django.urls import path, include

app_name = 'api'

urlpatterns = [
    # Jobs API
    path('jobs/', include('apps.jobs.urls.api')),

    # Companies API
    path('companies/', include('apps.companies.api_urls')),

    # Billing API
    path('billing/', include('apps.billing.api_urls')),
]
