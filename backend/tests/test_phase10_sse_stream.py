from __future__ import annotations

import asyncio
import threading

import pytest
from fastapi.testclient import TestClient

from api.deps import event_service_singleton
from main import app


@pytest.fixture
def api_client() -> TestClient:
    with TestClient(app) as client:
        yield client


def test_workflow_sse_stream_delivers_json_events_and_completed(api_client: TestClient) -> None:
    wf_id = "wf-sse-contract-01"

    def emit_chain() -> None:
        async def go() -> None:
            await asyncio.sleep(0.05)
            await event_service_singleton.emit(wf_id, "phase.started", {"phase": "INGESTION"})
            await event_service_singleton.emit(
                wf_id,
                "workflow.completed",
                {"output_id": None, "total_cost_usd": 0.0},
            )

        asyncio.run(go())

    thread = threading.Thread(target=emit_chain)
    thread.start()
    collected = b""
    try:
        with api_client.stream("GET", f"/api/workflow-runs/{wf_id}/events") as response:
            assert response.status_code == 200
            for chunk in response.iter_bytes(chunk_size=2048):
                collected += chunk
                if b"workflow.completed" in collected and b"phase.started" in collected:
                    break
    finally:
        thread.join(timeout=10)

    text = collected.decode("utf-8", errors="replace")
    assert "phase.started" in text
    assert "workflow.completed" in text
    assert "data:" in text
