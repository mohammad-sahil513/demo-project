"""Workflow routes."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel, ConfigDict

from api.deps import get_task_dispatcher, get_workflow_executor, get_workflow_service
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
        logger.info("workflow.create.persisted workflow_run_id=%s", record.workflow_run_id)
    if payload.start_immediately:
        if verbose_logs_enabled():
            logger.info("workflow.create.dispatch workflow_run_id=%s", record.workflow_run_id)
        task_dispatcher.dispatch(background_tasks, workflow_executor.run, record.workflow_run_id)
    return created_response(record.model_dump(), message="Workflow created")


@router.get("")
async def list_workflows(workflow_service: WorkflowService = Depends(get_workflow_service)) -> object:
    items = [item.model_dump() for item in workflow_service.list_all()]
    return success_response({"items": items, "total": len(items)})


@router.get("/{workflow_run_id}")
async def get_workflow(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    workflow = workflow_service.get_or_raise(workflow_run_id)
    return success_response(workflow.model_dump())


@router.get("/{workflow_run_id}/status")
async def get_workflow_status(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
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
    return success_response(data)


@router.get("/{workflow_run_id}/sections")
async def get_workflow_sections(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
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
    return success_response(data)


@router.get("/{workflow_run_id}/observability")
async def get_workflow_observability(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    workflow = workflow_service.get_or_raise(workflow_run_id)
    summary = getattr(workflow, "observability_summary", {}) or {}
    data = {"workflow_run_id": workflow_run_id, **summary}
    return success_response(data)


@router.get("/{workflow_run_id}/errors")
async def get_workflow_errors(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    workflow = workflow_service.get_or_raise(workflow_run_id)
    return success_response(
        {
            "errors": getattr(workflow, "errors", []),
            "warnings": getattr(workflow, "warnings", []),
        },
    )


@router.get("/{workflow_run_id}/diagnostics")
async def get_workflow_diagnostics(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
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
        "errors": getattr(workflow, "errors", []),
        "warnings": getattr(workflow, "warnings", []),
    }
    return success_response(data)
