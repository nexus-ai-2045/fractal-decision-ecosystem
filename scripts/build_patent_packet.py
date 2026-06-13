#!/usr/bin/env python3
"""Build local private patent packet artifacts."""

from __future__ import annotations

import hashlib
import textwrap
from datetime import datetime, timezone
from pathlib import Path

try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
except ModuleNotFoundError:  # pragma: no cover - exercised when reportlab is absent.
    LETTER = None
    Paragraph = object
    SimpleDocTemplate = None
    Spacer = object


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md"
OUT_DIR = ROOT / "patent-packet"
PDF = OUT_DIR / "FDE_PROVISIONAL_PATENT_DISCLOSURE_DRAFT.pdf"
MANIFEST = OUT_DIR / "MANIFEST.sha256"
README = OUT_DIR / "README.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def markdown_to_paragraphs(text: str) -> list[Paragraph | Spacer]:
    if SimpleDocTemplate is None:
        raise RuntimeError("reportlab is not available")

    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    heading = styles["Heading2"]
    title = styles["Title"]

    story: list[Paragraph | Spacer] = []
    in_code = False
    code_lines: list[str] = []

    def flush_code() -> None:
        nonlocal code_lines
        if not code_lines:
            return
        escaped = "<br/>".join(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for line in code_lines)
        story.append(Paragraph(f"<font name='Courier'>{escaped}</font>", body))
        story.append(Spacer(1, 8))
        code_lines = []

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line:
            story.append(Spacer(1, 6))
            continue
        if line.startswith("# "):
            story.append(Paragraph(line[2:], title))
            story.append(Spacer(1, 10))
            continue
        if line.startswith("## "):
            story.append(Paragraph(line[3:], heading))
            story.append(Spacer(1, 6))
            continue
        if line.startswith("### "):
            story.append(Paragraph(line[4:], styles["Heading3"]))
            story.append(Spacer(1, 4))
            continue
        wrapped = line
        if line.startswith("- "):
            wrapped = "• " + line[2:]
        story.append(Paragraph(wrapped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), body))
    flush_code()
    return story


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_simple_pdf(text: str, path: Path) -> None:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            lines.append("")
            continue
        if line.startswith("#"):
            line = line.lstrip("#").strip()
        if line.startswith("- "):
            line = "* " + line[2:]
        for wrapped in textwrap.wrap(line, width=88) or [""]:
            lines.append(wrapped)

    pages = [lines[index : index + 45] for index in range(0, len(lines), 45)] or [[]]
    objects: list[str] = []
    objects.append("<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + page_index * 2} 0 R" for page_index in range(len(pages)))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>")
    for page_index, page_lines in enumerate(pages):
        page_obj = 3 + page_index * 2
        content_obj = page_obj + 1
        stream_lines = ["BT", "/F1 10 Tf", "50 742 Td", "14 TL"]
        for line in page_lines:
            stream_lines.append(f"({pdf_escape(line)}) Tj")
            stream_lines.append("T*")
        stream_lines.append("ET")
        stream = "\n".join(stream_lines)
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
            f"/Contents {content_obj} 0 R >>"
        )
        objects.append(f"<< /Length {len(stream.encode('latin-1', errors='replace'))} >>\nstream\n{stream}\nendstream")

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n{obj}\nendobj\n".encode("latin-1", errors="replace"))
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    path.write_bytes(bytes(output))


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    text = SOURCE.read_text(encoding="utf-8")
    if SimpleDocTemplate is None:
        build_simple_pdf(text, PDF)
    else:
        doc = SimpleDocTemplate(str(PDF), pagesize=LETTER, title="FDE Provisional Patent Disclosure Draft")
        doc.build(markdown_to_paragraphs(text))

    generated_at = datetime.now(timezone.utc).isoformat()
    files = [SOURCE, PDF, ROOT / "DEFENSIVE_PATENT_REVIEW.md", ROOT / "INVENTION_RECORD.md"]
    manifest_lines = [
        "# FDE patent packet SHA256 manifest",
        f"generated_at_utc={generated_at}",
        "",
    ]
    for path in files:
        manifest_lines.append(f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}")
    MANIFEST.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    README.write_text(
        "\n".join(
            [
                "# FDE Patent Packet",
                "",
                "Private local packet. Do not publish.",
                "",
                "- `FDE_PROVISIONAL_PATENT_DISCLOSURE_DRAFT.pdf`: printable draft packet.",
                "- `MANIFEST.sha256`: hashes for packet integrity.",
                "",
                "No patent application has been filed by this build step.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"built={PDF.relative_to(ROOT).as_posix()}")
    print(f"manifest={MANIFEST.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
