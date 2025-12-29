"""
Unit tests for Pydantic schemas.

Tests validation, required fields, defaults, and type conversions.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.product import (
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductStatus,
)
from app.schemas.alert import AlertResponse, AlertType, AlertStatus
from app.schemas.price_history import PriceHistoryResponse


# ============================================================================
# Product Schema Tests
# ============================================================================

@pytest.mark.unit
class TestProductCreateSchema:
    """Test ProductCreate schema."""

    def test_product_create_valid(self):
        """Test creating ProductCreate with valid data."""
        data = {
            "name": "Sony WH-1000XM5",
            "url": "https://www.amazon.fr/dp/B09XS7JWHH",
            "domain": "amazon.fr",
            "target_price": 299.99,
            "check_frequency_hours": 24,
        }
        product = ProductCreate(**data)

        assert product.name == "Sony WH-1000XM5"
        assert product.url == "https://www.amazon.fr/dp/B09XS7JWHH"
        assert product.domain == "amazon.fr"
        assert product.target_price == 299.99
        assert product.check_frequency_hours == 24

    def test_product_create_required_fields(self):
        """Test that required fields are enforced."""
        # Missing required fields
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(url="https://amazon.fr/test")

        errors = exc_info.value.errors()
        field_names = [error['loc'][0] for error in errors]
        assert 'name' in field_names
        assert 'domain' in field_names

    def test_product_create_url_validation(self):
        """Test URL validation."""
        data = {
            "name": "Test Product",
            "url": "invalid-url",
            "domain": "amazon.fr",
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        errors = exc_info.value.errors()
        assert any('url' in str(error['loc']) for error in errors)

    def test_product_create_url_with_http(self):
        """Test that URL must start with http:// or https://."""
        data = {
            "name": "Test Product",
            "url": "www.amazon.fr/product",
            "domain": "amazon.fr",
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

    def test_product_create_domain_normalization(self):
        """Test domain is normalized to lowercase."""
        data = {
            "name": "Test Product",
            "url": "https://www.amazon.fr/product",
            "domain": "AMAZON.FR",
        }
        product = ProductCreate(**data)

        assert product.domain == "amazon.fr"

    def test_product_create_default_values(self):
        """Test default values are applied."""
        data = {
            "name": "Test Product",
            "url": "https://www.amazon.fr/product",
            "domain": "amazon.fr",
        }
        product = ProductCreate(**data)

        assert product.check_frequency_hours == 24
        assert product.target_price is None
        assert product.image_url is None

    def test_product_create_optional_fields(self):
        """Test optional fields."""
        data = {
            "name": "Test Product",
            "url": "https://www.amazon.fr/product",
            "domain": "amazon.fr",
            "target_price": 199.99,
            "image_url": "https://example.com/image.jpg",
            "tags": "electronics,headphones",
            "notes": "Great product",
        }
        product = ProductCreate(**data)

        assert product.target_price == 199.99
        assert product.image_url == "https://example.com/image.jpg"
        assert product.tags == "electronics,headphones"
        assert product.notes == "Great product"

    def test_product_create_check_frequency_validation(self):
        """Test check_frequency_hours validation (1-168)."""
        # Valid value
        data = {
            "name": "Test Product",
            "url": "https://www.amazon.fr/product",
            "domain": "amazon.fr",
            "check_frequency_hours": 48,
        }
        product = ProductCreate(**data)
        assert product.check_frequency_hours == 48

        # Invalid: too low
        data["check_frequency_hours"] = 0
        with pytest.raises(ValidationError):
            ProductCreate(**data)

        # Invalid: too high
        data["check_frequency_hours"] = 200
        with pytest.raises(ValidationError):
            ProductCreate(**data)

    def test_product_create_target_price_validation(self):
        """Test target_price validation (must be >= 0)."""
        data = {
            "name": "Test Product",
            "url": "https://www.amazon.fr/product",
            "domain": "amazon.fr",
            "target_price": -10.0,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        errors = exc_info.value.errors()
        assert any('target_price' in str(error['loc']) for error in errors)

    def test_product_create_name_length_validation(self):
        """Test name length validation."""
        # Too short
        data = {
            "name": "",
            "url": "https://www.amazon.fr/product",
            "domain": "amazon.fr",
        }
        with pytest.raises(ValidationError):
            ProductCreate(**data)

        # Too long (>500 chars)
        data["name"] = "A" * 501
        with pytest.raises(ValidationError):
            ProductCreate(**data)


@pytest.mark.unit
class TestProductUpdateSchema:
    """Test ProductUpdate schema."""

    def test_product_update_all_optional(self):
        """Test that all fields in ProductUpdate are optional."""
        # Empty update should be valid
        product = ProductUpdate()
        assert product.name is None
        assert product.url is None
        assert product.target_price is None

    def test_product_update_partial(self):
        """Test partial update with some fields."""
        data = {
            "target_price": 249.99,
            "status": ProductStatus.PAUSED,
        }
        product = ProductUpdate(**data)

        assert product.target_price == 249.99
        assert product.status == ProductStatus.PAUSED
        assert product.name is None  # Not updated

    def test_product_update_status_enum(self):
        """Test status enum validation."""
        data = {"status": ProductStatus.ACTIVE}
        product = ProductUpdate(**data)
        assert product.status == ProductStatus.ACTIVE

        # Invalid status
        with pytest.raises(ValidationError):
            ProductUpdate(status="invalid_status")

    def test_product_update_validations_apply(self):
        """Test that validations apply to ProductUpdate."""
        # Negative target price
        with pytest.raises(ValidationError):
            ProductUpdate(target_price=-10.0)

        # Invalid check frequency
        with pytest.raises(ValidationError):
            ProductUpdate(check_frequency_hours=0)


@pytest.mark.unit
class TestProductResponseSchema:
    """Test ProductResponse schema."""

    def test_product_response_from_orm(self, sample_product):
        """Test ProductResponse can be created from ORM model."""
        response = ProductResponse.model_validate(sample_product)

        assert response.id == sample_product.id
        assert response.name == sample_product.name
        assert response.url == sample_product.url
        assert response.domain == sample_product.domain
        assert response.current_price == sample_product.current_price
        assert response.currency == sample_product.currency
        assert response.status == sample_product.status

    def test_product_response_all_fields(self, sample_product):
        """Test ProductResponse includes all fields."""
        response = ProductResponse.model_validate(sample_product)

        # Check all expected fields exist
        assert hasattr(response, 'id')
        assert hasattr(response, 'name')
        assert hasattr(response, 'url')
        assert hasattr(response, 'domain')
        assert hasattr(response, 'current_price')
        assert hasattr(response, 'currency')
        assert hasattr(response, 'target_price')
        assert hasattr(response, 'image_url')
        assert hasattr(response, 'check_frequency_hours')
        assert hasattr(response, 'status')
        assert hasattr(response, 'created_at')
        assert hasattr(response, 'updated_at')
        assert hasattr(response, 'last_checked_at')
        assert hasattr(response, 'consecutive_errors')


# ============================================================================
# Alert Schema Tests
# ============================================================================

@pytest.mark.unit
class TestAlertResponseSchema:
    """Test AlertResponse schema."""

    def test_alert_response_from_orm(self, sample_alert):
        """Test AlertResponse can be created from ORM model."""
        response = AlertResponse.model_validate(sample_alert)

        assert response.id == sample_alert.id
        assert response.product_id == sample_alert.product_id
        assert response.type == sample_alert.type
        assert response.status == sample_alert.status
        assert response.old_price == sample_alert.old_price
        assert response.new_price == sample_alert.new_price
        assert response.price_drop_percentage == sample_alert.price_drop_percentage
        assert response.message == sample_alert.message

    def test_alert_type_enum_values(self):
        """Test AlertType enum values."""
        assert AlertType.PRICE_DROP == "price_drop"
        assert AlertType.TARGET_REACHED == "target_reached"
        assert AlertType.PROMO_DETECTED == "promo_detected"

    def test_alert_status_enum_values(self):
        """Test AlertStatus enum values."""
        assert AlertStatus.UNREAD == "unread"
        assert AlertStatus.READ == "read"
        assert AlertStatus.DISMISSED == "dismissed"


# ============================================================================
# PriceHistory Schema Tests
# ============================================================================

@pytest.mark.unit
class TestPriceHistoryResponseSchema:
    """Test PriceHistoryResponse schema."""

    def test_price_history_response_from_orm(self, test_db, sample_product):
        """Test PriceHistoryResponse can be created from ORM model."""
        from app.models import PriceHistory

        history = PriceHistory(
            product_id=sample_product.id,
            price=99.99,
            currency="EUR",
            is_promo=False,
            recorded_at=datetime.utcnow(),
        )
        test_db.add(history)
        test_db.commit()
        test_db.refresh(history)

        response = PriceHistoryResponse.model_validate(history)

        assert response.id == history.id
        assert response.product_id == history.product_id
        assert response.price == history.price
        assert response.currency == history.currency
        assert response.is_promo == history.is_promo
        assert response.recorded_at == history.recorded_at

    def test_price_history_with_promo(self, test_db, sample_product):
        """Test PriceHistoryResponse with promotional data."""
        from app.models import PriceHistory

        history = PriceHistory(
            product_id=sample_product.id,
            price=79.99,
            currency="EUR",
            is_promo=True,
            promo_percentage=20.0,
            recorded_at=datetime.utcnow(),
        )
        test_db.add(history)
        test_db.commit()
        test_db.refresh(history)

        response = PriceHistoryResponse.model_validate(history)

        assert response.is_promo is True
        assert response.promo_percentage == 20.0


# ============================================================================
# Schema Validation Edge Cases
# ============================================================================

@pytest.mark.unit
class TestSchemaEdgeCases:
    """Test edge cases for schema validation."""

    def test_product_create_with_unicode_name(self):
        """Test ProductCreate with unicode characters in name."""
        data = {
            "name": "Écouteurs Sony WH-1000XM5 — Édition Spéciale",
            "url": "https://www.amazon.fr/product",
            "domain": "amazon.fr",
        }
        product = ProductCreate(**data)
        assert product.name == "Écouteurs Sony WH-1000XM5 — Édition Spéciale"

    def test_product_create_with_long_url(self):
        """Test ProductCreate with very long URL."""
        long_url = "https://www.amazon.fr/product?" + ("param=value&" * 100)
        data = {
            "name": "Test Product",
            "url": long_url,
            "domain": "amazon.fr",
        }
        product = ProductCreate(**data)
        assert product.url == long_url

    def test_product_update_with_none_explicitly(self):
        """Test ProductUpdate can set fields to None."""
        data = {
            "target_price": None,
            "notes": None,
        }
        product = ProductUpdate(**data)
        assert product.target_price is None
        assert product.notes is None

    def test_product_create_tags_with_special_chars(self):
        """Test ProductCreate with special characters in tags."""
        data = {
            "name": "Test Product",
            "url": "https://www.amazon.fr/product",
            "domain": "amazon.fr",
            "tags": "electronics,high-end,noise-canceling,Bluetooth 5.0",
        }
        product = ProductCreate(**data)
        assert product.tags == "electronics,high-end,noise-canceling,Bluetooth 5.0"

    def test_product_create_zero_target_price(self):
        """Test ProductCreate with zero target price (valid edge case)."""
        data = {
            "name": "Test Product",
            "url": "https://www.amazon.fr/product",
            "domain": "amazon.fr",
            "target_price": 0.0,
        }
        product = ProductCreate(**data)
        assert product.target_price == 0.0

    def test_product_response_datetime_serialization(self, sample_product):
        """Test that datetime fields are properly serialized."""
        response = ProductResponse.model_validate(sample_product)

        # Should be datetime objects
        assert isinstance(response.created_at, datetime)
        assert isinstance(response.updated_at, datetime)

        # Should be serializable to JSON
        json_data = response.model_dump()
        assert 'created_at' in json_data
        assert 'updated_at' in json_data

    def test_product_create_domain_with_spaces(self):
        """Test domain normalization removes spaces."""
        data = {
            "name": "Test Product",
            "url": "https://www.amazon.fr/product",
            "domain": "  amazon.fr  ",
        }
        product = ProductCreate(**data)
        assert product.domain == "amazon.fr"

    def test_product_create_check_frequency_boundaries(self):
        """Test check_frequency_hours at boundaries."""
        # Minimum valid value
        data = {
            "name": "Test Product",
            "url": "https://www.amazon.fr/product",
            "domain": "amazon.fr",
            "check_frequency_hours": 1,
        }
        product = ProductCreate(**data)
        assert product.check_frequency_hours == 1

        # Maximum valid value
        data["check_frequency_hours"] = 168
        product = ProductCreate(**data)
        assert product.check_frequency_hours == 168

    def test_product_name_minimum_length(self):
        """Test product name must have minimum length."""
        data = {
            "name": "A",
            "url": "https://www.amazon.fr/product",
            "domain": "amazon.fr",
        }
        # Should be valid (min_length=1)
        product = ProductCreate(**data)
        assert product.name == "A"
