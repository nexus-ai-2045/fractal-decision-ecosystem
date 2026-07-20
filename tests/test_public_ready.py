import hashlib
import copy
import json
import os
import subprocess
from pathlib import Path

import pytest

from scripts import fde_operational_closeout
from scripts import public_ready_check
from scripts.adr_next import next_adr_filename
from scripts.mvp_gate_check import evaluate as evaluate_mvp_gate
from scripts.fde_architecture_drift_check import evaluate as evaluate_fde_architecture_drift
from scripts.fde_operational_closeout import evaluate as evaluate_fde_operational_closeout
from scripts.fde_operational_closeout import _validate_execution_receipt
from scripts.fde_workflow_check import evaluate as evaluate_fde_workflow
from scripts.pre_publication_gate_check import evaluate as evaluate_pre_publication
from scripts.pre_publication_gate_check import forbidden_patent_material_paths
from scripts.pre_publication_gate_check import validate_sha256_manifest
from scripts.public_ready_check import main as public_ready_main
from scripts.human_review_packet_check import evaluate as evaluate_human_review_packet
from scripts.no_transport_contact_check import evaluate as evaluate_no_transport_contact
from scripts.public_kernel_diff_manifest import evaluate as evaluate_public_kernel_diff
from scripts.residual_zero_goal_check import evaluate as evaluate_residual_zero_goal
from scripts.roadmap_gate_check import evaluate as evaluate_roadmap_gate
from scripts.verify_residual_zero_contract import evaluate as evaluate_residual_zero_contract
from scripts.visual_html_smoke import evaluate as evaluate_visual_html_smoke


def test_mvp_gate_is_the_top_level_gate_without_recursive_pytest() -> None:
    result = evaluate_mvp_gate(run_pytest=False)
    assert result["overall"] == "ok", result["checks"]


def test_public_ready_check_passes_as_nested_mvp_check() -> None:
    assert public_ready_main() == 0


def _fake_private_handle_trailer() -> str:
    # このリポジトリ自身が check_forbidden_patterns() で全 .py file を走査するため、
    # fixture 内の禁止 token をソース上で非連続に組み立て、file scan の誤検知を避ける。
    handle = "say" + "_yas"
    email_user = "tama" + "goe"
    return f"Co-authored-by: {handle} <{email_user}@gmail.com>\n"


def _fake_windows_path_fragment() -> str:
    drive = "C:"
    sep = "\\" + "Users" + "\\"
    return drive + sep + "example" + "\\Projects\\shared\\scripts\\preflight.py"


def _fake_posix_path_fragment() -> str:
    return "/" + "Users" + "/example/Projects/shared/scripts/preflight.py"


def test_git_history_scan_passes_on_clean_log_text() -> None:
    clean_log_text = (
        "Nexus AI <noreply@nexus-ai.local> Nexus AI <noreply@nexus-ai.local> "
        "Add roadmap gate drift guard\n"
        "\n"
        "## 概要\n"
        "roadmap gate に必須語を追加した。\n"
        "\n"
        "## 検証\n"
        "- `python -m pytest -q`\n"
        "\n"
        "Co-authored-by: Nexus AI <noreply@nexus-ai.local>\n"
    )

    assert public_ready_check.scan_git_log_text_for_forbidden_patterns(clean_log_text) == []


def test_git_history_scan_detects_private_handle_in_commit_body_trailer() -> None:
    dirty_log_text = (
        "nexus_ai <nexus.ai.2045@gmail.com> nexus_ai <nexus.ai.2045@gmail.com> "
        "Add roadmap gate drift guard (#3)\n"
        "\n"
        "## 概要\n"
        "roadmap gate に必須語を追加した。\n"
        "\n"
        "Co-authored-by: Nexus AI <noreply@nexus-ai.local>\n"
        f"{_fake_private_handle_trailer()}"
    )

    errors = public_ready_check.scan_git_log_text_for_forbidden_patterns(dirty_log_text)

    assert any("private handle" in error for error in errors)


def test_git_history_scan_detects_windows_local_path_in_commit_body() -> None:
    dirty_log_text = (
        "nexus_ai <nexus.ai.2045@gmail.com> nexus_ai <nexus.ai.2045@gmail.com> "
        "Add AI contact safety contract (#8)\n"
        "\n"
        "## 検証\n"
        f"- `python {_fake_windows_path_fragment()}`\n"
        "\n"
        "Co-authored-by: Nexus AI <noreply@nexus-ai.local>\n"
    )

    errors = public_ready_check.scan_git_log_text_for_forbidden_patterns(dirty_log_text)

    assert any("personal absolute path" in error for error in errors)


def test_git_history_scan_detects_posix_style_local_path_in_commit_body() -> None:
    dirty_log_text = (
        "nexus_ai <nexus.ai.2045@gmail.com> nexus_ai <nexus.ai.2045@gmail.com> "
        "Add AI contact safety contract (#8)\n"
        "\n"
        "## 検証\n"
        f"- `python {_fake_posix_path_fragment()}`\n"
        "\n"
        "Co-authored-by: Nexus AI <noreply@nexus-ai.local>\n"
    )

    errors = public_ready_check.scan_git_log_text_for_forbidden_patterns(dirty_log_text)

    assert any("personal absolute path" in error for error in errors)


def test_pre_publication_gate_check_passes() -> None:
    result = evaluate_pre_publication()
    assert result["overall"] == "ok", result["errors"]


def test_fde_workflow_manifest_is_machine_readable_without_external_action() -> None:
    result = evaluate_fde_workflow()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert result["workflow"]["control_plane"] == "FDE"
    assert "external_approval_required" in result["workflow"]["states"]
    assert result["workflow"]["closed_loop_sequence"] == [
        "goal_and_boundary",
        "capability_inventory",
        "roadmap",
        "preflight",
        "implement",
        "verify",
        "operational_guarantee",
        "feedback",
        "system_update",
    ]
    assert result["workflow"]["capability_inventory_order"] == [
        "official_capability",
        "oss_prior_art",
        "local_ssot",
        "existing_wrapper_or_library",
        "gap_only_to_implement",
    ]
    assert result["workflow"]["verification_layers"] == [
        "lint",
        "unit",
        "integration",
        "smoke",
        "e2e",
        "regression",
    ]
    assert result["workflow"]["system_update_targets"] == [
        "route",
        "skill",
        "gate",
        "test",
        "ssot",
        "roadmap",
    ]
    assert result["workflow"]["learning_return_to"] == "goal_and_boundary"
    assert result["workflow"]["feedback_contract"] == [
        "failure_kind",
        "evidence",
        "system_update_target",
        "regression_test",
        "promotion_decision",
        "rollback_path",
    ]
    assert result["workflow"]["closed_loop_transitions"][-1] == "system_update->goal_and_boundary"
    assert "verify=test_evidence" in result["workflow"]["state_evidence_contract"]
    assert any(
        binding.startswith("verify=compileall+git_diff_check+pytest")
        for binding in result["workflow"]["state_gate_bindings"]
    )
    assert result["workflow"]["target_workflow_runner"] == {
        "manifest_schema": "fde.target_workflow.v1",
        "stop_at": "review_packet",
        "receipt": "metadata_only",
        "external_actions_performed": False,
    }


def test_release_please_uses_existing_unprefixed_v_tag_contract() -> None:
    root = public_ready_check.ROOT
    config = json.loads((root / "release-please-config.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / ".release-please-manifest.json").read_text(encoding="utf-8"))
    package = config["packages"]["."]

    assert package["include-v-in-tag"] is True
    assert package["include-component-in-tag"] is False
    assert (root / "version.txt").read_text(encoding="utf-8").strip() == manifest["."]


def test_fde_workflow_rejects_an_incomplete_learning_contract(tmp_path) -> None:
    workflow = tmp_path / "fde_workflow.yaml"
    text = (public_ready_check.ROOT / "fde_workflow.yaml").read_text(encoding="utf-8")
    workflow.write_text(
        text.replace("  - rollback_path\n", "", 1).replace("  - regression\n", ""),
        encoding="utf-8",
    )

    result = evaluate_fde_workflow(workflow)

    assert result["overall"] == "error"
    assert "verification_layers is missing, contains unknown values, or is out of order" in result["errors"]
    assert "learning_adoption_requires is missing, contains unknown values, or is out of order" in result["errors"]


def test_fde_workflow_rejects_an_out_of_order_closed_loop(tmp_path) -> None:
    workflow = tmp_path / "fde_workflow.yaml"
    text = (public_ready_check.ROOT / "fde_workflow.yaml").read_text(encoding="utf-8")
    workflow.write_text(
        text.replace(
            "  - feedback\n  - system_update\n  - closeout",
            "  - system_update\n  - feedback\n  - closeout",
            1,
        ),
        encoding="utf-8",
    )

    result = evaluate_fde_workflow(workflow)

    assert result["overall"] == "error"
    assert "states is missing, contains unknown values, or is out of order" in result["errors"]


@pytest.mark.parametrize(
    "mutation, expected_error",
    (
        (lambda text: text + "invalid yaml\n", "invalid manifest syntax"),
        (
            lambda text: text.replace(
                "external_actions_performed: false",
                "external_actions_performed: true\n# external_actions_performed: false",
            ),
            "comments and tabs are not allowed",
        ),
        (
            lambda text: text.replace(
                "learning_return_to: goal_and_boundary",
                "learning_return_to: nowhere\nlearning_return_to: goal_and_boundary",
            ),
            "duplicate key: learning_return_to",
        ),
        (
            lambda text: text.replace("  - pytest\n", ""),
            "required_local_gates is missing, contains unknown values, or is out of order",
        ),
        (
            lambda text: text.replace("  stop_at: review_packet", "  stop_at: merge"),
            "target_workflow_runner is missing, contains unknown values, or has invalid values",
        ),
        (
            lambda text: text.replace(
                "  receipt: metadata_only",
                "  receipt: metadata_only\n  bypass: allowed",
            ),
            "unknown mapping key in target_workflow_runner: bypass",
        ),
    ),
)
def test_fde_workflow_fails_closed_on_ambiguous_or_spoofed_input(
    tmp_path,
    mutation,
    expected_error,
) -> None:
    workflow = tmp_path / "fde_workflow.yaml"
    text = (public_ready_check.ROOT / "fde_workflow.yaml").read_text(encoding="utf-8")
    workflow.write_text(mutation(text), encoding="utf-8")

    result = evaluate_fde_workflow(workflow)

    assert result["overall"] == "error"
    assert any(expected_error in error for error in result["errors"])


def test_public_ready_ci_installs_declared_project_dependencies() -> None:
    workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "public-ready.yml").read_text(encoding="utf-8")
    assert "python -m pip install -r requirements-dev.txt" in workflow


def test_fde_architecture_drift_check_connects_docs_scripts_and_tests() -> None:
    result = evaluate_fde_architecture_drift()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert "fde_workflow.yaml" in result["checked_files"]
    assert "scripts/fde_operational_closeout.py" in result["checked_files"]


def test_fde_operational_closeout_reports_residue_without_public_action() -> None:
    result = evaluate_fde_operational_closeout(run_pytest=False)
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert result["implementation_residue"] == "none"
    assert result["operation_residue"] in {"none", "uncommitted_changes"}
    assert result["worktree_clean"] is (result["operation_residue"] == "none")
    assert result["delivery_residue"] in {
        "none",
        "upstream_not_configured",
        "branch_not_synchronized",
        "git_state_unavailable",
    }
    assert result["local_residual_zero"] is (
        result["operation_residue"] == "none"
        and result["delivery_residue"] == "none"
        and result["human_review"]["ok"] is True
    )
    assert result["residual_zero"] is (
        result["local_residual_zero"] and result["remote_ci"]["ok"] is True
    )
    assert result["external_public_residue"] == "approval_gated"
    assert result["checks"]["architecture_drift"]["overall"] == "ok"
    assert "fde_workflow.yaml is the machine-readable closed-loop SSOT" in result["context_to_preserve"]


def test_fde_operational_closeout_delivery_state_is_machine_readable() -> None:
    result = evaluate_fde_operational_closeout(
        run_pytest=False,
        require_delivery_ready=False,
    )
    for field in (
        "gate_health",
        "worktree_clean",
        "changed_entries",
        "upstream",
        "ahead",
        "behind",
        "delivery_residue",
        "residual_zero",
        "context_to_preserve",
        "resume_checks",
        "workflow_execution_receipt",
        "remote_ci",
    ):
        assert field in result
    receipt = result["workflow_execution_receipt"]
    assert receipt["schema_version"] == "fde.execution.receipt.v1"
    assert len(receipt["gate_receipt_sha256"]) == 64
    assert receipt["planned_transitions"][-1] == "system_update->goal_and_boundary"
    assert receipt["transition_events"][-1]["status"] == "blocked"
    assert set(receipt["verification"]) == {
        "lint",
        "unit",
        "integration",
        "smoke",
        "e2e",
        "regression",
    }
    assert receipt["check_events"]
    assert all(len(event["result_sha256"]) == 64 for event in receipt["check_events"])


def test_fde_operational_closeout_reads_updated_artifacts_from_pr_merge_commit(
    monkeypatch,
) -> None:
    calls: list[list[str]] = []

    def fake_git(args: list[str], *, allow_failure: bool = False) -> str:
        calls.append(args)
        return "scripts/fde_operational_closeout.py\ntests/test_public_ready.py"

    monkeypatch.setattr(fde_operational_closeout, "_git", fake_git)

    artifacts = fde_operational_closeout._implemented_artifacts(
        {"changed_entries": []},
        "merge-head",
    )

    assert artifacts == [
        "scripts/fde_operational_closeout.py",
        "tests/test_public_ready.py",
    ]
    assert calls == [
        [
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-only",
            "-r",
            "-m",
            "--first-parent",
            "merge-head",
        ]
    ]


def test_fde_closed_loop_e2e_contract_reaches_closeout() -> None:
    result = evaluate_fde_operational_closeout(run_pytest=False)
    receipt = result["workflow_execution_receipt"]

    assert result["gate_health"] == "ok"
    assert receipt["planned_transitions"][0] == "goal_and_boundary->capability_inventory"
    assert receipt["planned_transitions"][-1] == "system_update->goal_and_boundary"
    assert receipt["transition_events"][-1]["status"] == "blocked"
    assert {event["name"] for event in receipt["check_events"]} >= {
        "workflow",
        "architecture_drift",
        "pre_publication",
        "visual_html_smoke",
        "compileall",
        "git_diff_check",
    }


def test_fde_execution_receipt_validator_detects_tampering() -> None:
    result = evaluate_fde_operational_closeout(run_pytest=False)
    receipt = copy.deepcopy(result["workflow_execution_receipt"])
    transitions = list(receipt["planned_transitions"])

    assert _validate_execution_receipt(receipt, result["checks"], transitions) == []

    receipt["gate_receipt_sha256"] = "0" * 64
    receipt["transition_events"][-1]["evidence"] = []
    errors = _validate_execution_receipt(receipt, result["checks"], transitions)

    assert "execution receipt gate digest mismatch" in errors
    assert "execution receipt transition event is incomplete" in errors


def test_fde_execution_receipt_validator_rejects_duplicate_events_and_fake_evidence() -> None:
    result = evaluate_fde_operational_closeout(run_pytest=False)
    receipt = copy.deepcopy(result["workflow_execution_receipt"])
    transitions = list(receipt["planned_transitions"])

    receipt["check_events"][1] = copy.deepcopy(receipt["check_events"][0])
    receipt["verification"]["e2e"] = {
        "status": "applied",
        "evidence": ["not-a-real-check"],
        "waiver": None,
    }
    errors = _validate_execution_receipt(receipt, result["checks"], transitions)

    assert "execution receipt check event names are missing, duplicated, or out of order" in errors
    assert "execution receipt verification evidence is unknown: e2e" in errors


def test_fde_dependency_registry_reuses_existing_learning_authorities() -> None:
    text = (public_ready_check.ROOT / "dependency-registry.md").read_text(encoding="utf-8")
    for term in (
        "| official-capability |",
        "measurement-gate",
        "operational-command-smoke",
        "runtime-guarantee-matrix",
        "low-pdca-orchestrator",
        "external-authority",
        "operator-local-adapter",
    ):
        assert term in text


def test_fde_dependency_registry_has_no_private_filesystem_authority_paths() -> None:
    text = (public_ready_check.ROOT / "dependency-registry.md").read_text(encoding="utf-8")
    private_markers = (
        "Documents/brain/",
        "Documents/lanes/",
        "Documents/reports/",
        "Documents/references/",
        "~/.claude/",
        "/Applications/",
        "/Users/",
        "/home/",
    )
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        for marker in private_markers:
            assert marker not in line, f"authority row embeds private path: {line}"


def test_source_pointers_resolve_without_opaque_imported_source_only_rows() -> None:
    text = (public_ready_check.ROOT / "source-pointers.md").read_text(encoding="utf-8")
    assert "公開解決先" in text
    assert "| imported-source |" not in text
    assert "Documents/" not in text


def test_roadmap_gate_has_first_iteration_contract_without_external_write() -> None:
    result = evaluate_roadmap_gate()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert result["first_iteration"]["status"] == "ready"


def test_residual_zero_goal_check_passes_without_external_write() -> None:
    result = evaluate_residual_zero_goal()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert result["goal"]["status"] == "ready"


def test_residual_zero_goal_defines_three_pr_closeout() -> None:
    text = (public_ready_check.ROOT / "RESIDUAL_ZERO_GOAL_2026-07-05.md").read_text(
        encoding="utf-8"
    )
    for term in (
        "implementation",
        "operation",
        "external/public",
        "Blocker Ledger",
        "Three-PR Plan",
        "PR 1: Team Formation + Residual Zero Goal",
        "PR 2: Contact Safety + Residual Operation Smoke",
        "PR 3: Public Boundary Package + Operational Closeout",
        "no_transport_contact_check.py",
        "verify_residual_zero_contract.py",
        "visual_html_smoke.py",
        "public_kernel_diff_manifest.py",
        "human_review_packet_check.py",
        "external actions remain false",
    ):
        assert term in text


def test_no_transport_contact_check_passes_without_external_write() -> None:
    result = evaluate_no_transport_contact()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert result["transport_adapter_approved"] is False


def test_residual_zero_contract_check_passes_without_external_write() -> None:
    result = evaluate_residual_zero_contract()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert result["residual_zero_scope"] == "repository-local implementation and operation only"


def test_visual_html_smoke_passes_without_external_write() -> None:
    result = evaluate_visual_html_smoke()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert result["href_count"] > 0


def test_system_overview_visualizes_fde_control_plane() -> None:
    text = (public_ready_check.ROOT / "SYSTEM_OVERVIEW.md").read_text(encoding="utf-8")
    for term in (
        "FDE 全体図",
        "```mermaid",
        "判断制御面",
        "ローカル運用面",
        "公開境界面",
        "entry -> packet -> evidence -> decision -> closure",
        "visual.html",
        "fde_workflow.yaml",
        "scripts/fde_operational_closeout.py",
        "隣接product adapter",
        "機能マップ",
        "roadmap funnel",
        "## 継続学習面",
        "operational guarantee",
        "feedback / failure classification",
        "route / skill / gate / test",
    ):
        assert term in text


def test_public_kernel_diff_manifest_passes_without_public_action() -> None:
    result = evaluate_public_kernel_diff()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert result["manifest"]["status"] == "local_public_kernel_diff_manifest"
    assert result["manifest"]["files"]


def test_human_review_packet_check_passes_without_public_action() -> None:
    result = evaluate_human_review_packet()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert result["approved_operation_now"] == "none"


def test_roadmap_implementation_plan_is_guarded_by_tests() -> None:
    text = (public_ready_check.ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    for term in (
        "Implementation Orchestration",
        "Implementation Roadmap",
        "Sprint 0: Post-Merge Verification Receipt",
        "状態: ローカル完了",
        "Sprint 1: Roadmap / Gate Drift Guard",
        "Sprint 2: AI Contact Safety Contract Hardening",
        "Sprint 2.5: Team Formation / Orchestration Gate",
        "状態: 次のFDE-native実装候補",
        "Team Creator",
        "team_plan",
        "no_team_reason",
        "return_contract",
        "adoption_gate",
        "Sprint 4: Public Kernel / Rights Diff Automation",
        "Sprint 6: Human-Gated Publication / Filing Package",
        "public release、visibility 変更、patent filing",
    ):
        assert term in text


def test_operational_guarantee_records_post_merge_receipts_without_public_approval() -> None:
    text = (public_ready_check.ROOT / "OPERATIONAL_GUARANTEE.md").read_text(encoding="utf-8")
    for term in (
        "Post-Merge Receipts",
        "未実装ロードマップ",
        "future scope",
        "#7",
        "af1af13e444c2dad0f9878e77d243ae98c469fb9",
        "#8",
        "a627c1683a2cd7b08cc29a31bacd4bae73d2e034",
        "public release、repository visibility 変更、external sending、patent filing の承認ではありません",
        "scripts/public_kernel_diff_manifest.py",
        "scripts/human_review_packet_check.py",
        "scripts/pr_review_signal_check.py",
        "human_review_required",
        "レビュー済みとは言いません",
    ):
        assert term in text


def test_review_signal_absorption_rule_keeps_checks_and_review_separate() -> None:
    text = (public_ready_check.ROOT / "docs" / "review-signal-absorption.md").read_text(encoding="utf-8")
    for term in (
        "CI成功、bot check成功、bot review comment、人間レビューを混ぜない",
        "scripts/pr_review_signal_check.py",
        "statusCheckRollup",
        "human_review_required",
        "Cursor Bugbotがdisabled",
        "CI成功だけで2または3を満たしたとは扱わない",
    ):
        assert term in text


def test_publication_review_packet_is_not_public_approval() -> None:
    text = (public_ready_check.ROOT / "PUBLICATION_REVIEW_PACKET.md").read_text(encoding="utf-8")
    for term in (
        "状態: review packet のみ / public action 承認なし",
        "Repository: `nexus-ai-2045/fractal-decision-ecosystem`",
        "現在の visibility: public",
        "visibility 変更は実施済み",
        "以後の変更は再承認制",
        "現時点で承認された操作: なし",
        "この packet による external action 実行: false",
        "gh repo edit nexus-ai-2045/fractal-decision-ecosystem --visibility public",
        "この packet から repository public 化を実行しない",
        "local gate success を publication approval として扱わない",
    ):
        assert term in text


def test_mvp_scope_review_records_smoke_preflight_and_scope_boundary() -> None:
    text = (public_ready_check.ROOT / "MVP_SCOPE_REVIEW_2026-07-02.md").read_text(encoding="utf-8")
    for term in (
        "local smoke / preflight review complete",
        "External actions: none",
        "FDE MVP GATE CHECK OK",
        "18 passed",
        "entry -> packet -> evidence -> decision -> closure",
        "Sprint 0 is locally complete",
        "Sprint 1 is locally complete",
        "Sprint 2 is the next FDE-native work",
        "Device app, OS service, avatar, voice UI, Bluetooth, Wi-Fi, P2P, cloud relay",
        "Publication remains approval-gated",
    ):
        assert term in text


def test_adr_auto_numbering_uses_next_repo_local_number(tmp_path) -> None:
    assert next_adr_filename(decisions_dir=tmp_path) == "ADR-0001-short-title.md"
    (tmp_path / "ADR-0001-first-decision.md").write_text("# ADR-0001\n", encoding="utf-8")
    (tmp_path / "notes.md").write_text("not an ADR\n", encoding="utf-8")

    assert next_adr_filename(decisions_dir=tmp_path) == "ADR-0002-short-title.md"


def test_mvp_axis_operating_card_has_13_items_and_boundaries() -> None:
    text = (public_ready_check.ROOT / "mvp-axis-operating-card.md").read_text(encoding="utf-8")
    for term in (
        "FDE MVP軸別13運用カード",
        "MVP軸",
        "ユーザー行動",
        "最小E2E",
        "public/private境界",
        "ADR/採番",
        "python scripts\\adr_next.py",
        "MVP は public release approval ではない",
        "repository visibility 変更 approval ではない",
    ):
        assert term in text


def test_product_creative_review_path_adr_is_connected() -> None:
    text = (
        public_ready_check.ROOT / "decisions" / "ADR-0002-product-creative-review-path.md"
    ).read_text(encoding="utf-8")
    for term in (
        "Product / Creative review path",
        "visual.html",
        "ROADMAP.md",
        "OPERATIONAL_GUARANTEE.md",
        "PUBLIC_KERNEL_PLAN.md",
        "publication、external sending、repository visibility changes",
    ):
        assert term in text


def test_ai_contact_safety_contract_is_reviewable_without_external_action() -> None:
    note = (public_ready_check.ROOT / "ai-contact-safety-contract.md").read_text(encoding="utf-8")
    adr = (
        public_ready_check.ROOT / "decisions" / "ADR-0003-ai-contact-safety-contract.md"
    ).read_text(encoding="utf-8")
    for term in (
        "Contact identity 契約",
        "data boundary 契約",
        "contact packet schema 候補",
        "contact_packet:",
        "blocked",
        "revocation",
        "replay_protection",
        "transport_adapter_status: unapproved",
        "no_raw_source_pointer",
        "transport adapter は未承認",
    ):
        assert term in note
    for term in (
        "AI contact safety contract",
        "identity",
        "consent",
        "data boundary",
        "自動 contact",
        "public release",
    ):
        assert term in adr


def test_team_formation_orchestration_gate_is_reviewable_without_external_action() -> None:
    roadmap = (public_ready_check.ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    adr = (
        public_ready_check.ROOT / "decisions" / "ADR-0004-team-formation-orchestration-gate.md"
    ).read_text(encoding="utf-8")
    public_gate = (public_ready_check.ROOT / "public-kernel" / "GATES.md").read_text(encoding="utf-8")

    for term in (
        "Team Formation / Orchestration",
        "Team Creator",
        "team_plan",
        "no_team_reason",
        "return_contract",
        "adoption_gate",
        "stopline_owner",
    ):
        assert term in roadmap
        assert term in adr

    for term in (
        "Team Formation Gate",
        "Team Creator",
        "return_contract",
        "adoption_gate",
        "no_team_reason",
        "final decision",
    ):
        assert term in public_gate


def test_pre_publication_gate_detects_stale_patent_packet_manifest(tmp_path) -> None:
    packet = tmp_path / "patent-packet"
    packet.mkdir()
    source = tmp_path / "INVENTION_RECORD.md"
    source.write_text("original record\n", encoding="utf-8")
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    (packet / "MANIFEST.sha256").write_text(
        f"# manifest\n{original_hash}  INVENTION_RECORD.md\n",
        encoding="utf-8",
    )

    source.write_text("changed record\n", encoding="utf-8")

    errors = validate_sha256_manifest(
        tmp_path,
        "patent-packet/MANIFEST.sha256",
        ("INVENTION_RECORD.md",),
    )

    assert errors
    assert "hash mismatch: INVENTION_RECORD.md" in errors[0]


def test_forbidden_patent_material_paths_detects_draft_and_packet() -> None:
    tracked = [
        "README.md",
        "PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md",
        "patent-packet/MANIFEST.sha256",
        "patent-packet/README.md",
        "scripts/build_patent_packet.py",
    ]

    forbidden = forbidden_patent_material_paths(tracked)

    assert forbidden == [
        "PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md",
        "patent-packet/MANIFEST.sha256",
        "patent-packet/README.md",
    ]


def test_forbidden_patent_material_paths_is_empty_for_clean_tree() -> None:
    tracked = ["README.md", "scripts/build_patent_packet.py", "TODO_FDE_PUBLIC_KERNEL_RIGHTS.md"]

    assert forbidden_patent_material_paths(tracked) == []


def test_pre_publication_gate_rejects_tracked_patent_material_in_public_repo() -> None:
    result = subprocess.run(
        ["git", "ls-files", "PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md", "patent-packet"],
        cwd=public_ready_check.ROOT,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    tracked = [line.strip() for line in result.stdout.splitlines() if line.strip()]

    assert forbidden_patent_material_paths(tracked) == []
    gitignore_text = (public_ready_check.ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md" in gitignore_text
    assert "patent-packet/" in gitignore_text


def test_patent_disclosure_record_documents_removal_without_legal_advice() -> None:
    text = (public_ready_check.ROOT / "PATENT_DISCLOSURE_RECORD.md").read_text(encoding="utf-8")
    for term in (
        "事実記録のみ。法的助言ではない",
        "2026-07 に public 化された",
        "patent-packet/",
        "git 履歴の書き換え",
        "専門家",
        "出願する / しない",
    ):
        assert term in text


@pytest.mark.skipif(os.name != "nt", reason="Windows pyenv shim regression")
def test_run_mvp_gate_rejects_broken_windows_pyenv_shim(tmp_path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    (fake_bin / "py.cmd").write_text(
        "@echo off\r\necho py launcher unavailable 1>&2\r\nexit /b 1\r\n",
        encoding="utf-8",
    )
    (fake_bin / "python.cmd").write_text(
        "@echo off\r\necho pyenv: python: command not found\r\nexit /b 0\r\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    result = subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(public_ready_check.ROOT / "scripts" / "run_mvp_gate.ps1"),
            "--skip-pytest",
        ],
        cwd=public_ready_check.ROOT,
        env=env,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode != 0, result.stdout
    assert "pyenv shim is not usable for the MVP gate" in result.stdout
    assert "FDE MVP GATE CHECK" not in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="Windows shim regression")
def test_run_mvp_gate_requires_mvp_gate_output_even_when_python_exits_zero(tmp_path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    (fake_bin / "py.cmd").write_text(
        "@echo off\r\necho py launcher unavailable 1>&2\r\nexit /b 1\r\n",
        encoding="utf-8",
    )
    (fake_bin / "python.cmd").write_text(
        "\r\n".join(
            [
                "@echo off",
                "if \"%~1\"==\"-c\" (",
                "  echo {\"marker\":\"fde-mvp-gate-python-probe\",\"ok\":true,\"version\":[3,13,1],\"executable\":\"C:\\\\fake\\\\python.exe\"}",
                "  exit /b 0",
                ")",
                "echo python shim returned without running the MVP gate",
                "exit /b 0",
                "",
            ]
        ),
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    result = subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(public_ready_check.ROOT / "scripts" / "run_mvp_gate.ps1"),
            "--skip-pytest",
        ],
        cwd=public_ready_check.ROOT,
        env=env,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode != 0, result.stdout
    assert "MVP gate did not produce the expected gate output" in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="Windows shim regression")
def test_run_mvp_gate_accepts_json_output_with_diagnostic_prefix(tmp_path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    (fake_bin / "py.cmd").write_text(
        "@echo off\r\necho py launcher unavailable 1>&2\r\nexit /b 1\r\n",
        encoding="utf-8",
    )
    (fake_bin / "python.cmd").write_text(
        "\r\n".join(
            [
                "@echo off",
                "if \"%~1\"==\"-c\" (",
                "  echo {\"marker\":\"fde-mvp-gate-python-probe\",\"ok\":true,\"version\":[3,13,1],\"executable\":\"C:\\\\fake\\\\python.exe\"}",
                "  exit /b 0",
                ")",
                "echo diagnostic line before json",
                "echo {\"overall\":\"ok\",\"checks\":[]}",
                "exit /b 0",
                "",
            ]
        ),
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    result = subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(public_ready_check.ROOT / "scripts" / "run_mvp_gate.ps1"),
            "--json",
        ],
        cwd=public_ready_check.ROOT,
        env=env,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout
    assert "diagnostic line before json" in result.stdout
