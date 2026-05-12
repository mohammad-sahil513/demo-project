"""In-memory event broker for Server-Sent Events (SSE) subscribers.

The workflow executor emits events at every phase boundary (e.g.
``phase.started``, ``phase.completed``, ``workflow.completed``); the
frontend subscribes to the SSE endpoint, which reads from one
:class:`asyncio.Queue` per subscriber.

Design choices:

- **Per-workflow fanout** — each ``workflow_run_id`` has its own list of
  subscriber queues. Most workflows have a single subscriber (the
  Progress page in the UI), but multiple tabs subscribe independently.
- **Bounded queues** — ``maxsize=200`` events. A queue that fills up
  is treated as a slow consumer; new events are dropped rather than
  blocking the producer. The workflow record on disk is still the
  authoritative state.
- **In-memory only** — surviving process restarts is not a requirement
  (the workflow executor is also in-memory). After a restart the
  frontend transparently reconnects and reads the persisted workflow
  state.
"""

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
