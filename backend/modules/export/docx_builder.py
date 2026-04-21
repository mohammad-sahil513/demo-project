"""Build a fresh DOCX from StyleMap + assembled sections (inbuilt templates)."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from modules.assembly.models import AssembledDocument
from modules.export.markdown_tables import parse_gfm_table, split_markdown_blocks
from modules.template.models import StyleMap


def _apply_paragraph_style(paragraph, ps) -> None:
    for run in paragraph.runs:
        run.font.name = ps.font_name
        run.font.size = Pt(ps.font_size_pt)
        run.font.bold = ps.bold
        run.font.italic = ps.italic
    if ps.alignment == "center":
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    elif ps.alignment == "right":
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
    else:
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT


def _heading_style_name(level: int) -> str:
    if level <= 1:
        return "Heading 1"
    if level == 2:
        return "Heading 2"
    return "Heading 3"


def _add_body_line(doc: Document, line: str, style_map: StyleMap) -> None:
    stripped = line.strip()
    if not stripped:
        return
    bullet_prefixes = ("- ", "* ", "• ")
    numbered = re.match(r"^(\d+)[.)]\s+", stripped)
    p = None
    for bp in bullet_prefixes:
        if stripped.startswith(bp):
            text = stripped[len(bp) :].strip()
            try:
                p = doc.add_paragraph(text, style="List Bullet")
            except (KeyError, ValueError):
                p = doc.add_paragraph(f"• {text}", style="Normal")
            break
    if p is None and numbered:
        text = stripped[numbered.end() :].strip()
        try:
            p = doc.add_paragraph(text, style="List Number")
        except (KeyError, ValueError):
            p = doc.add_paragraph(stripped, style="Normal")
    if p is None:
        p = doc.add_paragraph(stripped)
        p.style = doc.styles["Normal"]
    if p.style.name == "Normal" or "List" not in (p.style.name or ""):
        _apply_paragraph_style(p, style_map.body)


class DocxBuilder:
    def __init__(self, storage_root: Path) -> None:
        self._storage_root = storage_root

    def build(self, assembled: AssembledDocument, style_map: StyleMap, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = Document()
        title_para = doc.add_paragraph(assembled.title)
        title_para.style = doc.styles["Title"]

        for section in assembled.sections:
            heading = doc.add_paragraph(section.title)
            try:
                heading.style = doc.styles[_heading_style_name(section.level)]
            except KeyError:
                heading.style = doc.styles["Heading 1"]
            _apply_paragraph_style(heading, style_map.heading_1 if section.level <= 1 else style_map.heading_2)

            if section.output_type == "diagram" and section.diagram_path:
                img = self._storage_root / Path(section.diagram_path)
                if img.exists():
                    doc.add_picture(str(img), width=Inches(5.5))
                elif section.content.strip():
                    self._add_body_blocks(doc, section.content, style_map)
            else:
                self._add_body_blocks(doc, section.content, style_map)

        doc.save(str(output_path))

    def _add_body_blocks(self, doc: Document, content: str, style_map: StyleMap) -> None:
        for kind, payload in split_markdown_blocks(content):
            if kind == "text":
                for para_text in payload.split("\n\n"):
                    chunk = para_text.strip()
                    if not chunk:
                        continue
                    lines = chunk.split("\n")
                    if len(lines) == 1:
                        _add_body_line(doc, lines[0], style_map)
                    else:
                        for line in lines:
                            _add_body_line(doc, line, style_map)
            else:
                rows = parse_gfm_table(payload)
                if not rows:
                    continue
                cols = max(len(r) for r in rows)
                table = doc.add_table(rows=len(rows), cols=cols)
                table.style = "Table Grid"
                for r_idx, row in enumerate(rows):
                    for c_idx in range(cols):
                        cell = table.cell(r_idx, c_idx)
                        val = row[c_idx] if c_idx < len(row) else ""
                        cell.text = val
                        for run in cell.paragraphs[0].runs:
                            run.font.size = Pt(style_map.body.font_size_pt)
                            if r_idx == 0:
                                run.font.bold = True
