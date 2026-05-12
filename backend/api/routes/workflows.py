"""Workflow routes — create runs, poll status, and read diagnostics.

Endpoints (all under ``/api/workflow-runs``):

- ``POST   ""``                            Create a run. Validates the
                                           document/template pair; if
                                           ``start_immediately`` is true
                                           (default) the executor is
                                           dispatched as a background
                                           task and progress flows to the
                                           SSE stream.
- ``GET    ""``                            List all runs.
- ``GET    /{id}``                         Full record.
- ``GET    /{id}/status``                  Compact poll-friendly payload
                                           (status + phase + progress %).
- ``GET    /{id}/sections``                Section plan + per-section
                                           progress (used by the
                                           generation UI).
- ``GET    /{id}/observability``           Aggregated cost summary +
                                           integrity hints. Adds
                                           ``runtime_policy_mode`` so the
                                           UI can show "strict" vs
                                           "local-skip" mode.
- ``GET    /{id}/errors``                  Errors + warnings collected
                                           during the run.
- ``GET    /{id}/diagnostics``             Everything an operator needs
                                           for postmortem analysis.
- ``GET    /{id}/sections/{section_id}/diagram``  Serve a generated
                                           diagram PNG; the resolver
                                           rejects any path that escapes
                                           ``storage_root`` to prevent
                                           directory traversal.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict

from api.deps import get_task_dispatcher, get_workflow_executor, get_workflow_service
from core.config import settings
from core.logging import get_logger, verbose_logs_enabled
from core.response import created_response, success_response
from services.workflow_executor import WorkflowExecutor
from services.workflow_service import WorkflowService

router = APIRouter()
logger = get_logger(__name__)


class WorkflowCreateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    document_id: str
    template_id: str
    doc_type: str | None = None
    start_immediately: bool = True


@router.post("")
async def create_workflow(
    payload: WorkflowCreateRequest,
    background_tasks: BackgroundTasks,
    workflow_service: WorkflowService = Depends(get_workflow_service),
    workflow_executor: WorkflowExecutor = Depends(get_workflow_executor),
    task_dispatcher=Depends(get_task_dispatcher),
) -> object:
    if verbose_logs_enabled():
        logger.info(
            "workflow.create.request document_id=%s template_id=%s doc_type=%s start_immediately=%s",
            payload.document_id,
            payload.template_id,
            payload.doc_type,
            payload.start_immediately,
        )
    record = workflow_service.create(
        document_id=payload.document_id,
        template_id=payload.template_id,
        doc_type=payload.doc_type,
    )
    if verbose_logs_enabled():
        logger.info("workflows.create.completed workflow_run_id=%s", record.workflow_run_id)
    if payload.start_immediately:
        if verbose_logs_enabled():
            logger.info("workflows.dispatch.started workflow_run_id=%s", record.workflow_run_id)
        task_dispatcher.dispatch(background_tasks, workflow_executor.run, record.workflow_run_id)
    return created_response(record.model_dump(), message="Workflow created")


@router.get("")
async def list_workflows(workflow_service: WorkflowService = Depends(get_workflow_service)) -> object:
    logger.info("workflows.list.started")
    items = [item.model_dump() for item in workflow_service.list_all()]
    logger.info("workflows.list.completed total=%s", len(items))
    return success_response({"items": items, "total": len(items)})


@router.get("/{workflow_run_id}")
async def get_workflow(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    logger.info("workflows.get.started workflow_run_id=%s", workflow_run_id)
    workflow = workflow_service.get_or_raise(workflow_run_id)
    if verbose_logs_enabled():
        logger.info(
            "workflows.get.completed workflow_run_id=%s status=%s phase=%s",
            workflow_run_id,
            workflow.status,
            workflow.current_phase,
        )
    return success_response(workflow.model_dump())


@router.get("/{workflow_run_id}/status")
async def get_workflow_status(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    logger.info("workflows.status.started workflow_run_id=%s", workflow_run_id)
    workflow = workflow_service.get_or_raise(workflow_run_id)
    data = {
        "workflow_run_id": workflow.workflow_run_id,
        "status": workflow.status,
        "current_phase": workflow.current_phase,
        "overall_progress_percent": workflow.overall_progress_percent,
        "current_step_label": workflow.current_step_label,
        "document_id": workflow.document_id,
        "template_id": workflow.template_id,
        "output_id": workflow.output_id,
    }
    logger.info(
        "workflows.status.completed workflow_run_id=%s status=%s progress=%s",
        workflow_run_id,
        workflow.status,
        workflow.overall_progress_percent,
    )
    return success_response(data)


@router.get("/{workflow_run_id}/sections/{section_id}/diagram")
async def get_workflow_section_diagram(
    workflow_run_id: str,
    section_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> FileResponse:
    """
    Serve a generated diagram PNG for document review (markdown preview).

    Path is resolved from the assembled section's diagram_path under storage_root.
    """
    workflow = workflow_service.get_or_raise(workflow_run_id)
    assembled = workflow.assembled_document or {}
    sections = assembled.get("sections")
    if not isinstance(sections, list):
        raise HTTPException(status_code=404, detail="No assembled document sections.")

    diagram_path: str | None = None
    for row in sections:
        if not isinstance(row, dict):
            continue
        if str(row.get("section_id") or "") != section_id:
            continue
        raw = row.get("diagram_path")
        diagram_path = str(raw).strip().replace("\\", "/") if raw else None
        break
    else:
        raise HTTPException(status_code=404, detail="Section not found in assembled document.")

    if not diagram_path:
        raise HTTPException(status_code=404, detail="This section has no generated diagram file.")

    root = settings.storage_root.resolve()
    try:
        abs_path = (root / Path(diagram_path)).resolve()
    except OSError as exc:
        raise HTTPException(status_code=400, detail="Invalid diagram path.") from exc

    try:
        abs_path.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Diagram path escapes storage root.") from exc

    if not abs_path.is_file():
        raise HTTPException(status_code=404, detail="Diagram file is missing on disk.")

    return FileResponse(abs_path, media_type="image/png")


@router.get("/{workflow_run_id}/sections")
async def get_workflow_sections(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    logger.info("workflows.sections.started workflow_run_id=%s", workflow_run_id)
    workflow = workflow_service.get_or_raise(workflow_run_id)
    data = {
        "workflow_run_id": workflow_run_id,
        "section_plan": getattr(workflow, "section_plan", []),
        "section_progress": getattr(
            workflow,
            "section_progress",
            {"total": 0, "completed": 0, "running": 0, "failed": 0, "pending": 0},
        ),
    }
    logger.info(
        "workflows.sections.completed workflow_run_id=%s total=%s completed=%s failed=%s",
        workflow_run_id,
        data["section_progress"].get("total", 0),
        data["section_progress"].get("completed", 0),
        data["section_progress"].get("failed", 0),
    )
    return success_response(data)


@router.get("/{workflow_run_id}/observability")
async def get_workflow_observability(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    logger.info("workflows.observability.started workflow_run_id=%s", workflow_run_id)
    workflow = workflow_service.get_or_raise(workflow_run_id)
    summary = getattr(workflow, "observability_summary", {}) or {}
    policy_mode = "local-skip" if str(settings.app_env).lower() in {"local", "development", "dev"} else "strict-fail"
    data = {"workflow_run_id": workflow_run_id, "runtime_policy_mode": policy_mode, **summary}
    data.setdefault("header_footer_integrity", "unknown")
    data.setdefault("media_integrity", "unknown")
    if verbose_logs_enabled():
        logger.info(
            "workflows.observability.completed workflow_run_id=%s keys=%s",
            workflow_run_id,
            sorted(summary.keys()),
        )
    return success_response(data)


@router.get("/{workflow_run_id}/errors")
async def get_workflow_errors(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    logger.info("workflows.errors.started workflow_run_id=%s", workflow_run_id)
    workflow = workflow_service.get_or_raise(workflow_run_id)
    errors = getattr(workflow, "errors", [])
    warnings = getattr(workflow, "warnings", [])
    logger.info(
        "workflows.errors.completed workflow_run_id=%s errors=%s warnings=%s",
        workflow_run_id,
        len(errors),
        len(warnings),
    )
    return success_response(
        {
            "errors": errors,
            "warnings": warnings,
        },
    )


@router.get("/{workflow_run_id}/diagnostics")
async def get_workflow_diagnostics(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    logger.info("workflows.diagnostics.started workflow_run_id=%s", workflow_run_id)
    workflow = workflow_service.get_or_raise(workflow_run_id)
    data = {
        "workflow_run_id": workflow_run_id,
        "status": workflow.status,
        "phases": getattr(workflow, "phases", []),
        "section_progress": getattr(
            workflow,
            "section_progress",
            {"total": 0, "completed": 0, "running": 0, "failed": 0, "pending": 0},
        ),
        "observability_summary": getattr(workflow, "observability_summary", {}),
        "header_footer_integrity": "unknown",
        "media_integrity": "unknown",
        "errors": getattr(workflow, "errors", []),
        "warnings": getattr(workflow, "warnings", []),
    }
    logger.info(
        "workflows.diagnostics.completed workflow_run_id=%s status=%s errors=%s warnings=%s",
        workflow_run_id,
        workflow.status,
        len(data["errors"]),
        len(data["warnings"]),
    )
    return success_response(data)
