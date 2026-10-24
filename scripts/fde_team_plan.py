#!/usr/bin/env python3
"""Validate FDE team_plan / no_team_reason packets (ADR-0004)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "fde_team_plan.v1.schema.json"
MAX_BYTES = 64 * 1024

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
    r"npm_[A-Za-z0-9]{20,}"
    r")"
)

# Delegates must not own these responsibilities (ADR-0004).
FORBIDDEN_DELEGATE_RETURNS = frozenset(
    {
        "final_decision",
        "publication_approval",
        "credential",
        "auth",
        "settings",
        "destructive",
        "merge",
        "push",
        "external_send",
    }
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


def validate_team_plan(packet: dict[str, Any]) -> list[str]:
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

    if packet.get("kind") == "team_plan":
        for index, item in enumerate(packet.get("delegate_plan") or []):
            if not isinstance(item, dict):
                continue
            returns = item.get("returns") or []
            for value in returns:
                if value in FORBIDDEN_DELEGATE_RETURNS:
                    errors.append(
                        f"delegate_plan/{index}/returns: forbidden responsibility {value}"
                    )
        owner = packet.get("stopline_owner")
        if owner not in {"main_runtime", "human"}:
            errors.append("stopline_owner: must remain main_runtime or human")
    return errors


def evaluate_team_plan(packet: dict[str, Any]) -> dict[str, Any]:
    errors = validate_team_plan(packet)
    kind = packet.get("kind") if not errors else None
    return {
        "overall": "ok" if not errors else "error",
        "schema_version": packet.get("schema_version") if not errors else None,
        "kind": kind,
        "gate": "ok" if not errors else "blocked",
        "external_actions_performed": False,
        "final_decision_retained_by_main": True,
        "errors": errors,
    }


def sample_team_plan() -> dict[str, Any]:
    return {
        "schema_version": "fde.team_plan.v1",
        "kind": "team_plan",
        "task": "nontrivial multi-surface verification",
        "roles": ["main_runtime", "reviewer", "implementer"],
        "delegate_plan": [
            {
                "role": "reviewer",
                "returns": ["evidence", "blocker", "review_packet"],
            },
            {
                "role": "implementer",
                "returns": ["diff", "smoke", "blocker"],
            },
        ],
        "return_contract": "typed receipts only; no raw chat absorption",
        "adoption_gate": "main_runtime adopts after human review when required",
        "stopline_owner": "main_runtime",
    }


def sample_no_team_reason() -> dict[str, Any]:
    return {
        "schema_version": "fde.team_plan.v1",
        "kind": "no_team_reason",
        "task": "fix typo in docs only",
        "reason_code": "tiny_task",
        "reason": "single-file docs typo with no branching surfaces",
        "stopline_owner": "main_runtime",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        size = args.input.stat().st_size
        if size > MAX_BYTES:
            raise ValueError(f"team plan exceeds {MAX_BYTES} bytes")
        packet = json.loads(
            args.input.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
        if not isinstance(packet, dict):
            raise ValueError("team plan must be a JSON object")
        result = evaluate_team_plan(packet)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        result = {
            "overall": "error",
            "schema_version": None,
            "kind": None,
            "gate": "blocked",
            "external_actions_performed": False,
            "final_decision_retained_by_main": True,
            "errors": [f"{type(error).__name__}: invalid team plan input"],
        }
    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(f"FDE TEAM PLAN {result['overall'].upper()}")
        print(f"kind: {result.get('kind')}")
        print(f"gate: {result.get('gate')}")
        print(
            f"external_actions_performed: {str(result['external_actions_performed']).lower()}"
        )
        for error in result.get("errors", []):
            print(f"- {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
