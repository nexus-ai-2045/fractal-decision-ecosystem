#!/usr/bin/env python3
"""Check project-local Chinju guidance for FDE-specific operating guarantees."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    ".chinju/manifest.json",
    ".chinju/policy.json",
    ".chinju/README.md",
    ".chinju/agent-guidance.md",
    ".chinju/project.md",
    ".chinju/workflow.md",
    ".chinju/quality-gates.md",
    ".chinju/knowledge/invariants.md",
    ".chinju/knowledge/incidents.md",
    ".chinju/knowledge/edge-cases.md",
)

REQUIRED_TERMS = {
    ".chinju/policy.json": (
        '"data_boundary": "local_first"',
        '"external_provider_requires_approval": true',
    ),
    ".chinju/project.md": (
        "Fractal Decision Ecosystem",
        "Repository visibility is private by default",
        "python scripts\\mvp_gate_check.py",
        "Linear is optional local handoff",
    ),
    ".chinju/quality-gates.md": (
        "python scripts\\mvp_gate_check.py",
        "python scripts\\linear_handoff_check.py",
        "python scripts\\chinju_guidance_check.py",
        "python scripts\\public_ready_check.py",
        "python scripts\\pre_publication_gate_check.py --json",
        "python -m compileall -q scripts tests",
        "python -m pytest -q",
    ),
    ".chinju/knowledge/invariants.md": (
        "FDE remains private",
        "Public release is never implied by local MVP completion",
        "Patent filing is optional external work",
        "Linear handoff is optional",
        "external_actions_performed: false",
    ),
    ".chinju/knowledge/incidents.md": (
        "Linear connector write was unavailable",
        "blocker was previously overstated",
        "dirty tree can hide unreviewed generated guidance",
    ),
    ".chinju/knowledge/edge-cases.md": (
        "Linear is requested but no Linear tool",
        "final create / submit remains an external write action",
        "User asks for `残務ゼロ`",
    ),
}


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def evaluate() -> dict[str, object]:
    errors: list[str] = []
    for relpath in REQUIRED_FILES:
        if not (ROOT / relpath).exists():
            errors.append(f"missing required file: {relpath}")

    if not errors:
        for relpath, terms in REQUIRED_TERMS.items():
            text = read(relpath)
            for term in terms:
                if term not in text:
                    errors.append(f"{relpath} missing required term: {term}")

    return {
        "overall": "ok" if not errors else "error",
        "error": len(errors),
        "errors": errors,
        "external_actions_performed": False,
        "guidance_status": "fde_specific" if not errors else "incomplete",
    }


def main() -> int:
    result = evaluate()
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"CHINJU GUIDANCE CHECK {result['overall'].upper()}")
        print(f"guidance_status: {result['guidance_status']}")
        print(f"external_actions_performed: {str(result['external_actions_performed']).lower()}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
