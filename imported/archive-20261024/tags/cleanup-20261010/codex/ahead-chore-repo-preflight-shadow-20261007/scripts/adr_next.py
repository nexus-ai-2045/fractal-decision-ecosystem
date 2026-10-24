#!/usr/bin/env python3
"""Print the next repo-local FDE ADR filename."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "decisions"
ADR_RE = re.compile(r"^ADR-(\d{4})-.+\.md$")


def existing_adr_numbers(decisions_dir: Path = DECISIONS) -> list[int]:
    if not decisions_dir.exists():
        return []
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


def main() -> int:
    print(next_adr_filename())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

