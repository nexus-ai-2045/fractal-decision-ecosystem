#!/usr/bin/env python3
"""PR review signals をCI成功と人間レビューから分離して分類する。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


BUGBOT_DISABLED_PATTERNS = (
    "BUGBOT_FREE_TIER_DISABLED_UPSELL",
    "Bugbot is not enabled",
    "Bugbot チェックは未実行",
    "自動レビューシグナルをスキップ",
)
HUMAN_REVIEW_REQUIRED_PATTERNS = (
    "人間レビューが必要",
    "human review",
    "human_review_required",
)
CURSOR_CHECK_PREFIX = "Cursor "
CODEX_REVIEW_MARKER = "Codex Review"


def _items(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = payload.get(key)
    return value if isinstance(value, list) else []


def _text(item: dict[str, Any]) -> str:
    value = item.get("body")
    return value if isinstance(value, str) else ""


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def _author_login(item: dict[str, Any]) -> str:
    author = item.get("author")
    if isinstance(author, dict):
        login = author.get("login")
        return login if isinstance(login, str) else ""
    return ""


def _check_runs(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in _items(payload, "statusCheckRollup") if isinstance(item, dict)]


def _successful_cursor_checks(payload: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for check in _check_runs(payload):
        name = check.get("name")
        if not isinstance(name, str) or not name.startswith(CURSOR_CHECK_PREFIX):
            continue
        if check.get("status") == "COMPLETED" and check.get("conclusion") == "SUCCESS":
            names.append(name)
    return sorted(names)


def _all_review_texts(payload: dict[str, Any]) -> list[str]:
    return [_text(item) for item in [*_items(payload, "reviews"), *_items(payload, "comments")]]


def evaluate(payload: dict[str, Any], require_human_review: bool = False) -> dict[str, Any]:
    review_texts = _all_review_texts(payload)
    joined_review_text = "\n".join(review_texts)
    cursor_bugbot_disabled = _contains_any(joined_review_text, BUGBOT_DISABLED_PATTERNS)
    human_review_required = cursor_bugbot_disabled or _contains_any(
        joined_review_text, HUMAN_REVIEW_REQUIRED_PATTERNS
    )

    codex_comments = [
        item
        for item in _items(payload, "reviews")
        if _author_login(item) == "chatgpt-codex-connector" or CODEX_REVIEW_MARKER in _text(item)
    ]
    cursor_checks = _successful_cursor_checks(payload)
    checks_success = all(
        check.get("status") == "COMPLETED" and check.get("conclusion") == "SUCCESS"
        for check in _check_runs(payload)
    )

    errors: list[str] = []
    if require_human_review and human_review_required:
        errors.append("human review is required before treating this PR as reviewed")

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "checks_success": checks_success,
        "cursor_checks_success": cursor_checks,
        "cursor_bugbot": "disabled" if cursor_bugbot_disabled else "not_disabled_or_not_seen",
        "codex_review_signal": "commented" if codex_comments else "not_seen",
        "automated_review_coverage": "insufficient" if human_review_required else "available",
        "human_review_required": human_review_required,
        "do_not_treat_check_success_as_review_approval": bool(cursor_checks or codex_comments),
        "errors": errors,
    }


def _load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr-json", type=Path, required=True, help="gh pr view --json output")
    parser.add_argument(
        "--require-human-review",
        action="store_true",
        help="人間レビュー必須状態なら非zeroにする",
    )
    parser.add_argument("--json", action="store_true", help="JSONで出力する")
    args = parser.parse_args(argv)

    result = evaluate(_load_payload(args.pr_json), require_human_review=args.require_human_review)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"PR REVIEW SIGNAL CHECK {result['overall'].upper()}")
        print(f"checks_success: {str(result['checks_success']).lower()}")
        print(f"automated_review_coverage: {result['automated_review_coverage']}")
        print(f"human_review_required: {str(result['human_review_required']).lower()}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
