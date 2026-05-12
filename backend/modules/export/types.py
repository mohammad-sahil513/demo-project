"""Export-layer input value types — decoupled from repository models.

``modules.export`` deliberately does not import from
``repositories.*_models`` so the layering rule stays clean. The services
layer constructs these :class:`NamedTuple` adapters and hands them to the
renderer instead.

- ``ExportDocumentInfo``  the source document's filename, used for the
                          export title and output filename.
- ``ExportTemplateInfo``  the template binding: which template, its
                          source (inbuilt / custom), the disk path for
                          custom templates, the placeholder schema, and
                          the section -> placeholder mapping that the
                          native filler consumes.
"""

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
