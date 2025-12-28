from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProductData:
    """Data extracted from a product page"""
    name: Optional[str] = None
    price: Optional[float] = None
    currency: str = "EUR"
    image_url: Optional[str] = None
    is_available: bool = True
    is_promo: bool = False
    promo_percentage: Optional[float] = None
    raw_html: Optional[str] = None
    parsed_at: datetime = None

    def __post_init__(self):
        if self.parsed_at is None:
            self.parsed_at = datetime.utcnow()

class ParserError(Exception):
    """Base exception for parser errors"""
    pass

class ParserNotFoundError(ParserError):
    """Raised when no parser is found for a domain"""
    pass

class PriceNotFoundError(ParserError):
    """Raised when price cannot be extracted"""
    pass

class BaseParser(ABC):
    """Abstract base class for all parsers"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize parser with optional configuration

        Args:
            config: Parser configuration (selectors, options, etc.)
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    @abstractmethod
    def supported_domains(self) -> list[str]:
        """List of domains this parser supports (e.g., ['amazon.fr', 'amazon.be'])"""
        pass

    @property
    @abstractmethod
    def requires_javascript(self) -> bool:
        """Whether this parser requires JavaScript rendering (Playwright)"""
        pass

    @abstractmethod
    async def parse(self, url: str) -> ProductData:
        """
        Parse a product page and extract data

        Args:
            url: Product page URL

        Returns:
            ProductData with extracted information

        Raises:
            ParserError: If parsing fails
        """
        pass

    @abstractmethod
    def extract_price(self, content: Any) -> Optional[float]:
        """
        Extract price from page content

        Args:
            content: HTML content (str or BeautifulSoup object)

        Returns:
            Price as float, or None if not found
        """
        pass

    @abstractmethod
    def extract_name(self, content: Any) -> Optional[str]:
        """
        Extract product name from page content

        Args:
            content: HTML content (str or BeautifulSoup object)

        Returns:
            Product name, or None if not found
        """
        pass

    def extract_image(self, content: Any) -> Optional[str]:
        """
        Extract product image URL from page content

        Args:
            content: HTML content (str or BeautifulSoup object)

        Returns:
            Image URL, or None if not found
        """
        return None

    def detect_promo(self, content: Any) -> tuple[bool, Optional[float]]:
        """
        Detect if product is on promotion

        Args:
            content: HTML content (str or BeautifulSoup object)

        Returns:
            Tuple of (is_promo, promo_percentage)
        """
        return False, None

    def validate_url(self, url: str) -> bool:
        """
        Validate that URL matches supported domains

        Args:
            url: URL to validate

        Returns:
            True if URL is valid for this parser
        """
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]

        return domain in self.supported_domains
