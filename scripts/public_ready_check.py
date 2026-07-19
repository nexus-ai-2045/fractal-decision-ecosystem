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
    "SYSTEM_OVERVIEW.md",
    "ROADMAP.md",
    "SYSTEMATIZATION_ARCHITECTURE_CHECK_2026-07-07.md",
    "fde_workflow.yaml",
    "RESIDUAL_ZERO_GOAL_2026-07-05.md",
    "PUBLICATION_REVIEW_PACKET.md",
    "ai-contact-safety-contract.md",
    "mvp-axis-operating-card.md",
    "scripts/mvp_gate_check.py",
    "scripts/run_mvp_gate.ps1",
    "scripts/roadmap_gate_check.py",
    "scripts/orchestration_gate_check.py",
    "scripts/fde_workflow_check.py",
    "scripts/fde_architecture_drift_check.py",
    "scripts/fde_operational_closeout.py",
    "scripts/residual_zero_goal_check.py",
    "scripts/no_transport_contact_check.py",
    "scripts/verify_residual_zero_contract.py",
    "scripts/visual_html_smoke.py",
    "scripts/public_kernel_diff_manifest.py",
    "scripts/human_review_packet_check.py",
    "scripts/adr_next.py",
    "decisions/README.md",
    "decisions/ADR-0001-development-card-adr-numbering.md",
    "decisions/ADR-0002-product-creative-review-path.md",
    "decisions/ADR-0003-ai-contact-safety-contract.md",
    "decisions/ADR-0004-team-formation-orchestration-gate.md",
    "decisions/ADR-0006-orchestration-spark-ops-gate.md",
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
        r"([A-Za-z]:\\+Users\\+|[A-Za-z]:/+Users/+|/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+)"
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
    "SYSTEM_OVERVIEW.md",
    "RESIDUAL_ZERO_GOAL_2026-07-05.md",
    "PUBLICATION_REVIEW_PACKET.md",
    "ai-contact-safety-contract.md",
    "mvp-axis-operating-card.md",
    "decisions/README.md",
    "decisions/ADR-0001-development-card-adr-numbering.md",
    "decisions/ADR-0002-product-creative-review-path.md",
    "decisions/ADR-0003-ai-contact-safety-contract.md",
    "decisions/ADR-0004-team-formation-orchestration-gate.md",
    "decisions/ADR-0006-orchestration-spark-ops-gate.md",
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
    return True


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
        "現在の visibility: public",
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
        "python -m pip install -r requirements-dev.txt",
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


GIT_HISTORY_LOG_FORMAT = "%an <%ae> %cn <%ce> %s%n%b"

GIT_HISTORY_FORBIDDEN_LABELS = ("private handle", "personal absolute path")


def scan_git_log_text_for_forbidden_patterns(text: str) -> list[str]:
    """git log 出力 (author/committer/subject/body) から禁止 pattern を検出する。

    commit body には `Co-authored-by:` trailer や検証コマンドの貼り付けが入るため、
    subject 行だけでなく body 全体を検査しないと個人名義やローカル絶対パスが
    素通りする (実際に private handle と Windows 絶対パスが commit body 経由で
    紛れ込んだ実績がある)。この関数は subprocess を呼ばない純粋関数にして、
    実 git 履歴を汚さずに文字列 fixture だけで単体テストできるようにしている。
    """
    found: list[str] = []
    for label in GIT_HISTORY_FORBIDDEN_LABELS:
        pattern = FORBIDDEN_PATTERNS[label]
        if pattern.search(text):
            found.append(f"git history に禁止 pattern が含まれています: {label}")
    return found


def check_git_history(errors: list[str]) -> None:
    git_dir = ROOT / ".git"
    if not git_dir.exists():
        return
    result = subprocess.run(
        ["git", "log", "--all", f"--format={GIT_HISTORY_LOG_FORMAT}"],
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return
    errors.extend(scan_git_log_text_for_forbidden_patterns(result.stdout))


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_readme_name(errors)
    check_japanese_documentation(errors)
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
