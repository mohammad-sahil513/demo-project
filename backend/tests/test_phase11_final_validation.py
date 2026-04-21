"""Phase 11 — contracts aligned with docs/09 Phase 11 (Health & Config API portions)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from main import app


def test_phase11_health_returns_ok_envelope() -> None:
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"


def test_phase11_ready_exposes_all_integration_flags() -> None:
    """Mirrors fields returned by api/routes/health.py ready() for production readiness checks."""
    client = TestClient(app)
    response = client.get("/api/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] == "ready"
    assert "app" in data and isinstance(data["app"], str)
    assert "env" in data and isinstance(data["env"], str)
    assert "azure_openai_configured" in data
    assert "azure_search_configured" in data
    assert "azure_doc_intelligence_configured" in data
    assert "kroki_url" in data and isinstance(data["kroki_url"], str)
    assert "storage_root" in data and isinstance(data["storage_root"], str)
