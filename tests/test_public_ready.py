import hashlib

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
