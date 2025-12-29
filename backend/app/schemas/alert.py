"""
Pydantic schemas for Alert API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AlertType(str, Enum):
    """Alert type enumeration"""
    PRICE_DROP = "price_drop"
    TARGET_REACHED = "target_reached"
    PROMO_DETECTED = "promo_detected"


class AlertStatus(str, Enum):
    """Alert status enumeration"""
    UNREAD = "unread"
    READ = "read"
    DISMISSED = "dismissed"


class ProductSummary(BaseModel):
    """Minimal product information for alert responses"""
    id: int
    name: str
    url: str
    domain: str
    image_url: Optional[str] = None
    currency: str

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    """Alert response schema with product information"""
    id: int
    product_id: int
    type: AlertType
    status: AlertStatus
    old_price: Optional[float] = Field(None, description="Previous price before change")
    new_price: float = Field(..., description="Current/new price")
    price_drop_percentage: Optional[float] = Field(None, description="Percentage drop (for PRICE_DROP alerts)")
    message: str = Field(..., description="Human-readable alert message")
    created_at: datetime
    read_at: Optional[datetime] = None

    # Include product details
    product: ProductSummary

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Paginated list of alerts"""
    alerts: list[AlertResponse]
    total: int = Field(..., description="Total number of alerts matching the filter")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
