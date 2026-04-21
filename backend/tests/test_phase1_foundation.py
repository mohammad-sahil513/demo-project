from __future__ import annotations

import re

from core.config import ensure_storage_dirs, settings
from core.constants import inbuilt_template_id_for
from core.ids import document_id, output_id, template_id, utc_now_iso, workflow_id
from repositories.document_models import DocumentRecord
from repositories.document_repo import DocumentRepository
from repositories.output_models import OutputRecord
from repositories.output_repo import OutputRepository
from repositories.template_models import TemplateRecord
from repositories.template_repo import TemplateRepository
from repositories.workflow_models import WorkflowRecord
from repositories.workflow_repo import WorkflowRepository


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
