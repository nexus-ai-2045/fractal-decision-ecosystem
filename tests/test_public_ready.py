import hashlib
import os
import subprocess

import pytest

from scripts import public_ready_check
from scripts.adr_next import next_adr_filename
from scripts.mvp_gate_check import evaluate as evaluate_mvp_gate
from scripts.chinju_guidance_check import evaluate as evaluate_chinju_guidance
from scripts.linear_handoff_check import evaluate as evaluate_linear_handoff
from scripts.pre_publication_gate_check import evaluate as evaluate_pre_publication
from scripts.pre_publication_gate_check import validate_sha256_manifest
from scripts.public_ready_check import main as public_ready_main
from scripts.roadmap_gate_check import evaluate as evaluate_roadmap_gate


def test_mvp_gate_is_the_top_level_gate_without_recursive_pytest() -> None:
    result = evaluate_mvp_gate(run_pytest=False)
    assert result["overall"] == "ok", result["checks"]


def test_public_ready_check_passes_as_nested_mvp_check() -> None:
    assert public_ready_main() == 0


def test_pre_publication_gate_check_passes() -> None:
    result = evaluate_pre_publication()
    assert result["overall"] == "ok", result["errors"]


def test_linear_handoff_packet_is_ready_without_external_write() -> None:
    result = evaluate_linear_handoff()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False


def test_chinju_guidance_is_fde_specific_without_external_write() -> None:
    result = evaluate_chinju_guidance()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False


def test_roadmap_gate_has_first_iteration_contract_without_external_write() -> None:
    result = evaluate_roadmap_gate()
    assert result["overall"] == "ok", result["errors"]
    assert result["external_actions_performed"] is False
    assert result["first_iteration"]["status"] == "ready"


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


def test_local_ai_workspace_state_is_outside_repository_package() -> None:
    assert not public_ready_check.is_repository_package_path(
        public_ready_check.ROOT / ".chinju" / "sessions" / "local.jsonl"
    )
    assert public_ready_check.is_repository_package_path(public_ready_check.ROOT / ".chinju" / "README.md")
    assert public_ready_check.is_repository_package_path(public_ready_check.ROOT / "README.md")


def test_local_ai_workspace_boundary_is_declared_and_untracked() -> None:
    errors: list[str] = []
    public_ready_check.check_local_ai_workspace_boundary(errors)
    assert errors == []


def test_local_ai_workspace_boundary_requires_gitignore_entry(tmp_path, monkeypatch) -> None:
    (tmp_path / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    monkeypatch.setattr(public_ready_check, "ROOT", tmp_path)

    errors: list[str] = []
    public_ready_check.check_local_ai_workspace_boundary(errors)

    assert ".gitignore に local AI-agent workspace 除外がありません: .chinju/sessions/" in errors


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
        text=True,
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
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode != 0, result.stdout
    assert "MVP gate did not produce the expected gate output" in result.stdout
