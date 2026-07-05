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
WINDOWS_USERS_ALT = "C:" + "/Users/"

FORBIDDEN_PUBLIC_PATTERNS = {
    "personal absolute path": re.compile(
        re.escape(WINDOWS_USERS)
        + "|"
        + re.escape(WINDOWS_USERS_ALT)
        + r"|/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+"
    ),
    "private source pointer": re.compile(r"Documents/brain|external-ai-route-registry", re.IGNORECASE),
    "secret-like token": re.compile(r"(sk-(proj-)?[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _public_files() -> list[Path]:
    if not PUBLIC_KERNEL.exists():
        return []
    return sorted(path for path in PUBLIC_KERNEL.rglob("*") if path.is_file())


def build_manifest() -> dict[str, object]:
    files = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in _public_files()
    ]
    return {
        "status": "local_public_kernel_diff_manifest",
        "external_actions_performed": False,
        "public_kernel_dir": "public-kernel/",
        "files": files,
        "kept_private_categories": list(REQUIRED_PRIVATE_BOUNDARY_TERMS),
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

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "manifest": build_manifest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--check", action="store_true", help="Return non-zero when manifest checks fail.")
    args = parser.parse_args()

    result = evaluate()
    if args.json or args.check:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"FDE PUBLIC KERNEL DIFF MANIFEST {result['overall'].upper()}")
        print(f"external_actions_performed: {str(result['external_actions_performed']).lower()}")
        for file_info in result["manifest"]["files"]:
            print(f"- {file_info['path']} {file_info['sha256']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
