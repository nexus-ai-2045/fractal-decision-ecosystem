#!/usr/bin/env python3
"""本文を含まないFDE activity evidence packetをread-onlyで検証する。"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "fde_activity_evidence.v1.schema.json"
MAX_ACTIVITY_EVIDENCE_BYTES = 128 * 1024
PERSONAL_PATH_PATTERN = re.compile(
    r"(?:[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+|\\\\[^\\/]+[\\/]users[\\/][A-Za-z0-9._-]+|/(?:Users|home)/[A-Za-z0-9._-]+|/root(?:[\\/]|$))",
    re.IGNORECASE,
)
SECRET_LIKE_PATTERN = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"sk-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{20,}|"
    r"(?i:Bearer)\s+[A-Za-z0-9\-._~+/]{20,}={0,2}|"
    r"xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16}|"
    r"npm_[A-Za-z0-9]{20,}|"
    r"-----BEGIN (?:OPENSSH |RSA |EC |ENCRYPTED |DSA )?PRIVATE KEY-----|"
    r"-----BEGIN PGP PRIVATE KEY BLOCK-----)"
)
RFC3339_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:[Zz]|[+-][0-9]{2}:[0-9]{2})$"
)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def _reject_non_finite(value: str) -> None:
    raise ValueError("non_finite_json_number")


def _iter_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _iter_strings(key)
            yield from _iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)


def _contains_unpaired_surrogate(value: Any) -> bool:
    return any(
        0xD800 <= ord(character) <= 0xDFFF
        for text in _iter_strings(value)
        for character in text
    )


def load_activity_evidence(path: Path) -> dict[str, Any]:
    with path.open("rb") as stream:
        raw = stream.read(MAX_ACTIVITY_EVIDENCE_BYTES + 1)
    if len(raw) > MAX_ACTIVITY_EVIDENCE_BYTES:
        raise ValueError("input_too_large")
    value = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_non_finite,
    )
    if not isinstance(value, dict):
        raise ValueError("activity evidence must be a JSON object")
    return value


def validate_activity_evidence(packet: dict[str, Any]) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: invalid {error.validator}"
        for error in sorted(
            validator.iter_errors(packet), key=lambda item: list(item.absolute_path)
        )
    ]
    try:
        serialized = json.dumps(packet, ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError):
        errors.append("<root>: invalid JSON value")
        return errors
    strings = list(_iter_strings(packet))
    if any(PERSONAL_PATH_PATTERN.search(value) for value in strings):
        errors.append("<root>: personal path is not allowed")
    if SECRET_LIKE_PATTERN.search(serialized):
        errors.append("<root>: secret-like content is not allowed")
    if _contains_unpaired_surrogate(packet):
        errors.append("<root>: invalid Unicode surrogate")
    occurred_at = packet.get("occurred_at")
    if isinstance(occurred_at, str):
        try:
            if not RFC3339_PATTERN.fullmatch(occurred_at):
                raise ValueError
            normalized = occurred_at.replace("t", "T")
            if normalized.endswith(("Z", "z")):
                normalized = normalized[:-1] + "+00:00"
            timestamp = datetime.fromisoformat(normalized)
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValueError
        except ValueError:
            errors.append("occurred_at: RFC 3339 date-time with timezone is required")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result: dict[str, Any] = {
        "overall": "error",
        "schema": None,
        "event_id": None,
        "external_actions_performed": False,
        "errors": [],
    }
    try:
        packet = load_activity_evidence(args.input)
        result["schema"] = packet.get("schema")
        result["event_id"] = packet.get("event_id")
        result["errors"] = validate_activity_evidence(packet)
        result["overall"] = "contract_valid" if not result["errors"] else "blocked"
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc) in {
            "duplicate_json_key",
            "non_finite_json_number",
            "input_too_large",
        }:
            code = str(exc)
        elif isinstance(exc, json.JSONDecodeError):
            code = "invalid_json"
        elif isinstance(exc, UnicodeError):
            code = "invalid_utf8"
        else:
            code = "input_unreadable"
        result["errors"] = [code]
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(result["overall"])
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["overall"] == "contract_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
