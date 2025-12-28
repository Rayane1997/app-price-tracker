from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class ProductStatus(str, Enum):
    ACTIVE = "active"
    ERROR = "error"
    NOT_TRACKABLE = "not_trackable"
    PAUSED = "paused"

# Base schema avec champs communs
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500, description="Product name")
    url: str = Field(..., description="Product URL")
    domain: str = Field(..., min_length=1, max_length=255, description="Domain (e.g., amazon.fr)")
    target_price: Optional[float] = Field(None, ge=0, description="Target price for alerts")
    image_url: Optional[str] = Field(None, description="Product image URL")
    check_frequency_hours: int = Field(24, ge=1, le=168, description="Check frequency in hours (1-168)")
    tags: Optional[str] = Field(None, max_length=500, description="Comma-separated tags")
    notes: Optional[str] = Field(None, description="User notes")

# Création de produit
class ProductCreate(ProductBase):
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v: str) -> str:
        # Extract domain from URL if needed
        return v.lower().strip()

# Mise à jour de produit (tous les champs optionnels)
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    url: Optional[str] = None
    target_price: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = None
    check_frequency_hours: Optional[int] = Field(None, ge=1, le=168)
    status: Optional[ProductStatus] = None
    tags: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None

# Réponse complète
class ProductResponse(BaseModel):
    id: int
    name: str
    url: str
    domain: str
    current_price: Optional[float] = None
    currency: str
    target_price: Optional[float] = None
    image_url: Optional[str] = None
    check_frequency_hours: int
    status: ProductStatus
    tags: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_checked_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    consecutive_errors: int
    last_error_message: Optional[str] = None

    class Config:
        from_attributes = True

# Liste de produits
class ProductList(BaseModel):
    products: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
