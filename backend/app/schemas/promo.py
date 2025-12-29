"""
Promo Detection Schemas

Pydantic schemas for promotional pricing data responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PromoStatusResponse(BaseModel):
    """Response schema for current promotional status of a product"""
    is_promo: bool = Field(..., description="Whether the product is currently on promotion")
    promo_percentage: Optional[float] = Field(None, description="Percentage discount (e.g., 15.5 for 15.5% off)")
    current_price: Optional[float] = Field(None, description="Current price of the product")
    currency: str = Field(..., description="Currency code (e.g., EUR, USD)")
    last_checked: Optional[datetime] = Field(None, description="Timestamp of last price check")


class PromoPeriod(BaseModel):
    """Response schema for a single promotional period"""
    start_date: datetime = Field(..., description="Start date of the promotional period")
    end_date: Optional[datetime] = Field(None, description="End date (None if still ongoing)")
    promo_percentage: Optional[float] = Field(None, description="Promotional discount percentage")
    average_price: float = Field(..., description="Average price during the promotional period")
    min_price: float = Field(..., description="Minimum price during the promotional period")
    max_price: float = Field(..., description="Maximum price during the promotional period")
    duration_days: int = Field(..., description="Duration of the promotional period in days")


class PromoHistoryResponse(BaseModel):
    """Response schema for promotional history of a product"""
    periods: List[PromoPeriod] = Field(default_factory=list, description="List of promotional periods")
    total_promo_days: int = Field(..., description="Total number of days with promotions")
    days_requested: int = Field(..., description="Number of days requested in the query")
