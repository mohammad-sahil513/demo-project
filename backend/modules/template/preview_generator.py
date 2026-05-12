"""Generate preview assets for compiled custom templates.

Two outputs:

- DOCX preview — a minimal Word document with the section plan rendered as
  numbered indented lines and a "Generated content placeholder" stub per
  section. Used by the template list UI as a quick visual sanity check.
- HTML preview — XLSX-only, a tiny ``<table>`` of sheet names. The template
  preview modal in the frontend renders this directly.

The minimal DOCX writer here only emits text paragraphs (no styling) — it
is intentionally tiny and dependency-free. For the sample-content preview
(closer to a real export) see ``modules.template.sample_assembled``.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
from zipfile import ZipFile

from core.exceptions import TemplateException
from modules.template.models import DocumentSkeleton, SectionDefinition


class TemplatePreviewGenerator:
    def build_preview_docx(
        self,
        *,
        destination: Path,
        title: str,
        section_plan: list[SectionDefinition],
    ) -> Path:
        lines = [f"Template Preview: {title}", ""]

        for section in section_plan:
            indent = "  " * max(0, section.level - 1)
            lines.append(f"{indent}{section.execution_order}. {section.title}")
            lines.append(f"{indent}Generated content placeholder.")
            lines.append("")

        destination.parent.mkdir(parents=True, exist_ok=True)
        self._write_minimal_docx(destination, lines)
        return destination

    def build_preview_html_from_xlsx(self, skeleton: DocumentSkeleton) -> str:
        if not skeleton.headings:
            raise TemplateException("Cannot build XLSX preview without sheet headings.")

        rows = "".join(
            f"<tr><td>{index + 1}</td><td>{escape(name)}</td></tr>"
            for index, name in enumerate(skeleton.headings)
        )
        return (
            "<div><h3>Template Preview</h3>"
            "<table><thead><tr><th>#</th><th>Sheet</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>"
        )

    def _write_minimal_docx(self, destination: Path, lines: list[str]) -> None:
        paragraph_xml = "".join(
            f"<w:p><w:r><w:t>{self._escape_xml(line)}</w:t></w:r></w:p>"
            for line in lines
        )
        document_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body>{paragraph_xml}</w:body>"
            "</w:document>"
        )
        content_types = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>"
        )
        rels = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            "</Relationships>"
        )

        with ZipFile(destination, "w") as archive:
            archive.writestr("[Content_Types].xml", content_types)
            archive.writestr("_rels/.rels", rels)
            archive.writestr("word/document.xml", document_xml)

    def _escape_xml(self, value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )
