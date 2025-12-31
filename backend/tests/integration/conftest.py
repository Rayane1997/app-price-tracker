"""
Integration test fixtures and configuration.

Provides:
- FastAPI TestClient
- Test database with real migrations
- Database session override
- Sample data fixtures for integration tests
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from typing import Generator

from app.main import app
from app.core.database import Base, get_db
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
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create an in-memory SQLite database for integration tests.
    Each test gets a fresh database with full schema.
    """
    # Create in-memory SQLite database with check_same_thread=False for TestClient
    engine = create_engine(
        "sqlite://",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> TestClient:
    """
    Create FastAPI TestClient with database override.
    All API calls will use the test database.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# Sample Data Fixtures for Integration Tests
# ============================================================================

@pytest.fixture
def sample_product(test_db: Session) -> Product:
    """Create a sample product for integration tests."""
    product = Product(
        name="Integration Test - Sony WH-1000XM5",
        url="https://www.amazon.fr/dp/B09XS7JWHH",
        domain="amazon.fr",
        current_price=349.99,
        currency="EUR",
        target_price=None,
        image_url="https://m.media-amazon.com/images/I/test.jpg",
        check_frequency_hours=24,
        status=ProductStatus.ACTIVE,
        tags="headphones,sony,test",
        notes="Integration test product",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_checked_at=datetime.utcnow(),
        last_success_at=datetime.utcnow(),
        consecutive_errors=0,
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    return product


@pytest.fixture
def multiple_products(test_db: Session) -> list[Product]:
    """Create multiple products for pagination and filtering tests."""
    products = [
        Product(
            name=f"Product {i}",
            url=f"https://www.amazon.fr/dp/TEST{i}",
            domain="amazon.fr" if i % 2 == 0 else "fnac.com",
            current_price=100.00 + i,
            currency="EUR",
            target_price=90.00 + i,
            status=ProductStatus.ACTIVE if i % 3 != 0 else ProductStatus.PAUSED,
            created_at=datetime.utcnow() - timedelta(days=i),
        )
        for i in range(1, 11)
    ]

    for product in products:
        test_db.add(product)

    test_db.commit()

    # Refresh all products
    for product in products:
        test_db.refresh(product)

    return products


@pytest.fixture
def product_with_price_history(test_db: Session) -> Product:
    """Create product with comprehensive price history."""
    product = Product(
        name="Product with History",
        url="https://www.fnac.com/product123",
        domain="fnac.com",
        current_price=99.99,
        currency="EUR",
        target_price=79.99,
        status=ProductStatus.ACTIVE,
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    # Add price history spanning 100 days
    now = datetime.utcnow()
    for i in range(100):
        price = 100 + (i % 20)  # Fluctuating price
        is_promo = i % 10 == 0  # Every 10th entry is promo

        entry = PriceHistory(
            product_id=product.id,
            price=price,
            currency="EUR",
            is_promo=is_promo,
            promo_percentage=15.0 if is_promo else None,
            recorded_at=now - timedelta(days=99 - i),
        )
        test_db.add(entry)

    test_db.commit()
    return product


@pytest.fixture
def product_with_alerts(test_db: Session) -> Product:
    """Create product with multiple alerts."""
    product = Product(
        name="Product with Alerts",
        url="https://www.amazon.fr/alerts",
        domain="amazon.fr",
        current_price=249.99,
        currency="EUR",
        status=ProductStatus.ACTIVE,
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    # Create alerts of different types and statuses
    alerts_data = [
        {
            "type": AlertType.PRICE_DROP,
            "status": AlertStatus.UNREAD,
            "old_price": 299.99,
            "new_price": 249.99,
            "price_drop_percentage": 16.67,
            "message": "Price dropped by 16.67%!",
        },
        {
            "type": AlertType.TARGET_REACHED,
            "status": AlertStatus.READ,
            "old_price": 299.99,
            "new_price": 249.99,
            "message": "Target price reached!",
        },
        {
            "type": AlertType.PROMO_DETECTED,
            "status": AlertStatus.DISMISSED,
            "old_price": None,
            "new_price": 249.99,
            "message": "Promo detected!",
        },
    ]

    for i, alert_data in enumerate(alerts_data):
        read_at = None
        if alert_data["status"] != AlertStatus.READ:
            read_at = None
        else:
            read_at = datetime.utcnow() - timedelta(hours=i)

        alert = Alert(
            product_id=product.id,
            created_at=datetime.utcnow() - timedelta(hours=i),
            read_at=read_at,
            **alert_data,
        )
        test_db.add(alert)

    test_db.commit()
    return product


@pytest.fixture
def sample_parser_config(test_db: Session) -> ParserConfig:
    """Create sample parser configuration."""
    config = ParserConfig(
        domain="test.com",
        price_selectors=[".price", "[data-price]"],
        name_selectors=["h1.title", ".product-name"],
        image_selectors=["img.main", "[data-image]"],
        use_playwright=False,
        domain_pattern=r".*\.test\.com$",
        rate_limit_seconds=1.0,
        max_retries=3,
        is_active=True,
    )
    test_db.add(config)
    test_db.commit()
    test_db.refresh(config)
    return config


@pytest.fixture
def multiple_parser_configs(test_db: Session) -> list[ParserConfig]:
    """Create multiple parser configs for testing."""
    configs = [
        ParserConfig(
            domain=f"test{i}.com",
            price_selectors=[".price"],
            name_selectors=[".title"],
            is_active=i % 2 == 0,
            created_at=datetime.utcnow() - timedelta(days=i),
        )
        for i in range(1, 6)
    ]

    for config in configs:
        test_db.add(config)

    test_db.commit()

    for config in configs:
        test_db.refresh(config)

    return configs
