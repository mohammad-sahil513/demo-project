"""Strict XLSX filler wrapper using existing builder with contract checks."""

from __future__ import annotations

from pathlib import Path

from modules.assembly.models import AssembledDocument
from modules.export.xlsx_builder import XlsxBuilder
from modules.export.xlsx_contract_guard import check_xlsx_schema


class XlsxPlaceholderFiller:
    def __init__(self) -> None:
        self._builder = XlsxBuilder()

    def fill(
        self,
        *,
        assembled: AssembledDocument,
        output_path: Path,
        template_path: Path | None,
        sheet_map: dict[str, object] | None,
        placeholder_schema: dict[str, object] | None,
    ) -> list[dict[str, object]]:
        warnings = check_xlsx_schema(placeholder_schema)
        warnings.extend(
            self._builder.build(
                assembled=assembled,
                output_path=output_path,
                template_path=template_path,
                sheet_map=sheet_map,
            )
        )
        return warnings

