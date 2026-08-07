#!/usr/bin/env python3
"""Build and check a local public-kernel diff manifest without publishing."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_KERNEL = ROOT / "public-kernel"
PLAN = ROOT / "PUBLIC_KERNEL_PLAN.md"

EXPECTED_PUBLIC_FILES = (
    "README.md",
    "LICENSE",
    "RIGHTS_NOTICE.md",
    "GATES.md",
    "RECURSIVE_MAP.md",
    "PUBLIC_BOUNDARY.md",
)

# Root-side rights / readiness files that bound publication (not shipped as full package).
RIGHTS_BOUNDARY_ROOT_FILES = (
    "LICENSE",
    "RIGHTS_NOTICE.md",
    "PUBLIC_READY.md",
    "SECURITY.md",
    "PUBLIC_KERNEL_PLAN.md",
    "DEFENSIVE_PATENT_REVIEW.md",
)

# Must never appear inside public-kernel/ (private operating package surface).
PRIVATE_MUST_NOT_LEAK = (
    "external-ai-route-registry.md",
    "operating-card.md",
    "dialogue-protocol.md",
    "axis-registry.md",
    "core.md",
    "root-router.md",
    "fde_workflow.yaml",
    "scripts/mvp_gate_check.py",
    "scripts/fde_operational_closeout.py",
)

REQUIRED_PRIVATE_BOUNDARY_TERMS = (
    "Full 50-skill recursive implementation",
    "Private structure",
    "`Documents/brain` pointers",
    "Local filesystem paths",
    "External AI route registry",
    "Absorbed dialogues",
    "Machine-specific runtime procedures",
    "Private guarantee scripts",
    "Patent-candidate implementation details",
)

WINDOWS_USERS = "C:" + "\\Users" + "\\"
WINDOWS_USERS_ALT = "C:" + "/" + "Users/"

FORBIDDEN_PUBLIC_PATTERNS = {
    "personal absolute path": re.compile(
        re.escape(WINDOWS_USERS)
        + "|"
        + re.escape(WINDOWS_USERS_ALT)
        + r"|/"
        + r"Users/[A-Za-z0-9._-]+|/"
        + r"home/[A-Za-z0-9._-]+"
    ),
    "private source pointer": re.compile(
        r"Documents/brain|external-ai-route-registry", re.IGNORECASE
    ),
    "secret-like token": re.compile(
        r"(sk-(proj-)?[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _public_files() -> list[Path]:
    if not PUBLIC_KERNEL.exists():
        return []
    return sorted(path for path in PUBLIC_KERNEL.rglob("*") if path.is_file())


def _root_vs_kernel_comparisons() -> list[dict[str, object]]:
    """Compare overlapping root vs public-kernel files (hash identity)."""
    rows: list[dict[str, object]] = []
    for name in EXPECTED_PUBLIC_FILES:
        root_path = ROOT / name
        kernel_path = PUBLIC_KERNEL / name
        if not kernel_path.exists():
            continue
        row: dict[str, object] = {
            "name": name,
            "in_root": root_path.is_file(),
            "in_public_kernel": True,
        }
        if root_path.is_file():
            root_hash = _sha256(root_path)
            kernel_hash = _sha256(kernel_path)
            row["root_sha256"] = root_hash
            row["kernel_sha256"] = kernel_hash
            row["identical"] = root_hash == kernel_hash
        else:
            row["root_sha256"] = None
            row["kernel_sha256"] = _sha256(kernel_path)
            row["identical"] = False
            row["note"] = "kernel_only_sanitized_candidate"
        rows.append(row)
    return rows


def _rights_boundary_files() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for name in RIGHTS_BOUNDARY_ROOT_FILES:
        path = ROOT / name
        rows.append(
            {
                "path": name,
                "present": path.is_file(),
                "sha256": _sha256(path) if path.is_file() else None,
            }
        )
    return rows


def build_manifest() -> dict[str, object]:
    files = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in _public_files()
    ]
    comparisons = _root_vs_kernel_comparisons()
    return {
        "status": "local_public_kernel_diff_manifest",
        "external_actions_performed": False,
        "public_kernel_dir": "public-kernel/",
        "files": files,
        "kept_private_categories": list(REQUIRED_PRIVATE_BOUNDARY_TERMS),
        "root_vs_kernel": comparisons,
        "rights_boundary_root_files": _rights_boundary_files(),
        "private_must_not_leak": list(PRIVATE_MUST_NOT_LEAK),
        # Kernel is a sanitized candidate, not a full private package clone.
        "public_kernel_is_full_private_package": False,
    }


def evaluate() -> dict[str, object]:
    errors: list[str] = []
    if not PUBLIC_KERNEL.exists():
        errors.append("public-kernel/ is missing")
    for relpath in EXPECTED_PUBLIC_FILES:
        if not (PUBLIC_KERNEL / relpath).exists():
            errors.append(f"public-kernel missing expected file: {relpath}")

    if not PLAN.exists():
        errors.append("PUBLIC_KERNEL_PLAN.md is missing")
        plan_text = ""
    else:
        plan_text = PLAN.read_text(encoding="utf-8")
    for term in REQUIRED_PRIVATE_BOUNDARY_TERMS:
        if term not in plan_text:
            errors.append(f"PUBLIC_KERNEL_PLAN.md missing private boundary term: {term}")

    for path in _public_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        relpath = path.relative_to(ROOT).as_posix()
        for label, pattern in FORBIDDEN_PUBLIC_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{relpath}: forbidden public-kernel pattern: {label}")

    # Private operating package must not leak into public-kernel tree.
    for relpath in PRIVATE_MUST_NOT_LEAK:
        leaked = PUBLIC_KERNEL / relpath
        if leaked.exists():
            errors.append(f"public-kernel must not contain private package path: {relpath}")

    for item in _rights_boundary_files():
        if not item["present"]:
            errors.append(f"rights boundary root file missing: {item['path']}")

    # Guard: public-kernel must stay a small candidate set, not the whole private package.
    public_count = len(_public_files())
    if public_count > 64:
        errors.append(
            f"public-kernel file count {public_count} looks like a full package dump"
        )

    # Guard: if root and kernel LICENSE/RIGHTS are identical for ALL overlapping names,
    # still OK; if package has huge private surface, we already check leaks.
    # Explicitly mark that full private package identity is forbidden.
    private_markers = ("fde_workflow.yaml", "scripts/mvp_gate_check.py", "operating-card.md")
    if all((ROOT / name).exists() for name in private_markers) and all(
        (PUBLIC_KERNEL / name).exists() for name in private_markers
    ):
        errors.append("public-kernel looks identical to private operating package")

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "manifest": build_manifest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--check", action="store_true", help="Return non-zero when manifest checks fail."
    )
    args = parser.parse_args()

    result = evaluate()
    if args.json or args.check:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"FDE PUBLIC KERNEL DIFF MANIFEST {result['overall'].upper()}")
        print(
            f"external_actions_performed: {str(result['external_actions_performed']).lower()}"
        )
        for file_info in result["manifest"]["files"]:
            print(f"- {file_info['path']} {file_info['sha256']}")
        for row in result["manifest"]["root_vs_kernel"]:
            print(
                f"compare {row['name']}: identical={row.get('identical')} "
                f"in_root={row.get('in_root')}"
            )
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
