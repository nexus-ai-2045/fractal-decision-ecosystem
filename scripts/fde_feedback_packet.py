#!/usr/bin/env python3
"""FDE cross-runtime feedback packetをread-onlyで検証する。"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "fde_feedback_packet.v1.schema.json"
PERSONAL_PATH_PATTERN = re.compile(
    r"(?:[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+|/(?:Users|home)/[A-Za-z0-9._-]+)"
)
SECRET_LIKE_PATTERN = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{20,}|Bearer\s+[A-Za-z0-9._-]{20,})"
)
SURROGATE_ESCAPE_PATTERN = re.compile(r"\\u[dD][89aAbB][0-9a-fA-F]{2}")


def validate_feedback_packet(packet: dict[str, Any]) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: invalid {error.validator}"
        for error in sorted(validator.iter_errors(packet), key=lambda item: list(item.absolute_path))
    ]
    act = packet.get("act")
    serialized = json.dumps(packet, ensure_ascii=True)
    if PERSONAL_PATH_PATTERN.search(serialized):
        errors.append("<root>: personal path is not allowed")
    if SECRET_LIKE_PATTERN.search(serialized):
        errors.append("<root>: secret-like content is not allowed")
    if SURROGATE_ESCAPE_PATTERN.search(serialized):
        errors.append("<root>: invalid Unicode surrogate")
    observed_at = packet.get("observed_at")
    if isinstance(observed_at, str):
        try:
            datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        except ValueError:
            errors.append("observed_at: invalid date-time")
    check = packet.get("check")
    boundaries = packet.get("boundaries")
    if (
        isinstance(act, dict)
        and act.get("decision") == "adopt"
        and isinstance(check, dict)
        and check.get("human_review") == "rejected"
    ):
        errors.append("act/decision: adopt conflicts with rejected human review")
    elif (
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
        packet = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(packet, dict):
            raise ValueError("feedback packet must be a JSON object")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
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
    errors = validate_feedback_packet(packet)
    safe_identifiers = not any(
        "secret-like content" in error or "Unicode surrogate" in error
        for error in errors
    )
    result = {
        "overall": "ok" if not errors else "error",
        "schema_version": packet.get("schema_version"),
        "feedback_id": packet.get("feedback_id") if safe_identifiers else None,
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
