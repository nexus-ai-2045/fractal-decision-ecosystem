#!/usr/bin/env python3
"""Verify that residual-zero claims keep implementation, operation, and public blockers separate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.residual_zero_goal_check import evaluate as evaluate_goal

REQUIRED_OPERATIONAL_TERMS = (
    "状態: private repository 運用として保証済み",
    "実装残務: なし",
    "運用残務: なし",
    "public release 残務: 人間承認が必要",
    "現在の visibility: private",
    "この保証は repository の public 化を承認しません",
)

REQUIRED_MVP_TERMS = (
    "MVP status: complete for private local gate",
    "Repository visibility: private",
    "No external publication action performed",
    "Next milestone: publication approval only if public release is requested",
)

REQUIRED_GOAL_TERMS = (
    "implementation",
    "operation",
    "external/public",
    "approval-gated blocker",
    "external actions remain false",
)


def _check_terms(path: Path, terms: tuple[str, ...], errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing file: {path.relative_to(ROOT).as_posix()}")
        return
    text = path.read_text(encoding="utf-8")
    for term in terms:
        if term not in text:
            errors.append(f"{path.relative_to(ROOT).as_posix()} missing required term: {term}")


def evaluate() -> dict[str, object]:
    errors: list[str] = []
    goal = evaluate_goal()
    if goal["overall"] != "ok":
        errors.extend(str(error) for error in goal["errors"])

    _check_terms(ROOT / "OPERATIONAL_GUARANTEE.md", REQUIRED_OPERATIONAL_TERMS, errors)
    _check_terms(ROOT / "MVP_STATUS.md", REQUIRED_MVP_TERMS, errors)
    _check_terms(ROOT / "RESIDUAL_ZERO_GOAL_2026-07-05.md", REQUIRED_GOAL_TERMS, errors)

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "residual_zero_scope": "private local implementation and operation only",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = evaluate()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"FDE RESIDUAL ZERO CONTRACT CHECK {result['overall'].upper()}")
        print(f"external_actions_performed: {str(result['external_actions_performed']).lower()}")
        print(f"residual_zero_scope: {result['residual_zero_scope']}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
