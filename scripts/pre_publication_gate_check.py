#!/usr/bin/env python3
"""Check FDE pre-publication gates without performing external actions."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_KERNEL = ROOT / "public-kernel"

REQUIRED_ROOT_FILES = (
    "LICENSE",
    "RIGHTS_NOTICE.md",
    "PUBLIC_KERNEL_PLAN.md",
    "DEFENSIVE_PATENT_REVIEW.md",
    "PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md",
    "INVENTION_RECORD.md",
    "TODO_FDE_PUBLIC_KERNEL_RIGHTS.md",
    "patent-packet/README.md",
    "patent-packet/FDE_PROVISIONAL_PATENT_DISCLOSURE_DRAFT.pdf",
    "patent-packet/MANIFEST.sha256",
)

REQUIRED_PUBLIC_KERNEL_FILES = (
    "README.md",
    "LICENSE",
    "RIGHTS_NOTICE.md",
    "GATES.md",
    "RECURSIVE_MAP.md",
    "PUBLIC_BOUNDARY.md",
)

def _compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


WINDOWS_USERS = "C:" + "\\Users" + "\\"
WINDOWS_USERS_ALT = "C:" + "/Users/"


FORBIDDEN_PUBLIC_KERNEL_PATTERNS = {
    "personal absolute path": re.compile(
        re.escape(WINDOWS_USERS)
        + "|"
        + re.escape(WINDOWS_USERS_ALT)
        + r"|/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+"
    ),
    "private source pointer": re.compile(r"Documents/brain|external-ai-route-registry", re.IGNORECASE),
    "secret-like token": re.compile(r"(sk-(proj-)?[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
}

REQUIRED_LICENSE_TERMS = (
    "owner, who may use, modify",
    "without restriction",
    "For everyone else, no license is granted",
    "not open source",
    "No patent license is granted",
    "No trademark license is granted",
)

REQUIRED_PATENT_DRAFT_TERMS = (
    "Do not publish this draft",
    "Do not mark FDE as \"Patent Pending\" unless an",
    "Recursive Source-Pointer Skill Routing",
    "Figure 1: Recursive Routing Stack",
    "Figure 2: Containment and Completion Loop",
    "Figure 3: Public/Private Split",
    "Candidate Claim Concepts",
)

REQUIRED_PUBLIC_READY_TERMS = (
    "public 化は patent / public kernel gate で保留",
    "defensive provisional patent filing",
    "inventor / owner / assignee",
    "public-kernel/",
    "Patent Pending",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_required_files(errors: list[str]) -> None:
    for rel in REQUIRED_ROOT_FILES:
        if not (ROOT / rel).exists():
            errors.append(f"missing root file: {rel}")
    for rel in REQUIRED_PUBLIC_KERNEL_FILES:
        if not (PUBLIC_KERNEL / rel).exists():
            errors.append(f"missing public-kernel file: {rel}")


def check_license(errors: list[str]) -> None:
    text = _compact(read(ROOT / "LICENSE"))
    for term in REQUIRED_LICENSE_TERMS:
        if term not in text:
            errors.append(f"LICENSE missing required term: {term}")


def check_patent_packet(errors: list[str]) -> None:
    text = read(ROOT / "PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md")
    for term in REQUIRED_PATENT_DRAFT_TERMS:
        if term not in text:
            errors.append(f"PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md missing: {term}")
    if "Patent Pending" in text and "unless an\napplication is actually filed" not in text:
        errors.append("Patent Pending wording is not guarded by filing requirement")
    manifest = read(ROOT / "patent-packet" / "MANIFEST.sha256")
    for rel in (
        "PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md",
        "patent-packet/FDE_PROVISIONAL_PATENT_DISCLOSURE_DRAFT.pdf",
        "DEFENSIVE_PATENT_REVIEW.md",
        "INVENTION_RECORD.md",
    ):
        if rel not in manifest:
            errors.append(f"patent-packet/MANIFEST.sha256 missing hash entry: {rel}")


def check_public_kernel(errors: list[str]) -> None:
    for path in sorted(PUBLIC_KERNEL.rglob("*")):
        if not path.is_file():
            continue
        text = read(path)
        compact = _compact(text).lower()
        rel = path.relative_to(ROOT).as_posix()
        for label, pattern in FORBIDDEN_PUBLIC_KERNEL_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{rel}: forbidden public-kernel pattern: {label}")
        if path.suffix.lower() in {".md", ""} and "not open source" not in compact and path.name in {"LICENSE", "README.md", "RIGHTS_NOTICE.md"}:
            errors.append(f"{rel}: missing not-open-source boundary")


def check_public_ready(errors: list[str]) -> None:
    text = read(ROOT / "PUBLIC_READY.md")
    for term in REQUIRED_PUBLIC_READY_TERMS:
        if term not in text:
            errors.append(f"PUBLIC_READY.md missing: {term}")


def build_manifest() -> dict[str, object]:
    files = [
        ROOT / "PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md",
        ROOT / "DEFENSIVE_PATENT_REVIEW.md",
        ROOT / "INVENTION_RECORD.md",
        ROOT / "PUBLIC_KERNEL_PLAN.md",
        ROOT / "RIGHTS_NOTICE.md",
        ROOT / "LICENSE",
        ROOT / "patent-packet" / "FDE_PROVISIONAL_PATENT_DISCLOSURE_DRAFT.pdf",
        ROOT / "patent-packet" / "MANIFEST.sha256",
    ]
    return {
        "status": "local_pre_publication_packet",
        "external_actions_performed": False,
        "files": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in files
            if path.exists()
        ],
    }


def evaluate() -> dict[str, object]:
    errors: list[str] = []
    check_required_files(errors)
    if not errors:
        check_license(errors)
        check_patent_packet(errors)
        check_public_kernel(errors)
        check_public_ready(errors)
    return {
        "overall": "ok" if not errors else "error",
        "error": len(errors),
        "errors": errors,
        "manifest": build_manifest(),
        "remaining_human_or_external_blockers": [
            "confirm inventor name(s)",
            "confirm owner / assignee",
            "decide whether to file provisional patent application",
            "perform patent filing if chosen",
            "approve exact GitHub repository visibility change before any public release",
        ],
    }


def main() -> int:
    result = evaluate()
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"PRE-PUBLICATION GATE CHECK {result['overall'].upper()}")
        for error in result["errors"]:
            print(f"- {error}")
        print("remaining_human_or_external_blockers:")
        for blocker in result["remaining_human_or_external_blockers"]:
            print(f"- {blocker}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
