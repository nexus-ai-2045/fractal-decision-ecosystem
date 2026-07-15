#!/usr/bin/env python3
"""FDE のlocal operational closeoutを read-only JSON として返す。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.fde_workflow_check import evaluate as evaluate_workflow
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


def _git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip()


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


def evaluate(run_pytest: bool = True, target_receipt: Path | None = None, target_manifest: Path | None = None, target_repo: Path | None = None) -> dict[str, object]:
    checks: dict[str, dict[str, object]] = {
        "workflow": evaluate_workflow(),
        "public_ready": _run_public_ready(),
        "pre_publication": evaluate_pre_publication(),
        "roadmap": evaluate_roadmap(),
        "residual_zero_goal": evaluate_residual_zero_goal(),
        "no_transport_contact": evaluate_no_transport_contact(),
        "residual_zero_contract": evaluate_residual_zero_contract(),
        "visual_html_smoke": evaluate_visual_html_smoke(),
        "public_kernel_diff": evaluate_public_kernel_diff(),
        "human_review_packet": evaluate_human_review_packet(),
    }
    if run_pytest:
        checks["pytest"] = _run_pytest()
    if target_receipt is not None:
        try:
            if target_manifest is None:
                raise ValueError("target manifest required")
            receipt = json.loads(target_receipt.read_text(encoding="utf-8"))
            manifest = load_manifest(target_manifest, target_repo=target_repo)
            schema = json.loads((ROOT / "schemas/fde_target_workflow_receipt.v1.schema.json").read_text(encoding="utf-8"))
            validate(receipt, schema)
            expected = {item["name"]: __import__("hashlib").sha256(json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest() for item in manifest["checks"]}
            actual = {item["name"]: item.get("check_digest") for item in receipt["checks"]}
            complete = len(receipt["checks"]) == receipt["expected_check_count"] == len(manifest["checks"]) and all(item.get("status") == "passed" for item in receipt["checks"])
            current_trust = _verify_trust(manifest)
            bound = receipt["workflow_id"] == manifest["workflow_id"] and receipt["manifest_digest"] == manifest["manifest_digest"] and actual == expected and isinstance(current_trust, dict) and receipt["trust_attestation"] == current_trust
            residues = receipt.get("implementation_residue") == "none" and receipt.get("operation_residue") == "human_review_required" and receipt.get("external_public_residue") == "approval_gated"
            ok = receipt["state"] == "human_review_required" and complete and bound and residues and receipt["external_actions_performed"] is False
            checks["target_workflow"] = {"ok": ok, "consistency_ok": ok, "evidence_integrity": "local_unsealed_consistency", "state": receipt.get("state"), "manifest_digest": receipt.get("manifest_digest"), "operational_guarantee": "human_review_required", "external_actions_performed": False}
        except Exception:
            checks["target_workflow"] = {"ok": False, "state": "receipt_invalid", "external_actions_performed": False}

    errors: list[str] = []
    for name, result in checks.items():
        ok = result.get("ok") if "ok" in result else result.get("overall") == "ok"
        if not ok:
            errors.append(f"{name} failed")

    branch = _git(["branch", "--show-current"])
    head = _git(["rev-parse", "--short", "HEAD"])
    relation = _git(["status", "--short", "--branch"]).splitlines()[0]
    target_review_required = bool(checks.get("target_workflow", {}).get("ok"))

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "branch": branch,
        "head": head,
        "branch_relation": relation,
        "implementation_residue": "none" if not errors else "unknown",
        "operation_residue": "human_review_required" if target_review_required else ("none" if not errors else "unknown"),
        "external_public_residue": "approval_gated",
        "next_required_human_decision": "target PR human review" if target_review_required else "publication approval only if public release is requested",
        "later_publication_gate": "publication approval only if public release is requested",
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--skip-pytest", action="store_true")
    parser.add_argument("--target-receipt", type=Path)
    parser.add_argument("--target-manifest", type=Path)
    parser.add_argument("--target-repo", type=Path)
    args = parser.parse_args()
    result = evaluate(run_pytest=not args.skip_pytest, target_receipt=args.target_receipt, target_manifest=args.target_manifest, target_repo=args.target_repo)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"FDE OPERATIONAL CLOSEOUT {result['overall'].upper()}")
        print(f"implementation_residue: {result['implementation_residue']}")
        print(f"operation_residue: {result['operation_residue']}")
        print(f"external_public_residue: {result['external_public_residue']}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
