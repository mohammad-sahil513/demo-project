"""Background task dispatcher used by API dependencies."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import BackgroundTasks

from core.logging import get_logger

logger = get_logger(__name__)


class TaskDispatcher:
    def dispatch(
        self,
        background_tasks: BackgroundTasks | None,
        fn: Callable[..., Awaitable[Any]],
        *args: Any,
    ) -> None:
        if background_tasks is not None:
            background_tasks.add_task(fn, *args)
            return

        try:
            asyncio.get_running_loop().create_task(fn(*args))
        except RuntimeError:
            logger.exception("No running event loop for background dispatch")
