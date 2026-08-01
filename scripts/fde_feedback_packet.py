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
PERSONAL_PATH_PATTERN = re.compile(
    r"(?:[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+|\\\\[^\\/]+[\\/]users[\\/][A-Za-z0-9._-]+|/(?:Users|home)/[A-Za-z0-9._-]+|/root(?:[\\/]|$))",
    re.IGNORECASE,
)
SECRET_LIKE_PATTERN = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{20,}|(?i:Bearer)\s+[A-Za-z0-9._-]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16}|npm_[A-Za-z0-9]{20,}|-----BEGIN (?:OPENSSH |RSA |EC |ENCRYPTED |DSA |PGP )?PRIVATE KEY-----)"
)
RFC3339_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:[Zz]|[+-][0-9]{2}:[0-9]{2})$"
)


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
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
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
    }
    print(
        json.dumps(result, ensure_ascii=True, indent=2)
        if args.json
        else ("PASS" if not errors else "\n".join(errors))
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
