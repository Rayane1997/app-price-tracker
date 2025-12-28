from celery.schedules import crontab

# Celery Beat schedule configuration
beat_schedule = {
    # Track all active products every hour
    'schedule-all-products-tracking': {
        'task': 'app.workers.tasks.schedule_all_products_tracking',
        'schedule': crontab(minute=0),  # Every hour at minute 0
        'options': {
            'expires': 3600,  # Expire after 1 hour
        }
    },
}
