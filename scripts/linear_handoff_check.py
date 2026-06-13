#!/usr/bin/env python3
"""Check the optional local Linear handoff packet without external writes."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "LINEAR_EXPORT.md",
    "LINEAR_CREATE_MANUAL.md",
    "LINEAR_ISSUE_RECORD.md",
    "TODO_FDE_PUBLIC_KERNEL_RIGHTS.md",
)

REQUIRED_PACKET_TERMS = (
    "optional local handoff packet",
    "この issue は、公開・patent filing・外部 submit・GitHub visibility 変更の承認として扱わない",
    "Repository visibility は private のまま",
    "External publication / release / announcement は未実行",
    "Patent filing は未実行",
    "Inventor decision: user-confirmed sole inventor",
    "Owner / assignee decision: user owner, no assignee",
    "Filing strategy: public disclosure 前に self-file defensive provisional patent application",
    "Linear は必須ではなく、使う場合だけ手動作成する",
    "python scripts\\mvp_gate_check.py",
    "Linear を使う場合だけ",
    "LINEAR_ISSUE_RECORD.md",
)

REQUIRED_MANUAL_TERMS = (
    "外部 write action への別途明示承認なしに",
    "LINEAR_EXPORT.md",
    "LINEAR_ISSUE_RECORD.md",
    "This Is Not Approval For",
    "Codex による connector / browser / API submit",
)

REQUIRED_RECORD_TERMS = (
    "optional; no Linear issue required for local FDE operation",
    "Linear issue ID: N/A unless used",
    "Linear issue URL: N/A unless used",
    "publication、patent filing、connector submission、GitHub visibility change の承認ではない",
    "If used, issue description は `LINEAR_EXPORT.md` から貼った",
)

REQUIRED_TODO_TERMS = (
    "Linear issue creation is optional, not required for local FDE operation",
    "If used, Linear issue を手動作成する",
    "If used, Linear issue identifier / URL を `LINEAR_ISSUE_RECORD.md` に記録する",
    "Defensive provisional patent application を public disclosure 前に filing する方針を決める",
    "Next milestone: provisional filing execution",
    "Exact repository への explicit current-conversation approval なしに GitHub repository visibility を変更しない",
)


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def require_terms(errors: list[str], relpath: str, terms: tuple[str, ...]) -> None:
    text = read(relpath)
    for term in terms:
        if term not in text:
            errors.append(f"{relpath} missing required term: {term}")


def evaluate() -> dict[str, object]:
    errors: list[str] = []
    for relpath in REQUIRED_FILES:
        if not (ROOT / relpath).exists():
            errors.append(f"missing required file: {relpath}")

    if not errors:
        require_terms(errors, "LINEAR_EXPORT.md", REQUIRED_PACKET_TERMS)
        require_terms(errors, "LINEAR_CREATE_MANUAL.md", REQUIRED_MANUAL_TERMS)
        require_terms(errors, "LINEAR_ISSUE_RECORD.md", REQUIRED_RECORD_TERMS)
        require_terms(errors, "TODO_FDE_PUBLIC_KERNEL_RIGHTS.md", REQUIRED_TODO_TERMS)

    return {
        "overall": "ok" if not errors else "error",
        "error": len(errors),
        "errors": errors,
        "external_actions_performed": False,
        "handoff_status": "optional_packet_ready" if not errors else "blocked",
        "not_guaranteed_by_local_repo": [
            "patent filing submission",
            "filing receipt / application number preservation",
            "GitHub repository visibility change approval",
        ],
    }


def main() -> int:
    result = evaluate()
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"LINEAR HANDOFF CHECK {result['overall'].upper()}")
        print(f"handoff_status: {result['handoff_status']}")
        print(f"external_actions_performed: {str(result['external_actions_performed']).lower()}")
        for error in result["errors"]:
            print(f"- {error}")
        if result["not_guaranteed_by_local_repo"]:
            print("not_guaranteed_by_local_repo:")
            for item in result["not_guaranteed_by_local_repo"]:
                print(f"- {item}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
