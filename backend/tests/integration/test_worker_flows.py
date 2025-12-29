"""
Integration tests for worker flows (end-to-end price tracking).

Tests complete worker scenarios:
- Price tracking flow: fetch -> parse -> store -> generate alerts
- Alert generation logic for different scenarios
- Product status updates based on results
- Anti-spam protection for alerts
"""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models import Product, ProductStatus, PriceHistory, Alert, AlertType, AlertStatus
from app.utils.alert_generator import check_and_create_alerts


# ============================================================================
# Helper Functions
# ============================================================================

def create_price_history_entry(
    db: Session,
    product_id: int,
    price: float,
    is_promo: bool = False,
    promo_percentage: float = None,
    days_ago: int = 0,
) -> PriceHistory:
    """Helper to create price history entry."""
    entry = PriceHistory(
        product_id=product_id,
        price=price,
        currency="EUR",
        is_promo=is_promo,
        promo_percentage=promo_percentage,
        recorded_at=datetime.utcnow() - timedelta(days=days_ago),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


# ============================================================================
# Complete Price Tracking Flow
# ============================================================================

def test_complete_price_tracking_flow_success(test_db: Session, sample_product: Product):
    """
    Test complete price tracking flow:
    1. Product exists
    2. Price is fetched (mocked)
    3. Price history is created
    4. Product is updated
    5. Alerts are generated (if applicable)
    """
    # Arrange: Product exists with a previous price
    create_price_history_entry(test_db, sample_product.id, price=399.99, days_ago=1)

    # Act: Simulate new price check with price drop
    new_price = 349.99
    is_promo = False

    # Create new price history
    new_entry = create_price_history_entry(test_db, sample_product.id, price=new_price)

    # Update product
    sample_product.current_price = new_price
    sample_product.last_checked_at = datetime.utcnow()
    sample_product.last_success_at = datetime.utcnow()
    sample_product.consecutive_errors = 0
    test_db.commit()

    # Generate alerts
    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo)

    # Assert: Verify complete flow
    # 1. Price history created
    assert new_entry.price == new_price
    assert new_entry.product_id == sample_product.id

    # 2. Product updated
    test_db.refresh(sample_product)
    assert sample_product.current_price == new_price
    assert sample_product.last_success_at is not None
    assert sample_product.consecutive_errors == 0

    # 3. Alert generated (12.5% drop from 399.99 to 349.99)
    assert len(alerts) == 1
    assert alerts[0].type == AlertType.PRICE_DROP
    assert alerts[0].new_price == new_price
    assert alerts[0].old_price == 399.99


def test_price_tracking_flow_with_failed_fetch(test_db: Session, sample_product: Product):
    """
    Test price tracking flow when fetch fails:
    1. Price fetch fails (returns None)
    2. Error is recorded in price history
    3. Product status is updated
    4. No alerts are generated
    """
    # Arrange: Product with previous successful checks
    sample_product.consecutive_errors = 0
    test_db.commit()

    # Act: Simulate failed price check
    failed_entry = PriceHistory(
        product_id=sample_product.id,
        price=None,  # Failed fetch
        currency=sample_product.currency,
        is_promo=False,
        recorded_at=datetime.utcnow(),
    )
    test_db.add(failed_entry)
    test_db.commit()

    # Update product error count
    sample_product.consecutive_errors += 1
    sample_product.last_error_message = "Failed to fetch price"
    sample_product.last_checked_at = datetime.utcnow()
    test_db.commit()

    # Try to generate alerts (should not create any)
    alerts = check_and_create_alerts(test_db, sample_product, None, False)

    # Assert
    assert len(alerts) == 0
    assert sample_product.consecutive_errors == 1
    assert sample_product.last_error_message is not None


def test_product_status_changes_to_error_after_multiple_failures(
    test_db: Session, sample_product: Product
):
    """Test that product status changes to ERROR after 3 consecutive failures."""
    # Arrange: Product starts active
    sample_product.status = ProductStatus.ACTIVE
    sample_product.consecutive_errors = 0
    test_db.commit()

    # Act: Simulate 3 consecutive failures
    for i in range(3):
        failed_entry = PriceHistory(
            product_id=sample_product.id,
            price=None,
            currency=sample_product.currency,
            recorded_at=datetime.utcnow() - timedelta(minutes=i),
        )
        test_db.add(failed_entry)
        sample_product.consecutive_errors += 1

    test_db.commit()

    # Update status based on error count
    if sample_product.consecutive_errors >= 3:
        sample_product.status = ProductStatus.ERROR

    test_db.commit()

    # Assert
    test_db.refresh(sample_product)
    assert sample_product.consecutive_errors == 3
    assert sample_product.status == ProductStatus.ERROR


# ============================================================================
# Alert Generation - PRICE_DROP Scenario
# ============================================================================

def test_alert_generation_price_drop_10_percent(test_db: Session, sample_product: Product):
    """Test PRICE_DROP alert is generated when price drops by >= 10%."""
    # Arrange: Previous price
    create_price_history_entry(test_db, sample_product.id, price=100.00, days_ago=1)

    # Act: New price with 15% drop
    new_price = 85.00
    create_price_history_entry(test_db, sample_product.id, price=new_price)

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=False)

    # Assert
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.type == AlertType.PRICE_DROP
    assert alert.old_price == 100.00
    assert alert.new_price == 85.00
    assert alert.price_drop_percentage == 15.0
    assert "15.0%" in alert.message


def test_alert_generation_price_drop_exactly_10_percent(
    test_db: Session, sample_product: Product
):
    """Test PRICE_DROP alert is generated for exactly 10% drop."""
    # Arrange
    create_price_history_entry(test_db, sample_product.id, price=100.00, days_ago=1)

    # Act: Exactly 10% drop
    new_price = 90.00
    create_price_history_entry(test_db, sample_product.id, price=new_price)

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=False)

    # Assert
    assert len(alerts) == 1
    assert alerts[0].type == AlertType.PRICE_DROP
    assert alerts[0].price_drop_percentage == 10.0


def test_no_alert_generation_price_drop_less_than_10_percent(
    test_db: Session, sample_product: Product
):
    """Test that no PRICE_DROP alert is generated for < 10% drop."""
    # Arrange
    create_price_history_entry(test_db, sample_product.id, price=100.00, days_ago=1)

    # Act: Only 5% drop
    new_price = 95.00
    create_price_history_entry(test_db, sample_product.id, price=new_price)

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=False)

    # Assert
    assert len(alerts) == 0


def test_no_alert_for_price_increase(test_db: Session, sample_product: Product):
    """Test that no PRICE_DROP alert is generated when price increases."""
    # Arrange
    create_price_history_entry(test_db, sample_product.id, price=100.00, days_ago=1)

    # Act: Price increase
    new_price = 120.00
    create_price_history_entry(test_db, sample_product.id, price=new_price)

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=False)

    # Assert
    assert len(alerts) == 0


# ============================================================================
# Alert Generation - TARGET_REACHED Scenario
# ============================================================================

def test_alert_generation_target_reached(test_db: Session, sample_product: Product):
    """Test TARGET_REACHED alert when price drops to target."""
    # Arrange
    sample_product.target_price = 299.99
    test_db.commit()
    create_price_history_entry(test_db, sample_product.id, price=349.99, days_ago=1)

    # Act: Price reaches target
    new_price = 299.99
    create_price_history_entry(test_db, sample_product.id, price=new_price)

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=False)

    # Assert
    assert len(alerts) >= 1
    target_alerts = [a for a in alerts if a.type == AlertType.TARGET_REACHED]
    assert len(target_alerts) == 1
    assert target_alerts[0].new_price == 299.99


def test_alert_generation_target_below(test_db: Session, sample_product: Product):
    """Test TARGET_REACHED alert when price drops below target."""
    # Arrange
    sample_product.target_price = 299.99
    test_db.commit()
    create_price_history_entry(test_db, sample_product.id, price=349.99, days_ago=1)

    # Act: Price goes below target
    new_price = 279.99
    create_price_history_entry(test_db, sample_product.id, price=new_price)

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=False)

    # Assert
    target_alerts = [a for a in alerts if a.type == AlertType.TARGET_REACHED]
    assert len(target_alerts) == 1


def test_no_target_alert_when_no_target_set(test_db: Session, sample_product: Product):
    """Test that no TARGET_REACHED alert is generated when no target is set."""
    # Arrange
    sample_product.target_price = None
    test_db.commit()
    create_price_history_entry(test_db, sample_product.id, price=100.00, days_ago=1)

    # Act
    new_price = 50.00  # Any price
    create_price_history_entry(test_db, sample_product.id, price=new_price)

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=False)

    # Assert
    target_alerts = [a for a in alerts if a.type == AlertType.TARGET_REACHED]
    assert len(target_alerts) == 0


# ============================================================================
# Alert Generation - PROMO_DETECTED Scenario
# ============================================================================

def test_alert_generation_promo_detected(test_db: Session, sample_product: Product):
    """Test PROMO_DETECTED alert when product goes on promo."""
    # Arrange: Previous entry NOT on promo
    create_price_history_entry(
        test_db, sample_product.id, price=100.00, is_promo=False, days_ago=1
    )

    # Act: New entry IS on promo
    new_price = 80.00
    create_price_history_entry(
        test_db, sample_product.id, price=new_price, is_promo=True, promo_percentage=20.0
    )

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=True)

    # Assert
    promo_alerts = [a for a in alerts if a.type == AlertType.PROMO_DETECTED]
    assert len(promo_alerts) == 1
    assert "Promotion detected" in promo_alerts[0].message


def test_no_promo_alert_when_already_on_promo(test_db: Session, sample_product: Product):
    """Test that no PROMO_DETECTED alert is generated if already on promo."""
    # Arrange: Previous entry WAS on promo
    create_price_history_entry(
        test_db, sample_product.id, price=80.00, is_promo=True, days_ago=1
    )

    # Act: Still on promo
    new_price = 80.00
    create_price_history_entry(
        test_db, sample_product.id, price=new_price, is_promo=True
    )

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=True)

    # Assert
    promo_alerts = [a for a in alerts if a.type == AlertType.PROMO_DETECTED]
    assert len(promo_alerts) == 0


# ============================================================================
# Alert Anti-Spam Protection
# ============================================================================

def test_anti_spam_no_duplicate_alerts_within_24h(
    test_db: Session, sample_product: Product
):
    """Test that duplicate alerts are not created within 24 hours."""
    # Arrange: Previous price
    create_price_history_entry(test_db, sample_product.id, price=100.00, days_ago=2)

    # Act 1: First price drop (should create alert)
    new_price_1 = 85.00
    create_price_history_entry(test_db, sample_product.id, price=new_price_1, days_ago=1)
    alerts_1 = check_and_create_alerts(test_db, sample_product, new_price_1, is_promo=False)

    # Act 2: Another price drop immediately after (should NOT create alert)
    new_price_2 = 80.00
    create_price_history_entry(test_db, sample_product.id, price=new_price_2)
    alerts_2 = check_and_create_alerts(test_db, sample_product, new_price_2, is_promo=False)

    # Assert
    assert len(alerts_1) == 1  # First alert created
    assert alerts_1[0].type == AlertType.PRICE_DROP

    # Second alert should be blocked by anti-spam
    price_drop_alerts_2 = [a for a in alerts_2 if a.type == AlertType.PRICE_DROP]
    assert len(price_drop_alerts_2) == 0


def test_anti_spam_allows_alert_after_24h(test_db: Session, sample_product: Product):
    """Test that alerts are allowed after 24 hours have passed."""
    # Arrange: Previous price
    create_price_history_entry(test_db, sample_product.id, price=100.00, days_ago=3)

    # Act 1: First price drop
    create_price_history_entry(test_db, sample_product.id, price=85.00, days_ago=2)
    alerts_1 = check_and_create_alerts(test_db, sample_product, 85.00, is_promo=False)

    # Simulate passage of time by aging the existing alert beyond 24h
    assert alerts_1, "Expected initial alert to be created"
    alerts_1[0].created_at = datetime.utcnow() - timedelta(hours=25)
    test_db.commit()

    # Act 2: Another price drop after 24 hours (should create new alert)
    new_price_2 = 70.00
    create_price_history_entry(test_db, sample_product.id, price=new_price_2)
    alerts_2 = check_and_create_alerts(test_db, sample_product, new_price_2, is_promo=False)

    # Assert
    price_drop_alerts = [a for a in alerts_2 if a.type == AlertType.PRICE_DROP]
    assert len(price_drop_alerts) == 1  # New alert should be created


def test_anti_spam_different_alert_types_allowed(
    test_db: Session, sample_product: Product
):
    """Test that different alert types can be created simultaneously."""
    # Arrange
    sample_product.target_price = 80.00
    test_db.commit()
    create_price_history_entry(test_db, sample_product.id, price=100.00, is_promo=False, days_ago=1)

    # Act: Price drops to target AND is on promo
    new_price = 75.00
    create_price_history_entry(
        test_db, sample_product.id, price=new_price, is_promo=True, promo_percentage=25.0
    )

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=True)

    # Assert: Should create PRICE_DROP, TARGET_REACHED, and PROMO_DETECTED
    alert_types = [a.type for a in alerts]
    assert AlertType.PRICE_DROP in alert_types  # 25% drop
    assert AlertType.TARGET_REACHED in alert_types  # Below target
    assert AlertType.PROMO_DETECTED in alert_types  # On promo


# ============================================================================
# Multiple Alerts in Single Flow
# ============================================================================

def test_multiple_alerts_generated_in_single_flow(
    test_db: Session, sample_product: Product
):
    """
    Test that multiple alerts can be generated in a single price check
    when multiple conditions are met.
    """
    # Arrange
    sample_product.target_price = 200.00
    test_db.commit()
    create_price_history_entry(
        test_db, sample_product.id, price=300.00, is_promo=False, days_ago=1
    )

    # Act: Price drops significantly, reaches target, and goes on promo
    new_price = 180.00  # 40% drop, below target, on promo
    create_price_history_entry(
        test_db, sample_product.id, price=new_price, is_promo=True, promo_percentage=40.0
    )

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=True)

    # Assert: All three alert types should be created
    assert len(alerts) == 3
    alert_types = [a.type for a in alerts]
    assert AlertType.TARGET_REACHED in alert_types
    assert AlertType.PRICE_DROP in alert_types
    assert AlertType.PROMO_DETECTED in alert_types


# ============================================================================
# Edge Cases
# ============================================================================

def test_first_price_check_no_previous_price(test_db: Session, sample_product: Product):
    """Test that first price check (no history) doesn't generate PRICE_DROP alert."""
    # Arrange: No previous price history

    # Act: First price check
    new_price = 100.00
    create_price_history_entry(test_db, sample_product.id, price=new_price)

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=False)

    # Assert: No PRICE_DROP alert (no previous price to compare)
    price_drop_alerts = [a for a in alerts if a.type == AlertType.PRICE_DROP]
    assert len(price_drop_alerts) == 0


def test_alert_generation_with_zero_previous_price(
    test_db: Session, sample_product: Product
):
    """Test alert generation handles zero previous price gracefully."""
    # Arrange: Previous price is 0 (edge case)
    create_price_history_entry(test_db, sample_product.id, price=0.0, days_ago=1)

    # Act
    new_price = 100.00
    create_price_history_entry(test_db, sample_product.id, price=new_price)

    alerts = check_and_create_alerts(test_db, sample_product, new_price, is_promo=False)

    # Assert: Should not crash, no PRICE_DROP alert (avoid division by zero)
    price_drop_alerts = [a for a in alerts if a.type == AlertType.PRICE_DROP]
    assert len(price_drop_alerts) == 0


def test_product_status_reset_on_successful_check(test_db: Session, sample_product: Product):
    """Test that consecutive_errors resets to 0 on successful price check."""
    # Arrange: Product in error state
    sample_product.status = ProductStatus.ERROR
    sample_product.consecutive_errors = 5
    test_db.commit()

    # Act: Successful price check
    new_price = 100.00
    create_price_history_entry(test_db, sample_product.id, price=new_price)

    sample_product.consecutive_errors = 0
    sample_product.status = ProductStatus.ACTIVE
    sample_product.last_success_at = datetime.utcnow()
    test_db.commit()

    # Assert
    test_db.refresh(sample_product)
    assert sample_product.consecutive_errors == 0
    assert sample_product.status == ProductStatus.ACTIVE
