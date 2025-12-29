"""
Unit tests for promotional detection utilities.

Tests price drop calculations, promo status checks, and promo history retrieval.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.utils.promo_detector import (
    calculate_price_drop_percentage,
    is_significant_drop,
    get_current_promo_status,
    get_promo_history,
)
from app.models import Product, ProductStatus, PriceHistory


# ============================================================================
# Price Drop Percentage Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestCalculatePriceDropPercentage:
    """Test calculate_price_drop_percentage function."""

    @pytest.mark.parametrize("old_price,new_price,expected", [
        (100.0, 85.0, 15.0),
        (100.0, 50.0, 50.0),
        (100.0, 75.0, 25.0),
        (200.0, 150.0, 25.0),
        (99.99, 79.99, 20.0),
        (149.99, 99.99, 33.34),
        (50.0, 45.0, 10.0),
    ])
    def test_price_drop_percentage_valid(self, old_price, new_price, expected):
        """Test price drop percentage calculation with valid prices."""
        result = calculate_price_drop_percentage(old_price, new_price)
        assert result == pytest.approx(expected, rel=0.01)

    @pytest.mark.parametrize("old_price,new_price", [
        (None, 100.0),
        (100.0, None),
        (None, None),
    ])
    def test_price_drop_percentage_none_values(self, old_price, new_price):
        """Test price drop percentage with None values."""
        result = calculate_price_drop_percentage(old_price, new_price)
        assert result is None

    def test_price_drop_percentage_zero_old_price(self):
        """Test price drop percentage with zero old price."""
        result = calculate_price_drop_percentage(0, 100.0)
        assert result is None

    def test_price_drop_percentage_price_increase(self):
        """Test price drop percentage when price increased (negative drop)."""
        result = calculate_price_drop_percentage(100.0, 150.0)
        assert result == -50.0  # Returns negative percentage

    def test_price_drop_percentage_same_price(self):
        """Test price drop percentage when prices are the same."""
        result = calculate_price_drop_percentage(100.0, 100.0)
        assert result == 0.0

    def test_price_drop_percentage_rounding(self):
        """Test that result is rounded to 2 decimal places."""
        result = calculate_price_drop_percentage(99.99, 66.66)
        # Actual calculation: (99.99-66.66)/99.99 * 100 = 33.33333...
        assert result == pytest.approx(33.33, rel=0.01)
        # Verify it's rounded to 2 decimals
        assert len(str(result).split('.')[-1]) <= 2


# ============================================================================
# Significant Drop Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestIsSignificantDrop:
    """Test is_significant_drop function."""

    @pytest.mark.parametrize("old_price,new_price,threshold,expected", [
        (100.0, 85.0, 10.0, True),   # 15% drop >= 10% threshold
        (100.0, 50.0, 10.0, True),   # 50% drop >= 10% threshold
        (100.0, 95.0, 10.0, False),  # 5% drop < 10% threshold
        (100.0, 75.0, 30.0, False),  # 25% drop < 30% threshold
        (100.0, 70.0, 30.0, True),   # 30% drop >= 30% threshold
        (200.0, 180.0, 10.0, True),  # 10% drop >= 10% threshold
        (200.0, 181.0, 10.0, False), # 9.5% drop < 10% threshold
    ])
    def test_is_significant_drop_various_thresholds(self, old_price, new_price, threshold, expected):
        """Test significant drop detection with various thresholds."""
        result = is_significant_drop(old_price, new_price, threshold)
        assert result == expected

    def test_is_significant_drop_default_threshold(self):
        """Test significant drop with default 10% threshold."""
        # 15% drop should be significant
        assert is_significant_drop(100.0, 85.0) is True

        # 5% drop should not be significant
        assert is_significant_drop(100.0, 95.0) is False

    @pytest.mark.parametrize("old_price,new_price", [
        (None, 100.0),
        (100.0, None),
        (None, None),
    ])
    def test_is_significant_drop_none_values(self, old_price, new_price):
        """Test significant drop with None values."""
        result = is_significant_drop(old_price, new_price)
        assert result is False

    def test_is_significant_drop_price_increase(self):
        """Test significant drop when price increased."""
        result = is_significant_drop(100.0, 150.0, 10.0)
        assert result is False

    def test_is_significant_drop_zero_old_price(self):
        """Test significant drop with zero old price."""
        result = is_significant_drop(0, 100.0)
        assert result is False


# ============================================================================
# Current Promo Status Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestGetCurrentPromoStatus:
    """Test get_current_promo_status function."""

    def test_get_current_promo_status_with_promo(self, test_db: Session, sample_promo_product: Product):
        """Test getting promo status for product on promotion."""
        result = get_current_promo_status(test_db, sample_promo_product.id)

        assert result is not None
        assert result['is_promo'] is True
        assert result['promo_percentage'] == 20.0
        assert result['current_price'] == 79.99
        assert result['currency'] == "EUR"
        assert result['last_checked'] is not None

    def test_get_current_promo_status_without_promo(self, test_db: Session, sample_product: Product):
        """Test getting promo status for product not on promotion."""
        # Add price history without promo
        history = PriceHistory(
            product_id=sample_product.id,
            price=349.99,
            currency="EUR",
            is_promo=False,
            recorded_at=datetime.utcnow(),
        )
        test_db.add(history)
        test_db.commit()

        result = get_current_promo_status(test_db, sample_product.id)

        assert result is not None
        assert result['is_promo'] is False
        assert result['promo_percentage'] is None
        assert result['current_price'] == 349.99

    def test_get_current_promo_status_no_history(self, test_db: Session, sample_product: Product):
        """Test getting promo status for product with no price history."""
        result = get_current_promo_status(test_db, sample_product.id)
        assert result is None

    def test_get_current_promo_status_nonexistent_product(self, test_db: Session):
        """Test getting promo status for non-existent product."""
        result = get_current_promo_status(test_db, 99999)
        assert result is None

    def test_get_current_promo_status_latest_entry(self, test_db: Session, sample_product_with_history: Product):
        """Test that only the latest price entry is returned."""
        result = get_current_promo_status(test_db, sample_product_with_history.id)

        assert result is not None
        # Should return the most recent price (99.99)
        assert result['current_price'] == 99.99


# ============================================================================
# Promo History Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestGetPromoHistory:
    """Test get_promo_history function."""

    def test_get_promo_history_with_promos(self, test_db: Session):
        """Test getting promo history for product with promotional periods."""
        # Create product
        product = Product(
            name="Test Product",
            url="https://www.amazon.fr/test",
            domain="amazon.fr",
            current_price=99.99,
            currency="EUR",
            status=ProductStatus.ACTIVE,
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)

        now = datetime.utcnow()

        # Add promo period (3 days ago to 1 day ago)
        promo_entries = [
            PriceHistory(
                product_id=product.id,
                price=79.99,
                currency="EUR",
                is_promo=True,
                promo_percentage=20.0,
                recorded_at=now - timedelta(days=3),
            ),
            PriceHistory(
                product_id=product.id,
                price=75.99,
                currency="EUR",
                is_promo=True,
                promo_percentage=25.0,
                recorded_at=now - timedelta(days=2),
            ),
            PriceHistory(
                product_id=product.id,
                price=77.99,
                currency="EUR",
                is_promo=True,
                promo_percentage=22.0,
                recorded_at=now - timedelta(days=1),
            ),
        ]

        for entry in promo_entries:
            test_db.add(entry)
        test_db.commit()

        # Get promo history
        result = get_promo_history(test_db, product.id, days=30)

        assert len(result) == 1
        assert result[0]['min_price'] == 75.99
        assert result[0]['max_price'] == 79.99
        assert result[0]['promo_percentage'] == 22.0  # Latest percentage
        assert result[0]['duration_days'] >= 2

    def test_get_promo_history_no_promos(self, test_db: Session, sample_product_with_history: Product):
        """Test getting promo history for product with no promos."""
        result = get_promo_history(test_db, sample_product_with_history.id, days=30)
        assert result == []

    def test_get_promo_history_no_price_history(self, test_db: Session, sample_product: Product):
        """Test getting promo history for product with no price history."""
        result = get_promo_history(test_db, sample_product.id, days=30)
        assert result == []

    def test_get_promo_history_multiple_periods(self, test_db: Session):
        """Test getting promo history with multiple separate promo periods."""
        # Create product
        product = Product(
            name="Test Product",
            url="https://www.amazon.fr/test",
            domain="amazon.fr",
            current_price=99.99,
            currency="EUR",
            status=ProductStatus.ACTIVE,
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)

        now = datetime.utcnow()

        # First promo period (20 days ago)
        test_db.add(PriceHistory(
            product_id=product.id,
            price=79.99,
            currency="EUR",
            is_promo=True,
            promo_percentage=20.0,
            recorded_at=now - timedelta(days=20),
        ))

        # Regular price (15 days ago)
        test_db.add(PriceHistory(
            product_id=product.id,
            price=99.99,
            currency="EUR",
            is_promo=False,
            recorded_at=now - timedelta(days=15),
        ))

        # Second promo period (5 days ago)
        test_db.add(PriceHistory(
            product_id=product.id,
            price=74.99,
            currency="EUR",
            is_promo=True,
            promo_percentage=25.0,
            recorded_at=now - timedelta(days=5),
        ))

        test_db.commit()

        # Get promo history
        result = get_promo_history(test_db, product.id, days=30)

        assert len(result) == 2
        assert result[0]['min_price'] == 79.99
        assert result[1]['min_price'] == 74.99

    def test_get_promo_history_ongoing_promo(self, test_db: Session, sample_promo_product: Product):
        """Test getting promo history with ongoing promotion."""
        result = get_promo_history(test_db, sample_promo_product.id, days=30)

        assert len(result) == 1
        assert result[0]['promo_percentage'] == 20.0
        assert result[0]['min_price'] == 79.99
        # Ongoing promo might have end_date as None or as the latest recorded date
        assert result[0]['start_date'] is not None

    def test_get_promo_history_time_range(self, test_db: Session):
        """Test promo history respects time range parameter."""
        product = Product(
            name="Test Product",
            url="https://www.amazon.fr/test",
            domain="amazon.fr",
            current_price=99.99,
            currency="EUR",
            status=ProductStatus.ACTIVE,
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)

        now = datetime.utcnow()

        # Old promo (60 days ago) - should not be included
        test_db.add(PriceHistory(
            product_id=product.id,
            price=79.99,
            currency="EUR",
            is_promo=True,
            promo_percentage=20.0,
            recorded_at=now - timedelta(days=60),
        ))

        # Recent promo (10 days ago) - should be included
        test_db.add(PriceHistory(
            product_id=product.id,
            price=74.99,
            currency="EUR",
            is_promo=True,
            promo_percentage=25.0,
            recorded_at=now - timedelta(days=10),
        ))

        test_db.commit()

        # Get promo history for last 30 days
        result = get_promo_history(test_db, product.id, days=30)

        assert len(result) == 1
        assert result[0]['min_price'] == 74.99

    def test_get_promo_history_average_price(self, test_db: Session):
        """Test that promo history calculates average price correctly."""
        product = Product(
            name="Test Product",
            url="https://www.amazon.fr/test",
            domain="amazon.fr",
            current_price=99.99,
            currency="EUR",
            status=ProductStatus.ACTIVE,
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)

        now = datetime.utcnow()

        # Promo with varying prices
        promo_prices = [80.0, 75.0, 85.0]  # Average: 80.0
        for i, price in enumerate(promo_prices):
            test_db.add(PriceHistory(
                product_id=product.id,
                price=price,
                currency="EUR",
                is_promo=True,
                promo_percentage=20.0,
                recorded_at=now - timedelta(days=3-i),
            ))

        test_db.commit()

        result = get_promo_history(test_db, product.id, days=30)

        assert len(result) == 1
        assert result[0]['average_price'] == 80.0
        assert result[0]['min_price'] == 75.0
        assert result[0]['max_price'] == 85.0


# ============================================================================
# Edge Cases Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestPromoDetectorEdgeCases:
    """Test edge cases for promo detector functions."""

    def test_calculate_price_drop_percentage_very_small_drop(self):
        """Test price drop calculation with very small percentage."""
        result = calculate_price_drop_percentage(100.0, 99.5)
        assert result == 0.5

    def test_calculate_price_drop_percentage_very_large_drop(self):
        """Test price drop calculation with very large percentage."""
        result = calculate_price_drop_percentage(1000.0, 10.0)
        assert result == 99.0

    def test_is_significant_drop_exact_threshold(self):
        """Test significant drop when drop equals threshold exactly."""
        result = is_significant_drop(100.0, 90.0, 10.0)
        assert result is True  # 10% drop >= 10% threshold

    def test_get_promo_history_single_day_promo(self, test_db: Session):
        """Test promo history with single-day promotion."""
        product = Product(
            name="Test Product",
            url="https://www.amazon.fr/test",
            domain="amazon.fr",
            current_price=99.99,
            currency="EUR",
            status=ProductStatus.ACTIVE,
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)

        # Single promo entry
        test_db.add(PriceHistory(
            product_id=product.id,
            price=79.99,
            currency="EUR",
            is_promo=True,
            promo_percentage=20.0,
            recorded_at=datetime.utcnow(),
        ))
        test_db.commit()

        result = get_promo_history(test_db, product.id, days=30)

        assert len(result) == 1
        assert result[0]['duration_days'] == 1  # Minimum 1 day
