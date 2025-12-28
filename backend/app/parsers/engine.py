from typing import Optional, Dict, Type
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
import logging
from .base import BaseParser, ProductData, ParserNotFoundError, ParserError
from .extractors import normalize_domain

logger = logging.getLogger(__name__)

class ParserEngine:
    """
    Main parser engine that selects and executes the appropriate parser
    """

    def __init__(self):
        self._parsers: Dict[str, Type[BaseParser]] = {}
        self._browser: Optional[Browser] = None

    def register_parser(self, parser_class: Type[BaseParser]):
        """
        Register a parser for specific domains

        Args:
            parser_class: Parser class to register
        """
        # Instantiate to get supported domains
        instance = parser_class()
        for domain in instance.supported_domains:
            self._parsers[domain.lower()] = parser_class
            logger.info(f"Registered parser {parser_class.__name__} for domain {domain}")

    def get_parser(self, url: str, config: Optional[Dict] = None) -> BaseParser:
        """
        Get appropriate parser for a URL

        Args:
            url: Product URL
            config: Optional parser configuration

        Returns:
            Parser instance

        Raises:
            ParserNotFoundError: If no parser found for domain
        """
        domain = normalize_domain(url)

        parser_class = self._parsers.get(domain)
        if not parser_class:
            raise ParserNotFoundError(f"No parser found for domain: {domain}")

        return parser_class(config=config)

    async def parse(self, url: str, config: Optional[Dict] = None) -> ProductData:
        """
        Parse a product page

        Args:
            url: Product URL
            config: Optional parser configuration

        Returns:
            ProductData with extracted information

        Raises:
            ParserError: If parsing fails
        """
        parser = self.get_parser(url, config)

        logger.info(f"Parsing {url} with {parser.__class__.__name__}")

        try:
            data = await parser.parse(url)
            logger.info(f"Successfully parsed {url}: price={data.price}, name={data.name[:50] if data.name else None}")
            return data
        except Exception as e:
            logger.error(f"Failed to parse {url}: {e}")
            raise ParserError(f"Parsing failed: {e}") from e

    async def fetch_html(self, url: str, use_playwright: bool = False, timeout: int = 30) -> str:
        """
        Fetch HTML content from URL

        Args:
            url: URL to fetch
            use_playwright: Whether to use Playwright (for JS-rendered sites)
            timeout: Request timeout in seconds

        Returns:
            HTML content

        Raises:
            ParserError: If fetch fails
        """
        if use_playwright:
            return await self._fetch_with_playwright(url, timeout)
        else:
            return await self._fetch_with_httpx(url, timeout)

    async def _fetch_with_httpx(self, url: str, timeout: int) -> str:
        """Fetch HTML with httpx (static content)"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as e:
                raise ParserError(f"HTTP error: {e}") from e

    async def _fetch_with_playwright(self, url: str, timeout: int) -> str:
        """Fetch HTML with Playwright (JS-rendered content)"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )

                await page.goto(url, wait_until='networkidle', timeout=timeout * 1000)
                html = await page.content()

                return html
            finally:
                await browser.close()

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML into BeautifulSoup object

        Args:
            html: HTML content

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')

# Global parser engine instance
parser_engine = ParserEngine()
