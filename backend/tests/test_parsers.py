"""
Unit tests for all site-specific parsers.

Tests all 6 parsers (Amazon, Cdiscount, Fnac, Boulanger, Bol, Coolblue).
"""
import pytest
from bs4 import BeautifulSoup
from unittest.mock import Mock, patch, AsyncMock

from app.parsers.amazon_parser import AmazonParser
from app.parsers.fr_sites_parsers import CdiscountParser, FnacParser, BoulangerParser
from app.parsers.be_sites_parsers import BolcomParser, CoolblueParser
from app.parsers.base import ProductData


# ============================================================================
# Amazon Parser Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.parsers
class TestAmazonParser:
    """Test AmazonParser."""

    def test_supported_domains(self):
        """Test Amazon supported domains."""
        parser = AmazonParser()
        assert "amazon.fr" in parser.supported_domains
        assert "amazon.be" in parser.supported_domains
        assert "amazon.com.be" in parser.supported_domains

    def test_requires_javascript(self):
        """Test that Amazon requires JavaScript."""
        parser = AmazonParser()
        assert parser.requires_javascript is True

    def test_validate_url_valid(self):
        """Test URL validation with valid Amazon URLs."""
        parser = AmazonParser()
        assert parser.validate_url("https://www.amazon.fr/dp/B09XS7JWHH") is True
        assert parser.validate_url("https://amazon.fr/product/test") is True
        assert parser.validate_url("https://www.amazon.be/dp/B09XS7JWHH") is True
        assert parser.validate_url("https://www.amazon.com.be/dp/B0CG19FGQ5") is True

    def test_validate_url_invalid(self):
        """Test URL validation with invalid URLs."""
        parser = AmazonParser()
        assert parser.validate_url("https://www.fnac.com/product") is False
        assert parser.validate_url("https://www.amazon.com/product") is False

    def test_extract_price_from_html(self, amazon_html_sample):
        """Test price extraction from Amazon HTML."""
        parser = AmazonParser()
        soup = BeautifulSoup(amazon_html_sample, 'html.parser')
        price = parser.extract_price(soup)
        assert price == 349.99

    def test_extract_price_from_promo_html(self, amazon_promo_html_sample):
        """Test price extraction from promotional Amazon page."""
        parser = AmazonParser()
        soup = BeautifulSoup(amazon_promo_html_sample, 'html.parser')
        price = parser.extract_price(soup)
        assert price == 279.99

    def test_extract_name_from_html(self, amazon_html_sample):
        """Test product name extraction."""
        parser = AmazonParser()
        soup = BeautifulSoup(amazon_html_sample, 'html.parser')
        name = parser.extract_name(soup)
        assert name == "Sony WH-1000XM5 Wireless Headphones"

    def test_extract_image_from_html(self, amazon_html_sample):
        """Test image extraction."""
        parser = AmazonParser()
        soup = BeautifulSoup(amazon_html_sample, 'html.parser')
        image = parser.extract_image(soup)
        assert image == "https://m.media-amazon.com/images/I/test.jpg"

    def test_detect_promo_with_badge(self, amazon_promo_html_sample):
        """Test promo detection with badge."""
        parser = AmazonParser()
        soup = BeautifulSoup(amazon_promo_html_sample, 'html.parser')
        is_promo, percentage = parser.detect_promo(soup)
        assert is_promo is True
        assert percentage == 20.0

    def test_detect_promo_without_badge(self, amazon_html_sample):
        """Test promo detection on regular product."""
        parser = AmazonParser()
        soup = BeautifulSoup(amazon_html_sample, 'html.parser')
        is_promo, percentage = parser.detect_promo(soup)
        assert is_promo is False
        assert percentage is None

    def test_check_availability_in_stock(self, amazon_html_sample):
        """Test availability check for in-stock product."""
        parser = AmazonParser()
        soup = BeautifulSoup(amazon_html_sample, 'html.parser')
        is_available = parser._check_availability(soup)
        assert is_available is True

    def test_check_availability_out_of_stock(self):
        """Test availability check for out-of-stock product."""
        parser = AmazonParser()
        html = "<html><body><div id='availability'>Currently unavailable</div></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        is_available = parser._check_availability(soup)
        assert is_available is False

    def test_extract_price_invalid_html(self, invalid_html_sample):
        """Test price extraction with invalid HTML."""
        parser = AmazonParser()
        soup = BeautifulSoup(invalid_html_sample, 'html.parser')
        price = parser.extract_price(soup)
        assert price is None

    @pytest.mark.asyncio
    async def test_parse_full_workflow(self, amazon_html_sample):
        """Test complete parsing workflow."""
        parser = AmazonParser()

        with patch('app.parsers.engine.ParserEngine.fetch_html', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = amazon_html_sample

            result = await parser.parse("https://www.amazon.fr/dp/B09XS7JWHH")

            assert isinstance(result, ProductData)
            assert result.name == "Sony WH-1000XM5 Wireless Headphones"
            assert result.price == 349.99
            assert result.currency == "EUR"
            assert result.is_available is True
            mock_fetch.assert_called_once()


# ============================================================================
# Cdiscount Parser Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.parsers
class TestCdiscountParser:
    """Test CdiscountParser."""

    def test_supported_domains(self):
        """Test Cdiscount supported domains."""
        parser = CdiscountParser()
        assert "cdiscount.com" in parser.supported_domains

    def test_requires_javascript(self):
        """Test that Cdiscount doesn't require JavaScript."""
        parser = CdiscountParser()
        assert parser.requires_javascript is False

    def test_extract_price_from_html(self, cdiscount_html_sample):
        """Test price extraction from Cdiscount HTML."""
        parser = CdiscountParser()
        soup = BeautifulSoup(cdiscount_html_sample, 'html.parser')
        price = parser.extract_price(soup)
        assert price == 299.99

    def test_extract_name_from_html(self, cdiscount_html_sample):
        """Test name extraction from Cdiscount HTML."""
        parser = CdiscountParser()
        soup = BeautifulSoup(cdiscount_html_sample, 'html.parser')
        name = parser.extract_name(soup)
        assert name == "Casque Sony WH-1000XM5"

    def test_extract_image_from_html(self, cdiscount_html_sample):
        """Test image extraction from Cdiscount HTML."""
        parser = CdiscountParser()
        soup = BeautifulSoup(cdiscount_html_sample, 'html.parser')
        image = parser.extract_image(soup)
        assert image == "https://cdn.cdiscount.com/test.jpg"

    @pytest.mark.asyncio
    async def test_parse_full_workflow(self, cdiscount_html_sample):
        """Test complete Cdiscount parsing workflow."""
        parser = CdiscountParser()

        with patch('app.parsers.engine.ParserEngine.fetch_html', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = cdiscount_html_sample

            result = await parser.parse("https://www.cdiscount.com/product123")

            assert isinstance(result, ProductData)
            assert result.name == "Casque Sony WH-1000XM5"
            assert result.price == 299.99
            assert result.currency == "EUR"


# ============================================================================
# Fnac Parser Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.parsers
class TestFnacParser:
    """Test FnacParser."""

    def test_supported_domains(self):
        """Test Fnac supported domains."""
        parser = FnacParser()
        assert "fnac.com" in parser.supported_domains

    def test_extract_price_from_html(self, fnac_html_sample):
        """Test price extraction from Fnac HTML."""
        parser = FnacParser()
        soup = BeautifulSoup(fnac_html_sample, 'html.parser')
        price = parser.extract_price(soup)
        assert price == 319.99

    def test_extract_name_from_html(self, fnac_html_sample):
        """Test name extraction from Fnac HTML."""
        parser = FnacParser()
        soup = BeautifulSoup(fnac_html_sample, 'html.parser')
        name = parser.extract_name(soup)
        assert name == "Sony WH-1000XM5"

    def test_extract_image_from_html(self, fnac_html_sample):
        """Test image extraction from Fnac HTML."""
        parser = FnacParser()
        soup = BeautifulSoup(fnac_html_sample, 'html.parser')
        image = parser.extract_image(soup)
        assert image == "https://static.fnac.com/test.jpg"


# ============================================================================
# Boulanger Parser Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.parsers
class TestBoulangerParser:
    """Test BoulangerParser."""

    def test_supported_domains(self):
        """Test Boulanger supported domains."""
        parser = BoulangerParser()
        assert "boulanger.com" in parser.supported_domains

    def test_extract_price_from_html(self, boulanger_html_sample):
        """Test price extraction from Boulanger HTML."""
        parser = BoulangerParser()
        soup = BeautifulSoup(boulanger_html_sample, 'html.parser')
        price = parser.extract_price(soup)
        assert price == 329.99

    def test_extract_name_from_html(self, boulanger_html_sample):
        """Test name extraction from Boulanger HTML."""
        parser = BoulangerParser()
        soup = BeautifulSoup(boulanger_html_sample, 'html.parser')
        name = parser.extract_name(soup)
        assert name == "Sony WH-1000XM5 Noir"

    def test_extract_image_from_html(self, boulanger_html_sample):
        """Test image extraction from Boulanger HTML."""
        parser = BoulangerParser()
        soup = BeautifulSoup(boulanger_html_sample, 'html.parser')
        image = parser.extract_image(soup)
        assert image == "https://boulanger.scene7.com/test.jpg"


# ============================================================================
# Bol.com Parser Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.parsers
class TestBolcomParser:
    """Test BolcomParser."""

    def test_supported_domains(self):
        """Test Bol.com supported domains."""
        parser = BolcomParser()
        assert "bol.com" in parser.supported_domains

    def test_extract_price_from_html(self, bol_html_sample):
        """Test price extraction from Bol.com HTML."""
        parser = BolcomParser()
        soup = BeautifulSoup(bol_html_sample, 'html.parser')
        price = parser.extract_price(soup)
        assert price == 299.99

    def test_extract_name_from_html(self, bol_html_sample):
        """Test name extraction from Bol.com HTML."""
        parser = BolcomParser()
        soup = BeautifulSoup(bol_html_sample, 'html.parser')
        name = parser.extract_name(soup)
        assert name == "Sony WH-1000XM5"

    def test_extract_image_from_html(self, bol_html_sample):
        """Test image extraction from Bol.com HTML."""
        parser = BolcomParser()
        soup = BeautifulSoup(bol_html_sample, 'html.parser')
        image = parser.extract_image(soup)
        assert image == "https://media.bol.com/test.jpg"


# ============================================================================
# Coolblue Parser Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.parsers
class TestCoolblueParser:
    """Test CoolblueParser."""

    def test_supported_domains(self):
        """Test Coolblue supported domains."""
        parser = CoolblueParser()
        assert "coolblue.be" in parser.supported_domains

    def test_extract_price_from_html(self, coolblue_html_sample):
        """Test price extraction from Coolblue HTML."""
        parser = CoolblueParser()
        soup = BeautifulSoup(coolblue_html_sample, 'html.parser')
        price = parser.extract_price(soup)
        assert price == 339.99

    def test_extract_name_from_html(self, coolblue_html_sample):
        """Test name extraction from Coolblue HTML."""
        parser = CoolblueParser()
        soup = BeautifulSoup(coolblue_html_sample, 'html.parser')
        name = parser.extract_name(soup)
        assert name == "Sony WH-1000XM5 Zwart"

    def test_extract_image_from_html(self, coolblue_html_sample):
        """Test image extraction from Coolblue HTML."""
        parser = CoolblueParser()
        soup = BeautifulSoup(coolblue_html_sample, 'html.parser')
        image = parser.extract_image(soup)
        assert image == "https://image.coolblue.be/test.jpg"


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

@pytest.mark.unit
@pytest.mark.parsers
class TestParserErrorHandling:
    """Test parser error handling across all parsers."""

    @pytest.mark.parametrize("ParserClass", [
        AmazonParser,
        CdiscountParser,
        FnacParser,
        BoulangerParser,
        BolcomParser,
        CoolblueParser,
    ])
    def test_extract_price_with_invalid_content(self, ParserClass):
        """Test that all parsers handle invalid content gracefully."""
        parser = ParserClass()
        result = parser.extract_price(None)
        assert result is None

    @pytest.mark.parametrize("ParserClass", [
        AmazonParser,
        CdiscountParser,
        FnacParser,
        BoulangerParser,
        BolcomParser,
        CoolblueParser,
    ])
    def test_extract_name_with_invalid_content(self, ParserClass):
        """Test that all parsers handle invalid content for name extraction."""
        parser = ParserClass()
        result = parser.extract_name(None)
        assert result is None

    @pytest.mark.parametrize("ParserClass", [
        AmazonParser,
        CdiscountParser,
        FnacParser,
        BoulangerParser,
        BolcomParser,
        CoolblueParser,
    ])
    def test_extract_image_with_invalid_content(self, ParserClass):
        """Test that all parsers handle invalid content for image extraction."""
        parser = ParserClass()
        result = parser.extract_image(None)
        assert result is None

    @pytest.mark.parametrize("ParserClass", [
        CdiscountParser,
        FnacParser,
        BoulangerParser,
        BolcomParser,
        CoolblueParser,
    ])
    def test_extract_price_with_no_price_in_html(self, ParserClass, invalid_html_sample):
        """Test parsers return None when no price is found."""
        parser = ParserClass()
        soup = BeautifulSoup(invalid_html_sample, 'html.parser')
        price = parser.extract_price(soup)
        assert price is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("ParserClass,valid_url", [
        (AmazonParser, "https://www.amazon.fr/dp/B09XS7JWHH"),
        (CdiscountParser, "https://www.cdiscount.com/product"),
        (FnacParser, "https://www.fnac.com/product"),
        (BoulangerParser, "https://www.boulanger.com/product"),
        (BolcomParser, "https://www.bol.com/product"),
        (CoolblueParser, "https://www.coolblue.be/product"),
    ])
    async def test_parse_raises_error_on_invalid_url(self, ParserClass, valid_url):
        """Test that parsers raise ValueError on wrong domain."""
        parser = ParserClass()
        invalid_url = "https://www.wrongdomain.com/product"

        with pytest.raises(ValueError, match="not supported"):
            await parser.parse(invalid_url)
