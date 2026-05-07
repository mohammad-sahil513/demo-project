"""Logging helpers for local development and workflow files."""

from __future__ import annotations

import logging
from pathlib import Path
from datetime import datetime, timezone
import json
import time

from core.config import settings


def _resolve_log_level(name: str, default_level: int) -> int:
    return getattr(logging, (name or "").upper(), default_level)


class _PhaseOnlyConsoleFilter(logging.Filter):
    _ALLOWED_PREFIXES = (
        "workflow.failed",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        if "phase.started" in msg or "phase.completed" in msg:
            return True
        return any(prefix in msg for prefix in self._ALLOWED_PREFIXES)


def configure_logging(level: int | None = None) -> None:
    resolved_level = _resolve_log_level(settings.log_level, logging.INFO)
    resolved_console_level = _resolve_log_level(settings.log_console_level, logging.WARNING)
    if level is not None:
        resolved_level = level
    root_logger = logging.getLogger()
    root_logger.setLevel(min(resolved_level, resolved_console_level))

    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(resolved_console_level)
    stream_handler.setFormatter(formatter)
    if settings.log_console_phase_only:
        stream_handler.addFilter(_PhaseOnlyConsoleFilter())

    root_logger.handlers.clear()
    root_logger.addHandler(stream_handler)


def verbose_logs_enabled() -> bool:
    return bool(settings.logs_verbose)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def get_workflow_log_path(workflow_run_id: str) -> Path:
    return settings.logs_path / f"{workflow_run_id}.log"


def get_workflow_observability_path(workflow_run_id: str) -> Path:
    return settings.logs_path / f"{workflow_run_id}_observability.jsonl"


def get_workflow_cost_log_path(workflow_run_id: str) -> Path:
    return settings.logs_path / f"{workflow_run_id}_cost.jsonl"


def append_workflow_log(
    workflow_run_id: str,
    message: str,
    *,
    level: str = "INFO",
) -> None:
    """
    Append one line to the per-workflow log file under storage/logs.
    """
    ts = datetime.now(timezone.utc).isoformat()
    path = get_workflow_log_path(workflow_run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"{ts} {level.upper()} {message}\n")


def append_workflow_cost_log(workflow_run_id: str, payload: dict[str, object]) -> None:
    """
    Append one JSON line containing only cost-related observability.
    """
    path = get_workflow_cost_log_path(workflow_run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": datetime.now(timezone.utc).isoformat(), **payload}
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=True) + "\n")


def cleanup_old_observability_logs(*, logs_path: Path, retention_days: int) -> int:
    """
    Delete old observability files from logs_path and return deleted count.
    """
    if retention_days < 0:
        return 0
    logs_path.mkdir(parents=True, exist_ok=True)
    cutoff = time.time() - (retention_days * 24 * 60 * 60)
    deleted = 0
    for path in logs_path.iterdir():
        if not path.is_file():
            continue
        name = path.name
        is_target = (
            name.endswith(".log")
            or name.endswith("_cost.jsonl")
            or name.endswith("_observability.jsonl")
        )
        if not is_target:
            continue
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
                deleted += 1
        except OSError:
            continue
    return deleted
