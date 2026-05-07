"""Production hosting helpers: storage health and in-process task recovery."""

from __future__ import annotations

from pathlib import Path

from core.config import Settings
from core.constants import WorkflowStatus
from core.ids import utc_now_iso
from core.logging import cleanup_old_observability_logs, get_logger
from repositories.workflow_repo import WorkflowRepository

logger = get_logger(__name__)

_RESTART_MSG = (
    "Workflow interrupted: the server restarted or the worker process ended before completion. "
    "Start a new workflow run if you still need this output."
)


def strict_policy_violations(settings: Settings) -> list[str]:
    """
    Return a list of strict-mode policy violations for staging/production.
    """
    violations: list[str] = []
    required_true = {
        "template_docx_placeholder_native_enabled": settings.template_docx_placeholder_native_enabled,
        "template_section_binding_strict": settings.template_section_binding_strict,
        "template_fidelity_strict_enabled": settings.template_fidelity_strict_enabled,
        "template_schema_validation_blocking": settings.template_schema_validation_blocking,
        "template_fidelity_media_integrity_blocking": settings.template_fidelity_media_integrity_blocking,
        "template_docx_require_native_for_custom": settings.template_docx_require_native_for_custom,
    }
    required_false = {
        "template_docx_legacy_export_allowed": settings.template_docx_legacy_export_allowed,
        "app_debug": settings.app_debug,
    }
    for key, value in required_true.items():
        if not bool(value):
            violations.append(f"{key} must be true")
    for key, value in required_false.items():
        if bool(value):
            violations.append(f"{key} must be false")
    return violations


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
    if settings.is_strict_env():
        violations = strict_policy_violations(settings)
        if violations:
            msg = (
                "Strict production profile validation failed: "
                + "; ".join(violations)
                + ". Fix env vars before starting the service."
            )
            logger.error(msg)
            raise RuntimeError(msg)

    if not verify_storage_writable(settings.storage_root):
        logger.error(
            "Set STORAGE_ROOT to a persistent, writable directory (mounted volume in Azure "
            "Container Apps/App Service, Kubernetes PVC, etc.)."
        )
    if settings.log_cleanup_enabled:
        deleted = cleanup_old_observability_logs(
            logs_path=settings.logs_path,
            retention_days=max(0, int(settings.log_retention_days)),
        )
        if deleted > 0:
            logger.info("observability.log.cleanup.deleted count=%s retention_days=%s", deleted, settings.log_retention_days)
    reconcile_interrupted_workflows(WorkflowRepository(settings.workflows_path))
