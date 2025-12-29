"""
Alert API endpoints for managing price alerts.

Provides endpoints to:
- List alerts with filtering and pagination
- Get single alert details
- Mark alerts as read
- Dismiss alerts
- Delete alerts
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import Optional
import math

from ..core.database import get_db
from ..models.alert import Alert, AlertType, AlertStatus
from ..models.product import Product
from ..schemas.alert import (
    AlertResponse,
    AlertListResponse,
    AlertType as AlertTypeSchema,
    AlertStatus as AlertStatusSchema,
)

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=AlertListResponse)
def list_alerts(
    status: Optional[AlertStatusSchema] = Query(None, description="Filter by alert status"),
    type: Optional[AlertTypeSchema] = Query(None, description="Filter by alert type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    List alerts with pagination and optional filtering.

    Supports filtering by:
    - status: Filter by alert status (unread, read, dismissed)
    - type: Filter by alert type (price_drop, target_reached, promo_detected)

    Results are ordered by creation date (newest first).

    Args:
        status: Optional alert status filter
        type: Optional alert type filter
        page: Page number (1-indexed)
        page_size: Number of items per page (1-100)
        db: Database session

    Returns:
        Paginated list of alerts with total count
    """
    # Build base query with product join for response
    query = db.query(Alert).join(Product)

    # Apply filters
    filters = []
    if status is not None:
        filters.append(Alert.status == AlertStatus(status.value))
    if type is not None:
        filters.append(Alert.type == AlertType(type.value))

    if filters:
        query = query.filter(and_(*filters))

    # Get total count before pagination
    total = query.count()

    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # Apply ordering and pagination
    alerts = (
        query
        .order_by(desc(Alert.created_at))
        .offset(skip)
        .limit(page_size)
        .all()
    )

    return AlertListResponse(
        alerts=alerts,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single alert by ID.

    Args:
        alert_id: Alert ID
        db: Database session

    Returns:
        Alert details with product information

    Raises:
        404: Alert not found
    """
    alert = (
        db.query(Alert)
        .join(Product)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.put("/{alert_id}/mark-read", response_model=AlertResponse)
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
):
    """
    Mark an alert as read.

    Changes the alert status from UNREAD to READ and records the timestamp.

    Args:
        alert_id: Alert ID
        db: Database session

    Returns:
        Updated alert

    Raises:
        404: Alert not found
    """
    alert = (
        db.query(Alert)
        .join(Product)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Update status to READ
    alert.status = AlertStatus.READ

    # Record when it was read (if not already set)
    if alert.read_at is None:
        from datetime import datetime
        alert.read_at = datetime.utcnow()

    db.commit()
    db.refresh(alert)

    return alert


@router.put("/{alert_id}/dismiss", response_model=AlertResponse)
def dismiss_alert(
    alert_id: int,
    db: Session = Depends(get_db),
):
    """
    Dismiss an alert.

    Changes the alert status to DISMISSED. Dismissed alerts are typically
    hidden from the main alert list.

    Args:
        alert_id: Alert ID
        db: Database session

    Returns:
        Updated alert

    Raises:
        404: Alert not found
    """
    alert = (
        db.query(Alert)
        .join(Product)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Update status to DISMISSED
    alert.status = AlertStatus.DISMISSED

    db.commit()
    db.refresh(alert)

    return alert


@router.delete("/{alert_id}", status_code=204)
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
):
    """
    Permanently delete an alert.

    This operation cannot be undone.

    Args:
        alert_id: Alert ID
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        404: Alert not found
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alert)
    db.commit()

    return None
