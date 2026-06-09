"""Parser for irishstatutebook.ie statute *print* pages.

These pages carry almost no semantic CSS classes, but they use a stable anchor
convention that maps 1:1 onto the document tree — so we point selectors at the
page's own structural markers (the brief's "CSS selectors at headings/body"):

    <a name="partN">     a Part              -> Section (container)
    <a name="secN">      a numbered section  -> Article; its title is the <b>
                                                in the <p> right after the anchor
    <a name="sN._pM">    paragraph M of secN -> body text appended to that Article

The statute's long title (the "An Act to ..." text) is not in a <p>; it lives in
the page's JSON-LD metadata (`schema:description`), which we read for the
Introductory Text.

Reference output (this exact page) matches the client's preview:
    title = "Markets in Financial Instruments Act 2018"
    stats = {sections: 3, articles: 10}
"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup

from core.base import BaseParser
from core.registry import register
from core.schema import Article, Document, Section, slugify

_PART = re.compile(r"part\d+")
_SEC = re.compile(r"sec\d+")
_PARA = re.compile(r"s\d+\._p\d+")


def _text(node) -> str:
    if node is None:
        return ""
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()


@register
class IrishStatuteBookParser(BaseParser):
    source_id = "irishstatutebook.ie"
    url_patterns = ("irishstatutebook.ie",)

    def parse(self, html: str, source_url: str = "") -> Document:
        soup = BeautifulSoup(html, "html.parser")

        # --- title: h1 minus its "Permanent Page URL" dropdown ---
        h1 = soup.find("h1")
        if h1:
            for junk in h1.find_all("div"):
                junk.extract()
        title = _text(h1) or (soup.title.get_text(strip=True) if soup.title else "")
        doc = Document(title=title, source_url=source_url)
        doc_slug = slugify(title)

        # --- Introductory Text: long title from JSON-LD metadata ---
        m = re.search(r'"schema:description":\s*"((?:[^"\\]|\\.)*)"', html)
        if m:
            long_title = re.sub(r"\s+", " ",
                                m.group(1).encode().decode("unicode_escape")).strip()
            doc.add(Article(title="Introductory Text", content=long_title,
                            code=f"{doc_slug}-introductory-text"))

        # --- walk the anchors in document order, building the tree ---
        current_part: Section | None = None
        current_article: Article | None = None

        for a in soup.find_all("a", attrs={"name": True}):
            name = a.get("name", "")
            if _PART.fullmatch(name):
                p1 = a.find_next("p")
                part_title = _text(p1)
                # The subtitle (e.g. "Preliminary and General") lives in
                # the next sibling <p> with a <span class="smallcaps">.
                p2 = p1.find_next_sibling("p") if p1 else None
                if p2 and p2.find("span", class_="smallcaps"):
                    part_title += " " + _text(p2)
                current_part = Section(title=part_title)
                doc.add(current_part)
                current_article = None
            elif _SEC.fullmatch(name):
                art_title = _text(a.find_next("p"))
                section_slug = slugify(current_part.title) if current_part else ""
                code_prefix = f"{doc_slug}-{section_slug}" if section_slug else doc_slug
                current_article = Article(
                    title=art_title, content="",
                    code=f"{code_prefix}-{slugify(art_title)}")
                (current_part.add if current_part else doc.add)(current_article)
            elif _PARA.fullmatch(name):
                para = _text(a.find_next("p"))
                if current_article is not None and para:
                    sep = "\n\n" if current_article.content else ""
                    current_article.content += sep + para

        return doc
