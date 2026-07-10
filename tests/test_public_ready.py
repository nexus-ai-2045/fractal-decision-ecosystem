import hashlib
import os
import subprocess

import pytest

from scripts import public_ready_check
from scripts.adr_next import next_adr_filename
from scripts.mvp_gate_check import evaluate as evaluate_mvp_gate
from scripts.fde_architecture_drift_check import evaluate as evaluate_fde_architecture_drift
from scripts.fde_operational_closeout import evaluate as evaluate_fde_operational_closeout
from scripts.fde_workflow_check import evaluate as evaluate_fde_workflow
from scripts.pre_publication_gate_check import evaluate as evaluate_pre_publication
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


def test_pre_publication_gate_check_passes() -> None:
    result = evaluate_pre_publication()
    assert result["overall"] == "ok", result["errors"]


def test_fde_workflow_manifest_is_machine_readable_without_external_action() -> None:
    result = evaluate_fde_workflow()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert result["workflow"]["control_plane"] == "FDE"
    assert "external_approval_required" in result["workflow"]["states"]


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
    assert result["operation_residue"] == "none"
    assert result["external_public_residue"] == "approval_gated"


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
    assert result["residual_zero_scope"] == "private local implementation and operation only"


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
    ):
        assert term in text


def test_publication_review_packet_is_not_public_approval() -> None:
    text = (public_ready_check.ROOT / "PUBLICATION_REVIEW_PACKET.md").read_text(encoding="utf-8")
    for term in (
        "状態: review packet のみ / public action 承認なし",
        "Repository: `nexus-ai-2045/fractal-decision-ecosystem`",
        "現在の visibility: private",
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
