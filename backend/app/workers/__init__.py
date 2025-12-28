# Celery tasks for price scraping
from .celery_app import celery_app
from .tasks import track_product_price, schedule_all_products_tracking

__all__ = ['celery_app', 'track_product_price', 'schedule_all_products_tracking']
