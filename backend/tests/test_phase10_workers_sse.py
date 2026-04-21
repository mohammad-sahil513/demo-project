from __future__ import annotations

import asyncio
import logging

import pytest

from workers.dispatcher import TaskDispatcher


def test_dispatcher_create_task_logs_background_task_failed(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.ERROR)
    dispatcher = TaskDispatcher()

    async def failing_task(resource_id: str) -> None:
        del resource_id
        raise ValueError("intentional failure")

    async def run_dispatch_and_wait() -> None:
        dispatcher.dispatch(None, failing_task, "wf-deadbeef")
        await asyncio.sleep(0.05)

    asyncio.run(run_dispatch_and_wait())

    assert any("background_task_failed" in r.getMessage() for r in caplog.records)
    assert any("failing_task" in r.getMessage() for r in caplog.records)
    assert any("wf-deadbeef" in r.getMessage() for r in caplog.records)
