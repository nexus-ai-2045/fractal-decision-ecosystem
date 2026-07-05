#!/usr/bin/env python3
"""Check the human publication review packet without performing public actions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "PUBLICATION_REVIEW_PACKET.md"

REQUIRED_TERMS = (
    "Status: review packet only / no public action approved",
    "Repository: `nexus-ai-2045/fractal-decision-ecosystem`",
    "Current visibility: private",
    "Approved operation now: none",
    "External actions performed by this packet: false",
    "gh repo edit nexus-ai-2045/fractal-decision-ecosystem --visibility public",
    "target repository in `owner/name` form",
    "exact operation / command",
    "visible content summary",
    "README review",
    "LICENSE review",
    "SECURITY.md review",
    "PUBLIC_READY.md review",
    "personal path scan",
    "secret scan",
    "public-kernel diff manifest",
    "Patent Pending",
    "Do not make the repository public from this packet",
    "Do not treat local gate success as publication approval",
)


def evaluate() -> dict[str, object]:
    errors: list[str] = []
    if not PACKET.exists():
        errors.append("PUBLICATION_REVIEW_PACKET.md is missing")
        text = ""
    else:
        text = PACKET.read_text(encoding="utf-8")
    for term in REQUIRED_TERMS:
        if term not in text:
            errors.append(f"PUBLICATION_REVIEW_PACKET.md missing required term: {term}")
    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "approved_operation_now": "none",
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = evaluate()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"FDE HUMAN REVIEW PACKET CHECK {result['overall'].upper()}")
        print(f"external_actions_performed: {str(result['external_actions_performed']).lower()}")
        print(f"approved_operation_now: {result['approved_operation_now']}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
