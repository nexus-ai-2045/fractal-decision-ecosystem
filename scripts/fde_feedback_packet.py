#!/usr/bin/env python3
"""FDE cross-runtime feedback packetをread-onlyで検証する。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "fde_feedback_packet.v1.schema.json"
# Valid packets are small; reject oversized producer input before loading.
MAX_FEEDBACK_PACKET_BYTES = 128 * 1024
CANONICAL_UPDATE_TARGETS = frozenset(
    {"route", "skill", "gate", "test", "ssot", "roadmap"}
)
PERSONAL_PATH_PATTERN = re.compile(
    r"(?:[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+|\\\\[^\\/]+[\\/]users[\\/][A-Za-z0-9._-]+|/(?:Users|home)/[A-Za-z0-9._-]+|/root(?:[\\/]|$))",
    re.IGNORECASE,
)
# Bearer token alphabet follows RFC 6750 (unreserved / sub-delims / + / / / =).
SECRET_LIKE_PATTERN = re.compile(
    r"(?:"
    r"gh[pousr]_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|"
    r"sk-[A-Za-z0-9_-]{20,}|"
    r"AIza[A-Za-z0-9_-]{20,}|"
    r"(?i:Bearer)\s+[A-Za-z0-9\-._~+/]{20,}={0,2}|"
    r"xox[baprs]-[A-Za-z0-9-]{20,}|"
    r"AKIA[0-9A-Z]{16}|"
    r"npm_[A-Za-z0-9]{20,}|"
    r"-----BEGIN (?:OPENSSH |RSA |EC |ENCRYPTED |DSA )?PRIVATE KEY-----|"
    r"-----BEGIN PGP PRIVATE KEY BLOCK-----"
    r")"
)
RFC3339_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:[Zz]|[+-][0-9]{2}:[0-9]{2})$"
)
WHITESPACE_ONLY_PATTERN = re.compile(r"^\s*$")


def contains_unpaired_surrogate(value: Any) -> bool:
    if isinstance(value, str):
        return any(0xD800 <= ord(character) <= 0xDFFF for character in value)
    if isinstance(value, dict):
        return any(
            contains_unpaired_surrogate(key) or contains_unpaired_surrogate(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(contains_unpaired_surrogate(item) for item in value)
    return False


def iter_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(key)
            yield from iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)


def feedback_packet_sha256(packet: dict[str, Any]) -> str:
    canonical = json.dumps(
        packet,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
SAFE_REF_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#-]*$")


def _safe_token(value: str, *, fallback: str, max_len: int = 128) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._:-]+", "-", value.strip())
    cleaned = cleaned.strip("-._:")
    if not cleaned or not SAFE_ID_PATTERN.fullmatch(cleaned[:max_len]):
        return fallback[:max_len]
    return cleaned[:max_len]


def _safe_ref(value: str, *, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._:/#-]+", "-", value.strip())
    cleaned = cleaned.strip("-._:/#")
    if not cleaned or not SAFE_REF_PATTERN.fullmatch(cleaned[:256]):
        return fallback[:256]
    return cleaned[:256]


def draft_feedback_from_target_receipt(
    receipt: dict[str, Any],
    *,
    intake: dict[str, Any] | None = None,
    producer: str = "fde-target-workflow",
    observed_at: str | None = None,
) -> dict[str, Any]:
    """Build a hold/revise draft from a target-workflow receipt.

    Reuses fde.feedback.v1 only. Never emits act.decision=adopt.
    Metadata digests/refs only — no absolute paths or raw tool output.
    """
    if not isinstance(receipt, dict):
        raise ValueError("receipt must be a JSON object")
    intake = intake or {}
    return_path = intake.get("return_path") if isinstance(intake, dict) else None
    if isinstance(return_path, dict):
        if return_path.get("kind") != "feedback_packet":
            raise ValueError("intake.return_path.kind must be feedback_packet")
        if return_path.get("schema") != "fde.feedback.v1":
            raise ValueError("intake.return_path.schema must be fde.feedback.v1")

    workflow_id = _safe_token(
        str(receipt.get("workflow_id") or "workflow"),
        fallback="workflow-unknown",
    )
    manifest_digest = str(receipt.get("manifest_digest") or "")
    state = str(receipt.get("state") or "blocked")
    checks = receipt.get("checks") if isinstance(receipt.get("checks"), list) else []
    ok = (
        state == "human_review_required"
        and bool(checks)
        and all(
            isinstance(item, dict) and item.get("status") == "passed" for item in checks
        )
    )
    failed_names = [
        str(item.get("name") or "check")
        for item in checks
        if isinstance(item, dict) and item.get("status") != "passed"
    ]
    goal = str(intake.get("goal") or "complete local checks and stop at review packet")
    owner = str(intake.get("owner") or "unspecified")
    scope = str(intake.get("scope") or "target-workflow")
    # Keep free text free of path/secret-like patterns by constraining to short prose.
    goal_text = re.sub(r"\s+", " ", goal).strip()[:900] or "local verification"
    owner_text = re.sub(r"\s+", " ", owner).strip()[:120] or "unspecified"
    scope_text = re.sub(r"\s+", " ", scope).strip()[:200] or "target-workflow"

    evidence: list[dict[str, str]] = [
        {
            "kind": "receipt",
            "ref": _safe_ref(
                f"receipt:workflow:{workflow_id}",
                fallback="receipt:workflow:unknown",
            ),
        }
    ]
    if manifest_digest and re.fullmatch(r"[0-9a-fA-F]{16,128}", manifest_digest):
        evidence.append(
            {
                "kind": "receipt",
                "ref": _safe_ref(
                    f"receipt:manifest:{manifest_digest[:64]}",
                    fallback="receipt:manifest:unknown",
                ),
            }
        )
    for item in checks[:16]:
        if not isinstance(item, dict):
            continue
        name = _safe_token(str(item.get("name") or "check"), fallback="check")
        status = _safe_token(str(item.get("status") or "unknown"), fallback="unknown")
        digest = str(item.get("check_digest") or item.get("output_digest") or "")
        if digest and re.fullmatch(r"[0-9a-fA-F]{16,128}", digest):
            ref = f"receipt:check:{name}:{status}:{digest[:32]}"
        else:
            ref = f"receipt:check:{name}:{status}"
        evidence.append(
            {
                "kind": "receipt",
                "ref": _safe_ref(ref, fallback=f"receipt:check:{name}:{status}"),
            }
        )

    if ok:
        decision = "hold"
        outcome = "met"
        failure_kind = "none"
        update_targets = ["none"]
        next_plan = (
            "human review of review_packet receipt; do not auto-apply learning"
        )
        actions = [
            "run registered local checks",
            "stop at review_packet",
            "draft fde.feedback.v1 for human review",
        ]
    elif state in {"trust_review_required", "locked"}:
        decision = "revise"
        outcome = "not_met"
        failure_kind = "trust_or_lock"
        update_targets = ["gate", "test"]
        next_plan = "resolve trust registry or lock then rerun target workflow"
        actions = ["attempt trusted local workflow", f"stop at {state}"]
    else:
        decision = "revise"
        outcome = "not_met"
        failure_kind = "check_failed"
        update_targets = ["test", "gate"]
        failed = ",".join(
            _safe_token(name, fallback="check") for name in failed_names[:8]
        ) or "unknown"
        next_plan = f"repair failed checks ({failed}) then rerun target workflow"
        actions = ["run registered local checks", "stop on first failure"]

    timestamp = observed_at or datetime.now().astimezone().isoformat(timespec="seconds")
    packet: dict[str, Any] = {
        "schema_version": "fde.feedback.v1",
        "feedback_id": _safe_token(
            f"feedback-draft-{workflow_id}",
            fallback="feedback-draft-unknown",
        ),
        "source_run_id": _safe_token(
            f"run-{workflow_id}",
            fallback="run-unknown",
        ),
        "producer": _safe_token(producer, fallback="fde-target-workflow"),
        "consumer": "fde",
        "observed_at": timestamp,
        "plan": {
            "hypothesis": f"local checks for {scope_text} under owner {owner_text}",
            "expected_effect": goal_text,
            "verification_plan": [
                "execute trusted target workflow checks",
                "validate draft with fde_feedback_packet",
            ],
        },
        "do": {
            "actions": actions,
            "changed_artifacts": [],
        },
        "check": {
            "outcome": outcome,
            "evidence": evidence[:32],
            "human_review": "pending",
        },
        "act": {
            "decision": decision,
            "failure_kind": failure_kind,
            "update_targets": update_targets,
            "regression_test": "tests/test_feedback_packet.py",
            "rollback_path": "discard draft packet; keep review_packet stop",
            "next_plan_input": next_plan,
        },
        "boundaries": {
            # Draft generation itself never performs external actions.
            # Receipt claims of external work stay outside this packet.
            "external_actions_performed": False,
            "human_gate_required": True,
        },
        "provenance": {
            "source_refs": [
                {
                    "kind": "receipt",
                    "ref": _safe_ref(
                        f"receipt:workflow:{workflow_id}",
                        fallback="receipt:workflow:unknown",
                    ),
                },
                {
                    "kind": "source",
                    "ref": "docs/feedback-loop-packet.md",
                },
            ]
        },
    }
    if packet["act"]["decision"] == "adopt":
        raise ValueError("draft generator must not emit adopt")
    errors = validate_feedback_packet(packet)
    if errors:
        raise ValueError(f"draft failed validation: {errors[0]}")
    return packet


def validate_feedback_packet(
    packet: dict[str, Any],
    *,
    approved_packet_sha256: set[str] | None = None,
) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: invalid {error.validator}"
        for error in sorted(validator.iter_errors(packet), key=lambda item: list(item.absolute_path))
    ]
    act = packet.get("act")
    strings = list(iter_strings(packet))
    try:
        serialized = json.dumps(packet, ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError):
        errors.append("<root>: invalid JSON value")
        return errors
    if any(PERSONAL_PATH_PATTERN.search(value) for value in strings):
        errors.append("<root>: personal path is not allowed")
    if SECRET_LIKE_PATTERN.search(serialized):
        errors.append("<root>: secret-like content is not allowed")
    if contains_unpaired_surrogate(packet):
        errors.append("<root>: invalid Unicode surrogate")
    observed_at = packet.get("observed_at")
    if isinstance(observed_at, str):
        try:
            if not RFC3339_PATTERN.fullmatch(observed_at):
                raise ValueError("RFC 3339 date-time is required")
            normalized_timestamp = observed_at.replace("t", "T")
            if normalized_timestamp.endswith(("Z", "z")):
                normalized_timestamp = normalized_timestamp[:-1] + "+00:00"
            timestamp = datetime.fromisoformat(normalized_timestamp)
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValueError("timezone offset is required")
        except ValueError:
            errors.append("observed_at: invalid date-time")
    check = packet.get("check")
    boundaries = packet.get("boundaries")
    approved_packet_sha256 = approved_packet_sha256 or set()
    if (
        isinstance(act, dict)
        and act.get("decision") == "adopt"
        and feedback_packet_sha256(packet) not in approved_packet_sha256
    ):
        errors.append("act/decision: adopt requires FDE approval context")
    if (
        isinstance(act, dict)
        and act.get("decision") == "adopt"
        and isinstance(check, dict)
        and check.get("human_review") == "rejected"
    ):
        errors.append("act/decision: adopt conflicts with rejected human review")
    if (
        isinstance(act, dict)
        and act.get("decision") == "adopt"
        and isinstance(boundaries, dict)
        and boundaries.get("human_gate_required") is True
        and (
            not isinstance(check, dict)
            or check.get("human_review") != "approved"
        )
    ):
        errors.append("act/decision: adopt requires approved human review")
    if isinstance(act, dict):
        failure_kind = act.get("failure_kind")
        update_targets = act.get("update_targets")
        if isinstance(failure_kind, str) and WHITESPACE_ONLY_PATTERN.fullmatch(
            failure_kind
        ):
            errors.append("act/failure_kind: non-empty content is required")
        if isinstance(update_targets, list):
            if failure_kind == "none":
                if update_targets != ["none"]:
                    errors.append(
                        "act/update_targets: failure_kind none requires [\"none\"]"
                    )
            elif "none" in update_targets:
                errors.append(
                    "act/update_targets: none is only valid when failure_kind is none"
                )
            elif not any(
                target in CANONICAL_UPDATE_TARGETS for target in update_targets
            ):
                errors.append("act/update_targets: canonical target is required")
    for field_path, value in (
        ("feedback_id", packet.get("feedback_id")),
        ("source_run_id", packet.get("source_run_id")),
        ("producer", packet.get("producer")),
    ):
        if isinstance(value, str) and WHITESPACE_ONLY_PATTERN.fullmatch(value):
            errors.append(f"{field_path}: non-empty content is required")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        help="Existing fde.feedback.v1 packet to validate (read-only).",
    )
    parser.add_argument(
        "--from-receipt",
        type=Path,
        help="Target workflow receipt to draft a hold/revise feedback packet from.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Optional target workflow manifest for intake.goal/owner/return_path.",
    )
    parser.add_argument(
        "--write",
        type=Path,
        help="Optional path to write a drafted packet (metadata-only JSON).",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if bool(args.input) == bool(args.from_receipt):
        result = {
            "overall": "error",
            "schema_version": None,
            "feedback_id": None,
            "external_actions_performed": False,
            "errors": [
                "ValueError: exactly one of --input or --from-receipt is required"
            ],
        }
        print(
            json.dumps(result, ensure_ascii=True, indent=2)
            if args.json
            else "\n".join(result["errors"])
        )
        return 1

    try:
        if args.from_receipt is not None:
            receipt_size = args.from_receipt.stat().st_size
            if receipt_size > MAX_FEEDBACK_PACKET_BYTES:
                raise ValueError(
                    f"receipt exceeds {MAX_FEEDBACK_PACKET_BYTES} bytes"
                )
            receipt = json.loads(
                args.from_receipt.read_text(encoding="utf-8"),
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError(f"invalid JSON constant: {value}")
                ),
                object_pairs_hook=reject_duplicate_keys,
            )
            if not isinstance(receipt, dict):
                raise ValueError("receipt must be a JSON object")
            intake: dict[str, Any] | None = None
            if args.manifest is not None:
                manifest = json.loads(
                    args.manifest.read_text(encoding="utf-8"),
                    object_pairs_hook=reject_duplicate_keys,
                )
                if not isinstance(manifest, dict):
                    raise ValueError("manifest must be a JSON object")
                raw_intake = manifest.get("intake")
                if raw_intake is not None and not isinstance(raw_intake, dict):
                    raise ValueError("manifest.intake must be an object")
                intake = raw_intake if isinstance(raw_intake, dict) else None
            packet = draft_feedback_from_target_receipt(
                receipt,
                intake=intake,
            )
            if args.write is not None:
                write_path = args.write.resolve()
                write_path.parent.mkdir(parents=True, exist_ok=True)
                write_path.write_text(
                    json.dumps(packet, ensure_ascii=True, indent=2, sort_keys=True)
                    + "\n",
                    encoding="utf-8",
                )
        else:
            packet_size = args.input.stat().st_size
            if packet_size > MAX_FEEDBACK_PACKET_BYTES:
                raise ValueError(
                    f"feedback packet exceeds {MAX_FEEDBACK_PACKET_BYTES} bytes"
                )
            packet = json.loads(
                args.input.read_text(encoding="utf-8"),
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError(f"invalid JSON constant: {value}")
                ),
                object_pairs_hook=reject_duplicate_keys,
            )
            if not isinstance(packet, dict):
                raise ValueError("feedback packet must be a JSON object")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as error:
        result = {
            "overall": "error",
            "schema_version": None,
            "feedback_id": None,
            "external_actions_performed": False,
            "errors": [f"{type(error).__name__}: invalid feedback input"],
        }
        print(
            json.dumps(result, ensure_ascii=True, indent=2)
            if args.json
            else "\n".join(result["errors"])
        )
        return 1
    try:
        errors = validate_feedback_packet(
            packet,
            approved_packet_sha256=None,
        )
    except RecursionError as error:
        result = {
            "overall": "error",
            "schema_version": None,
            "feedback_id": None,
            "external_actions_performed": False,
            "errors": [f"{type(error).__name__}: invalid feedback input"],
        }
        print(
            json.dumps(result, ensure_ascii=True, indent=2)
            if args.json
            else "\n".join(result["errors"])
        )
        return 1
    identifiers_are_non_sensitive = not any(
        "secret-like content" in error
        or "personal path" in error
        or "Unicode surrogate" in error
        for error in errors
    )
    schema_version = packet.get("schema_version")
    feedback_id = packet.get("feedback_id")
    result = {
        "overall": "ok" if not errors else "error",
        "schema_version": (
            schema_version
            if identifiers_are_non_sensitive
            and schema_version == "fde.feedback.v1"
            else None
        ),
        "feedback_id": (
            feedback_id
            if identifiers_are_non_sensitive
            and isinstance(feedback_id, str)
            and 1 <= len(feedback_id) <= 128
            else None
        ),
        "external_actions_performed": False,
        "errors": errors,
        "mode": "draft" if args.from_receipt is not None else "validate",
        "act_decision": (
            packet.get("act", {}).get("decision")
            if isinstance(packet.get("act"), dict)
            and identifiers_are_non_sensitive
            else None
        ),
    }
    print(
        json.dumps(result, ensure_ascii=True, indent=2)
        if args.json
        else ("PASS" if not errors else "\n".join(errors))
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
