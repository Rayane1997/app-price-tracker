import re
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

def extract_price_from_text(text: str) -> Optional[float]:
    """
    Extract price from text string

    Examples:
        "29,99 €" -> 29.99
        "€ 49.99" -> 49.99
        "1 234,56 EUR" -> 1234.56
        "Price: $19.99" -> 19.99

    Args:
        text: Text containing a price

    Returns:
        Price as float, or None if no price found
    """
    if not text:
        return None

    # Remove extra whitespace
    text = ' '.join(text.split())

    # Pattern to match prices (handles European and US formats)
    # Matches: 1,234.56 or 1.234,56 or 1234.56 or 1234,56
    patterns = [
        # European format: 1.234,56 or 1234,56
        r'(\d{1,3}(?:\.\d{3})*,\d{2})',
        # US format: 1,234.56 or 1234.56
        r'(\d{1,3}(?:,\d{3})*\.\d{2})',
        # Simple formats: 1234.56 or 1234,56
        r'(\d+[.,]\d{2})',
        # Integer prices: 1234
        r'(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            price_str = match.group(1)
            # Convert to float
            # Replace comma with dot for European format
            if ',' in price_str:
                # European format (1.234,56 -> 1234.56)
                price_str = price_str.replace('.', '').replace(',', '.')
            else:
                # US format (1,234.56 -> 1234.56)
                price_str = price_str.replace(',', '')

            try:
                return float(price_str)
            except ValueError:
                continue

    logger.warning(f"Could not extract price from text: {text[:100]}")
    return None

def clean_price_string(text: str) -> str:
    """
    Clean price string by removing currency symbols and extra characters

    Args:
        text: Raw price text

    Returns:
        Cleaned price string
    """
    if not text:
        return ""

    # Remove currency symbols
    currency_symbols = ['€', '$', '£', 'EUR', 'USD', 'GBP']
    for symbol in currency_symbols:
        text = text.replace(symbol, '')

    # Remove extra whitespace
    text = ' '.join(text.split())

    return text.strip()

def detect_currency(text: str) -> str:
    """
    Detect currency from text

    Args:
        text: Text containing currency symbol

    Returns:
        Currency code (EUR, USD, GBP, etc.)
    """
    if not text:
        return "EUR"

    text = text.upper()

    if '€' in text or 'EUR' in text:
        return "EUR"
    elif '$' in text or 'USD' in text:
        return "USD"
    elif '£' in text or 'GBP' in text:
        return "GBP"

    # Default to EUR for FR/BE sites
    return "EUR"

def extract_promo_percentage(original_price: float, current_price: float) -> Optional[float]:
    """
    Calculate promotion percentage

    Args:
        original_price: Original price before discount
        current_price: Current discounted price

    Returns:
        Discount percentage (e.g., 25.0 for 25% off), or None if no discount
    """
    if not original_price or not current_price:
        return None

    if current_price >= original_price:
        return None

    discount = ((original_price - current_price) / original_price) * 100
    return round(discount, 2)

def normalize_domain(url: str) -> str:
    """
    Extract and normalize domain from URL

    Args:
        url: Full URL

    Returns:
        Normalized domain (e.g., "amazon.fr")
    """
    from urllib.parse import urlparse

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # Remove www. prefix
    if domain.startswith('www.'):
        domain = domain[4:]

    return domain

def is_valid_price(price: Optional[float]) -> bool:
    """
    Validate that price is reasonable

    Args:
        price: Price to validate

    Returns:
        True if price is valid
    """
    if price is None:
        return False

    # Price must be positive and less than 1 million EUR
    return 0 < price < 1_000_000
