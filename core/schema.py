"""Output contract: the structured-document tree every parser must emit.

A parsed document is a tree of two node kinds:
  - Section  : a container (Part / Chapter / ...) with children
  - Article  : a leaf carrying actual text content

`Document.to_dict()` is the single source of truth for the JSON shape that the
validator checks and the client's pipeline ingests. Keep it stable.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Union


def slugify(text: str) -> str:
    """url-safe lowercase slug, e.g. 'Short title' -> 'short-title'."""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


@dataclass
class Article:
    """A leaf node holding text content."""
    title: str
    content: str
    code: str = ""
    type: str = "article"

    def to_dict(self) -> dict:
        return {"type": "article", "title": self.title,
                "code": self.code, "content": self.content}


@dataclass
class Section:
    """A container node (Part / Chapter / ...)."""
    title: str
    children: list[Union["Section", Article]] = field(default_factory=list)
    type: str = "section"

    def add(self, node: Union["Section", Article]) -> None:
        self.children.append(node)

    def to_dict(self) -> dict:
        return {"type": "section", "title": self.title,
                "children": [c.to_dict() for c in self.children]}


@dataclass
class Document:
    """Root of a parsed document."""
    title: str
    source_url: str = ""
    type: str = "Act"
    status: str = "active"
    sections: list[Union[Section, Article]] = field(default_factory=list)

    def add(self, node: Union[Section, Article]) -> None:
        self.sections.append(node)

    def stats(self) -> dict:
        def walk(nodes):
            sec = art = 0
            for n in nodes:
                if isinstance(n, Section):
                    sec += 1
                    s2, a2 = walk(n.children)
                    sec += s2
                    art += a2
                else:
                    art += 1
            return sec, art
        s, a = walk(self.sections)
        return {"sections": s, "articles": a}

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "type": self.type,
            "status": self.status,
            "source_url": self.source_url,
            "sections": [n.to_dict() for n in self.sections],
            "stats": self.stats(),
        }
