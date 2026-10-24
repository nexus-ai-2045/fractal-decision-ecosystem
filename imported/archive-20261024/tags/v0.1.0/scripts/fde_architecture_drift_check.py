#!/usr/bin/env python3
"""FDE のdocs/scripts/testsが同じシステム化primitiveを見ているか確認する。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECKS = {
    "README.md": ("## 完成図", "軽く賢く", "entry -> packet -> evidence -> decision -> closure"),
    "ROADMAP.md": ("## 完成図", "## 可視化マップ", "判断制御面", "ローカル運用面", "公開境界面"),
    "SYSTEM_OVERVIEW.md": (
        "FDE 全体図",
        "判断制御面",
        "fde_workflow.yaml",
        "scripts/fde_operational_closeout.py",
        "隣接product adapter",
        "機能マップ",
    ),
    "SYSTEMATIZATION_ARCHITECTURE_CHECK_2026-07-07.md": (
        "小さな state machine と gate bundle",
        "scripts/fde_operational_closeout.py",
        "scripts/fde_architecture_drift_check.py",
    ),
    "fde_workflow.yaml": ("control_plane: FDE", "external_approval_required"),
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

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "checked_files": checked_files,
    }


def main() -> int:
    result = evaluate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
