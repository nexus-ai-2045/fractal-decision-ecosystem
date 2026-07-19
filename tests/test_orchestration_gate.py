"""Team formation / orchestration gate の packet validation と docs contract テスト。"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from scripts import public_ready_check
from scripts.orchestration_gate_check import evaluate
from scripts.orchestration_gate_check import evaluate_packet
from scripts.orchestration_gate_check import main as orchestration_gate_main


ROOT = public_ready_check.ROOT


def _packet(**overrides: str) -> str:
    base = {
        "question": "summarize the diff for review",
        "mode": "review",
        "execution_mode": "delegate",
        "orchestration_required": "yes",
        "orchestration_reason": "multiple files need parallel summary",
        "delegate_plan": "Spark summarizes; Codex adopts",
        "codex_main_role": "adoption and minimal patch",
        "return_to": "main closeout",
        "precheck": "live todo matches",
        "route_mode": "balanced",
        "budget": "token: low",
        "team_plan": "yes",
        "task": "diff summary",
        "roles": "spark summarizer, codex integrator",
        "return_contract": "changed files table",
        "adoption_gate": "codex local fact check",
        "stopline_owner": "codex",
        "spark_candidate": "yes",
        "routing_decision": "spark_delegate",
        "thin_source_route": "spark",
        "risk": "low",
    }
    base.update(overrides)
    return "\n".join(f"{key}: {value}" for key, value in base.items()) + "\n"


def _without_fields(text: str, *fields: str) -> str:
    prefixes = tuple(f"{field}:" for field in fields)
    lines = [line for line in text.splitlines() if not line.startswith(prefixes)]
    return "\n".join(lines) + "\n"


def _assert_errors(text: str, *needles: str) -> None:
    errors = evaluate_packet(text)
    assert errors, f"expected packet errors, got none for:\n{text}"
    joined = "\n".join(errors)
    for needle in needles:
        assert needle.lower() in joined.lower(), f"missing {needle!r} in errors:\n{joined}"


def test_orchestration_gate_docs_pass() -> None:
    result = evaluate()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert isinstance(result["errors"], list)
    assert isinstance(result["docs"], dict)
    assert result["packet"] is None


def test_packet_requires_orchestration_required() -> None:
    _assert_errors(_without_fields(_packet(), "orchestration_required"), "orchestration_required")


def test_packet_no_requires_reason() -> None:
    _assert_errors(
        _without_fields(_packet(orchestration_required="no"), "orchestration_reason"),
        "orchestration_reason",
    )


def test_packet_yes_requires_delegate_fields() -> None:
    for field in (
        "delegate_plan",
        "codex_main_role",
        "return_to",
        "precheck",
        "route_mode",
        "budget",
    ):
        _assert_errors(_without_fields(_packet(), field), field)


def test_packet_yes_requires_team_plan_or_no_team_reason() -> None:
    _assert_errors(
        _without_fields(_packet(), "team_plan", "no_team_reason"),
        "team_plan",
        "no_team_reason",
    )


def test_packet_team_plan_requires_minimum_fields() -> None:
    for field in (
        "task",
        "roles",
        "delegate_plan",
        "return_contract",
        "adoption_gate",
        "stopline_owner",
    ):
        _assert_errors(_without_fields(_packet(team_plan="yes"), field), field)


@pytest.mark.parametrize(
    ("language", "needle"),
    [
        ("Type1 audit before send", "type1"),
        ("risk: high with final decision", "final decision"),
        ("publication approval required", "publication"),
    ],
)
def test_spark_delegate_cannot_own_type1_or_final_decision(language: str, needle: str) -> None:
    text = _packet(question=language, delegate_plan=language, routing_decision="spark_delegate")
    _assert_errors(text, "spark_delegate", needle)


@pytest.mark.parametrize(
    "spark_phrase",
    [
        "diff要約 for review",
        "build a 比較表 for options",
        "format the test log output",
    ],
)
def test_spark_suitable_task_requires_spark_candidate(spark_phrase: str) -> None:
    text = _without_fields(
        _packet(question=spark_phrase, delegate_plan=spark_phrase),
        "spark_candidate",
    )
    _assert_errors(text, "spark_candidate")


def test_valid_spark_delegate_packet_passes() -> None:
    assert evaluate_packet(_packet()) == []


def test_cli_json_ok(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["orchestration_gate_check", "--json"])
    assert orchestration_gate_main() == 0

    result = subprocess.run(
        [sys.executable, "-m", "scripts.orchestration_gate_check", "--json"],
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["overall"] == "ok"
    assert payload["external_actions_performed"] is False
