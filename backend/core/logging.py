"""Logging helpers for local development and workflow files."""

from __future__ import annotations

import logging
from pathlib import Path

from core.config import settings


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def get_workflow_log_path(workflow_run_id: str) -> Path:
    return settings.logs_path / f"{workflow_run_id}.log"


def get_workflow_observability_path(workflow_run_id: str) -> Path:
    return settings.logs_path / f"{workflow_run_id}_observability.jsonl"
