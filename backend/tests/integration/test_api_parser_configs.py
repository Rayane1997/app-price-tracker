"""
Integration tests for Parser Configs API endpoints.

Tests parser configuration CRUD operations and validation with real database.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import ParserConfig


# ============================================================================
# GET /api/v1/parser-configs/ - List Parser Configs
# ============================================================================

def test_list_parser_configs_empty(client: TestClient, test_db: Session):
    """Test listing parser configs when database is empty."""
    response = client.get("/api/v1/parser-configs/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["configs"] == []
    assert data["page"] == 1
    assert data["total_pages"] == 1


def test_list_parser_configs_with_pagination(
    client: TestClient, multiple_parser_configs: list[ParserConfig]
):
    """Test parser config listing with pagination."""
    response = client.get("/api/v1/parser-configs/?page=1&page_size=3")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["configs"]) == 3
    assert data["page"] == 1
    assert data["page_size"] == 3
    assert data["total_pages"] == 2


def test_list_parser_configs_filter_active(
    client: TestClient, multiple_parser_configs: list[ParserConfig]
):
    """Test filtering parser configs by active status."""
    response = client.get("/api/v1/parser-configs/?is_active=true")

    assert response.status_code == 200
    data = response.json()
    # Even numbered configs are active
    assert data["total"] == 2
    for config in data["configs"]:
        assert config["is_active"] is True


def test_list_parser_configs_filter_inactive(
    client: TestClient, multiple_parser_configs: list[ParserConfig]
):
    """Test filtering parser configs by inactive status."""
    response = client.get("/api/v1/parser-configs/?is_active=false")

    assert response.status_code == 200
    data = response.json()
    # Odd numbered configs are inactive
    assert data["total"] == 3
    for config in data["configs"]:
        assert config["is_active"] is False


def test_list_parser_configs_sorting(
    client: TestClient, multiple_parser_configs: list[ParserConfig]
):
    """Test sorting parser configs."""
    response = client.get("/api/v1/parser-configs/?sort_by=domain&sort_order=asc")

    assert response.status_code == 200
    data = response.json()
    domains = [config["domain"] for config in data["configs"]]
    assert domains == sorted(domains)


# ============================================================================
# GET /api/v1/parser-configs/{id} - Get Single Parser Config
# ============================================================================

def test_get_parser_config_success(
    client: TestClient, sample_parser_config: ParserConfig
):
    """Test retrieving a single parser config by ID."""
    response = client.get(f"/api/v1/parser-configs/{sample_parser_config.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_parser_config.id
    assert data["domain"] == sample_parser_config.domain
    assert data["price_selectors"] == sample_parser_config.price_selectors
    assert data["name_selectors"] == sample_parser_config.name_selectors
    assert data["image_selectors"] == sample_parser_config.image_selectors
    assert data["use_playwright"] == sample_parser_config.use_playwright
    assert data["is_active"] == sample_parser_config.is_active


def test_get_parser_config_not_found(client: TestClient, test_db: Session):
    """Test retrieving non-existent parser config returns 404."""
    response = client.get("/api/v1/parser-configs/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Parser configuration not found"


# ============================================================================
# GET /api/v1/parser-configs/domain/{domain} - Get Config by Domain
# ============================================================================

def test_get_parser_config_by_domain_success(
    client: TestClient, sample_parser_config: ParserConfig
):
    """Test retrieving parser config by domain."""
    response = client.get(f"/api/v1/parser-configs/domain/{sample_parser_config.domain}")

    assert response.status_code == 200
    data = response.json()
    assert data["domain"] == sample_parser_config.domain
    assert data["id"] == sample_parser_config.id


def test_get_parser_config_by_domain_not_found(client: TestClient, test_db: Session):
    """Test retrieving parser config for non-existent domain returns 404."""
    response = client.get("/api/v1/parser-configs/domain/nonexistent.com")

    assert response.status_code == 404
    assert "Parser configuration not found" in response.json()["detail"]


def test_get_parser_config_by_domain_case_insensitive(
    client: TestClient, sample_parser_config: ParserConfig
):
    """Test domain lookup is case-insensitive."""
    # sample_parser_config has domain "test.com"
    response = client.get("/api/v1/parser-configs/domain/TEST.COM")

    assert response.status_code == 200
    data = response.json()
    assert data["domain"] == "test.com"  # Stored in lowercase


# ============================================================================
# POST /api/v1/parser-configs/ - Create Parser Config
# ============================================================================

def test_create_parser_config_success(client: TestClient, test_db: Session):
    """Test creating a new parser configuration."""
    payload = {
        "domain": "newsite.com",
        "price_selectors": [".price", "[data-price]"],
        "name_selectors": ["h1.title"],
        "image_selectors": ["img.main"],
        "use_playwright": False,
        "is_active": True,
    }

    response = client.post("/api/v1/parser-configs/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["domain"] == payload["domain"]
    assert data["price_selectors"] == payload["price_selectors"]
    assert data["name_selectors"] == payload["name_selectors"]
    assert data["is_active"] is True
    assert "id" in data

    # Verify in database
    config = test_db.query(ParserConfig).filter_by(id=data["id"]).first()
    assert config is not None
    assert config.domain == payload["domain"]


def test_create_parser_config_minimal_data(client: TestClient, test_db: Session):
    """Test creating parser config with minimal required fields."""
    payload = {
        "domain": "minimal.com",
        "price_selectors": [".price"],
    }

    response = client.post("/api/v1/parser-configs/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["domain"] == "minimal.com"
    assert data["use_playwright"] is False  # Default
    assert data["is_active"] is True  # Default
    assert data["rate_limit_seconds"] == 1.0  # Default
    assert data["max_retries"] == 3  # Default


def test_create_parser_config_duplicate_domain(
    client: TestClient, sample_parser_config: ParserConfig
):
    """Test creating parser config with duplicate domain returns error."""
    payload = {
        "domain": sample_parser_config.domain,  # Already exists
        "price_selectors": [".price"],
    }

    response = client.post("/api/v1/parser-configs/", json=payload)

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_create_parser_config_domain_normalized_to_lowercase(
    client: TestClient, test_db: Session
):
    """Test that domain is normalized to lowercase."""
    payload = {
        "domain": "UPPERCASE.COM",
        "price_selectors": [".price"],
    }

    response = client.post("/api/v1/parser-configs/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["domain"] == "uppercase.com"  # Normalized


def test_create_parser_config_missing_required_fields(client: TestClient, test_db: Session):
    """Test creating parser config without required fields."""
    payload = {
        "domain": "missing.com",
        # Missing price_selectors
    }

    response = client.post("/api/v1/parser-configs/", json=payload)

    assert response.status_code == 422  # Validation error


# ============================================================================
# PUT /api/v1/parser-configs/{id} - Update Parser Config
# ============================================================================

def test_update_parser_config_success(
    client: TestClient, sample_parser_config: ParserConfig
):
    """Test updating an existing parser configuration."""
    payload = {
        "price_selectors": [".new-price", "[data-new-price]"],
        "use_playwright": True,
        "is_active": False,
    }

    response = client.put(f"/api/v1/parser-configs/{sample_parser_config.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_parser_config.id
    assert data["price_selectors"] == payload["price_selectors"]
    assert data["use_playwright"] is True
    assert data["is_active"] is False
    # Domain should remain unchanged
    assert data["domain"] == sample_parser_config.domain


def test_update_parser_config_partial_update(
    client: TestClient, sample_parser_config: ParserConfig
):
    """Test partial update (only some fields)."""
    original_selectors = sample_parser_config.price_selectors
    payload = {"is_active": False}

    response = client.put(f"/api/v1/parser-configs/{sample_parser_config.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
    # Selectors should remain unchanged
    assert data["price_selectors"] == original_selectors


def test_update_parser_config_not_found(client: TestClient, test_db: Session):
    """Test updating non-existent parser config returns 404."""
    payload = {"is_active": False}

    response = client.put("/api/v1/parser-configs/99999", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Parser configuration not found"


def test_update_parser_config_domain_normalized(
    client: TestClient, sample_parser_config: ParserConfig
):
    """Test that updating domain normalizes it to lowercase."""
    payload = {"domain": "NEWDOMAIN.COM"}

    response = client.put(f"/api/v1/parser-configs/{sample_parser_config.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["domain"] == "newdomain.com"


# ============================================================================
# DELETE /api/v1/parser-configs/{id} - Delete Parser Config
# ============================================================================

def test_delete_parser_config_success(
    client: TestClient, sample_parser_config: ParserConfig, test_db: Session
):
    """Test deleting a parser configuration."""
    config_id = sample_parser_config.id

    response = client.delete(f"/api/v1/parser-configs/{config_id}")

    assert response.status_code == 204
    assert response.content == b""

    # Verify config is deleted from database
    config = test_db.query(ParserConfig).filter_by(id=config_id).first()
    assert config is None


def test_delete_parser_config_not_found(client: TestClient, test_db: Session):
    """Test deleting non-existent parser config returns 404."""
    response = client.delete("/api/v1/parser-configs/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Parser configuration not found"


# ============================================================================
# POST /api/v1/parser-configs/{id}/test - Test Parser Config
# ============================================================================

def test_test_parser_config_success(
    client: TestClient, sample_parser_config: ParserConfig
):
    """Test validating a parser configuration."""
    test_url = "https://test.com/product123"

    response = client.post(
        f"/api/v1/parser-configs/{sample_parser_config.id}/test?url={test_url}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["config_id"] == sample_parser_config.id
    assert data["domain"] == sample_parser_config.domain
    assert data["test_url"] == test_url
    assert "selectors_available" in data
    assert data["selectors_available"]["price"] is True
    assert data["status"] == "ready"


def test_test_parser_config_not_found(client: TestClient, test_db: Session):
    """Test testing non-existent parser config returns 404."""
    response = client.post(
        "/api/v1/parser-configs/99999/test?url=https://test.com/product"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Parser configuration not found"


def test_test_parser_config_missing_url(
    client: TestClient, sample_parser_config: ParserConfig
):
    """Test testing parser config without URL parameter."""
    response = client.post(f"/api/v1/parser-configs/{sample_parser_config.id}/test")

    assert response.status_code == 422  # Missing required query parameter


def test_test_parser_config_missing_price_selectors(
    client: TestClient, test_db: Session
):
    """Test that config without price_selectors fails validation."""
    # Create config without price_selectors
    config = ParserConfig(
        domain="incomplete.com",
        price_selectors=[],  # Empty
        is_active=True,
    )
    test_db.add(config)
    test_db.commit()
    test_db.refresh(config)

    response = client.post(
        f"/api/v1/parser-configs/{config.id}/test?url=https://incomplete.com/test"
    )

    assert response.status_code == 400
    assert "missing price_selectors" in response.json()["detail"].lower()


# ============================================================================
# Edge Cases and Validation
# ============================================================================

def test_list_parser_configs_invalid_page(client: TestClient, test_db: Session):
    """Test listing parser configs with invalid page number."""
    response = client.get("/api/v1/parser-configs/?page=0")

    assert response.status_code == 422


def test_list_parser_configs_invalid_page_size(client: TestClient, test_db: Session):
    """Test listing parser configs with invalid page size."""
    response = client.get("/api/v1/parser-configs/?page_size=200")

    assert response.status_code == 422


def test_list_parser_configs_invalid_sort_order(client: TestClient, test_db: Session):
    """Test listing parser configs with invalid sort order."""
    response = client.get("/api/v1/parser-configs/?sort_order=invalid")

    assert response.status_code == 422


def test_create_parser_config_with_all_optional_fields(
    client: TestClient, test_db: Session
):
    """Test creating parser config with all optional fields specified."""
    payload = {
        "domain": "complete.com",
        "price_selectors": [".price"],
        "name_selectors": [".name"],
        "image_selectors": [".image"],
        "use_playwright": True,
        "domain_pattern": r".*\.complete\.com$",
        "rate_limit_seconds": 2.5,
        "max_retries": 5,
        "is_active": False,
    }

    response = client.post("/api/v1/parser-configs/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["domain"] == "complete.com"
    assert data["use_playwright"] is True
    assert data["domain_pattern"] == payload["domain_pattern"]
    assert data["rate_limit_seconds"] == 2.5
    assert data["max_retries"] == 5
    assert data["is_active"] is False
