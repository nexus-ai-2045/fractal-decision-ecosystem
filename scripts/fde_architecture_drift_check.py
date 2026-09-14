#!/usr/bin/env python3
"""FDE のdocs/scripts/testsが同じシステム化primitiveを見ているか確認する。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.fde_workflow_check import evaluate as evaluate_workflow

# Public package では物理 path を持たない。capability key だけを検証する。
# resolution / mode は dependency-registry.md の該当行と一致することを
# evaluate() が実際に比較する (Codex P2: 以前は key の出現有無しか見ておらず、
# resolution を書き換えても verified のまま緑になっていた)。
EXTERNAL_AUTHORITIES = {
    "measurement-gate": {
        "capability": "測定可能な claim の実測、shadow 観測、昇格判断",
        "resolution": "operator-local-adapter",
        "mode": "external-authority",
    },
    "operational-command-smoke": {
        "capability": "command の dry-run / smoke / verify / report / regression 接続契約",
        "resolution": "operator-local-adapter",
        "mode": "external-authority",
    },
    "runtime-guarantee-matrix": {
        "capability": "runtime ごとの hard / warn / fail-closed / fail-open 保証差",
        "resolution": "operator-local-adapter",
        "mode": "external-authority",
    },
    "low-pdca-orchestrator": {
        "capability": "goal / decomposition / dispatch / check / act を回す shared skill",
        "resolution": "operator-local-adapter",
        "mode": "external-authority",
    },
    "startup-boot-gate": {
        "capability": "tier 契約を SessionStart で注入する warn-only boot gate",
        "resolution": "operator-local-adapter",
        "mode": "external-authority",
    },
    "fact-provenance": {
        "capability": "毎turn事実来歴の hook 実装と runtime drift 検査",
        "resolution": "operator-local-adapter",
        "mode": "external-authority",
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
        "## 目的",
        "## できること",
        "## クイックスタート",
        "## 安全境界",
        "operational_guarantee",
        "system_update",
        "schema_bound",
        "docs/fde-concept-guide.md",
    ),
    "docs/fde-concept-guide.md": (
        "## 完成図",
        "軽く賢く",
        "entry -> packet -> evidence -> decision -> closure",
        "## 閉ループの完成条件",
        "operational_guarantee",
        "system_update",
    ),
    "docs/local-chat-integration-map.md": (
        "portable composition contract",
        "chat-orchestrator",
        "fde.feedback.v1",
        "review_packet",
        "fde_operational_closeout.py",
        "operator-local-adapter",
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
        "startup-boot-gate",
        "fact-provenance",
        "measurement-gate",
        "operational-command-smoke",
        "runtime-guarantee-matrix",
        "low-pdca-orchestrator",
        "operator-local-adapter",
    ),
    "scripts/fde_operational_closeout.py": (
        "implementation_residue",
        "operation_residue",
        "external_public_residue",
        "post_merge_cleanup",
        "--run-post-merge-cleanup",
    ),
    "scripts/post_merge_cleanup.py": (
        "git fetch --prune",
        "worktree prune",
        "merged_local_branches",
        "delete_branch_on_merge",
        "refs/remotes/origin/main",
        "fail-closed",
    ),
    "docs/superpowers/skills/post-merge-cleanup.md": (
        "scripts/post_merge_cleanup.py",
        "resolvable ref",
        "test_ci_checkout_without_local_main_uses_origin_main",
    ),
    "tests/test_public_ready.py": (
        "test_fde_workflow_manifest_is_machine_readable_without_external_action",
        "test_fde_architecture_drift_check_connects_docs_scripts_and_tests",
        "test_fde_operational_closeout_reports_residue_without_public_action",
    ),
    "schemas/fde_route_failure.v1.schema.json": (
        "route_failure",
        "x-definitions",
    ),
    "scripts/fde_route_failure_check.py": (
        "fde_route_failure.v1.schema.json",
        "unknown_usage",
        "dead_entry",
    ),
    "tests/test_route_failure_registry.py": (
        "fde_route_failure_check",
        "test_route_failure_registry_matches_docs",
    ),
}


def _row_embeds_private_path(line: str) -> bool:
    return any(marker in line for marker in PRIVATE_PATH_MARKERS)


CAPABILITY_TABLE_HEADER = ["key", "capability", "resolution", "mode"]
_TABLE_SEPARATOR_CELL = re.compile(r"^:?-{1,}:?$")


def _split_table_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if len(stripped) < 2 or not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _parse_capability_registry_rows(registry_text: str) -> dict[str, dict[str, str]]:
    """`| key | capability | resolution | mode |` table の各行を key ごとに parse する。

    以前は key 文字列が registry 本文のどこかに出現するかだけを見ており、
    resolution / mode を書き換えても検知できなかった (Codex P2)。
    """
    rows: dict[str, dict[str, str]] = {}
    lines = registry_text.splitlines()
    i = 0
    while i < len(lines) - 1:
        header_cells = _split_table_row(lines[i])
        if header_cells != CAPABILITY_TABLE_HEADER:
            i += 1
            continue
        sep_cells = _split_table_row(lines[i + 1])
        if (
            sep_cells is None
            or len(sep_cells) != len(header_cells)
            or not all(_TABLE_SEPARATOR_CELL.fullmatch(c) for c in sep_cells)
        ):
            i += 1
            continue
        j = i + 2
        while j < len(lines):
            row_cells = _split_table_row(lines[j])
            if row_cells is None or len(row_cells) != len(header_cells):
                break
            key, capability, resolution, mode = row_cells
            rows[key] = {
                "capability": capability,
                "resolution": resolution,
                "mode": mode,
            }
            j += 1
        i = j
    return rows


_PARENTHETICAL = re.compile(r"[（(][^（）()]*[）)]")


def _strip_parenthetical(text: str) -> str:
    return _PARENTHETICAL.sub("", text).strip()


def _check_external_authority(
    key: str, meta: dict[str, str], registry_rows: dict[str, dict[str, str]]
) -> tuple[dict[str, object], list[str]]:
    """registry の該当行を実際に parse した結果と meta を全 field 比較する。

    以前は `key in registry_text` (出現有無) だけを見ており、resolution を
    `operator-local-adapter` から `withheld` に書き換えても listed=True の
    まま verified receipt を出していた (Codex P2)。
    """
    errors: list[str] = []
    row = registry_rows.get(key)
    listed = row is not None

    actual_capability = row["capability"] if row else None
    actual_resolution = row["resolution"] if row else None
    actual_mode = row["mode"] if row else None

    key_row_has_private_path = row is not None and _row_embeds_private_path(
        " ".join(row.values())
    )
    # registry 側は capability 本文の途中や末尾に（補足）を挟むことがあるため、
    # 括弧書きを取り除いてから完全一致で比較する。非空だけだと文言の drift を見逃す。
    capability_matches = (
        row is not None
        and _strip_parenthetical(actual_capability) == meta["capability"]
    )
    resolution_matches = row is not None and actual_resolution == meta["resolution"]
    mode_matches = row is not None and actual_mode == meta["mode"]

    ok = (
        listed
        and not key_row_has_private_path
        and capability_matches
        and resolution_matches
        and mode_matches
    )
    receipt = {
        "capability": meta["capability"],
        "resolution": meta["resolution"],
        "mode": meta["mode"],
        "listed_in_registry": listed,
        "private_path_embedded": key_row_has_private_path,
        "registry_capability": actual_capability,
        "registry_resolution": actual_resolution,
        "registry_mode": actual_mode,
        "capability_matches_registry": capability_matches,
        "resolution_matches_registry": resolution_matches,
        "mode_matches_registry": mode_matches,
        "scope": "standalone_public_package",
        "status": "verified" if ok else "error",
        "waiver_reason": None,
    }

    if not listed:
        errors.append(f"external authority capability missing from registry: {key}")
        return receipt, errors
    if key_row_has_private_path:
        errors.append(f"external authority embeds private path in public registry: {key}")
    if not capability_matches:
        errors.append(
            f"external authority capability mismatch: {key} "
            f"expected={meta['capability']!r} actual={actual_capability!r}"
        )
    if not resolution_matches:
        errors.append(
            f"external authority resolution mismatch: {key} "
            f"expected={meta['resolution']!r} actual={actual_resolution!r}"
        )
    if not mode_matches:
        errors.append(
            f"external authority mode mismatch: {key} "
            f"expected={meta['mode']!r} actual={actual_mode!r}"
        )
    return receipt, errors


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
    registry_rows = _parse_capability_registry_rows(registry_text)
    authority_receipts: dict[str, dict[str, object]] = {}
    for key, meta in EXTERNAL_AUTHORITIES.items():
        receipt, key_errors = _check_external_authority(key, meta, registry_rows)
        authority_receipts[key] = receipt
        errors.extend(key_errors)

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
