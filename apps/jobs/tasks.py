"""
Jobs Celery tasks.
"""
from celery import shared_task
from django.utils import timezone
from django.db import transaction


@shared_task
def expire_job_posts():
    """
    Expire job posts that have passed their expiry date.
    """
    from .models import JobPost

    now = timezone.now()

    with transaction.atomic():
        posts_to_expire = JobPost.objects.filter(
            status='published',
            expires_at__lt=now,
            is_deleted=False
        ).select_for_update()

        expired_count = 0
        for post in posts_to_expire:
            post.status = 'expired'
            post.save(update_fields=['status', 'updated_at'])
            expired_count += 1

            # Create audit log
            from apps.audit.models import AuditLog
            AuditLog.objects.create(
                actor_type='system',
                action='expire',
                target_type='JobPost',
                target_id=str(post.id),
                details={'reason': 'auto_expire'}
            )

    return {'expired': expired_count}


@shared_task
def purge_deleted_posts():
    """
    Permanently delete soft-deleted posts older than 60 days.
    """
    from datetime import timedelta
    from .models import JobPost

    cutoff = timezone.now() - timedelta(days=60)

    deleted, _ = JobPost.all_objects.filter(
        is_deleted=True,
        deleted_at__lt=cutoff
    ).delete()

    return {'purged': deleted}


@shared_task
def process_job_alerts(job_id):
    """
    Process job alerts for a newly published job.
    """
    from .models import JobPost, JobAlert
    from django.db.models import Q

    try:
        job = JobPost.objects.get(id=job_id, status='published')
    except JobPost.DoesNotExist:
        return {'error': 'Job not found'}

    # Find matching alerts
    alerts = JobAlert.objects.filter(
        is_active=True,
        is_verified=True
    )

    # Filter by criteria
    if job.category:
        alerts = alerts.filter(
            Q(category__isnull=True) | Q(category=job.category)
        )

    if job.province:
        alerts = alerts.filter(
            Q(province__isnull=True) | Q(province=job.province)
        )

    # Filter by keywords
    alerts_to_notify = []
    for alert in alerts:
        if alert.keywords:
            keywords = [k.strip().lower() for k in alert.keywords.split(',')]
            job_text = f'{job.title} {job.description}'.lower()
            if any(kw in job_text for kw in keywords):
                alerts_to_notify.append(alert)
        else:
            alerts_to_notify.append(alert)

    # Send notifications (implement based on channel)
    sent_count = 0
    for alert in alerts_to_notify:
        # TODO: Implement actual notification sending
        # send_job_alert_notification.delay(alert.id, job.id)
        alert.last_sent_at = timezone.now()
        alert.save(update_fields=['last_sent_at'])
        sent_count += 1

    return {'alerts_sent': sent_count}


@shared_task
def update_job_view_counts():
    """
    Batch update view counts from cache (if using Redis for real-time counts).
    """
    # This is a placeholder for implementing cached view counts
    # In production, you might store view counts in Redis and batch update to DB
    return {'status': 'completed'}
