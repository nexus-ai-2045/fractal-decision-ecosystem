#!/usr/bin/env python3
"""Validate FDE AI contact packets without approving transport implementation."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "fde_contact_packet.v1.schema.json"
MAX_CONTACT_PACKET_BYTES = 64 * 1024

PERSONAL_PATH_PATTERN = re.compile(
    r"(?:[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+|\\\\[^\\/]+[\\/]users[\\/][A-Za-z0-9._-]+|/(?:Users|home)/[A-Za-z0-9._-]+|/root(?:[\\/]|$))",
    re.IGNORECASE,
)
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

# Fields named by ai-contact-safety-contract.md as block triggers when unset.
BLOCK_IF_MISSING = (
    ("packet_id", ("packet_id",)),
    ("verification_method", ("identity", "verification_method")),
    ("consent_scope", ("consent", "consent_scope")),
    ("ttl", ("data_boundary", "ttl")),
    ("checksum", ("data_boundary", "checksum")),
    ("human_approved_at", ("data_boundary", "human_approved_at")),
    ("replay_protection", ("safety", "replay_protection")),
    ("transport_adapter_status", ("safety", "transport_adapter_status")),
)


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


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


def _get_path(packet: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = packet
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _valid_rfc3339(value: str) -> bool:
    if not RFC3339_PATTERN.fullmatch(value):
        return False
    try:
        normalized = value.replace("t", "T")
        if normalized.endswith(("Z", "z")):
            normalized = normalized[:-1] + "+00:00"
        timestamp = datetime.fromisoformat(normalized)
        return timestamp.tzinfo is not None and timestamp.utcoffset() is not None
    except ValueError:
        return False


def validate_contact_packet(packet: dict[str, Any]) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: invalid {error.validator}"
        for error in sorted(
            validator.iter_errors(packet), key=lambda item: list(item.absolute_path)
        )
    ]
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
    for field_path in (
        ("consent", "expiry"),
        ("data_boundary", "human_approved_at"),
    ):
        value = _get_path(packet, field_path)
        if isinstance(value, str) and not _valid_rfc3339(value):
            errors.append(f"{'/'.join(field_path)}: invalid date-time")
    safety = packet.get("safety")
    if isinstance(safety, dict) and safety.get("transport_adapter_status") not in (
        None,
        "unapproved",
    ):
        errors.append(
            "safety/transport_adapter_status: only unapproved is allowed in FDE package"
        )
    closure = packet.get("closure")
    if isinstance(closure, dict) and closure.get("next_contact_allowed") is True:
        errors.append(
            "closure/next_contact_allowed: true is not allowed while transport is unapproved"
        )
    return errors


def evaluate_contact_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Return schema + gate result. Never performs contact or transport."""
    validation_errors = validate_contact_packet(packet)
    blocked_reasons: list[str] = []
    for label, path in BLOCK_IF_MISSING:
        value = _get_path(packet, path)
        if value is None or (isinstance(value, str) and WHITESPACE_ONLY_PATTERN.fullmatch(value)):
            blocked_reasons.append(f"missing:{label}")
    transport = _get_path(packet, ("safety", "transport_adapter_status"))
    if transport != "unapproved":
        blocked_reasons.append("transport_adapter_not_unapproved")
    if validation_errors:
        blocked_reasons.append("schema_invalid")
    # Complete, transport-unapproved packets may be review-ready, but contact stays blocked.
    gate = "blocked"
    if not validation_errors and not any(
        reason.startswith("missing:") or reason == "transport_adapter_not_unapproved"
        for reason in blocked_reasons
    ):
        gate = "review_ready"
        # Contact action remains blocked by transport policy.
        blocked_reasons.append("transport_unapproved_contact_blocked")
        gate_contact = "blocked"
    else:
        gate_contact = "blocked"
    return {
        "overall": "ok" if not validation_errors else "error",
        "schema_version": packet.get("schema_version")
        if not validation_errors
        else None,
        "packet_id": packet.get("packet_id") if not validation_errors else None,
        "gate": gate,
        "contact_action": gate_contact,
        "transport_adapter_approved": False,
        "external_actions_performed": False,
        "blocked_reasons": blocked_reasons,
        "errors": validation_errors,
    }


def sample_complete_packet() -> dict[str, Any]:
    """Fixture helper for tests — not a transport approval."""
    return {
        "schema_version": "fde.contact_packet.v1",
        "packet_id": "contact-review-001",
        "actor": "local-agent",
        "peer": "peer-agent",
        "purpose": "exchange minimized reviewable summary",
        "identity": {
            "verification_method": "shared-registry-pin",
            "verification_evidence": "registry:peer-agent:v1",
        },
        "consent": {
            "consent_scope": "summary-only no-secret",
            "expiry": "2026-12-31T00:00:00+00:00",
            "revocation": "user-settings-revoke-contact",
        },
        "data_boundary": {
            "sensitivity": "internal",
            "recipient_class": "trusted_peer",
            "allowed_fields": ["summary", "status"],
            "redaction_required": True,
            "ttl": "24h",
            "checksum": "sha256:0123456789abcdef0123456789abcdef",
            "human_approved_at": "2026-08-07T12:00:00+00:00",
            "no_raw_source_pointer": True,
        },
        "safety": {
            "blocklist": [],
            "replay_protection": "nonce-and-expiry",
            "transport_adapter_status": "unapproved",
        },
        "closure": {
            "decision": "review_ready",
            "next_contact_allowed": False,
            "evidence_pointer": "receipt:contact-review-001",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        size = args.input.stat().st_size
        if size > MAX_CONTACT_PACKET_BYTES:
            raise ValueError(
                f"contact packet exceeds {MAX_CONTACT_PACKET_BYTES} bytes"
            )
        packet = json.loads(
            args.input.read_text(encoding="utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"invalid JSON constant: {value}")
            ),
            object_pairs_hook=reject_duplicate_keys,
        )
        if not isinstance(packet, dict):
            raise ValueError("contact packet must be a JSON object")
        result = evaluate_contact_packet(packet)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as error:
        result = {
            "overall": "error",
            "schema_version": None,
            "packet_id": None,
            "gate": "blocked",
            "contact_action": "blocked",
            "transport_adapter_approved": False,
            "external_actions_performed": False,
            "blocked_reasons": ["invalid_input"],
            "errors": [f"{type(error).__name__}: invalid contact input"],
        }
    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(f"FDE CONTACT PACKET {result['overall'].upper()}")
        print(f"gate: {result['gate']}")
        print(f"contact_action: {result['contact_action']}")
        print(
            f"transport_adapter_approved: {str(result['transport_adapter_approved']).lower()}"
        )
        print(
            f"external_actions_performed: {str(result['external_actions_performed']).lower()}"
        )
        for reason in result.get("blocked_reasons", []):
            print(f"- blocked: {reason}")
        for error in result.get("errors", []):
            print(f"- error: {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
