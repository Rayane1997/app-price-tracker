"""
Parser registry - Registers all parsers with the engine
"""
from .engine import parser_engine
from .amazon_parser import AmazonParser
from .fr_sites_parsers import CdiscountParser, FnacParser, BoulangerParser
from .be_sites_parsers import BolcomParser, CoolblueParser
import logging

logger = logging.getLogger(__name__)

def register_all_parsers():
    """Register all available parsers with the global parser engine"""
    parsers = [
        AmazonParser,
        CdiscountParser,
        FnacParser,
        BoulangerParser,
        BolcomParser,
        CoolblueParser,
    ]

    for parser_class in parsers:
        try:
            parser_engine.register_parser(parser_class)
        except Exception as e:
            logger.error(f"Failed to register parser {parser_class.__name__}: {e}")

# Auto-register on import
register_all_parsers()
