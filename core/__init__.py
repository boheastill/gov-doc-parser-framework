"""Core framework: schema (output contract), base parser, registry, validator."""
from .base import BaseParser
from .registry import detect, get_parser, known_sources, register
from .schema import Article, Document, Section, slugify
from .validator import is_valid, validate

__all__ = [
    "BaseParser", "register", "get_parser", "detect", "known_sources",
    "Document", "Section", "Article", "slugify", "validate", "is_valid",
]
