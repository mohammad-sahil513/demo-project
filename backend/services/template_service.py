"""Template service for custom template files and compile lifecycle."""

from __future__ import annotations

from pathlib import Path

from core.constants import TemplateStatus
from core.ids import template_id, utc_now_iso
from core.logging import get_logger
from core.exceptions import TemplateException
from infrastructure.sk_adapter import AzureSKAdapter
from modules.template.classifier import TemplateClassifier
from modules.template.extractor import TemplateExtractor
from modules.template.models import StyleMap
from modules.template.planner import SectionPlanner
from modules.template.preview_generator import TemplatePreviewGenerator
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
        if record.status not in {TemplateStatus.COMPILING.value, TemplateStatus.PENDING.value}:
            return record
        try:
            file_path = self.get_file_path(template_id_value)
            suffix = Path(record.filename).suffix.lower()
            if suffix == ".docx":
                skeleton, style_map, sheet_map = self._extractor.extract_docx(file_path)
            elif suffix == ".xlsx":
                skeleton, style_map, sheet_map = self._extractor.extract_xlsx(file_path)
            else:
                raise TemplateException(f"Unsupported template file type: {record.filename}")

            classifications = await self._classifier.classify_sections(skeleton)
            section_plan = self._planner.build_from_skeleton_and_classifications(skeleton, classifications)

            preview_html: str | None = None
            preview_path: str | None = None
            if suffix == ".docx":
                preview_file = self._repo._path / f"{template_id_value}_preview.docx"
                self._preview_generator.build_preview_docx(
                    destination=preview_file,
                    title=skeleton.title,
                    section_plan=section_plan,
                )
                preview_path = preview_file.name
            else:
                preview_html = self._preview_generator.build_preview_html_from_xlsx(skeleton)

            return self._repo.update(
                template_id_value,
                status=TemplateStatus.READY.value,
                compiled_at=utc_now_iso(),
                compile_error=None,
                section_plan=[section.model_dump() for section in section_plan],
                style_map=style_map.model_dump(),
                sheet_map=sheet_map,
                preview_path=preview_path,
                preview_html=preview_html,
            )
        except Exception as exc:
            logger.exception("template_compile_failed template_id=%s", template_id_value)
            return self._repo.update(
                template_id_value,
                status=TemplateStatus.FAILED.value,
                compiled_at=None,
                compile_error=str(exc),
                section_plan=[],
                style_map=StyleMap().model_dump(),
                sheet_map={},
                preview_path=None,
                preview_html=None,
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

    def get_preview_html(self, template_id_value: str) -> str:
        record = self.get_or_raise(template_id_value)
        if record.preview_html:
            return record.preview_html
        preview = record.preview_path or f"Template {template_id_value} preview is not generated yet."
        return f"<div><strong>{record.filename}</strong><p>{preview}</p></div>"

    def delete(self, template_id_value: str) -> bool:
        record = self.get_or_raise(template_id_value)
        if record.file_path:
            file_path = self._repo._path / record.file_path
            if file_path.exists():
                file_path.unlink()
            else:
                logger.warning(
                    "template_binary_missing",
                    template_id=template_id_value,
                    file_path=str(file_path),
                )
        return self._repo.delete(template_id_value)
