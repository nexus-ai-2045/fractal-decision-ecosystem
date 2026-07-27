from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.fde_task_manager import (
    InvalidTaskError,
    build_manager_plan,
    normalize_task,
)


NOW = datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc)


def task(task_id: str, **overrides):
    payload = {
        "schema": "fde.manager_task.v1",
        "task_id": task_id,
        "title": task_id,
        "created_at": "2026-07-26T00:00:00Z",
        "people_impact": "none",
        "commitment": "none",
        "deadline": None,
        "harm_risk": "none",
        "external_boundary": "none",
        "runnable": True,
        "blocked_reason": None,
        "workflow_manifest": "examples/dcb_target_workflow.json",
        "target_repo": "C:/repo",
        "closure_rule": "evidence_required",
    }
    payload.update(overrides)
    return payload


def test_trust_and_commitment_impact_outrank_internal_improvement():
    plan = build_manager_plan(
        [
            task("internal", title="内部基盤を改善"),
            task(
                "promise",
                people_impact="waiting_person",
                commitment="explicit",
                deadline="2026-07-27T10:00:00Z",
                harm_risk="reputation",
            ),
        ],
        now=NOW,
    )

    assert [item["task_id"] for item in plan["selected"]] == [
        "promise",
        "internal",
    ]
    assert plan["selected"][0]["priority_reasons"][:3] == [
        "overdue",
        "explicit_commitment",
        "waiting_person",
    ]


def test_external_boundary_goes_to_decision_box_without_execution():
    plan = build_manager_plan(
        [
            task(
                "push",
                external_boundary="git_push",
                people_impact="waiting_person",
                commitment="explicit",
            )
        ],
        now=NOW,
    )

    item = plan["selected"][0]
    assert item["route"] == "human_review_required"
    assert item["execute"] is False
    assert plan["decision_box"][0]["task_id"] == "push"


def test_safe_registered_workflow_is_only_declared_ready():
    plan = build_manager_plan([task("safe")], now=NOW)

    item = plan["selected"][0]
    assert item["route"] == "target_workflow"
    assert item["execute"] is True
    assert item["closure_rule"] == "evidence_required"
    assert plan["external_actions_performed"] is False


def test_manager_limits_active_batch_to_three_and_orders_oldest_first_on_tie():
    tasks = [
        task("new", created_at="2026-07-27T09:00:00Z"),
        task("oldest", created_at="2026-07-20T09:00:00Z"),
        task("middle", created_at="2026-07-25T09:00:00Z"),
        task("fourth", created_at="2026-07-26T09:00:00Z"),
    ]

    plan = build_manager_plan(tasks, now=NOW, limit=3)

    assert [item["task_id"] for item in plan["selected"]] == [
        "oldest",
        "middle",
        "fourth",
    ]
    assert [item["task_id"] for item in plan["queued"]] == ["new"]


def test_blocked_task_is_routed_to_self_resolve_not_marked_done():
    plan = build_manager_plan(
        [
            task(
                "blocked",
                runnable=False,
                blocked_reason="runtime_unavailable",
            )
        ],
        now=NOW,
    )

    item = plan["selected"][0]
    assert item["route"] == "self_resolve"
    assert item["execute"] is False
    assert item["state"] == "blocked"


def test_required_manager_fields_fail_closed():
    payload = task("missing")
    del payload["closure_rule"]

    with pytest.raises(InvalidTaskError, match="closure_rule"):
        normalize_task(payload, now=NOW)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("people_impact", "maybe"),
        ("commitment", "probably"),
        ("harm_risk", "catastrophic"),
        ("runnable", "yes"),
    ],
)
def test_task_schema_rejects_ambiguous_values(field, value):
    with pytest.raises(InvalidTaskError, match="invalid task schema"):
        normalize_task(task("ambiguous", **{field: value}), now=NOW)


def test_task_schema_rejects_uncontracted_fields():
    with pytest.raises(InvalidTaskError, match="invalid task schema"):
        normalize_task(task("extra", guessed_priority=999), now=NOW)


def test_manager_rejects_duplicate_task_ids():
    with pytest.raises(InvalidTaskError, match="duplicate task_id"):
        build_manager_plan([task("same"), task("same")], now=NOW)


def test_manager_rejects_oversized_input_file(tmp_path):
    path = tmp_path / "too-large.json"
    path.write_bytes(b" " * (2 * 1024 * 1024 + 1))
    completed = subprocess.run(
        [sys.executable, "scripts/fde_task_manager.py", str(path), "--json"],
        cwd=Path(__file__).resolve().parents[1],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 1
    assert json.loads(completed.stdout)["reason"] == "input exceeds 2 MiB"


def test_cli_emits_plan_without_runtime_execution_and_preserves_utf8(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text(
        json.dumps(
            {"tasks": [task("safe", title="日本語の安全な案件")]},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, "scripts/fde_task_manager.py", str(path), "--json"],
        cwd=Path(__file__).resolve().parents[1],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["selected"][0]["task_id"] == "safe"
    assert payload["selected"][0]["title"] == "日本語の安全な案件"
    assert "results" not in payload
    assert payload["external_actions_performed"] is False
