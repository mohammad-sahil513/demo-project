"""Workflow service for workflow run persistence and guards."""

from __future__ import annotations

from core.constants import DocType, TemplateSource, TemplateStatus, WorkflowStatus
from core.exceptions import ValidationException
from core.ids import utc_now_iso, workflow_id
from modules.template.inbuilt.registry import doc_type_for_inbuilt_template, is_inbuilt_template_id
from repositories.document_models import DocumentRecord
from repositories.document_repo import DocumentRepository
from repositories.template_models import TemplateRecord
from repositories.template_repo import TemplateRepository
from repositories.workflow_models import WorkflowRecord
from repositories.workflow_repo import WorkflowRepository


class WorkflowService:
    def __init__(
        self,
        repo: WorkflowRepository,
        document_repo: DocumentRepository,
        template_repo: TemplateRepository,
    ) -> None:
        self._repo = repo
        self._document_repo = document_repo
        self._template_repo = template_repo

    def create(
        self,
        *,
        document_id: str,
        template_id: str,
        doc_type: str | None = None,
    ) -> WorkflowRecord:
        document = self.get_document(document_id)
        template = self.get_template(template_id)
        resolved_doc_type = doc_type or template.template_type
        if resolved_doc_type is None:
            raise ValidationException("doc_type is required when template has no template_type")

        try:
            normalized_doc_type = DocType(resolved_doc_type).value
        except ValueError as exc:
            raise ValidationException(f"Unsupported doc_type: {resolved_doc_type}") from exc

        if template.template_type and template.template_type != normalized_doc_type:
            raise ValidationException(
                f"Template/doc_type mismatch: template={template.template_type} doc_type={normalized_doc_type}",
            )

        now = utc_now_iso()
        record = WorkflowRecord(
            workflow_run_id=workflow_id(),
            document_id=document.document_id,
            template_id=template.template_id,
            doc_type=normalized_doc_type,
            status=WorkflowStatus.PENDING.value,
            current_phase=None,
            overall_progress_percent=0.0,
            current_step_label="Queued",
            output_id=None,
            created_at=now,
            updated_at=now,
        )
        return self._repo.save(record)

    def get(self, workflow_run_id: str) -> WorkflowRecord | None:
        return self._repo.get(workflow_run_id)

    def get_or_raise(self, workflow_run_id: str) -> WorkflowRecord:
        return self._repo.get_or_raise(workflow_run_id)

    def update(self, workflow_run_id: str, **fields: object) -> WorkflowRecord:
        return self._repo.update(workflow_run_id, **fields)

    def list_all(self) -> list[WorkflowRecord]:
        return self._repo.list_all()

    def get_document(self, document_id: str) -> DocumentRecord:
        return self._document_repo.get_or_raise(document_id)

    def get_template(self, template_id: str) -> TemplateRecord:
        record = self._template_repo.get(template_id)
        if record is not None:
            return record
        if is_inbuilt_template_id(template_id):
            doc_type = doc_type_for_inbuilt_template(template_id).value
            now = utc_now_iso()
            return TemplateRecord(
                template_id=template_id,
                filename=f"{doc_type.lower()}_inbuilt",
                template_type=doc_type,
                template_source=TemplateSource.INBUILT,
                status=TemplateStatus.READY.value,
                compiled_at=now,
                created_at=now,
                updated_at=now,
            )
        return self._template_repo.get_or_raise(template_id)
