#!/usr/bin/env python3
"""Run a parser against a local HTML copy and print / save structured JSON.

Examples:
    # auto-detect source from --url, validate, print JSON
    python cli.py fixtures/irishstatutebook/markets_act_2018.html \
        --url https://www.irishstatutebook.ie/eli/2018/act/25/enacted/en/print.html

    # force a source and write output to a file
    python cli.py page.html --source irishstatutebook.ie -o out.json
"""
from __future__ import annotations

import argparse
import json
import sys

import parsers  # noqa: F401  (registers all parsers)
from core.registry import detect, get_parser, known_sources
from core.validator import validate


def main() -> int:
    ap = argparse.ArgumentParser(description="Parse an offline HTML page into structured JSON.")
    ap.add_argument("html", help="path to a local HTML copy of the page")
    ap.add_argument("--url", default="", help="original source URL (stored + used to auto-detect)")
    ap.add_argument("--source", default="", help=f"force source id; known: {known_sources()}")
    ap.add_argument("-o", "--out", default="", help="write JSON here instead of stdout")
    ap.add_argument("--no-validate", action="store_true", help="skip structural validation")
    args = ap.parse_args()

    html = open(args.html, encoding="utf-8", errors="ignore").read()

    parser = get_parser(args.source) if args.source else detect(args.url)
    if parser is None:
        print(f"error: could not pick a parser. pass --source (known: {known_sources()})",
              file=sys.stderr)
        return 2

    doc = parser.parse(html, args.url)

    if not args.no_validate:
        issues = validate(doc)
        if issues:
            print("VALIDATION FAILED:", file=sys.stderr)
            for i in issues:
                print(f"  - {i}", file=sys.stderr)
            return 1
        print(f"validation: OK ({doc.stats()})", file=sys.stderr)

    payload = json.dumps(doc.to_dict(), ensure_ascii=False, indent=2)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(payload)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
