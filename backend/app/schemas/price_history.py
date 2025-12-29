from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PriceHistoryResponse(BaseModel):
    """Response schema for individual price history entry"""
    id: int
    product_id: int
    price: Optional[float] = None
    currency: str
    is_promo: bool
    promo_percentage: Optional[float] = None
    recorded_at: datetime
    scrape_duration_ms: Optional[int] = None

    class Config:
        from_attributes = True


class PriceStatisticsResponse(BaseModel):
    """Response schema for price statistics"""
    current_price: Optional[float] = Field(None, description="Most recent price")
    lowest_price: Optional[float] = Field(None, description="Lowest price in period")
    highest_price: Optional[float] = Field(None, description="Highest price in period")
    average_price: Optional[float] = Field(None, description="Average price in period")
    price_change_percentage: Optional[float] = Field(None, description="Price change % from first to current")
    last_updated: Optional[datetime] = Field(None, description="Last price check timestamp")
    total_checks: int = Field(0, description="Total number of price checks")


class PriceChartDataResponse(BaseModel):
    """Response schema for Chart.js-ready price chart data"""
    labels: list[str] = Field(default_factory=list, description="ISO timestamp strings for x-axis")
    prices: list[Optional[float]] = Field(default_factory=list, description="Price values for y-axis")
    promos: list[bool] = Field(default_factory=list, description="Promo indicators for highlighting")
