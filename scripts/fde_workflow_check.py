#!/usr/bin/env python3
"""FDE workflow manifest を read-only で検証する。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "fde_workflow.yaml"

REQUIRED_TERMS = (
    "schema_version: fde.workflow.v1",
    "control_plane: FDE",
    "external_actions_performed: false",
    "external_approval_required",
    "public_release",
    "repository_visibility_change",
    "external_send",
    "patent_filing",
    "pytest",
    "target_workflow_runner",
    "stop_at: review_packet",
    "receipt: metadata_only",
)

REQUIRED_STATES = (
    "intake",
    "scope",
    "orchestrate",
    "implement",
    "verify",
    "review_packet",
    "closeout",
    "external_approval_required",
)


def evaluate() -> dict[str, object]:
    errors: list[str] = []
    if not WORKFLOW.exists():
        text = ""
        errors.append("fde_workflow.yaml is missing")
    else:
        text = WORKFLOW.read_text(encoding="utf-8")

    for term in REQUIRED_TERMS:
        if term not in text:
            errors.append(f"fde_workflow.yaml missing required term: {term}")

    missing_states = [state for state in REQUIRED_STATES if f"  - {state}" not in text]
    for state in missing_states:
        errors.append(f"fde_workflow.yaml missing state: {state}")

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "workflow": {
            "control_plane": "FDE",
            "states": list(REQUIRED_STATES),
        },
    }


def main() -> int:
    result = evaluate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
