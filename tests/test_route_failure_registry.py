import json
import subprocess
from pathlib import Path

from scripts.fde_route_failure_check import (
    ROOT,
    SCHEMA_RELPATH,
    evaluate,
    extract_usages,
    iter_doc_paths,
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


def test_generic_enum_name_requires_route_failure_prefixed_usage(tmp_path):
    """`none` のような一般語は code span だけでは evidence にしない (Codex P2)。"""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    schema_src = json.loads((ROOT / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    (schema_dir / Path(SCHEMA_RELPATH).name).write_text(
        json.dumps(schema_src), encoding="utf-8"
    )
    lines = []
    for name in schema_src["enum"]:
        # `none` だけは route_failure 付きの使用を与えず、無関係な散文に置く。
        if name == "none":
            lines.append("この項目は none です。")
        else:
            lines.append(f"`{name}`")
    (tmp_path / "doc.md").write_text("\n".join(lines), encoding="utf-8")

    result = evaluate(root=tmp_path)
    assert result["overall"] == "error"
    assert any("dead_entry: none" in e for e in result["errors"])


def test_nested_documentation_directories_are_scanned(tmp_path):
    """decisions/ や .github/ の誤用も unknown_usage で捕まる (Codex P2)。"""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    schema_src = json.loads((ROOT / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    (schema_dir / Path(SCHEMA_RELPATH).name).write_text(
        json.dumps(schema_src), encoding="utf-8"
    )
    (tmp_path / "doc.md").write_text(
        "\n".join(f"`{n}`" for n in schema_src["enum"] if n != "none")
        + "\nroute_failure: none\n",
        encoding="utf-8",
    )
    adr_dir = tmp_path / "decisions"
    adr_dir.mkdir()
    (adr_dir / "ADR-0001.md").write_text(
        "route_failure: misspelled_name\n", encoding="utf-8"
    )

    result = evaluate(root=tmp_path)
    assert result["overall"] == "error"
    assert any("unknown_usage: misspelled_name" in e for e in result["errors"])


def test_excluded_working_directories_are_not_scanned(tmp_path):
    """.venv / node_modules 等の生成物は走査しない。"""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    schema_src = json.loads((ROOT / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    (schema_dir / Path(SCHEMA_RELPATH).name).write_text(
        json.dumps(schema_src), encoding="utf-8"
    )
    (tmp_path / "doc.md").write_text(
        "\n".join(f"`{n}`" for n in schema_src["enum"] if n != "none")
        + "\nroute_failure: none\n",
        encoding="utf-8",
    )
    vendored = tmp_path / "node_modules" / "pkg"
    vendored.mkdir(parents=True)
    (vendored / "README.md").write_text(
        "route_failure: vendored_typo\n", encoding="utf-8"
    )

    result = evaluate(root=tmp_path)
    assert result["overall"] == "ok"


def test_iter_doc_paths_restricts_to_tracked_files_in_git_repo(tmp_path):
    """Codex P2: untracked / gitignore 対象の probe file を走査しない。"""
    repo = tmp_path
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / "doc.md").write_text("route_failure: none\n", encoding="utf-8")
    subprocess.run(["git", "add", "doc.md"], cwd=repo, check=True)

    untracked_dir = repo / ".pytest_cache" / "v" / "cache"
    untracked_dir.mkdir(parents=True)
    (untracked_dir / "probe.md").write_text(
        "route_failure: experimental_not_registered\n", encoding="utf-8"
    )

    paths = iter_doc_paths(repo)
    rels = {p.relative_to(repo).as_posix() for p in paths}
    assert rels == {"doc.md"}
    assert not any("pytest_cache" in rel for rel in rels)


def test_iter_doc_paths_falls_back_to_glob_when_root_is_not_a_git_repo(tmp_path):
    """既存テストは git repo でない tmp_path を root に渡すので、fallback を固定する。"""
    (tmp_path / "doc.md").write_text("route_failure: none\n", encoding="utf-8")

    paths = iter_doc_paths(tmp_path)
    rels = {p.relative_to(tmp_path).as_posix() for p in paths}
    assert rels == {"doc.md"}


def test_uppercase_route_failure_value_is_reported_as_unknown_usage(tmp_path):
    """Codex P2: `route_failure: NOT_REGISTERED` を握りつぶさず unknown_usage にする。"""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    schema_src = json.loads((ROOT / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    (schema_dir / Path(SCHEMA_RELPATH).name).write_text(
        json.dumps(schema_src), encoding="utf-8"
    )
    doc = "\n".join(f"`{name}`" for name in schema_src["enum"])
    doc += "\nroute_failure: NOT_REGISTERED\n"
    (tmp_path / "doc.md").write_text(doc, encoding="utf-8")

    result = evaluate(root=tmp_path)
    assert result["overall"] == "error"
    assert any("unknown_usage: NOT_REGISTERED" in e for e in result["errors"])


def test_quoted_route_failure_value_is_reported_as_unknown_usage(tmp_path):
    """Codex P2: `route_failure: "not_registered"` を握りつぶさず unknown_usage にする。"""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    schema_src = json.loads((ROOT / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    (schema_dir / Path(SCHEMA_RELPATH).name).write_text(
        json.dumps(schema_src), encoding="utf-8"
    )
    doc = "\n".join(f"`{name}`" for name in schema_src["enum"])
    doc += '\nroute_failure: "not_registered"\n'
    (tmp_path / "doc.md").write_text(doc, encoding="utf-8")

    result = evaluate(root=tmp_path)
    assert result["overall"] == "error"
    assert any("unknown_usage: not_registered" in e for e in result["errors"])


def test_route_failure_value_with_trailing_garbage_is_not_partially_accepted(tmp_path):
    """Codex P2: `route_failure: noneXYZ` を部分一致で `none` として受理しない。"""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    schema_src = json.loads((ROOT / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    (schema_dir / Path(SCHEMA_RELPATH).name).write_text(
        json.dumps(schema_src), encoding="utf-8"
    )
    doc = "\n".join(f"`{name}`" for name in schema_src["enum"] if name != "none")
    doc += "\nこの項目は none です。\n"
    doc += "\nroute_failure: noneXYZ\n"
    (tmp_path / "doc.md").write_text(doc, encoding="utf-8")

    result = evaluate(root=tmp_path)
    assert result["overall"] == "error"
    assert any("unknown_usage: noneXYZ" in e for e in result["errors"])
    # 部分一致の "none" を正しい usage として誤採用していないこと。
    assert any("dead_entry: none" in e for e in result["errors"])


def test_markdown_table_route_failure_column_is_checked(tmp_path):
    """Codex P2: markdown table の route_failure 列 typo も unknown_usage にする。"""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    schema_src = json.loads((ROOT / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    (schema_dir / Path(SCHEMA_RELPATH).name).write_text(
        json.dumps(schema_src), encoding="utf-8"
    )
    doc = "\n".join(f"`{name}`" for name in schema_src["enum"])
    doc += "\n\n"
    doc += "| rank | gate | route_failure |\n"
    doc += "|---:|---|---|\n"
    doc += "| 0 | user correction | `human_judgment_ignoredd` |\n"
    (tmp_path / "doc.md").write_text(doc, encoding="utf-8")

    result = evaluate(root=tmp_path)
    assert result["overall"] == "error"
    assert any(
        "unknown_usage: human_judgment_ignoredd" in e for e in result["errors"]
    )


def test_markdown_table_adjacent_columns_are_not_misread_as_route_failure(tmp_path):
    """既知の false positive 回帰: 隣接列の値を route 名として誤検知しない。"""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    schema_src = json.loads((ROOT / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    (schema_dir / Path(SCHEMA_RELPATH).name).write_text(
        json.dumps(schema_src), encoding="utf-8"
    )
    doc = "\n".join(f"`{name}`" for name in schema_src["enum"])
    doc += "\n\n"
    doc += "| rank | gate | route_failure |\n"
    doc += "|---:|---|---|\n"
    doc += "| 0 | totally_unregistered_gate_name | `none` |\n"
    (tmp_path / "doc.md").write_text(doc, encoding="utf-8")

    result = evaluate(root=tmp_path)
    assert result["overall"] == "ok"
    assert not any(
        "totally_unregistered_gate_name" in e for e in result["errors"]
    )


def test_route_registry_is_an_aggregate_subgate_and_tracked():
    """mvp_gate が registry を実行し、3 file を tracked 必須に含める (Codex P2)。"""
    from scripts import mvp_gate_check

    gate = mvp_gate_check.evaluate(run_pytest=False)
    names = [check["name"] for check in gate["checks"]]
    assert "fde_route_failure_check" in names

    required = set(mvp_gate_check.REQUIRED_TRACKED_FILES)
    assert SCHEMA_RELPATH in required
    assert "scripts/fde_route_failure_check.py" in required
    assert "tests/test_route_failure_registry.py" in required


def test_iter_doc_paths_keeps_tracked_non_ascii_filenames(tmp_path):
    """`git ls-files` 既定の quotepath は非 ASCII 名を quote して返す。
    -z で読まないと日本語名の tracked 文書が走査から黙って落ちる (fail-open)。"""
    repo = tmp_path
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / "日本語.md").write_text("route_failure: none\n", encoding="utf-8")
    subprocess.run(["git", "add", "日本語.md"], cwd=repo, check=True)

    rels = {p.relative_to(repo).as_posix() for p in iter_doc_paths(repo)}
    assert rels == {"日本語.md"}
