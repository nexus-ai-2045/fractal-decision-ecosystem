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
from scripts.fde_architecture_drift_check import evaluate as evaluate_fde_architecture_drift
from scripts.fde_workflow_check import evaluate as evaluate_fde_workflow
from scripts.residual_zero_goal_check import evaluate as evaluate_residual_zero_goal
from scripts.no_transport_contact_check import evaluate as evaluate_no_transport_contact
from scripts.verify_residual_zero_contract import evaluate as evaluate_residual_zero_contract
from scripts.visual_html_smoke import evaluate as evaluate_visual_html_smoke
from scripts.public_kernel_diff_manifest import evaluate as evaluate_public_kernel_diff
from scripts.human_review_packet_check import evaluate as evaluate_human_review_packet


REQUIRED_STATUS_TERMS = (
    "MVP状態: public repository 運用として完了",
    "リポジトリ可視性: public",
    "外部公開 action: 実行済み",
    "発明者判断: ユーザー単独発明者として確認済み",
    "所有者判断: ユーザーが保持",
    "権利方針: 出願または公開の別判断があるまで、特許・出願詳細は意図的に広めに保つ",
    "次の節目: public release が要求された場合だけ、publication approval に進む",
)

REQUIRED_TRACKED_FILES = (
    ".github/workflows/public-ready.yml",
    "MVP_STATUS.md",
    "scripts/mvp_gate_check.py",
    "scripts/public_ready_check.py",
    "scripts/roadmap_gate_check.py",
    "scripts/residual_zero_goal_check.py",
    "scripts/no_transport_contact_check.py",
    "scripts/verify_residual_zero_contract.py",
    "scripts/visual_html_smoke.py",
    "scripts/public_kernel_diff_manifest.py",
    "scripts/human_review_packet_check.py",
    "scripts/adr_next.py",
    "ROADMAP.md",
    "SYSTEM_OVERVIEW.md",
    "RESIDUAL_ZERO_GOAL_2026-07-05.md",
    "PUBLICATION_REVIEW_PACKET.md",
    "ai-contact-safety-contract.md",
    "mvp-axis-operating-card.md",
    "decisions/README.md",
    "decisions/ADR-0001-development-card-adr-numbering.md",
    "decisions/ADR-0002-product-creative-review-path.md",
    "decisions/ADR-0003-ai-contact-safety-contract.md",
    "decisions/ADR-0004-team-formation-orchestration-gate.md",
    "tests/test_public_ready.py",
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


def _run_fde_workflow() -> dict[str, object]:
    result = evaluate_fde_workflow()
    ok = result["overall"] == "ok" and result["external_actions_performed"] is False
    return {
        "name": "fde_workflow_check",
        "ok": ok,
        "result": result,
    }


def _run_fde_architecture_drift() -> dict[str, object]:
    result = evaluate_fde_architecture_drift()
    ok = result["overall"] == "ok" and result["external_actions_performed"] is False
    return {
        "name": "fde_architecture_drift_check",
        "ok": ok,
        "result": result,
    }


def _run_residual_zero_goal() -> dict[str, object]:
    result = evaluate_residual_zero_goal()
    ok = result["overall"] == "ok" and result["external_actions_performed"] is False
    return {
        "name": "residual_zero_goal_check",
        "ok": ok,
        "result": result,
    }


def _run_no_transport_contact() -> dict[str, object]:
    result = evaluate_no_transport_contact()
    ok = result["overall"] == "ok" and result["external_actions_performed"] is False
    return {
        "name": "no_transport_contact_check",
        "ok": ok,
        "result": result,
    }


def _run_residual_zero_contract() -> dict[str, object]:
    result = evaluate_residual_zero_contract()
    ok = result["overall"] == "ok" and result["external_actions_performed"] is False
    return {
        "name": "verify_residual_zero_contract",
        "ok": ok,
        "result": result,
    }


def _run_visual_html_smoke() -> dict[str, object]:
    result = evaluate_visual_html_smoke()
    ok = result["overall"] == "ok" and result["external_actions_performed"] is False
    return {
        "name": "visual_html_smoke",
        "ok": ok,
        "result": result,
    }


def _run_public_kernel_diff() -> dict[str, object]:
    result = evaluate_public_kernel_diff()
    ok = result["overall"] == "ok" and result["external_actions_performed"] is False
    return {
        "name": "public_kernel_diff_manifest",
        "ok": ok,
        "result": result,
    }


def _run_human_review_packet() -> dict[str, object]:
    result = evaluate_human_review_packet()
    ok = result["overall"] == "ok" and result["external_actions_performed"] is False
    return {
        "name": "human_review_packet_check",
        "ok": ok,
        "result": result,
    }


def _run_pytest() -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
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
        _run_fde_workflow(),
        _run_fde_architecture_drift(),
        _run_residual_zero_goal(),
        _run_no_transport_contact(),
        _run_residual_zero_contract(),
        _run_visual_html_smoke(),
        _run_public_kernel_diff(),
        _run_human_review_packet(),
        _check_mvp_status_file(),
        _check_required_files_tracked(),
    ]
    if run_pytest:
        checks.append(_run_pytest())

    ok = all(bool(check["ok"]) for check in checks)
    return {
        "overall": "ok" if ok else "error",
        "external_actions_performed": False,
        "repository_visibility_expected": "public",
        "mvp_status": "complete_for_public_repository_operation" if ok else "blocked",
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
