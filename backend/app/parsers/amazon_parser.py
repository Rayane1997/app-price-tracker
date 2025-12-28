from typing import Optional, Any
from bs4 import BeautifulSoup
import re
from .base import BaseParser, ProductData, PriceNotFoundError
from .extractors import extract_price_from_text, clean_price_string, detect_currency
from .engine import ParserEngine
import logging

logger = logging.getLogger(__name__)

class AmazonParser(BaseParser):
    """
    Parser for Amazon.fr and Amazon.be

    Requires Playwright due to JavaScript rendering
    """

    @property
    def supported_domains(self) -> list[str]:
        return ['amazon.fr', 'amazon.be']

    @property
    def requires_javascript(self) -> bool:
        return True  # Amazon uses JS for price rendering

    async def parse(self, url: str) -> ProductData:
        """Parse Amazon product page"""
        if not self.validate_url(url):
            raise ValueError(f"URL {url} is not supported by AmazonParser")

        engine = ParserEngine()

        # Fetch HTML with Playwright
        self.logger.info(f"Fetching Amazon page: {url}")
        html = await engine.fetch_html(url, use_playwright=True, timeout=45)
        soup = engine.parse_html(html)

        # Extract data
        price = self.extract_price(soup)
        name = self.extract_name(soup)
        image = self.extract_image(soup)
        is_available = self._check_availability(soup)
        is_promo, promo_pct = self.detect_promo(soup)
        currency = detect_currency(html)

        self.logger.info(f"Amazon parsing complete: name='{name[:50] if name else None}...', price={price} {currency}, available={is_available}, promo={is_promo}")

        return ProductData(
            name=name,
            price=price,
            currency=currency,
            image_url=image,
            is_available=is_available,
            is_promo=is_promo,
            promo_percentage=promo_pct,
            raw_html=html[:1000],  # First 1000 chars for debugging
        )

    def extract_price(self, content: Any) -> Optional[float]:
        """Extract price from Amazon page"""
        if not isinstance(content, BeautifulSoup):
            return None

        # Amazon price selectors (in order of priority)
        price_selectors = [
            # Main price (most common)
            '.a-price.a-price-range .a-offscreen',
            '.a-price .a-offscreen',
            'span.a-price-whole',

            # Deal price
            '#priceblock_dealprice',
            '#priceblock_ourprice',
            '#priceblock_saleprice',

            # Mobile price
            '#price_inside_buybox',
            '.a-color-price',

            # Kindle/Digital
            '#kindle-price',
            '#digital-list-price',
        ]

        for selector in price_selectors:
            elements = content.select(selector)
            for element in elements:
                price_text = clean_price_string(element.get_text())
                price = extract_price_from_text(price_text)
                if price:
                    self.logger.info(f"Found Amazon price using selector: {selector} -> {price}")
                    return price

        # Fallback: search for price in JSON-LD structured data
        price = self._extract_price_from_json_ld(content)
        if price:
            return price

        self.logger.warning(f"Could not extract price from Amazon page")
        return None

    def _extract_price_from_json_ld(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from JSON-LD structured data"""
        scripts = soup.find_all('script', type='application/ld+json')

        for script in scripts:
            try:
                import json
                data = json.loads(script.string)

                # Handle Product schema
                if isinstance(data, dict) and data.get('@type') == 'Product':
                    offers = data.get('offers', {})
                    if isinstance(offers, dict):
                        price_str = offers.get('price')
                        if price_str:
                            self.logger.info(f"Found Amazon price in JSON-LD: {price_str}")
                            return float(price_str)
                    elif isinstance(offers, list) and offers:
                        price_str = offers[0].get('price')
                        if price_str:
                            self.logger.info(f"Found Amazon price in JSON-LD (array): {price_str}")
                            return float(price_str)
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                self.logger.debug(f"Failed to parse JSON-LD: {e}")
                continue

        return None

    def extract_name(self, content: Any) -> Optional[str]:
        """Extract product name from Amazon page"""
        if not isinstance(content, BeautifulSoup):
            return None

        # Amazon title selectors
        title_selectors = [
            '#productTitle',
            '#title',
            'h1.a-size-large',
            'h1 span#productTitle',
        ]

        for selector in title_selectors:
            element = content.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title:
                    self.logger.info(f"Found Amazon title using selector: {selector}")
                    return title

        self.logger.warning(f"Could not extract title from Amazon page")
        return None

    def extract_image(self, content: Any) -> Optional[str]:
        """Extract product image from Amazon page"""
        if not isinstance(content, BeautifulSoup):
            return None

        # Amazon image selectors
        image_selectors = [
            '#landingImage',
            '#imgBlkFront',
            '#main-image',
            'img#imgTagWrapperId',
            'img.a-dynamic-image',
        ]

        for selector in image_selectors:
            element = content.select_one(selector)
            if element:
                # Try data-old-hires first (high-res image)
                img_url = element.get('data-old-hires')
                if img_url:
                    self.logger.info(f"Found Amazon image (data-old-hires): {img_url[:80]}...")
                    return img_url

                # Try src
                img_url = element.get('src')
                if img_url:
                    self.logger.info(f"Found Amazon image (src): {img_url[:80]}...")
                    return img_url

                # Try data-a-dynamic-image (JSON with URLs)
                dynamic_img = element.get('data-a-dynamic-image')
                if dynamic_img:
                    try:
                        import json
                        urls = json.loads(dynamic_img)
                        if urls and isinstance(urls, dict):
                            # Get first URL
                            img_url = list(urls.keys())[0]
                            self.logger.info(f"Found Amazon image (data-a-dynamic-image): {img_url[:80]}...")
                            return img_url
                    except (json.JSONDecodeError, IndexError):
                        pass

        self.logger.warning(f"Could not extract image from Amazon page")
        return None

    def detect_promo(self, content: Any) -> tuple[bool, Optional[float]]:
        """Detect if product is on promotion on Amazon"""
        if not isinstance(content, BeautifulSoup):
            return False, None

        # Look for deal badge
        deal_badges = content.select('.dealBadge, .savingsPercentage, span.a-color-price')
        if deal_badges:
            for badge in deal_badges:
                text = badge.get_text()
                # Extract percentage like "-25%" or "Save 30%"
                match = re.search(r'(\d+)\s*%', text)
                if match:
                    percentage = float(match.group(1))
                    self.logger.info(f"Found Amazon promo badge: {percentage}% off")
                    return True, percentage

        # Look for strikethrough price (indicates discount)
        strikethrough = content.select('.a-text-strike, span.a-price.a-text-price')
        if strikethrough:
            self.logger.info(f"Found Amazon strikethrough price - product is on promo")
            return True, None

        return False, None

    def _check_availability(self, soup: BeautifulSoup) -> bool:
        """Check if product is available"""
        # Check for "Currently unavailable" or "Out of stock"
        unavailable_texts = [
            'currently unavailable',
            'out of stock',
            'actuellement indisponible',
            'en rupture de stock',
            'niet op voorraad',  # Dutch (BE)
        ]

        page_text = soup.get_text().lower()

        for text in unavailable_texts:
            if text in page_text:
                self.logger.info(f"Product unavailable: found '{text}'")
                return False

        # Check for availability badge
        availability = soup.select_one('#availability, #availability-brief')
        if availability:
            avail_text = availability.get_text().lower()
            for text in unavailable_texts:
                if text in avail_text:
                    self.logger.info(f"Product unavailable in availability section: '{text}'")
                    return False

        self.logger.info(f"Product is available")
        return True
