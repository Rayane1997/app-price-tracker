from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ParserConfigBase(BaseModel):
    """Base schema for ParserConfig"""
    domain: str = Field(..., min_length=1, max_length=255, description="Domain (e.g., amazon.fr)")
    price_selectors: List[str] = Field(..., min_length=1, description="Ordered price CSS selectors")
    name_selectors: Optional[List[str]] = Field(None, description="Name CSS selectors")
    image_selectors: Optional[List[str]] = Field(None, description="Image CSS selectors")
    use_playwright: bool = Field(False, description="Use Playwright for JavaScript rendering")
    domain_pattern: Optional[str] = Field(None, max_length=500, description="Regex pattern for domain")
    rate_limit_seconds: float = Field(1.0, gt=0, description="Rate limit in seconds")
    max_retries: int = Field(3, ge=0, description="Maximum retries")
    is_active: bool = Field(True, description="Is configuration active")


class ParserConfigCreate(ParserConfigBase):
    """Schema for creating ParserConfig"""
    pass


class ParserConfigUpdate(BaseModel):
    """Schema for updating ParserConfig (all fields optional)"""
    domain: Optional[str] = Field(None, min_length=1, max_length=255)
    price_selectors: Optional[List[str]] = None
    name_selectors: Optional[List[str]] = None
    image_selectors: Optional[List[str]] = None
    use_playwright: Optional[bool] = None
    domain_pattern: Optional[str] = Field(None, max_length=500)
    rate_limit_seconds: Optional[float] = Field(None, gt=0)
    max_retries: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ParserConfigResponse(BaseModel):
    """Complete ParserConfig response"""
    id: int
    domain: str
    price_selectors: List[str]
    name_selectors: Optional[List[str]] = None
    image_selectors: Optional[List[str]] = None
    use_playwright: bool
    domain_pattern: Optional[str] = None
    rate_limit_seconds: float
    max_retries: int
    is_active: bool
    error_count: int
    last_error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ParserConfigList(BaseModel):
    """Paginated list of ParserConfigs"""
    configs: list[ParserConfigResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
