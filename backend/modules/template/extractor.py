"""Template skeleton and style extraction for custom templates.

For ``.docx`` templates we walk ``word/document.xml`` and build:

- a list of :class:`ExtractedHeading` (heading text, level, style name,
  numbering prefix);
- a mapping ``order -> table_header_row`` for the first table that appears
  under each heading;
- a flag for whether a Table of Contents was detected (so we can skip
  re-emitting TOC entries as headings).

For ``.xlsx`` templates each worksheet becomes a level-1 "heading" and we
detect the header row per worksheet (either strict row-1 or a heuristic
scan of the first 5 rows, controlled by ``HEADER_DETECTION_MODE``).

The heading detector accepts three patterns:
1. Paragraphs styled ``Heading N``.
2. Numbered body paragraphs like ``1.2 Scope``.
3. Short ALL-CAPS lines (<= 12 words).

It explicitly *rejects* TOC paragraphs and ``... 3`` dot-leader lines so the
plan only contains actual body headings.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

from core.config import settings
from core.exceptions import TemplateException
from modules.template.models import DocumentSkeleton, ExtractedHeading, StyleMap
from modules.template.xlsx_workbook import open_xlsx_workbook

_WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
_SHEET_NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
_W_URI = _WORD_NS["w"]
_W_P = f"{{{_W_URI}}}p"
_W_TBL = f"{{{_W_URI}}}tbl"


class TemplateExtractor:
    # TOC title lines
    _TOC_TITLE_RE = re.compile(r"^(table of contents|contents)$", re.IGNORECASE)

    # TOC entry examples:
    # 1 Introduction ............ 3
    # 2.1 Scope ............ 5
    # Appendix A ............ 10
    _TOC_LINE_RE = re.compile(r"^(?:\d+(?:\.\d+)*)?\s*.+?\.{2,}\s*\d+\s*$")

    # Numbered body headings:
    # 1 Introduction
    # 2.1 Scope
    _NUMBERED_HEADING_RE = re.compile(r"^(?P<num>\d+(?:\.\d+)*)\s+\S+")
    _HEADING_STYLE_LEVEL_RE = re.compile(r"heading\s*(\d+)$", re.IGNORECASE)

    def extract(self, template_path: Path) -> tuple[DocumentSkeleton, StyleMap, dict[str, object]]:
        suffix = template_path.suffix.lower()
        if suffix == ".docx":
            return self.extract_docx(template_path)
        if suffix == ".xlsx":
            return self.extract_xlsx(template_path)
        raise TemplateException(f"Unsupported template format: {template_path.suffix}")

    def extract_docx(self, template_path: Path) -> tuple[DocumentSkeleton, StyleMap, dict[str, object]]:
        with ZipFile(template_path, "r") as archive:
            try:
                document_xml = archive.read("word/document.xml")
            except KeyError as exc:
                raise TemplateException("Invalid DOCX template: missing word/document.xml") from exc

        root = ET.fromstring(document_xml)
        body = root.find("w:body", _WORD_NS)
        if body is None:
            raise TemplateException("Invalid DOCX template: missing w:body in document.xml")

        table_headers_by_order: dict[int, list[str]] = {}
        heading_items: list[ExtractedHeading] = []
        walk_state: dict[str, object] = {
            "in_toc": False,
            "saw_toc": False,
            "order": 0,
            "previous_key": None,
            "current_heading_order": None,
            "table_candidates": {},
        }

        for child in body:
            if child.tag == _W_P:
                self._docx_walk_paragraph(child, heading_items, walk_state)
            elif child.tag == _W_TBL:
                ch_ord = walk_state.get("current_heading_order")
                if ch_ord is not None:
                    headers = self._extract_docx_table_first_row_headers(child)
                    if headers:
                        cands = walk_state["table_candidates"]
                        assert isinstance(cands, dict)
                        lst = cands.setdefault(int(ch_ord), [])
                        assert isinstance(lst, list)
                        lst.append(headers)

        if not heading_items:
            raise TemplateException("No headings detected in DOCX template for compilation.")

        raw_cands = walk_state.get("table_candidates") or {}
        if isinstance(raw_cands, dict):
            for ord_key, lists in raw_cands.items():
                if not isinstance(lists, list):
                    continue
                nonempty = [x for x in lists if isinstance(x, list) and x]
                if nonempty:
                    best = max(nonempty, key=len)
                    table_headers_by_order[int(ord_key)] = best

        headings = [item.text for item in heading_items]
        table_headers_by_heading: dict[str, list[str]] = {}
        for item in heading_items:
            hdrs = table_headers_by_order.get(item.order)
            if hdrs:
                table_headers_by_heading[item.text] = list(hdrs)

        saw_toc = bool(walk_state["saw_toc"])
        skeleton = DocumentSkeleton(
            title=template_path.stem,
            headings=headings,
            heading_items=heading_items,
            table_headers_by_heading=table_headers_by_heading,
            table_headers_by_heading_order=dict(table_headers_by_order),
            raw_structure={
                "source": "docx",
                "heading_count": len(heading_items),
                "toc_detected": saw_toc,
                "levels": [item.level for item in heading_items],
            },
        )
        return skeleton, StyleMap(), {}

    def _docx_walk_paragraph(
        self,
        paragraph: ET.Element,
        heading_items: list[ExtractedHeading],
        walk_state: dict[str, object],
    ) -> None:
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", _WORD_NS)).strip()
        if not text:
            return

        style_name_node = paragraph.find(".//w:pStyle", _WORD_NS)
        style_value = ""
        if style_name_node is not None:
            style_value = (
                style_name_node.attrib.get(f"{{{_W_URI}}}val") or ""
            ).strip().lower()

        normalized_text = self._normalize_text(text)
        in_toc = bool(walk_state["in_toc"])
        order = int(walk_state["order"])
        previous_key = walk_state["previous_key"]

        if self._is_toc_title(normalized_text):
            walk_state["in_toc"] = True
            walk_state["saw_toc"] = True
            return

        if self._is_toc_style(style_value):
            walk_state["in_toc"] = True
            walk_state["saw_toc"] = True
            return

        if in_toc:
            if self._looks_like_toc_line(normalized_text):
                return

            if not self._is_real_heading(normalized_text, style_value):
                return

            walk_state["in_toc"] = False
            in_toc = False

        if not self._is_real_heading(normalized_text, style_value):
            return

        level = self._derive_heading_level(normalized_text, style_value)
        numbering = self._extract_numbering_prefix(normalized_text)

        key = (normalized_text.lower(), level)
        if previous_key == key:
            return
        walk_state["previous_key"] = key

        order += 1
        walk_state["order"] = order
        heading_items.append(
            ExtractedHeading(
                text=normalized_text,
                level=level,
                order=order,
                style_name=style_value or None,
                numbering=numbering,
            ),
        )
        walk_state["current_heading_order"] = order

    def _extract_docx_table_first_row_headers(self, tbl: ET.Element) -> list[str]:
        rows = tbl.findall("w:tr", _WORD_NS)
        if not rows:
            return []
        first = rows[0]
        headers: list[str] = []
        for tc in first.findall("w:tc", _WORD_NS):
            tc_pr = tc.find("w:tcPr", _WORD_NS)
            if tc_pr is not None:
                vm = tc_pr.find("w:vMerge", _WORD_NS)
                if vm is not None:
                    vval = (vm.attrib.get(f"{{{_W_URI}}}val") or "").lower()
                    if vval != "restart":
                        continue

            grid_span = 1
            if tc_pr is not None:
                gs = tc_pr.find("w:gridSpan", _WORD_NS)
                if gs is not None:
                    try:
                        grid_span = max(1, int(gs.attrib.get(f"{{{_W_URI}}}val", "1")))
                    except ValueError:
                        grid_span = 1

            parts: list[str] = []
            for node in tc.findall(".//w:t", _WORD_NS):
                if node.text:
                    parts.append(node.text)
            cell = self._normalize_text("".join(parts))
            if not cell:
                continue
            for _ in range(grid_span):
                headers.append(cell)
        return [h for h in headers if h]

    def extract_xlsx(self, template_path: Path) -> tuple[DocumentSkeleton, StyleMap, dict[str, object]]:
        with ZipFile(template_path, "r") as archive:
            try:
                workbook_xml = archive.read("xl/workbook.xml")
            except KeyError as exc:
                raise TemplateException("Invalid XLSX template: missing xl/workbook.xml") from exc

        root = ET.fromstring(workbook_xml)
        sheet_names: list[str] = []
        heading_items: list[ExtractedHeading] = []

        for sheet in root.findall(".//s:sheets/s:sheet", _SHEET_NS):
            name = sheet.attrib.get("name")
            if name:
                sheet_names.append(name.strip())

        if not sheet_names:
            raise TemplateException("No worksheets detected in XLSX template for compilation.")

        for idx, name in enumerate(sheet_names, start=1):
            heading_items.append(
                ExtractedHeading(
                    text=name,
                    level=1,
                    order=idx,
                    style_name="worksheet",
                    numbering=None,
                ),
            )

        skeleton = DocumentSkeleton(
            title=template_path.stem,
            headings=sheet_names,
            heading_items=heading_items,
            raw_structure={
                "source": "xlsx",
                "sheet_count": len(sheet_names),
            },
        )
        schema = self._extract_xlsx_schema(template_path, sheet_names)
        if not any(item.get("headers") for item in schema):
            raise TemplateException("No worksheet header rows detected in XLSX template for compilation.")

        sheet_map = {
            "sheets": [{"name": name, "index": i + 1} for i, name in enumerate(sheet_names)],
            "schema": schema,
        }
        return skeleton, StyleMap(), sheet_map

    def _extract_xlsx_schema(self, template_path: Path, sheet_names: list[str]) -> list[dict[str, object]]:
        schema: list[dict[str, object]] = []
        with open_xlsx_workbook(template_path, read_only=True, data_only=True) as wb:
            for idx, sheet_name in enumerate(sheet_names, start=1):
                if sheet_name not in wb.sheetnames:
                    schema.append(
                        {
                            "sheet_name": sheet_name,
                            "index": idx,
                            "headers": [],
                            "required_columns": [],
                            "column_count": 0,
                        }
                    )
                    continue

                ws = wb[sheet_name]
                headers, detection_meta = self._detect_headers(ws)

                schema.append(
                    {
                        "sheet_name": sheet_name,
                        "index": idx,
                        "headers": headers,
                        "required_columns": list(headers),
                        "column_count": len(headers),
                        "header_detection_metadata": detection_meta,
                    }
                )
        return schema

    def _detect_headers(self, worksheet) -> tuple[list[str], dict[str, object]]:
        mode = str(getattr(settings, "header_detection_mode", "strict_row1") or "strict_row1").strip().lower()
        max_rows = max(1, int(getattr(settings, "header_scan_max_rows", 5) or 5))

        def normalize_row(values: tuple[object, ...]) -> list[str]:
            headers: list[str] = []
            seen: dict[str, int] = {}
            for value in values:
                text = self._normalize_text(str(value or ""))
                if not text:
                    continue
                key = text.lower()
                if key in seen:
                    seen[key] += 1
                    text = f"{text}_{seen[key]}"
                else:
                    seen[key] = 1
                headers.append(text)
            return headers

        if mode == "strict_row1":
            first = next(worksheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
            return normalize_row(first), {"mode": "strict_row1", "selected_row": 1}

        best_row = 1
        best_headers: list[str] = []
        best_score = -1.0
        for r in range(1, max_rows + 1):
            row = next(worksheet.iter_rows(min_row=r, max_row=r, values_only=True), ())
            headers = normalize_row(row)
            if not row:
                continue
            non_empty_ratio = (len(headers) / len(row)) if len(row) else 0.0
            numeric_count = sum(1 for v in headers if v.replace(".", "", 1).isdigit())
            numeric_ratio = (numeric_count / len(headers)) if headers else 1.0
            score = non_empty_ratio - numeric_ratio
            if score > best_score:
                best_score = score
                best_headers = headers
                best_row = r
        return best_headers, {
            "mode": "heuristic_scan_n_rows",
            "selected_row": best_row,
            "max_rows_scanned": max_rows,
            "score": round(best_score, 4),
        }

    def _normalize_text(self, text: str) -> str:
        return " ".join((text or "").split()).strip()

    def _is_toc_title(self, text: str) -> bool:
        return bool(self._TOC_TITLE_RE.match(text))

    def _is_toc_style(self, style_value: str) -> bool:
        if not style_value:
            return False
        return style_value.startswith("toc")

    def _looks_like_toc_line(self, text: str) -> bool:
        return bool(self._TOC_LINE_RE.match(text))

    def _is_real_heading(self, text: str, style_value: str) -> bool:
        """Detect actual body headings while excluding TOC content.

        Accepts paragraphs styled ``HeadingN``, numbered headings, and
        short ALL-CAPS lines; rejects ``toc`` style and dot-leader rows.
        """
        if not text:
            return False

        if self._is_toc_style(style_value):
            return False

        if self._looks_like_toc_line(text):
            return False

        is_heading = "heading" in style_value

        if not is_heading and self._NUMBERED_HEADING_RE.match(text):
            is_heading = True

        if not is_heading and text.isupper() and len(text.split()) <= 12:
            is_heading = True

        return is_heading

    def _derive_heading_level(self, text: str, style_value: str) -> int:
        """Prefer explicit ``Heading N`` styles. Otherwise infer from numbering depth.

        ``1.2.3 Foo`` is level 3 (two dots + 1); a bare ``Foo`` line is level 1.
        """
        if style_value:
            style_match = self._HEADING_STYLE_LEVEL_RE.search(style_value)
            if style_match:
                try:
                    return max(1, int(style_match.group(1)))
                except ValueError:
                    pass

        numbering = self._extract_numbering_prefix(text)
        if numbering:
            return numbering.count(".") + 1

        return 1

    def _extract_numbering_prefix(self, text: str) -> str | None:
        match = self._NUMBERED_HEADING_RE.match(text)
        if not match:
            return None
        return match.group("num")
