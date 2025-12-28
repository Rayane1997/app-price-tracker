from typing import Optional, Any
from bs4 import BeautifulSoup
import re
from .base import BaseParser, ProductData
from .extractors import extract_price_from_text, clean_price_string, detect_currency
from .engine import ParserEngine
import logging

logger = logging.getLogger(__name__)


class CdiscountParser(BaseParser):
    """Parser for Cdiscount.com - Static HTML only"""

    @property
    def supported_domains(self) -> list[str]:
        return ['cdiscount.com', 'www.cdiscount.com']

    @property
    def requires_javascript(self) -> bool:
        return False

    async def parse(self, url: str) -> ProductData:
        """Parse Cdiscount product page"""
        if not self.validate_url(url):
            raise ValueError(f"URL {url} is not supported by CdiscountParser")

        engine = ParserEngine()
        self.logger.info(f"Fetching Cdiscount page: {url}")
        html = await engine.fetch_html(url, use_playwright=False)
        soup = engine.parse_html(html)

        price = self.extract_price(soup)
        name = self.extract_name(soup)
        image = self.extract_image(soup)
        currency = detect_currency(html)

        self.logger.info(f"Cdiscount parsing complete: name='{name[:50] if name else None}...', price={price} {currency}")

        return ProductData(
            name=name,
            price=price,
            currency=currency,
            image_url=image,
            raw_html=html[:1000],
        )

    def extract_price(self, content: Any) -> Optional[float]:
        """Extract price from Cdiscount page"""
        if not isinstance(content, BeautifulSoup):
            return None

        price_selectors = [
            '.fpPrice',
            'span.price',
            '.hideFromPro',
            '.product-price',
            'span[itemprop="price"]',
        ]

        for selector in price_selectors:
            elements = content.select(selector)
            for element in elements:
                price_text = clean_price_string(element.get_text())
                price = extract_price_from_text(price_text)
                if price:
                    self.logger.info(f"Found Cdiscount price using selector: {selector} -> {price}")
                    return price

        self.logger.warning("Could not extract price from Cdiscount page")
        return None

    def extract_name(self, content: Any) -> Optional[str]:
        """Extract product name from Cdiscount page"""
        if not isinstance(content, BeautifulSoup):
            return None

        name_selectors = [
            'h1[itemprop="name"]',
            '.fpDesCol h1',
            'h1.product-title',
            'h1',
        ]

        for selector in name_selectors:
            element = content.select_one(selector)
            if element:
                name = element.get_text().strip()
                if name and len(name) > 5:
                    self.logger.info(f"Found Cdiscount name using selector: {selector}")
                    return name

        self.logger.warning("Could not extract name from Cdiscount page")
        return None

    def extract_image(self, content: Any) -> Optional[str]:
        """Extract product image from Cdiscount page"""
        if not isinstance(content, BeautifulSoup):
            return None

        image_selectors = [
            'img.ProductMainImage',
            'img[itemprop="image"]',
            'img.main-image',
            'img.product-image',
        ]

        for selector in image_selectors:
            element = content.select_one(selector)
            if element:
                img_url = element.get('src') or element.get('data-src')
                if img_url:
                    self.logger.info(f"Found Cdiscount image: {img_url[:80]}...")
                    return img_url

        self.logger.warning("Could not extract image from Cdiscount page")
        return None


class FnacParser(BaseParser):
    """Parser for Fnac.com - Static HTML only"""

    @property
    def supported_domains(self) -> list[str]:
        return ['fnac.com', 'www.fnac.com']

    @property
    def requires_javascript(self) -> bool:
        return False

    async def parse(self, url: str) -> ProductData:
        """Parse Fnac product page"""
        if not self.validate_url(url):
            raise ValueError(f"URL {url} is not supported by FnacParser")

        engine = ParserEngine()
        self.logger.info(f"Fetching Fnac page: {url}")
        html = await engine.fetch_html(url, use_playwright=False)
        soup = engine.parse_html(html)

        price = self.extract_price(soup)
        name = self.extract_name(soup)
        image = self.extract_image(soup)
        currency = detect_currency(html)

        self.logger.info(f"Fnac parsing complete: name='{name[:50] if name else None}...', price={price} {currency}")

        return ProductData(
            name=name,
            price=price,
            currency=currency,
            image_url=image,
            raw_html=html[:1000],
        )

    def extract_price(self, content: Any) -> Optional[float]:
        """Extract price from Fnac page"""
        if not isinstance(content, BeautifulSoup):
            return None

        price_selectors = [
            '.f-buyBox-price-value',
            '.Price--current',
            '.ProductOffers-price',
            'span[itemprop="price"]',
            '.product-price',
        ]

        for selector in price_selectors:
            elements = content.select(selector)
            for element in elements:
                price_text = clean_price_string(element.get_text())
                price = extract_price_from_text(price_text)
                if price:
                    self.logger.info(f"Found Fnac price using selector: {selector} -> {price}")
                    return price

        self.logger.warning("Could not extract price from Fnac page")
        return None

    def extract_name(self, content: Any) -> Optional[str]:
        """Extract product name from Fnac page"""
        if not isinstance(content, BeautifulSoup):
            return None

        name_selectors = [
            'h1.f-productHeader-Title',
            'h1[itemprop="name"]',
            'h1.product-title',
            'h1',
        ]

        for selector in name_selectors:
            element = content.select_one(selector)
            if element:
                name = element.get_text().strip()
                if name and len(name) > 5:
                    self.logger.info(f"Found Fnac name using selector: {selector}")
                    return name

        self.logger.warning("Could not extract name from Fnac page")
        return None

    def extract_image(self, content: Any) -> Optional[str]:
        """Extract product image from Fnac page"""
        if not isinstance(content, BeautifulSoup):
            return None

        image_selectors = [
            'img.Picture-img',
            'img[itemprop="image"]',
            'img.main-image',
            'img.product-image',
        ]

        for selector in image_selectors:
            element = content.select_one(selector)
            if element:
                img_url = element.get('src') or element.get('data-src')
                if img_url:
                    self.logger.info(f"Found Fnac image: {img_url[:80]}...")
                    return img_url

        self.logger.warning("Could not extract image from Fnac page")
        return None


class BoulangerParser(BaseParser):
    """Parser for Boulanger.com - Static HTML only"""

    @property
    def supported_domains(self) -> list[str]:
        return ['boulanger.com', 'www.boulanger.com']

    @property
    def requires_javascript(self) -> bool:
        return False

    async def parse(self, url: str) -> ProductData:
        """Parse Boulanger product page"""
        if not self.validate_url(url):
            raise ValueError(f"URL {url} is not supported by BoulangerParser")

        engine = ParserEngine()
        self.logger.info(f"Fetching Boulanger page: {url}")
        html = await engine.fetch_html(url, use_playwright=False)
        soup = engine.parse_html(html)

        price = self.extract_price(soup)
        name = self.extract_name(soup)
        image = self.extract_image(soup)
        currency = detect_currency(html)

        self.logger.info(f"Boulanger parsing complete: name='{name[:50] if name else None}...', price={price} {currency}")

        return ProductData(
            name=name,
            price=price,
            currency=currency,
            image_url=image,
            raw_html=html[:1000],
        )

    def extract_price(self, content: Any) -> Optional[float]:
        """Extract price from Boulanger page"""
        if not isinstance(content, BeautifulSoup):
            return None

        price_selectors = [
            '.price-sales',
            '.product-price',
            'span[itemprop="price"]',
            '.current-price',
            '.sale-price',
        ]

        for selector in price_selectors:
            elements = content.select(selector)
            for element in elements:
                price_text = clean_price_string(element.get_text())
                price = extract_price_from_text(price_text)
                if price:
                    self.logger.info(f"Found Boulanger price using selector: {selector} -> {price}")
                    return price

        self.logger.warning("Could not extract price from Boulanger page")
        return None

    def extract_name(self, content: Any) -> Optional[str]:
        """Extract product name from Boulanger page"""
        if not isinstance(content, BeautifulSoup):
            return None

        name_selectors = [
            'h1.title',
            'h1[itemprop="name"]',
            'h1.product-title',
            'h1',
        ]

        for selector in name_selectors:
            element = content.select_one(selector)
            if element:
                name = element.get_text().strip()
                if name and len(name) > 5:
                    self.logger.info(f"Found Boulanger name using selector: {selector}")
                    return name

        self.logger.warning("Could not extract name from Boulanger page")
        return None

    def extract_image(self, content: Any) -> Optional[str]:
        """Extract product image from Boulanger page"""
        if not isinstance(content, BeautifulSoup):
            return None

        image_selectors = [
            'img.main-image',
            'img[itemprop="image"]',
            'img.product-image',
            'img.primary-image',
        ]

        for selector in image_selectors:
            element = content.select_one(selector)
            if element:
                img_url = element.get('src') or element.get('data-src')
                if img_url:
                    self.logger.info(f"Found Boulanger image: {img_url[:80]}...")
                    return img_url

        self.logger.warning("Could not extract image from Boulanger page")
        return None
