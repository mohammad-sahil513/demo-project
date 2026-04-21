"""Route assembled documents to the correct file builder."""

from __future__ import annotations

from pathlib import Path

from core.constants import DocType, TemplateSource
from modules.assembly.models import AssembledDocument
from modules.export.docx_builder import DocxBuilder
from modules.export.docx_filler import DocxFiller
from modules.export.types import ExportDocumentInfo, ExportTemplateInfo
from modules.export.xlsx_builder import XlsxBuilder
from modules.template.inbuilt.registry import is_inbuilt_template_id
from modules.template.models import StyleMap


class ExportRenderer:
    def __init__(self, storage_root: Path) -> None:
        self._storage_root = storage_root
        self._docx_builder = DocxBuilder(storage_root)
        self._docx_filler = DocxFiller(storage_root)
        self._xlsx = XlsxBuilder()

    def render(
        self,
        *,
        workflow_run_id: str,
        document: ExportDocumentInfo,
        template: ExportTemplateInfo,
        assembled: AssembledDocument,
        style_map: StyleMap,
        sheet_map: dict[str, object] | None = None,
    ) -> tuple[Path, str, list[dict[str, object]]]:
        outputs = self._storage_root / "outputs"
        outputs.mkdir(parents=True, exist_ok=True)
        stem = Path(document.filename).stem
        friendly_doc = f"{stem}_{assembled.doc_type}"
        export_warnings: list[dict[str, object]] = []

        if assembled.doc_type == DocType.UAT.value:
            out = outputs / f"{workflow_run_id}.xlsx"
            tpl: Path | None = None
            if template.file_path:
                cand = self._storage_root / "templates" / Path(template.file_path)
                if cand.is_file():
                    tpl = cand
            self._xlsx.build(assembled, out, template_path=tpl, sheet_map=sheet_map)
            return out, f"{friendly_doc}.xlsx", export_warnings

        out = outputs / f"{workflow_run_id}.docx"
        use_inbuilt = template.template_source == TemplateSource.INBUILT or is_inbuilt_template_id(
            template.template_id,
        )
        if use_inbuilt:
            self._docx_builder.build(assembled, style_map, out)
            return out, f"{friendly_doc}.docx", export_warnings

        custom_tpl: Path | None = None
        if template.file_path:
            cand = self._storage_root / "templates" / Path(template.file_path)
            if cand.is_file():
                custom_tpl = cand
        if custom_tpl is not None:
            export_warnings.extend(
                self._docx_filler.fill(custom_tpl, assembled, out, style_map=style_map),
            )
            return out, f"{friendly_doc}.docx", export_warnings

        self._docx_builder.build(assembled, style_map, out)
        return out, f"{friendly_doc}.docx", export_warnings
