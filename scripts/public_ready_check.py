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
    "ROADMAP.md",
    "ai-contact-safety-contract.md",
    "mvp-axis-operating-card.md",
    "scripts/mvp_gate_check.py",
    "scripts/run_mvp_gate.ps1",
    "scripts/roadmap_gate_check.py",
    "scripts/chinju_guidance_check.py",
    "scripts/adr_next.py",
    "decisions/README.md",
    "decisions/ADR-0001-development-card-adr-numbering.md",
    "decisions/ADR-0002-product-creative-review-path.md",
    "decisions/ADR-0003-ai-contact-safety-contract.md",
)

LOCAL_AI_WORKSPACE_PATHS = (
    ".chinju/sessions",
)

PACKAGE_EXCLUDED_PARTS = (
    ".git",
    "__pycache__",
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
JAPANESE_TEXT = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")

JAPANESE_REQUIRED_DOCS = (
    "README.md",
    "PUBLIC_READY.md",
    "MVP_STATUS.md",
    "OPERATIONAL_GUARANTEE.md",
    "TODO_FDE_PUBLIC_KERNEL_RIGHTS.md",
    "ROADMAP.md",
    "ai-contact-safety-contract.md",
    "mvp-axis-operating-card.md",
    "decisions/README.md",
    "decisions/ADR-0001-development-card-adr-numbering.md",
    "decisions/ADR-0002-product-creative-review-path.md",
    "decisions/ADR-0003-ai-contact-safety-contract.md",
    "PUBLIC_KERNEL_PLAN.md",
    "SECURITY.md",
    "public-kernel/README.md",
    "public-kernel/GATES.md",
    "public-kernel/PUBLIC_BOUNDARY.md",
    "public-kernel/RECURSIVE_MAP.md",
    "public-kernel/RIGHTS_NOTICE.md",
)

LANGUAGE_POLICY_TERMS = (
    "人間が読む本文、見出し、説明文は日本語で書きます",
    "code identifier、schema field、file name、GitHub Actions keyword、frontmatter key は英語のまま維持します",
)


def is_repository_package_path(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        rel = path if not path.is_absolute() else Path(path.name)
    rel_parts = rel.as_posix().split("/")
    if any(part in PACKAGE_EXCLUDED_PARTS for part in rel_parts):
        return False
    rel_posix = rel.as_posix().rstrip("/")
    return not any(
        rel_posix == excluded or rel_posix.startswith(f"{excluded}/")
        for excluded in LOCAL_AI_WORKSPACE_PATHS
    )


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for pattern in ("*.md", "*.html", "*.toml", "*.py", ".gitignore", "LICENSE"):
        files.extend(ROOT.rglob(pattern))
    return sorted({path for path in files if is_repository_package_path(path)})


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


def check_japanese_documentation(errors: list[str]) -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for term in LANGUAGE_POLICY_TERMS:
        if term not in readme:
            errors.append(f"README.md に日本語保証の必須文言がありません: {term}")

    for relpath in JAPANESE_REQUIRED_DOCS:
        path = ROOT / relpath
        if not path.exists():
            errors.append(f"日本語保証対象 doc がありません: {relpath}")
            continue
        text = path.read_text(encoding="utf-8")
        if not JAPANESE_TEXT.search(text):
            errors.append(f"{relpath}: 人間向け documentation は日本語本文を含む必要があります")


def check_operational_guarantee(errors: list[str]) -> None:
    text = (ROOT / "OPERATIONAL_GUARANTEE.md").read_text(encoding="utf-8")
    required_phrases = (
        "実装残務: なし",
        "運用残務: なし",
        "public release 残務: 人間承認が必要",
        "patent decision 残務: なし",
        "patent filing 実行残務: なし（optional / approval-gated）",
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
        "scripts/run_mvp_gate.ps1",
        "shell: pwsh",
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


def check_local_ai_workspace_boundary(errors: list[str]) -> None:
    gitignore = ROOT / ".gitignore"
    if not gitignore.exists():
        errors.append(".gitignore がありません")
        return

    ignored_patterns = {
        line.strip()
        for line in gitignore.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    for relpath in LOCAL_AI_WORKSPACE_PATHS:
        if f"{relpath}/" not in ignored_patterns:
            errors.append(f".gitignore に local AI-agent workspace 除外がありません: {relpath}/")

    if not (ROOT / ".git").exists():
        return
    for relpath in LOCAL_AI_WORKSPACE_PATHS:
        result = subprocess.run(
            ["git", "ls-files", "--", relpath],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.stdout.strip():
            errors.append(f"{relpath}/ が git tracked package に含まれています")


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
        if not is_repository_package_path(path):
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
    check_japanese_documentation(errors)
    check_operational_guarantee(errors)
    check_failure_postmortem_contract(errors)
    check_workflow_contract(errors)
    check_local_ai_workspace_boundary(errors)
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
