from .base import (
    BaseParser,
    ProductData,
    ParserError,
    ParserNotFoundError,
    PriceNotFoundError,
)
from .engine import ParserEngine, parser_engine
from .generic_parser import GenericParser
from .amazon_parser import AmazonParser
from .fr_sites_parsers import CdiscountParser, FnacParser, BoulangerParser
from .be_sites_parsers import BolcomParser, CoolblueParser
from . import extractors

# Import registry to auto-register parsers
from . import registry

__all__ = [
    "BaseParser",
    "ProductData",
    "ParserError",
    "ParserNotFoundError",
    "PriceNotFoundError",
    "ParserEngine",
    "parser_engine",
    "GenericParser",
    "AmazonParser",
    "CdiscountParser",
    "FnacParser",
    "BoulangerParser",
    "BolcomParser",
    "CoolblueParser",
    "extractors",
]
