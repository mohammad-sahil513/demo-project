"""Workflow executor skeleton for Phase 3."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

from core.constants import MODEL_PRICING, PHASE_WEIGHTS, TemplateStatus, WorkflowPhase, WorkflowStatus
from core.exceptions import WorkflowException
from core.ids import utc_now_iso
from modules.ingestion.ingestion_coordinator import IngestionCoordinator, IngestionRunResult
from modules.ingestion.orchestrator import IngestionOrchestrator
from modules.generation.cost_tracking import GenerationCostTracker
from modules.generation.models import GenerationSectionResult
from modules.generation.observability import merge_generation_observability
from modules.generation.orchestrator import GenerationOrchestrator
from modules.observability.cost_rollup import merge_full_cost_summary
from modules.assembly.assembler import DocumentAssembler
from modules.assembly.models import AssembledDocument
from modules.export.renderer import ExportRenderer
from modules.export.types import ExportDocumentInfo, ExportTemplateInfo
from modules.retrieval.packager import EvidencePackager
from modules.retrieval.retriever import SectionRetriever, merge_retrieval_observability
from modules.template.inbuilt.registry import (
    doc_type_for_inbuilt_template,
    get_inbuilt_section_plan,
    get_inbuilt_style_map,
    is_inbuilt_template_id,
)
from modules.template.models import SectionDefinition, StyleMap
from repositories.document_models import DocumentRecord
from core.config import settings
from core.logging import get_logger
from services.event_service import EventService
from services.output_service import OutputService
from services.workflow_service import WorkflowService

logger = get_logger(__name__)


@dataclass(slots=True)
class _RetrievalCostTracker:
    llm_cost_usd: float = 0.0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_llm_calls: int = 0

    def track_call(self, *, model: str, task: str, input_tokens: int, output_tokens: int) -> None:
        del task
        rates = MODEL_PRICING.get(model)
        if rates is None:
            return
        self.total_tokens_in += int(input_tokens)
        self.total_tokens_out += int(output_tokens)
        self.total_llm_calls += 1
        self.llm_cost_usd += (input_tokens / 1000.0) * rates["input"] + (output_tokens / 1000.0) * rates["output"]


class WorkflowExecutor:
    def __init__(
        self,
        workflow_service: WorkflowService,
        event_service: EventService,
        ingestion_orchestrator: IngestionOrchestrator | None = None,
        ingestion_coordinator: IngestionCoordinator | None = None,
        section_retriever: SectionRetriever | None = None,
        evidence_packager: EvidencePackager | None = None,
        generation_orchestrator: GenerationOrchestrator | None = None,
        output_service: OutputService | None = None,
        document_assembler: DocumentAssembler | None = None,
        export_renderer: ExportRenderer | None = None,
    ) -> None:
        self._workflow_service = workflow_service
        self._event_service = event_service
        self._ingestion_orchestrator = ingestion_orchestrator
        self._ingestion_coordinator = ingestion_coordinator
        self._section_retriever = section_retriever
        self._evidence_packager = evidence_packager
        self._generation_orchestrator = generation_orchestrator
        self._output_service = output_service
        self._document_assembler = document_assembler or DocumentAssembler()
        self._export_renderer = export_renderer or ExportRenderer(settings.storage_root)

    async def _run_phase(
        self,
        workflow_run_id: str,
        phase: WorkflowPhase,
        fn: Callable[[str], Awaitable[None]],
    ) -> None:
        logger.info(
            "phase.started workflow_run_id=%s phase=%s",
            workflow_run_id,
            phase.value,
        )
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
                logger.info(
                    "phase.attempt workflow_run_id=%s phase=%s attempt=%s",
                    workflow_run_id,
                    phase.value,
                    attempt + 1,
                )
                await fn(workflow_run_id)
                break
            except Exception as exc:
                logger.exception(
                    "phase.attempt_failed workflow_run_id=%s phase=%s attempt=%s error=%s",
                    workflow_run_id,
                    phase.value,
                    attempt + 1,
                    str(exc),
                )
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
        logger.info(
            "phase.completed workflow_run_id=%s phase=%s progress=%s",
            workflow_run_id,
            phase.value,
            progress,
        )

    async def _phase_input_preparation(self, workflow_run_id: str) -> None:
        self._workflow_service.update(workflow_run_id, current_step_label="Initializing workflow")

    async def _phase_ingestion(self, workflow_run_id: str) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        document = self._workflow_service.get_document(workflow.document_id)
        logger.info(
            "ingestion.enter workflow_run_id=%s document_id=%s",
            workflow_run_id,
            workflow.document_id,
        )

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
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        template = self._workflow_service.get_template(workflow.template_id)
        logger.info(
            "template_preparation.enter workflow_run_id=%s template_id=%s",
            workflow_run_id,
            workflow.template_id,
        )

        if is_inbuilt_template_id(template.template_id):
            doc_type = doc_type_for_inbuilt_template(template.template_id)
            section_plan = get_inbuilt_section_plan(doc_type)
            style_map = get_inbuilt_style_map(doc_type)
            self._workflow_service.update(
                workflow_run_id,
                current_step_label=f"Inbuilt template ready ({doc_type.value})",
                section_plan=[item.model_dump() for item in section_plan],
                style_map=style_map.model_dump(),
                sheet_map={},
            )
            return

        if template.status != TemplateStatus.READY.value:
            raise WorkflowException(f"Template {template.template_id} is not ready: {template.status}")

        section_plan = [SectionDefinition.model_validate(item) for item in (template.section_plan or [])]
        if not section_plan:
            raise WorkflowException(f"Template {template.template_id} has no compiled section plan.")
        style_map = StyleMap.model_validate(template.style_map or {})
        self._workflow_service.update(
            workflow_run_id,
            current_step_label=f"Template ready ({len(section_plan)} sections)",
            section_plan=[item.model_dump() for item in section_plan],
            style_map=style_map.model_dump(),
            sheet_map=template.sheet_map or {},
        )

    async def _phase_section_planning(self, workflow_run_id: str) -> None:
        self._workflow_service.update(workflow_run_id, current_step_label="Section planning stub")

    async def _phase_retrieval(self, workflow_run_id: str) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        section_plan = [SectionDefinition.model_validate(item) for item in (workflow.section_plan or [])]
        logger.info(
            "retrieval.enter workflow_run_id=%s sections=%s",
            workflow_run_id,
            len(section_plan),
        )
        if not section_plan:
            self._workflow_service.update(workflow_run_id, current_step_label="Retrieval skipped (no sections)")
            return

        if self._section_retriever is None or self._evidence_packager is None:
            message = "Retrieval dependencies not configured"
            if self._is_local_env():
                self._workflow_service.update(workflow_run_id, current_step_label=f"{message} (local skip)")
                return
            raise WorkflowException(message)
        if not self._section_retriever.is_configured():
            message = "Retrieval not configured (missing Azure credentials)"
            if self._is_local_env():
                self._workflow_service.update(
                    workflow_run_id,
                    current_step_label=f"{message}; skipped in local env",
                )
                return
            raise WorkflowException(message)

        self._workflow_service.update(
            workflow_run_id,
            current_step_label=f"Retrieving evidence for {len(section_plan)} sections",
        )
        retrieval_cost_tracker = _RetrievalCostTracker()
        tasks = [
            self._retrieve_one_section(workflow.document_id, section, retrieval_cost_tracker)
            for section in section_plan
        ]
        outputs = await asyncio.gather(*tasks)

        section_retrieval_results: dict[str, dict[str, object]] = {}
        total_embedding_cost_usd = 0.0
        for section_id, bundle_dict, embedding_cost_usd in outputs:
            section_retrieval_results[section_id] = bundle_dict
            total_embedding_cost_usd += embedding_cost_usd

        updated = self._workflow_service.update(
            workflow_run_id,
            section_retrieval_results=section_retrieval_results,
            current_step_label=f"Retrieved evidence for {len(section_retrieval_results)} sections",
        )
        observability_summary = merge_retrieval_observability(
            getattr(updated, "observability_summary", None),
            llm_cost_usd=retrieval_cost_tracker.llm_cost_usd,
            embedding_cost_usd=total_embedding_cost_usd,
            retrieved_sections=len(section_retrieval_results),
            total_tokens_in=retrieval_cost_tracker.total_tokens_in,
            total_tokens_out=retrieval_cost_tracker.total_tokens_out,
            total_llm_calls=retrieval_cost_tracker.total_llm_calls,
        )
        self._workflow_service.update(workflow_run_id, observability_summary=observability_summary)

    async def _phase_generation(self, workflow_run_id: str) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        section_plan = [SectionDefinition.model_validate(item) for item in (workflow.section_plan or [])]
        logger.info(
            "generation.enter workflow_run_id=%s sections=%s",
            workflow_run_id,
            len(section_plan),
        )
        if not section_plan:
            self._workflow_service.update(workflow_run_id, current_step_label="Generation skipped (no sections)")
            return

        if self._generation_orchestrator is None:
            message = "Generation dependencies not configured"
            if self._is_local_env():
                self._workflow_service.update(workflow_run_id, current_step_label=f"{message} (local skip)")
                return
            raise WorkflowException(message)

        if not self._generation_orchestrator.is_configured():
            message = "Generation not configured (missing Azure credentials)"
            if self._is_local_env():
                self._workflow_service.update(
                    workflow_run_id,
                    current_step_label=f"{message}; skipped in local env",
                )
                return
            raise WorkflowException(message)

        self._workflow_service.update(
            workflow_run_id,
            current_step_label=f"Generating content for {len(section_plan)} sections",
        )
        cost_tracker = GenerationCostTracker()

        async def _emit(wid: str, event_type: str, payload: dict[str, object] | None) -> None:
            await self._event_service.emit(wid, event_type, payload)

        raw_results = await self._generation_orchestrator.run_all_sections(
            workflow_run_id=workflow_run_id,
            sections=section_plan,
            section_retrieval_results=dict(workflow.section_retrieval_results or {}),
            doc_type=workflow.doc_type,
            cost_tracker=cost_tracker,
            emit=_emit,
        )
        section_generation_results: dict[str, dict[str, object]] = {}
        for section_id, payload in raw_results.items():
            cleaned = dict(payload)
            cleaned.pop("diagram_source", None)
            section_generation_results[section_id] = GenerationSectionResult.model_validate(cleaned).model_dump()

        failed = sum(1 for row in section_generation_results.values() if row.get("error"))
        completed = len(section_generation_results) - failed
        section_progress = {
            "total": len(section_generation_results),
            "pending": 0,
            "running": 0,
            "completed": completed,
            "failed": failed,
        }

        updated = self._workflow_service.update(
            workflow_run_id,
            section_generation_results=section_generation_results,
            section_progress=section_progress,
            current_step_label=f"Generated {len(section_generation_results)} sections",
        )
        observability_summary = merge_generation_observability(
            getattr(updated, "observability_summary", None),
            llm_cost_usd=cost_tracker.llm_cost_usd,
            generated_sections=len(section_generation_results),
            total_tokens_in=cost_tracker.total_tokens_in,
            total_tokens_out=cost_tracker.total_tokens_out,
            total_llm_calls=cost_tracker.total_llm_calls,
        )
        self._workflow_service.update(workflow_run_id, observability_summary=observability_summary)
        logger.info(
            "generation.completed workflow_run_id=%s completed=%s failed=%s",
            workflow_run_id,
            completed,
            failed,
        )

    async def _phase_assembly_validation(self, workflow_run_id: str) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        document = self._workflow_service.get_document(workflow.document_id)
        logger.info(
            "assembly.enter workflow_run_id=%s document_id=%s",
            workflow_run_id,
            workflow.document_id,
        )
        section_plan = [SectionDefinition.model_validate(x) for x in (workflow.section_plan or [])]
        gen = workflow.section_generation_results or {}
        if not section_plan:
            self._workflow_service.update(workflow_run_id, current_step_label="Assembly skipped (no sections)")
            return
        outcome = self._document_assembler.assemble(
            document_filename=document.filename,
            doc_type=workflow.doc_type,
            section_plan=section_plan,
            section_generation_results=dict(gen),
        )
        merged_warnings = list(workflow.warnings or []) + outcome.warnings
        self._workflow_service.update(
            workflow_run_id,
            assembled_document=outcome.document.model_dump(),
            warnings=merged_warnings,
            current_step_label=f"Assembled {len(outcome.document.sections)} sections",
        )

    async def _phase_render_export(self, workflow_run_id: str) -> None:
        if self._output_service is None:
            self._workflow_service.update(workflow_run_id, current_step_label="Export skipped (no output service)")
            return
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        logger.info(
            "render_export.enter workflow_run_id=%s",
            workflow_run_id,
        )
        ad = workflow.assembled_document or {}
        if not ad.get("sections"):
            self._workflow_service.update(workflow_run_id, current_step_label="Export skipped (nothing to render)")
            return

        template = self._workflow_service.get_template(workflow.template_id)
        document = self._workflow_service.get_document(workflow.document_id)
        assembled = AssembledDocument.model_validate(ad)
        style_map = StyleMap.model_validate(workflow.style_map or {})
        out_path, filename, export_warnings = self._export_renderer.render(
            workflow_run_id=workflow_run_id,
            document=ExportDocumentInfo(filename=document.filename),
            template=ExportTemplateInfo(
                template_id=template.template_id,
                template_source=template.template_source,
                file_path=template.file_path,
            ),
            assembled=assembled,
            style_map=style_map,
            sheet_map=dict(workflow.sheet_map or {}),
        )
        wf2 = self._workflow_service.get_or_raise(workflow_run_id)
        render_warnings = list(wf2.warnings or []) + export_warnings
        record = self._output_service.create(
            workflow_run_id=workflow_run_id,
            document_id=document.document_id,
            doc_type=workflow.doc_type,
            file_path=out_path,
            filename=filename,
        )
        self._workflow_service.update(
            workflow_run_id,
            output_id=record.output_id,
            warnings=render_warnings,
            current_step_label="Output file ready",
        )
        await self._event_service.emit(
            workflow_run_id,
            "output.ready",
            {"output_id": record.output_id, "filename": filename},
        )

    async def _retrieve_one_section(
        self,
        document_id: str,
        section: SectionDefinition,
        cost_tracker: _RetrievalCostTracker,
    ) -> tuple[str, dict[str, object], float]:
        if self._section_retriever is None or self._evidence_packager is None:
            raise WorkflowException("Retrieval dependencies not configured.")
        chunks, embedding_cost_usd = await self._section_retriever.retrieve_for_section(
            section,
            document_id=document_id,
            cost_tracker=cost_tracker,
        )
        bundle = self._evidence_packager.package(section.section_id, chunks)
        bundle_dict = {
            "context_text": bundle.context_text,
            "citations": [citation.model_dump() for citation in bundle.citations],
        }
        return section.section_id, bundle_dict, embedding_cost_usd

    @staticmethod
    def _is_local_env() -> bool:
        return settings.app_env.lower() in {"development", "dev", "local", "test"}

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
        logger.info("workflow.started workflow_run_id=%s", workflow_run_id)
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
            summary = getattr(workflow, "observability_summary", None) or {}
            total_cost = float(summary.get("total_cost_usd", 0.0))
            try:
                await self._event_service.emit(
                    workflow_run_id,
                    "workflow.completed",
                    {"output_id": workflow.output_id, "total_cost_usd": total_cost},
                )
            except Exception:
                logger.exception(
                    "workflow_completed_emit_failed workflow_run_id=%s",
                    workflow_run_id,
                )
            logger.info("workflow.completed workflow_run_id=%s", workflow_run_id)
        except Exception as exc:
            logger.exception(
                "workflow.failed workflow_run_id=%s error=%s",
                workflow_run_id,
                str(exc),
            )
            self._workflow_service.update(
                workflow_run_id,
                status=WorkflowStatus.FAILED.value,
                current_step_label=str(exc),
            )
            try:
                await self._event_service.emit(
                    workflow_run_id,
                    "workflow.failed",
                    {"error": str(exc)},
                )
            except Exception:
                logger.exception(
                    "workflow_failed_emit_failed workflow_run_id=%s",
                    workflow_run_id,
                )
            # Do not re-raise: failure is persisted; terminal emit is best-effort for SSE clients.
