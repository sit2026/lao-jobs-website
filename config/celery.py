"""
Celery configuration for Lao Jobs project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('lao_jobs')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    # Expire job posts every hour
    'expire-job-posts': {
        'task': 'apps.jobs.tasks.expire_job_posts',
        'schedule': crontab(minute=0),  # Every hour at :00
    },

    # Expire subscriptions every hour
    'expire-subscriptions': {
        'task': 'apps.billing.tasks.expire_subscriptions',
        'schedule': crontab(minute=30),  # Every hour at :30
    },

    # Purge soft-deleted posts (daily at 3:00 AM)
    'purge-deleted-posts': {
        'task': 'apps.jobs.tasks.purge_deleted_posts',
        'schedule': crontab(hour=3, minute=0),
    },

    # Purge expired invoices (daily at 3:30 AM)
    'purge-expired-invoices': {
        'task': 'apps.billing.tasks.purge_expired_invoices',
        'schedule': crontab(hour=3, minute=30),
    },

    # Send subscription expiry reminders (daily at 9:00 AM)
    'send-expiry-reminders': {
        'task': 'apps.billing.tasks.send_expiry_reminders',
        'schedule': crontab(hour=9, minute=0),
    },

    # Cleanup expired OTP records (daily at 4:00 AM)
    'cleanup-otp-records': {
        'task': 'apps.accounts.tasks.cleanup_expired_otp',
        'schedule': crontab(hour=4, minute=0),
    },

    # Generate sitemap (daily at 5:00 AM)
    'generate-sitemap': {
        'task': 'apps.core.tasks.generate_sitemap',
        'schedule': crontab(hour=5, minute=0),
    },
}

app.conf.timezone = 'Asia/Vientiane'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
