"""BaseParser — the interface every source parser implements.

A parser is responsible for exactly one source (one website / document family).
It receives the raw HTML of one page (worked against offline) and returns a
`Document`. Keep parsers pure: HTML in, Document out, no network, no disk.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .schema import Document


class BaseParser(ABC):
    #: stable id for this source, usually its domain, e.g. "irishstatutebook.ie"
    source_id: str = ""
    #: url patterns this parser claims (substrings); used for auto-detection
    url_patterns: tuple[str, ...] = ()

    @abstractmethod
    def parse(self, html: str, source_url: str = "") -> Document:
        """Parse one page's HTML into a Document. Must be deterministic & offline."""
        raise NotImplementedError
