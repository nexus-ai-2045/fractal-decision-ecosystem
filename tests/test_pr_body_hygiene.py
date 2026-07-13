"""PR タイトル/本文の PII・ローカル絶対パス scan の単体テスト。

2026-07-11 の実事故 (squash merge が生成した commit body に、PR 本文経由で
Windows ローカル絶対パスと Co-authored-by trailer 形式の個人情報が
そのまま転写された) を再現する fixture を使う。fixture はこの public repo に
実在の個人ハンドル・メールアドレスを平文で残さないよう、ダミー値のみ使う。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

from scripts import public_ready_check
from scripts.pr_body_hygiene_check import evaluate


ROOT = public_ready_check.ROOT


def _dummy_windows_verification_line() -> str:
    # 実事故と同じ形: 検証コマンド欄に Windows 絶対パスが素で書かれていた。
    # 実在ユーザー名を避けるため "example-user" というダミー値を使う。
    drive = "C:"
    sep = "\\" + "Users" + "\\"
    return "- `python " + drive + sep + "example-user" + "\\Projects\\shared\\scripts\\preflight.py`"


def _dummy_macos_path_fragment() -> str:
    return "/" + "Users" + "/example-user/Projects/shared/scripts/preflight.py"


def _dummy_co_author_trailer() -> str:
    # 実事故と同じ trailer 形式。ハンドル/メールは example ドメインのダミー値。
    return "Co-authored-by: example-handle <someone@example.com>"


def _incident_shaped_body() -> str:
    return "\n".join(
        [
            "## 概要",
            "PR 本文 scan gate を追加した。",
            "",
            "## 検証",
            _dummy_windows_verification_line(),
            "",
            _dummy_co_author_trailer(),
        ]
    )


def _clean_body() -> str:
    return "\n".join(
        [
            "## 概要",
            "PR 本文 scan gate を追加した。",
            "",
            "## 検証",
            "- `python -m pytest -q`",
            "- `python scripts/pr_body_hygiene_check.py --title \"t\" --body \"clean\"`",
            "- https://github.com/nexus-ai-2045/fractal-decision-ecosystem/pull/1",
            "",
            "Co-authored-by: Nexus AI <noreply@nexus-ai.local>",
        ]
    )


def test_detects_windows_local_path_in_verification_command() -> None:
    result = evaluate("PR hygiene gate を追加", _incident_shaped_body())

    assert result["overall"] == "error"
    labels = {finding["label"] for finding in result["findings"]}
    assert "windows local path" in labels


def test_detects_disallowed_co_author_trailer() -> None:
    result = evaluate("title", _dummy_co_author_trailer())

    assert result["overall"] == "error"
    labels = {finding["label"] for finding in result["findings"]}
    assert "disallowed co-authored-by trailer" in labels


def test_detects_macos_style_local_path() -> None:
    result = evaluate("title", f"- `python {_dummy_macos_path_fragment()}`")

    assert result["overall"] == "error"
    labels = {finding["label"] for finding in result["findings"]}
    assert "macOS local path" in labels


def test_masks_windows_username_in_output() -> None:
    result = evaluate("title", _dummy_windows_verification_line())

    masked_blob = json.dumps(result, ensure_ascii=False)
    assert "example-user" not in masked_blob
    assert "***" in masked_blob


def test_masks_email_local_part_in_output() -> None:
    result = evaluate("title", _dummy_co_author_trailer())

    masked_blob = json.dumps(result, ensure_ascii=False)
    assert "someone" not in masked_blob
    assert "***@example.com" in masked_blob


def test_clean_body_with_relative_paths_and_urls_passes() -> None:
    result = evaluate("chore: add pr hygiene gate", _clean_body())

    assert result["overall"] == "ok", result["findings"]
    assert result["findings"] == []


def test_allowlisted_github_noreply_email_passes() -> None:
    body = "Co-authored-by: Example Bot <12345+example-bot@users.noreply.github.com>"

    result = evaluate("title", body)

    assert result["overall"] == "ok", result["findings"]


def test_denylist_handle_from_argument_is_detected_and_masked() -> None:
    body = "requested by example-handle in DMs"

    result = evaluate("title", body, denylist=["example-handle"])

    assert result["overall"] == "error"
    denylist_findings = [f for f in result["findings"] if f["label"] == "denylisted personal handle"]
    assert denylist_findings
    for finding in denylist_findings:
        assert finding["masked"] == "***"


def test_denylist_empty_does_not_false_positive() -> None:
    result = evaluate("title", "no denylist configured here", denylist=[])

    assert result["overall"] == "ok"


def test_cli_reads_title_and_body_from_env_vars_and_masks_output() -> None:
    env = os.environ.copy()
    env["PR_HYGIENE_TITLE"] = "Fix bug"
    env["PR_HYGIENE_BODY"] = _dummy_windows_verification_line()
    env.pop("PR_HYGIENE_DENYLIST", None)

    result = subprocess.run(
        [sys.executable, "-m", "scripts.pr_body_hygiene_check"],
        cwd=ROOT,
        env=env,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 1, result.stdout
    assert "example-user" not in result.stdout
    assert "windows local path" in result.stdout


def test_cli_body_file_option_reports_json(tmp_path: Path) -> None:
    body_file = tmp_path / "body.txt"
    body_file.write_text(_dummy_co_author_trailer(), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.pr_body_hygiene_check",
            "--title",
            "t",
            "--body-file",
            str(body_file),
            "--json",
        ],
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 1, result.stdout
    payload = json.loads(result.stdout)
    assert payload["overall"] == "error"
    assert "someone" not in result.stdout


def test_cli_stdin_option_reports_failure() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.pr_body_hygiene_check", "--title", "t", "--stdin"],
        cwd=ROOT,
        input=_dummy_windows_verification_line(),
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 1, result.stdout


def test_cli_clean_body_exits_zero() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.pr_body_hygiene_check",
            "--title",
            "chore: clean",
            "--body",
            "no secrets here",
        ],
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_pr_hygiene_workflow_triggers_on_edited_and_reads_env_not_inline() -> None:
    workflow_path = ROOT / ".github" / "workflows" / "pr-hygiene.yml"
    assert workflow_path.exists()
    text = workflow_path.read_text(encoding="utf-8")
    parsed = yaml.safe_load(text)

    pull_request_config = parsed.get("on", parsed.get(True, {})).get("pull_request", {})
    types = pull_request_config.get("types", [])
    for required_type in ("opened", "edited", "synchronize", "reopened"):
        assert required_type in types

    assert "PR_HYGIENE_TITLE" in text
    assert "PR_HYGIENE_BODY" in text

    run_lines = [
        line.strip()
        for line in text.splitlines()
        if "pr_body_hygiene_check.py" in line and line.strip().startswith("run:")
    ]
    assert run_lines, "python scripts/pr_body_hygiene_check.py を呼ぶ run: 行が必要"
    # PR タイトル/本文は env: 経由で渡し、run: の shell 文字列へ直接埋め込まない
    # (github.event.pull_request.title/body の script injection 回避)。
    for line in run_lines:
        assert "${{" not in line
