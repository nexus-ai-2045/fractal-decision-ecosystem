#!/usr/bin/env python3
"""FDE closed-loop workflow manifest を strict / read-only で検証する。"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "fde_workflow.yaml"

REQUIRED_STATES = (
    "intake",
    "goal_and_boundary",
    "capability_inventory",
    "scope",
    "roadmap",
    "orchestrate",
    "preflight",
    "implement",
    "verify",
    "operational_guarantee",
    "review_packet",
    "feedback",
    "system_update",
    "closeout",
    "external_approval_required",
)
CLOSED_LOOP_SEQUENCE = (
    "goal_and_boundary",
    "capability_inventory",
    "roadmap",
    "preflight",
    "implement",
    "verify",
    "operational_guarantee",
    "feedback",
    "system_update",
)
CAPABILITY_INVENTORY_ORDER = (
    "official_capability",
    "oss_prior_art",
    "local_ssot",
    "existing_wrapper_or_library",
    "gap_only_to_implement",
)
VERIFICATION_LAYERS = ("lint", "unit", "integration", "smoke", "e2e", "regression")
SYSTEM_UPDATE_TARGETS = ("route", "skill", "gate", "test", "ssot", "roadmap")
LEARNING_ADOPTION_REQUIREMENTS = ("evidence", "rollback_path", "adoption_gate")
FEEDBACK_CONTRACT = (
    "failure_kind",
    "evidence",
    "system_update_target",
    "regression_test",
    "promotion_decision",
    "rollback_path",
)
CLOSED_LOOP_TRANSITIONS = tuple(
    f"{source}->{target}"
    for source, target in zip(
        CLOSED_LOOP_SEQUENCE,
        (*CLOSED_LOOP_SEQUENCE[1:], "goal_and_boundary"),
    )
)
STATE_EVIDENCE_CONTRACT = (
    "goal_and_boundary=goal+boundary",
    "capability_inventory=inventory+gap_only_to_implement",
    "roadmap=owner+done_when",
    "preflight=environment+authority+stopline",
    "implement=diff",
    "verify=test_evidence",
    "operational_guarantee=receipt+residue",
    "feedback=failure_kind+postmortem_action",
    "system_update=updated_artifact+regression_test+rollback_path",
)
STATE_GATE_BINDINGS = (
    "orchestrate=orchestration_gate_check",
    "preflight=pre_publication_gate_check+fde_architecture_drift_check",
    "verify=compileall+git_diff_check+pytest+pre_publication_gate_check+visual_html_smoke+public_ready_check",
    "operational_guarantee=fde_operational_closeout+remote_ci+human_review_receipt",
    "system_update=fde_workflow_check+fde_architecture_drift_check+regression_test",
    "external_approval_required=human_review_packet_check",
)
BLOCKED_TRANSITIONS = (
    "public_release",
    "repository_visibility_change",
    "external_send",
    "patent_filing",
    "credential_change",
    "auth_settings_change",
    "destructive_operation",
)
REQUIRED_LOCAL_GATES = (
    "target_workflow_runner",
    "public_ready_check",
    "pre_publication_gate_check",
    "roadmap_gate_check",
    "orchestration_gate_check",
    "residual_zero_goal_check",
    "no_transport_contact_check",
    "verify_residual_zero_contract",
    "visual_html_smoke",
    "public_kernel_diff_manifest",
    "human_review_packet_check",
    "pytest",
)
TARGET_WORKFLOW_RUNNER = {
    "manifest_schema": "fde.target_workflow.v1",
    "stop_at": "review_packet",
    "receipt": "metadata_only",
    "external_actions_performed": False,
}

SCALAR_KEYS = {
    "schema_version",
    "control_plane",
    "workflow_profile",
    "external_actions_performed",
    "external_action_scope",
    "external_authority_policy",
    "learning_return_to",
}
LIST_CONTRACTS = {
    "states": REQUIRED_STATES,
    "closed_loop_sequence": CLOSED_LOOP_SEQUENCE,
    "capability_inventory_order": CAPABILITY_INVENTORY_ORDER,
    "verification_layers": VERIFICATION_LAYERS,
    "system_update_targets": SYSTEM_UPDATE_TARGETS,
    "learning_adoption_requires": LEARNING_ADOPTION_REQUIREMENTS,
    "feedback_contract": FEEDBACK_CONTRACT,
    "closed_loop_transitions": CLOSED_LOOP_TRANSITIONS,
    "state_evidence_contract": STATE_EVIDENCE_CONTRACT,
    "state_gate_bindings": STATE_GATE_BINDINGS,
    "blocked_transitions": BLOCKED_TRANSITIONS,
    "required_local_gates": REQUIRED_LOCAL_GATES,
}
MAPPING_CONTRACTS = {"target_workflow_runner": TARGET_WORKFLOW_RUNNER}
ALLOWED_KEYS = SCALAR_KEYS | set(LIST_CONTRACTS) | set(MAPPING_CONTRACTS)
TOP_LEVEL = re.compile(r"^([a-z][a-z0-9_]*):(?: (.*))?$")
LIST_ITEM = re.compile(r"^  - ([^\s].*)$")
MAPPING_ITEM = re.compile(r"^  ([a-z][a-z0-9_]*): ([^\s].*)$")


def _parse_manifest(text: str) -> tuple[dict[str, object], list[str]]:
    """Parse the intentionally small YAML subset and reject ambiguity fail-closed."""
    data: dict[str, object] = {}
    errors: list[str] = []
    active_list: str | None = None
    active_mapping: str | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line:
            continue
        if "\t" in line or "#" in line:
            errors.append(f"line {line_number}: comments and tabs are not allowed")
            continue

        top_match = TOP_LEVEL.fullmatch(line)
        if top_match:
            key, raw_value = top_match.groups()
            active_list = None
            active_mapping = None
            if key not in ALLOWED_KEYS:
                errors.append(f"line {line_number}: unknown key: {key}")
                continue
            if key in data:
                errors.append(f"line {line_number}: duplicate key: {key}")
                continue
            if raw_value is None:
                if key in LIST_CONTRACTS:
                    data[key] = []
                    active_list = key
                elif key in MAPPING_CONTRACTS:
                    data[key] = {}
                    active_mapping = key
                else:
                    errors.append(f"line {line_number}: scalar key requires a value: {key}")
                    continue
            else:
                if key not in SCALAR_KEYS:
                    errors.append(f"line {line_number}: list key cannot have a scalar value: {key}")
                    continue
                if raw_value == "true":
                    data[key] = True
                elif raw_value == "false":
                    data[key] = False
                else:
                    data[key] = raw_value
            continue

        mapping_match = MAPPING_ITEM.fullmatch(line)
        if mapping_match and active_mapping:
            key, raw_value = mapping_match.groups()
            target = data[active_mapping]
            assert isinstance(target, dict)
            expected_keys = MAPPING_CONTRACTS[active_mapping]
            if key not in expected_keys:
                errors.append(
                    f"line {line_number}: unknown mapping key in {active_mapping}: {key}"
                )
            elif key in target:
                errors.append(
                    f"line {line_number}: duplicate mapping key in {active_mapping}: {key}"
                )
            elif raw_value == "true":
                target[key] = True
            elif raw_value == "false":
                target[key] = False
            else:
                target[key] = raw_value
            continue

        item_match = LIST_ITEM.fullmatch(line)
        if item_match and active_list:
            item = item_match.group(1)
            target = data[active_list]
            assert isinstance(target, list)
            if item in target:
                errors.append(f"line {line_number}: duplicate list item in {active_list}: {item}")
            else:
                target.append(item)
            continue

        errors.append(f"line {line_number}: invalid manifest syntax")

    for key in ALLOWED_KEYS - data.keys():
        errors.append(f"missing required key: {key}")
    return data, errors


def evaluate(workflow: Path = WORKFLOW) -> dict[str, object]:
    if not workflow.exists():
        data: dict[str, object] = {}
        errors = ["fde_workflow.yaml is missing"]
    else:
        data, errors = _parse_manifest(workflow.read_text(encoding="utf-8"))

    scalar_contracts = {
        "schema_version": "fde.workflow.v2",
        "control_plane": "FDE",
        "workflow_profile": "repository_closeout",
        "external_actions_performed": False,
        "external_action_scope": "this_check_invocation_only",
        "external_authority_policy": "optional_workspace_enrichment",
        "learning_return_to": "goal_and_boundary",
    }
    for key, expected in scalar_contracts.items():
        if key in data and data[key] != expected:
            errors.append(f"invalid {key}: expected {expected!r}, got {data[key]!r}")

    for key, expected in LIST_CONTRACTS.items():
        if key in data and data[key] != list(expected):
            errors.append(f"{key} is missing, contains unknown values, or is out of order")

    for key, expected in MAPPING_CONTRACTS.items():
        if key in data and data[key] != expected:
            errors.append(f"{key} is missing, contains unknown values, or has invalid values")

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": data.get("external_actions_performed"),
        "external_action_scope": data.get("external_action_scope"),
        "errors": errors,
        "workflow": {
            "control_plane": data.get("control_plane"),
            "workflow_profile": data.get("workflow_profile"),
            "external_authority_policy": data.get("external_authority_policy"),
            "states": data.get("states", []),
            "closed_loop_sequence": data.get("closed_loop_sequence", []),
            "capability_inventory_order": data.get("capability_inventory_order", []),
            "verification_layers": data.get("verification_layers", []),
            "system_update_targets": data.get("system_update_targets", []),
            "feedback_contract": data.get("feedback_contract", []),
            "closed_loop_transitions": data.get("closed_loop_transitions", []),
            "state_evidence_contract": data.get("state_evidence_contract", []),
            "state_gate_bindings": data.get("state_gate_bindings", []),
            "learning_return_to": data.get("learning_return_to"),
            "target_workflow_runner": data.get("target_workflow_runner", {}),
        },
    }


def main() -> int:
    result = evaluate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
