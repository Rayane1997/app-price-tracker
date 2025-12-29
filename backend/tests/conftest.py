"""
Pytest configuration and fixtures for unit tests.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.database import Base
from app.models import Product, ProductStatus, PriceHistory, Alert, AlertType, AlertStatus


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create an in-memory SQLite database for testing.
    Each test gets a fresh database.
    """
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:", echo=False)

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


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_product(test_db: Session) -> Product:
    """Create a sample product in the database."""
    product = Product(
        name="Test Product - Sony WH-1000XM5",
        url="https://www.amazon.fr/dp/B09XS7JWHH",
        domain="amazon.fr",
        current_price=349.99,
        currency="EUR",
        target_price=299.99,
        image_url="https://m.media-amazon.com/images/I/test.jpg",
        check_frequency_hours=24,
        status=ProductStatus.ACTIVE,
        tags="headphones,sony",
        notes="Premium noise-canceling headphones",
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
def sample_product_with_history(test_db: Session) -> Product:
    """Create a sample product with price history."""
    product = Product(
        name="Product with Price History",
        url="https://www.fnac.com/product123",
        domain="fnac.com",
        current_price=99.99,
        currency="EUR",
        target_price=79.99,
        status=ProductStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    # Add price history entries (newest to oldest)
    history_entries = [
        PriceHistory(
            product_id=product.id,
            price=99.99,
            currency="EUR",
            is_promo=False,
            recorded_at=datetime.utcnow(),
        ),
        PriceHistory(
            product_id=product.id,
            price=119.99,
            currency="EUR",
            is_promo=False,
            recorded_at=datetime.utcnow() - timedelta(days=1),
        ),
        PriceHistory(
            product_id=product.id,
            price=129.99,
            currency="EUR",
            is_promo=False,
            recorded_at=datetime.utcnow() - timedelta(days=2),
        ),
    ]

    for entry in history_entries:
        test_db.add(entry)

    test_db.commit()
    return product


@pytest.fixture
def sample_promo_product(test_db: Session) -> Product:
    """Create a product with promotional pricing."""
    product = Product(
        name="Product on Promo",
        url="https://www.amazon.fr/promo123",
        domain="amazon.fr",
        current_price=79.99,
        currency="EUR",
        status=ProductStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    # Add promo price history
    promo_entry = PriceHistory(
        product_id=product.id,
        price=79.99,
        currency="EUR",
        is_promo=True,
        promo_percentage=20.0,
        recorded_at=datetime.utcnow(),
    )
    test_db.add(promo_entry)

    # Add non-promo history
    regular_entry = PriceHistory(
        product_id=product.id,
        price=99.99,
        currency="EUR",
        is_promo=False,
        recorded_at=datetime.utcnow() - timedelta(days=1),
    )
    test_db.add(regular_entry)

    test_db.commit()
    return product


@pytest.fixture
def sample_alert(test_db: Session, sample_product: Product) -> Alert:
    """Create a sample alert."""
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
    return alert


# ============================================================================
# Mock HTML Fixtures
# ============================================================================

@pytest.fixture
def amazon_html_sample() -> str:
    """Sample Amazon HTML with price."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Amazon Product</title></head>
    <body>
        <h1 id="productTitle">Sony WH-1000XM5 Wireless Headphones</h1>
        <span class="a-price">
            <span class="a-offscreen">349,99 €</span>
            <span class="a-price-whole">349,</span>
            <span class="a-price-fraction">99</span>
            <span class="a-price-symbol">€</span>
        </span>
        <img id="landingImage" src="https://m.media-amazon.com/images/I/test.jpg" />
        <div id="availability">In Stock</div>
    </body>
    </html>
    """


@pytest.fixture
def amazon_promo_html_sample() -> str:
    """Sample Amazon HTML with promotional price."""
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <h1 id="productTitle">Sony WH-1000XM5 - ON SALE</h1>
        <span class="a-price">
            <span class="a-offscreen">279,99 €</span>
        </span>
        <span class="savingsPercentage">-20%</span>
        <span class="a-text-strike">349,99 €</span>
    </body>
    </html>
    """


@pytest.fixture
def cdiscount_html_sample() -> str:
    """Sample Cdiscount HTML."""
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <h1 itemprop="name">Casque Sony WH-1000XM5</h1>
        <span class="fpPrice">299,99 €</span>
        <img class="ProductMainImage" src="https://cdn.cdiscount.com/test.jpg" />
    </body>
    </html>
    """


@pytest.fixture
def fnac_html_sample() -> str:
    """Sample Fnac HTML."""
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <h1 class="f-productHeader-Title">Sony WH-1000XM5</h1>
        <div class="f-buyBox-price-value">319,99 €</div>
        <img class="Picture-img" src="https://static.fnac.com/test.jpg" />
    </body>
    </html>
    """


@pytest.fixture
def boulanger_html_sample() -> str:
    """Sample Boulanger HTML."""
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <h1 class="title">Sony WH-1000XM5 Noir</h1>
        <span class="price-sales">329,99 €</span>
        <img class="main-image" src="https://boulanger.scene7.com/test.jpg" />
    </body>
    </html>
    """


@pytest.fixture
def bol_html_sample() -> str:
    """Sample Bol.com HTML."""
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <h1 data-test="title">Sony WH-1000XM5</h1>
        <span class="promo-price">€ 299,99</span>
        <img class="js_selected_image" src="https://media.bol.com/test.jpg" />
    </body>
    </html>
    """


@pytest.fixture
def coolblue_html_sample() -> str:
    """Sample Coolblue HTML."""
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <h1 class="product-name">Sony WH-1000XM5 Zwart</h1>
        <span class="sales-price__current">€ 339,99</span>
        <img class="main-image" src="https://image.coolblue.be/test.jpg" />
    </body>
    </html>
    """


@pytest.fixture
def invalid_html_sample() -> str:
    """Invalid HTML for error testing."""
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <div>No product information here</div>
    </body>
    </html>
    """
