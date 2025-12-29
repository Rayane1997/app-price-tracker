"""
Alert generation logic for price tracking.

This module handles the creation of alerts based on price changes,
target price achievements, and promotional detections.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..models.alert import Alert, AlertType, AlertStatus
from ..models.price_history import PriceHistory
from ..models.product import Product

import logging

logger = logging.getLogger(__name__)


def get_previous_price(db: Session, product_id: int) -> Optional[float]:
    """
    Get the most recent successful price before the current check.

    Args:
        db: Database session
        product_id: Product ID

    Returns:
        Previous price or None if no previous price exists
    """
    # Get the last 2 price history entries (most recent and second-most recent)
    price_entries = (
        db.query(PriceHistory)
        .filter(
            and_(
                PriceHistory.product_id == product_id,
                PriceHistory.price.isnot(None)
            )
        )
        .order_by(desc(PriceHistory.recorded_at))
        .limit(2)
        .all()
    )

    # If we have at least 2 entries, return the second one
    if len(price_entries) >= 2:
        return price_entries[1].price

    return None


def has_recent_alert(
    db: Session,
    product_id: int,
    alert_type: AlertType,
    hours: int = 24
) -> bool:
    """
    Check if a similar alert was created recently (anti-spam).

    Args:
        db: Database session
        product_id: Product ID
        alert_type: Type of alert to check for
        hours: Number of hours to look back (default: 24)

    Returns:
        True if a recent alert exists, False otherwise
    """
    time_threshold = datetime.utcnow() - timedelta(hours=hours)

    existing_alert = (
        db.query(Alert)
        .filter(
            and_(
                Alert.product_id == product_id,
                Alert.type == alert_type,
                Alert.created_at >= time_threshold
            )
        )
        .first()
    )

    return existing_alert is not None


def create_alert(
    db: Session,
    product_id: int,
    alert_type: AlertType,
    message: str,
    old_price: Optional[float],
    new_price: float,
    price_drop_percentage: Optional[float] = None
) -> Alert:
    """
    Create and commit a new alert to the database.

    Args:
        db: Database session
        product_id: Product ID
        alert_type: Type of alert
        message: Alert message
        old_price: Previous price (can be None)
        new_price: Current price
        price_drop_percentage: Percentage drop (optional)

    Returns:
        Created Alert object
    """
    alert = Alert(
        product_id=product_id,
        type=alert_type,
        status=AlertStatus.UNREAD,
        old_price=old_price,
        new_price=new_price,
        price_drop_percentage=price_drop_percentage,
        message=message,
        created_at=datetime.utcnow()
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    logger.info(f"Created {alert_type.value} alert for product {product_id}")

    return alert


def check_and_create_alerts(
    db: Session,
    product: Product,
    new_price: float,
    is_promo: bool
) -> List[Alert]:
    """
    Check alert rules and create appropriate alerts for a product.

    This function checks three types of alerts:
    1. TARGET_REACHED: Price has dropped to or below the target price
    2. PRICE_DROP: Price has dropped by 10% or more
    3. PROMO_DETECTED: Product is now on promotion

    Anti-spam protection: Alerts of the same type won't be created if one
    already exists for the same product in the last 24 hours.

    Args:
        db: Database session
        product: Product object
        new_price: Current price from the latest check
        is_promo: Whether the product is currently on promotion

    Returns:
        List of created Alert objects
    """
    created_alerts = []

    # Skip alert generation if new_price is None (failed scraping)
    if new_price is None:
        logger.debug(f"Skipping alert generation for product {product.id}: new_price is None")
        return created_alerts

    # Get previous price for comparison
    previous_price = get_previous_price(db, product.id)

    # Rule 1: TARGET_REACHED
    # Check if target price is set and the new price has reached or dropped below it
    if product.target_price is not None and new_price <= product.target_price:
        # Check for duplicate alerts (anti-spam)
        if not has_recent_alert(db, product.id, AlertType.TARGET_REACHED):
            message = (
                f"🎯 Price target reached! "
                f"{product.name} is now {new_price:.2f} {product.currency}, "
                f"at or below your target of {product.target_price:.2f} {product.currency}."
            )

            alert = create_alert(
                db=db,
                product_id=product.id,
                alert_type=AlertType.TARGET_REACHED,
                message=message,
                old_price=previous_price,
                new_price=new_price
            )
            created_alerts.append(alert)
            logger.info(f"TARGET_REACHED alert created for product {product.id}")

    # Rule 2: PRICE_DROP (>= 10%)
    # Check if price has dropped by at least 10% from the previous price
    if previous_price is not None and previous_price > 0:
        price_drop_percentage = ((previous_price - new_price) / previous_price) * 100

        if price_drop_percentage >= 10:
            # Check for duplicate alerts (anti-spam)
            if not has_recent_alert(db, product.id, AlertType.PRICE_DROP):
                message = (
                    f"📉 Price drop detected! "
                    f"{product.name} dropped by {price_drop_percentage:.1f}% "
                    f"from {previous_price:.2f} to {new_price:.2f} {product.currency}."
                )

                alert = create_alert(
                    db=db,
                    product_id=product.id,
                    alert_type=AlertType.PRICE_DROP,
                    message=message,
                    old_price=previous_price,
                    new_price=new_price,
                    price_drop_percentage=price_drop_percentage
                )
                created_alerts.append(alert)
                logger.info(
                    f"PRICE_DROP alert created for product {product.id} "
                    f"(drop: {price_drop_percentage:.1f}%)"
                )

    # Rule 3: PROMO_DETECTED
    # Check if product is now on promotion (and wasn't before)
    if is_promo:
        # Check if the product was on promo in the previous check
        previous_promo = False
        if previous_price is not None:
            # Get the second-most recent price history entry to check promo status
            previous_entry = (
                db.query(PriceHistory)
                .filter(
                    and_(
                        PriceHistory.product_id == product.id,
                        PriceHistory.price.isnot(None)
                    )
                )
                .order_by(desc(PriceHistory.recorded_at))
                .offset(1)
                .first()
            )
            if previous_entry:
                previous_promo = previous_entry.is_promo

        # Only create alert if product wasn't on promo before
        if not previous_promo:
            # Check for duplicate alerts (anti-spam)
            if not has_recent_alert(db, product.id, AlertType.PROMO_DETECTED):
                # Get promo percentage if available
                latest_entry = (
                    db.query(PriceHistory)
                    .filter(PriceHistory.product_id == product.id)
                    .order_by(desc(PriceHistory.recorded_at))
                    .first()
                )

                promo_info = ""
                if latest_entry and latest_entry.promo_percentage:
                    promo_info = f" (save {latest_entry.promo_percentage}%)"

                message = (
                    f"🏷️ Promotion detected! "
                    f"{product.name} is now on sale{promo_info} "
                    f"at {new_price:.2f} {product.currency}."
                )

                alert = create_alert(
                    db=db,
                    product_id=product.id,
                    alert_type=AlertType.PROMO_DETECTED,
                    message=message,
                    old_price=previous_price,
                    new_price=new_price
                )
                created_alerts.append(alert)
                logger.info(f"PROMO_DETECTED alert created for product {product.id}")

    return created_alerts
