#!/usr/bin/env python3
"""route_failure 語彙の enum 正本と文書の同期を検査する。

契約 (v1):
- 文書中の `route_failure: <name>` / `route_failure=<name>` 形式の使用は、
  schemas/fde_route_failure.v1.schema.json の enum に載っていなければならない
  (unknown_usage)。
- enum の各 name は、route_failure の文脈で少なくとも 1 回出現しなければならない
  (dead_entry。文書から消した name を enum に残さない)。

dead_entry の evidence は次のどちらか。裸の散文中の語は数えない。
- `route_failure:` / `route_failure=` 付きの使用 (= usages)
- code span (`` `name` ``) としての定義・言及

`none` のような一般語は code span でも一般文脈と区別できないため、
usages (route_failure 付き) のみを evidence とする。これが無いと、route 文書から
当該 route 値が全部消えても無関係な散文の "none" で検査が緑のままになる。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_RELPATH = "schemas/fde_route_failure.v1.schema.json"

# 追跡されている文書・設定を網羅する。root だけを見ると decisions/ の ADR や
# .github/ の workflow に書かれた誤用を取りこぼす。
DOC_GLOBS = (
    "*.md",
    "*.yaml",
    "*.yml",
    "**/*.md",
    "**/*.yaml",
    "**/*.yml",
)

# 走査から外す作業ディレクトリ (生成物 / 依存 / VCS 内部)。
EXCLUDED_DIR_PARTS = frozenset({".git", ".venv", "node_modules", "__pycache__", ".local"})

# 一般語と衝突するため code span を evidence に使えない enum 値。
# これらは route_failure 付きの使用だけを evidence とする。
GENERIC_NAMES = frozenset({"none"})

# スカラー値全体を (quote 付きの形も含めて) まず捕捉する。enum との照合は
# 呼び出し側で行う。ここで文字クラスを enum の語彙 ([a-z0-9_]) に絞ると、
# `route_failure: noneXYZ` のような不正値が `none` として部分一致してしまう
# (Codex P2)。value 側は「空白 / パイプ / カンマ / quote 文字」以外を貪欲に取り、
# quote が開いていれば同じ quote で閉じることを要求する。
USAGE_PATTERN = re.compile(
    r"route_failure[:=][ \t]*"
    r"(?P<q>[`\"'])?"
    r"(?P<value>[^\s|,`\"']+)"
    r"(?(q)(?P=q))"
)

# `route_failure: none | fde_boot_unread` のような候補列挙行から
# 2 個目以降の名前も拾う。
ENUM_LIST_PATTERN = re.compile(r"route_failure[:=][^\n|]*((?:\|[^\n|]+)+)")

# markdown table の `route_failure` 列を検出するための行パーサ。
TABLE_SEPARATOR_CELL = re.compile(r"^:?-{1,}:?$")
TABLE_CELL_TOKEN = re.compile(r"[a-z0-9_]+")


def load_enum(root: Path = ROOT) -> list[str]:
    schema = json.loads((root / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    return list(schema["enum"])


def _doc_suffix_ok(path: Path) -> bool:
    return path.suffix in (".md", ".yaml", ".yml")


def _tracked_doc_paths(root: Path) -> list[Path] | None:
    """`git ls-files` ベースで tracked file だけを返す。

    git repo でない root (既存テストの tmp_path 等) では None を返し、
    呼び出し側で従来の glob 走査へ fallback させる。untracked / gitignore
    対象 (`.pytest_cache/...` の probe.md 等) を実験的な route_failure 値ごと
    拾って gate を落とすのを防ぐ (Codex P2)。
    """
    try:
        proc = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None

    paths: list[Path] = []
    # -z で NUL 区切りに読む。既定の core.quotepath では非 ASCII 名が quote されて
    # 返り、日本語名の tracked 文書が is_file() で落ちて走査から黙って消える。
    for line in proc.stdout.split("\0"):
        rel = line
        if not rel:
            continue
        rel_path = Path(rel)
        if EXCLUDED_DIR_PARTS & set(rel_path.parts[:-1]):
            continue
        candidate = root / rel_path
        if not _doc_suffix_ok(candidate) or not candidate.is_file():
            continue
        paths.append(candidate)
    return sorted(paths)


def _glob_doc_paths(root: Path) -> list[Path]:
    paths: set[Path] = set()
    for pattern in DOC_GLOBS:
        paths.update(root.glob(pattern))
    return sorted(
        p
        for p in paths
        if p.is_file()
        and not (EXCLUDED_DIR_PARTS & set(p.relative_to(root).parts))
    )


def iter_doc_paths(root: Path = ROOT) -> list[Path]:
    tracked = _tracked_doc_paths(root)
    if tracked is not None:
        return tracked
    return _glob_doc_paths(root)


def _split_table_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if len(stripped) < 2 or not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _is_table_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(TABLE_SEPARATOR_CELL.fullmatch(c) for c in cells)


def extract_table_usages(text: str) -> set[str]:
    """markdown table の `route_failure` 列のセルだけを usage として拾う。

    列位置を header 行から特定し、その列だけを読むことで、隣接セル
    (gate 名など) を route 名として誤検知する既知の false positive を避ける
    (Codex P2)。
    """
    names: set[str] = set()
    lines = text.splitlines()
    i = 0
    while i < len(lines) - 1:
        header_cells = _split_table_row(lines[i])
        if header_cells is None:
            i += 1
            continue
        sep_cells = _split_table_row(lines[i + 1])
        if (
            sep_cells is None
            or len(sep_cells) != len(header_cells)
            or not _is_table_separator_row(sep_cells)
        ):
            i += 1
            continue
        if "route_failure" not in header_cells:
            i += 2
            continue
        col_index = header_cells.index("route_failure")
        j = i + 2
        while j < len(lines):
            row_cells = _split_table_row(lines[j])
            if row_cells is None or len(row_cells) != len(header_cells):
                break
            cell = row_cells[col_index]
            for token in re.split(r"[\s/|,]+", cell):
                token = token.strip("`\"'")
                if TABLE_CELL_TOKEN.fullmatch(token):
                    names.add(token)
            j += 1
        i = j
    return names


def extract_usages(text: str) -> set[str]:
    names = {m.group("value") for m in USAGE_PATTERN.finditer(text)}
    for match in ENUM_LIST_PATTERN.finditer(text):
        for part in match.group(1).split("|"):
            token = part.strip().strip("`")
            if re.fullmatch(r"[a-z0-9_]+", token):
                names.add(token)
    names |= extract_table_usages(text)
    return names


def evaluate(root: Path = ROOT) -> dict[str, object]:
    enum_names = load_enum(root)
    errors: list[str] = []

    duplicates = sorted({n for n in enum_names if enum_names.count(n) > 1})
    for name in duplicates:
        errors.append(f"enum duplicate: {name}")

    usages: dict[str, list[str]] = {}
    corpus_parts: list[str] = []
    for path in iter_doc_paths(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        corpus_parts.append(text)
        for name in extract_usages(text):
            usages.setdefault(name, []).append(rel)

    enum_set = set(enum_names)
    for name in sorted(usages):
        if name not in enum_set:
            errors.append(
                f"unknown_usage: {name} (files: {', '.join(sorted(set(usages[name])))})"
            )

    corpus = "\n".join(corpus_parts)
    for name in enum_names:
        if name in usages:
            continue
        if name in GENERIC_NAMES:
            errors.append(
                f"dead_entry: {name} has no route_failure-prefixed usage in any doc "
                "(generic word: code span alone is not evidence)"
            )
            continue
        if not re.search(rf"`{re.escape(name)}`", corpus):
            errors.append(
                f"dead_entry: {name} is not defined or referenced as a code span in any doc"
            )

    return {
        "overall": "ok" if not errors else "error",
        "external_actions_performed": False,
        "errors": errors,
        "enum_count": len(enum_names),
        "usage_names": sorted(usages),
    }


def main() -> int:
    result = evaluate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
