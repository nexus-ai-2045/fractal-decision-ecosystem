#!/usr/bin/env python3
"""FDE task routing policy.

構造化済み案件を信用・約束・期限優先で並べ、1回に最大3件を
target workflow / self-resolve / human reviewへ振り分ける純粋な制御面。
executorや外部runtimeは持たず、このscript自体は外部操作を行わない。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import FormatChecker, ValidationError, validate


SCHEMA = "fde.manager_task.v1"
ROOT = Path(__file__).resolve().parents[1]
TASK_SCHEMA = json.loads(
    (ROOT / "schemas" / "fde_manager_task.v1.schema.json").read_text(encoding="utf-8")
)
MAX_INPUT_BYTES = 2 * 1024 * 1024
REQUIRED_FIELDS = {
    "schema",
    "task_id",
    "title",
    "created_at",
    "people_impact",
    "commitment",
    "deadline",
    "harm_risk",
    "external_boundary",
    "runnable",
    "blocked_reason",
    "workflow_manifest",
    "target_repo",
    "closure_rule",
}
EXTERNAL_BOUNDARIES = {
    "external_send",
    "publication",
    "git_push",
    "pull_request",
    "merge",
    "billing",
    "credential",
    "auth",
    "settings",
    "destructive",
}


class InvalidTaskError(ValueError):
    """Manager入力が安全に評価できない時のfail-closed例外。"""


def _parse_time(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise InvalidTaskError(f"invalid {field}") from exc
    if parsed.tzinfo is None:
        raise InvalidTaskError(f"{field} must include timezone")
    return parsed.astimezone(timezone.utc)


def _priority(task: dict[str, Any], now: datetime) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    deadline = task["deadline"]
    if deadline:
        deadline_at = _parse_time(deadline, "deadline")
        seconds_left = (deadline_at - now).total_seconds()
        if seconds_left < 0:
            score += 1000
            reasons.append("overdue")
        elif seconds_left <= 24 * 60 * 60:
            score += 700
            reasons.append("deadline_within_24h")
        elif seconds_left <= 7 * 24 * 60 * 60:
            score += 300
            reasons.append("deadline_within_7d")

    if task["commitment"] == "explicit":
        score += 500
        reasons.append("explicit_commitment")
    elif task["commitment"] == "implied":
        score += 200
        reasons.append("implied_commitment")

    if task["people_impact"] == "waiting_person":
        score += 400
        reasons.append("waiting_person")
    elif task["people_impact"] == "team_blocked":
        score += 350
        reasons.append("team_blocked")
    elif task["people_impact"] == "other":
        score += 100
        reasons.append("people_impact")

    if task["harm_risk"] == "safety":
        score += 900
        reasons.append("safety_risk")
    elif task["harm_risk"] == "financial":
        score += 600
        reasons.append("financial_risk")
    elif task["harm_risk"] == "reputation":
        score += 300
        reasons.append("reputation_risk")
    elif task["harm_risk"] == "data":
        score += 500
        reasons.append("data_risk")

    if not reasons:
        reasons.append("internal_queue")
    return score, reasons


def _route(task: dict[str, Any]) -> tuple[str, bool, str]:
    boundary = task["external_boundary"]
    if boundary in EXTERNAL_BOUNDARIES:
        return "human_review_required", False, "waiting_human_review"
    if boundary not in {"none", None}:
        return "human_review_required", False, "unknown_external_boundary"
    if not task["runnable"] or task["blocked_reason"]:
        return "self_resolve", False, "blocked"
    if not task["workflow_manifest"]:
        return "inspect", False, "needs_workflow_mapping"
    return "target_workflow", True, "ready"


def normalize_task(
    payload: dict[str, Any], *, now: datetime | None = None
) -> dict[str, Any]:
    missing = sorted(REQUIRED_FIELDS - payload.keys())
    if missing:
        raise InvalidTaskError(f"missing fields: {', '.join(missing)}")
    if payload["schema"] != SCHEMA:
        raise InvalidTaskError("unsupported schema")
    try:
        validate(payload, TASK_SCHEMA, format_checker=FormatChecker())
    except ValidationError as exc:
        raise InvalidTaskError("invalid task schema") from exc
    if not isinstance(payload["task_id"], str) or not payload["task_id"].strip():
        raise InvalidTaskError("invalid task_id")
    if payload["closure_rule"] != "evidence_required":
        raise InvalidTaskError("closure_rule must be evidence_required")
    created_at = _parse_time(payload["created_at"], "created_at")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    score, reasons = _priority(payload, current)
    route, execute, state = _route(payload)
    return {
        **payload,
        "created_at": created_at.isoformat(),
        "priority_score": score,
        "priority_reasons": reasons,
        "route": route,
        "execute": execute,
        "state": state,
    }


def build_manager_plan(
    tasks: list[dict[str, Any]],
    *,
    now: datetime | None = None,
    limit: int = 3,
) -> dict[str, Any]:
    if not 1 <= limit <= 3:
        raise ValueError("limit must be between 1 and 3")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    normalized = [normalize_task(item, now=current) for item in tasks]
    task_ids = [item["task_id"] for item in normalized]
    if len(task_ids) != len(set(task_ids)):
        raise InvalidTaskError("duplicate task_id")
    normalized.sort(
        key=lambda item: (
            -item["priority_score"],
            item["created_at"],
            item["task_id"],
        )
    )
    selected = normalized[:limit]
    return {
        "schema": "fde.manager_plan.v1",
        "generated_at": current.isoformat(),
        "goal": "他者への迷惑を止め、約束を守り、証拠ある完了を増やす",
        "selected": selected,
        "queued": normalized[limit:],
        "decision_box": [
            item for item in selected if item["route"] == "human_review_required"
        ],
        "executable": [item for item in selected if item["execute"]],
        "external_actions_performed": False,
    }


def _load_tasks(path: Path) -> list[dict[str, Any]]:
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise InvalidTaskError("input exceeds 2 MiB")
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("tasks")
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise InvalidTaskError("input must be a task array or {tasks: [...]}")
    return data


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        tasks = _load_tasks(args.input)
        result = build_manager_plan(tasks, limit=args.limit)
    except (InvalidTaskError, OSError, json.JSONDecodeError, ValueError) as exc:
        result = {
            "schema": "fde.manager_plan.v1",
            "state": "blocked",
            "failure_stage": "input_validation",
            "reason": str(exc),
            "external_actions_performed": False,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
