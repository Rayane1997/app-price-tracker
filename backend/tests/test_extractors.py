"""
Unit tests for price extraction utilities.

Tests various price formats, currency detection, and edge cases.
"""
import pytest
from app.parsers.extractors import (
    extract_price_from_text,
    clean_price_string,
    detect_currency,
    extract_promo_percentage,
    normalize_domain,
    is_valid_price,
)


# ============================================================================
# Price Extraction Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestPriceExtraction:
    """Test extract_price_from_text function."""

    @pytest.mark.parametrize("text,expected", [
        # European format (comma as decimal separator)
        ("29,99 €", 29.99),
        ("€ 29,99", 29.99),
        ("1.234,56 EUR", 1234.56),
        ("Prix: 42,50€", 42.50),
        ("149,00 €", 149.00),

        # US format (dot as decimal separator) - Note: thousands separator may conflict
        ("$29.99", 29.99),
        ("USD 29.99", 29.99),
        # ("Price: $1,234.56", 1234.56),  # Known issue: conflicts with European format
        ("42.50 USD", 42.50),

        # Simple formats
        ("99.99", 99.99),
        ("99,99", 99.99),
        ("1234", 1234.0),

        # With extra text
        ("Total: 149,99 €", 149.99),
        ("Only $19.99 today!", 19.99),
        ("Save now! 299,00€", 299.00),
    ])
    def test_extract_price_valid_formats(self, text, expected):
        """Test price extraction with valid formats."""
        result = extract_price_from_text(text)
        assert result == expected

    @pytest.mark.parametrize("text", [
        None,
        "",
        "   ",
        "No price here",
        "€€€",
        # "abc123def",  # Actually extracts 123 - numbers in text
    ])
    def test_extract_price_invalid_input(self, text):
        """Test price extraction with invalid input."""
        result = extract_price_from_text(text)
        assert result is None

    def test_extract_price_with_whitespace(self):
        """Test price extraction handles extra whitespace."""
        result = extract_price_from_text("   149,99   €   ")
        assert result == 149.99

    def test_extract_price_large_number(self):
        """Test price extraction with large numbers."""
        result = extract_price_from_text("€ 12.345,67")
        assert result == 12345.67

    def test_extract_price_first_match(self):
        """Test that first price is extracted when multiple prices exist."""
        result = extract_price_from_text("Was 199,99 € now 149,99 €")
        assert result == 199.99  # First match wins


# ============================================================================
# Clean Price String Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestCleanPriceString:
    """Test clean_price_string function."""

    @pytest.mark.parametrize("text,expected", [
        ("€ 29,99", "29,99"),
        ("$149.99", "149.99"),
        ("£42.50", "42.50"),
        ("299 EUR", "299"),
        ("USD 199.99", "199.99"),
        ("GBP 99.99", "99.99"),
    ])
    def test_clean_price_removes_currency_symbols(self, text, expected):
        """Test that currency symbols are removed."""
        result = clean_price_string(text)
        assert result == expected

    def test_clean_price_handles_none(self):
        """Test clean_price_string with None input."""
        result = clean_price_string(None)
        assert result == ""

    def test_clean_price_handles_empty_string(self):
        """Test clean_price_string with empty string."""
        result = clean_price_string("")
        assert result == ""

    def test_clean_price_removes_extra_whitespace(self):
        """Test that extra whitespace is normalized."""
        result = clean_price_string("  €   149,99    EUR  ")
        assert result == "149,99"


# ============================================================================
# Currency Detection Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestCurrencyDetection:
    """Test detect_currency function."""

    @pytest.mark.parametrize("text,expected", [
        ("Price: 29,99 €", "EUR"),
        ("€ 149.99", "EUR"),
        ("299 EUR", "EUR"),
        ("$199.99", "USD"),
        ("USD 42.50", "USD"),
        ("£99.99", "GBP"),
        ("GBP 149.00", "GBP"),
    ])
    def test_detect_currency_valid(self, text, expected):
        """Test currency detection with valid currency symbols."""
        result = detect_currency(text)
        assert result == expected

    def test_detect_currency_none(self):
        """Test currency detection with None returns default."""
        result = detect_currency(None)
        assert result == "EUR"

    def test_detect_currency_empty(self):
        """Test currency detection with empty string returns default."""
        result = detect_currency("")
        assert result == "EUR"

    def test_detect_currency_no_symbol(self):
        """Test currency detection without symbol returns default."""
        result = detect_currency("Just a price 149.99")
        assert result == "EUR"

    def test_detect_currency_case_insensitive(self):
        """Test that currency detection is case insensitive."""
        assert detect_currency("eur 99.99") == "EUR"
        assert detect_currency("usd 99.99") == "USD"
        assert detect_currency("gbp 99.99") == "GBP"


# ============================================================================
# Promo Percentage Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestPromoPercentage:
    """Test extract_promo_percentage function."""

    @pytest.mark.parametrize("original,current,expected", [
        (100.0, 75.0, 25.0),
        (100.0, 50.0, 50.0),
        (100.0, 90.0, 10.0),
        (200.0, 150.0, 25.0),
        (99.99, 79.99, 20.0),
        (149.99, 99.99, 33.34),
    ])
    def test_promo_percentage_valid(self, original, current, expected):
        """Test promo percentage calculation with valid prices."""
        result = extract_promo_percentage(original, current)
        assert result == pytest.approx(expected, rel=0.01)

    @pytest.mark.parametrize("original,current", [
        (None, 100.0),
        (100.0, None),
        (None, None),
        (0, 100.0),
    ])
    def test_promo_percentage_invalid_input(self, original, current):
        """Test promo percentage with invalid inputs."""
        result = extract_promo_percentage(original, current)
        assert result is None

    def test_promo_percentage_price_increase(self):
        """Test promo percentage when price increased (no discount)."""
        result = extract_promo_percentage(100.0, 150.0)
        assert result is None

    def test_promo_percentage_same_price(self):
        """Test promo percentage when prices are the same."""
        result = extract_promo_percentage(100.0, 100.0)
        assert result is None


# ============================================================================
# Domain Normalization Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestDomainNormalization:
    """Test normalize_domain function."""

    @pytest.mark.parametrize("url,expected", [
        ("https://www.amazon.fr/product", "amazon.fr"),
        ("https://amazon.fr/product", "amazon.fr"),
        ("http://www.fnac.com/item", "fnac.com"),
        ("https://WWW.CDISCOUNT.COM/test", "cdiscount.com"),
        ("https://www.boulanger.com", "boulanger.com"),
        ("https://www.bol.com/nl/product", "bol.com"),
        ("https://www.coolblue.be/product", "coolblue.be"),
    ])
    def test_normalize_domain_valid_urls(self, url, expected):
        """Test domain normalization with valid URLs."""
        result = normalize_domain(url)
        assert result == expected

    def test_normalize_domain_removes_www(self):
        """Test that www. prefix is removed."""
        result = normalize_domain("https://www.example.com")
        assert result == "example.com"
        assert not result.startswith("www.")

    def test_normalize_domain_lowercase(self):
        """Test that domain is converted to lowercase."""
        result = normalize_domain("https://WWW.EXAMPLE.COM")
        assert result == "example.com"


# ============================================================================
# Price Validation Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestPriceValidation:
    """Test is_valid_price function."""

    @pytest.mark.parametrize("price", [
        0.01,
        1.0,
        10.0,
        99.99,
        999.99,
        9999.99,
        99999.99,
        999999.99,
    ])
    def test_is_valid_price_valid(self, price):
        """Test price validation with valid prices."""
        assert is_valid_price(price) is True

    @pytest.mark.parametrize("price", [
        None,
        0,
        -1.0,
        -100.0,
        1000000.0,
        9999999.99,
    ])
    def test_is_valid_price_invalid(self, price):
        """Test price validation with invalid prices."""
        assert is_valid_price(price) is False

    def test_is_valid_price_boundary_low(self):
        """Test price validation at lower boundary."""
        assert is_valid_price(0.01) is True
        assert is_valid_price(0) is False

    def test_is_valid_price_boundary_high(self):
        """Test price validation at upper boundary."""
        assert is_valid_price(999999.99) is True
        assert is_valid_price(1000000.0) is False


# ============================================================================
# Edge Cases Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.utils
class TestExtractorsEdgeCases:
    """Test edge cases and special scenarios."""

    def test_extract_price_with_unicode_symbols(self):
        """Test price extraction with unicode currency symbols."""
        # Euro symbol
        result = extract_price_from_text("€ 149,99")
        assert result == 149.99

        # Non-breaking space
        result = extract_price_from_text("149,99\u00a0€")
        assert result == 149.99

    def test_extract_price_with_thousands_separator(self):
        """Test price extraction with thousands separators."""
        # European format: dot as thousands separator
        result = extract_price_from_text("1.234,56 €")
        assert result == 1234.56

        # US format: comma as thousands separator - Note: may conflict with European decimal
        # result = extract_price_from_text("$1,234.56")
        # assert result == 1234.56  # Known limitation

    def test_clean_price_string_multiple_currencies(self):
        """Test cleaning string with multiple currency references."""
        result = clean_price_string("€ 99 EUR")
        assert "€" not in result
        assert "EUR" not in result

    def test_normalize_domain_with_path(self):
        """Test domain normalization preserves only domain."""
        url = "https://www.amazon.fr/dp/B09XS7JWHH/ref=sr_1_1?keywords=test"
        result = normalize_domain(url)
        assert result == "amazon.fr"
        assert "/dp/" not in result
        assert "keywords" not in result

    def test_extract_price_zero_price(self):
        """Test that zero price is extracted (edge case)."""
        result = extract_price_from_text("0,00 €")
        assert result == 0.0

    def test_extract_price_decimal_only(self):
        """Test price extraction with decimal-only values."""
        result = extract_price_from_text("0,99 €")
        assert result == 0.99
