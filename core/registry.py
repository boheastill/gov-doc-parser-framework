"""Parser registry — map a source id (or URL) to its parser.

Usage:
    from core.registry import register, get_parser, detect

    @register
    class MyParser(BaseParser):
        source_id = "example.com"
        url_patterns = ("example.com",)
        ...

Parsers register themselves by being imported (see parsers/__init__.py).
"""
from __future__ import annotations

from typing import Optional, Type

from .base import BaseParser

_REGISTRY: dict[str, Type[BaseParser]] = {}


def register(cls: Type[BaseParser]) -> Type[BaseParser]:
    """Class decorator: add a parser to the registry under its source_id."""
    if not getattr(cls, "source_id", ""):
        raise ValueError(f"{cls.__name__} must set source_id")
    _REGISTRY[cls.source_id] = cls
    return cls


def get_parser(source_id: str) -> BaseParser:
    if source_id not in _REGISTRY:
        raise KeyError(f"no parser registered for source_id={source_id!r}. "
                       f"known: {sorted(_REGISTRY)}")
    return _REGISTRY[source_id]()


def detect(url: str) -> Optional[BaseParser]:
    """Pick a parser by matching url against each parser's url_patterns."""
    for cls in _REGISTRY.values():
        if any(pat in url for pat in cls.url_patterns):
            return cls()
    return None


def known_sources() -> list[str]:
    return sorted(_REGISTRY)
