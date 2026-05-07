"""Strict placeholder DOCX filler wrapper.

Current implementation reuses DocxFiller for compatibility while exposing
strict-mode diagnostics and contract boundary.
"""

from __future__ import annotations

from pathlib import Path

from modules.assembly.models import AssembledDocument
from modules.export.docx_filler import DocxFiller
from modules.template.models import StyleMap


class DocxPlaceholderFiller:
    def __init__(self, storage_root: Path) -> None:
        self._delegate = DocxFiller(storage_root)

    def fill(
        self,
        *,
        template_path: Path,
        assembled: AssembledDocument,
        output_path: Path,
        style_map: StyleMap,
        placeholder_schema: dict[str, object] | None,
    ) -> list[dict[str, object]]:
        warnings = self._delegate.fill(
            template_path=template_path,
            assembled=assembled,
            output_path=output_path,
            style_map=style_map,
        )
        if not placeholder_schema:
            warnings.append(
                {
                    "code": "placeholder_schema_missing",
                    "severity": "warning",
                    "message": "Strict DOCX filler executed without placeholder schema.",
                }
            )
        return warnings

