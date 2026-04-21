"""In-memory event service for SSE subscribers."""

from __future__ import annotations

import asyncio

from core.ids import utc_now_iso


class EventService:
    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue[dict[str, object]]]] = {}

    def subscribe(self, workflow_run_id: str) -> asyncio.Queue[dict[str, object]]:
        queue: asyncio.Queue[dict[str, object]] = asyncio.Queue(maxsize=200)
        self._queues.setdefault(workflow_run_id, []).append(queue)
        return queue

    def unsubscribe(self, workflow_run_id: str, queue: asyncio.Queue[dict[str, object]]) -> None:
        queues = self._queues.get(workflow_run_id, [])
        if queue in queues:
            queues.remove(queue)
        if not queues and workflow_run_id in self._queues:
            del self._queues[workflow_run_id]

    async def emit(self, workflow_run_id: str, event_type: str, payload: dict[str, object] | None = None) -> None:
        event = {
            "type": event_type,
            "workflow_run_id": workflow_run_id,
            "timestamp": utc_now_iso(),
            **(payload or {}),
        }
        for queue in list(self._queues.get(workflow_run_id, [])):
            if queue.full():
                continue
            queue.put_nowait(event)

    def subscriber_count(self, workflow_run_id: str) -> int:
        return len(self._queues.get(workflow_run_id, []))
