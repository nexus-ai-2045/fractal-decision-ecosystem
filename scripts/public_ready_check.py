#!/usr/bin/env python3
"""Fractal Decision Ecosystem の公開準備チェック。"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "PUBLIC_READY.md",
    "MVP_STATUS.md",
    "OPERATIONAL_GUARANTEE.md",
    ".github/workflows/public-ready.yml",
    "scripts/mvp_gate_check.py",
)


def _join_chars(chars: str) -> str:
    return "".join(chars.split())


PRIVATE_HANDLE_PATTERN = "|".join(
    re.escape(token)
    for token in (
        _join_chars("s a y y a s"),
        _join_chars("s a y _ y a s"),
        _join_chars("y a s u h i r o k a w a g o e"),
        _join_chars("t a m a g o e"),
    )
)

ARCHIVED_WORKSPACE_PATTERN = "|".join(
    re.escape(token)
    for token in (
        "_workspace-config-archive",
        "C-Users-" + _join_chars("y a s") + "-Projetcs",
    )
)

FORBIDDEN_PATTERNS = {
    "personal absolute path": re.compile(
        r"(C:\\Users\\|C:/Users/|/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+)"
    ),
    "archived workspace path": re.compile(ARCHIVED_WORKSPACE_PATTERN),
    "private handle": re.compile(PRIVATE_HANDLE_PATTERN, re.IGNORECASE),
    "private key": re.compile(r"-----BEGIN (RSA|OPENSSH|EC|DSA)? ?PRIVATE KEY-----"),
    "OpenAI key": re.compile(r"sk-(proj-)?[A-Za-z0-9_-]{20,}"),
    "GitHub token": re.compile(r"(ghp|github_pat)_[A-Za-z0-9_]{20,}"),
    "frontmatter draft status": re.compile(r"(?m)^(status|type):\s*draft\s*$"),
}

LOCAL_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for pattern in ("*.md", "*.html", "*.toml", "*.py", ".gitignore", "LICENSE"):
        files.extend(ROOT.rglob(pattern))
    return sorted({path for path in files if ".git" not in path.parts and "__pycache__" not in path.parts})


def check_required_files(errors: list[str]) -> None:
    for name in REQUIRED_FILES:
        if not (ROOT / name).exists():
            errors.append(f"missing required file: {name}")


def check_readme_name(errors: list[str]) -> None:
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    text = readme.read_text(encoding="utf-8")
    if "Fractal Decision Ecosystem" not in text:
        errors.append("README.md に Fractal Decision Ecosystem の明記が必要です")
    for phrase in ("## 言語方針", "人間が読む本文", "schema field"):
        if phrase not in text:
            errors.append(f"README.md に言語方針の必須文言がありません: {phrase}")


def check_operational_guarantee(errors: list[str]) -> None:
    text = (ROOT / "OPERATIONAL_GUARANTEE.md").read_text(encoding="utf-8")
    required_phrases = (
        "実装残務: なし",
        "運用残務: なし",
        "public release 残務: 人間承認が必要",
        "現在の visibility: private",
        "failure_kind",
        "postmortem_action",
    )
    for phrase in required_phrases:
        if phrase not in text:
            errors.append(f"OPERATIONAL_GUARANTEE.md に必須文言がありません: {phrase}")


def check_failure_postmortem_contract(errors: list[str]) -> None:
    required_docs = (
        "core.md",
        "search-orchestration.md",
        "operating-card.md",
        "PUBLIC_READY.md",
        "OPERATIONAL_GUARANTEE.md",
    )
    required_terms = (
        "failure_kind",
        "postmortem_action",
        "attachment_failed",
        "wrong_surface",
        "timeout",
        "secret_risk",
    )
    for name in required_docs:
        text = (ROOT / name).read_text(encoding="utf-8")
        for term in required_terms[:2]:
            if term not in text:
                errors.append(f"{name} に外部 review 失敗の必須用語がありません: {term}")
        if name in {"core.md", "search-orchestration.md", "operating-card.md"}:
            for term in required_terms[2:]:
                if term not in text:
                    errors.append(f"{name} に failure_kind の値がありません: {term}")


def check_workflow_contract(errors: list[str]) -> None:
    workflow = ROOT / ".github" / "workflows" / "public-ready.yml"
    text = workflow.read_text(encoding="utf-8")
    required_terms = (
        "python scripts/mvp_gate_check.py",
        "python -m pip install pytest",
        "actions/checkout@v6",
        "actions/setup-python@v6",
        "pull_request:",
        "workflow_dispatch:",
        "contents: read",
    )
    for term in required_terms:
        if term not in text:
            errors.append(f"workflow に必須用語がありません: {term}")


def check_forbidden_patterns(errors: list[str]) -> None:
    for path in iter_text_files():
        if path == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for label, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{rel}: 禁止 pattern が見つかりました: {label}")


def check_local_markdown_links(errors: list[str]) -> None:
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for match in LOCAL_LINK.finditer(text):
            raw = match.group(1).strip()
            if not raw or raw.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target = unquote(raw.split("#", 1)[0])
            if not target:
                continue
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            if not (path.parent / target).exists():
                errors.append(f"{path.relative_to(ROOT).as_posix()}: local link の参照先がありません: {raw}")


def check_git_history(errors: list[str]) -> None:
    git_dir = ROOT / ".git"
    if not git_dir.exists():
        return
    result = subprocess.run(
        ["git", "log", "--all", "--format=%an <%ae> %cn <%ce> %s"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return
    pattern = FORBIDDEN_PATTERNS["private handle"]
    for line in result.stdout.splitlines():
        if pattern.search(line):
            errors.append("git history に private handle/email が含まれています")
            return


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_readme_name(errors)
    check_operational_guarantee(errors)
    check_failure_postmortem_contract(errors)
    check_workflow_contract(errors)
    check_forbidden_patterns(errors)
    check_local_markdown_links(errors)
    check_git_history(errors)

    if errors:
        print("PUBLIC READY CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PUBLIC READY CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
