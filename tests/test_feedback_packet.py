import json
import subprocess
import sys
from pathlib import Path

from scripts.fde_feedback_packet import validate_feedback_packet


ROOT = Path(__file__).resolve().parents[1]


def valid_packet() -> dict:
    return {
        "schema_version": "fde.feedback.v1",
        "feedback_id": "feedback-long-thread-latency-001",
        "source_run_id": "run-long-thread-baseline-001",
        "producer": "engineering-brain",
        "consumer": "fde",
        "observed_at": "2026-07-28T18:00:00+09:00",
        "plan": {
            "hypothesis": "long task reconstruction dominates open latency",
            "expected_effect": "reduce time to interactive",
            "verification_plan": ["compare short and long tasks"],
        },
        "do": {
            "actions": ["collect read-only timing"],
            "changed_artifacts": [],
        },
        "check": {
            "outcome": "partial",
            "evidence": [
                {"kind": "trace", "ref": "run-long-thread-baseline-001"}
            ],
            "human_review": "pending",
        },
        "act": {
            "decision": "revise",
            "update_targets": ["skill", "test"],
            "rollback_path": "remove the candidate detector",
            "next_plan_input": "capture renderer phase timing",
        },
        "boundaries": {
            "external_actions_performed": False,
            "human_gate_required": True,
        },
        "provenance": {
            "source_refs": [
                {"kind": "source", "ref": "rollout-metadata-summary"}
            ],
        },
    }


def test_feedback_packet_schema_accepts_a_complete_cross_repo_packet() -> None:
    errors = validate_feedback_packet(valid_packet())

    assert errors == []


def test_feedback_packet_rejects_act_without_check_evidence() -> None:
    packet = valid_packet()
    packet["check"]["evidence"] = []

    errors = validate_feedback_packet(packet)

    assert any("evidence" in error for error in errors)


def test_feedback_packet_schema_is_public_and_machine_readable() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "fde_feedback_packet.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )

    assert schema["$id"].endswith("/fde_feedback_packet.v1.schema.json")
    assert schema["properties"]["schema_version"]["const"] == "fde.feedback.v1"
    assert schema["additionalProperties"] is False


def test_feedback_packet_rejects_raw_evidence_text() -> None:
    packet = valid_packet()
    packet["check"]["evidence"] = ["raw conversation text is not a pointer"]

    errors = validate_feedback_packet(packet)

    assert any("evidence" in error for error in errors)


def test_feedback_packet_rejects_personal_path_in_next_plan() -> None:
    packet = valid_packet()
    packet["act"]["next_plan_input"] = (
        "inspect "
        + "C:"
        + chr(47)
        + "Users/alice/private/session.jsonl"
    )

    errors = validate_feedback_packet(packet)

    assert any("personal path" in error for error in errors)


def test_feedback_packet_rejects_adopt_while_human_review_is_pending() -> None:
    packet = valid_packet()
    packet["act"]["decision"] = "adopt"

    errors = validate_feedback_packet(packet)

    assert any("adopt requires approved human review" in error for error in errors)


def test_feedback_packet_rejects_secret_like_content() -> None:
    packet = valid_packet()
    packet["act"]["next_plan_input"] = "use token " + "ghp_" + ("x" * 36)

    errors = validate_feedback_packet(packet)

    assert any("secret-like" in error for error in errors)


def test_cli_reports_invalid_json_without_traceback(tmp_path: Path) -> None:
    packet_path = tmp_path / "invalid-feedback.json"
    packet_path.write_text("{not-json", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "fde_feedback_packet.py"),
            "--input",
            str(packet_path),
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["overall"] == "error"
    assert payload["errors"] == ["JSONDecodeError: invalid feedback input"]
    assert "Traceback" not in result.stderr
    assert str(packet_path) not in result.stdout
