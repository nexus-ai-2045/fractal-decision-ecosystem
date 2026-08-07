import json
import subprocess
import sys
from pathlib import Path

from scripts.fde_team_plan import (
    evaluate_team_plan,
    sample_no_team_reason,
    sample_team_plan,
    validate_team_plan,
)

ROOT = Path(__file__).resolve().parents[1]


def test_team_plan_valid() -> None:
    packet = sample_team_plan()
    assert validate_team_plan(packet) == []
    result = evaluate_team_plan(packet)
    assert result["overall"] == "ok"
    assert result["kind"] == "team_plan"
    assert result["final_decision_retained_by_main"] is True
    assert result["external_actions_performed"] is False


def test_no_team_reason_valid() -> None:
    packet = sample_no_team_reason()
    assert validate_team_plan(packet) == []
    result = evaluate_team_plan(packet)
    assert result["overall"] == "ok"
    assert result["kind"] == "no_team_reason"


def test_forbidden_delegate_return_rejected() -> None:
    packet = sample_team_plan()
    packet["delegate_plan"][0]["returns"] = ["final_decision", "evidence"]
    errors = validate_team_plan(packet)
    assert any("final_decision" in error for error in errors)


def test_stopline_owner_cannot_be_delegate() -> None:
    packet = sample_team_plan()
    packet["stopline_owner"] = "delegate"
    errors = validate_team_plan(packet)
    assert errors


def test_missing_reason_on_no_team_fails() -> None:
    packet = sample_no_team_reason()
    del packet["reason"]
    errors = validate_team_plan(packet)
    assert errors


def test_personal_path_rejected() -> None:
    packet = sample_team_plan()
    packet["task"] = "inspect " + "C:" + chr(47) + "Users/alice/private"
    errors = validate_team_plan(packet)
    assert any("personal path" in error for error in errors)


def test_schema_const() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "fde_team_plan.v1.schema.json").read_text(encoding="utf-8")
    )
    assert schema["oneOf"][0]["properties"]["schema_version"]["const"] == "fde.team_plan.v1"
    assert schema["oneOf"][0]["properties"]["kind"]["const"] == "team_plan"
    assert schema["oneOf"][1]["properties"]["kind"]["const"] == "no_team_reason"


def test_cli_ok(tmp_path: Path) -> None:
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(sample_team_plan()), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "fde_team_plan.py"),
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
    assert payload["kind"] == "team_plan"


def test_adr_and_roadmap_reference_machine_schema() -> None:
    adr = (ROOT / "decisions" / "ADR-0004-team-formation-orchestration-gate.md").read_text(
        encoding="utf-8"
    )
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    assert "schemas/fde_team_plan.v1.schema.json" in adr
    assert "scripts/fde_team_plan.py" in adr
    assert "fde.team_plan.v1" in roadmap or "fde_team_plan" in roadmap
