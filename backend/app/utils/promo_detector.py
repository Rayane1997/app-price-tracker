"""
Promo Detection Utility Functions

This module provides utility functions for working with promotional pricing data,
including price drop calculations, promo status checks, and promo history retrieval.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from ..models.price_history import PriceHistory
from ..models.product import Product


def calculate_price_drop_percentage(old_price: Optional[float], new_price: Optional[float]) -> Optional[float]:
    """
    Calculate the percentage price drop between two prices.

    Args:
        old_price: The original/previous price
        new_price: The new/current price

    Returns:
        The percentage drop as a positive number (e.g., 15.5 for 15.5% drop),
        or None if calculation is not possible

    Examples:
        >>> calculate_price_drop_percentage(100.0, 85.0)
        15.0
        >>> calculate_price_drop_percentage(50.0, 60.0)
        -20.0
        >>> calculate_price_drop_percentage(None, 50.0)
        None
    """
    if old_price is None or new_price is None:
        return None

    if old_price == 0:
        return None

    drop_percentage = ((old_price - new_price) / old_price) * 100
    return round(drop_percentage, 2)


def is_significant_drop(
    old_price: Optional[float],
    new_price: Optional[float],
    threshold: float = 10.0
) -> bool:
    """
    Determine if the price drop between two prices is significant.

    Args:
        old_price: The original/previous price
        new_price: The new/current price
        threshold: Minimum percentage drop to be considered significant (default: 10%)

    Returns:
        True if the drop is >= threshold percentage, False otherwise

    Examples:
        >>> is_significant_drop(100.0, 85.0, 10.0)
        True
        >>> is_significant_drop(100.0, 95.0, 10.0)
        False
    """
    drop_percentage = calculate_price_drop_percentage(old_price, new_price)

    if drop_percentage is None:
        return False

    return drop_percentage >= threshold


def get_current_promo_status(db: Session, product_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the current promotional status for a product.

    Args:
        db: Database session
        product_id: The product ID to check

    Returns:
        Dictionary with promo status information:
        {
            'is_promo': bool,
            'promo_percentage': Optional[float],
            'current_price': Optional[float],
            'currency': str,
            'last_checked': Optional[datetime]
        }
        Returns None if no price history exists for the product.
    """
    # Get the product to verify it exists and get currency
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    # Get the most recent price history entry
    latest_price = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(desc(PriceHistory.recorded_at))
        .first()
    )

    if not latest_price:
        return None

    return {
        'is_promo': latest_price.is_promo,
        'promo_percentage': latest_price.promo_percentage,
        'current_price': latest_price.price,
        'currency': product.currency,
        'last_checked': latest_price.recorded_at
    }


def get_promo_history(
    db: Session,
    product_id: int,
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Get promotional periods for a product within a specified timeframe.

    This function identifies and groups consecutive promotional price entries
    into distinct promotional periods.

    Args:
        db: Database session
        product_id: The product ID to check
        days: Number of days to look back (default: 30)

    Returns:
        List of promotional periods, each containing:
        {
            'start_date': datetime,
            'end_date': Optional[datetime],  # None if still ongoing
            'promo_percentage': Optional[float],
            'average_price': float,
            'min_price': float,
            'max_price': float,
            'duration_days': int
        }
        Returns empty list if no promos found or no price history exists.
    """
    # Calculate the cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Get all price history entries in the timeframe, ordered chronologically
    price_entries = (
        db.query(PriceHistory)
        .filter(
            PriceHistory.product_id == product_id,
            PriceHistory.recorded_at >= cutoff_date
        )
        .order_by(PriceHistory.recorded_at)
        .all()
    )

    if not price_entries:
        return []

    # Group consecutive promo entries into periods
    promo_periods = []
    current_period = None

    for entry in price_entries:
        if entry.is_promo and entry.price is not None:
            if current_period is None:
                # Start a new promo period
                current_period = {
                    'start_date': entry.recorded_at,
                    'end_date': None,
                    'promo_percentage': entry.promo_percentage,
                    'prices': [entry.price],
                    'recorded_dates': [entry.recorded_at]
                }
            else:
                # Continue current promo period
                current_period['end_date'] = entry.recorded_at
                current_period['prices'].append(entry.price)
                current_period['recorded_dates'].append(entry.recorded_at)
                # Update promo_percentage to the latest value
                if entry.promo_percentage is not None:
                    current_period['promo_percentage'] = entry.promo_percentage
        else:
            # Non-promo entry - close current period if exists
            if current_period is not None:
                # Finalize the period
                prices = current_period['prices']
                start_date = current_period['start_date']
                end_date = current_period['end_date'] or current_period['start_date']

                duration = (end_date - start_date).days
                if duration == 0:
                    duration = 1  # Minimum 1 day for same-day promos

                promo_periods.append({
                    'start_date': start_date,
                    'end_date': end_date,
                    'promo_percentage': current_period['promo_percentage'],
                    'average_price': round(sum(prices) / len(prices), 2),
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'duration_days': duration
                })
                current_period = None

    # Handle case where the last entry was a promo (period still ongoing)
    if current_period is not None:
        prices = current_period['prices']
        start_date = current_period['start_date']
        end_date = current_period['end_date']

        # If end_date is None, the promo is still ongoing (single entry)
        if end_date is None:
            duration = 1
        else:
            duration = (end_date - start_date).days
            if duration == 0:
                duration = 1

        promo_periods.append({
            'start_date': start_date,
            'end_date': end_date,  # None if still ongoing
            'promo_percentage': current_period['promo_percentage'],
            'average_price': round(sum(prices) / len(prices), 2),
            'min_price': min(prices),
            'max_price': max(prices),
            'duration_days': duration
        })

    return promo_periods
