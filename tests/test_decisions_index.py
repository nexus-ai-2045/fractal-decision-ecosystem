import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "decisions"
SECTION_FOR_STATUS = {"accepted": "## 採用済みADR", "proposed": "## 提案中ADR"}
STATUS_LINE = re.compile(r"^Status: (accepted|proposed)$", re.MULTILINE)
DATE_LINE = re.compile(r"^Date: ([0-9]{4}-[0-9]{2}-[0-9]{2})$", re.MULTILINE)
LOOSE_HEADER_LINE = re.compile(r"^[ \t]*(?:-[ \t]*)?(?:Status|Date):[^\n]*$", re.MULTILINE)
ROW_LINK = re.compile(r"^\|\s*\[(ADR-\d{4}-[^\]]+\.md)\]", re.MULTILINE)


def adr_files() -> list[Path]:
    return sorted(DECISIONS.glob("ADR-*.md"))


def header_block(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    first_section = text.find("\n## ")
    return text if first_section == -1 else text[:first_section]


def adr_statuses() -> dict[str, str]:
    statuses = {}
    for path in adr_files():
        match = STATUS_LINE.search(header_block(path))
        statuses[path.name] = match.group(1) if match else ""
    return statuses


def is_real_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


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
        header_lines = LOOSE_HEADER_LINE.findall(header_block(path))
        statuses = [line for line in header_lines if STATUS_LINE.fullmatch(line)]
        dates = [match.group(1) for line in header_lines if (match := DATE_LINE.fullmatch(line))]
        if len(header_lines) != 2 or len(statuses) != 1 or len(dates) != 1 or not is_real_date(dates[0]):
            malformed[path.name] = header_lines
    assert malformed == {}


def test_decisions_index_lists_each_adr_once_under_its_status() -> None:
    sections = index_sections((DECISIONS / "README.md").read_text(encoding="utf-8"))
    listed = [name for names in sections.values() for name in names]
    assert sorted(listed) == sorted(set(listed))
    assert sorted(set(listed) - set(adr_statuses())) == []
    misplaced = {
        name: SECTION_FOR_STATUS.get(status)
        for name, status in adr_statuses().items()
        if name not in sections.get(SECTION_FOR_STATUS.get(status, ""), [])
    }
    assert misplaced == {}
