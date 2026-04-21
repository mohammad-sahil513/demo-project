"""Fill a custom DOCX template with assembled section content."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from docx.shared import Inches, Pt

from core.ids import utc_now_iso
from modules.assembly.models import AssembledDocument
from modules.export.markdown_tables import parse_gfm_table, split_markdown_blocks
from modules.template.models import StyleMap


def _heading_level(paragraph: Paragraph) -> int | None:
    style_name = paragraph.style.name if paragraph.style else ""
    if not style_name.startswith("Heading"):
        return None
    parts = style_name.split()
    try:
        return int(parts[-1])
    except (ValueError, IndexError):
        return 1


def _insert_paragraph_after(paragraph: Paragraph, text: str = "", style: object | None = None) -> Paragraph:
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)  # type: ignore[attr-defined]
    new_para = Paragraph(new_p, paragraph._parent)  # type: ignore[arg-type]
    if text:
        new_para.add_run(text)
    if style is not None:
        new_para.style = style
    return new_para


def _clear_following_until_heading(doc: Document, heading: Paragraph) -> None:
    el = heading._p
    nxt = el.getnext()
    while nxt is not None:
        if nxt.tag.endswith("p"):
            para = Paragraph(nxt, doc)
            if _heading_level(para) is not None:
                break
        nxt_next = nxt.getnext()
        parent = nxt.getparent()
        if parent is not None:
            parent.remove(nxt)
        nxt = nxt_next


def _move_table_after(paragraph: Paragraph, table) -> None:
    tbl_el = table._tbl
    parent = tbl_el.getparent()
    if parent is not None:
        parent.remove(tbl_el)
    paragraph._p.addnext(tbl_el)  # type: ignore[attr-defined]


def _add_line_after_doc(
    doc: Document,
    after: Paragraph,
    line: str,
    normal,
    sm: StyleMap,
) -> Paragraph:
    stripped = line.strip()
    if not stripped:
        return after
    bullet_prefixes = ("- ", "* ", "• ")
    numbered = re.match(r"^(\d+)[.)]\s+", stripped)
    ref = _insert_paragraph_after(after, "", normal)
    for bp in bullet_prefixes:
        if stripped.startswith(bp):
            text = stripped[len(bp) :].strip()
            try:
                ref.style = doc.styles["List Bullet"]
                if text:
                    ref.add_run(text)
            except (KeyError, ValueError):
                ref.add_run(f"• {text}")
            for run in ref.runs:
                run.font.size = Pt(sm.body.font_size_pt)
            return ref
    if numbered:
        text = stripped[numbered.end() :].strip()
        try:
            ref.style = doc.styles["List Number"]
            if text:
                ref.add_run(text)
        except (KeyError, ValueError):
            ref.add_run(stripped)
        for run in ref.runs:
            run.font.size = Pt(sm.body.font_size_pt)
        return ref
    out = _insert_paragraph_after(after, stripped, normal)
    for run in out.runs:
        run.font.size = Pt(sm.body.font_size_pt)
    return out


class DocxFiller:
    def __init__(self, storage_root: Path) -> None:
        self._storage_root = storage_root

    def fill(
        self,
        template_path: Path,
        assembled: AssembledDocument,
        output_path: Path,
        *,
        style_map: StyleMap | None = None,
    ) -> list[dict[str, object]]:
        """Return workflow-style warning dicts (e.g. missing template headings)."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = Document(str(template_path))
        used_heading_elements: set[int] = set()
        warnings: list[dict[str, object]] = []
        sm = style_map or StyleMap()
        ts = utc_now_iso()
        normal = doc.styles["Normal"]

        for section in assembled.sections:
            heading: Paragraph | None = None
            for p in doc.paragraphs:
                if id(p._p) in used_heading_elements:
                    continue
                if p.text.strip() == section.title.strip():
                    heading = p
                    used_heading_elements.add(id(p._p))
                    break
            if heading is None:
                warnings.append(
                    {
                        "phase": "RENDER_EXPORT",
                        "code": "template_heading_not_found",
                        "section_id": section.section_id,
                        "title": section.title,
                        "message": (
                            f"No paragraph matching heading {section.title!r} in template; "
                            "section content was not inserted."
                        ),
                        "at": ts,
                    },
                )
                continue

            _clear_following_until_heading(doc, heading)
            ref: Paragraph = heading
            if section.output_type == "diagram" and section.diagram_path:
                img = self._storage_root / Path(section.diagram_path)
                if img.exists():
                    ref = _insert_paragraph_after(ref, "")
                    run = ref.add_run()
                    run.add_picture(str(img), width=Inches(5.5))
                elif section.content.strip():
                    ref = self._append_blocks(doc, ref, section.content, sm, normal)
            else:
                ref = self._append_blocks(doc, ref, section.content, sm, normal)

        doc.save(str(output_path))
        return warnings

    def _append_blocks(
        self,
        doc: Document,
        after: Paragraph,
        content: str,
        sm: StyleMap,
        normal,
    ) -> Paragraph:
        ref = after
        for kind, payload in split_markdown_blocks(content):
            if kind == "text":
                for chunk in payload.split("\n\n"):
                    block = chunk.strip()
                    if not block:
                        continue
                    lines = block.split("\n")
                    if len(lines) == 1:
                        ref = _add_line_after_doc(doc, ref, lines[0], normal, sm)
                    else:
                        for line in lines:
                            ref = _add_line_after_doc(doc, ref, line, normal, sm)
            else:
                rows = parse_gfm_table(payload)
                if not rows:
                    continue
                cols = max(len(r) for r in rows)
                ref = _insert_paragraph_after(ref, "")
                table = doc.add_table(rows=len(rows), cols=cols)
                table.style = "Table Grid"
                _move_table_after(ref, table)
                for r_idx, row in enumerate(rows):
                    for c_idx in range(cols):
                        cell = table.cell(r_idx, c_idx)
                        val = row[c_idx] if c_idx < len(row) else ""
                        cell.text = val
                        if r_idx == 0:
                            for run in cell.paragraphs[0].runs:
                                run.font.bold = True
                tail = OxmlElement("w:p")
                table._tbl.addnext(tail)
                ref = Paragraph(tail, doc)
        return ref
