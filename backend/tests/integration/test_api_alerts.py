"""
Integration tests for Alerts API endpoints.

Tests alert management, filtering, and status updates with real database.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Alert, AlertType, AlertStatus, Product


# ============================================================================
# GET /api/v1/alerts/ - List Alerts
# ============================================================================

def test_list_alerts_empty(client: TestClient, test_db: Session):
    """Test listing alerts when database is empty."""
    response = client.get("/api/v1/alerts/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["alerts"] == []
    assert data["page"] == 1
    assert data["total_pages"] == 1


def test_list_alerts_with_pagination(client: TestClient, product_with_alerts: Product):
    """Test alert listing with pagination."""
    response = client.get("/api/v1/alerts/?page=1&page_size=2")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["alerts"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 2


def test_list_alerts_filter_by_status(client: TestClient, product_with_alerts: Product):
    """Test filtering alerts by status."""
    response = client.get("/api/v1/alerts/?status=unread")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    for alert in data["alerts"]:
        assert alert["status"] == "unread"


def test_list_alerts_filter_by_type(client: TestClient, product_with_alerts: Product):
    """Test filtering alerts by type."""
    response = client.get("/api/v1/alerts/?type=price_drop")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    for alert in data["alerts"]:
        assert alert["type"] == "price_drop"


def test_list_alerts_filter_by_status_and_type(
    client: TestClient, product_with_alerts: Product
):
    """Test filtering alerts by both status and type."""
    response = client.get("/api/v1/alerts/?status=read&type=target_reached")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    alert = data["alerts"][0]
    assert alert["status"] == "read"
    assert alert["type"] == "target_reached"


def test_list_alerts_ordered_by_created_at_desc(
    client: TestClient, product_with_alerts: Product
):
    """Test that alerts are ordered by creation date (newest first)."""
    response = client.get("/api/v1/alerts/")

    assert response.status_code == 200
    data = response.json()
    created_dates = [
        datetime.fromisoformat(alert["created_at"].replace("Z", ""))
        for alert in data["alerts"]
    ]
    assert created_dates == sorted(created_dates, reverse=True)


def test_list_alerts_includes_product_info(
    client: TestClient, product_with_alerts: Product
):
    """Test that alert list includes product information."""
    response = client.get("/api/v1/alerts/")

    assert response.status_code == 200
    data = response.json()
    for alert in data["alerts"]:
        assert "product_id" in alert
        assert alert["product_id"] == product_with_alerts.id


# ============================================================================
# GET /api/v1/alerts/{id} - Get Single Alert
# ============================================================================

def test_get_alert_success(client: TestClient, product_with_alerts: Product, test_db: Session):
    """Test retrieving a single alert by ID."""
    # Get first alert from the product
    alert = test_db.query(Alert).filter_by(product_id=product_with_alerts.id).first()

    response = client.get(f"/api/v1/alerts/{alert.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == alert.id
    assert data["product_id"] == product_with_alerts.id
    assert data["type"] in ["price_drop", "target_reached", "promo_detected"]
    assert data["status"] in ["unread", "read", "dismissed"]
    assert "message" in data
    assert "created_at" in data


def test_get_alert_not_found(client: TestClient, test_db: Session):
    """Test retrieving non-existent alert returns 404."""
    response = client.get("/api/v1/alerts/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Alert not found"


# ============================================================================
# PUT /api/v1/alerts/{id}/mark-read - Mark Alert as Read
# ============================================================================

def test_mark_alert_read_success(
    client: TestClient, product_with_alerts: Product, test_db: Session
):
    """Test marking an alert as read."""
    # Find an unread alert
    alert = (
        test_db.query(Alert)
        .filter_by(product_id=product_with_alerts.id, status=AlertStatus.UNREAD)
        .first()
    )
    assert alert is not None

    response = client.put(f"/api/v1/alerts/{alert.id}/mark-read")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == alert.id
    assert data["status"] == "read"
    assert "read_at" in data
    assert data["read_at"] is not None

    # Verify in database
    test_db.refresh(alert)
    assert alert.status == AlertStatus.READ
    assert alert.read_at is not None


def test_mark_alert_read_already_read(
    client: TestClient, product_with_alerts: Product, test_db: Session
):
    """Test marking an already-read alert as read (idempotent)."""
    # Find a read alert
    alert = (
        test_db.query(Alert)
        .filter_by(product_id=product_with_alerts.id, status=AlertStatus.READ)
        .first()
    )
    assert alert is not None

    original_read_at = alert.read_at

    response = client.put(f"/api/v1/alerts/{alert.id}/mark-read")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "read"
    # read_at should not change
    assert data["read_at"] == original_read_at.isoformat()


def test_mark_alert_read_not_found(client: TestClient, test_db: Session):
    """Test marking non-existent alert as read returns 404."""
    response = client.put("/api/v1/alerts/99999/mark-read")

    assert response.status_code == 404
    assert response.json()["detail"] == "Alert not found"


# ============================================================================
# PUT /api/v1/alerts/{id}/dismiss - Dismiss Alert
# ============================================================================

def test_dismiss_alert_success(
    client: TestClient, product_with_alerts: Product, test_db: Session
):
    """Test dismissing an alert."""
    # Get any alert
    alert = test_db.query(Alert).filter_by(product_id=product_with_alerts.id).first()

    response = client.put(f"/api/v1/alerts/{alert.id}/dismiss")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == alert.id
    assert data["status"] == "dismissed"

    # Verify in database
    test_db.refresh(alert)
    assert alert.status == AlertStatus.DISMISSED


def test_dismiss_alert_not_found(client: TestClient, test_db: Session):
    """Test dismissing non-existent alert returns 404."""
    response = client.put("/api/v1/alerts/99999/dismiss")

    assert response.status_code == 404
    assert response.json()["detail"] == "Alert not found"


def test_dismiss_alert_idempotent(
    client: TestClient, product_with_alerts: Product, test_db: Session
):
    """Test dismissing an already-dismissed alert (idempotent)."""
    # Find dismissed alert
    alert = (
        test_db.query(Alert)
        .filter_by(product_id=product_with_alerts.id, status=AlertStatus.DISMISSED)
        .first()
    )
    assert alert is not None

    response = client.put(f"/api/v1/alerts/{alert.id}/dismiss")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "dismissed"


# ============================================================================
# DELETE /api/v1/alerts/{id} - Delete Alert
# ============================================================================

def test_delete_alert_success(
    client: TestClient, product_with_alerts: Product, test_db: Session
):
    """Test deleting an alert."""
    # Get any alert
    alert = test_db.query(Alert).filter_by(product_id=product_with_alerts.id).first()
    alert_id = alert.id

    response = client.delete(f"/api/v1/alerts/{alert_id}")

    assert response.status_code == 204
    assert response.content == b""

    # Verify alert is deleted from database
    deleted_alert = test_db.query(Alert).filter_by(id=alert_id).first()
    assert deleted_alert is None


def test_delete_alert_not_found(client: TestClient, test_db: Session):
    """Test deleting non-existent alert returns 404."""
    response = client.delete("/api/v1/alerts/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Alert not found"


def test_delete_alert_does_not_delete_product(
    client: TestClient, product_with_alerts: Product, test_db: Session
):
    """Test that deleting an alert does not delete the associated product."""
    # Get alert
    alert = test_db.query(Alert).filter_by(product_id=product_with_alerts.id).first()
    alert_id = alert.id
    product_id = product_with_alerts.id

    # Delete alert
    response = client.delete(f"/api/v1/alerts/{alert_id}")
    assert response.status_code == 204

    # Verify product still exists
    product = test_db.query(Product).filter_by(id=product_id).first()
    assert product is not None


# ============================================================================
# Edge Cases and Validation
# ============================================================================

def test_list_alerts_invalid_page(client: TestClient, test_db: Session):
    """Test listing alerts with invalid page number."""
    response = client.get("/api/v1/alerts/?page=0")

    assert response.status_code == 422  # Validation error


def test_list_alerts_invalid_page_size(client: TestClient, test_db: Session):
    """Test listing alerts with invalid page size."""
    response = client.get("/api/v1/alerts/?page_size=200")

    assert response.status_code == 422  # Exceeds max


def test_list_alerts_invalid_status(client: TestClient, test_db: Session):
    """Test listing alerts with invalid status value."""
    response = client.get("/api/v1/alerts/?status=invalid")

    assert response.status_code == 422


def test_list_alerts_invalid_type(client: TestClient, test_db: Session):
    """Test listing alerts with invalid type value."""
    response = client.get("/api/v1/alerts/?type=invalid")

    assert response.status_code == 422


# ============================================================================
# Integration with Product Deletion
# ============================================================================

def test_alerts_deleted_when_product_deleted(
    client: TestClient, product_with_alerts: Product, test_db: Session
):
    """Test that alerts are cascade-deleted when product is deleted."""
    product_id = product_with_alerts.id

    # Verify alerts exist
    alert_count = test_db.query(Alert).filter_by(product_id=product_id).count()
    assert alert_count > 0

    # Delete product
    response = client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == 204

    # Verify alerts are deleted
    alert_count_after = test_db.query(Alert).filter_by(product_id=product_id).count()
    assert alert_count_after == 0


# ============================================================================
# Alert Data Validation
# ============================================================================

def test_price_drop_alert_contains_price_data(
    client: TestClient, product_with_alerts: Product, test_db: Session
):
    """Test that price drop alerts contain old_price, new_price, and percentage."""
    alert = (
        test_db.query(Alert)
        .filter_by(product_id=product_with_alerts.id, type=AlertType.PRICE_DROP)
        .first()
    )

    response = client.get(f"/api/v1/alerts/{alert.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "price_drop"
    assert data["old_price"] is not None
    assert data["new_price"] is not None
    assert data["price_drop_percentage"] is not None


def test_target_reached_alert_contains_message(
    client: TestClient, product_with_alerts: Product, test_db: Session
):
    """Test that target_reached alerts contain proper message."""
    alert = (
        test_db.query(Alert)
        .filter_by(product_id=product_with_alerts.id, type=AlertType.TARGET_REACHED)
        .first()
    )

    response = client.get(f"/api/v1/alerts/{alert.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "target_reached"
    assert "message" in data
    assert len(data["message"]) > 0
