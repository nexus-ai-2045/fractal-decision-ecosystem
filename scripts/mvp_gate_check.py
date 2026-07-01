#!/usr/bin/env python3
"""Run the local FDE MVP completion gate without external actions."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.pre_publication_gate_check import evaluate as evaluate_pre_publication
from scripts.public_ready_check import main as public_ready_main
from scripts.roadmap_gate_check import evaluate as evaluate_roadmap
from scripts.chinju_guidance_check import evaluate as evaluate_chinju_guidance


REQUIRED_STATUS_TERMS = (
    "MVP status: complete for private local gate",
    "Repository visibility: private",
    "No external publication action performed",
    "Inventor decision: user-confirmed sole inventor",
    "Owner decision: user retains ownership",
    "Rights strategy: keep patent / filing details intentionally broad until a separate filing decision or action is approved",
    "Next milestone: publication approval only if public release is requested",
)

REQUIRED_TRACKED_FILES = (
    ".github/workflows/public-ready.yml",
    "MVP_STATUS.md",
    "scripts/mvp_gate_check.py",
    "scripts/public_ready_check.py",
    "scripts/roadmap_gate_check.py",
    "scripts/chinju_guidance_check.py",
    "scripts/adr_next.py",
    "ROADMAP.md",
    "ai-contact-safety-contract.md",
    "mvp-axis-operating-card.md",
    "decisions/README.md",
    "decisions/ADR-0001-development-card-adr-numbering.md",
    "decisions/ADR-0002-product-creative-review-path.md",
    "decisions/ADR-0003-ai-contact-safety-contract.md",
    "tests/test_public_ready.py",
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


def _run_public_ready() -> dict[str, object]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exit_code = public_ready_main()
    return {
        "name": "public_ready_check",
        "ok": exit_code == 0,
        "exit_code": exit_code,
        "output": output.getvalue().strip().splitlines(),
    }


def _run_pre_publication() -> dict[str, object]:
    result = evaluate_pre_publication()
    return {
        "name": "pre_publication_gate_check",
        "ok": result["overall"] == "ok",
        "result": result,
    }


def _run_roadmap() -> dict[str, object]:
    result = evaluate_roadmap()
    return {
        "name": "roadmap_gate_check",
        "ok": result["overall"] == "ok",
        "result": result,
    }


def _run_chinju_guidance() -> dict[str, object]:
    result = evaluate_chinju_guidance()
    return {
        "name": "chinju_guidance_check",
        "ok": result["overall"] == "ok",
        "result": result,
    }


def _run_pytest() -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "name": "pytest",
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "output": result.stdout.strip().splitlines(),
    }


def _check_mvp_status_file() -> dict[str, object]:
    path = ROOT / "MVP_STATUS.md"
    missing_terms: list[str] = []
    if not path.exists():
        return {
            "name": "mvp_status_file",
            "ok": False,
            "missing_terms": list(REQUIRED_STATUS_TERMS),
            "error": "MVP_STATUS.md is missing",
        }
    text = path.read_text(encoding="utf-8")
    for term in REQUIRED_STATUS_TERMS:
        if term not in text:
            missing_terms.append(term)
    return {
        "name": "mvp_status_file",
        "ok": not missing_terms,
        "missing_terms": missing_terms,
    }


def _check_required_files_tracked() -> dict[str, object]:
    missing: list[str] = []
    for relpath in REQUIRED_TRACKED_FILES:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", relpath],
            cwd=ROOT,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode != 0:
            missing.append(relpath)
    return {
        "name": "required_files_tracked",
        "ok": not missing,
        "missing": missing,
    }


def evaluate(run_pytest: bool = True) -> dict[str, object]:
    checks = [
        _run_public_ready(),
        _run_pre_publication(),
        _run_roadmap(),
        _run_chinju_guidance(),
        _check_mvp_status_file(),
        _check_required_files_tracked(),
    ]
    if run_pytest:
        checks.append(_run_pytest())

    ok = all(bool(check["ok"]) for check in checks)
    return {
        "overall": "ok" if ok else "error",
        "external_actions_performed": False,
        "repository_visibility_expected": "private",
        "mvp_status": "complete_for_private_local_gate" if ok else "blocked",
        "next_milestone": "publication approval only if public release is requested",
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--skip-pytest",
        action="store_true",
        help="Skip pytest; intended for focused unit tests of this checker.",
    )
    args = parser.parse_args()

    result = evaluate(run_pytest=not args.skip_pytest)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"FDE MVP GATE CHECK {result['overall'].upper()}")
        print(f"mvp_status: {result['mvp_status']}")
        print(f"external_actions_performed: {str(result['external_actions_performed']).lower()}")
        print(f"next_milestone: {result['next_milestone']}")
        for check in result["checks"]:
            state = "ok" if check["ok"] else "error"
            print(f"- {check['name']}: {state}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
