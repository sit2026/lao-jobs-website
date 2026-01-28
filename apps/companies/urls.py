"""
Company (Employer Portal) URL configuration.
"""
from django.urls import path
from . import views

app_name = 'employer'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Company Profile
    path('profile/', views.profile_view, name='profile'),

    # Jobs Management
    path('jobs/', views.my_jobs_view, name='my_jobs'),
    path('jobs/create/', views.job_create_view, name='job_create'),
    path('jobs/<uuid:job_id>/edit/', views.job_edit_view, name='job_edit'),
    path('jobs/<uuid:job_id>/publish/', views.job_publish_view, name='job_publish'),
    path('jobs/<uuid:job_id>/close/', views.job_close_view, name='job_close'),
    path('jobs/<uuid:job_id>/delete/', views.job_delete_view, name='job_delete'),
    path('jobs/<uuid:job_id>/duplicate/', views.job_duplicate_view, name='job_duplicate'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]
