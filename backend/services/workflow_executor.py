"""Workflow executor skeleton for Phase 3."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

from core.constants import PHASE_WEIGHTS, WorkflowPhase, WorkflowStatus
from core.exceptions import WorkflowException
from core.ids import utc_now_iso
from modules.ingestion.ingestion_coordinator import IngestionCoordinator, IngestionRunResult
from modules.ingestion.orchestrator import IngestionOrchestrator
from modules.observability.cost_rollup import merge_full_cost_summary
from repositories.document_models import DocumentRecord
from core.config import settings
from services.event_service import EventService
from services.workflow_service import WorkflowService


class WorkflowExecutor:
    def __init__(
        self,
        workflow_service: WorkflowService,
        event_service: EventService,
        ingestion_orchestrator: IngestionOrchestrator | None = None,
        ingestion_coordinator: IngestionCoordinator | None = None,
    ) -> None:
        self._workflow_service = workflow_service
        self._event_service = event_service
        self._ingestion_orchestrator = ingestion_orchestrator
        self._ingestion_coordinator = ingestion_coordinator

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
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        document = self._workflow_service.get_document(workflow.document_id)

        if self._ingestion_orchestrator is None or self._ingestion_coordinator is None:
            self._workflow_service.update(workflow_run_id, current_step_label="Ingestion dependencies not configured")
            return
        if not self._ingestion_orchestrator.is_configured():
            self._workflow_service.update(
                workflow_run_id,
                current_step_label="Ingestion skipped (No Azure credentials)",
            )
            return

        self._workflow_service.update(workflow_run_id, current_step_label="Parsing BRD document")
        skipped, result = await self._ingestion_coordinator.run_ingestion_if_needed(
            document.document_id,
            lambda doc: self._run_ingestion_pipeline(workflow_run_id, doc),
        )
        if skipped:
            self._workflow_service.update(
                workflow_run_id,
                current_step_label="Ingestion skipped (already indexed)",
            )
            return

        if result is not None:
            self._apply_ingestion_observability(workflow_run_id, result)
            self._workflow_service.update(
                workflow_run_id,
                current_step_label=f"Ingestion completed ({result.chunk_count} chunks)",
            )

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

    async def _run_ingestion_pipeline(
        self,
        workflow_run_id: str,
        document: DocumentRecord,
    ) -> IngestionRunResult:
        self._workflow_service.update(workflow_run_id, current_step_label="Parsing BRD document")
        file_path = Path(settings.documents_path) / document.file_path
        return await self._ingestion_orchestrator.run(
            workflow_run_id=workflow_run_id,
            document_id=document.document_id,
            file_path=file_path,
            content_type=document.content_type,
        )

    def _apply_ingestion_observability(self, workflow_run_id: str, result: IngestionRunResult) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        merged = merge_full_cost_summary(
            getattr(workflow, "observability_summary", None),
            embedding_cost_usd=result.embedding_cost_usd,
            document_intelligence_cost_usd=result.document_intelligence_cost_usd,
            extra={
                "page_count": result.page_count,
                "indexed_chunk_count": result.chunk_count,
            },
        )
        self._workflow_service.update(workflow_run_id, observability_summary=merged)

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
