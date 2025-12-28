from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class AlertType(str, enum.Enum):
    PRICE_DROP = "price_drop"
    TARGET_REACHED = "target_reached"
    PROMO_DETECTED = "promo_detected"

class AlertStatus(str, enum.Enum):
    UNREAD = "unread"
    READ = "read"
    DISMISSED = "dismissed"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)

    # Alert info
    type = Column(Enum(AlertType), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.UNREAD, index=True)

    # Price data
    old_price = Column(Float, nullable=True)
    new_price = Column(Float, nullable=False)
    price_drop_percentage = Column(Float, nullable=True)

    # Message
    message = Column(Text, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    product = relationship("Product", back_populates="alerts")
