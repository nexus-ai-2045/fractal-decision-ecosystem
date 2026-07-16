#!/usr/bin/env python3
"""Check the FDE residual-zero goal contract without external actions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOAL = ROOT / "RESIDUAL_ZERO_GOAL_2026-07-05.md"

REQUIRED_TERMS = (
    "Status: historical goal completed / current public repository residual semantics retained",
    "implementation",
    "operation",
    "external/public",
    "Blocker Ledger",
    "Three-PR Plan",
    "PR 1: Team Formation + Residual Zero Goal",
    "PR 2: Contact Safety + Residual Operation Smoke",
    "PR 3: Public Boundary Package + Operational Closeout",
    "no_transport_contact_check.py",
    "verify_residual_zero_contract.py",
    "visual_html_smoke.py",
    "public_kernel_diff_manifest.py",
    "human_review_packet_check.py",
    "external actions remain false",
    "repository visibility is public; any further visibility change remains approval-gated",
)


def evaluate() -> dict[str, object]:
    errors: list[str] = []
    if not GOAL.exists():
        errors.append("RESIDUAL_ZERO_GOAL_2026-07-05.md is missing")
        text = ""
    else:
        text = GOAL.read_text(encoding="utf-8")

    for term in REQUIRED_TERMS:
        if term not in text:
            errors.append(f"Residual zero goal missing required term: {term}")

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "goal": {
            "scope": "public repository local implementation and operation residual-zero semantics",
            "status": "ready" if not errors else "blocked",
            "requires_human_review_before_merge": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = evaluate()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"FDE RESIDUAL ZERO GOAL CHECK {result['overall'].upper()}")
        print(f"external_actions_performed: {str(result['external_actions_performed']).lower()}")
        print(f"goal_status: {result['goal']['status']}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
