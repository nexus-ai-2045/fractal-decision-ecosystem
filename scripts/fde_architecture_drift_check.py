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

# Public package では物理 path を持たない。capability key だけを検証する。
EXTERNAL_AUTHORITIES = {
    "measurement-gate": {
        "capability": "測定可能な claim の実測、shadow 観測、昇格判断",
        "resolution": "operator-local-adapter",
    },
    "operational-command-smoke": {
        "capability": "command の dry-run / smoke / verify / report / regression 接続契約",
        "resolution": "operator-local-adapter",
    },
    "runtime-guarantee-matrix": {
        "capability": "runtime ごとの hard / warn / fail-closed / fail-open 保証差",
        "resolution": "operator-local-adapter",
    },
    "low-pdca-orchestrator": {
        "capability": "goal / decomposition / dispatch / check / act を回す shared skill",
        "resolution": "operator-local-adapter",
    },
}

PRIVATE_PATH_MARKERS = (
    "Documents/",
    "~/" + "claude",
    "/" + "Users/",
    "/" + "home/",
    "/" + "Applications/",
    "C:\\" + "Users",
)

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
        "operator-local-adapter",
    ),
    "scripts/fde_operational_closeout.py": ("implementation_residue", "operation_residue", "external_public_residue"),
    "tests/test_public_ready.py": (
        "test_fde_workflow_manifest_is_machine_readable_without_external_action",
        "test_fde_architecture_drift_check_connects_docs_scripts_and_tests",
        "test_fde_operational_closeout_reports_residue_without_public_action",
    ),
}


def _row_embeds_private_path(line: str) -> bool:
    return any(marker in line for marker in PRIVATE_PATH_MARKERS)


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

    registry_text = (ROOT / "dependency-registry.md").read_text(encoding="utf-8")
    authority_receipts: dict[str, dict[str, object]] = {}
    for key, meta in EXTERNAL_AUTHORITIES.items():
        listed = key in registry_text
        key_row_has_private_path = any(
            key in line and _row_embeds_private_path(line)
            for line in registry_text.splitlines()
        )
        ok = listed and not key_row_has_private_path
        authority_receipts[key] = {
            "capability": meta["capability"],
            "resolution": meta["resolution"],
            "listed_in_registry": listed,
            "private_path_embedded": key_row_has_private_path,
            "scope": "standalone_public_package",
            "status": "verified" if ok else "error",
            "waiver_reason": None,
        }
        if not listed:
            errors.append(f"external authority capability missing from registry: {key}")
        if key_row_has_private_path:
            errors.append(f"external authority embeds private path in public registry: {key}")

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
