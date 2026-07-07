#!/usr/bin/env python3
"""Check the local FDE roadmap contract without external actions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "ROADMAP.md"

REQUIRED_TERMS = (
    "状態: 初回実装サイクル準備完了",
    "ローカル実装残務ゼロ",
    "外部 action: なし",
    "## 完成図",
    "Now",
    "Next",
    "Future",
    "Core/Product",
    "Team Formation / Orchestration",
    "UX/Product Design",
    "Security",
    "AI/OpenAI Dev",
    "Creative/Comms",
    "Operations",
    "goal",
    "evidence",
    "gate",
    "owner",
    "done_when",
    "human review",
    "merge は人間目視レビュー後",
    "ローカル実装残務: なし",
    "Roadmap gate は `scripts/mvp_gate_check.py` に接続済み",
    "Team formation / orchestration は `decisions/ADR-0004-team-formation-orchestration-gate.md` に記録済み。",
    "Implementation Orchestration",
    "Implementation Roadmap",
    "Sprint 0: Post-Merge Verification Receipt",
    "状態: ローカル完了",
    "Sprint 2: AI Contact Safety Contract Hardening",
    "Sprint 2.5: Team Formation / Orchestration Gate",
    "状態: 次のFDE-native実装候補",
    "Sprint 4: Public Kernel / Rights Diff Automation",
    "Sprint 6: Human-Gated Publication / Filing Package",
    "chat-orchestrator",
    "codex-security",
    "Product Design / Creative Production",
    "no-external-action",
    "MVP_SCOPE_REVIEW_2026-07-02.md",
    "Team Creator",
    "team_plan",
    "no_team_reason",
    "return_contract",
    "adoption_gate",
)

REQUIRED_LANES = (
    "Core/Product",
    "Team Formation / Orchestration",
    "UX/Product Design",
    "Security",
    "AI/OpenAI Dev",
    "Creative/Comms",
    "Operations",
)


def evaluate() -> dict[str, object]:
    errors: list[str] = []
    if not ROADMAP.exists():
        errors.append("ROADMAP.md is missing")
        text = ""
    else:
        text = ROADMAP.read_text(encoding="utf-8")

    for term in REQUIRED_TERMS:
        if term not in text:
            errors.append(f"ROADMAP.md missing required term: {term}")

    missing_lanes = [lane for lane in REQUIRED_LANES if f"| {lane} |" not in text]
    for lane in missing_lanes:
        errors.append(f"ROADMAP.md missing lane row: {lane}")

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "first_iteration": {
            "status": "ready" if not errors else "blocked",
            "scope": "local roadmap contract",
            "human_review_required_before_merge": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = evaluate()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"FDE ROADMAP GATE CHECK {result['overall'].upper()}")
        print(f"external_actions_performed: {str(result['external_actions_performed']).lower()}")
        print(f"first_iteration_status: {result['first_iteration']['status']}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
