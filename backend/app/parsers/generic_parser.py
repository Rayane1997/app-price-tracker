from typing import Optional, Any
from bs4 import BeautifulSoup
from .base import BaseParser, ProductData, PriceNotFoundError
from .extractors import extract_price_from_text, clean_price_string, detect_currency
from .engine import ParserEngine
import logging

logger = logging.getLogger(__name__)

class GenericParser(BaseParser):
    """
    Generic parser that uses CSS selectors from configuration
    Can be used for any site with proper configuration
    """

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)

        # Require configuration
        if not config:
            raise ValueError("GenericParser requires configuration with selectors")

        self.domain = config.get('domain')
        self.price_selectors = config.get('price_selectors', {})
        self.name_selectors = config.get('name_selectors', {})
        self.image_selectors = config.get('image_selectors', {})
        self.use_playwright = config.get('use_playwright', False)

    @property
    def supported_domains(self) -> list[str]:
        return [self.domain] if self.domain else []

    @property
    def requires_javascript(self) -> bool:
        return self.use_playwright

    async def parse(self, url: str) -> ProductData:
        """Parse product page using configured selectors"""
        engine = ParserEngine()

        # Fetch HTML
        html = await engine.fetch_html(url, use_playwright=self.use_playwright)
        soup = engine.parse_html(html)

        # Extract data
        price = self.extract_price(soup)
        name = self.extract_name(soup)
        image = self.extract_image(soup)
        currency = detect_currency(html)

        return ProductData(
            name=name,
            price=price,
            currency=currency,
            image_url=image,
            is_available=price is not None,
            raw_html=html[:1000],  # Store first 1000 chars for debugging
        )

    def extract_price(self, content: Any) -> Optional[float]:
        """Extract price using configured selectors"""
        if not isinstance(content, BeautifulSoup):
            return None

        # Try primary selector
        primary_selector = self.price_selectors.get('primary')
        if primary_selector:
            element = content.select_one(primary_selector)
            if element:
                price_text = clean_price_string(element.get_text())
                price = extract_price_from_text(price_text)
                if price:
                    return price

        # Try fallback selectors
        fallbacks = self.price_selectors.get('fallback', [])
        for selector in fallbacks:
            element = content.select_one(selector)
            if element:
                price_text = clean_price_string(element.get_text())
                price = extract_price_from_text(price_text)
                if price:
                    logger.info(f"Found price using fallback selector: {selector}")
                    return price

        logger.warning(f"Could not extract price for domain {self.domain}")
        return None

    def extract_name(self, content: Any) -> Optional[str]:
        """Extract product name using configured selectors"""
        if not isinstance(content, BeautifulSoup):
            return None

        # Try primary selector
        primary_selector = self.name_selectors.get('primary')
        if primary_selector:
            element = content.select_one(primary_selector)
            if element:
                return element.get_text().strip()

        # Try fallback selectors
        fallbacks = self.name_selectors.get('fallback', [])
        for selector in fallbacks:
            element = content.select_one(selector)
            if element:
                logger.info(f"Found name using fallback selector: {selector}")
                return element.get_text().strip()

        return None

    def extract_image(self, content: Any) -> Optional[str]:
        """Extract product image using configured selectors"""
        if not isinstance(content, BeautifulSoup):
            return None

        # Try primary selector
        primary_selector = self.image_selectors.get('primary')
        if primary_selector:
            element = content.select_one(primary_selector)
            if element:
                # Try src, data-src, srcset attributes
                for attr in ['src', 'data-src', 'data-lazy-src']:
                    url = element.get(attr)
                    if url:
                        return url

        return None
