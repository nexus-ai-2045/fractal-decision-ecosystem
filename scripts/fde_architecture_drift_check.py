#!/usr/bin/env python3
"""FDE のdocs/scripts/testsが同じシステム化primitiveを見ているか確認する。"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.fde_workflow_check import evaluate as evaluate_workflow

EXTERNAL_AUTHORITIES = {
    "measurement-gate": "Documents/brain/measurement-gate.md",
    "operational-command-smoke": "Documents/brain/operational-command-smoke-contract.md",
    "runtime-guarantee-matrix": "Documents/references/runtime-guarantee-matrix.md",
    "low-pdca-orchestrator": "shared/skills/low-pdca-orchestrator/SKILL.md",
}

CHECKS = {
    "README.md": (
        "## 完成図",
        "軽く賢く",
        "entry -> packet -> evidence -> decision -> closure",
        "## 閉ループの完成条件",
        "operational_guarantee",
        "system_update",
    ),
    "ROADMAP.md": ("## 完成図", "## 可視化マップ", "判断制御面", "ローカル運用面", "公開境界面"),
    "SYSTEM_OVERVIEW.md": (
        "FDE 全体図",
        "判断制御面",
        "fde_workflow.yaml",
        "scripts/fde_operational_closeout.py",
        "隣接product adapter",
        "機能マップ",
        "## 継続学習面",
        "system update",
    ),
    "SYSTEMATIZATION_ARCHITECTURE_CHECK_2026-07-07.md": (
        "小さな state machine と gate bundle",
        "scripts/fde_operational_closeout.py",
        "scripts/fde_architecture_drift_check.py",
    ),
    "fde_workflow.yaml": (
        "control_plane: FDE",
        "external_approval_required",
        "closed_loop_sequence",
        "learning_adoption_requires",
        "capability_inventory_order",
        "feedback_contract",
    ),
    "dependency-registry.md": (
        "measurement-gate",
        "operational-command-smoke",
        "runtime-guarantee-matrix",
        "low-pdca-orchestrator",
    ),
    "scripts/fde_operational_closeout.py": ("implementation_residue", "operation_residue", "external_public_residue"),
    "tests/test_public_ready.py": (
        "test_fde_workflow_manifest_is_machine_readable_without_external_action",
        "test_fde_architecture_drift_check_connects_docs_scripts_and_tests",
        "test_fde_operational_closeout_reports_residue_without_public_action",
    ),
}


def evaluate() -> dict[str, object]:
    errors: list[str] = []
    checked_files: list[str] = []
    for relpath, terms in CHECKS.items():
        path = ROOT / relpath
        checked_files.append(relpath)
        if not path.exists():
            errors.append(f"missing architecture file: {relpath}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{relpath} missing required term: {term}")

    workflow = evaluate_workflow()
    if workflow["overall"] != "ok":
        errors.append("machine-readable workflow contract failed")

    projects_root = next(
        (
            parent
            for parent in ROOT.parents
            if (parent / "Documents").is_dir() and (parent / "shared").is_dir()
        ),
        None,
    )
    authority_receipts: dict[str, dict[str, object]] = {}
    for key, relative_path in EXTERNAL_AUTHORITIES.items():
        path = projects_root / relative_path if projects_root else None
        available = bool(path and path.is_file())
        authority_receipts[key] = {
            "path": relative_path,
            "available": available,
            "scope": "workspace" if projects_root else "standalone_public_package",
            "status": "verified" if available else "waived_optional_workspace_enrichment",
            "waiver_reason": None if available else "public package core is self-contained; this authority only enriches a matching workspace",
        }
        if projects_root and not available:
            errors.append(f"external authority is missing in workspace: {key} -> {relative_path}")

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "checked_files": checked_files,
        "workflow_contract": workflow["overall"],
        "external_authorities": authority_receipts,
    }


def main() -> int:
    result = evaluate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
