from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, Literal
from datetime import datetime, timedelta
from ..core.database import get_db
from ..models.price_history import PriceHistory
from ..models.product import Product
from ..schemas.price_history import (
    PriceHistoryResponse,
    PriceStatisticsResponse,
    PriceChartDataResponse,
)

router = APIRouter(prefix="/products", tags=["price-history"])


def get_time_filter(period: str) -> Optional[datetime]:
    """
    Calculate the datetime threshold for filtering based on period.

    Args:
        period: One of "7d", "30d", "90d", "all"

    Returns:
        datetime threshold or None for "all"
    """
    if period == "all":
        return None

    period_map = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
    }

    days = period_map.get(period)
    if days is None:
        return None

    return datetime.utcnow() - timedelta(days=days)


@router.get("/{product_id}/price-history", response_model=list[PriceHistoryResponse])
def get_price_history(
    product_id: int,
    period: Literal["7d", "30d", "90d", "all"] = Query("all", description="Time period filter"),
    db: Session = Depends(get_db),
):
    """
    Get price history for a product with optional time period filtering.

    Args:
        product_id: Product ID
        period: Time period - "7d" (last 7 days), "30d" (last 30 days),
                "90d" (last 90 days), or "all" (no filter)

    Returns:
        List of price history entries ordered by most recent first

    Raises:
        404: Product not found
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Build query
    query = db.query(PriceHistory).filter(PriceHistory.product_id == product_id)

    # Apply time filter
    time_threshold = get_time_filter(period)
    if time_threshold:
        query = query.filter(PriceHistory.recorded_at >= time_threshold)

    # Order by most recent first
    price_history = query.order_by(desc(PriceHistory.recorded_at)).all()

    return price_history


@router.get("/{product_id}/price-history/stats", response_model=PriceStatisticsResponse)
def get_price_statistics(
    product_id: int,
    db: Session = Depends(get_db),
):
    """
    Get comprehensive price statistics for a product.

    Statistics include:
    - Current price (most recent)
    - Lowest price (all time)
    - Highest price (all time)
    - Average price (all time)
    - Price change percentage (from first to current)
    - Last update timestamp
    - Total number of price checks

    Args:
        product_id: Product ID

    Returns:
        Price statistics object

    Raises:
        404: Product not found
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get aggregated statistics using SQL
    stats = db.query(
        func.min(PriceHistory.price).label("lowest_price"),
        func.max(PriceHistory.price).label("highest_price"),
        func.avg(PriceHistory.price).label("average_price"),
        func.count(PriceHistory.id).label("total_checks"),
        func.max(PriceHistory.recorded_at).label("last_updated"),
    ).filter(
        PriceHistory.product_id == product_id,
        PriceHistory.price.isnot(None)  # Only count successful price checks
    ).first()

    # Get current price (most recent entry)
    current_entry = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id,
        PriceHistory.price.isnot(None)
    ).order_by(desc(PriceHistory.recorded_at)).first()

    current_price = current_entry.price if current_entry else None

    # Get first price for percentage calculation
    first_entry = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id,
        PriceHistory.price.isnot(None)
    ).order_by(PriceHistory.recorded_at.asc()).first()

    # Calculate price change percentage
    price_change_percentage = None
    if first_entry and current_price and first_entry.price:
        price_change_percentage = ((current_price - first_entry.price) / first_entry.price) * 100

    return PriceStatisticsResponse(
        current_price=current_price,
        lowest_price=stats.lowest_price if stats else None,
        highest_price=stats.highest_price if stats else None,
        average_price=float(stats.average_price) if stats and stats.average_price else None,
        price_change_percentage=price_change_percentage,
        last_updated=stats.last_updated if stats else None,
        total_checks=stats.total_checks if stats else 0,
    )


@router.get("/{product_id}/price-history/chart", response_model=PriceChartDataResponse)
def get_price_chart_data(
    product_id: int,
    period: Literal["7d", "30d", "90d", "all"] = Query("all", description="Time period filter"),
    db: Session = Depends(get_db),
):
    """
    Get Chart.js-ready price history data for visualization.

    Returns data in format optimized for Chart.js:
    - labels: ISO timestamp strings for x-axis
    - prices: Price values for y-axis (null for failed checks)
    - promos: Boolean flags to highlight promotional periods

    Args:
        product_id: Product ID
        period: Time period - "7d", "30d", "90d", or "all"

    Returns:
        Chart data object with synchronized arrays

    Raises:
        404: Product not found
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Build query
    query = db.query(PriceHistory).filter(PriceHistory.product_id == product_id)

    # Apply time filter
    time_threshold = get_time_filter(period)
    if time_threshold:
        query = query.filter(PriceHistory.recorded_at >= time_threshold)

    # Order by timestamp ascending for chart
    price_history = query.order_by(PriceHistory.recorded_at.asc()).all()

    # Build chart data arrays
    labels = []
    prices = []
    promos = []

    for entry in price_history:
        labels.append(entry.recorded_at.isoformat())
        prices.append(entry.price)  # Can be None for failed checks
        promos.append(entry.is_promo)

    return PriceChartDataResponse(
        labels=labels,
        prices=prices,
        promos=promos,
    )
