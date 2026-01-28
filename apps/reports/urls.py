"""
Reports URL configuration.
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('job/<uuid:job_id>/', views.report_job_view, name='report_job'),
    path('reasons/', views.report_reasons_view, name='reasons'),
]
