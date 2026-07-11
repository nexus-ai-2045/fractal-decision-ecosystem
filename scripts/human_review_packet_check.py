#!/usr/bin/env python3
"""人間向け公開レビューpacketを、public actionなしで検証する。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "PUBLICATION_REVIEW_PACKET.md"

REQUIRED_TERMS = (
    "状態: review packet のみ / public action 承認なし",
    "Repository: `nexus-ai-2045/fractal-decision-ecosystem`",
    "現在の visibility: public",
    "visibility 変更は実施済み",
    "以後の変更は再承認制",
    "現時点で承認された操作: なし",
    "この packet による external action 実行: false",
    "gh repo edit nexus-ai-2045/fractal-decision-ecosystem --visibility public",
    "target repository を `owner/name` form で確認する",
    "exact operation / command",
    "web上で visible になる内容を要約する",
    "README をレビューする",
    "LICENSE をレビューする",
    "SECURITY.md をレビューする",
    "PUBLIC_READY.md をレビューする",
    "personal path scan",
    "secret scan",
    "public-kernel diff manifest",
    "Patent Pending",
    "この packet から repository public 化を実行しない",
    "local gate success を publication approval として扱わない",
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
