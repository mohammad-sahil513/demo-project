"""Workflow JSON repository."""

from __future__ import annotations

from pathlib import Path

from repositories.base import BaseJsonRepository
from repositories.workflow_models import WorkflowRecord


class WorkflowRepository(BaseJsonRepository[WorkflowRecord]):
    def __init__(self, storage_path: Path) -> None:
        super().__init__(storage_path=storage_path, model_class=WorkflowRecord)

    def _id_field(self) -> str:
        return "workflow_run_id"

    def get_or_raise(self, workflow_run_id: str, resource_name: str = "Workflow") -> WorkflowRecord:
        return super().get_or_raise(workflow_run_id, resource_name)

    def update(self, workflow_run_id: str, **fields: object) -> WorkflowRecord:
        return super().update(workflow_run_id, resource_name="Workflow", **fields)

    def list_by_document(self, document_id: str) -> list[WorkflowRecord]:
        return [w for w in self.list_all() if w.document_id == document_id]
