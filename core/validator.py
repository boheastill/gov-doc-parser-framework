"""Validator — mirrors the client's "automated validators + quick review" gate.

Run it on a parsed Document before submitting. Returns a list of human-readable
issues; an empty list means the document passes structural validation.

This is intentionally strict: a parser that produces an empty article or a
duplicate code is a parser that will fail review, so catch it here first.
"""
from __future__ import annotations

from .schema import Article, Document, Section


def validate(doc: Document) -> list[str]:
    issues: list[str] = []

    if not doc.title or not doc.title.strip():
        issues.append("document title is empty")
    if not doc.source_url:
        issues.append("document source_url is empty")
    if not doc.sections:
        issues.append("document has no sections/articles")

    codes: dict[str, int] = {}

    def walk(node, path: str):
        if isinstance(node, Section):
            if not node.title.strip():
                issues.append(f"{path}: section has empty title")
            if not node.children:
                issues.append(f"{path}: section '{node.title}' has no children")
            for i, child in enumerate(node.children):
                walk(child, f"{path}/{i}")
        elif isinstance(node, Article):
            if not node.title.strip():
                issues.append(f"{path}: article has empty title")
            if not node.content.strip():
                issues.append(f"{path}: article '{node.title}' has empty content")
            if node.code:
                codes[node.code] = codes.get(node.code, 0) + 1

    for i, node in enumerate(doc.sections):
        walk(node, f"sections/{i}")

    for code, n in codes.items():
        if n > 1:
            issues.append(f"duplicate article code '{code}' appears {n} times")

    return issues


def is_valid(doc: Document) -> bool:
    return not validate(doc)
