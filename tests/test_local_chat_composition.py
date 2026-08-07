import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import scripts.fde_operational_closeout as closeout_mod
import scripts.fde_target_workflow as runner
from scripts.fde_feedback_packet import (
    draft_feedback_from_target_receipt,
    validate_feedback_packet,
)
from scripts.fde_operational_closeout import evaluate as closeout_evaluate
from scripts.fde_task_manager import build_manager_plan
from scripts.fde_target_workflow import load_manifest, run_workflow


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 7, 14, 0, tzinfo=timezone.utc)


def sample_intake():
    return {
        "owner": "composition-unit",
        "scope": "local-chat composition smoke",
        "goal": "plan then verify then draft feedback hold",
        "external_boundary": "none",
        "return_path": {"kind": "feedback_packet", "schema": "fde.feedback.v1"},
    }


def target_manifest():
    return {
        "schema": "fde.target_workflow.v1",
        "workflow_id": "composition-smoke",
        "target_id": "unit",
        "repo_root": str(ROOT),
        "approval_gate": "review_packet",
        "capabilities": {
            "process": True,
            "network": False,
            "external_write": False,
            "git_write": False,
        },
        "intake": sample_intake(),
        "checks": [
            {
                "name": "ok",
                "argv": [sys.executable, "scripts/public_ready_check.py"],
                "timeout_seconds": 30,
            }
        ],
    }


def manager_task():
    return {
        "schema": "fde.manager_task.v1",
        "task_id": "composition-1",
        "title": "run local composition smoke",
        "created_at": "2026-08-07T00:00:00Z",
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


def test_local_chat_composition_chain_plan_receipt_draft_closeout(tmp_path, monkeypatch):
    """Map contract: plan -> receipt -> feedback draft -> closeout bind.

    Reuses existing manager / runner / draft / closeout only. No new binary.
    """
    def fake_trust(manifest):
        # Return dict attestation (not True) so closeout bind can compare equality.
        return {
            "registry_id": "unit-test",
            "base_commit": "0" * 40,
            "head": "0" * 40,
            "tree": "0" * 40,
            "script_hashes": {
                item["name"]: "0" * 64 for item in manifest["checks"]
            },
        }

    monkeypatch.setattr(runner, "_verify_trust", fake_trust)
    monkeypatch.setattr(closeout_mod, "_verify_trust", fake_trust)

    plan = build_manager_plan([manager_task()], now=NOW)
    assert plan["external_actions_performed"] is False
    assert plan["selected"]
    assert plan["selected"][0]["route"] == "target_workflow"
    assert plan["selected"][0]["execute"] is True

    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(target_manifest()), encoding="utf-8")
    state_root = tmp_path / ".local"
    receipt = run_workflow(load_manifest(path), state_root=state_root)
    assert receipt["state"] == "human_review_required"
    assert receipt["external_actions_performed"] is False

    packet = draft_feedback_from_target_receipt(
        receipt,
        intake=sample_intake(),
        observed_at="2026-08-07T14:00:00+00:00",
    )
    assert validate_feedback_packet(packet) == []
    assert packet["act"]["decision"] == "hold"
    assert packet["check"]["human_review"] == "pending"
    assert packet["boundaries"]["external_actions_performed"] is False
    assert packet["act"]["decision"] != "adopt"

    receipt_path = state_root / "composition-receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    closed = closeout_evaluate(
        run_pytest=False,
        target_receipt=receipt_path,
        target_manifest=path,
    )
    assert closed["checks"]["target_workflow"]["ok"] is True, closed["checks"]["target_workflow"]
    assert closed["external_actions_performed"] is False


def test_local_chat_map_documents_composition_not_binary() -> None:
    text = (ROOT / "docs/local-chat-integration-map.md").read_text(encoding="utf-8")
    assert "chat-orchestrator" in text
    assert "fde.feedback.v1" in text
    assert "fde_operational_closeout.py" in text
    assert "composition" in text.lower() or "Composition" in text
    assert "not a new executable" in text or "新規 binary" in text or "not a new binary" in text


def test_contact_schema_pins_next_contact_allowed_false() -> None:
    schema = json.loads(
        (ROOT / "schemas/fde_contact_packet.v1.schema.json").read_text(encoding="utf-8")
    )
    next_allowed = schema["properties"]["closure"]["properties"]["next_contact_allowed"]
    assert next_allowed.get("const") is False
