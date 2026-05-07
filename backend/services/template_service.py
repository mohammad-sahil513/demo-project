"""Template service for custom template files and compile lifecycle."""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from core.config import settings
from core.constants import TemplateStatus
from core.ids import template_id, utc_now_iso
from core.logging import get_logger
from core.exceptions import TemplateException
from infrastructure.sk_adapter import AzureSKAdapter
from modules.template.classifier import TemplateClassifier
from modules.template.contract_validator import validate_template_schema
from modules.template.docx_template_normalize import apply_docx_template_normalize
from modules.template.extractor import TemplateExtractor
from modules.template.schema_models import TemplateSchema
from modules.template.export_hint import compute_export_path_hint
from modules.template.section_bindings import resolve_section_placeholder_bindings
from modules.template.models import StyleMap
from modules.template.planner import SectionPlanner
from modules.template.section_plan_apply import apply_xlsx_sheet_schema_to_plan
from modules.template.preview_generator import TemplatePreviewGenerator
from modules.template.sample_assembled import assembled_document_from_section_plan
from modules.template.schema_extractor_docx import extract_docx_schema
from modules.template.schema_extractor_xlsx import extract_xlsx_schema
from modules.export.docx_filler import DocxFiller
from modules.export.docx_integrity import check_docx_integrity, summarize_docx_integrity_issues
from modules.export.docx_placeholder_filler import DocxPlaceholderFiller
from repositories.template_models import TemplateRecord
from repositories.template_repo import TemplateRepository

logger = get_logger(__name__)


class TemplateService:
    def __init__(
        self,
        repo: TemplateRepository,
        *,
        extractor: TemplateExtractor | None = None,
        classifier: TemplateClassifier | None = None,
        planner: SectionPlanner | None = None,
        preview_generator: TemplatePreviewGenerator | None = None,
        sk_adapter: AzureSKAdapter | None = None,
    ) -> None:
        self._repo = repo
        self._extractor = extractor or TemplateExtractor()
        adapter = sk_adapter or AzureSKAdapter()
        self._classifier = classifier or TemplateClassifier(adapter)
        self._planner = planner or SectionPlanner()
        self._preview_generator = preview_generator or TemplatePreviewGenerator()

    def export_path_hint_for_record(self, record: TemplateRecord) -> str:
        return compute_export_path_hint(record)

    async def _classify_sections_resilient(self, skeleton: object) -> object:
        timeout = max(1.0, float(settings.template_classifier_timeout_seconds))
        retries = max(0, int(settings.template_classifier_max_retries))
        attempts = retries + 1
        last_exc: BaseException | None = None
        for attempt in range(attempts):
            try:
                return await asyncio.wait_for(
                    self._classifier.classify_sections(skeleton),
                    timeout=timeout,
                )
            except TimeoutError as exc:
                last_exc = exc
                logger.warning(
                    "template.compile.classifier_timeout attempt=%s/%s timeout_s=%s",
                    attempt + 1,
                    attempts,
                    timeout,
                )
        msg = (
            f"Template section classification timed out after {attempts} attempt(s) ({timeout:g}s each). "
            "Check Azure OpenAI availability or increase TEMPLATE_CLASSIFIER_TIMEOUT_SECONDS."
        )
        raise TemplateException(msg) from last_exc

    def requeue_compile(self, template_id_value: str) -> TemplateRecord:
        self.get_or_raise(template_id_value)
        return self._repo.update(
            template_id_value,
            status=TemplateStatus.COMPILING.value,
            compile_error=None,
            updated_at=utc_now_iso(),
        )

    def validate_template_contract(
        self,
        template_id_value: str,
        *,
        persist: bool = True,
    ) -> dict[str, object]:
        record = self.get_or_raise(template_id_value)
        file_path = self.get_file_path(template_id_value)
        suffix = Path(record.filename).suffix.lower()

        if suffix == ".docx":
            schema = extract_docx_schema(file_path)
        elif suffix == ".xlsx":
            schema = extract_xlsx_schema(file_path)
        else:
            raise TemplateException(f"Unsupported template file type: {record.filename}")

        schema_merged = self._merge_user_bindings_into_schema(record, schema)
        validation_errors, validation_warnings = validate_template_schema(schema_merged)
        validation_status = "invalid" if validation_errors else ("warning" if validation_warnings else "valid")

        payload: dict[str, object] = {
            "template_id": record.template_id,
            "schema_version": schema_merged.schema_version,
            "placeholder_schema": schema_merged.model_dump(),
            "validation_status": validation_status,
            "errors": validation_errors,
            "warnings": validation_warnings,
        }

        if persist:
            updated = self._repo.update(
                template_id_value,
                schema_version=schema_merged.schema_version,
                placeholder_schema=schema_merged.model_dump(),
                validation_status=validation_status,
                validation_errors=validation_errors,
                validation_warnings=validation_warnings,
                updated_at=utc_now_iso(),
            )
            payload["template_id"] = updated.template_id

        return payload

    def _merge_user_bindings_into_schema(self, record: TemplateRecord, schema: TemplateSchema) -> TemplateSchema:
        raw = schema.model_dump()
        user = dict(record.section_placeholder_bindings or {})
        if user:
            merged = {**dict(raw.get("section_placeholder_bindings") or {}), **user}
            raw["section_placeholder_bindings"] = merged
        return TemplateSchema.model_validate(raw)

    def update_section_bindings(
        self,
        template_id_value: str,
        bindings: dict[str, object],
    ) -> TemplateRecord:
        """Replace explicit section→placeholder map (hybrid binding layer 1)."""
        self.get_or_raise(template_id_value)
        return self._repo.update(
            template_id_value,
            section_placeholder_bindings=dict(bindings),
            updated_at=utc_now_iso(),
        )

    def _probe_docx_sample_fill_integrity(
        self,
        *,
        template_id_value: str,
        template_path: Path,
        preview_file: Path,
        section_plan_dicts: list[dict[str, object]],
        template_type: str,
        filename: str,
        style_map: StyleMap,
        schema_dump: dict[str, object],
    ) -> tuple[bool, list[dict[str, object]], list[dict[str, object]], dict[str, str]]:
        """
        Run export-parity DOCX fill with sample section bodies, then integrity check vs template.
        Returns (ok, fill_warnings, integrity_issues, summary).
        """
        if not section_plan_dicts:
            return False, [], [], {}

        assembled = assembled_document_from_section_plan(
            template_type=template_type,
            filename=filename,
            section_plan=section_plan_dicts,
        )
        try:
            preview_file.parent.mkdir(parents=True, exist_ok=True)
            if preview_file.exists():
                preview_file.unlink()
        except OSError:
            logger.exception(
                "template.preview.unlink_failed template_id=%s path=%s",
                template_id_value,
                str(preview_file),
            )

        try:
            if settings.template_fidelity_strict_enabled:
                filler = DocxPlaceholderFiller(settings.storage_root)
                fill_warnings = filler.fill(
                    template_path=template_path,
                    assembled=assembled,
                    output_path=preview_file,
                    style_map=style_map,
                    placeholder_schema=schema_dump,
                )
            else:
                legacy = DocxFiller(settings.storage_root)
                fill_warnings = legacy.fill(
                    template_path,
                    assembled,
                    preview_file,
                    style_map=style_map,
                )
            issues = check_docx_integrity(
                template_path=template_path,
                output_path=preview_file,
                placeholder_schema=schema_dump,
            )
            summary = summarize_docx_integrity_issues(issues)
            return True, fill_warnings, issues, summary
        except Exception:
            logger.exception("template.preview.sample_fill.failed template_id=%s", template_id_value)
            try:
                if preview_file.exists():
                    preview_file.unlink()
            except OSError:
                pass
            return False, [], [], {}

    def fidelity_report(self, record: TemplateRecord) -> dict[str, object]:
        """API payload for GET /templates/{id}/fidelity-report (stored probe results)."""
        suffix = Path(record.filename).suffix.lower()
        base: dict[str, object] = {
            "template_id": record.template_id,
            "fidelity_status": record.validation_status,
            "validation_errors": record.validation_errors,
            "validation_warnings": record.validation_warnings,
            "integrity_issues": list(record.fidelity_integrity_issues or []),
            "integrity_checked_at": record.fidelity_integrity_checked_at,
        }
        if suffix != ".docx":
            base["integrity_summary"] = {
                "overall": "not_applicable",
                "header_footer_integrity": "not_applicable",
                "relationship_integrity": "not_applicable",
                "media_integrity": "not_applicable",
                "document_xml_integrity": "not_applicable",
            }
            return base

        summary = dict(record.fidelity_integrity_summary or {})
        if not summary and record.fidelity_integrity_issues:
            summary = summarize_docx_integrity_issues(
                [dict(x) for x in record.fidelity_integrity_issues],
            )
        if not summary and not record.fidelity_integrity_checked_at:
            summary = {
                "overall": "unknown",
                "header_footer_integrity": "unknown",
                "relationship_integrity": "unknown",
                "media_integrity": "unknown",
                "document_xml_integrity": "unknown",
            }
        base["integrity_summary"] = summary
        return base

    def refresh_template_fidelity(self, template_id_value: str, *, persist: bool = True) -> dict[str, object]:
        """Re-run sample fill + integrity for a READY DOCX template; optionally persist."""
        record = self.get_or_raise(template_id_value)
        if record.status != TemplateStatus.READY.value:
            raise TemplateException(
                f"Template {template_id_value} is not READY (status={record.status}).",
            )
        suffix = Path(record.filename).suffix.lower()
        if suffix != ".docx":
            return self.fidelity_report(record)

        file_path = self.get_file_path(template_id_value)
        preview_file = self.get_preview_file_path(template_id_value)
        style_map = StyleMap.model_validate(record.style_map or {})
        section_plan_dicts = [dict(x) for x in (record.section_plan or [])]
        schema_dump = dict(record.placeholder_schema or {})

        ok, _fill_w, issues, summary = self._probe_docx_sample_fill_integrity(
            template_id_value=template_id_value,
            template_path=file_path,
            preview_file=preview_file,
            section_plan_dicts=section_plan_dicts,
            template_type=record.template_type,
            filename=record.filename,
            style_map=style_map,
            schema_dump=schema_dump,
        )
        if not ok:
            raise TemplateException(
                "Sample preview fill failed; ensure the template compiles with a non-empty section plan.",
            )

        checked_at = utc_now_iso()
        if persist:
            record = self._repo.update(
                template_id_value,
                fidelity_integrity_issues=issues,
                fidelity_integrity_summary=summary,
                fidelity_integrity_checked_at=checked_at,
                updated_at=checked_at,
            )
        else:
            record = record.model_copy(
                update={
                    "fidelity_integrity_issues": issues,
                    "fidelity_integrity_summary": summary,
                    "fidelity_integrity_checked_at": checked_at,
                },
            )
        payload = self.fidelity_report(record)
        payload["refreshed"] = True
        return payload

    def save_template(
        self,
        *,
        filename: str,
        template_type: str,
        payload: bytes,
        version: str | None = None,
    ) -> TemplateRecord:
        now = utc_now_iso()
        new_id = template_id()

        file_path = self._repo._path / f"{new_id}.bin"
        file_path.write_bytes(payload)

        record = TemplateRecord(
            template_id=new_id,
            filename=filename,
            template_type=template_type,
            version=version,
            status=TemplateStatus.COMPILING.value,
            file_path=file_path.name,
            created_at=now,
            updated_at=now,
        )
        return self._repo.save(record)

    async def compile_template(self, template_id_value: str) -> TemplateRecord:
        record = self.get_or_raise(template_id_value)

        if record.status not in {
            TemplateStatus.COMPILING.value,
            TemplateStatus.PENDING.value,
        }:
            return record

        preview_file: Path | None = None

        try:
            file_path = self.get_file_path(template_id_value)
            suffix = Path(record.filename).suffix.lower()

            normalize_warnings: list[dict[str, object]] = []
            if suffix == ".docx" and settings.template_upload_normalize_enabled:
                normalize_warnings = apply_docx_template_normalize(file_path)

            if suffix == ".docx":
                skeleton, style_map, sheet_map = self._extractor.extract_docx(file_path)
                schema = extract_docx_schema(file_path)
            elif suffix == ".xlsx":
                skeleton, style_map, sheet_map = self._extractor.extract_xlsx(file_path)
                schema = extract_xlsx_schema(file_path)
            else:
                raise TemplateException(f"Unsupported template file type: {record.filename}")

            schema_merged = self._merge_user_bindings_into_schema(record, schema)
            validation_errors, validation_warnings = validate_template_schema(schema_merged)
            validation_errors = list(validation_errors)
            validation_warnings = list(validation_warnings) + normalize_warnings

            if settings.template_schema_validation_blocking and validation_errors:
                raise TemplateException(
                    f"Template schema validation failed with {len(validation_errors)} error(s).",
                )

            classifications = await self._classify_sections_resilient(skeleton)
            section_plan = self._planner.build_from_skeleton_and_classifications(
                skeleton,
                classifications,
            )
            section_plan = apply_xlsx_sheet_schema_to_plan(section_plan, sheet_map)

            resolved_map, bind_err, bind_warn = resolve_section_placeholder_bindings(
                section_plan=[s.model_dump() for s in section_plan],
                placeholder_schema=schema_merged.model_dump(),
            )
            validation_errors.extend(bind_err)
            validation_warnings.extend(bind_warn)
            validation_status = "invalid" if validation_errors else ("warning" if validation_warnings else "valid")

            if settings.template_section_binding_strict and bind_err:
                raise TemplateException(
                    f"Section–placeholder binding failed with {len(bind_err)} error(s).",
                )
            if settings.template_schema_validation_blocking and validation_errors:
                raise TemplateException(
                    f"Template schema validation failed with {len(validation_errors)} error(s).",
                )

            preview_html: str | None = None
            preview_path: str | None = None
            fidelity_integrity_issues: list[dict[str, object]] = []
            fidelity_integrity_summary: dict[str, str] = {}
            fidelity_integrity_checked_at: str | None = None

            if suffix == ".docx":
                preview_file = self._repo._path / f"{template_id_value}_preview.docx"
                section_plan_dicts = [s.model_dump() for s in section_plan]
                schema_dump = schema_merged.model_dump()
                if settings.template_preview_sample_fill_enabled:
                    ok, _fw, issues, summary = self._probe_docx_sample_fill_integrity(
                        template_id_value=template_id_value,
                        template_path=file_path,
                        preview_file=preview_file,
                        section_plan_dicts=section_plan_dicts,
                        template_type=record.template_type,
                        filename=record.filename,
                        style_map=style_map,
                        schema_dump=schema_dump,
                    )
                    if ok:
                        preview_path = preview_file.name
                        fidelity_integrity_issues = issues
                        fidelity_integrity_summary = summary
                        fidelity_integrity_checked_at = utc_now_iso()
                    else:
                        fidelity_integrity_issues = [
                            {
                                "code": "preview_sample_fill_failed",
                                "severity": "warning",
                                "message": (
                                    "Sample fill for preview did not complete; "
                                    "using fallback preview artifact."
                                ),
                            }
                        ]
                        fidelity_integrity_summary = {
                            "overall": "unknown",
                            "header_footer_integrity": "unknown",
                            "relationship_integrity": "unknown",
                            "media_integrity": "unknown",
                            "document_xml_integrity": "unknown",
                        }
                        fidelity_integrity_checked_at = utc_now_iso()
                        try:
                            if preview_file.exists():
                                preview_file.unlink()
                        except OSError:
                            pass
                        if settings.template_fidelity_preview_v2_enabled:
                            shutil.copyfile(file_path, preview_file)
                        else:
                            self._preview_generator.build_preview_docx(
                                destination=preview_file,
                                title=skeleton.title,
                                section_plan=section_plan,
                            )
                        preview_path = preview_file.name
                elif settings.template_fidelity_preview_v2_enabled:
                    shutil.copyfile(file_path, preview_file)
                    preview_path = preview_file.name
                else:
                    self._preview_generator.build_preview_docx(
                        destination=preview_file,
                        title=skeleton.title,
                        section_plan=section_plan,
                    )
                    preview_path = preview_file.name
            else:
                preview_html = self._preview_generator.build_preview_html_from_xlsx(skeleton)

            update_kw: dict[str, object] = dict(
                status=TemplateStatus.READY.value,
                compiled_at=utc_now_iso(),
                compile_error=None,
                section_plan=[section.model_dump() for section in section_plan],
                style_map=style_map.model_dump(),
                sheet_map=sheet_map,
                schema_version=schema_merged.schema_version,
                placeholder_schema=schema_merged.model_dump(),
                validation_status=validation_status,
                validation_errors=validation_errors,
                validation_warnings=validation_warnings,
                preview_path=preview_path,
                preview_html=preview_html,
                resolved_section_bindings=dict(resolved_map),
            )
            if suffix == ".docx":
                update_kw["fidelity_integrity_issues"] = fidelity_integrity_issues
                update_kw["fidelity_integrity_summary"] = fidelity_integrity_summary
                update_kw["fidelity_integrity_checked_at"] = fidelity_integrity_checked_at
            else:
                update_kw["fidelity_integrity_issues"] = []
                update_kw["fidelity_integrity_summary"] = {}
                update_kw["fidelity_integrity_checked_at"] = None

            xlsx_schema_n = 0
            if isinstance(sheet_map, dict):
                sch = sheet_map.get("schema")
                if isinstance(sch, list):
                    xlsx_schema_n = len(sch)
            docx_table_heading_orders = (
                len(skeleton.table_headers_by_heading_order) if suffix == ".docx" else 0
            )
            table_sections_with_contract = sum(
                1
                for s in section_plan
                if s.output_type == "table" and (s.table_headers or s.required_fields)
            )
            logger.info(
                "template.compile.summary template_id=%s source_format=%s section_count=%s "
                "docx_heading_orders_with_table_headers=%s xlsx_schema_sheet_rows=%s "
                "table_sections_with_contract=%s",
                template_id_value,
                suffix.lstrip("."),
                len(section_plan),
                docx_table_heading_orders,
                xlsx_schema_n if suffix == ".xlsx" else 0,
                table_sections_with_contract,
            )

            return self._repo.update(template_id_value, **update_kw)

        except Exception as exc:
            logger.exception("template.compile.failed template_id=%s", template_id_value)
            compile_error = str(exc) or "Template compile failed"
            if preview_file is not None:
                try:
                    if preview_file.exists():
                        preview_file.unlink()
                except Exception:
                    logger.exception(
                        "template.compile.preview_cleanup_failed template_id=%s path=%s",
                        template_id_value,
                        str(preview_file),
                    )
            return self._repo.update(
                template_id_value,
                status=TemplateStatus.FAILED.value,
                compile_error=compile_error,
                compiled_at=utc_now_iso(),
                section_plan=[],
                style_map=StyleMap().model_dump(),
                sheet_map={},
                validation_status="invalid",
                validation_errors=[
                    {
                        "code": "template_compile_failed",
                        "message": compile_error,
                        "level": "error",
                    }
                ],
                validation_warnings=[],
                preview_path=None,
                preview_html=None,
                fidelity_integrity_issues=[],
                fidelity_integrity_summary={},
                fidelity_integrity_checked_at=None,
                resolved_section_bindings={},
            )

    def list_all(self) -> list[TemplateRecord]:
        return self._repo.list_all()

    def get_or_raise(self, template_id_value: str) -> TemplateRecord:
        return self._repo.get_or_raise(template_id_value)

    def get_file_path(self, template_id_value: str) -> Path:
        record = self.get_or_raise(template_id_value)
        if not record.file_path:
            raise TemplateException(f"Template has no file path: {template_id_value}")
        return self._repo._path / record.file_path

    def get_preview_file_path(self, template_id_value: str) -> Path:
        record = self.get_or_raise(template_id_value)
        if not record.preview_path:
            raise TemplateException(f"Template has no preview path: {template_id_value}")
        return self._repo._path / record.preview_path

    def get_preview_html(self, template_id_value: str) -> str:
        record = self.get_or_raise(template_id_value)
        if record.preview_html:
            return record.preview_html

        preview = record.preview_path or f"Template {template_id_value} preview is not generated yet."
        return f"<div><strong>{record.filename}</strong><p>{preview}</p></div>"

    def get_placeholder_schema(self, template_id_value: str) -> dict[str, object]:
        record = self.get_or_raise(template_id_value)
        return dict(record.placeholder_schema or {})

    def delete(self, template_id_value: str) -> bool:
        record = self.get_or_raise(template_id_value)

        # Delete both binary and preview artifacts if present
        for relative_path in [record.file_path, record.preview_path]:
            if not relative_path:
                continue

            path = self._repo._path / relative_path
            if path.exists():
                path.unlink()
            else:
                logger.warning(
                    "template.file.missing template_id=%s file_path=%s",
                    template_id_value,
                    str(path),
                )

        return self._repo.delete(template_id_value)

    def _cleanup_failed_template(self, *, record: TemplateRecord, preview_file: Path | None) -> None:
        """
        Delete failed template artifacts and remove the record from the repository.
        """
        paths_to_delete: list[Path] = []

        if record.file_path:
            paths_to_delete.append(self._repo._path / record.file_path)

        if record.preview_path:
            paths_to_delete.append(self._repo._path / record.preview_path)

        if preview_file is not None:
            paths_to_delete.append(preview_file)

        seen: set[Path] = set()
        for path in paths_to_delete:
            if path in seen:
                continue
            seen.add(path)

            try:
                if path.exists():
                    path.unlink()
                    logger.info(
                        "template.cleanup.file.deleted template_id=%s path=%s",
                        record.template_id,
                        str(path),
                    )
            except Exception:
                logger.exception(
                    "template.cleanup.file.delete_failed template_id=%s path=%s",
                    record.template_id,
                    str(path),
                )

        try:
            self._repo.delete(record.template_id)
            logger.info("template.cleanup.record.deleted template_id=%s", record.template_id)
        except Exception:
            logger.exception(
                "template.cleanup.record.delete_failed template_id=%s",
                record.template_id,
            )
