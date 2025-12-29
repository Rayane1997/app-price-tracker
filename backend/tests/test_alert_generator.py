"""
Unit tests for alert generation logic.

Tests all 3 alert types: TARGET_REACHED, PRICE_DROP, PROMO_DETECTED.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.utils.alert_generator import (
    get_previous_price,
    has_recent_alert,
    create_alert,
    check_and_create_alerts,
)
from app.models import Product, ProductStatus, PriceHistory, Alert, AlertType, AlertStatus


# ============================================================================
# Get Previous Price Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestGetPreviousPrice:
    """Test get_previous_price function."""

    def test_get_previous_price_with_history(self, test_db: Session, sample_product_with_history: Product):
        """Test getting previous price with existing price history."""
        previous_price = get_previous_price(test_db, sample_product_with_history.id)

        # Should return second most recent price (119.99)
        assert previous_price == 119.99

    def test_get_previous_price_single_entry(self, test_db: Session, sample_product: Product):
        """Test getting previous price with only one price entry."""
        # Add single price entry
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=349.99,
            currency="EUR",
            recorded_at=datetime.utcnow(),
        ))
        test_db.commit()

        previous_price = get_previous_price(test_db, sample_product.id)
        # Should return None (only one entry)
        assert previous_price is None

    def test_get_previous_price_no_history(self, test_db: Session, sample_product: Product):
        """Test getting previous price with no price history."""
        previous_price = get_previous_price(test_db, sample_product.id)
        assert previous_price is None

    def test_get_previous_price_ignores_none_prices(self, test_db: Session, sample_product: Product):
        """Test that None prices are ignored."""
        now = datetime.utcnow()

        # Add entries with None price (failed scrapes)
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=None,
            currency="EUR",
            recorded_at=now,
        ))
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=99.99,
            currency="EUR",
            recorded_at=now - timedelta(hours=1),
        ))
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=89.99,
            currency="EUR",
            recorded_at=now - timedelta(hours=2),
        ))
        test_db.commit()

        previous_price = get_previous_price(test_db, sample_product.id)
        # Should skip None and return 89.99
        assert previous_price == 89.99


# ============================================================================
# Has Recent Alert Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestHasRecentAlert:
    """Test has_recent_alert function."""

    def test_has_recent_alert_true(self, test_db: Session, sample_alert: Alert):
        """Test that recent alert is detected."""
        result = has_recent_alert(
            test_db,
            sample_alert.product_id,
            AlertType.PRICE_DROP,
            hours=24
        )
        assert result is True

    def test_has_recent_alert_false_no_alerts(self, test_db: Session, sample_product: Product):
        """Test that no recent alert is detected when none exist."""
        result = has_recent_alert(
            test_db,
            sample_product.id,
            AlertType.PRICE_DROP,
            hours=24
        )
        assert result is False

    def test_has_recent_alert_false_different_type(self, test_db: Session, sample_alert: Alert):
        """Test that alerts of different type don't count."""
        # sample_alert is PRICE_DROP
        result = has_recent_alert(
            test_db,
            sample_alert.product_id,
            AlertType.TARGET_REACHED,  # Different type
            hours=24
        )
        assert result is False

    def test_has_recent_alert_false_old_alert(self, test_db: Session, sample_product: Product):
        """Test that old alerts don't count as recent."""
        # Create old alert (48 hours ago)
        old_alert = Alert(
            product_id=sample_product.id,
            type=AlertType.PRICE_DROP,
            status=AlertStatus.UNREAD,
            old_price=399.99,
            new_price=349.99,
            message="Old alert",
            created_at=datetime.utcnow() - timedelta(hours=48),
        )
        test_db.add(old_alert)
        test_db.commit()

        # Check for recent alert (last 24 hours)
        result = has_recent_alert(
            test_db,
            sample_product.id,
            AlertType.PRICE_DROP,
            hours=24
        )
        assert result is False

    def test_has_recent_alert_custom_timeframe(self, test_db: Session, sample_product: Product):
        """Test has_recent_alert with custom timeframe."""
        # Create alert 12 hours ago
        alert = Alert(
            product_id=sample_product.id,
            type=AlertType.PRICE_DROP,
            status=AlertStatus.UNREAD,
            old_price=399.99,
            new_price=349.99,
            message="Recent alert",
            created_at=datetime.utcnow() - timedelta(hours=12),
        )
        test_db.add(alert)
        test_db.commit()

        # Should be found with 24-hour window
        assert has_recent_alert(test_db, sample_product.id, AlertType.PRICE_DROP, hours=24) is True

        # Should not be found with 6-hour window
        assert has_recent_alert(test_db, sample_product.id, AlertType.PRICE_DROP, hours=6) is False


# ============================================================================
# Create Alert Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestCreateAlert:
    """Test create_alert function."""

    def test_create_alert_basic(self, test_db: Session, sample_product: Product):
        """Test creating a basic alert."""
        alert = create_alert(
            db=test_db,
            product_id=sample_product.id,
            alert_type=AlertType.PRICE_DROP,
            message="Price dropped!",
            old_price=399.99,
            new_price=349.99,
            price_drop_percentage=12.5,
        )

        assert alert.id is not None
        assert alert.product_id == sample_product.id
        assert alert.type == AlertType.PRICE_DROP
        assert alert.status == AlertStatus.UNREAD
        assert alert.old_price == 399.99
        assert alert.new_price == 349.99
        assert alert.price_drop_percentage == 12.5
        assert alert.message == "Price dropped!"
        assert alert.created_at is not None

    def test_create_alert_without_old_price(self, test_db: Session, sample_product: Product):
        """Test creating alert without old price (e.g., TARGET_REACHED)."""
        alert = create_alert(
            db=test_db,
            product_id=sample_product.id,
            alert_type=AlertType.TARGET_REACHED,
            message="Target reached!",
            old_price=None,
            new_price=299.99,
        )

        assert alert.old_price is None
        assert alert.new_price == 299.99
        assert alert.price_drop_percentage is None

    def test_create_alert_persists_to_database(self, test_db: Session, sample_product: Product):
        """Test that created alert is persisted to database."""
        alert = create_alert(
            db=test_db,
            product_id=sample_product.id,
            alert_type=AlertType.PROMO_DETECTED,
            message="Promo detected!",
            old_price=349.99,
            new_price=279.99,
        )

        # Verify it can be queried from database
        db_alert = test_db.query(Alert).filter(Alert.id == alert.id).first()
        assert db_alert is not None
        assert db_alert.type == AlertType.PROMO_DETECTED


# ============================================================================
# Check and Create Alerts Tests (Main Function)
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestCheckAndCreateAlerts:
    """Test check_and_create_alerts function (main alert logic)."""

    def test_target_reached_alert_created(self, test_db: Session, sample_product: Product):
        """Test TARGET_REACHED alert creation when price reaches target."""
        # Set target price
        sample_product.target_price = 299.99
        test_db.commit()

        # Add price history
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=349.99,
            currency="EUR",
            recorded_at=datetime.utcnow() - timedelta(hours=1),
        ))
        test_db.commit()

        # Check alerts with new price at/below target
        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=299.99,
            is_promo=False
        )

        assert len(alerts) == 1
        assert alerts[0].type == AlertType.TARGET_REACHED
        assert alerts[0].new_price == 299.99
        assert "target" in alerts[0].message.lower()

    def test_target_reached_alert_not_created_above_target(self, test_db: Session, sample_product: Product):
        """Test TARGET_REACHED alert not created when price above target."""
        sample_product.target_price = 299.99
        test_db.commit()

        # Price above target
        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=349.99,
            is_promo=False
        )

        # No TARGET_REACHED alert should be created
        target_alerts = [a for a in alerts if a.type == AlertType.TARGET_REACHED]
        assert len(target_alerts) == 0

    def test_price_drop_alert_created(self, test_db: Session, sample_product: Product):
        """Test PRICE_DROP alert creation when price drops >= 10%."""
        # Add price history with NEW price already added (simulating after scrape)
        # Most recent (new) = 358.99, Previous = 399.99
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=399.99,
            currency="EUR",
            recorded_at=datetime.utcnow() - timedelta(hours=2),
        ))
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=358.99,
            currency="EUR",
            recorded_at=datetime.utcnow() - timedelta(hours=1),
        ))
        test_db.commit()

        # Check alerts - the function expects new_price to already be in history
        # Previous price (399.99) compared to new price (358.99) = 10.25% drop
        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=358.99,
            is_promo=False
        )

        price_drop_alerts = [a for a in alerts if a.type == AlertType.PRICE_DROP]
        assert len(price_drop_alerts) == 1
        assert price_drop_alerts[0].old_price == 399.99
        assert price_drop_alerts[0].new_price == 358.99
        assert price_drop_alerts[0].price_drop_percentage >= 10.0

    def test_price_drop_alert_not_created_small_drop(self, test_db: Session, sample_product: Product):
        """Test PRICE_DROP alert not created when drop < 10%."""
        # Add previous price
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=100.0,
            currency="EUR",
            recorded_at=datetime.utcnow(),
        ))
        test_db.commit()

        # Only 5% drop
        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=95.0,
            is_promo=False
        )

        price_drop_alerts = [a for a in alerts if a.type == AlertType.PRICE_DROP]
        assert len(price_drop_alerts) == 0

    def test_promo_detected_alert_created(self, test_db: Session, sample_product: Product):
        """Test PROMO_DETECTED alert creation when promo starts."""
        # Add non-promo history
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=349.99,
            currency="EUR",
            is_promo=False,
            recorded_at=datetime.utcnow() - timedelta(hours=1),
        ))
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=349.99,
            currency="EUR",
            is_promo=False,
            recorded_at=datetime.utcnow(),
        ))
        test_db.commit()

        # Check alerts with promo
        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=279.99,
            is_promo=True
        )

        promo_alerts = [a for a in alerts if a.type == AlertType.PROMO_DETECTED]
        assert len(promo_alerts) == 1
        assert promo_alerts[0].new_price == 279.99
        assert "promo" in promo_alerts[0].message.lower() or "sale" in promo_alerts[0].message.lower()

    def test_promo_detected_alert_not_created_if_already_promo(self, test_db: Session, sample_promo_product: Product):
        """Test PROMO_DETECTED alert not created if already on promo."""
        # Product already has promo history
        # Add another promo entry
        test_db.add(PriceHistory(
            product_id=sample_promo_product.id,
            price=75.99,
            currency="EUR",
            is_promo=True,
            promo_percentage=25.0,
            recorded_at=datetime.utcnow(),
        ))
        test_db.commit()

        # Check alerts with promo (but was already promo)
        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_promo_product,
            new_price=75.99,
            is_promo=True
        )

        promo_alerts = [a for a in alerts if a.type == AlertType.PROMO_DETECTED]
        # Should not create new PROMO_DETECTED alert
        assert len(promo_alerts) == 0

    def test_multiple_alerts_created(self, test_db: Session, sample_product: Product):
        """Test multiple alerts can be created at once."""
        sample_product.target_price = 250.0
        test_db.commit()

        # Add previous non-promo price
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=399.99,
            currency="EUR",
            is_promo=False,
            recorded_at=datetime.utcnow() - timedelta(hours=1),
        ))
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=399.99,
            currency="EUR",
            is_promo=False,
            recorded_at=datetime.utcnow(),
        ))
        test_db.commit()

        # New price: on promo, reaches target, and drops >10%
        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=249.99,
            is_promo=True
        )

        # Should create all 3 types
        alert_types = [a.type for a in alerts]
        assert AlertType.TARGET_REACHED in alert_types
        assert AlertType.PRICE_DROP in alert_types
        assert AlertType.PROMO_DETECTED in alert_types

    def test_anti_spam_prevents_duplicate_alerts(self, test_db: Session, sample_product: Product):
        """Test anti-spam mechanism prevents duplicate alerts within 24h."""
        sample_product.target_price = 299.99
        test_db.commit()

        # Create first alert
        alerts1 = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=299.99,
            is_promo=False
        )
        assert len(alerts1) == 1

        # Try to create same type of alert again immediately
        alerts2 = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=299.99,
            is_promo=False
        )

        # Should not create duplicate
        assert len(alerts2) == 0

    def test_no_alert_created_when_price_none(self, test_db: Session, sample_product: Product):
        """Test no alerts created when new_price is None (failed scrape)."""
        sample_product.target_price = 299.99
        test_db.commit()

        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=None,
            is_promo=False
        )

        assert len(alerts) == 0

    def test_no_alert_without_previous_price_for_price_drop(self, test_db: Session, sample_product: Product):
        """Test PRICE_DROP alert not created without previous price."""
        # No price history

        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=299.99,
            is_promo=False
        )

        # Should not create PRICE_DROP alert (no previous price to compare)
        price_drop_alerts = [a for a in alerts if a.type == AlertType.PRICE_DROP]
        assert len(price_drop_alerts) == 0

    def test_target_reached_exact_match(self, test_db: Session, sample_product: Product):
        """Test TARGET_REACHED alert when price exactly matches target."""
        sample_product.target_price = 299.99
        test_db.commit()

        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=299.99,  # Exactly at target
            is_promo=False
        )

        target_alerts = [a for a in alerts if a.type == AlertType.TARGET_REACHED]
        assert len(target_alerts) == 1


# ============================================================================
# Edge Cases Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestAlertGeneratorEdgeCases:
    """Test edge cases for alert generator."""

    def test_price_drop_exactly_10_percent(self, test_db: Session, sample_product: Product):
        """Test PRICE_DROP alert created when drop is exactly 10%."""
        # Add both prices to history (old and new)
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=100.0,
            currency="EUR",
            recorded_at=datetime.utcnow() - timedelta(hours=1),
        ))
        test_db.add(PriceHistory(
            product_id=sample_product.id,
            price=90.0,
            currency="EUR",
            recorded_at=datetime.utcnow(),
        ))
        test_db.commit()

        # Exactly 10% drop
        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=90.0,
            is_promo=False
        )

        price_drop_alerts = [a for a in alerts if a.type == AlertType.PRICE_DROP]
        assert len(price_drop_alerts) == 1
        assert price_drop_alerts[0].price_drop_percentage == 10.0

    def test_target_price_below_current_creates_alert(self, test_db: Session, sample_product: Product):
        """Test TARGET_REACHED alert when new price is below target."""
        sample_product.target_price = 299.99
        test_db.commit()

        # Price below target
        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=249.99,
            is_promo=False
        )

        target_alerts = [a for a in alerts if a.type == AlertType.TARGET_REACHED]
        assert len(target_alerts) == 1

    def test_no_target_alert_when_target_not_set(self, test_db: Session, sample_product: Product):
        """Test no TARGET_REACHED alert when target_price is None."""
        sample_product.target_price = None
        test_db.commit()

        alerts = check_and_create_alerts(
            db=test_db,
            product=sample_product,
            new_price=199.99,
            is_promo=False
        )

        target_alerts = [a for a in alerts if a.type == AlertType.TARGET_REACHED]
        assert len(target_alerts) == 0
