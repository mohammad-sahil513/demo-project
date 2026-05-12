"""Server-Sent Events stream for workflow progress.

``GET /api/workflow-runs/{workflow_run_id}/events``

The frontend Progress page opens an ``EventSource`` against this URL to
watch phase transitions in real time. Behavior:

- Subscribes to :class:`EventService` and yields each event as an SSE
  ``data:`` line containing the JSON payload.
- Sends a ``: heartbeat`` comment every 30 seconds so HTTP intermediaries
  (load balancers, proxies) do not idle the connection.
- Closes the stream automatically when a terminal event arrives —
  ``workflow.completed`` or ``workflow.failed``.
- Always unsubscribes in the ``finally`` block so a dropped client does
  not leak a queue.

Response headers disable buffering and caching to keep events flowing as
soon as the executor produces them.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.deps import get_event_service
from core.logging import get_logger
from services.event_service import EventService

router = APIRouter()
logger = get_logger(__name__)


async def _event_stream(
    workflow_run_id: str,
    event_service: EventService,
) -> AsyncGenerator[str, None]:
    logger.info("events.stream.started workflow_run_id=%s", workflow_run_id)
    queue = event_service.subscribe(workflow_run_id)
    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                logger.info(
                    "events.stream.event workflow_run_id=%s event_type=%s",
                    workflow_run_id,
                    event.get("type"),
                )
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") in {"workflow.completed", "workflow.failed"}:
                    logger.info("events.stream.terminal workflow_run_id=%s", workflow_run_id)
                    break
            except asyncio.TimeoutError:
                logger.info("events.stream.heartbeat workflow_run_id=%s", workflow_run_id)
                yield ": heartbeat\n\n"
    finally:
        event_service.unsubscribe(workflow_run_id, queue)
        logger.info("events.stream.completed workflow_run_id=%s", workflow_run_id)


@router.get("/{workflow_run_id}/events")
async def stream_workflow_events(
    workflow_run_id: str,
    event_service: EventService = Depends(get_event_service),
) -> StreamingResponse:
    logger.info("events.route.started workflow_run_id=%s", workflow_run_id)
    return StreamingResponse(
        _event_stream(workflow_run_id, event_service),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
