#!/usr/bin/env python3
"""FDE のlocal operational closeoutを read-only JSON として返す。"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.fde_workflow_check import SYSTEM_UPDATE_TARGETS
from scripts.fde_workflow_check import evaluate as evaluate_workflow
from scripts.fde_architecture_drift_check import evaluate as evaluate_architecture_drift
from scripts.human_review_packet_check import evaluate as evaluate_human_review_packet
from scripts.no_transport_contact_check import evaluate as evaluate_no_transport_contact
from scripts.pre_publication_gate_check import evaluate as evaluate_pre_publication
from scripts.public_kernel_diff_manifest import evaluate as evaluate_public_kernel_diff
from scripts.public_ready_check import main as public_ready_main
from scripts.residual_zero_goal_check import evaluate as evaluate_residual_zero_goal
from scripts.roadmap_gate_check import evaluate as evaluate_roadmap
from scripts.verify_residual_zero_contract import evaluate as evaluate_residual_zero_contract
from scripts.visual_html_smoke import evaluate as evaluate_visual_html_smoke
from scripts.fde_target_workflow import _verify_trust, load_manifest

RUNTIME_DIR = ROOT / ".fde-runtime"
HUMAN_REVIEW_RECEIPT = RUNTIME_DIR / "human-review-receipt.json"


def _git(args: list[str], *, allow_failure: bool = False) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0 and not allow_failure:
        detail = result.stderr.strip() or "no error output"
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def _delivery_state() -> dict[str, object]:
    git_errors: list[str] = []
    try:
        status_lines = _git(["status", "--porcelain=v1"]).splitlines()
    except RuntimeError as exc:
        status_lines = ["git_status_unavailable"]
        git_errors.append(str(exc))
    upstream = _git(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
        allow_failure=True,
    )
    ahead = 0
    behind = 0
    if upstream:
        try:
            counts = _git(["rev-list", "--left-right", "--count", f"HEAD...{upstream}"]).split()
            if len(counts) == 2 and all(value.isdigit() for value in counts):
                ahead, behind = (int(value) for value in counts)
            else:
                git_errors.append("git rev-list returned an invalid ahead/behind result")
        except RuntimeError as exc:
            git_errors.append(str(exc))

    if git_errors:
        delivery_residue = "git_state_unavailable"
    elif not upstream:
        delivery_residue = "upstream_not_configured"
    elif ahead or behind:
        delivery_residue = "branch_not_synchronized"
    else:
        delivery_residue = "none"

    return {
        "worktree_clean": not status_lines,
        "changed_entries": status_lines,
        "upstream": upstream or None,
        "ahead": ahead,
        "behind": behind,
        "delivery_residue": delivery_residue,
        "git_errors": git_errors,
    }


def _implemented_artifacts(delivery: dict[str, object], head: str) -> list[str]:
    changed_entries = delivery.get("changed_entries", [])
    implemented_artifacts = (
        list(changed_entries) if isinstance(changed_entries, list) else []
    )
    if implemented_artifacts or head == "unknown":
        return implemented_artifacts
    try:
        return _git(
            [
                "diff-tree",
                "--root",
                "--no-commit-id",
                "--name-only",
                "-r",
                "-m",
                "--first-parent",
                head,
            ]
        ).splitlines()
    except RuntimeError:
        return []


def _human_review_state(head: str) -> dict[str, object]:
    if not HUMAN_REVIEW_RECEIPT.exists():
        return {"status": "missing", "ok": False, "error": "human review receipt is missing"}
    try:
        receipt = json.loads(HUMAN_REVIEW_RECEIPT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "invalid", "ok": False, "error": str(exc)}
    try:
        current_tree = _git(["rev-parse", f"{head}^{{tree}}"])
    except RuntimeError as exc:
        return {"status": "unavailable", "ok": False, "error": str(exc)}
    required = ("schema_version", "decision", "reviewer", "reviewed_at", "reviewed_tree")
    missing = [field for field in required if not receipt.get(field)]
    tree_matches = receipt.get("reviewed_tree") == current_tree
    ok = (
        not missing
        and receipt.get("schema_version") == "fde.human-review.v1"
        and receipt.get("decision") == "approved"
        and tree_matches
    )
    return {
        "status": "approved" if ok else "invalid",
        "ok": ok,
        "reviewer": receipt.get("reviewer"),
        "reviewed_at": receipt.get("reviewed_at"),
        "reviewed_tree": receipt.get("reviewed_tree"),
        "current_tree": current_tree,
        "tree_matches": tree_matches,
        "missing_fields": missing,
    }


def _record_human_review(reviewer: str) -> Path:
    staged_files = _git(["diff", "--cached", "--name-only"]).splitlines()
    if not staged_files:
        raise RuntimeError("human review receipt requires staged changes")
    reviewed_tree = _git(["write-tree"])
    payload = {
        "schema_version": "fde.human-review.v1",
        "decision": "approved",
        "reviewer": reviewer,
        "reviewed_at": datetime.now(UTC).isoformat(),
        "reviewed_tree": reviewed_tree,
        "reviewed_files": staged_files,
    }
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    temporary = HUMAN_REVIEW_RECEIPT.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(HUMAN_REVIEW_RECEIPT)
    return HUMAN_REVIEW_RECEIPT


def _write_context_receipt(result: dict[str, object]) -> Path:
    serialized = json.dumps(result, ensure_ascii=False, sort_keys=True).encode("utf-8")
    envelope = {
        "schema_version": "fde.context.receipt.v1",
        "receipt_sha256": hashlib.sha256(serialized).hexdigest(),
        "receipt": result,
    }
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    head = str(result.get("head", "unknown"))[:12]
    history_dir = RUNTIME_DIR / "closeout-receipts"
    history_dir.mkdir(parents=True, exist_ok=True)
    target = history_dir / f"{stamp}-{head}.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    latest = RUNTIME_DIR / "closeout-receipt-latest.json"
    latest_tmp = latest.with_suffix(".tmp")
    latest_tmp.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    latest_tmp.replace(latest)
    persisted = json.loads(target.read_text(encoding="utf-8"))
    persisted_receipt = persisted.get("receipt")
    persisted_digest = hashlib.sha256(
        json.dumps(persisted_receipt, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    if (
        persisted.get("schema_version") != "fde.context.receipt.v1"
        or persisted.get("receipt_sha256") != persisted_digest
    ):
        raise RuntimeError("persisted context receipt failed its envelope hash verification")
    return target


def _context_receipt_state() -> dict[str, object]:
    latest = RUNTIME_DIR / "closeout-receipt-latest.json"
    if not latest.exists():
        return {"status": "missing", "ok": None}
    try:
        envelope = json.loads(latest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "invalid", "ok": False, "error": str(exc)}
    receipt = envelope.get("receipt")
    digest = hashlib.sha256(
        json.dumps(receipt, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    ok = (
        envelope.get("schema_version") == "fde.context.receipt.v1"
        and envelope.get("receipt_sha256") == digest
    )
    return {
        "status": "verified" if ok else "invalid",
        "ok": ok,
        "receipt_sha256": envelope.get("receipt_sha256"),
        "path": latest.relative_to(ROOT).as_posix(),
    }


def _validate_execution_receipt(
    receipt: dict[str, object],
    checks: dict[str, dict[str, object]],
    expected_transitions: list[str],
) -> list[str]:
    errors: list[str] = []
    if receipt.get("schema_version") != "fde.execution.receipt.v1":
        errors.append("execution receipt has an invalid schema_version")
    if not re.fullmatch(r"[0-9a-f]{40}", str(receipt.get("head", ""))):
        errors.append("execution receipt head is not a full commit SHA")
    expected_gate_digest = hashlib.sha256(
        json.dumps(checks, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    if receipt.get("gate_receipt_sha256") != expected_gate_digest:
        errors.append("execution receipt gate digest mismatch")
    if receipt.get("planned_transitions") != expected_transitions:
        errors.append("execution receipt planned transitions mismatch")

    transition_events = receipt.get("transition_events")
    if not isinstance(transition_events, list) or [
        event.get("transition") for event in transition_events if isinstance(event, dict)
    ] != expected_transitions:
        errors.append("execution receipt transition events mismatch")
    elif any(
        event.get("status") not in {"completed", "blocked", "skipped"}
        or not event.get("evidence")
        for event in transition_events
    ):
        errors.append("execution receipt transition event is incomplete")

    check_events = receipt.get("check_events")
    if not isinstance(check_events, list) or len(check_events) != len(checks):
        errors.append("execution receipt check events mismatch")
    else:
        event_names = [
            event.get("name") if isinstance(event, dict) else None
            for event in check_events
        ]
        if event_names != list(checks):
            errors.append("execution receipt check event names are missing, duplicated, or out of order")
        for event in check_events:
            if not isinstance(event, dict) or event.get("name") not in checks:
                errors.append("execution receipt contains an unknown check event")
                continue
            try:
                datetime.fromisoformat(str(event.get("started_at")))
                datetime.fromisoformat(str(event.get("completed_at")))
            except ValueError:
                errors.append(f"execution receipt check event has invalid time: {event.get('name')}")
            expected_digest = hashlib.sha256(
                json.dumps(checks[str(event["name"])], ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest()
            if event.get("result_sha256") != expected_digest:
                errors.append(f"execution receipt check digest mismatch: {event.get('name')}")

    verification = receipt.get("verification")
    expected_layers = {"lint", "unit", "integration", "smoke", "e2e", "regression"}
    if not isinstance(verification, dict) or set(verification) != expected_layers:
        errors.append("execution receipt verification layers mismatch")
    else:
        allowed_evidence = set(checks) | {
            "pytest:test_fde_closed_loop_e2e_contract_reaches_closeout"
        }
        for layer, record in verification.items():
            if not isinstance(record, dict) or record.get("status") not in {"applied", "waived"}:
                errors.append(f"execution receipt verification status is invalid: {layer}")
            elif record["status"] == "applied" and not record.get("evidence"):
                errors.append(f"execution receipt verification evidence is missing: {layer}")
            elif record["status"] == "waived" and not record.get("waiver"):
                errors.append(f"execution receipt verification waiver is missing: {layer}")
            elif any(
                evidence not in allowed_evidence
                for evidence in record.get("evidence", [])
            ):
                errors.append(f"execution receipt verification evidence is unknown: {layer}")
    return errors


def _run_public_ready() -> dict[str, object]:
    import contextlib
    import io

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exit_code = public_ready_main()
    return {"ok": exit_code == 0, "output": output.getvalue().strip().splitlines()}


def _run_pytest() -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "output": result.stdout.strip().splitlines(),
    }


def _run_compileall() -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "scripts", "tests"],
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {"ok": result.returncode == 0, "output": result.stdout.strip().splitlines()}


def _run_git_diff_check() -> dict[str, object]:
    result = subprocess.run(
        ["git", "diff", "--check"],
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {"ok": result.returncode == 0, "output": result.stdout.strip().splitlines()}


def _evaluate_target_workflow(
    target_receipt: Path,
    target_manifest: Path | None,
    target_repo: Path | None,
) -> dict[str, object]:
    try:
        if target_manifest is None:
            raise ValueError("target manifest required")
        receipt = json.loads(target_receipt.read_text(encoding="utf-8"))
        manifest = load_manifest(target_manifest, target_repo=target_repo)
        schema = json.loads(
            (ROOT / "schemas/fde_target_workflow_receipt.v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        validate(receipt, schema)
        expected = {
            item["name"]: hashlib.sha256(
                json.dumps(
                    item,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode()
            ).hexdigest()
            for item in manifest["checks"]
        }
        actual = {item["name"]: item.get("check_digest") for item in receipt["checks"]}
        complete = (
            len(receipt["checks"])
            == receipt["expected_check_count"]
            == len(manifest["checks"])
            and all(item.get("status") == "passed" for item in receipt["checks"])
        )
        current_trust = _verify_trust(manifest)
        bound = (
            receipt["workflow_id"] == manifest["workflow_id"]
            and receipt["manifest_digest"] == manifest["manifest_digest"]
            and actual == expected
            and isinstance(current_trust, dict)
            and receipt["trust_attestation"] == current_trust
        )
        residues = (
            receipt.get("implementation_residue") == "none"
            and receipt.get("operation_residue") == "human_review_required"
            and receipt.get("external_public_residue") == "approval_gated"
        )
        ok = (
            receipt["state"] == "human_review_required"
            and complete
            and bound
            and residues
            and receipt["external_actions_performed"] is False
        )
        return {
            "ok": ok,
            "consistency_ok": ok,
            "evidence_integrity": "local_unsealed_consistency",
            "state": receipt.get("state"),
            "manifest_digest": receipt.get("manifest_digest"),
            "operational_guarantee": "human_review_required",
            "external_actions_performed": False,
        }
    except Exception:
        return {
            "ok": False,
            "state": "receipt_invalid",
            "external_actions_performed": False,
        }


def _remote_ci_state(branch: str, head: str) -> dict[str, object]:
    try:
        result = subprocess.run(
            [
                "gh", "run", "list", "--branch", branch, "--commit", head,
                "--workflow", "Public Ready", "--limit", "1", "--json",
                "status,conclusion,url,headSha",
            ],
            cwd=ROOT,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        return {"status": "unavailable", "ok": False, "error": f"GitHub CLI could not start: {exc}"}
    if result.returncode != 0:
        return {
            "status": "unavailable",
            "ok": False,
            "error": result.stderr.strip() or "gh run list failed",
        }
    try:
        runs = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return {"status": "invalid_response", "ok": False, "error": str(exc)}
    if not runs:
        return {"status": "not_found", "ok": False, "error": "no matching Public Ready run"}
    run = runs[0]
    head_matches = run.get("headSha") == head
    return {
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "url": run.get("url"),
        "head_sha": run.get("headSha"),
        "head_matches": head_matches,
        "ok": head_matches and run.get("status") == "completed" and run.get("conclusion") == "success",
    }


def evaluate(
    run_pytest: bool = True,
    require_delivery_ready: bool = False,
    require_remote_ci: bool = False,
    target_receipt: Path | None = None,
    target_manifest: Path | None = None,
    target_repo: Path | None = None,
) -> dict[str, object]:
    check_specs = (
        ("workflow", evaluate_workflow),
        ("architecture_drift", evaluate_architecture_drift),
        ("public_ready", _run_public_ready),
        ("pre_publication", evaluate_pre_publication),
        ("roadmap", evaluate_roadmap),
        ("residual_zero_goal", evaluate_residual_zero_goal),
        ("no_transport_contact", evaluate_no_transport_contact),
        ("residual_zero_contract", evaluate_residual_zero_contract),
        ("visual_html_smoke", evaluate_visual_html_smoke),
        ("public_kernel_diff", evaluate_public_kernel_diff),
        ("human_review_packet", evaluate_human_review_packet),
        ("compileall", _run_compileall),
        ("git_diff_check", _run_git_diff_check),
    )
    checks: dict[str, dict[str, object]] = {}
    check_events: list[dict[str, object]] = []
    for name, check in check_specs:
        started_at = datetime.now(UTC).isoformat()
        try:
            result = check()
        except Exception as exc:  # fail-closed adapter boundary
            result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        completed_at = datetime.now(UTC).isoformat()
        checks[name] = result
        check_events.append(
            {
                "name": name,
                "started_at": started_at,
                "completed_at": completed_at,
                "result_sha256": hashlib.sha256(
                    json.dumps(result, ensure_ascii=False, sort_keys=True).encode("utf-8")
                ).hexdigest(),
            }
        )
    if run_pytest:
        started_at = datetime.now(UTC).isoformat()
        checks["pytest"] = _run_pytest()
        check_events.append(
            {
                "name": "pytest",
                "started_at": started_at,
                "completed_at": datetime.now(UTC).isoformat(),
                "result_sha256": hashlib.sha256(
                    json.dumps(checks["pytest"], ensure_ascii=False, sort_keys=True).encode("utf-8")
                ).hexdigest(),
            }
        )
    if target_receipt is not None:
        started_at = datetime.now(UTC).isoformat()
        checks["target_workflow"] = _evaluate_target_workflow(
            target_receipt,
            target_manifest,
            target_repo,
        )
        check_events.append(
            {
                "name": "target_workflow",
                "started_at": started_at,
                "completed_at": datetime.now(UTC).isoformat(),
                "result_sha256": hashlib.sha256(
                    json.dumps(
                        checks["target_workflow"],
                        ensure_ascii=False,
                        sort_keys=True,
                    ).encode("utf-8")
                ).hexdigest(),
            }
        )

    errors: list[str] = []
    for name, result in checks.items():
        ok = result.get("ok") if "ok" in result else result.get("overall") == "ok"
        if not ok:
            errors.append(f"{name} failed")

    try:
        branch = _git(["branch", "--show-current"])
        head = _git(["rev-parse", "HEAD"])
        relation = _git(["status", "--short", "--branch"]).splitlines()[0]
    except (RuntimeError, IndexError) as exc:
        branch = "unknown"
        head = "unknown"
        relation = "unknown"
        errors.append(f"git metadata unavailable: {exc}")
    delivery = _delivery_state()
    errors.extend(str(error) for error in delivery["git_errors"])
    remote_ci = (
        _remote_ci_state(branch, head)
        if require_remote_ci and branch != "unknown" and head != "unknown"
        else {"status": "not_checked", "ok": None}
    )
    human_review = _human_review_state(head) if head != "unknown" else {
        "status": "unavailable",
        "ok": False,
        "error": "git HEAD is unavailable",
    }
    context_receipt = _context_receipt_state()
    if context_receipt["ok"] is False:
        errors.append("persisted context receipt failed hash verification")
    gate_health_ok = not errors
    delivery_local_zero = (
        gate_health_ok
        and bool(delivery["worktree_clean"])
        and delivery["delivery_residue"] == "none"
    )
    if require_delivery_ready and not delivery["worktree_clean"]:
        errors.append("worktree has uncommitted changes")
    if require_delivery_ready and delivery["delivery_residue"] != "none":
        errors.append(f"delivery is not ready: {delivery['delivery_residue']}")
    if require_delivery_ready and not human_review["ok"]:
        errors.append(f"human review is not verified: {human_review['status']}")
    if require_remote_ci and not remote_ci["ok"]:
        errors.append(f"remote CI is not successful: {remote_ci['status']}")
    local_residual_zero = delivery_local_zero and human_review["ok"] is True
    residual_zero = local_residual_zero and remote_ci["ok"] is True
    target_review_required = bool(checks.get("target_workflow", {}).get("ok"))

    if not gate_health_ok:
        failure_kind = "gate_failure"
        system_update_target = "gate"
    elif not delivery_local_zero or not human_review["ok"]:
        failure_kind = "delivery_incomplete"
        system_update_target = "gate"
    elif remote_ci["ok"] is not True:
        failure_kind = "remote_ci_incomplete"
        system_update_target = "gate"
    else:
        failure_kind = "none"
        system_update_target = "none"

    verification_receipt = {
        "lint": {"status": "applied", "evidence": ["compileall", "git_diff_check", "workflow", "architecture_drift"]},
        "unit": {"status": "applied" if run_pytest else "waived", "evidence": ["pytest"] if run_pytest else [], "waiver": None if run_pytest else "--skip-pytest"},
        "integration": {"status": "applied", "evidence": ["pre_publication", "roadmap"]},
        "smoke": {"status": "applied", "evidence": ["visual_html_smoke"]},
        "e2e": {"status": "applied" if run_pytest else "waived", "evidence": ["pytest:test_fde_closed_loop_e2e_contract_reaches_closeout"] if run_pytest else [], "waiver": None if run_pytest else "--skip-pytest"},
        "regression": {"status": "applied" if run_pytest else "waived", "evidence": ["pytest"] if run_pytest else [], "waiver": None if run_pytest else "--skip-pytest"},
    }
    gate_receipt_sha256 = hashlib.sha256(
        json.dumps(checks, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    workflow_payload = checks.get("workflow", {}).get("workflow", {})
    transition_trace = (
        workflow_payload.get("closed_loop_transitions", [])
        if isinstance(workflow_payload, dict)
        else []
    )
    block_reasons = list(errors) or [
        f"delivery_residue={delivery['delivery_residue']}",
        f"human_review={human_review['status']}",
        f"remote_ci={remote_ci['status']}",
    ]
    planned_transitions = list(transition_trace)
    transition_events: list[dict[str, object]] = []
    for transition in planned_transitions:
        completed = gate_health_ok and (
            transition != "system_update->goal_and_boundary" or residual_zero
        )
        transition_events.append(
            {
                "transition": transition,
                "status": "completed" if completed else "blocked",
                "evidence": gate_receipt_sha256 if completed else block_reasons,
            }
        )

    rollback_path = f"git revert {head}" if delivery["worktree_clean"] else "not_available_before_commit"
    implemented_artifacts = _implemented_artifacts(delivery, head)
    feedback_receipt = {
        "failure_kind": failure_kind,
        "evidence": [gate_receipt_sha256],
        "system_update_target": system_update_target,
        "regression_test": "pytest",
        "promotion_decision": "promote" if residual_zero else "hold_until_delivery_review_and_remote_ci_ready",
        "rollback_path": rollback_path,
        "adoption_gate": {
            "human_review": human_review["status"],
            "remote_ci": remote_ci["status"],
        },
        "updated_artifact": implemented_artifacts,
    }
    receipt_contract_errors: list[str] = []
    for field in ("evidence", "rollback_path", "adoption_gate", "updated_artifact"):
        if not feedback_receipt.get(field):
            receipt_contract_errors.append(f"feedback receipt missing required field: {field}")
    target_is_valid = (
        feedback_receipt["system_update_target"] == "none"
        if feedback_receipt["failure_kind"] == "none"
        else feedback_receipt["system_update_target"] in SYSTEM_UPDATE_TARGETS
    )
    if not target_is_valid:
        receipt_contract_errors.append("feedback receipt has an unknown system_update_target")
    if receipt_contract_errors:
        errors.extend(receipt_contract_errors)

    execution_receipt = {
        "schema_version": "fde.execution.receipt.v1",
        "created_at": datetime.now(UTC).isoformat(),
        "head": head,
        "gate_receipt_sha256": gate_receipt_sha256,
        "goal": "close the FDE workflow from goal through operational guarantee and system update",
        "boundary": "repository-local implementation and operation; publication and merge approval excluded",
        "planned_transitions": planned_transitions,
        "transition_events": transition_events,
        "check_events": check_events,
        "verification": verification_receipt,
        "feedback": feedback_receipt,
        "receipt_contract": "pending_validation",
        "blockers": list(errors),
        "next_decision": "human review before commit and push" if not residual_zero else "none",
    }
    receipt_contract_errors.extend(
        _validate_execution_receipt(execution_receipt, checks, planned_transitions)
    )
    execution_receipt["receipt_contract"] = (
        "ok" if not receipt_contract_errors else "error"
    )
    if receipt_contract_errors:
        errors.extend(
            error for error in receipt_contract_errors if error not in errors
        )

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "external_action_scope": "this_check_invocation_only",
        "errors": errors,
        "branch": branch,
        "head": head,
        "branch_relation": relation,
        "gate_health": "ok" if gate_health_ok else "error",
        "implementation_residue": "none" if gate_health_ok else "unknown",
        "operation_residue": (
            "human_review_required"
            if target_review_required
            else
            "none"
            if gate_health_ok and delivery["worktree_clean"]
            else "uncommitted_changes"
            if gate_health_ok
            else "unknown"
        ),
        "delivery_residue": delivery["delivery_residue"],
        "worktree_clean": delivery["worktree_clean"],
        "changed_entries": delivery["changed_entries"],
        "upstream": delivery["upstream"],
        "ahead": delivery["ahead"],
        "behind": delivery["behind"],
        "git_errors": delivery["git_errors"],
        "residual_zero": residual_zero,
        "local_residual_zero": local_residual_zero,
        "remote_ci": remote_ci,
        "human_review": human_review,
        "context_receipt": context_receipt,
        "external_public_residue": "approval_gated",
        "next_required_human_decision": (
            "target PR human review"
            if target_review_required
            else "publication approval only if public release is requested"
        ),
        "later_publication_gate": "publication approval only if public release is requested",
        "context_to_preserve": [
            "fde_workflow.yaml is the machine-readable closed-loop SSOT",
            "dependency-registry.md points to external measurement, smoke, runtime guarantee, and PDCA authorities",
            "local gate success is not publication or merge approval",
            "post-push residual zero requires a clean worktree and synchronized upstream",
        ],
        "resume_checks": [
            "git status --short --branch",
            "python3 -m pytest -q",
            "python3 scripts/mvp_gate_check.py",
            "python3 scripts/fde_operational_closeout.py --json --require-delivery-ready --require-remote-ci",
        ],
        "workflow_execution_receipt": execution_receipt,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--skip-pytest", action="store_true")
    parser.add_argument("--target-receipt", type=Path)
    parser.add_argument("--target-manifest", type=Path)
    parser.add_argument("--target-repo", type=Path)
    parser.add_argument(
        "--require-delivery-ready",
        action="store_true",
        help="Fail unless the worktree is clean and HEAD is synchronized with its upstream.",
    )
    parser.add_argument(
        "--require-remote-ci",
        action="store_true",
        help="Fail unless GitHub Actions Public Ready succeeded for the current HEAD.",
    )
    parser.add_argument(
        "--write-context-receipt",
        action="store_true",
        help="Persist the JSON receipt under ignored .fde-runtime/ for chat resume.",
    )
    parser.add_argument(
        "--record-human-review",
        metavar="REVIEWER",
        help="Record approval for the currently staged tree and exit.",
    )
    args = parser.parse_args()
    if args.record_human_review:
        try:
            path = _record_human_review(args.record_human_review)
        except RuntimeError as exc:
            print(f"HUMAN REVIEW RECEIPT ERROR: {exc}")
            return 1
        print(f"HUMAN REVIEW RECEIPT RECORDED: {path.relative_to(ROOT).as_posix()}")
        return 0
    result = evaluate(
        run_pytest=not args.skip_pytest,
        require_delivery_ready=args.require_delivery_ready,
        require_remote_ci=args.require_remote_ci,
        target_receipt=args.target_receipt,
        target_manifest=args.target_manifest,
        target_repo=args.target_repo,
    )
    if args.write_context_receipt:
        try:
            _write_context_receipt(result)
        except (OSError, RuntimeError, json.JSONDecodeError) as exc:
            result["errors"].append(f"context receipt persistence failed: {exc}")
            result["overall"] = "error"
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"FDE OPERATIONAL CLOSEOUT {result['overall'].upper()}")
        print(f"implementation_residue: {result['implementation_residue']}")
        print(f"operation_residue: {result['operation_residue']}")
        print(f"delivery_residue: {result['delivery_residue']}")
        print(f"residual_zero: {str(result['residual_zero']).lower()}")
        print(f"external_public_residue: {result['external_public_residue']}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
