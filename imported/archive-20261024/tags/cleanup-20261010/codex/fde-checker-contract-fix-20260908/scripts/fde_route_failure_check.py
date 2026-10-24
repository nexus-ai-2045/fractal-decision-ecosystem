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

USAGE_PATTERN = re.compile(r"route_failure[:=]\s*`?([a-z0-9_]+)`?")

# `route_failure: none | fde_boot_unread` のような候補列挙行から
# 2 個目以降の名前も拾う。
ENUM_LIST_PATTERN = re.compile(r"route_failure[:=][^\n|]*((?:\|[^\n|]+)+)")


def load_enum(root: Path = ROOT) -> list[str]:
    schema = json.loads((root / SCHEMA_RELPATH).read_text(encoding="utf-8"))
    return list(schema["enum"])


def iter_doc_paths(root: Path = ROOT) -> list[Path]:
    paths: set[Path] = set()
    for pattern in DOC_GLOBS:
        paths.update(root.glob(pattern))
    return sorted(
        p
        for p in paths
        if p.is_file()
        and not (EXCLUDED_DIR_PARTS & set(p.relative_to(root).parts))
    )


def extract_usages(text: str) -> set[str]:
    names = set(USAGE_PATTERN.findall(text))
    for match in ENUM_LIST_PATTERN.finditer(text):
        for part in match.group(1).split("|"):
            token = part.strip().strip("`")
            if re.fullmatch(r"[a-z0-9_]+", token):
                names.add(token)
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
