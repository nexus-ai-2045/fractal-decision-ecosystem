import json
from pathlib import Path

from scripts.fde_route_failure_check import (
    ROOT,
    SCHEMA_RELPATH,
    evaluate,
    extract_usages,
    load_enum,
)


def test_route_failure_registry_matches_docs():
    result = evaluate()
    assert result["errors"] == []
    assert result["overall"] == "ok"
    assert result["external_actions_performed"] is False


def test_schema_enum_is_unique_and_nonempty():
    names = load_enum()
    assert names
    assert len(names) == len(set(names))
    assert "none" in names


def test_schema_defines_every_enum_name():
    schema = json.loads((ROOT / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    definitions = schema["x-definitions"]
    assert set(schema["enum"]) == set(definitions)
    for name, meta in definitions.items():
        assert meta.get("summary"), name
        assert meta.get("source"), name


def test_extract_usages_reads_prefixed_and_pipe_listed_names():
    text = (
        "- route_failure: none | fde_boot_unread\n"
        "`route_failure: fact_output_gate_missed` として扱う\n"
        "route_failure=send_path_unconfirmed\n"
    )
    assert extract_usages(text) == {
        "none",
        "fde_boot_unread",
        "fact_output_gate_missed",
        "send_path_unconfirmed",
    }


def test_unknown_usage_is_detected(tmp_path):
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    schema_src = json.loads((ROOT / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    (schema_dir / Path(SCHEMA_RELPATH).name).write_text(
        json.dumps(schema_src), encoding="utf-8"
    )
    doc = "\n".join(f"`{name}`" for name in schema_src["enum"])
    doc += "\nroute_failure: not_a_registered_name\n"
    (tmp_path / "doc.md").write_text(doc, encoding="utf-8")

    result = evaluate(root=tmp_path)
    assert result["overall"] == "error"
    assert any("unknown_usage: not_a_registered_name" in e for e in result["errors"])


def test_dead_enum_entry_is_detected(tmp_path):
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    schema_src = json.loads((ROOT / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    (schema_dir / Path(SCHEMA_RELPATH).name).write_text(
        json.dumps(schema_src), encoding="utf-8"
    )
    names = schema_src["enum"]
    doc = "\n".join(f"`{name}`" for name in names if name != "new_surface_blocked")
    (tmp_path / "doc.md").write_text(doc, encoding="utf-8")

    result = evaluate(root=tmp_path)
    assert result["overall"] == "error"
    assert any("dead_entry: new_surface_blocked" in e for e in result["errors"])
