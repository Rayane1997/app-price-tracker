from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)

    # Price data
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    is_promo = Column(Boolean, default=False)
    promo_percentage = Column(Float, nullable=True)

    # Source
    source = Column(String(50), default="scraper")  # scraper, manual, api
    scrape_duration_ms = Column(Integer, nullable=True)

    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    product = relationship("Product", back_populates="price_history")
