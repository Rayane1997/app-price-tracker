from typing import Optional, Any
from bs4 import BeautifulSoup
import re
from .base import BaseParser, ProductData
from .extractors import extract_price_from_text, clean_price_string, detect_currency
from .engine import ParserEngine
import logging

logger = logging.getLogger(__name__)


class BolcomParser(BaseParser):
    """Parser for Bol.com - Static HTML only"""

    @property
    def supported_domains(self) -> list[str]:
        return ['bol.com', 'www.bol.com']

    @property
    def requires_javascript(self) -> bool:
        return False

    async def parse(self, url: str) -> ProductData:
        """Parse Bol.com product page"""
        if not self.validate_url(url):
            raise ValueError(f"URL {url} is not supported by BolcomParser")

        engine = ParserEngine()
        self.logger.info(f"Fetching Bol.com page: {url}")
        html = await engine.fetch_html(url, use_playwright=False)
        soup = engine.parse_html(html)

        price = self.extract_price(soup)
        name = self.extract_name(soup)
        image = self.extract_image(soup)
        currency = detect_currency(html)

        self.logger.info(f"Bol.com parsing complete: name='{name[:50] if name else None}...', price={price} {currency}")

        return ProductData(
            name=name,
            price=price,
            currency=currency,
            image_url=image,
            raw_html=html[:1000],
        )

    def extract_price(self, content: Any) -> Optional[float]:
        """Extract price from Bol.com page"""
        if not isinstance(content, BeautifulSoup):
            return None

        price_selectors = [
            '.promo-price',
            '.price-block__highlight',
            'span[data-test="price"]',
            '.product-price',
            'span.price',
        ]

        for selector in price_selectors:
            elements = content.select(selector)
            for element in elements:
                price_text = clean_price_string(element.get_text())
                price = extract_price_from_text(price_text)
                if price:
                    self.logger.info(f"Found Bol.com price using selector: {selector} -> {price}")
                    return price

        self.logger.warning("Could not extract price from Bol.com page")
        return None

    def extract_name(self, content: Any) -> Optional[str]:
        """Extract product name from Bol.com page"""
        if not isinstance(content, BeautifulSoup):
            return None

        name_selectors = [
            'h1[data-test="title"]',
            'h1.page-heading',
            'h1[itemprop="name"]',
            'h1.product-title',
            'h1',
        ]

        for selector in name_selectors:
            element = content.select_one(selector)
            if element:
                name = element.get_text().strip()
                if name and len(name) > 5:
                    self.logger.info(f"Found Bol.com name using selector: {selector}")
                    return name

        self.logger.warning("Could not extract name from Bol.com page")
        return None

    def extract_image(self, content: Any) -> Optional[str]:
        """Extract product image from Bol.com page"""
        if not isinstance(content, BeautifulSoup):
            return None

        image_selectors = [
            'img.js_selected_image',
            'img[data-test="image"]',
            'img[itemprop="image"]',
            'img.main-image',
            'img.product-image',
        ]

        for selector in image_selectors:
            element = content.select_one(selector)
            if element:
                img_url = element.get('src') or element.get('data-src')
                if img_url:
                    self.logger.info(f"Found Bol.com image: {img_url[:80]}...")
                    return img_url

        self.logger.warning("Could not extract image from Bol.com page")
        return None


class CoolblueParser(BaseParser):
    """Parser for Coolblue.be - Static HTML only"""

    @property
    def supported_domains(self) -> list[str]:
        return ['coolblue.be', 'www.coolblue.be']

    @property
    def requires_javascript(self) -> bool:
        return False

    async def parse(self, url: str) -> ProductData:
        """Parse Coolblue.be product page"""
        if not self.validate_url(url):
            raise ValueError(f"URL {url} is not supported by CoolblueParser")

        engine = ParserEngine()
        self.logger.info(f"Fetching Coolblue page: {url}")
        html = await engine.fetch_html(url, use_playwright=False)
        soup = engine.parse_html(html)

        price = self.extract_price(soup)
        name = self.extract_name(soup)
        image = self.extract_image(soup)
        currency = detect_currency(html)

        self.logger.info(f"Coolblue parsing complete: name='{name[:50] if name else None}...', price={price} {currency}")

        return ProductData(
            name=name,
            price=price,
            currency=currency,
            image_url=image,
            raw_html=html[:1000],
        )

    def extract_price(self, content: Any) -> Optional[float]:
        """Extract price from Coolblue page"""
        if not isinstance(content, BeautifulSoup):
            return None

        price_selectors = [
            '.sales-price__current',
            '.product-price',
            '[data-test="price"]',
            'span[itemprop="price"]',
            '.price',
        ]

        for selector in price_selectors:
            elements = content.select(selector)
            for element in elements:
                price_text = clean_price_string(element.get_text())
                price = extract_price_from_text(price_text)
                if price:
                    self.logger.info(f"Found Coolblue price using selector: {selector} -> {price}")
                    return price

        self.logger.warning("Could not extract price from Coolblue page")
        return None

    def extract_name(self, content: Any) -> Optional[str]:
        """Extract product name from Coolblue page"""
        if not isinstance(content, BeautifulSoup):
            return None

        name_selectors = [
            'h1.product-name',
            'h1[data-test="title"]',
            'h1[itemprop="name"]',
            'h1.product-title',
            'h1',
        ]

        for selector in name_selectors:
            element = content.select_one(selector)
            if element:
                name = element.get_text().strip()
                if name and len(name) > 5:
                    self.logger.info(f"Found Coolblue name using selector: {selector}")
                    return name

        self.logger.warning("Could not extract name from Coolblue page")
        return None

    def extract_image(self, content: Any) -> Optional[str]:
        """Extract product image from Coolblue page"""
        if not isinstance(content, BeautifulSoup):
            return None

        image_selectors = [
            'img.main-image',
            'img[itemprop="image"]',
            'img[data-test="image"]',
            'img.product-image',
            'img.primary-image',
        ]

        for selector in image_selectors:
            element = content.select_one(selector)
            if element:
                img_url = element.get('src') or element.get('data-src')
                if img_url:
                    self.logger.info(f"Found Coolblue image: {img_url[:80]}...")
                    return img_url

        self.logger.warning("Could not extract image from Coolblue page")
        return None
