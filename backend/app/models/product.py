from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class ProductStatus(str, enum.Enum):
    ACTIVE = "active"
    ERROR = "error"
    NOT_TRACKABLE = "not_trackable"
    PAUSED = "paused"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    url = Column(Text, nullable=False)
    domain = Column(String(255), nullable=False, index=True)

    # Current price info
    current_price = Column(Float, nullable=True)
    currency = Column(String(3), default="EUR")
    target_price = Column(Float, nullable=True)

    # Image
    image_url = Column(Text, nullable=True)

    # Tracking config
    check_frequency_hours = Column(Integer, default=24)
    status = Column(Enum(ProductStatus), default=ProductStatus.ACTIVE, index=True)

    # Metadata
    tags = Column(String(500), nullable=True)  # Comma-separated
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_checked_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)

    # Error tracking
    consecutive_errors = Column(Integer, default=0)
    last_error_message = Column(Text, nullable=True)

    # Relationships
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="product", cascade="all, delete-orphan")
