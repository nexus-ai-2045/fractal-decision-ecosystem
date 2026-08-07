import json
import subprocess
import sys
from pathlib import Path

from scripts.fde_contact_packet import (
    evaluate_contact_packet,
    sample_complete_packet,
    validate_contact_packet,
)

ROOT = Path(__file__).resolve().parents[1]


def test_schema_accepts_complete_unapproved_transport_packet() -> None:
    packet = sample_complete_packet()
    assert validate_contact_packet(packet) == []
    result = evaluate_contact_packet(packet)
    assert result["overall"] == "ok"
    assert result["gate"] == "review_ready"
    assert result["contact_action"] == "blocked"
    assert result["transport_adapter_approved"] is False
    assert result["external_actions_performed"] is False
    assert "transport_unapproved_contact_blocked" in result["blocked_reasons"]


def test_missing_ttl_blocks_contact() -> None:
    packet = sample_complete_packet()
    del packet["data_boundary"]["ttl"]
    result = evaluate_contact_packet(packet)
    assert result["overall"] == "error"
    assert result["contact_action"] == "blocked"
    assert any("missing:ttl" in reason for reason in result["blocked_reasons"])


def test_transport_approved_is_rejected() -> None:
    packet = sample_complete_packet()
    packet["safety"]["transport_adapter_status"] = "approved"
    errors = validate_contact_packet(packet)
    assert any("transport_adapter_status" in error for error in errors)
    result = evaluate_contact_packet(packet)
    assert result["overall"] == "error"
    assert result["transport_adapter_approved"] is False


def test_next_contact_allowed_true_is_rejected() -> None:
    packet = sample_complete_packet()
    packet["closure"]["next_contact_allowed"] = True
    errors = validate_contact_packet(packet)
    assert any("next_contact_allowed" in error for error in errors)


def test_personal_path_and_secret_are_rejected() -> None:
    packet = sample_complete_packet()
    packet["purpose"] = "inspect " + "C:" + chr(47) + "Users/alice/secret.json"
    packet["consent"]["consent_scope"] = "token " + "ghp_" + ("x" * 36)
    errors = validate_contact_packet(packet)
    assert any("personal path" in error for error in errors)
    assert any("secret-like" in error for error in errors)


def test_schema_file_is_public_and_const_version() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "fde_contact_packet.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert schema["properties"]["schema_version"]["const"] == "fde.contact_packet.v1"
    assert (
        schema["properties"]["safety"]["properties"]["transport_adapter_status"]["const"]
        == "unapproved"
    )
    assert schema["additionalProperties"] is False


def test_cli_evaluate_complete_packet(tmp_path: Path) -> None:
    path = tmp_path / "contact.json"
    path.write_text(json.dumps(sample_complete_packet()), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "fde_contact_packet.py"),
            "--input",
            str(path),
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    payload = json.loads(result.stdout)
    assert payload["overall"] == "ok"
    assert payload["gate"] == "review_ready"
    assert payload["contact_action"] == "blocked"
    assert payload["external_actions_performed"] is False


def test_contract_points_to_machine_schema() -> None:
    text = (ROOT / "ai-contact-safety-contract.md").read_text(encoding="utf-8")
    assert "schemas/fde_contact_packet.v1.schema.json" in text
    assert "fde.contact_packet.v1" in text
    assert "scripts/fde_contact_packet.py" in text
