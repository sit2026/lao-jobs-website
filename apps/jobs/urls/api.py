"""
Jobs API URL configuration.
"""
from django.urls import path
from apps.jobs import api_views

urlpatterns = [
    # Job listing API
    path('', api_views.job_list_api, name='job_list'),
    path('<uuid:job_id>/', api_views.job_detail_api, name='job_detail'),

    # Quick apply
    path('<uuid:job_id>/apply/', api_views.job_apply_api, name='job_apply'),

    # Save job
    path('<uuid:job_id>/save/', api_views.save_job_api, name='save_job'),

    # Job alerts
    path('alerts/', api_views.create_job_alert_api, name='create_alert'),
]
