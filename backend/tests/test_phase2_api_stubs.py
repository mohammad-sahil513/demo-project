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
    assert "critical_checks_passed" in body["data"]
    assert "failed_checks" in body["data"]


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

    doc_cost = client.get(f"/api/documents/{document_id}/cost")
    assert doc_cost.status_code == 200
    cost_payload = doc_cost.json()["data"]
    assert cost_payload["document_id"] == document_id
    assert cost_payload["workflow_count"] >= 1
    assert "total_cost_usd" in cost_payload
    assert "all_status_totals" in cost_payload
    assert "total_cost_usd" in cost_payload["all_status_totals"]

    doc_details = client.get(f"/api/documents/{document_id}")
    assert doc_details.status_code == 200
    detail_payload = doc_details.json()["data"]
    assert "cost_summary" in detail_payload
    assert detail_payload["cost_summary"]["document_id"] == document_id
    assert "all_status_totals" in detail_payload["cost_summary"]


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


def test_template_recompile_endpoint_queues_compile() -> None:
    client = TestClient(app)

    upload = client.post(
        "/api/templates/upload",
        files={
            "file": (
                "recompile.docx",
                _minimal_docx_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        },
        data={"template_type": "PDD"},
    )
    assert upload.status_code == 201
    template_id = upload.json()["data"]["template_id"]

    for _ in range(40):
        st = client.get(f"/api/templates/{template_id}/compile-status").json()["data"]["status"]
        if st in {"READY", "FAILED"}:
            break
        time.sleep(0.05)

    rec = client.post(f"/api/templates/{template_id}/recompile")
    assert rec.status_code == 200
    body = rec.json()
    assert body["success"] is True
    assert body["data"]["status"] == "COMPILING"
    assert "export_path_hint" in body["data"]


def test_template_upload_contract_rejects_mismatched_extension() -> None:
    client = TestClient(app)

    uat_bad = client.post(
        "/api/templates/upload",
        files={
            "file": (
                "uat-template.docx",
                _minimal_docx_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        },
        data={"template_type": "UAT"},
    )
    assert 400 <= uat_bad.status_code < 500
    assert ".xlsx" in str(uat_bad.json())

    pdd_bad = client.post(
        "/api/templates/upload",
        files={"file": ("pdd-template.xlsx", b"not-relevant", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"template_type": "PDD"},
    )
    assert 400 <= pdd_bad.status_code < 500
    assert ".docx" in str(pdd_bad.json())


def test_template_validate_endpoint_recomputes_and_persists() -> None:
    client = TestClient(app)

    upload = client.post(
        "/api/templates/upload",
        files={
            "file": (
                "validate.docx",
                _minimal_docx_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        },
        data={"template_type": "PDD"},
    )
    assert upload.status_code == 201
    template_id = upload.json()["data"]["template_id"]

    # Wait until compile persists initial template metadata.
    for _ in range(40):
        status = client.get(f"/api/templates/{template_id}/compile-status")
        assert status.status_code == 200
        if status.json()["data"]["status"] in {"READY", "FAILED"}:
            break
        time.sleep(0.05)

    # Force stale persisted validation state via repository file update.
    template_get = client.get(f"/api/templates/{template_id}")
    assert template_get.status_code in {200, 202}
    current_data = template_get.json()["data"]

    from repositories.template_repo import TemplateRepository

    repo = TemplateRepository(settings.templates_path)
    repo.update(
        template_id,
        validation_status="invalid",
        validation_errors=[{"code": "stale", "message": "stale"}],
        validation_warnings=[],
    )

    validate = client.post(f"/api/templates/{template_id}/validate")
    assert validate.status_code == 200
    validated = validate.json()["data"]
    assert validated["template_id"] == template_id
    assert validated["validation_status"] in {"valid", "warning", "invalid"}
    assert validated["validation_status"] != "invalid" or not any(
        e.get("code") == "stale" for e in validated.get("errors", [])
    )
    assert "placeholder_schema" in validated
    assert "schema_version" in validated

    # Verify persistence was refreshed.
    schema_resp = client.get(f"/api/templates/{template_id}/schema")
    assert schema_resp.status_code == 200
    schema_data = schema_resp.json()["data"]
    assert schema_data["validation_status"] == validated["validation_status"]


def test_template_fidelity_report_includes_integrity_summary() -> None:
    client = TestClient(app)
    upload = client.post(
        "/api/templates/upload",
        files={
            "file": (
                "fidelity.docx",
                _minimal_docx_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        },
        data={"template_type": "PDD"},
    )
    assert upload.status_code == 201
    template_id = upload.json()["data"]["template_id"]
    for _ in range(40):
        st = client.get(f"/api/templates/{template_id}/compile-status").json()["data"]["status"]
        if st in {"READY", "FAILED"}:
            break
        time.sleep(0.05)

    rep = client.get(f"/api/templates/{template_id}/fidelity-report")
    assert rep.status_code == 200
    data = rep.json()["data"]
    assert data["template_id"] == template_id
    assert "integrity_summary" in data
    assert "integrity_issues" in data
    assert "integrity_checked_at" in data
    summary = data["integrity_summary"]
    assert summary["overall"] in {"pass", "fail", "unknown", "not_applicable"}

