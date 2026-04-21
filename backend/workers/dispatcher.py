"""Background task dispatcher used by API dependencies."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import BackgroundTasks

from core.logging import get_logger

logger = get_logger(__name__)


async def _run_guarded(
    fn: Callable[..., Awaitable[Any]],
    args: tuple[Any, ...],
) -> None:
    try:
        await fn(*args)
    except Exception:
        resource_id: str | None = None
        if len(args) == 1 and isinstance(args[0], str):
            resource_id = args[0]
        logger.exception(
            "background_task_failed task=%s resource_id=%s",
            getattr(fn, "__name__", str(fn)),
            resource_id,
        )


class TaskDispatcher:
    def dispatch(
        self,
        background_tasks: BackgroundTasks | None,
        fn: Callable[..., Awaitable[Any]],
        *args: Any,
    ) -> None:
        bound = (fn, tuple(args))

        if background_tasks is not None:
            background_tasks.add_task(_run_guarded, bound[0], bound[1])
            return

        try:
            asyncio.get_running_loop().create_task(_run_guarded(bound[0], bound[1]))
        except RuntimeError:
            logger.exception("No running event loop for background dispatch")
