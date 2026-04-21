"""Workflow executor skeleton for Phase 3."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from core.constants import PHASE_WEIGHTS, WorkflowPhase, WorkflowStatus
from core.exceptions import WorkflowException
from core.ids import utc_now_iso
from services.event_service import EventService
from services.workflow_service import WorkflowService


class WorkflowExecutor:
    def __init__(self, workflow_service: WorkflowService, event_service: EventService) -> None:
        self._workflow_service = workflow_service
        self._event_service = event_service

    async def _run_phase(
        self,
        workflow_run_id: str,
        phase: WorkflowPhase,
        fn: Callable[[str], Awaitable[None]],
    ) -> None:
        self._workflow_service.update(
            workflow_run_id,
            current_phase=phase.value,
            current_step_label=f"{phase.value} started",
        )
        await self._event_service.emit(
            workflow_run_id,
            "phase.started",
            {"phase": phase.value},
        )

        for attempt in range(2):
            try:
                await fn(workflow_run_id)
                break
            except Exception as exc:
                if attempt == 0:
                    await asyncio.sleep(2)
                    continue
                raise WorkflowException(
                    f"Phase failed after retry ({phase.value}): {exc}",
                    code="WORKFLOW_PHASE_ERROR",
                ) from exc

        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        progress = min(100.0, float(workflow.overall_progress_percent) + PHASE_WEIGHTS[phase])
        self._workflow_service.update(
            workflow_run_id,
            overall_progress_percent=progress,
            current_step_label=f"{phase.value} completed",
        )
        await self._event_service.emit(
            workflow_run_id,
            "phase.completed",
            {"phase": phase.value, "duration_ms": 0},
        )

    async def _phase_input_preparation(self, workflow_run_id: str) -> None:
        self._workflow_service.update(workflow_run_id, current_step_label="Initializing workflow")

    async def _phase_ingestion(self, workflow_run_id: str) -> None:
        self._workflow_service.update(workflow_run_id, current_step_label="Ingestion stub completed")

    async def _phase_template_preparation(self, workflow_run_id: str) -> None:
        self._workflow_service.update(workflow_run_id, current_step_label="Template preparation stub")

    async def _phase_section_planning(self, workflow_run_id: str) -> None:
        self._workflow_service.update(workflow_run_id, current_step_label="Section planning stub")

    async def _phase_retrieval(self, workflow_run_id: str) -> None:
        self._workflow_service.update(workflow_run_id, current_step_label="Retrieval stub")

    async def _phase_generation(self, workflow_run_id: str) -> None:
        self._workflow_service.update(workflow_run_id, current_step_label="Generation stub")

    async def _phase_assembly_validation(self, workflow_run_id: str) -> None:
        self._workflow_service.update(workflow_run_id, current_step_label="Assembly validation stub")

    async def _phase_render_export(self, workflow_run_id: str) -> None:
        self._workflow_service.update(workflow_run_id, current_step_label="Render export stub")

    async def run(self, workflow_run_id: str) -> None:
        self._workflow_service.get_or_raise(workflow_run_id)
        self._workflow_service.update(
            workflow_run_id,
            status=WorkflowStatus.RUNNING.value,
            started_at=utc_now_iso(),
            current_step_label="Workflow started",
        )
        await self._event_service.emit(workflow_run_id, "workflow.started", {"doc_type": "stub"})

        try:
            await self._run_phase(
                workflow_run_id,
                WorkflowPhase.INPUT_PREPARATION,
                self._phase_input_preparation,
            )
            await self._run_phase(workflow_run_id, WorkflowPhase.INGESTION, self._phase_ingestion)
            await self._run_phase(
                workflow_run_id,
                WorkflowPhase.TEMPLATE_PREPARATION,
                self._phase_template_preparation,
            )
            await self._run_phase(
                workflow_run_id,
                WorkflowPhase.SECTION_PLANNING,
                self._phase_section_planning,
            )
            await self._run_phase(workflow_run_id, WorkflowPhase.RETRIEVAL, self._phase_retrieval)
            await self._run_phase(workflow_run_id, WorkflowPhase.GENERATION, self._phase_generation)
            await self._run_phase(
                workflow_run_id,
                WorkflowPhase.ASSEMBLY_VALIDATION,
                self._phase_assembly_validation,
            )
            await self._run_phase(
                workflow_run_id,
                WorkflowPhase.RENDER_EXPORT,
                self._phase_render_export,
            )

            self._workflow_service.update(
                workflow_run_id,
                status=WorkflowStatus.COMPLETED.value,
                overall_progress_percent=100.0,
                completed_at=utc_now_iso(),
                current_step_label="Workflow completed",
            )
            workflow = self._workflow_service.get_or_raise(workflow_run_id)
            await self._event_service.emit(
                workflow_run_id,
                "workflow.completed",
                {"output_id": workflow.output_id, "total_cost_usd": 0.0},
            )
        except Exception as exc:
            self._workflow_service.update(
                workflow_run_id,
                status=WorkflowStatus.FAILED.value,
                current_step_label=str(exc),
            )
            await self._event_service.emit(
                workflow_run_id,
                "workflow.failed",
                {"error": str(exc)},
            )
            raise
