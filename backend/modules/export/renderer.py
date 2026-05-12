"""Route assembled documents to the correct file builder.

The :class:`ExportRenderer` is the single public entry point used by the
RENDER_EXPORT workflow phase. Given an :class:`AssembledDocument` plus
template / document context, it decides which builder to invoke:

- **Inbuilt DOCX**          built from scratch by :class:`DocxBuilder`
                            using one of the inbuilt style maps.
- **Custom DOCX (native)**  placeholder-native filler that writes content
                            into deterministic OOXML locations.
- **Custom DOCX (strict)**  placeholder filler with strict fidelity gates
                            (no fallback when schema is incomplete).
- **Custom DOCX (legacy)**  heading-based filler retained for backward
                            compatibility (gated by feature flag).
- **XLSX**                  workbook filler that respects the user-supplied
                            template's sheet layout.

Each path runs a post-build pipeline: integrity check (zip + media +
content control), surface fidelity scan, optional structure fixer for
title/TOC pagination, and a flag to make Word recompute fields on open.
"""
from __future__ import annotations

from pathlib import Path

from core.config import settings
from core.constants import DocType, TemplateSource
from modules.assembly.models import AssembledDocument, AssembledSection
from modules.assembly.normalizer import normalize_section_content
from modules.export.docx_builder import DocxBuilder
from modules.export.docx_filler import DocxFiller
from modules.export.docx_integrity import check_docx_integrity, check_docx_surface_fidelity
from modules.export.docx_placeholder_filler import DocxPlaceholderFiller
from modules.export.docx_placeholder_writer import fill_docx_placeholders_native
from modules.export.docx_structure_fixer import enforce_title_toc_pagination
from modules.export.docx_update_fields import ensure_update_fields_on_open
from modules.export.types import ExportDocumentInfo, ExportTemplateInfo
from modules.export.xlsx_builder import XlsxBuilder
from modules.export.xlsx_placeholder_filler import XlsxPlaceholderFiller
from modules.template.inbuilt.registry import is_inbuilt_template_id
from modules.template.models import StyleMap


class ExportRenderer:
    def __init__(self, storage_root: Path) -> None:
        self._storage_root = storage_root
        self._docx_builder = DocxBuilder(storage_root)
        self._docx_filler = DocxFiller(storage_root)
        self._docx_placeholder_filler = DocxPlaceholderFiller(storage_root)
        self._xlsx = XlsxBuilder()
        self._xlsx_placeholder_filler = XlsxPlaceholderFiller()

    def _finalize_docx_export(
        self,
        out: Path,
        *,
        document: ExportDocumentInfo,
        assembled: AssembledDocument,
        export_warnings: list[dict[str, object]],
        apply_structure_fixer: bool,
    ) -> None:
        if apply_structure_fixer:
            export_warnings.extend(
                enforce_title_toc_pagination(
                    out,
                    doc_title=document.filename,
                    doc_type=assembled.doc_type,
                )
            )
        elif settings.template_docx_structure_fixer_enabled:
            scope = (settings.template_docx_structure_fixer_scope or "inbuilt_only").strip().lower()
            if scope != "all":
                export_warnings.append(
                    {
                        "phase": "RENDER_EXPORT",
                        "code": "docx_structure_fixer_skipped_non_inbuilt",
                        "message": (
                            "Title/TOC pagination fixer skipped for this export to preserve custom template layout. "
                            "Set TEMPLATE_DOCX_STRUCTURE_FIXER_SCOPE=all for legacy behavior on custom DOCX."
                        ),
                    }
                )
        ensure_update_fields_on_open(out)

    @staticmethod
    def _apply_structure_fixer_for_path(*, filled_custom_template: bool) -> bool:
        scope = (settings.template_docx_structure_fixer_scope or "inbuilt_only").strip().lower()
        if scope == "all":
            return True
        return not filled_custom_template

    def render(
        self,
        *,
        workflow_run_id: str,
        document: ExportDocumentInfo,
        template: ExportTemplateInfo,
        assembled: AssembledDocument,
        style_map: StyleMap,
        sheet_map: dict[str, object] | None = None,
        export_mode: str | None = None,
    ) -> tuple[Path, str, list[dict[str, object]]]:
        outputs = self._storage_root / "outputs"
        outputs.mkdir(parents=True, exist_ok=True)

        stem = Path(document.filename).stem
        friendly_doc = f"{stem}_{assembled.doc_type}"

        export_warnings: list[dict[str, object]] = []

        mode = (export_mode or assembled.export_mode or "final").strip().lower()
        assembled_for_export = self._prepare_document_for_export(
            assembled=assembled,
            export_mode=mode,
            export_warnings=export_warnings,
        )

        if assembled_for_export.doc_type == DocType.UAT.value:
            out = outputs / f"{workflow_run_id}.xlsx"
            tpl: Path | None = None
            if template.file_path:
                cand = self._storage_root / "templates" / Path(template.file_path)
                if cand.is_file():
                    tpl = cand

            if settings.template_fidelity_strict_enabled:
                xlsx_warnings = self._xlsx_placeholder_filler.fill(
                    assembled=assembled_for_export,
                    output_path=out,
                    template_path=tpl,
                    sheet_map=sheet_map,
                    placeholder_schema=template.placeholder_schema,
                )
            else:
                xlsx_warnings = self._xlsx.build(
                    assembled_for_export,
                    out,
                    template_path=tpl,
                    sheet_map=sheet_map,
                )
            export_warnings.extend(xlsx_warnings)
            return out, f"{friendly_doc}.xlsx", export_warnings

        out = outputs / f"{workflow_run_id}.docx"

        use_inbuilt = (
            template.template_source == TemplateSource.INBUILT
            or is_inbuilt_template_id(template.template_id)
        )
        if use_inbuilt:
            self._docx_builder.build(assembled_for_export, style_map, out)
            self._finalize_docx_export(
                out,
                document=document,
                assembled=assembled_for_export,
                export_warnings=export_warnings,
                apply_structure_fixer=self._apply_structure_fixer_for_path(filled_custom_template=False),
            )
            return out, f"{friendly_doc}.docx", export_warnings

        custom_tpl: Path | None = None
        if template.file_path:
            cand = self._storage_root / "templates" / Path(template.file_path)
            if cand.is_file():
                custom_tpl = cand

        if custom_tpl is not None:
            use_native = (
                settings.template_docx_placeholder_native_enabled
                and template.section_placeholder_map
                and len(template.section_placeholder_map) > 0
                and template.placeholder_schema is not None
            )
            if settings.template_docx_require_native_for_custom and not use_native:
                export_warnings.append(
                    {
                        "phase": "RENDER_EXPORT",
                        "code": "docx_native_prerequisites_unmet",
                        "message": (
                            "Custom DOCX export requires placeholder-native path "
                            "(TEMPLATE_DOCX_PLACEHOLDER_NATIVE_ENABLED, non-empty bindings map, placeholder_schema)."
                        ),
                    },
                )
                return out, f"{friendly_doc}.docx", export_warnings
            if use_native:
                export_warnings.extend(
                    fill_docx_placeholders_native(
                        template_path=custom_tpl,
                        output_path=out,
                        assembled=assembled_for_export,
                        placeholder_schema=template.placeholder_schema,
                        section_placeholder_map=dict(template.section_placeholder_map),
                    )
                )
                self._finalize_docx_export(
                    out,
                    document=document,
                    assembled=assembled_for_export,
                    export_warnings=export_warnings,
                    apply_structure_fixer=self._apply_structure_fixer_for_path(filled_custom_template=True),
                )
                export_warnings.extend(
                    check_docx_integrity(
                        template_path=custom_tpl,
                        output_path=out,
                        placeholder_schema=template.placeholder_schema,
                    )
                )
                export_warnings.extend(
                    check_docx_surface_fidelity(
                        template_path=custom_tpl,
                        output_path=out,
                        placeholder_schema=template.placeholder_schema,
                    )
                )
            elif settings.template_fidelity_strict_enabled:
                export_warnings.extend(
                    self._docx_placeholder_filler.fill(
                        template_path=custom_tpl,
                        assembled=assembled_for_export,
                        output_path=out,
                        style_map=style_map,
                        placeholder_schema=template.placeholder_schema,
                    )
                )
                self._finalize_docx_export(
                    out,
                    document=document,
                    assembled=assembled_for_export,
                    export_warnings=export_warnings,
                    apply_structure_fixer=self._apply_structure_fixer_for_path(filled_custom_template=True),
                )
                export_warnings.extend(
                    check_docx_integrity(
                        template_path=custom_tpl,
                        output_path=out,
                        placeholder_schema=template.placeholder_schema,
                    )
                )
                export_warnings.extend(
                    check_docx_surface_fidelity(
                        template_path=custom_tpl,
                        output_path=out,
                        placeholder_schema=template.placeholder_schema,
                    )
                )
            else:
                if not settings.template_docx_legacy_export_allowed:
                    export_warnings.append(
                        {
                            "phase": "RENDER_EXPORT",
                            "code": "docx_legacy_export_disallowed",
                            "message": (
                                "Heading-based DocxFiller export is disabled "
                                "(TEMPLATE_DOCX_LEGACY_EXPORT_ALLOWED=false). "
                                "Enable native placeholders or TEMPLATE_FIDELITY_STRICT_ENABLED."
                            ),
                        },
                    )
                    return out, f"{friendly_doc}.docx", export_warnings
                export_warnings.extend(
                    self._docx_filler.fill(custom_tpl, assembled_for_export, out, style_map=style_map),
                )
                self._finalize_docx_export(
                    out,
                    document=document,
                    assembled=assembled_for_export,
                    export_warnings=export_warnings,
                    apply_structure_fixer=self._apply_structure_fixer_for_path(filled_custom_template=True),
                )
                export_warnings.extend(
                    check_docx_surface_fidelity(
                        template_path=custom_tpl,
                        output_path=out,
                        placeholder_schema=template.placeholder_schema,
                    )
                )
            return out, f"{friendly_doc}.docx", export_warnings

        self._docx_builder.build(assembled_for_export, style_map, out)
        self._finalize_docx_export(
            out,
            document=document,
            assembled=assembled_for_export,
            export_warnings=export_warnings,
            apply_structure_fixer=self._apply_structure_fixer_for_path(filled_custom_template=False),
        )
        return out, f"{friendly_doc}.docx", export_warnings

    def _prepare_document_for_export(
        self,
        *,
        assembled: AssembledDocument,
        export_mode: str,
        export_warnings: list[dict[str, object]],
    ) -> AssembledDocument:
        """
        Final safety-pass before rendering.

        Why this exists:
        - Assembly should already normalize content, but export should still enforce
          final-mode stripping so internal drafting content does not leak into deliverables
          if upstream content arrives unclean.
        """
        if export_mode != "final":
            return assembled

        cleaned_sections: list[AssembledSection] = []
        child_map = self._build_child_title_map(assembled)

        for section in assembled.sections:
            if section.output_type == "diagram":
                if not section.diagram_path:
                    export_warnings.append(
                        {
                            "phase": "RENDER_EXPORT",
                            "code": "diagram_path_missing",
                            "section_id": section.section_id,
                            "title": section.title,
                            "message": (
                                f"Diagram section {section.title!r} reached export without a diagram_path; "
                                "the final DOCX may show only the heading."
                            ),
                        },
                    )
                cleaned_sections.append(
                    section.model_copy(
                        update={
                            "export_mode": "final",
                        }
                    )
                )
                continue

            normalized = normalize_section_content(
                section_title=section.title,
                content=section.content or "",
                child_titles=child_map.get(section.section_id, []),
                export_mode="final",
            )
            cleaned_sections.append(
                section.model_copy(
                    update={
                        "content": normalized.content,
                        "export_mode": "final",
                    }
                )
            )

        return assembled.model_copy(
            update={
                "sections": cleaned_sections,
                "export_mode": "final",
            }
        )

    def _build_child_title_map(self, assembled: AssembledDocument) -> dict[str, list[str]]:
        """
        Reconstruct child-title visibility from assembled section ordering + levels.
        """
        child_map: dict[str, list[str]] = {}
        sections = assembled.sections

        for idx, current in enumerate(sections):
            child_titles: list[str] = []
            current_level = int(current.level)

            for next_section in sections[idx + 1:]:
                next_level = int(next_section.level)
                if next_level <= current_level:
                    break
                child_titles.append(next_section.title)

            child_map[current.section_id] = child_titles

        return child_map
