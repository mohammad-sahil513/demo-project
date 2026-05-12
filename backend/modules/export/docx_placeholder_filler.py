"""Strict placeholder DOCX filler wrapper.

Public surface for the *strict* placeholder fill path. The current
implementation delegates to the legacy :class:`DocxFiller` so we can swap
in the new native writer behind this stable contract without touching the
renderer. The wrapper sets ``placeholder_schema`` to ``None`` on the
delegate call so the heading-based path runs uniformly — strict gating
itself is enforced by the renderer before this filler is invoked.
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

