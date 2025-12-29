import asyncio
from datetime import datetime
from typing import Optional
import logging
from celery import Task
from sqlalchemy.orm import Session
from .celery_app import celery_app
from ..core.database import SessionLocal
from ..models.product import Product, ProductStatus
from ..models.price_history import PriceHistory
from ..parsers.engine import parser_engine
from ..parsers.base import ParserError
from ..utils.alert_generator import check_and_create_alerts
import time

logger = logging.getLogger(__name__)

# Rate limiting: track last scrape time per domain
_domain_last_scrape = {}


class DatabaseTask(Task):
    """Base task with database session management"""
    _db: Optional[Session] = None

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3,
)
def track_product_price(self, product_id: int):
    """
    Track price for a single product

    Args:
        product_id: ID of the product to track

    Returns:
        dict with status and price information
    """
    db = self.db
    start_time = time.time()

    logger.info(f"Starting price tracking for product {product_id}")

    # Get product from database
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.error(f"Product {product_id} not found")
        return {"status": "error", "message": "Product not found"}

    # Skip if product is not trackable
    if product.status in [ProductStatus.ERROR, ProductStatus.NOT_TRACKABLE, ProductStatus.PAUSED]:
        logger.info(f"Skipping product {product_id} with status {product.status}")
        return {"status": "skipped", "reason": f"Product status is {product.status}"}

    # Rate limiting: wait if needed for this domain
    domain = product.domain
    if domain in _domain_last_scrape:
        time_since_last = time.time() - _domain_last_scrape[domain]
        if time_since_last < 5:
            wait_time = 5 - time_since_last
            logger.info(f"Rate limiting: waiting {wait_time:.2f}s for domain {domain}")
            time.sleep(wait_time)

    try:
        # Parse the product page
        logger.info(f"Parsing URL: {product.url}")
        product_data = asyncio.run(parser_engine.parse(product.url))

        # Update domain last scrape time
        _domain_last_scrape[domain] = time.time()

        # Calculate scrape duration
        scrape_duration_ms = int((time.time() - start_time) * 1000)

        # Create price history entry
        price_history = PriceHistory(
            product_id=product.id,
            price=product_data.price,
            currency=product_data.currency or "EUR",
            is_promo=product_data.is_promo or False,
            promo_percentage=product_data.promo_percentage,
            source="scraper",
            scrape_duration_ms=scrape_duration_ms,
            recorded_at=datetime.utcnow(),
        )
        db.add(price_history)

        # Update product information
        product.current_price = product_data.price
        product.currency = product_data.currency or "EUR"
        product.last_checked_at = datetime.utcnow()
        product.last_success_at = datetime.utcnow()
        product.consecutive_errors = 0
        product.last_error_message = None

        # Update product name and image if they were extracted and different
        if product_data.name and product_data.name != product.name:
            logger.info(f"Updating product name from '{product.name}' to '{product_data.name}'")
            product.name = product_data.name

        if product_data.image_url and product_data.image_url != product.image_url:
            logger.info(f"Updating product image URL")
            product.image_url = product_data.image_url

        # Ensure status is ACTIVE on success
        if product.status != ProductStatus.ACTIVE:
            product.status = ProductStatus.ACTIVE

        db.commit()

        # Generate alerts based on price changes (after commit to ensure data is saved)
        alerts_created = []
        try:
            alerts_created = check_and_create_alerts(
                db=db,
                product=product,
                new_price=product_data.price,
                is_promo=product_data.is_promo or False
            )
            if alerts_created:
                logger.info(
                    f"Created {len(alerts_created)} alert(s) for product {product_id}: "
                    f"{[alert.type.value for alert in alerts_created]}"
                )
        except Exception as alert_error:
            # Don't fail the task if alert creation fails
            logger.error(
                f"Failed to create alerts for product {product_id}: {alert_error}",
                exc_info=True
            )

        logger.info(
            f"Successfully tracked product {product_id}: "
            f"price={product_data.price} {product_data.currency}, "
            f"duration={scrape_duration_ms}ms, "
            f"alerts_created={len(alerts_created)}"
        )

        return {
            "status": "success",
            "product_id": product_id,
            "price": product_data.price,
            "currency": product_data.currency,
            "duration_ms": scrape_duration_ms,
            "alerts_created": len(alerts_created),
        }

    except ParserError as e:
        # Parser-specific error
        db.rollback()  # Rollback any uncommitted changes before error handling
        logger.error(f"Parser error for product {product_id}: {e}")
        return _handle_tracking_error(db, product, str(e))

    except Exception as e:
        # General error
        db.rollback()  # Rollback any uncommitted changes before error handling
        logger.error(f"Unexpected error tracking product {product_id}: {e}", exc_info=True)
        return _handle_tracking_error(db, product, str(e))


def _handle_tracking_error(db: Session, product: Product, error_message: str) -> dict:
    """
    Handle tracking error and update product status

    Args:
        db: Database session
        product: Product that failed
        error_message: Error message

    Returns:
        dict with error information
    """
    product.last_checked_at = datetime.utcnow()
    product.last_error_message = error_message
    product.consecutive_errors += 1

    # Mark as ERROR if too many consecutive errors
    if product.consecutive_errors >= 5:
        logger.warning(
            f"Product {product.id} marked as ERROR after {product.consecutive_errors} consecutive errors"
        )
        product.status = ProductStatus.ERROR

    db.commit()

    return {
        "status": "error",
        "product_id": product.id,
        "message": error_message,
        "consecutive_errors": product.consecutive_errors,
    }


@celery_app.task(bind=True, base=DatabaseTask)
def schedule_all_products_tracking(self):
    """
    Schedule tracking for all active products

    This task is called periodically by Celery Beat
    """
    db = self.db

    logger.info("Scheduling price tracking for all active products")

    # Get all active products
    products = db.query(Product).filter(Product.status == ProductStatus.ACTIVE).all()

    logger.info(f"Found {len(products)} active products to track")

    scheduled_count = 0
    for product in products:
        # Check if product is due for tracking based on check_frequency_hours
        if product.last_checked_at:
            hours_since_check = (datetime.utcnow() - product.last_checked_at).total_seconds() / 3600
            if hours_since_check < product.check_frequency_hours:
                logger.debug(
                    f"Skipping product {product.id}: checked {hours_since_check:.1f}h ago, "
                    f"frequency is {product.check_frequency_hours}h"
                )
                continue

        # Schedule the tracking task
        track_product_price.delay(product.id)
        scheduled_count += 1
        logger.debug(f"Scheduled tracking for product {product.id}")

    logger.info(f"Scheduled tracking for {scheduled_count} products")

    return {
        "status": "success",
        "total_products": len(products),
        "scheduled": scheduled_count,
    }
