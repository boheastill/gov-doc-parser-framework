"""TEMPLATE — copy this file to add a parser for a new source.

Steps to add a source (for contributors / agents):
  1. Copy this file to `parsers/<sourcename>.py`.
  2. Set `source_id` (usually the domain) and `url_patterns`.
  3. Implement `parse()`: read the page's structure (anchors / headings /
     CSS selectors) and build a Document of Sections + Articles.
  4. Add a fixture: `fixtures/<sourcename>/<sample>.html` (an offline copy).
  5. Add a test under `tests/` (assert title + stats + a sample article).
  6. Register the parser import in `parsers/__init__.py`.

Keep it pure: HTML in, Document out. No network, no disk, no globals.
Run `python cli.py fixtures/<sourcename>/<sample>.html --source <source_id>`
and make sure the validator reports zero issues before opening a PR.
"""
from __future__ import annotations

from bs4 import BeautifulSoup

from core.base import BaseParser
from core.registry import register
from core.schema import Article, Document, Section, slugify


# @register   # <-- uncomment when implemented
class TemplateParser(BaseParser):
    source_id = ""           # e.g. "example.com"
    url_patterns = ()        # e.g. ("example.com",)

    def parse(self, html: str, source_url: str = "") -> Document:
        soup = BeautifulSoup(html, "html.parser")
        doc = Document(title=soup.title.get_text(strip=True) if soup.title else "",
                       source_url=source_url)

        # Example skeleton: top-level headings -> Sections, sub-blocks -> Articles.
        # Replace selectors with whatever marks structure on YOUR source.
        for h2 in soup.select("h2"):
            section = Section(title=h2.get_text(strip=True))
            for block in []:                       # TODO: find this section's blocks
                section.add(Article(
                    title="", content="",
                    code=slugify(f"{doc.title}-{...}")))
            doc.add(section)

        return doc
