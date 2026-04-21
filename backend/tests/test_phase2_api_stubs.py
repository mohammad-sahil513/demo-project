from __future__ import annotations

import time
from io import BytesIO
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient

from core.config import ensure_storage_dirs, settings
from main import app


def _minimal_docx_bytes() -> bytes:
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>1. Overview</w:t></w:r></w:p>'
        "</w:body>"
        "</w:document>"
    )
    stream = BytesIO()
    with ZipFile(stream, "w") as archive:
        archive.writestr("word/document.xml", document_xml)
    return stream.getvalue()


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "storage_root", tmp_path / "storage")
    ensure_storage_dirs()
    yield


def test_health_endpoint_contract() -> None:
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"


def test_ready_endpoint_contract() -> None:
    client = TestClient(app)
    response = client.get("/api/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "azure_openai_configured" in body["data"]
    assert "azure_search_configured" in body["data"]
    assert "azure_doc_intelligence_configured" in body["data"]


def test_document_template_workflow_lifecycle() -> None:
    client = TestClient(app)

    doc_upload = client.post(
        "/api/documents/upload",
        files={"file": ("sample.pdf", b"%PDF-1.4 test", "application/pdf")},
    )
    assert doc_upload.status_code == 201
    document = doc_upload.json()["data"]
    document_id = document["document_id"]

    list_docs = client.get("/api/documents")
    assert list_docs.status_code == 200
    assert list_docs.json()["data"]["total"] == 1

    tpl_upload = client.post(
        "/api/templates/upload",
        files={
            "file": (
                "template.docx",
                _minimal_docx_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        },
        data={"template_type": "PDD"},
    )
    assert tpl_upload.status_code == 201
    template_id = tpl_upload.json()["data"]["template_id"]

    compile_status = client.get(f"/api/templates/{template_id}/compile-status")
    assert compile_status.status_code == 200
    assert compile_status.json()["data"]["status"] in {"COMPILING", "READY"}

    workflow_create = client.post(
        "/api/workflow-runs",
        json={"document_id": document_id, "template_id": template_id, "start_immediately": True},
    )
    assert workflow_create.status_code == 201
    workflow_id = workflow_create.json()["data"]["workflow_run_id"]

    final_status = None
    for _ in range(20):
        status_response = client.get(f"/api/workflow-runs/{workflow_id}/status")
        assert status_response.status_code == 200
        final_status = status_response.json()["data"]["status"]
        if final_status in {"COMPLETED", "FAILED"}:
            break
        time.sleep(0.05)

    assert final_status == "COMPLETED"


def test_template_compile_status_transitions_ready_and_failed() -> None:
    client = TestClient(app)

    ready_upload = client.post(
        "/api/templates/upload",
        files={
            "file": (
                "ready.docx",
                _minimal_docx_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        },
        data={"template_type": "PDD"},
    )
    assert ready_upload.status_code == 201
    ready_template_id = ready_upload.json()["data"]["template_id"]

    failed_upload = client.post(
        "/api/templates/upload",
        files={
            "file": (
                "failed.docx",
                b"definitely-not-a-docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        },
        data={"template_type": "PDD"},
    )
    assert failed_upload.status_code == 201
    failed_template_id = failed_upload.json()["data"]["template_id"]

    ready_status = "COMPILING"
    failed_status = "COMPILING"
    for _ in range(40):
        ready_status = client.get(f"/api/templates/{ready_template_id}/compile-status").json()["data"]["status"]
        failed_status = client.get(f"/api/templates/{failed_template_id}/compile-status").json()["data"]["status"]
        if ready_status in {"READY", "FAILED"} and failed_status in {"READY", "FAILED"}:
            break
        time.sleep(0.05)

    assert ready_status == "READY"
    assert failed_status == "FAILED"
