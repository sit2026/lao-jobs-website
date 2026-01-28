"""
Public job URL configuration.
"""
from django.urls import path
from apps.jobs import views

app_name = 'jobs'

urlpatterns = [
    # Homepage
    path('', views.home_view, name='home'),

    # Job listing and search
    path('jobs/', views.job_list_view, name='list'),

    # Job detail
    path('jobs/<uuid:job_id>/', views.job_detail_view, name='detail'),

    # Category pages
    path('jobs/category/<slug:slug>/', views.category_jobs_view, name='category'),
    path('categories/', views.all_categories_view, name='all_categories'),

    # Province pages
    path('jobs/province/<slug:slug>/', views.province_jobs_view, name='province'),
    path('provinces/', views.all_provinces_view, name='all_provinces'),

    # Company jobs
    path('company/<uuid:company_id>/jobs/', views.company_jobs_view, name='company_jobs'),
]
