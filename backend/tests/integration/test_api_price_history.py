"""
Integration tests for Price History API endpoints.

Tests price history retrieval, statistics, and chart data with real database.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models import Product, PriceHistory


# ============================================================================
# GET /api/v1/products/{id}/price-history - Get Price History
# ============================================================================

def test_get_price_history_all_period(
    client: TestClient, product_with_price_history: Product
):
    """Test retrieving all price history for a product."""
    response = client.get(
        f"/api/v1/products/{product_with_price_history.id}/price-history?period=all"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 100  # We created 100 entries
    assert all("price" in entry for entry in data)
    assert all("recorded_at" in entry for entry in data)
    # Should be ordered by most recent first
    dates = [datetime.fromisoformat(entry["recorded_at"].replace("Z", "")) for entry in data]
    assert dates == sorted(dates, reverse=True)


def test_get_price_history_7d_period(
    client: TestClient, product_with_price_history: Product
):
    """Test retrieving 7-day price history."""
    response = client.get(
        f"/api/v1/products/{product_with_price_history.id}/price-history?period=7d"
    )

    assert response.status_code == 200
    data = response.json()
    # Should only include entries from last 7 days
    assert len(data) <= 7
    # Verify all dates are within last 7 days
    cutoff = datetime.utcnow() - timedelta(days=7)
    for entry in data:
        recorded_at = datetime.fromisoformat(entry["recorded_at"].replace("Z", ""))
        assert recorded_at >= cutoff


def test_get_price_history_30d_period(
    client: TestClient, product_with_price_history: Product
):
    """Test retrieving 30-day price history."""
    response = client.get(
        f"/api/v1/products/{product_with_price_history.id}/price-history?period=30d"
    )

    assert response.status_code == 200
    data = response.json()
    # Should include entries from last 30 days
    assert len(data) <= 30
    cutoff = datetime.utcnow() - timedelta(days=30)
    for entry in data:
        recorded_at = datetime.fromisoformat(entry["recorded_at"].replace("Z", ""))
        assert recorded_at >= cutoff


def test_get_price_history_90d_period(
    client: TestClient, product_with_price_history: Product
):
    """Test retrieving 90-day price history."""
    response = client.get(
        f"/api/v1/products/{product_with_price_history.id}/price-history?period=90d"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 90


def test_get_price_history_empty(client: TestClient, sample_product: Product):
    """Test retrieving price history for product with no history."""
    response = client.get(f"/api/v1/products/{sample_product.id}/price-history")

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_price_history_product_not_found(client: TestClient, test_db: Session):
    """Test retrieving price history for non-existent product."""
    response = client.get("/api/v1/products/99999/price-history")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


# ============================================================================
# GET /api/v1/products/{id}/price-history/stats - Price Statistics
# ============================================================================

def test_get_price_statistics_with_history(
    client: TestClient, product_with_price_history: Product
):
    """Test retrieving price statistics for product with history."""
    response = client.get(
        f"/api/v1/products/{product_with_price_history.id}/price-history/stats"
    )

    assert response.status_code == 200
    data = response.json()

    # Verify all statistics fields are present
    assert "current_price" in data
    assert "lowest_price" in data
    assert "highest_price" in data
    assert "average_price" in data
    assert "price_change_percentage" in data
    assert "last_updated" in data
    assert "total_checks" in data

    # Verify statistics make sense
    assert data["total_checks"] == 100
    assert data["lowest_price"] <= data["highest_price"]
    assert data["current_price"] is not None
    assert data["average_price"] is not None


def test_get_price_statistics_empty_history(
    client: TestClient, sample_product: Product
):
    """Test statistics for product with no price history."""
    response = client.get(f"/api/v1/products/{sample_product.id}/price-history/stats")

    assert response.status_code == 200
    data = response.json()

    # Statistics should be None/0 for empty history
    assert data["current_price"] is None
    assert data["lowest_price"] is None
    assert data["highest_price"] is None
    assert data["average_price"] is None
    assert data["price_change_percentage"] is None
    assert data["total_checks"] == 0


def test_get_price_statistics_product_not_found(client: TestClient, test_db: Session):
    """Test statistics for non-existent product."""
    response = client.get("/api/v1/products/99999/price-history/stats")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_get_price_statistics_single_entry(client: TestClient, test_db: Session):
    """Test statistics with only one price entry."""
    # Create product with single price entry
    product = Product(
        name="Single Entry Product",
        url="https://www.test.com/single",
        domain="test.com",
        current_price=100.00,
        currency="EUR",
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    # Add single price history entry
    entry = PriceHistory(
        product_id=product.id,
        price=100.00,
        currency="EUR",
        is_promo=False,
        recorded_at=datetime.utcnow(),
    )
    test_db.add(entry)
    test_db.commit()

    response = client.get(f"/api/v1/products/{product.id}/price-history/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["current_price"] == 100.00
    assert data["lowest_price"] == 100.00
    assert data["highest_price"] == 100.00
    assert data["average_price"] == 100.00
    assert data["price_change_percentage"] == 0.0  # No change
    assert data["total_checks"] == 1


# ============================================================================
# GET /api/v1/products/{id}/price-history/chart - Chart Data
# ============================================================================

def test_get_price_chart_data_all_period(
    client: TestClient, product_with_price_history: Product
):
    """Test retrieving chart data for all periods."""
    response = client.get(
        f"/api/v1/products/{product_with_price_history.id}/price-history/chart?period=all"
    )

    assert response.status_code == 200
    data = response.json()

    # Verify chart data structure
    assert "labels" in data
    assert "prices" in data
    assert "promos" in data

    # All arrays should have same length
    assert len(data["labels"]) == len(data["prices"])
    assert len(data["labels"]) == len(data["promos"])
    assert len(data["labels"]) == 100

    # Labels should be ISO timestamps
    for label in data["labels"]:
        assert isinstance(label, str)
        # Should be parseable as datetime
        datetime.fromisoformat(label)

    # Prices should be numeric
    for price in data["prices"]:
        assert isinstance(price, (int, float))

    # Promos should be boolean
    for promo in data["promos"]:
        assert isinstance(promo, bool)


def test_get_price_chart_data_7d_period(
    client: TestClient, product_with_price_history: Product
):
    """Test retrieving chart data for 7-day period."""
    response = client.get(
        f"/api/v1/products/{product_with_price_history.id}/price-history/chart?period=7d"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["labels"]) <= 7


def test_get_price_chart_data_empty_history(client: TestClient, sample_product: Product):
    """Test chart data for product with no history."""
    response = client.get(f"/api/v1/products/{sample_product.id}/price-history/chart")

    assert response.status_code == 200
    data = response.json()
    assert data["labels"] == []
    assert data["prices"] == []
    assert data["promos"] == []


def test_get_price_chart_data_product_not_found(client: TestClient, test_db: Session):
    """Test chart data for non-existent product."""
    response = client.get("/api/v1/products/99999/price-history/chart")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_get_price_chart_data_chronological_order(
    client: TestClient, product_with_price_history: Product
):
    """Test that chart data is in chronological order (oldest to newest)."""
    response = client.get(
        f"/api/v1/products/{product_with_price_history.id}/price-history/chart"
    )

    assert response.status_code == 200
    data = response.json()

    # Parse timestamps and verify chronological order
    timestamps = [datetime.fromisoformat(label) for label in data["labels"]]
    assert timestamps == sorted(timestamps)  # Should be ascending


# ============================================================================
# Integration with Product Creation
# ============================================================================

def test_price_history_after_product_creation(client: TestClient, test_db: Session):
    """Test that new products start with empty price history."""
    # Create product
    payload = {
        "name": "New Product",
        "url": "https://www.test.com/new",
    }
    create_response = client.post("/api/v1/products/", json=payload)
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]

    # Check price history
    history_response = client.get(f"/api/v1/products/{product_id}/price-history")
    assert history_response.status_code == 200
    assert history_response.json() == []


# ============================================================================
# Edge Cases
# ============================================================================

def test_get_price_history_with_null_prices(client: TestClient, test_db: Session):
    """Test price history includes entries with null prices (failed checks)."""
    # Create product
    product = Product(
        name="Product with Failed Checks",
        url="https://www.test.com/failed",
        domain="test.com",
        currency="EUR",
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    # Add entry with null price (failed check)
    entry = PriceHistory(
        product_id=product.id,
        price=None,  # Failed check
        currency="EUR",
        is_promo=False,
        recorded_at=datetime.utcnow(),
    )
    test_db.add(entry)
    test_db.commit()

    response = client.get(f"/api/v1/products/{product.id}/price-history")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["price"] is None


def test_price_statistics_excludes_null_prices(client: TestClient, test_db: Session):
    """Test that price statistics exclude null prices from calculations."""
    # Create product
    product = Product(
        name="Product with Mixed Results",
        url="https://www.test.com/mixed",
        domain="test.com",
        currency="EUR",
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    # Add successful price check
    test_db.add(
        PriceHistory(
            product_id=product.id,
            price=100.00,
            currency="EUR",
            recorded_at=datetime.utcnow(),
        )
    )

    # Add failed check
    test_db.add(
        PriceHistory(
            product_id=product.id,
            price=None,
            currency="EUR",
            recorded_at=datetime.utcnow() - timedelta(hours=1),
        )
    )

    test_db.commit()

    response = client.get(f"/api/v1/products/{product.id}/price-history/stats")

    assert response.status_code == 200
    data = response.json()
    # Only 1 successful price check should be counted
    assert data["total_checks"] == 1
    assert data["current_price"] == 100.00
