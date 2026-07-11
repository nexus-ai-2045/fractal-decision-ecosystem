#!/usr/bin/env python3
"""Check FDE pre-publication gates without performing external actions."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PUBLIC_KERNEL = ROOT / "public-kernel"

from scripts.human_review_packet_check import evaluate as evaluate_human_review_packet
from scripts.public_kernel_diff_manifest import evaluate as evaluate_public_kernel_diff

REQUIRED_ROOT_FILES = (
    "LICENSE",
    "RIGHTS_NOTICE.md",
    "PUBLIC_KERNEL_PLAN.md",
    "DEFENSIVE_PATENT_REVIEW.md",
    "INVENTION_RECORD.md",
    "TODO_FDE_PUBLIC_KERNEL_RIGHTS.md",
    "PUBLICATION_REVIEW_PACKET.md",
    "PATENT_DISCLOSURE_RECORD.md",
)

# PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md と patent-packet/ は 2026-07 の repository
# public 化に伴い誤って公開されたため、tracked file から除去し .gitignore に追加した
# (PATENT_DISCLOSURE_RECORD.md 参照)。この 2 つは REQUIRED_ROOT_FILES に含めず、代わりに
# check_no_public_patent_material() で「tracked として存在しないこと」を検査する。
FORBIDDEN_PATENT_MATERIAL_GITIGNORE_ENTRIES = (
    "PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md",
    "patent-packet/",
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

REQUIRED_TODO_PATENT_PACKET_TERMS = (
    "を git 追跡から除去し `.gitignore` に追加する",
    "PATENT_DISCLOSURE_RECORD.md",
    "local-only 生成物",
)

REQUIRED_PATENT_DISCLOSURE_RECORD_TERMS = (
    "事実記録のみ。法的助言ではない",
    "2026-07 に public 化された",
    "patent-packet/",
    "git 履歴の書き換え",
    "専門家",
    "出願する / しない",
)

REQUIRED_PUBLIC_READY_TERMS = (
    "patent filing は patent / public kernel gate で保留",
    "patent / filing 方針は意図的に broad",
    "inventor / owner / assignee",
    "user-confirmed sole inventor",
    "assignee は none / unassigned",
    "public-kernel/",
    "Patent Pending",
    "外部送信",
    "announcement",
    "visibility 変更",
    "public release の宣言",
)

REQUIRED_INVENTION_RECORD_TERMS = (
    "Inventor(s): user-confirmed sole inventor",
    "Owner: user",
    "Assignee: none / unassigned",
    "Patent / filing details: intentionally broad",
    "Public release: hold until explicit repository visibility approval",
)


SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")


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


def parse_sha256_manifest(manifest_path: Path) -> tuple[dict[str, str], list[str]]:
    entries: dict[str, str] = {}
    errors: list[str] = []
    for line_number, raw_line in enumerate(read(manifest_path).splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("generated_at_utc="):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            errors.append(f"line {line_number}: malformed SHA256 entry")
            continue
        digest, rel = parts[0].lower(), parts[1].strip()
        if not SHA256_RE.fullmatch(digest):
            errors.append(f"line {line_number}: invalid SHA256 for {rel}")
            continue
        if rel in entries:
            errors.append(f"line {line_number}: duplicate hash entry: {rel}")
            continue
        entries[rel] = digest
    return entries, errors


def validate_sha256_manifest(root: Path, manifest_rel: str, required_rels: tuple[str, ...]) -> list[str]:
    manifest_path = root / manifest_rel
    if not manifest_path.exists():
        return [f"{manifest_rel} missing"]

    entries, parse_errors = parse_sha256_manifest(manifest_path)
    errors = [f"{manifest_rel}: {error}" for error in parse_errors]
    for rel in required_rels:
        expected = entries.get(rel)
        if expected is None:
            errors.append(f"{manifest_rel} missing hash entry: {rel}")
            continue
        path = root / rel
        if not path.exists():
            errors.append(f"{manifest_rel} hash target missing: {rel}")
            continue
        actual = sha256(path)
        if actual != expected:
            errors.append(f"{manifest_rel} hash mismatch: {rel} expected {expected} actual {actual}")
    return errors


def check_patent_packet(errors: list[str]) -> None:
    todo_text = read(ROOT / "TODO_FDE_PUBLIC_KERNEL_RIGHTS.md")
    for term in REQUIRED_TODO_PATENT_PACKET_TERMS:
        if term not in todo_text:
            errors.append(f"TODO_FDE_PUBLIC_KERNEL_RIGHTS.md missing: {term}")


def check_patent_disclosure_record(errors: list[str]) -> None:
    text = read(ROOT / "PATENT_DISCLOSURE_RECORD.md")
    for term in REQUIRED_PATENT_DISCLOSURE_RECORD_TERMS:
        if term not in text:
            errors.append(f"PATENT_DISCLOSURE_RECORD.md missing: {term}")


def forbidden_patent_material_paths(tracked_files: list[str]) -> list[str]:
    """git 管理下の tracked file から、除去対象の特許素材だけを抽出する。"""
    forbidden = []
    for rel in tracked_files:
        if rel == "PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md" or rel.startswith("patent-packet/"):
            forbidden.append(rel)
    return forbidden


def check_no_public_patent_material(errors: list[str]) -> None:
    """公開 repo の tracked file に特許素材 (draft / packet) が存在しないことを検査する。"""
    gitignore_text = read(ROOT / ".gitignore") if (ROOT / ".gitignore").exists() else ""
    for pattern in FORBIDDEN_PATENT_MATERIAL_GITIGNORE_ENTRIES:
        if pattern not in gitignore_text:
            errors.append(f".gitignore missing patent-material entry: {pattern}")

    git_dir = ROOT / ".git"
    if not git_dir.exists():
        return
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return
    tracked = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    forbidden = forbidden_patent_material_paths(tracked)
    if forbidden:
        errors.append(
            "patent material is tracked in the public repository: " + ", ".join(sorted(forbidden))
        )


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


def check_invention_record(errors: list[str]) -> None:
    text = read(ROOT / "INVENTION_RECORD.md")
    for term in REQUIRED_INVENTION_RECORD_TERMS:
        if term not in text:
            errors.append(f"INVENTION_RECORD.md missing: {term}")


def build_manifest() -> dict[str, object]:
    files = [
        ROOT / "DEFENSIVE_PATENT_REVIEW.md",
        ROOT / "INVENTION_RECORD.md",
        ROOT / "PATENT_DISCLOSURE_RECORD.md",
        ROOT / "PUBLIC_KERNEL_PLAN.md",
        ROOT / "RIGHTS_NOTICE.md",
        ROOT / "LICENSE",
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
    check_no_public_patent_material(errors)
    if not errors:
        check_license(errors)
        check_patent_packet(errors)
        check_patent_disclosure_record(errors)
        check_public_kernel(errors)
        check_public_ready(errors)
        check_invention_record(errors)
        public_kernel_diff = evaluate_public_kernel_diff()
        human_review_packet = evaluate_human_review_packet()
        if public_kernel_diff["overall"] != "ok":
            errors.extend(str(error) for error in public_kernel_diff["errors"])
        if human_review_packet["overall"] != "ok":
            errors.extend(str(error) for error in human_review_packet["errors"])
    return {
        "overall": "ok" if not errors else "error",
        "error": len(errors),
        "errors": errors,
        "manifest": build_manifest(),
        "remaining_human_or_external_blockers": [
            "repository visibility change is already approved and applied (public)",
            "further visibility changes, external sending, announcement, and patent filing still require explicit approval in the current turn",
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
