"""Structural tests for the irishstatutebook parser against the reference page.

Asserts the parsed tree matches the client's published preview for the
Markets in Financial Instruments Act 2018 (sections: 3, articles: 10).
"""
import pathlib

import parsers  # noqa: F401  (registers parsers)
from core.registry import get_parser
from core.validator import validate

FIXTURE = pathlib.Path(__file__).parent.parent / "fixtures" / "irishstatutebook" / "markets_act_2018.html"
URL = "https://www.irishstatutebook.ie/eli/2018/act/25/enacted/en/print.html"


def _doc():
    html = FIXTURE.read_text(encoding="utf-8", errors="ignore")
    return get_parser("irishstatutebook.ie").parse(html, URL)


def test_title():
    assert _doc().title == "Markets in Financial Instruments Act 2018"


def test_stats_match_preview():
    assert _doc().stats() == {"sections": 3, "articles": 10}


def test_intro_long_title():
    intro = _doc().sections[0]
    assert intro.title == "Introductory Text"
    assert intro.content.startswith("An Act to make")


def test_first_part_articles():
    doc = _doc()
    part1 = doc.sections[1]
    assert part1.title == "PART 1 Preliminary and General"
    titles = [a.title for a in part1.children]
    assert titles == ["Short title", "Expenses", "Repeal"]


def test_passes_validation():
    assert validate(_doc()) == []


def test_article_codes_include_section_path():
    doc = _doc()
    part1 = doc.sections[1]
    codes = [a.code for a in part1.children]
    # Codes must include the section slug between doc slug and article slug
    assert codes == [
        "markets-in-financial-instruments-act-2018-part-1-preliminary-and-general-short-title",
        "markets-in-financial-instruments-act-2018-part-1-preliminary-and-general-expenses",
        "markets-in-financial-instruments-act-2018-part-1-preliminary-and-general-repeal",
    ]
