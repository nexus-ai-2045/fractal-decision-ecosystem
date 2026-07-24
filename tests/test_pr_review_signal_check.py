from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts import public_ready_check
from scripts.pr_review_signal_check import evaluate


ROOT = public_ready_check.ROOT


def _pr_payload_with_disabled_bugbot() -> dict[str, object]:
    return {
        "reviews": [
            {
                "author": {"login": "cursor"},
                "body": "Cursor Bugbot チェックは未実行のため自動レビューシグナルをスキップしました。人間レビューが必要です。",
            },
            {
                "author": {"login": "chatgpt-codex-connector"},
                "body": "### 💡 Codex Review\nHere are some automated review suggestions for this pull request.",
            },
        ],
        "comments": [
            {
                "author": {"login": "cursor"},
                "body": "<!-- BUGBOT_FREE_TIER_DISABLED_UPSELL -->\nBugbot is not enabled for your account.",
            }
        ],
        "statusCheckRollup": [
            {
                "name": "Cursor Approval Agent: Pull Request Router and Approver",
                "status": "COMPLETED",
                "conclusion": "SUCCESS",
            },
            {
                "name": "public-ready",
                "status": "COMPLETED",
                "conclusion": "SUCCESS",
            },
        ],
    }


def test_disabled_bugbot_is_classified_as_human_review_required() -> None:
    result = evaluate(_pr_payload_with_disabled_bugbot())

    assert result["overall"] == "ok"
    assert result["checks_success"] is True
    assert result["cursor_bugbot"] == "disabled"
    assert result["automated_review_coverage"] == "insufficient"
    assert result["human_review_required"] is True
    assert result["do_not_treat_check_success_as_review_approval"] is True


def test_require_human_review_fails_when_bugbot_was_disabled() -> None:
    result = evaluate(_pr_payload_with_disabled_bugbot(), require_human_review=True)

    assert result["overall"] == "error"
    assert result["errors"] == ["human review is required before treating this PR as reviewed"]


def test_cli_reports_machine_readable_review_signal(tmp_path: Path) -> None:
    payload = tmp_path / "pr.json"
    payload.write_text(json.dumps(_pr_payload_with_disabled_bugbot(), ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.pr_review_signal_check",
            "--pr-json",
            str(payload),
            "--json",
        ],
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout
    parsed = json.loads(result.stdout)
    assert parsed["cursor_bugbot"] == "disabled"
    assert parsed["human_review_required"] is True
