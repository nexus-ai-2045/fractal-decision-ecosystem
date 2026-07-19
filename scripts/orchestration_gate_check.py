#!/usr/bin/env python3
"""Orchestration / Spark routing gate for FDE docs and optional packets."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC_CONTRACTS: dict[str, tuple[str, ...]] = {
    "core.md": (
        "orchestration_required",
        "orchestration_reason",
        "delegate_plan",
        "codex_main_role",
        "return_to",
        "packet-invalid",
    ),
    "operating-card.md": (
        "orchestration_required",
        "GPT-5.3-Codex-Spark",
        "spark_candidate",
        "spark_delegate",
        "thin_source_route",
        "routing_decision",
    ),
    "search-orchestration.md": (
        "orchestration_required",
        "GPT-5.3-Codex-Spark",
        "spark_candidate",
        "spark_delegate",
        "thin_source_route",
        "Team Creator",
    ),
    "decisions/ADR-0004-team-formation-orchestration-gate.md": (
        "Team Creator",
        "team_plan",
        "no_team_reason",
        "return_contract",
        "adoption_gate",
        "stopline_owner",
    ),
    "decisions/ADR-0006-orchestration-spark-ops-gate.md": (
        "orchestration_gate_check",
        "spark_candidate",
        "GPT-5.3-Codex-Spark",
        "packet-file",
    ),
    "OPERATIONAL_GUARANTEE.md": (
        "scripts/orchestration_gate_check.py",
        "orchestration_required",
        "spark_candidate",
    ),
    "ROADMAP.md": (
        "Team Formation / Orchestration",
        "orchestration_gate_check",
        "GPT-5.3-Codex-Spark",
    ),
}

YES_REQUIRED_FIELDS = (
    "delegate_plan",
    "codex_main_role",
    "return_to",
    "precheck",
    "route_mode",
    "budget",
)
TEAM_PLAN_REQUIRED_FIELDS = (
    "task",
    "roles",
    "delegate_plan",
    "return_contract",
    "adoption_gate",
    "stopline_owner",
)
SPARK_SUITABLE_PHRASES = (
    "diff要約",
    "比較表",
    "test log",
    "lint/test",
    "候補抽出",
)
SPARK_FORBIDDEN_PATTERNS = (
    (re.compile(r"type\s*1|type1", re.IGNORECASE), "type1"),
    (re.compile(r"final\s+decision", re.IGNORECASE), "final decision"),
    (re.compile(r"publication", re.IGNORECASE), "publication"),
    (re.compile(r"credential|auth_settings|destructive", re.IGNORECASE), "type1"),
)
FIELD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")


def _parse_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        match = FIELD_RE.match(line)
        if not match:
            continue
        key, value = match.groups()
        fields[key] = value.strip()
    return fields


def _field_present(fields: dict[str, str], key: str) -> bool:
    value = fields.get(key)
    if value is None:
        return False
    return value != "" and value.lower() not in {"missing", "unknown", "none", "n/a"}


def evaluate_packet(text: str) -> list[str]:
    """Validate a minimal orchestration / Spark packet text."""
    errors: list[str] = []
    fields = _parse_fields(text)
    lowered = text.lower()

    if not _field_present(fields, "orchestration_required"):
        errors.append("packet missing required field: orchestration_required")
        return errors

    required = fields["orchestration_required"].strip().lower()
    if required not in {"yes", "no"}:
        errors.append("orchestration_required must be yes or no")
        return errors

    if required == "no":
        if not _field_present(fields, "orchestration_reason"):
            errors.append("orchestration_required: no requires orchestration_reason")
        return errors

    for field in YES_REQUIRED_FIELDS:
        if not _field_present(fields, field):
            errors.append(f"orchestration_required: yes requires {field}")

    has_team_plan = _field_present(fields, "team_plan")
    has_no_team_reason = _field_present(fields, "no_team_reason")
    if not has_team_plan and not has_no_team_reason:
        errors.append("nontrivial packet requires team_plan or no_team_reason")

    if has_team_plan:
        for field in TEAM_PLAN_REQUIRED_FIELDS:
            if not _field_present(fields, field):
                errors.append(f"team_plan requires {field}")

    spark_suitable = any(phrase.lower() in lowered for phrase in SPARK_SUITABLE_PHRASES)
    if spark_suitable and not _field_present(fields, "spark_candidate"):
        errors.append("spark-suitable task requires spark_candidate")

    routing = fields.get("routing_decision", "").strip().lower()
    if routing == "spark_delegate":
        for pattern, label in SPARK_FORBIDDEN_PATTERNS:
            if pattern.search(text):
                errors.append(
                    f"spark_delegate cannot own {label}; keep final authority on main runtime"
                )

    return errors


def evaluate_docs() -> dict[str, object]:
    errors: list[str] = []
    checked: dict[str, bool] = {}
    for relpath, terms in DOC_CONTRACTS.items():
        path = ROOT / relpath
        if not path.exists():
            errors.append(f"missing required file: {relpath}")
            checked[relpath] = False
            continue
        text = path.read_text(encoding="utf-8")
        missing = [term for term in terms if term not in text]
        if missing:
            for term in missing:
                errors.append(f"{relpath} missing required term: {term}")
            checked[relpath] = False
        else:
            checked[relpath] = True
    return {"ok": not errors, "checked": checked, "errors": errors}


def evaluate(packet_file: Path | None = None) -> dict[str, object]:
    docs = evaluate_docs()
    errors = list(docs["errors"])  # type: ignore[arg-type]
    packet_result: dict[str, object] | None = None

    if packet_file is not None:
        if not packet_file.exists():
            errors.append(f"packet file missing: {packet_file}")
            packet_result = {"path": str(packet_file), "ok": False, "errors": ["missing"]}
        else:
            packet_errors = evaluate_packet(packet_file.read_text(encoding="utf-8"))
            errors.extend(packet_errors)
            packet_result = {
                "path": str(packet_file),
                "ok": not packet_errors,
                "errors": packet_errors,
            }

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "docs": docs,
        "packet": packet_result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--packet-file",
        type=Path,
        help="Optional orchestration packet to validate.",
    )
    args = parser.parse_args()

    result = evaluate(packet_file=args.packet_file)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"FDE ORCHESTRATION GATE CHECK {result['overall'].upper()}")
        print(f"external_actions_performed: {str(result['external_actions_performed']).lower()}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
