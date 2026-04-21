"""Production hosting helpers: storage health and in-process task recovery."""

from __future__ import annotations

from pathlib import Path

from core.config import Settings
from core.constants import WorkflowStatus
from core.ids import utc_now_iso
from core.logging import get_logger
from repositories.workflow_repo import WorkflowRepository

logger = get_logger(__name__)

_RESTART_MSG = (
    "Workflow interrupted: the server restarted or the worker process ended before completion. "
    "Start a new workflow run if you still need this output."
)


def verify_storage_writable(storage_root: Path) -> bool:
    """Return True if ``storage_root`` can create and delete a small probe file."""
    storage_root.mkdir(parents=True, exist_ok=True)
    probe = storage_root / ".storage_write_probe"
    try:
        probe.write_bytes(b"ok")
        return True
    except OSError as exc:
        logger.error(
            "storage_not_writable path=%s detail=%s",
            storage_root,
            exc,
        )
        return False
    finally:
        try:
            if probe.is_file():
                probe.unlink()
        except OSError:
            pass


def reconcile_interrupted_workflows(repo: WorkflowRepository) -> int:
    """
    Mark ``RUNNING`` workflows as ``FAILED`` after a process restart.

    Background work is dispatched with FastAPI BackgroundTasks; it does not survive
    restarts. This avoids workflows stuck in RUNNING forever.
    """
    n = 0
    for w in repo.list_all():
        if w.status != WorkflowStatus.RUNNING.value:
            continue
        err = {
            "code": "SERVER_RESTART",
            "detail": _RESTART_MSG,
            "at": utc_now_iso(),
        }
        errors = [*w.errors, err]
        repo.update(
            w.workflow_run_id,
            status=WorkflowStatus.FAILED.value,
            current_phase=w.current_phase,
            current_step_label=_RESTART_MSG,
            errors=errors,
        )
        n += 1
        logger.warning(
            "workflow_marked_failed_after_restart workflow_run_id=%s",
            w.workflow_run_id,
        )
    return n


def run_hosting_startup(settings: Settings) -> None:
    """Storage probe + orphaned workflow reconciliation (call from app lifespan)."""
    if not verify_storage_writable(settings.storage_root):
        logger.error(
            "Set STORAGE_ROOT to a persistent, writable directory (mounted volume in Azure "
            "Container Apps/App Service, Kubernetes PVC, etc.)."
        )
    reconcile_interrupted_workflows(WorkflowRepository(settings.workflows_path))
