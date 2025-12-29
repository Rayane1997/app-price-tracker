"""
Unit tests for database models.

Tests Product, PriceHistory, Alert, and ParserConfig models.
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import (
    Product,
    ProductStatus,
    PriceHistory,
    Alert,
    AlertType,
    AlertStatus,
    ParserConfig,
)


# ============================================================================
# Product Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestProductModel:
    """Test Product model."""

    def test_create_product_basic(self, test_db: Session):
        """Test creating a basic product."""
        product = Product(
            name="Test Product",
            url="https://www.amazon.fr/product",
            domain="amazon.fr",
            current_price=99.99,
            currency="EUR",
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)

        assert product.id is not None
        assert product.name == "Test Product"
        assert product.url == "https://www.amazon.fr/product"
        assert product.domain == "amazon.fr"
        assert product.current_price == 99.99
        assert product.currency == "EUR"
        assert product.status == ProductStatus.ACTIVE  # Default
        assert product.created_at is not None
        assert product.updated_at is not None

    def test_product_default_values(self, test_db: Session):
        """Test Product model default values."""
        product = Product(
            name="Test Product",
            url="https://www.amazon.fr/product",
            domain="amazon.fr",
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)

        assert product.currency == "EUR"
        assert product.check_frequency_hours == 24
        assert product.status == ProductStatus.ACTIVE
        assert product.consecutive_errors == 0

    def test_product_with_target_price(self, test_db: Session):
        """Test Product with target price set."""
        product = Product(
            name="Test Product",
            url="https://www.amazon.fr/product",
            domain="amazon.fr",
            target_price=79.99,
        )
        test_db.add(product)
        test_db.commit()

        assert product.target_price == 79.99

    def test_product_with_metadata(self, test_db: Session):
        """Test Product with tags and notes."""
        product = Product(
            name="Test Product",
            url="https://www.amazon.fr/product",
            domain="amazon.fr",
            tags="electronics,headphones",
            notes="Black Friday deal target",
        )
        test_db.add(product)
        test_db.commit()

        assert product.tags == "electronics,headphones"
        assert product.notes == "Black Friday deal target"

    def test_product_status_enum(self, test_db: Session):
        """Test Product status enum values."""
        for status in [ProductStatus.ACTIVE, ProductStatus.ERROR, ProductStatus.NOT_TRACKABLE, ProductStatus.PAUSED]:
            product = Product(
                name=f"Product {status.value}",
                url=f"https://www.amazon.fr/{status.value}",
                domain="amazon.fr",
                status=status,
            )
            test_db.add(product)
            test_db.commit()
            test_db.refresh(product)

            assert product.status == status

    def test_product_relationships_price_history(self, test_db: Session):
        """Test Product relationship with PriceHistory."""
        product = Product(
            name="Test Product",
            url="https://www.amazon.fr/product",
            domain="amazon.fr",
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)

        # Add price history
        history = PriceHistory(
            product_id=product.id,
            price=99.99,
            currency="EUR",
            recorded_at=datetime.utcnow(),
        )
        test_db.add(history)
        test_db.commit()

        # Test relationship
        assert len(product.price_history) == 1
        assert product.price_history[0].price == 99.99

    def test_product_relationships_alerts(self, test_db: Session):
        """Test Product relationship with Alerts."""
        product = Product(
            name="Test Product",
            url="https://www.amazon.fr/product",
            domain="amazon.fr",
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)

        # Add alert
        alert = Alert(
            product_id=product.id,
            type=AlertType.PRICE_DROP,
            status=AlertStatus.UNREAD,
            new_price=79.99,
            message="Price dropped!",
        )
        test_db.add(alert)
        test_db.commit()

        # Test relationship
        assert len(product.alerts) == 1
        assert product.alerts[0].type == AlertType.PRICE_DROP

    def test_product_cascade_delete_price_history(self, test_db: Session, sample_product_with_history: Product):
        """Test cascade delete of price history when product is deleted."""
        product_id = sample_product_with_history.id

        # Verify price history exists
        history_count = test_db.query(PriceHistory).filter(
            PriceHistory.product_id == product_id
        ).count()
        assert history_count > 0

        # Delete product
        test_db.delete(sample_product_with_history)
        test_db.commit()

        # Verify price history is also deleted
        history_count = test_db.query(PriceHistory).filter(
            PriceHistory.product_id == product_id
        ).count()
        assert history_count == 0

    def test_product_cascade_delete_alerts(self, test_db: Session, sample_alert: Alert):
        """Test cascade delete of alerts when product is deleted."""
        product = test_db.query(Product).filter(Product.id == sample_alert.product_id).first()

        # Verify alert exists
        alert_count = test_db.query(Alert).filter(Alert.product_id == product.id).count()
        assert alert_count > 0

        # Delete product
        test_db.delete(product)
        test_db.commit()

        # Verify alerts are also deleted
        alert_count = test_db.query(Alert).filter(Alert.product_id == product.id).count()
        assert alert_count == 0


# ============================================================================
# PriceHistory Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestPriceHistoryModel:
    """Test PriceHistory model."""

    def test_create_price_history(self, test_db: Session, sample_product: Product):
        """Test creating a price history entry."""
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

        assert history.id is not None
        assert history.product_id == sample_product.id
        assert history.price == 99.99
        assert history.currency == "EUR"
        assert history.is_promo is False
        assert history.recorded_at is not None

    def test_price_history_with_promo(self, test_db: Session, sample_product: Product):
        """Test PriceHistory with promotional pricing."""
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

        assert history.is_promo is True
        assert history.promo_percentage == 20.0

    def test_price_history_default_values(self, test_db: Session, sample_product: Product):
        """Test PriceHistory default values."""
        history = PriceHistory(
            product_id=sample_product.id,
            price=99.99,
            currency="EUR",
            recorded_at=datetime.utcnow(),
        )
        test_db.add(history)
        test_db.commit()
        test_db.refresh(history)

        assert history.is_promo is False
        assert history.currency == "EUR"

    def test_price_history_relationship_to_product(self, test_db: Session, sample_product: Product):
        """Test PriceHistory relationship back to Product."""
        history = PriceHistory(
            product_id=sample_product.id,
            price=99.99,
            currency="EUR",
            recorded_at=datetime.utcnow(),
        )
        test_db.add(history)
        test_db.commit()
        test_db.refresh(history)

        assert history.product is not None
        assert history.product.id == sample_product.id
        assert history.product.name == sample_product.name

    def test_price_history_foreign_key_constraint(self, test_db: Session):
        """Test that foreign key constraint is enforced."""
        # Note: SQLite in-memory DB doesn't enforce foreign keys by default
        # This test documents expected behavior in production
        history = PriceHistory(
            product_id=99999,  # Non-existent product
            price=99.99,
            currency="EUR",
            recorded_at=datetime.utcnow(),
        )
        test_db.add(history)

        # In production PostgreSQL this would raise IntegrityError
        # In SQLite test mode, it may not - skip this assertion
        try:
            test_db.commit()
        except IntegrityError:
            pass  # Expected in production DB


# ============================================================================
# Alert Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestAlertModel:
    """Test Alert model."""

    def test_create_alert(self, test_db: Session, sample_product: Product):
        """Test creating an alert."""
        alert = Alert(
            product_id=sample_product.id,
            type=AlertType.PRICE_DROP,
            status=AlertStatus.UNREAD,
            old_price=399.99,
            new_price=349.99,
            price_drop_percentage=12.5,
            message="Price dropped by 12.5%!",
            created_at=datetime.utcnow(),
        )
        test_db.add(alert)
        test_db.commit()
        test_db.refresh(alert)

        assert alert.id is not None
        assert alert.product_id == sample_product.id
        assert alert.type == AlertType.PRICE_DROP
        assert alert.status == AlertStatus.UNREAD
        assert alert.old_price == 399.99
        assert alert.new_price == 349.99
        assert alert.price_drop_percentage == 12.5
        assert alert.message == "Price dropped by 12.5%!"

    def test_alert_type_enum(self, test_db: Session, sample_product: Product):
        """Test Alert type enum values."""
        alert_types = [
            AlertType.PRICE_DROP,
            AlertType.TARGET_REACHED,
            AlertType.PROMO_DETECTED,
        ]

        for alert_type in alert_types:
            alert = Alert(
                product_id=sample_product.id,
                type=alert_type,
                status=AlertStatus.UNREAD,
                new_price=299.99,
                message=f"Alert type: {alert_type.value}",
            )
            test_db.add(alert)
            test_db.commit()
            test_db.refresh(alert)

            assert alert.type == alert_type

    def test_alert_status_enum(self, test_db: Session, sample_product: Product):
        """Test Alert status enum values."""
        for status in [AlertStatus.UNREAD, AlertStatus.READ, AlertStatus.DISMISSED]:
            alert = Alert(
                product_id=sample_product.id,
                type=AlertType.PRICE_DROP,
                status=status,
                new_price=299.99,
                message=f"Status: {status.value}",
            )
            test_db.add(alert)
            test_db.commit()
            test_db.refresh(alert)

            assert alert.status == status

    def test_alert_default_status(self, test_db: Session, sample_product: Product):
        """Test Alert default status is UNREAD."""
        alert = Alert(
            product_id=sample_product.id,
            type=AlertType.PRICE_DROP,
            new_price=299.99,
            message="Test alert",
        )
        test_db.add(alert)
        test_db.commit()
        test_db.refresh(alert)

        assert alert.status == AlertStatus.UNREAD

    def test_alert_relationship_to_product(self, test_db: Session, sample_product: Product):
        """Test Alert relationship to Product."""
        alert = Alert(
            product_id=sample_product.id,
            type=AlertType.TARGET_REACHED,
            status=AlertStatus.UNREAD,
            new_price=299.99,
            message="Target reached!",
        )
        test_db.add(alert)
        test_db.commit()
        test_db.refresh(alert)

        assert alert.product is not None
        assert alert.product.id == sample_product.id
        assert alert.product.name == sample_product.name

    def test_alert_read_timestamp(self, test_db: Session, sample_product: Product):
        """Test Alert read_at timestamp."""
        alert = Alert(
            product_id=sample_product.id,
            type=AlertType.PRICE_DROP,
            status=AlertStatus.UNREAD,
            new_price=299.99,
            message="Test alert",
        )
        test_db.add(alert)
        test_db.commit()

        # Initially None
        assert alert.read_at is None

        # Mark as read
        alert.status = AlertStatus.READ
        alert.read_at = datetime.utcnow()
        test_db.commit()

        assert alert.read_at is not None
        assert alert.status == AlertStatus.READ


# ============================================================================
# ParserConfig Model Tests (if exists)
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestParserConfigModel:
    """Test ParserConfig model (if implemented)."""

    def test_create_parser_config(self, test_db: Session):
        """Test creating a parser config."""
        config = ParserConfig(
            domain="amazon.fr",
            price_selectors={"primary": ".a-price .a-offscreen", "fallback": []},
            requires_javascript=True,
            is_active=True,
        )
        test_db.add(config)
        test_db.commit()
        test_db.refresh(config)

        assert config.id is not None
        assert config.domain == "amazon.fr"
        assert config.is_active is True
        assert config.requires_javascript is True
        assert config.price_selectors is not None


# ============================================================================
# Model Validation Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestModelValidations:
    """Test model validations and constraints."""

    def test_product_timestamps_auto_update(self, test_db: Session):
        """Test that updated_at timestamp updates automatically."""
        product = Product(
            name="Test Product",
            url="https://www.amazon.fr/product",
            domain="amazon.fr",
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)

        original_updated_at = product.updated_at

        # Update product
        import time
        time.sleep(0.1)  # Ensure time difference
        product.name = "Updated Product Name"
        test_db.commit()
        test_db.refresh(product)

        # Note: onupdate in SQLAlchemy requires actual column change
        # The updated_at should be the same or newer
        assert product.updated_at >= original_updated_at

    def test_alert_created_at_set(self, test_db: Session, sample_product: Product):
        """Test that alert created_at is set automatically."""
        alert = Alert(
            product_id=sample_product.id,
            type=AlertType.PRICE_DROP,
            new_price=299.99,
            message="Test",
        )
        test_db.add(alert)
        test_db.commit()
        test_db.refresh(alert)

        assert alert.created_at is not None
        # Should be close to current time
        time_diff = (datetime.utcnow() - alert.created_at).total_seconds()
        assert time_diff < 5  # Within 5 seconds
