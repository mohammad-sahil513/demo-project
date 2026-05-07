"""Export inputs decoupled from repository models (layering)."""

from __future__ import annotations

from typing import NamedTuple


class ExportDocumentInfo(NamedTuple):
    filename: str


class ExportTemplateInfo(NamedTuple):
    template_id: str
    template_source: str
    file_path: str | None
    placeholder_schema: dict[str, object] | None = None
    section_placeholder_map: dict[str, list[str]] | None = None
