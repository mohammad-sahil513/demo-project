from __future__ import annotations

import asyncio

import pytest

from core.exceptions import ValidationException
from core.ids import utc_now_iso
from repositories.document_models import DocumentRecord
from repositories.document_repo import DocumentRepository
from repositories.template_models import TemplateRecord
from repositories.template_repo import TemplateRepository
from repositories.workflow_models import WorkflowRecord
from repositories.workflow_repo import WorkflowRepository
from services.document_service import DocumentService
from services.event_service import EventService
from services.workflow_service import WorkflowService


def test_document_delete_blocked_while_workflow_running(tmp_path) -> None:
    now = utc_now_iso()
    document_repo = DocumentRepository(tmp_path / "documents")
    workflow_repo = WorkflowRepository(tmp_path / "workflows")

    record = DocumentRecord(
        document_id="doc-guard",
        filename="guard.pdf",
        content_type="application/pdf",
        size_bytes=10,
        file_path="doc-guard.bin",
        created_at=now,
        updated_at=now,
    )
    document_repo.save(record)
    (tmp_path / "documents" / "doc-guard.bin").write_bytes(b"test")
    workflow_repo.save(
        WorkflowRecord(
            workflow_run_id="wf-running",
            document_id="doc-guard",
            template_id="tpl-guard",
            doc_type="PDD",
            status="RUNNING",
            current_phase="INPUT_PREPARATION",
            overall_progress_percent=1.0,
            current_step_label="Running",
            output_id=None,
            created_at=now,
            updated_at=now,
        ),
    )

    service = DocumentService(document_repo, workflow_repo=workflow_repo)
    with pytest.raises(ValidationException):
        service.delete("doc-guard")


def test_workflow_service_rejects_template_doc_type_mismatch(tmp_path) -> None:
    now = utc_now_iso()
    document_repo = DocumentRepository(tmp_path / "documents")
    template_repo = TemplateRepository(tmp_path / "templates")
    workflow_repo = WorkflowRepository(tmp_path / "workflows")

    document_repo.save(
        DocumentRecord(
            document_id="doc-123",
            filename="sample.pdf",
            content_type="application/pdf",
            size_bytes=4,
            file_path="doc-123.bin",
            created_at=now,
            updated_at=now,
        ),
    )
    template_repo.save(
        TemplateRecord(
            template_id="tpl-123",
            filename="template.docx",
            template_type="UAT",
            status="READY",
            created_at=now,
            updated_at=now,
        ),
    )

    service = WorkflowService(workflow_repo, document_repo=document_repo, template_repo=template_repo)
    with pytest.raises(ValidationException):
        service.create(document_id="doc-123", template_id="tpl-123", doc_type="PDD")


def test_event_service_fanout_for_multiple_subscribers() -> None:
    async def _run() -> None:
        events = EventService()
        queue_a = events.subscribe("wf-1")
        queue_b = events.subscribe("wf-1")

        await events.emit("wf-1", "phase.started", {"phase": "INPUT_PREPARATION"})
        payload_a = await asyncio.wait_for(queue_a.get(), timeout=1.0)
        payload_b = await asyncio.wait_for(queue_b.get(), timeout=1.0)

        assert payload_a["type"] == "phase.started"
        assert payload_b["type"] == "phase.started"
        assert payload_a["phase"] == "INPUT_PREPARATION"
        assert payload_b["phase"] == "INPUT_PREPARATION"

    asyncio.run(_run())
