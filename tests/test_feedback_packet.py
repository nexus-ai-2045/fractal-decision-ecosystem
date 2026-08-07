import json
import subprocess
import sys
from pathlib import Path

from scripts.fde_feedback_packet import (
    draft_feedback_from_target_receipt,
    feedback_packet_sha256,
    validate_feedback_packet,
)


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
            "failure_kind": "insufficient_evidence",
            "update_targets": ["skill", "test"],
            "regression_test": "tests/test_feedback_packet.py",
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


def test_validation_errors_do_not_echo_rejected_secret() -> None:
    packet = valid_packet()
    secret = "Bearer " + ("x" * 32)
    packet["check"]["evidence"][0]["ref"] = secret

    errors = validate_feedback_packet(packet)

    assert errors
    assert secret not in json.dumps(errors)


def test_rejects_fine_grained_github_token_and_paths_in_any_field() -> None:
    packet = valid_packet()
    packet["plan"]["hypothesis"] = "github_pat_" + ("x" * 40)
    packet["do"]["changed_artifacts"] = [
        chr(47) + "home/alice/private/trace.json"
    ]

    errors = validate_feedback_packet(packet)

    assert any("secret-like" in error for error in errors)
    assert any("personal path" in error for error in errors)


def test_rejected_review_cannot_be_adopted_even_without_required_gate() -> None:
    packet = valid_packet()
    packet["check"]["human_review"] = "rejected"
    packet["boundaries"]["human_gate_required"] = False
    packet["act"]["decision"] = "adopt"

    assert any("conflicts with rejected" in error for error in validate_feedback_packet(packet))


def test_packet_collections_are_bounded() -> None:
    packet = valid_packet()
    packet["do"]["actions"] = ["step"] * 17

    assert validate_feedback_packet(packet)


def test_unpaired_surrogate_is_rejected() -> None:
    packet = valid_packet()
    packet["feedback_id"] = "\ud800"

    assert any("Unicode surrogate" in error for error in validate_feedback_packet(packet))


def test_cli_redacts_secret_bearing_feedback_id(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["feedback_id"] = "ghp_" + ("x" * 36)
    packet_path = tmp_path / "feedback.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

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
    assert json.loads(result.stdout)["feedback_id"] is None


def test_cli_redacts_secret_bearing_schema_version(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["schema_version"] = "ghp_" + ("x" * 36)
    packet_path = tmp_path / "feedback.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

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

    assert json.loads(result.stdout)["schema_version"] is None


def test_valid_non_bmp_character_is_accepted() -> None:
    packet = valid_packet()
    packet["plan"]["hypothesis"] = "emoji is valid: \U0001f680"

    assert validate_feedback_packet(packet) == []


def test_personal_path_variants_are_rejected() -> None:
    for value in (
        chr(47) + "root/.codex/auth.json",
        "C:" + chr(47) + "users/alice/private.json",
    ):
        packet = valid_packet()
        packet["plan"]["hypothesis"] = value
        assert any("personal path" in error for error in validate_feedback_packet(packet))


def test_adopt_requires_fde_owned_approval_context() -> None:
    packet = valid_packet()
    packet["check"]["human_review"] = "approved"
    packet["boundaries"]["human_gate_required"] = False
    packet["act"]["decision"] = "adopt"

    assert any("FDE approval context" in error for error in validate_feedback_packet(packet))
    assert validate_feedback_packet(
        packet, approved_packet_sha256={feedback_packet_sha256(packet)}
    ) == []


def test_adopt_approval_is_bound_to_exact_packet_content() -> None:
    packet = valid_packet()
    packet["check"]["human_review"] = "approved"
    packet["boundaries"]["human_gate_required"] = False
    packet["act"]["decision"] = "adopt"
    approved_digest = feedback_packet_sha256(packet)

    packet["act"]["next_plan_input"] = "different action after approval"

    assert any(
        "FDE approval context" in error
        for error in validate_feedback_packet(
            packet, approved_packet_sha256={approved_digest}
        )
    )


def test_cli_redacts_personal_path_bearing_feedback_id(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["feedback_id"] = chr(47) + "home/alice/private"
    packet_path = tmp_path / "feedback.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

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

    assert json.loads(result.stdout)["feedback_id"] is None


def test_cli_only_echoes_schema_valid_identifiers(tmp_path: Path) -> None:
    for field, invalid_value in (
        ("schema_version", ["fde.feedback.v1"]),
        ("feedback_id", "x" * 129),
    ):
        packet = valid_packet()
        packet[field] = invalid_value
        packet_path = tmp_path / f"invalid-{field}.json"
        packet_path.write_text(json.dumps(packet), encoding="utf-8")

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
        assert json.loads(result.stdout)[field] is None


def test_feedback_packet_rejects_non_fde_consumer() -> None:
    packet = valid_packet()
    packet["consumer"] = "another-controller"

    errors = validate_feedback_packet(packet)

    assert any("consumer" in error for error in errors)


def test_cli_rejects_non_finite_json_constants(tmp_path: Path) -> None:
    packet_path = tmp_path / "nan.json"
    packet_path.write_text('{"feedback_id": NaN}', encoding="utf-8")

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
    assert json.loads(result.stdout)["errors"] == [
        "ValueError: invalid feedback input"
    ]
    assert "NaN" not in result.stdout


def test_programmatic_validator_rejects_non_finite_value_without_raising() -> None:
    packet = valid_packet()
    packet["plan"]["hypothesis"] = float("nan")

    errors = validate_feedback_packet(packet)

    assert "<root>: invalid JSON value" in errors


def test_private_key_marker_is_rejected() -> None:
    packet = valid_packet()
    packet["act"]["next_plan_input"] = (
        "-----BEGIN " + "OPENSSH PRIVATE KEY-----"
    )

    assert any(
        "secret-like" in error for error in validate_feedback_packet(packet)
    )


def test_additional_secret_formats_are_rejected() -> None:
    for secret in (
        "xoxb-" + ("A" * 48),
        "AKIA" + ("A" * 16),
        "npm_" + ("A" * 32),
    ):
        packet = valid_packet()
        packet["act"]["next_plan_input"] = secret
        assert any(
            "secret-like" in error
            for error in validate_feedback_packet(packet)
        )


def test_unc_user_path_is_rejected() -> None:
    packet = valid_packet()
    packet["act"]["next_plan_input"] = (
        chr(92) * 2 + "fileserver" + chr(92) + "users"
        + chr(92) + "alice" + chr(92) + "private.json"
    )

    assert any(
        "personal path" in error for error in validate_feedback_packet(packet)
    )


def test_cli_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    packet_path = tmp_path / "duplicate.json"
    packet_path.write_text(
        '{"act":{"decision":"adopt","decision":"revise"}}',
        encoding="utf-8",
    )

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
    assert json.loads(result.stdout)["errors"] == [
        "ValueError: invalid feedback input"
    ]


def test_bare_root_home_path_is_rejected() -> None:
    packet = valid_packet()
    packet["act"]["next_plan_input"] = chr(47) + "root"

    assert any(
        "personal path" in error for error in validate_feedback_packet(packet)
    )


def test_schema_uses_canonical_feedback_contract_fields_and_targets() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "fde_feedback_packet.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    act = schema["properties"]["act"]

    assert {"failure_kind", "regression_test"} <= set(act["required"])
    assert act["properties"]["update_targets"]["items"]["enum"] == [
        "route",
        "skill",
        "gate",
        "test",
        "ssot",
        "roadmap",
        "none",
    ]


def test_timestamp_requires_timezone_offset() -> None:
    packet = valid_packet()
    packet["observed_at"] = "2026-07-28T18:00:00"

    assert any("date-time" in error for error in validate_feedback_packet(packet))


def test_timestamp_rejects_iso_week_date_outside_rfc3339() -> None:
    packet = valid_packet()
    packet["observed_at"] = "2026-W31-2T18:00:00+09:00"

    assert any("date-time" in error for error in validate_feedback_packet(packet))


def test_secret_scan_matches_bearer_case_insensitively() -> None:
    packet = valid_packet()
    packet["plan"]["hypothesis"] = "bearer " + ("x" * 32)

    assert any("secret-like" in error for error in validate_feedback_packet(packet))


def test_secret_scan_accepts_rfc6750_bearer_and_pgp_block() -> None:
    for secret in (
        "Bearer abcd+efghijklmnopqrstuvwxyz",
        "-----BEGIN PGP PRIVATE KEY BLOCK-----",
    ):
        packet = valid_packet()
        packet["act"]["next_plan_input"] = secret
        assert any(
            "secret-like" in error for error in validate_feedback_packet(packet)
        )


def test_successful_run_allows_none_update_target() -> None:
    packet = valid_packet()
    packet["check"]["outcome"] = "met"
    packet["act"]["failure_kind"] = "none"
    packet["act"]["update_targets"] = ["none"]
    packet["act"]["decision"] = "hold"

    assert validate_feedback_packet(packet) == []


def test_none_update_target_requires_failure_kind_none() -> None:
    packet = valid_packet()
    packet["act"]["failure_kind"] = "insufficient_evidence"
    packet["act"]["update_targets"] = ["none"]

    assert any(
        "none is only valid" in error for error in validate_feedback_packet(packet)
    )


def test_failure_kind_none_requires_only_none_target() -> None:
    packet = valid_packet()
    packet["act"]["failure_kind"] = "none"
    packet["act"]["update_targets"] = ["skill"]

    assert any(
        'failure_kind none requires ["none"]' in error
        for error in validate_feedback_packet(packet)
    )


def test_whitespace_only_required_strings_are_rejected() -> None:
    packet = valid_packet()
    packet["feedback_id"] = " "
    packet["plan"]["hypothesis"] = "   "
    packet["act"]["next_plan_input"] = "\t"

    errors = validate_feedback_packet(packet)

    assert any("feedback_id" in error for error in errors)
    assert any("hypothesis" in error for error in errors)
    assert any("next_plan_input" in error for error in errors)


def test_cli_rejects_oversized_input_before_parse(tmp_path: Path) -> None:
    packet_path = tmp_path / "huge.json"
    packet_path.write_bytes(b" " * ((128 * 1024) + 1))

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
    assert payload["errors"] == ["ValueError: invalid feedback input"]
    assert "Traceback" not in result.stderr


def test_cli_converts_excessive_json_depth_to_structured_error(tmp_path: Path) -> None:
    packet_path = tmp_path / "deep.json"
    packet_path.write_text('{"x":' + ("[" * 10000) + "0" + ("]" * 10000) + "}", encoding="utf-8")

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
    assert payload["errors"] == ["RecursionError: invalid feedback input"]
    assert "Traceback" not in result.stderr


def sample_success_receipt() -> dict:
    return {
        "schema": "fde.target_workflow_receipt.v1",
        "workflow_id": "unit-success",
        "manifest_digest": "a" * 64,
        "state": "human_review_required",
        "approval_gate": "review_packet",
        "checks": [
            {
                "name": "ok",
                "check_digest": "b" * 64,
                "status": "passed",
                "exit_code": 0,
                "duration_ms": 12,
                "output_digest": "c" * 64,
            }
        ],
        "expected_check_count": 1,
        "implementation_residue": "none",
        "operation_residue": "human_review_required",
        "external_public_residue": "approval_gated",
        "external_actions_performed": False,
    }


def sample_failed_receipt() -> dict:
    return {
        "schema": "fde.target_workflow_receipt.v1",
        "workflow_id": "unit-failed",
        "manifest_digest": "d" * 64,
        "state": "blocked",
        "approval_gate": "review_packet",
        "checks": [
            {
                "name": "ok",
                "check_digest": "e" * 64,
                "status": "passed",
                "exit_code": 0,
                "duration_ms": 3,
                "output_digest": "f" * 64,
            },
            {
                "name": "bad",
                "check_digest": "1" * 64,
                "status": "failed",
                "exit_code": 1,
                "duration_ms": 4,
                "output_digest": "2" * 64,
            },
        ],
        "expected_check_count": 2,
        "implementation_residue": "check_failed",
        "operation_residue": "retry_required",
        "external_public_residue": "approval_gated",
        "external_actions_performed": False,
    }


def sample_intake() -> dict:
    return {
        "owner": "unit-test",
        "scope": "target-workflow-draft",
        "goal": "stop at review packet and draft feedback",
        "external_boundary": "none",
        "return_path": {"kind": "feedback_packet", "schema": "fde.feedback.v1"},
    }


def test_draft_from_success_receipt_is_valid_hold_pending() -> None:
    packet = draft_feedback_from_target_receipt(
        sample_success_receipt(),
        intake=sample_intake(),
        observed_at="2026-08-07T12:00:00+00:00",
    )
    assert validate_feedback_packet(packet) == []
    assert packet["act"]["decision"] == "hold"
    assert packet["check"]["human_review"] == "pending"
    assert packet["check"]["outcome"] == "met"
    assert packet["act"]["failure_kind"] == "none"
    assert packet["act"]["update_targets"] == ["none"]
    assert packet["boundaries"]["external_actions_performed"] is False
    assert packet["boundaries"]["human_gate_required"] is True
    rendered = json.dumps(packet)
    assert "C:\\" not in rendered
    assert "/Users/" not in rendered
    assert "adopt" not in rendered


def test_draft_from_failed_receipt_is_valid_revise() -> None:
    packet = draft_feedback_from_target_receipt(
        sample_failed_receipt(),
        intake=sample_intake(),
        observed_at="2026-08-07T12:00:00+00:00",
    )
    assert validate_feedback_packet(packet) == []
    assert packet["act"]["decision"] == "revise"
    assert packet["check"]["outcome"] == "not_met"
    assert packet["act"]["failure_kind"] == "check_failed"
    assert "none" not in packet["act"]["update_targets"]
    assert packet["check"]["human_review"] == "pending"


def test_draft_rejects_bad_return_path_schema() -> None:
    intake = sample_intake()
    intake["return_path"]["schema"] = "fde.feedback.v0"
    try:
        draft_feedback_from_target_receipt(sample_success_receipt(), intake=intake)
        raised = False
    except ValueError as error:
        raised = True
        assert "fde.feedback.v1" in str(error)
    assert raised


def test_draft_never_emits_adopt_decision() -> None:
    packet = draft_feedback_from_target_receipt(
        sample_success_receipt(),
        intake=sample_intake(),
        observed_at="2026-08-07T12:00:00+00:00",
    )
    assert packet["act"]["decision"] != "adopt"
    # adopt would fail validation without approval context
    packet["act"]["decision"] = "adopt"
    errors = validate_feedback_packet(packet)
    assert any("adopt" in error for error in errors)


def test_cli_draft_from_receipt_and_write(tmp_path: Path) -> None:
    # --write is confined to the process CWD (repo root in this test).
    work = ROOT / ".local" / "feedback-draft-cli-test"
    work.mkdir(parents=True, exist_ok=True)
    receipt_path = work / "receipt.json"
    manifest_path = work / "manifest.json"
    out_path = work / "draft.json"
    receipt_path.write_text(json.dumps(sample_success_receipt()), encoding="utf-8")
    manifest_path.write_text(
        json.dumps(
            {
                "schema": "fde.target_workflow.v1",
                "intake": sample_intake(),
            }
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "fde_feedback_packet.py"),
            "--from-receipt",
            str(receipt_path),
            "--manifest",
            str(manifest_path),
            "--write",
            str(out_path),
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
    assert payload["mode"] == "draft"
    assert payload["act_decision"] == "hold"
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written["schema_version"] == "fde.feedback.v1"
    assert written["act"]["decision"] == "hold"


def test_cli_requires_exactly_one_of_input_or_from_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "fde_feedback_packet.py"),
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

def test_draft_from_trust_review_receipt_is_revise() -> None:
    receipt = sample_success_receipt()
    receipt["state"] = "trust_review_required"
    packet = draft_feedback_from_target_receipt(
        receipt,
        intake=sample_intake(),
        observed_at="2026-08-07T12:00:00+00:00",
    )
    assert validate_feedback_packet(packet) == []
    assert packet["act"]["decision"] == "revise"
    assert packet["act"]["failure_kind"] == "trust_or_lock"
    assert packet["check"]["human_review"] == "pending"
    assert packet["act"]["decision"] != "adopt"


def test_draft_from_locked_receipt_is_revise() -> None:
    receipt = sample_success_receipt()
    receipt["state"] = "locked"
    packet = draft_feedback_from_target_receipt(
        receipt,
        intake=sample_intake(),
        observed_at="2026-08-07T12:00:00+00:00",
    )
    assert validate_feedback_packet(packet) == []
    assert packet["act"]["decision"] == "revise"
    assert packet["act"]["failure_kind"] == "trust_or_lock"


def test_cli_rejects_write_outside_cwd(tmp_path: Path) -> None:
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(sample_success_receipt()), encoding="utf-8")
    outside = Path.cwd().resolve().parent / "fde-feedback-draft-outside.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "fde_feedback_packet.py"),
            "--from-receipt",
            str(receipt_path),
            "--write",
            str(outside),
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
    assert not outside.exists()
