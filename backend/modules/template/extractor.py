"""Template skeleton and style extraction for custom templates."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

from core.exceptions import TemplateException
from modules.template.models import DocumentSkeleton, StyleMap

_WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
_SHEET_NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


class TemplateExtractor:
    def extract(self, template_path: Path) -> tuple[DocumentSkeleton, StyleMap, dict[str, object]]:
        suffix = template_path.suffix.lower()
        if suffix == ".docx":
            return self.extract_docx(template_path)
        if suffix == ".xlsx":
            return self.extract_xlsx(template_path)
        raise TemplateException(f"Unsupported template format: {template_path.suffix}")

    def extract_docx(self, template_path: Path) -> tuple[DocumentSkeleton, StyleMap, dict[str, object]]:
        headings: list[str] = []
        with ZipFile(template_path, "r") as archive:
            try:
                document_xml = archive.read("word/document.xml")
            except KeyError as exc:
                raise TemplateException("Invalid DOCX template: missing word/document.xml") from exc
        root = ET.fromstring(document_xml)
        for paragraph in root.findall(".//w:p", _WORD_NS):
            text = "".join(node.text or "" for node in paragraph.findall(".//w:t", _WORD_NS)).strip()
            if not text:
                continue
            style_name = paragraph.find(".//w:pStyle", _WORD_NS)
            style_value = ""
            if style_name is not None:
                style_value = (style_name.attrib.get(f'{{{_WORD_NS["w"]}}}val') or "").lower()
            # Capture likely section headings; fallback accepts short all-caps title-like lines.
            is_heading = "heading" in style_value or bool(re.match(r"^(?:\d+(?:\.\d+)*)\s+\S+", text))
            if not is_heading and text.isupper() and len(text.split()) <= 12:
                is_heading = True
            if is_heading:
                headings.append(text)

        if not headings:
            raise TemplateException("No headings detected in DOCX template for compilation.")

        skeleton = DocumentSkeleton(
            title=template_path.stem,
            headings=headings,
            raw_structure={"source": "docx", "heading_count": len(headings)},
        )
        return skeleton, StyleMap(), {}

    def extract_xlsx(self, template_path: Path) -> tuple[DocumentSkeleton, StyleMap, dict[str, object]]:
        with ZipFile(template_path, "r") as archive:
            try:
                workbook_xml = archive.read("xl/workbook.xml")
            except KeyError as exc:
                raise TemplateException("Invalid XLSX template: missing xl/workbook.xml") from exc
        root = ET.fromstring(workbook_xml)
        sheet_names: list[str] = []
        for sheet in root.findall(".//s:sheets/s:sheet", _SHEET_NS):
            name = sheet.attrib.get("name")
            if name:
                sheet_names.append(name.strip())
        if not sheet_names:
            raise TemplateException("No worksheets detected in XLSX template for compilation.")

        skeleton = DocumentSkeleton(
            title=template_path.stem,
            headings=sheet_names,
            raw_structure={"source": "xlsx", "sheet_count": len(sheet_names)},
        )
        sheet_map = {
            "sheets": [{"name": name, "index": i + 1} for i, name in enumerate(sheet_names)],
        }
        return skeleton, StyleMap(), sheet_map
