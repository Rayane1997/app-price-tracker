from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import Optional, List
from urllib.parse import urlparse
from ..models.product import Product, ProductStatus
from ..schemas.product import ProductCreate, ProductUpdate
from ..models.parser_config import ParserConfig
from ..schemas.parser_config import ParserConfigCreate, ParserConfigUpdate

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    # Remove www. prefix
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain.lower()

def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[ProductStatus] = None,
    domain: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[List[Product], int]:
    """Get products with filtering and pagination"""
    query = db.query(Product)

    # Filters
    if status:
        query = query.filter(Product.status == status)
    if domain:
        query = query.filter(Product.domain == domain)

    # Count total
    total = query.count()

    # Sorting
    order_column = getattr(Product, sort_by, Product.created_at)
    if sort_order == "asc":
        query = query.order_by(asc(order_column))
    else:
        query = query.order_by(desc(order_column))

    # Pagination
    products = query.offset(skip).limit(limit).all()

    return products, total

def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Get single product by ID"""
    return db.query(Product).filter(Product.id == product_id).first()

def create_product(db: Session, product: ProductCreate) -> Product:
    """Create new product"""
    # Extract domain from URL
    domain = extract_domain(product.url)

    # If name is not provided, use a temporary name based on domain
    name = product.name if product.name else f"Product from {domain}"

    db_product = Product(
        name=name,
        url=product.url,
        domain=domain,
        target_price=product.target_price,
        image_url=product.image_url,
        check_frequency_hours=product.check_frequency_hours,
        tags=product.tags,
        notes=product.notes,
        status=ProductStatus.ACTIVE,
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
    """Update existing product"""
    db_product = get_product(db, product_id)
    if not db_product:
        return None

    # Update only provided fields
    update_data = product_update.model_dump(exclude_unset=True)

    # If URL is updated, re-extract domain
    if "url" in update_data:
        update_data["domain"] = extract_domain(update_data["url"])

    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> bool:
    """Delete product (cascade deletes price_history and alerts)"""
    db_product = get_product(db, product_id)
    if not db_product:
        return False

    db.delete(db_product)
    db.commit()
    return True

def get_domains(db: Session) -> List[str]:
    """Get list of unique domains"""
    domains = db.query(Product.domain).distinct().all()
    return [d[0] for d in domains]


# ParserConfig CRUD functions

def get_parser_configs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[List[ParserConfig], int]:
    """Get parser configs with filtering and pagination"""
    query = db.query(ParserConfig)

    # Filters
    if is_active is not None:
        query = query.filter(ParserConfig.is_active == is_active)

    # Count total
    total = query.count()

    # Sorting
    order_column = getattr(ParserConfig, sort_by, ParserConfig.created_at)
    if sort_order == "asc":
        query = query.order_by(asc(order_column))
    else:
        query = query.order_by(desc(order_column))

    # Pagination
    configs = query.offset(skip).limit(limit).all()

    return configs, total


def get_parser_config(db: Session, config_id: int) -> Optional[ParserConfig]:
    """Get single parser config by ID"""
    return db.query(ParserConfig).filter(ParserConfig.id == config_id).first()


def get_parser_config_by_domain(db: Session, domain: str) -> Optional[ParserConfig]:
    """Get parser config by domain"""
    return db.query(ParserConfig).filter(ParserConfig.domain == domain.lower()).first()


def create_parser_config(db: Session, config: ParserConfigCreate) -> ParserConfig:
    """Create new parser config"""
    db_config = ParserConfig(
        domain=config.domain.lower(),
        price_selectors=config.price_selectors,
        name_selectors=config.name_selectors,
        image_selectors=config.image_selectors,
        use_playwright=config.use_playwright,
        domain_pattern=config.domain_pattern,
        rate_limit_seconds=config.rate_limit_seconds,
        max_retries=config.max_retries,
        is_active=config.is_active,
    )

    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def update_parser_config(
    db: Session, config_id: int, config_update: ParserConfigUpdate
) -> Optional[ParserConfig]:
    """Update existing parser config"""
    db_config = get_parser_config(db, config_id)
    if not db_config:
        return None

    # Update only provided fields
    update_data = config_update.model_dump(exclude_unset=True)

    # Lowercase domain if provided
    if "domain" in update_data:
        update_data["domain"] = update_data["domain"].lower()

    for field, value in update_data.items():
        setattr(db_config, field, value)

    db.commit()
    db.refresh(db_config)
    return db_config


def delete_parser_config(db: Session, config_id: int) -> bool:
    """Delete parser config"""
    db_config = get_parser_config(db, config_id)
    if not db_config:
        return False

    db.delete(db_config)
    db.commit()
    return True
