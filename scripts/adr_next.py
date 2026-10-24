#!/usr/bin/env python3
"""Print the next repo-local FDE ADR filename."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "decisions"
ADR_RE = re.compile(r"^ADR-(\d{4})-.+\.md$")


def existing_adr_numbers(decisions_dir: Path = DECISIONS) -> list[int]:
    # A missing or mistyped directory must not silently restart numbering at
    # 0001 (that would collide with existing ADRs); an existing empty
    # directory legitimately starts at 1.
    if not decisions_dir.exists():
        raise FileNotFoundError(f"decisions directory not found: {decisions_dir}")
    if not decisions_dir.is_dir():
        raise NotADirectoryError(f"decisions path is not a directory: {decisions_dir}")
    numbers: list[int] = []
    for path in decisions_dir.glob("ADR-*.md"):
        match = ADR_RE.match(path.name)
        if match:
            numbers.append(int(match.group(1)))
    return sorted(numbers)


def next_adr_number(decisions_dir: Path = DECISIONS) -> int:
    numbers = existing_adr_numbers(decisions_dir)
    return (numbers[-1] + 1) if numbers else 1


def next_adr_filename(slug: str = "short-title", decisions_dir: Path = DECISIONS) -> str:
    return f"ADR-{next_adr_number(decisions_dir):04d}-{slug}.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--decisions-dir",
        type=Path,
        default=DECISIONS,
        help="ADR directory to scan (default: repo-local decisions/)",
    )
    args = parser.parse_args(argv)
    try:
        filename = next_adr_filename(decisions_dir=args.decisions_dir)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"adr_next: {exc}", file=sys.stderr)
        return 1
    print(filename)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

