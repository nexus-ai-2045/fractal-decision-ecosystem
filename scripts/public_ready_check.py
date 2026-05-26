#!/usr/bin/env python3
"""Public readiness checks for Fractal Decision Ecosystem."""

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
)

FORBIDDEN_PATTERNS = {
    "personal absolute path": re.compile(
        r"(C:\\Users\\|C:/Users/|/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+)"
    ),
    "archived workspace path": re.compile(r"_workspace-config-archive|C-Users-yas-Projetcs"),
    "private handle": re.compile(r"(?i)(sayyas|say_yas|yasuhirokawagoe|tamagoe)"),
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
        errors.append("README.md must name Fractal Decision Ecosystem")


def check_forbidden_patterns(errors: list[str]) -> None:
    for path in iter_text_files():
        if path == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for label, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{rel}: forbidden {label}")


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
                errors.append(f"{path.relative_to(ROOT).as_posix()}: missing local link: {raw}")


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
            errors.append("git history contains a private handle/email")
            return


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_readme_name(errors)
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
