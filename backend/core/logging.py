"""Logging helpers for local development and per-workflow file sinks.

Two complementary logging streams live here:

1. **Process-wide standard logging** configured by :func:`configure_logging`.
   It routes to a single ``StreamHandler`` (stderr) with an optional filter
   that only surfaces workflow phase progression to the console, keeping the
   developer terminal readable while detailed logs flow to per-run files.

2. **Per-workflow file sinks** under ``storage/logs/``. These are used for
   long-running async workflow observability:

   - ``<workflow_run_id>.log``                    plain-text breadcrumbs
   - ``<workflow_run_id>_cost.jsonl``             one JSON object per LLM call
   - ``<workflow_run_id>_observability.jsonl``    structured event log

The cleanup helper at the bottom prunes files in ``storage/logs/`` older than
the configured retention window.
"""

from __future__ import annotations

import logging
from pathlib import Path
from datetime import datetime, timezone
import json
import time

from core.config import settings


def _resolve_log_level(name: str, default_level: int) -> int:
    """Convert a level name (``"DEBUG"``) to the numeric ``logging`` constant.

    Falls back to ``default_level`` rather than raising; misconfigured env
    vars should never prevent the service from starting.
    """
    return getattr(logging, (name or "").upper(), default_level)


class _PhaseOnlyConsoleFilter(logging.Filter):
    """Filter that only lets workflow phase / failure messages through.

    Enabled when ``LOG_CONSOLE_PHASE_ONLY=true`` (default). It keeps the
    terminal output focused on what a human reviewer cares about during a
    long run while detailed traces still land in the per-workflow file.
    """

    # Any record whose message contains one of these substrings is allowed
    # through. We use substring matching so we don't have to coordinate with
    # every emitter on a precise field-naming convention.
    _ALLOWED_PREFIXES = (
        "workflow.failed",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        if "phase.started" in msg or "phase.completed" in msg:
            return True
        return any(prefix in msg for prefix in self._ALLOWED_PREFIXES)


def configure_logging(level: int | None = None) -> None:
    """Wire up the root logger. Call once during application startup.

    The root logger's level is set to ``min(file, console)`` so neither
    handler is starved of records — the console handler then applies its
    own (typically higher) level and the optional phase-only filter.
    """
    resolved_level = _resolve_log_level(settings.log_level, logging.INFO)
    resolved_console_level = _resolve_log_level(settings.log_console_level, logging.WARNING)
    if level is not None:
        # Test/CLI override — lets a caller force a level without changing env.
        resolved_level = level
    root_logger = logging.getLogger()
    root_logger.setLevel(min(resolved_level, resolved_console_level))

    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(resolved_console_level)
    stream_handler.setFormatter(formatter)
    if settings.log_console_phase_only:
        stream_handler.addFilter(_PhaseOnlyConsoleFilter())

    # ``handlers.clear()`` is important under ``uvicorn --reload`` where
    # ``configure_logging`` may be called twice; otherwise we'd duplicate
    # every log line on each reload.
    root_logger.handlers.clear()
    root_logger.addHandler(stream_handler)


def verbose_logs_enabled() -> bool:
    """Whether modules should emit detailed per-step logs.

    Drives chatty ingestion / template logs that are useful when debugging a
    single document but noisy in normal operation.
    """
    return bool(settings.logs_verbose)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Use ``__name__`` to inherit module context."""
    return logging.getLogger(name)


def get_workflow_log_path(workflow_run_id: str) -> Path:
    """Path to the plain-text per-workflow log file."""
    return settings.logs_path / f"{workflow_run_id}.log"


def get_workflow_observability_path(workflow_run_id: str) -> Path:
    """Path to the JSONL structured event log for a workflow run."""
    return settings.logs_path / f"{workflow_run_id}_observability.jsonl"


def get_workflow_cost_log_path(workflow_run_id: str) -> Path:
    """Path to the JSONL LLM cost log for a workflow run."""
    return settings.logs_path / f"{workflow_run_id}_cost.jsonl"


def append_workflow_log(
    workflow_run_id: str,
    message: str,
    *,
    level: str = "INFO",
) -> None:
    """Append one line to the per-workflow log file under ``storage/logs``.

    Each line is prefixed with an ISO-8601 UTC timestamp and the level,
    matching the format the frontend log viewer parses on the
    ``/workflow-runs/{id}/log`` endpoint.
    """
    ts = datetime.now(timezone.utc).isoformat()
    path = get_workflow_log_path(workflow_run_id)
    # ``parents=True, exist_ok=True`` is idempotent — fine to call on every
    # append because the cost of stat-ing the directory is negligible.
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"{ts} {level.upper()} {message}\n")


def append_workflow_cost_log(workflow_run_id: str, payload: dict[str, object]) -> None:
    """Append one JSON line containing only cost-related observability.

    Uses ``ensure_ascii=True`` so non-ASCII content (model names, prompts)
    is escaped — guarantees the file is grep-able on any locale and avoids
    transport issues if the file is shipped to a log aggregator.
    """
    path = get_workflow_cost_log_path(workflow_run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": datetime.now(timezone.utc).isoformat(), **payload}
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=True) + "\n")


def cleanup_old_observability_logs(*, logs_path: Path, retention_days: int) -> int:
    """Delete old observability files from ``logs_path`` and return deleted count.

    The cutoff is computed against the file's ``mtime``; we only touch files
    whose names look like workflow logs to avoid clobbering anything an
    operator may have dropped in the directory. Errors on individual files
    are swallowed so a single locked file does not stop the sweep.
    """
    if retention_days < 0:
        # Negative retention disables the sweep entirely (escape hatch).
        return 0
    logs_path.mkdir(parents=True, exist_ok=True)
    cutoff = time.time() - (retention_days * 24 * 60 * 60)
    deleted = 0
    for path in logs_path.iterdir():
        if not path.is_file():
            continue
        name = path.name
        # Only consider files produced by this module's writers.
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
            # Locked / permission-denied — skip, log already happened upstream
            # via the caller in ``core.hosting.run_hosting_startup``.
            continue
    return deleted
