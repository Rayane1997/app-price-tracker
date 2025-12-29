"""
Integration tests for Products API endpoints.

Tests all product-related endpoints with real HTTP requests and database transactions.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Product, ProductStatus


# ============================================================================
# GET /api/v1/products/ - List Products
# ============================================================================

def test_list_products_empty(client: TestClient, test_db: Session):
    """Test listing products when database is empty."""
    response = client.get("/api/v1/products/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["products"] == []
    assert data["page"] == 1
    assert data["total_pages"] == 1


def test_list_products_with_pagination(client: TestClient, multiple_products: list[Product]):
    """Test product listing with pagination."""
    response = client.get("/api/v1/products/?page=1&page_size=5")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert len(data["products"]) == 5
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert data["total_pages"] == 2


def test_list_products_page_2(client: TestClient, multiple_products: list[Product]):
    """Test retrieving second page of products."""
    response = client.get("/api/v1/products/?page=2&page_size=5")

    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) == 5
    assert data["page"] == 2


def test_list_products_filter_by_status(client: TestClient, multiple_products: list[Product]):
    """Test filtering products by status."""
    response = client.get("/api/v1/products/?status=active")

    assert response.status_code == 200
    data = response.json()
    # Every 3rd product is PAUSED, so 7 are ACTIVE out of 10
    assert data["total"] == 7
    for product in data["products"]:
        assert product["status"] == "active"


def test_list_products_filter_by_domain(client: TestClient, multiple_products: list[Product]):
    """Test filtering products by domain."""
    response = client.get("/api/v1/products/?domain=amazon.fr")

    assert response.status_code == 200
    data = response.json()
    # Even numbered products are amazon.fr
    assert data["total"] == 5
    for product in data["products"]:
        assert product["domain"] == "amazon.fr"


def test_list_products_sorting_asc(client: TestClient, multiple_products: list[Product]):
    """Test sorting products in ascending order."""
    response = client.get("/api/v1/products/?sort_by=current_price&sort_order=asc")

    assert response.status_code == 200
    data = response.json()
    prices = [p["current_price"] for p in data["products"]]
    assert prices == sorted(prices)


def test_list_products_sorting_desc(client: TestClient, multiple_products: list[Product]):
    """Test sorting products in descending order."""
    response = client.get("/api/v1/products/?sort_by=current_price&sort_order=desc")

    assert response.status_code == 200
    data = response.json()
    prices = [p["current_price"] for p in data["products"]]
    assert prices == sorted(prices, reverse=True)


# ============================================================================
# GET /api/v1/products/domains - List Domains
# ============================================================================

def test_list_domains_empty(client: TestClient, test_db: Session):
    """Test listing domains when no products exist."""
    response = client.get("/api/v1/products/domains")

    assert response.status_code == 200
    assert response.json() == []


def test_list_domains_with_products(client: TestClient, multiple_products: list[Product]):
    """Test listing unique domains from products."""
    response = client.get("/api/v1/products/domains")

    assert response.status_code == 200
    domains = response.json()
    assert len(domains) == 2
    assert "amazon.fr" in domains
    assert "fnac.com" in domains


# ============================================================================
# GET /api/v1/products/{id} - Get Single Product
# ============================================================================

def test_get_product_success(client: TestClient, sample_product: Product):
    """Test retrieving a single product by ID."""
    response = client.get(f"/api/v1/products/{sample_product.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_product.id
    assert data["name"] == sample_product.name
    assert data["url"] == sample_product.url
    assert data["domain"] == sample_product.domain
    assert data["current_price"] == sample_product.current_price
    assert data["currency"] == sample_product.currency


def test_get_product_not_found(client: TestClient, test_db: Session):
    """Test retrieving non-existent product returns 404."""
    response = client.get("/api/v1/products/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


# ============================================================================
# POST /api/v1/products/ - Create Product
# ============================================================================

def test_create_product_success(client: TestClient, test_db: Session):
    """Test creating a new product."""
    payload = {
        "name": "New Test Product",
        "url": "https://www.amazon.fr/dp/NEWTEST",
        "target_price": 99.99,
        "check_frequency_hours": 12,
        "tags": "new,test",
        "notes": "Test notes",
    }

    response = client.post("/api/v1/products/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["url"] == payload["url"]
    assert data["domain"] == "amazon.fr"  # Auto-extracted
    assert data["target_price"] == payload["target_price"]
    assert data["status"] == "active"  # Default status
    assert "id" in data

    # Verify in database
    product = test_db.query(Product).filter_by(id=data["id"]).first()
    assert product is not None
    assert product.name == payload["name"]


def test_create_product_minimal_data(client: TestClient, test_db: Session):
    """Test creating product with minimal required fields."""
    payload = {
        "name": "Minimal Product",
        "url": "https://www.fnac.com/minimal",
    }

    response = client.post("/api/v1/products/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["domain"] == "fnac.com"
    assert data["check_frequency_hours"] == 24  # Default


def test_create_product_invalid_data(client: TestClient, test_db: Session):
    """Test creating product with invalid data returns validation error."""
    payload = {
        "name": "",  # Empty name
        "url": "not-a-valid-url",
    }

    response = client.post("/api/v1/products/", json=payload)

    assert response.status_code == 422  # Validation error


def test_create_product_missing_required_fields(client: TestClient, test_db: Session):
    """Test creating product without required fields."""
    payload = {
        "name": "Missing URL",
    }

    response = client.post("/api/v1/products/", json=payload)

    assert response.status_code == 422


# ============================================================================
# PUT /api/v1/products/{id} - Update Product
# ============================================================================

def test_update_product_success(client: TestClient, sample_product: Product):
    """Test updating an existing product."""
    payload = {
        "name": "Updated Product Name",
        "target_price": 199.99,
        "status": "paused",
    }

    response = client.put(f"/api/v1/products/{sample_product.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_product.id
    assert data["name"] == payload["name"]
    assert data["target_price"] == payload["target_price"]
    assert data["status"] == "paused"
    # URL should remain unchanged
    assert data["url"] == sample_product.url


def test_update_product_url_updates_domain(client: TestClient, sample_product: Product):
    """Test that updating URL also updates domain."""
    payload = {
        "url": "https://www.fnac.com/newproduct",
    }

    response = client.put(f"/api/v1/products/{sample_product.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["url"] == payload["url"]
    assert data["domain"] == "fnac.com"  # Auto-updated


def test_update_product_not_found(client: TestClient, test_db: Session):
    """Test updating non-existent product returns 404."""
    payload = {"name": "Does not matter"}

    response = client.put("/api/v1/products/99999", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product_partial_update(client: TestClient, sample_product: Product):
    """Test partial update (only some fields)."""
    original_url = sample_product.url
    payload = {"notes": "Updated notes only"}

    response = client.put(f"/api/v1/products/{sample_product.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == "Updated notes only"
    assert data["url"] == original_url  # Unchanged


# ============================================================================
# DELETE /api/v1/products/{id} - Delete Product
# ============================================================================

def test_delete_product_success(client: TestClient, sample_product: Product, test_db: Session):
    """Test deleting an existing product."""
    product_id = sample_product.id

    response = client.delete(f"/api/v1/products/{product_id}")

    assert response.status_code == 204
    assert response.content == b""

    # Verify product is deleted from database
    product = test_db.query(Product).filter_by(id=product_id).first()
    assert product is None


def test_delete_product_not_found(client: TestClient, test_db: Session):
    """Test deleting non-existent product returns 404."""
    response = client.delete("/api/v1/products/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_delete_product_cascades_to_price_history(
    client: TestClient, product_with_price_history: Product, test_db: Session
):
    """Test that deleting product also deletes associated price history."""
    from app.models import PriceHistory

    product_id = product_with_price_history.id

    # Verify price history exists before deletion
    history_count = (
        test_db.query(PriceHistory).filter_by(product_id=product_id).count()
    )
    assert history_count > 0

    # Delete product
    response = client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == 204

    # Verify price history is also deleted (cascade)
    history_count_after = (
        test_db.query(PriceHistory).filter_by(product_id=product_id).count()
    )
    assert history_count_after == 0


def test_delete_product_cascades_to_alerts(
    client: TestClient, product_with_alerts: Product, test_db: Session
):
    """Test that deleting product also deletes associated alerts."""
    from app.models import Alert

    product_id = product_with_alerts.id

    # Verify alerts exist before deletion
    alert_count = test_db.query(Alert).filter_by(product_id=product_id).count()
    assert alert_count > 0

    # Delete product
    response = client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == 204

    # Verify alerts are also deleted (cascade)
    alert_count_after = test_db.query(Alert).filter_by(product_id=product_id).count()
    assert alert_count_after == 0


# ============================================================================
# Edge Cases and Validation
# ============================================================================

def test_list_products_invalid_page(client: TestClient, test_db: Session):
    """Test listing products with invalid page number."""
    response = client.get("/api/v1/products/?page=0")

    assert response.status_code == 422  # Validation error


def test_list_products_invalid_page_size(client: TestClient, test_db: Session):
    """Test listing products with invalid page size."""
    response = client.get("/api/v1/products/?page_size=200")

    assert response.status_code == 422  # Exceeds max


def test_list_products_invalid_sort_order(client: TestClient, test_db: Session):
    """Test listing products with invalid sort order."""
    response = client.get("/api/v1/products/?sort_order=invalid")

    assert response.status_code == 422
