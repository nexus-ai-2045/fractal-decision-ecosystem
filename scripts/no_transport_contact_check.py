#!/usr/bin/env python3
"""Check AI contact contract hardening without approving transport implementation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "ai-contact-safety-contract.md"

REQUIRED_CONTRACT_TERMS = (
    "Contact Packet Schema Candidate",
    "contact_packet:",
    "packet_id:",
    "verification_method:",
    "consent_scope:",
    "ttl:",
    "checksum:",
    "human_approved_at:",
    "replay_protection:",
    "transport_adapter_status: unapproved",
    "contact は `blocked`",
    "transport adapter は未承認",
)

FORBIDDEN_TRANSPORT_IMPLEMENTATION_TERMS = (
    "BluetoothSocket",
    "navigator.bluetooth",
    "wifiDirect",
    "WiFiDirect",
    "createRfcommSocket",
    "p2p_connect",
    "cloud_relay_send",
    "nearbyConnection",
)


def _text_files() -> list[Path]:
    paths: list[Path] = []
    for pattern in ("*.py", "*.ps1", "*.html", "*.toml"):
        paths.extend(ROOT.rglob(pattern))
    return sorted(
        path
        for path in set(paths)
        if ".git" not in path.parts and "__pycache__" not in path.parts
        and path != Path(__file__).resolve()
    )


def evaluate() -> dict[str, object]:
    errors: list[str] = []
    if not CONTRACT.exists():
        errors.append("ai-contact-safety-contract.md is missing")
        contract_text = ""
    else:
        contract_text = CONTRACT.read_text(encoding="utf-8")

    for term in REQUIRED_CONTRACT_TERMS:
        if term not in contract_text:
            errors.append(f"AI contact contract missing required term: {term}")

    for path in _text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        relpath = path.relative_to(ROOT).as_posix()
        for term in FORBIDDEN_TRANSPORT_IMPLEMENTATION_TERMS:
            if term in text:
                errors.append(f"{relpath}: transport implementation term is not approved: {term}")

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "transport_adapter_approved": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = evaluate()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"FDE NO-TRANSPORT CONTACT CHECK {result['overall'].upper()}")
        print(f"external_actions_performed: {str(result['external_actions_performed']).lower()}")
        print(f"transport_adapter_approved: {str(result['transport_adapter_approved']).lower()}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
