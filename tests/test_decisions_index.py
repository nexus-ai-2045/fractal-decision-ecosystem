import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "decisions"
SECTION_FOR_STATUS = {"accepted": "## 採用済みADR", "proposed": "## 提案中ADR"}
STATUS_LINE = re.compile(r"^Status: (accepted|proposed)$", re.MULTILINE)
DATE_LINE = re.compile(r"^Date: \d{4}-\d{2}-\d{2}$", re.MULTILINE)
LOOSE_HEADER_LINE = re.compile(r"^[ \t]*(?:-[ \t]*)?(?:Status|Date):[^\n]*$", re.MULTILINE)
ROW_LINK = re.compile(r"^\|\s*\[(ADR-\d{4}-[^\]]+\.md)\]", re.MULTILINE)


def adr_files() -> list[Path]:
    return sorted(DECISIONS.glob("ADR-*.md"))


def adr_statuses() -> dict[str, str]:
    statuses = {}
    for path in adr_files():
        match = STATUS_LINE.search(path.read_text(encoding="utf-8"))
        statuses[path.name] = match.group(1) if match else ""
    return statuses


def index_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = ""
    for line in text.splitlines():
        if line.startswith("## "):
            current = line.strip()
            sections.setdefault(current, [])
            continue
        match = ROW_LINK.match(line)
        if match and current:
            sections[current].append(match.group(1))
    return sections


def test_every_adr_writes_status_and_date_in_the_single_canonical_form() -> None:
    malformed = {}
    for path in adr_files():
        header_lines = LOOSE_HEADER_LINE.findall(path.read_text(encoding="utf-8"))
        statuses = [line for line in header_lines if STATUS_LINE.fullmatch(line)]
        dates = [line for line in header_lines if DATE_LINE.fullmatch(line)]
        if len(header_lines) != 2 or len(statuses) != 1 or len(dates) != 1:
            malformed[path.name] = header_lines
    assert malformed == {}


def test_decisions_index_lists_each_adr_once_under_its_status() -> None:
    sections = index_sections((DECISIONS / "README.md").read_text(encoding="utf-8"))
    listed = [name for names in sections.values() for name in names]
    assert sorted(listed) == sorted(set(listed))
    misplaced = {
        name: SECTION_FOR_STATUS.get(status)
        for name, status in adr_statuses().items()
        if name not in sections.get(SECTION_FOR_STATUS.get(status, ""), [])
    }
    assert misplaced == {}
