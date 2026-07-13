#!/usr/bin/env python3
"""PR タイトル/本文に含まれる PII・ローカル絶対パスを検査する。

2026-07-11 の実事故: squash merge が生成する commit body には PR 本文が
そのまま転写される。ローカルの pre-push hook / push gate はローカル push を
経由しない squash merge commit には発火しないため、ローカル絶対パスと
`Co-authored-by:` trailer 経由の個人情報が public repo に漏洩した。この gate は
merge (= squash commit 生成) より前の PR 本文段階で同じ形の漏洩を検出する。

検出対象:
    - Windows / macOS / Linux のローカル絶対パス ("...Users\\<name>\\..." 等)
    - 許可リスト外のメールアドレス
    - 許可リスト外の名義を持つ `Co-authored-by:` trailer
    - 環境変数/引数で渡された denylist 文字列 (個人ハンドル等)

検出した秘密そのものは出力しない。username / local-part を "***" に
置換してから報告する。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


# 正規表現中の「1 個以上のバックスラッシュ」を表す regex 断片。
# public_ready_check.py の禁止 pattern scanner 自身が repo 内の全 *.py file を
# scan するため、"\\+Users\\+" を隣接リテラルとして書かず文字列連結で構築する
# (pre_publication_gate_check.py の WINDOWS_USERS と同じ回避方針)。
_BACKSLASH_RUN = "\\" + "\\+"

WINDOWS_BACKSLASH_PATH = re.compile(
    r"(?P<prefix>[A-Za-z]:" + _BACKSLASH_RUN + "Users" + _BACKSLASH_RUN + r")"
    r"(?P<user>[^\\\s]+)(?P<rest>\\[^\s`'\"]*)?"
)
WINDOWS_FORWARDSLASH_PATH = re.compile(
    r"(?P<prefix>[A-Za-z]:/+Users/+)(?P<user>[^/\s]+)(?P<rest>/[^\s`'\"]*)?"
)
MACOS_PATH = re.compile(r"(?P<prefix>/Users/)(?P<user>[A-Za-z0-9._-]+)(?P<rest>/[^\s`'\"]*)?")
LINUX_HOME_PATH = re.compile(r"(?P<prefix>/home/)(?P<user>[A-Za-z0-9._-]+)(?P<rest>/[^\s`'\"]*)?")

LOCAL_PATH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows local path", WINDOWS_BACKSLASH_PATH),
    ("windows local path", WINDOWS_FORWARDSLASH_PATH),
    ("macOS local path", MACOS_PATH),
    ("linux local path", LINUX_HOME_PATH),
)

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

CO_AUTHOR_TRAILER_PATTERN = re.compile(
    r"(?i)^co-authored-by:\s*(?P<name>.+?)\s*<(?P<email>[^>]+)>\s*$"
)

ALLOWED_EMAILS = frozenset(
    {
        "noreply@github.com",
        "noreply@nexus-ai.local",
        "nexus.ai.2045@gmail.com",
    }
)

GITHUB_NOREPLY_SUFFIX = "@users.noreply.github.com"


def is_allowed_email(email: str) -> bool:
    """公開名義として許可されたメールアドレスかどうかを判定する。"""
    normalized = email.strip().lower()
    if normalized in ALLOWED_EMAILS:
        return True
    return normalized.endswith(GITHUB_NOREPLY_SUFFIX)


@dataclass(frozen=True)
class Finding:
    line_number: int
    label: str
    masked: str


def _iter_lines_with_numbers(text: str) -> Iterable[tuple[int, str]]:
    for line_number, line in enumerate(text.splitlines(), start=1):
        yield line_number, line


def _mask_local_path(match: re.Match[str]) -> str:
    prefix = match.group("prefix")
    rest = match.group("rest")
    separator = "\\" if "\\" in prefix else "/"
    suffix = f"{separator}..." if rest else ""
    return f"{prefix}***{suffix}"


def _mask_email(email: str) -> str:
    local_part, separator, domain = email.partition("@")
    if not separator:
        return "***"
    return f"***@{domain}"


def find_local_path_findings(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in _iter_lines_with_numbers(text):
        for label, pattern in LOCAL_PATH_PATTERNS:
            for match in pattern.finditer(line):
                findings.append(Finding(line_number, label, _mask_local_path(match)))
    return findings


def find_disallowed_email_findings(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in _iter_lines_with_numbers(text):
        for match in EMAIL_PATTERN.finditer(line):
            email = match.group(0)
            if is_allowed_email(email):
                continue
            findings.append(Finding(line_number, "disallowed email address", _mask_email(email)))
    return findings


def find_co_author_trailer_findings(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in _iter_lines_with_numbers(text):
        match = CO_AUTHOR_TRAILER_PATTERN.match(line.strip())
        if not match:
            continue
        email = match.group("email")
        if is_allowed_email(email):
            continue
        findings.append(
            Finding(
                line_number,
                "disallowed co-authored-by trailer",
                f"Co-authored-by: *** <{_mask_email(email)}>",
            )
        )
    return findings


def find_denylist_handle_findings(text: str, denylist: Sequence[str]) -> list[Finding]:
    findings: list[Finding] = []
    normalized_denylist = [handle.strip() for handle in denylist if handle.strip()]
    if not normalized_denylist:
        return findings
    for line_number, line in _iter_lines_with_numbers(text):
        lowered = line.lower()
        for handle in normalized_denylist:
            if handle.lower() in lowered:
                findings.append(Finding(line_number, "denylisted personal handle", "***"))
    return findings


def evaluate(title: str | None, body: str | None, denylist: Sequence[str] | None = None) -> dict[str, object]:
    """PR タイトル/本文を検査する。1 行目は title、2 行目以降が body になる。"""
    title_text = title or ""
    body_text = body or ""
    combined = f"{title_text}\n{body_text}"

    findings: list[Finding] = []
    findings.extend(find_local_path_findings(combined))
    findings.extend(find_disallowed_email_findings(combined))
    findings.extend(find_co_author_trailer_findings(combined))
    findings.extend(find_denylist_handle_findings(combined, denylist or ()))
    findings.sort(key=lambda finding: (finding.line_number, finding.label, finding.masked))

    return {
        "overall": "ok" if not findings else "error",
        "findings": [
            {"line": finding.line_number, "label": finding.label, "masked": finding.masked}
            for finding in findings
        ],
    }


def _load_denylist_from_env() -> list[str]:
    raw = os.environ.get("PR_HYGIENE_DENYLIST", "")
    return [item.strip() for item in raw.split(",") if item.strip()]


def _resolve_title(args: argparse.Namespace) -> str:
    if args.title is not None:
        return args.title
    return os.environ.get("PR_HYGIENE_TITLE", "")


def _resolve_body(args: argparse.Namespace) -> str:
    if args.body is not None:
        return args.body
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8", errors="replace")
    if args.stdin:
        return sys.stdin.read()
    return os.environ.get("PR_HYGIENE_BODY", "")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PR タイトル/本文の PII・ローカルパス検査")
    parser.add_argument("--title", default=None, help="PR タイトル (省略時は環境変数 PR_HYGIENE_TITLE)")
    parser.add_argument(
        "--body",
        default=None,
        help="PR 本文 (省略時は --body-file / --stdin / 環境変数 PR_HYGIENE_BODY)",
    )
    parser.add_argument("--body-file", default=None, help="PR 本文を読み込む file path")
    parser.add_argument("--stdin", action="store_true", help="標準入力から PR 本文を読み込む")
    parser.add_argument("--json", action="store_true", help="結果を JSON で出力する")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    title = _resolve_title(args)
    body = _resolve_body(args)
    denylist = _load_denylist_from_env()

    result = evaluate(title, body, denylist=denylist)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["overall"] == "ok":
        print("PR BODY HYGIENE CHECK OK")
    else:
        print("PR BODY HYGIENE CHECK FAILED")
        for finding in result["findings"]:
            print(f"- line {finding['line']}: {finding['label']}: {finding['masked']}")

    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
