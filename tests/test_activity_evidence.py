import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.fde_activity_evidence import (
    MAX_ACTIVITY_EVIDENCE_BYTES,
    load_activity_evidence,
    validate_activity_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
HEX_A = "a" * 64
HEX_B = "b" * 64


def valid_packet() -> dict:
    return {
        "schema": "fde.activity-evidence.v1",
        "event_id": HEX_A,
        "content_hash": HEX_B,
        "actor_type": "human",
        "identity_status": "verified",
        "source": "manual",
        "occurred_at": "2026-08-10T12:00:00+09:00",
        "provenance": {
            "generated_by": None,
            "derived_from": [],
            "parent_event_id": None,
            "trace_id": None,
        },
    }


def test_schema_accepts_existing_activity_log_contract() -> None:
    assert validate_activity_evidence(valid_packet()) == []


def test_schema_accepts_opaque_provenance_ids() -> None:
    packet = valid_packet()
    packet["provenance"] = {
        "generated_by": "nexus-activity-log.v2",
        "derived_from": [HEX_B, "event:upstream-1"],
        "parent_event_id": HEX_B,
        "trace_id": "trace:01HXYZ",
    }
    assert validate_activity_evidence(packet) == []


def test_schema_is_closed_and_machine_readable() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "fde_activity_evidence.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert schema["properties"]["schema"]["const"] == "fde.activity-evidence.v1"
    assert schema["additionalProperties"] is False
    assert schema["properties"]["event_id"]["pattern"] == "^[0-9a-f]{64}$"


@pytest.mark.parametrize("field", ["content", "raw_text", "message", "prompt", "response", "url", "destination"])
def test_rejects_raw_or_routing_fields(field: str) -> None:
    packet = valid_packet()
    packet[field] = "must not cross the boundary"
    assert validate_activity_evidence(packet)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("event_id", "event-1"),
        ("content_hash", "A" * 64),
        ("actor_type", "person"),
        ("identity_status", "trusted"),
        ("occurred_at", "2026-08-10T12:00:00"),
    ],
)
def test_rejects_invalid_identity_or_time_fields(field: str, value: str) -> None:
    packet = valid_packet()
    packet[field] = value
    assert validate_activity_evidence(packet)


@pytest.mark.parametrize(
    "value",
    [
        "C:" + "\\" + "Users" + "\\" + "someone" + "\\private.txt",
        "ghp_" + "a" * 24,
        "\ud800",
    ],
)
def test_rejects_sensitive_or_invalid_source(value: str) -> None:
    packet = valid_packet()
    packet["source"] = value
    assert validate_activity_evidence(packet)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source", "https://example.invalid/event"),
        ("source", "free form body"),
    ],
)
def test_rejects_non_opaque_allowed_field_values(field: str, value: str) -> None:
    packet = valid_packet()
    packet[field] = value
    assert validate_activity_evidence(packet)


@pytest.mark.parametrize("field", ["generated_by", "trace_id"])
def test_rejects_routing_values_inside_provenance(field: str) -> None:
    packet = valid_packet()
    packet["provenance"][field] = "https://example.invalid/private"
    assert validate_activity_evidence(packet)


@pytest.mark.parametrize("value", ["free form body", "https://example.invalid/private"])
def test_rejects_non_opaque_derived_from_values(value: str) -> None:
    packet = valid_packet()
    packet["provenance"]["derived_from"] = [value]
    assert validate_activity_evidence(packet)


def test_loader_rejects_duplicate_keys_and_non_finite_numbers(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"schema":"a","schema":"b"}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate_json_key"):
        load_activity_evidence(duplicate)

    non_finite = tmp_path / "nan.json"
    non_finite.write_text('{"value":NaN}', encoding="utf-8")
    with pytest.raises(ValueError, match="non_finite_json_number"):
        load_activity_evidence(non_finite)


def test_loader_rejects_oversized_input(tmp_path: Path) -> None:
    path = tmp_path / "large.json"
    path.write_text(" " * (MAX_ACTIVITY_EVIDENCE_BYTES + 1), encoding="utf-8")
    with pytest.raises(ValueError, match="input_too_large"):
        load_activity_evidence(path)


def test_cli_does_not_echo_input_path_or_duplicate_key(tmp_path: Path) -> None:
    path = tmp_path / "private-name.json"
    path.write_text(
        '{"attacker\\u001b[31m":"a","attacker\\u001b[31m":"b"}',
        encoding="utf-8",
    )
    completed = subprocess.run(
        [sys.executable, "scripts/fde_activity_evidence.py", "--input", str(path), "--json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1
    assert str(path) not in completed.stdout
    assert "attacker" not in completed.stdout
    assert json.loads(completed.stdout)["errors"] == ["duplicate_json_key"]


def test_cli_reports_read_only_receipt(tmp_path: Path) -> None:
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(valid_packet()), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "scripts/fde_activity_evidence.py", "--input", str(path), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["overall"] == "contract_valid"
    assert result["external_actions_performed"] is False
