from __future__ import annotations

import re
import logging
import pytest

from core.config import ensure_storage_dirs, settings
from core.constants import inbuilt_template_id_for
from core.ids import document_id, output_id, template_id, utc_now_iso, workflow_id
from core.logging import _PhaseOnlyConsoleFilter, configure_logging
from repositories.document_models import DocumentRecord
from repositories.document_repo import DocumentRepository
from repositories.output_models import OutputRecord
from repositories.output_repo import OutputRepository
from repositories.template_models import TemplateRecord
from repositories.template_repo import TemplateRepository
from repositories.workflow_models import WorkflowRecord
from repositories.workflow_repo import WorkflowRepository
from services.document_service import DocumentService


def test_id_generation_and_inbuilt_template_mapping() -> None:
    assert re.fullmatch(r"wf-[0-9a-f]{12}", workflow_id())
    assert re.fullmatch(r"doc-[0-9a-f]{12}", document_id())
    assert re.fullmatch(r"tpl-[0-9a-f]{12}", template_id())
    assert re.fullmatch(r"out-[0-9a-f]{12}", output_id())
    assert inbuilt_template_id_for("PDD") == "tpl-inbuilt-pdd"


def test_storage_paths_and_directory_creation() -> None:
    ensure_storage_dirs()
    assert settings.documents_path.exists()
    assert settings.templates_path.exists()
    assert settings.workflows_path.exists()
    assert settings.outputs_path.exists()
    assert settings.diagrams_path.exists()
    assert settings.logs_path.exists()


def test_repository_crud_cycle_local(tmp_path) -> None:
    now = utc_now_iso()

    documents = DocumentRepository(tmp_path / "documents")
    templates = TemplateRepository(tmp_path / "templates")
    workflows = WorkflowRepository(tmp_path / "workflows")
    outputs = OutputRepository(tmp_path / "outputs")

    doc = DocumentRecord(
        document_id="doc-test",
        filename="sample.pdf",
        content_type="application/pdf",
        size_bytes=10,
        file_path="doc-test.bin",
        created_at=now,
        updated_at=now,
    )
    documents.save(doc)
    assert documents.get("doc-test") is not None
    documents.update("doc-test", filename="sample-2.pdf")
    assert documents.get("doc-test").filename == "sample-2.pdf"

    tpl = TemplateRecord(
        template_id="tpl-test",
        filename="template.docx",
        template_type="PDD",
        created_at=now,
        updated_at=now,
    )
    templates.save(tpl)
    assert len(templates.list_all()) == 1

    wf = WorkflowRecord(
        workflow_run_id="wf-test",
        document_id="doc-test",
        template_id="tpl-test",
        doc_type="PDD",
        created_at=now,
        updated_at=now,
    )
    workflows.save(wf)
    assert len(workflows.list_by_document("doc-test")) == 1

    out = OutputRecord(
        output_id="out-test",
        workflow_run_id="wf-test",
        document_id="doc-test",
        doc_type="PDD",
        output_format="DOCX",
        status="READY",
        file_path="out-test.docx",
        filename="out-test.docx",
        size_bytes=1024,
        created_at=now,
        updated_at=now,
    )
    outputs.save(out)
    assert outputs.get("out-test") is not None


def test_configure_logging_uses_console_level(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "log_level", "INFO")
    monkeypatch.setattr(settings, "log_console_level", "ERROR")
    configure_logging()
    root = logging.getLogger()
    assert root.handlers
    assert root.handlers[0].level == logging.ERROR


def test_phase_only_console_filter_allows_phase_logs_only() -> None:
    f = _PhaseOnlyConsoleFilter()
    allowed = logging.LogRecord(
        name="services.workflow_executor",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="phase.started workflow_run_id=wf-1 phase=INGESTION",
        args=(),
        exc_info=None,
    )
    blocked = logging.LogRecord(
        name="api.routes.documents",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="documents.upload.completed document_id=doc-1",
        args=(),
        exc_info=None,
    )
    blocked_attempt = logging.LogRecord(
        name="services.workflow_executor",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="phase.attempt workflow_run_id=wf-1 phase=INGESTION attempt=1",
        args=(),
        exc_info=None,
    )
    allowed_failure = logging.LogRecord(
        name="services.workflow_executor",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="workflow.failed workflow_run_id=wf-1 error=boom",
        args=(),
        exc_info=None,
    )
    assert f.filter(allowed) is True
    assert f.filter(blocked) is False
    assert f.filter(blocked_attempt) is False
    assert f.filter(allowed_failure) is True


def test_document_cost_summary_defaults_completed_and_includes_all_status(tmp_path) -> None:
    now = utc_now_iso()
    documents = DocumentRepository(tmp_path / "documents")
    workflows = WorkflowRepository(tmp_path / "workflows")
    service = DocumentService(documents, workflow_repo=workflows)
    documents.save(
        DocumentRecord(
            document_id="doc-cost",
            filename="sample.pdf",
            content_type="application/pdf",
            size_bytes=10,
            file_path="doc-cost.bin",
            created_at=now,
            updated_at=now,
        ),
    )
    workflows.save(
        WorkflowRecord(
            workflow_run_id="wf-ok",
            document_id="doc-cost",
            template_id="tpl-inbuilt-pdd",
            doc_type="PDD",
            status="COMPLETED",
            observability_summary={
                "llm_cost_usd": 1.0,
                "embedding_cost_usd": 2.0,
                "document_intelligence_cost_usd": 3.0,
            },
            created_at=now,
            updated_at=now,
        ),
    )
    workflows.save(
        WorkflowRecord(
            workflow_run_id="wf-fail",
            document_id="doc-cost",
            template_id="tpl-inbuilt-pdd",
            doc_type="PDD",
            status="FAILED",
            observability_summary={
                "llm_cost_usd": 10.0,
                "embedding_cost_usd": 20.0,
                "document_intelligence_cost_usd": 30.0,
            },
            created_at=now,
            updated_at=now,
        ),
    )
    data = service.cost_summary("doc-cost")
    assert data["workflow_count"] == 2
    assert data["completed_workflow_count"] == 1
    assert data["total_cost_usd"] == 6.0
    all_status = data["all_status_totals"]
    assert isinstance(all_status, dict)
    assert all_status["total_cost_usd"] == 66.0
