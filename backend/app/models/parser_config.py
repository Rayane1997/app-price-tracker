from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from datetime import datetime
from ..core.database import Base

class ParserConfig(Base):
    __tablename__ = "parser_configs"

    id = Column(Integer, primary_key=True, index=True)

    # Domain info
    domain = Column(String(255), unique=True, nullable=False, index=True)
    domain_pattern = Column(String(500), nullable=True)  # Regex pattern

    # Parser strategy
    requires_javascript = Column(Boolean, default=False)
    use_playwright = Column(Boolean, default=False)

    # Selectors (JSON with fallbacks)
    price_selectors = Column(JSON, nullable=False)  # {"primary": "...", "fallback": [...]}
    name_selectors = Column(JSON, nullable=True)
    image_selectors = Column(JSON, nullable=True)

    # Rate limiting
    rate_limit_seconds = Column(Integer, default=5)
    max_retries = Column(Integer, default=3)

    # Status
    is_active = Column(Boolean, default=True)
    error_count = Column(Integer, default=0)
    last_error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
