"""Document service for BRD file metadata + storage operations."""

from __future__ import annotations

from pathlib import Path

from core.constants import WorkflowStatus
from core.ids import document_id, utc_now_iso
from core.logging import get_logger
from core.exceptions import ValidationException
from repositories.document_models import DocumentRecord
from repositories.document_repo import DocumentRepository
from repositories.workflow_repo import WorkflowRepository

logger = get_logger(__name__)


class DocumentService:
    def __init__(self, repo: DocumentRepository, workflow_repo: WorkflowRepository | None = None) -> None:
        self._repo = repo
        self._workflow_repo = workflow_repo

    def save_document(self, *, filename: str, content_type: str, payload: bytes) -> DocumentRecord:
        now = utc_now_iso()
        new_id = document_id()
        file_path = self._repo._path / f"{new_id}.bin"
        file_path.write_bytes(payload)

        record = DocumentRecord(
            document_id=new_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(payload),
            status="READY",
            file_path=file_path.name,
            created_at=now,
            updated_at=now,
        )
        self._repo.save(record)
        return record

    def list_all(self) -> list[DocumentRecord]:
        return self._repo.list_all()

    def get_or_raise(self, document_id: str) -> DocumentRecord:
        return self._repo.get_or_raise(document_id)

    def get_file_path(self, document_id: str) -> Path:
        record = self.get_or_raise(document_id)
        return self._repo._path / record.file_path

    def delete(self, document_id: str) -> bool:
        if self._workflow_repo is not None:
            workflows = self._workflow_repo.list_by_document(document_id)
            running = [item.workflow_run_id for item in workflows if item.status == WorkflowStatus.RUNNING]
            if running:
                raise ValidationException(
                    f"Cannot delete document {document_id}; workflow(s) still running: {', '.join(running)}",
                )

        record = self.get_or_raise(document_id)
        file_path = self._repo._path / record.file_path
        if file_path.exists():
            file_path.unlink()
        else:
            logger.warning("document.binary.missing document_id=%s file_path=%s", document_id, str(file_path))
        return self._repo.delete(document_id)

    def cost_summary(self, document_id: str) -> dict[str, object]:
        if self._workflow_repo is None:
            return {
                "document_id": document_id,
                "workflow_count": 0,
                "completed_workflow_count": 0,
                "total_cost_usd": 0.0,
                "llm_cost_usd": 0.0,
                "embedding_cost_usd": 0.0,
                "document_intelligence_cost_usd": 0.0,
                "all_status_totals": {
                    "total_cost_usd": 0.0,
                    "llm_cost_usd": 0.0,
                    "embedding_cost_usd": 0.0,
                    "document_intelligence_cost_usd": 0.0,
                },
            }
        workflows = self._workflow_repo.list_by_document(document_id)
        completed_llm_cost = 0.0
        completed_embedding_cost = 0.0
        completed_docint_cost = 0.0
        all_llm_cost = 0.0
        all_embedding_cost = 0.0
        all_docint_cost = 0.0
        completed = 0
        for wf in workflows:
            summary = dict(getattr(wf, "observability_summary", None) or {})
            llm = float(summary.get("llm_cost_usd", 0.0) or 0.0)
            emb = float(summary.get("embedding_cost_usd", 0.0) or 0.0)
            doc = float(summary.get("document_intelligence_cost_usd", 0.0) or 0.0)
            all_llm_cost += llm
            all_embedding_cost += emb
            all_docint_cost += doc
            if wf.status == WorkflowStatus.COMPLETED:
                completed += 1
                completed_llm_cost += llm
                completed_embedding_cost += emb
                completed_docint_cost += doc
        total = completed_llm_cost + completed_embedding_cost + completed_docint_cost
        return {
            "document_id": document_id,
            "workflow_count": len(workflows),
            "completed_workflow_count": completed,
            "total_cost_usd": total,
            "llm_cost_usd": completed_llm_cost,
            "embedding_cost_usd": completed_embedding_cost,
            "document_intelligence_cost_usd": completed_docint_cost,
            "all_status_totals": {
                "total_cost_usd": all_llm_cost + all_embedding_cost + all_docint_cost,
                "llm_cost_usd": all_llm_cost,
                "embedding_cost_usd": all_embedding_cost,
                "document_intelligence_cost_usd": all_docint_cost,
            },
        }
