#!/usr/bin/env python3
"""Smoke-test visual.html review links and private/public boundary language."""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VISUAL = ROOT / "visual.html"

REQUIRED_TEXT = (
    "private local MVP は完了。public approval ではありません。",
    "MVP gate、roadmap gate、pre-publication gate",
    "未実装ロードマップ",
    "AI contact safety",
    "transportは実装しない",
    "Public kernel diff",
)

REQUIRED_HREFS = (
    "README.md",
    "ROADMAP.md",
    "OPERATIONAL_GUARANTEE.md",
    "PUBLIC_KERNEL_PLAN.md",
    "ai-contact-safety-contract.md",
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for name, value in attrs:
            if name == "href" and value:
                self.hrefs.append(value)


def evaluate() -> dict[str, object]:
    errors: list[str] = []
    if not VISUAL.exists():
        errors.append("visual.html is missing")
        text = ""
    else:
        text = VISUAL.read_text(encoding="utf-8")

    for term in REQUIRED_TEXT:
        if term not in text:
            errors.append(f"visual.html missing required text: {term}")

    parser = LinkParser()
    parser.feed(text)
    hrefs = set(parser.hrefs)
    for href in REQUIRED_HREFS:
        if href not in hrefs:
            errors.append(f"visual.html missing required href: {href}")
        elif href.endswith(".md") and not (ROOT / href).exists():
            errors.append(f"visual.html href target is missing: {href}")

    for href in hrefs:
        if href.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target = href.split("#", 1)[0]
        if target and not (ROOT / target).exists():
            errors.append(f"visual.html local href target is missing: {href}")

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "href_count": len(hrefs),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = evaluate()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"FDE VISUAL HTML SMOKE {result['overall'].upper()}")
        print(f"external_actions_performed: {str(result['external_actions_performed']).lower()}")
        print(f"href_count: {result['href_count']}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
