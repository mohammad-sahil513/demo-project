"""Workflow executor skeleton for Phase 3."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from core.constants import (
    DOCX_EXPORT_POLICY_BLOCKING_CODES,
    MODEL_PRICING,
    PHASE_WEIGHTS,
    SCHEMA_BLOCKING_CODES,
    SCHEMA_WARNING_CODES,
    TemplateStatus,
    WorkflowPhase,
    WorkflowStatus,
)
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
from core.logging import append_workflow_cost_log, append_workflow_log, get_logger
from services.event_service import EventService
from services.output_service import OutputService
from services.workflow_service import WorkflowService

logger = get_logger(__name__)


def merge_workflow_warnings(
    existing: list[dict[str, object]] | None,
    new: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Append new warnings without duplicate (code, section_id, message) tuples."""

    def _key(w: dict[str, object]) -> tuple[str, str, str]:
        return (
            str(w.get("code") or ""),
            str(w.get("section_id") or ""),
            str(w.get("message") or ""),
        )

    out: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()
    for w in list(existing or []) + list(new):
        k = _key(w)
        if k in seen:
            continue
        seen.add(k)
        out.append(w)
    return out


def _resolved_section_placeholder_map(template: object) -> dict[str, list[str]] | None:
    raw = getattr(template, "resolved_section_bindings", None) or {}
    if not isinstance(raw, dict) or not raw:
        return None
    out: dict[str, list[str]] = {}
    for k, v in raw.items():
        sk = str(k)
        if isinstance(v, list):
            out[sk] = [str(x) for x in v]
        elif v is not None:
            out[sk] = [str(v)]
    return out


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

        # Phase 2: limit retrieval fan-out against Azure AI Search
        self._max_concurrent_retrieval_sections = max(
            1,
            int(getattr(settings, "retrieval_max_concurrent_sections", 3)),
        )
        self._retrieval_semaphore = asyncio.Semaphore(self._max_concurrent_retrieval_sections)

    def _wf_log(self, workflow_run_id: str, message: str, *, level: str = "INFO") -> None:
        try:
            append_workflow_log(workflow_run_id, message, level=level)
        except Exception:
            logger.exception("workflow.filelog.failed workflow_run_id=%s", workflow_run_id)

    def _wf_cost_log(self, workflow_run_id: str, payload: dict[str, object]) -> None:
        try:
            append_workflow_cost_log(workflow_run_id, payload)
        except Exception:
            logger.exception("workflow.costlog.failed workflow_run_id=%s", workflow_run_id)

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
        self._wf_log(workflow_run_id, f"phase.started phase={phase.value}")
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

        phase_started_at = perf_counter()
        for attempt in range(2):
            try:
                logger.info(
                    "phase.attempt workflow_run_id=%s phase=%s attempt=%s",
                    workflow_run_id,
                    phase.value,
                    attempt + 1,
                )
                self._wf_log(workflow_run_id, f"phase.attempt phase={phase.value} attempt={attempt + 1}")
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
                self._wf_log(
                    workflow_run_id,
                    f"phase.attempt_failed phase={phase.value} attempt={attempt + 1} error={str(exc)}",
                    level="ERROR",
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
        duration_ms = int((perf_counter() - phase_started_at) * 1000)
        self._workflow_service.update(
            workflow_run_id,
            overall_progress_percent=progress,
            current_step_label=f"{phase.value} completed",
        )
        await self._event_service.emit(
            workflow_run_id,
            "phase.completed",
            {"phase": phase.value, "duration_ms": duration_ms},
        )
        logger.info(
            "phase.completed workflow_run_id=%s phase=%s progress=%s duration_ms=%s",
            workflow_run_id,
            phase.value,
            progress,
            duration_ms,
        )
        self._wf_log(workflow_run_id, f"phase.completed phase={phase.value} duration_ms={duration_ms}")
    async def _run_retrieval_with_semaphore(self, coro):
        async with self._retrieval_semaphore:
            return await coro

    async def _phase_input_preparation(self, workflow_run_id: str) -> None:
        logger.info("inputpreparation.phase.enter workflow_run_id=%s", workflow_run_id)
        self._workflow_service.update(workflow_run_id, current_step_label="Initializing workflow")
        logger.info("inputpreparation.phase.completed workflow_run_id=%s", workflow_run_id)

    async def _phase_ingestion(self, workflow_run_id: str) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        document = self._workflow_service.get_document(workflow.document_id)
        logger.info(
            "ingestion.enter workflow_run_id=%s document_id=%s",
            workflow_run_id,
            workflow.document_id,
        )

        if self._ingestion_orchestrator is None or self._ingestion_coordinator is None:
            logger.warning(
                "ingestion.phase.skippedmissingdependencies workflow_run_id=%s document_id=%s",
                workflow_run_id,
                workflow.document_id,
            )
            self._workflow_service.update(workflow_run_id, current_step_label="Ingestion dependencies not configured")
            return
        if not self._ingestion_orchestrator.is_configured():
            logger.warning(
                "ingestion.phase.skippednotconfigured workflow_run_id=%s document_id=%s",
                workflow_run_id,
                workflow.document_id,
            )
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
            logger.info(
                "ingestion.phase.skippedalreadyindexed workflow_run_id=%s document_id=%s",
                workflow_run_id,
                workflow.document_id,
            )
            self._workflow_service.update(
                workflow_run_id,
                current_step_label="Ingestion skipped (already indexed)",
            )
            return

        if result is not None:
            logger.info(
                "ingestion.completed workflow_run_id=%s document_id=%s chunk_count=%s page_count=%s embedding_cost_usd=%s",
                workflow_run_id,
                workflow.document_id,
                result.chunk_count,
                result.page_count,
                result.embedding_cost_usd,
            )
            self._apply_ingestion_observability(workflow_run_id, result)
            self._workflow_service.update(
                workflow_run_id,
                current_step_label=f"Ingestion completed ({result.chunk_count} chunks)",
            )

    async def _phase_template_preparation(self, workflow_run_id: str) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        template = self._workflow_service.get_template(workflow.template_id)
        logger.info(
            "templatepreparation.phase.enter workflow_run_id=%s template_id=%s",
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
            logger.info(
                "templatepreparation.phase.completedinbuilt workflow_run_id=%s template_id=%s doc_type=%s section_count=%s",
                workflow_run_id,
                template.template_id,
                doc_type.value,
                len(section_plan),
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
        logger.info(
            "templatepreparation.phase.completedcustom workflow_run_id=%s template_id=%s section_count=%s",
            workflow_run_id,
            template.template_id,
            len(section_plan),
        )

    async def _phase_section_planning(self, workflow_run_id: str) -> None:
        logger.info("sectionplanning.phase.enter workflow_run_id=%s", workflow_run_id)
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        template = self._workflow_service.get_template(workflow.template_id)
        section_plan = [SectionDefinition.model_validate(item) for item in (workflow.section_plan or [])]

        if not section_plan:
            self._workflow_service.update(workflow_run_id, current_step_label="Section planning skipped (no sections)")
            logger.info("sectionplanning.phase.skipped workflow_run_id=%s reason=no_sections", workflow_run_id)
            return

        planning_warnings: list[dict[str, object]] = []
        has_sheet_schema = (
            isinstance(workflow.sheet_map, dict)
            and isinstance(workflow.sheet_map.get("schema"), list)
            and len(workflow.sheet_map.get("schema") or []) > 0
        )
        ph_raw = (template.placeholder_schema or {}).get("placeholders")
        has_placeholder_schema = isinstance(ph_raw, list) and len(ph_raw) > 0
        if (
            workflow.doc_type == "UAT"
            and not is_inbuilt_template_id(workflow.template_id)
            and not has_sheet_schema
            and not has_placeholder_schema
        ):
            planning_warnings.append(
                {"code": "schema_not_ready", "message": "UAT template schema is missing for this workflow."}
            )

        table_sections = [s for s in section_plan if s.output_type == "table"]
        for section in table_sections:
            if not section.table_headers and not section.required_fields:
                planning_warnings.append(
                    {
                        "code": "table_contract_missing",
                        "section_id": section.section_id,
                        "message": "Table section has no table_headers/required_fields contract.",
                    }
                )

        merged_warnings = merge_workflow_warnings(workflow.warnings, planning_warnings)
        label = f"Section planning completed ({len(section_plan)} sections)"
        if planning_warnings:
            label = f"Section planning completed with {len(planning_warnings)} warnings"
        obs = dict(workflow.observability_summary or {})
        obs["section_planning_warning_codes"] = [
            str(w.get("code") or "") for w in planning_warnings if isinstance(w, dict)
        ]
        obs["section_planning_warning_count"] = len(planning_warnings)
        self._workflow_service.update(
            workflow_run_id,
            current_step_label=label,
            warnings=merged_warnings,
            observability_summary=obs,
        )
        logger.info(
            "sectionplanning.phase.completed workflow_run_id=%s warnings=%s warning_codes=%s",
            workflow_run_id,
            len(planning_warnings),
            obs["section_planning_warning_codes"],
        )

    async def _phase_retrieval(self, workflow_run_id: str) -> None:
        retrieval_started_at = perf_counter()

        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        section_plan = [SectionDefinition.model_validate(item) for item in (workflow.section_plan or [])]
        logger.info(
            "retrieval.enter workflow_run_id=%s sections=%s max_concurrent=%s",
            workflow_run_id,
            len(section_plan),
            self._max_concurrent_retrieval_sections,
        )

        if not section_plan:
            logger.info("retrieval.phase.skippednosections workflow_run_id=%s", workflow_run_id)
            self._workflow_service.update(workflow_run_id, current_step_label="Retrieval skipped (no sections)")
            return

        if self._section_retriever is None or self._evidence_packager is None:
            message = "Retrieval dependencies not configured"
            if self._is_local_env():
                logger.warning("retrieval.phase.skippedlocalmissingdependencies workflow_run_id=%s", workflow_run_id)
                self._workflow_service.update(workflow_run_id, current_step_label=f"{message} (local skip)")
                return
            raise WorkflowException(message)

        if not self._section_retriever.is_configured():
            message = "Retrieval not configured (missing Azure credentials)"
            if self._is_local_env():
                logger.warning("retrieval.phase.skippedlocalnotconfigured workflow_run_id=%s", workflow_run_id)
                self._workflow_service.update(
                    workflow_run_id,
                    current_step_label=f"{message}; skipped in local env",
                )
                return
            raise WorkflowException(message)

        ordered_sections = sorted(section_plan, key=lambda s: s.execution_order)

        self._workflow_service.update(
            workflow_run_id,
            current_step_label=f"Retrieving evidence for {len(ordered_sections)} sections",
        )

        retrieval_cost_tracker = _RetrievalCostTracker()

        tasks = []
        for section in ordered_sections:
            if section.content_mode in ("skip", "heading_only"):
                tasks.append(
                    self._run_retrieval_with_semaphore(self._empty_retrieval_for_section(section)),
                )
            else:
                tasks.append(
                    self._run_retrieval_with_semaphore(
                        self._retrieve_one_section(
                            workflow.document_id,
                            section,
                            retrieval_cost_tracker,
                        ),
                    ),
                )

        outputs = await asyncio.gather(*tasks)

        logger.info(
            "retrieval.sectiontasks.completed workflow_run_id=%s section_count=%s max_concurrent=%s",
            workflow_run_id,
            len(outputs),
            self._max_concurrent_retrieval_sections,
        )

        section_retrieval_results: dict[str, dict[str, object]] = {}
        total_embedding_cost_usd = 0.0
        total_chunks_retrieved = 0
        zero_hit_sections = 0

        for section_id, bundle_dict, embedding_cost_usd, chunk_count in outputs:
            section_retrieval_results[section_id] = bundle_dict
            total_embedding_cost_usd += embedding_cost_usd
            total_chunks_retrieved += chunk_count
            if chunk_count == 0:
                zero_hit_sections += 1

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

        # Add phase-level retrieval metrics
        observability_summary["retrieval_zero_hit_sections"] = zero_hit_sections
        observability_summary["retrieval_total_chunks"] = total_chunks_retrieved
        observability_summary["retrieval_phase_duration_ms"] = int((perf_counter() - retrieval_started_at) * 1000)
        observability_summary["retrieval_max_concurrent_sections"] = self._max_concurrent_retrieval_sections

        self._workflow_service.update(workflow_run_id, observability_summary=observability_summary)
        self._wf_cost_log(
            workflow_run_id,
            {
                "event": "retrieval_cost",
                "llm_cost_usd": retrieval_cost_tracker.llm_cost_usd,
                "embedding_cost_usd": total_embedding_cost_usd,
                "total_cost_usd": float(observability_summary.get("total_cost_usd", 0.0) or 0.0),
                "retrieved_sections": len(section_retrieval_results),
            },
        )

        logger.info(
            "retrieval.phase.completed workflow_run_id=%s retrieved_sections=%s retrieval_llm_cost_usd=%s "
            "embedding_cost_usd=%s total_chunks=%s zero_hit_sections=%s duration_ms=%s max_concurrent=%s",
            workflow_run_id,
            len(section_retrieval_results),
            retrieval_cost_tracker.llm_cost_usd,
            total_embedding_cost_usd,
            total_chunks_retrieved,
            zero_hit_sections,
            observability_summary["retrieval_phase_duration_ms"],
            self._max_concurrent_retrieval_sections,
        )



    async def _phase_generation(self, workflow_run_id: str) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        self._wf_log(workflow_run_id, "generation.phase.enter")
        section_plan = [SectionDefinition.model_validate(item) for item in (workflow.section_plan or [])]
        logger.info(
            "generation.enter workflow_run_id=%s sections=%s",
            workflow_run_id,
            len(section_plan),
        )
        if not section_plan:
            logger.info("generation.phase.skippednosections workflow_run_id=%s", workflow_run_id)
            self._workflow_service.update(workflow_run_id, current_step_label="Generation skipped (no sections)")
            return

        if self._generation_orchestrator is None:
            message = "Generation dependencies not configured"
            if self._is_local_env():
                logger.warning("generation.phase.skippedlocalmissingdependencies workflow_run_id=%s", workflow_run_id)
                self._workflow_service.update(workflow_run_id, current_step_label=f"{message} (local skip)")
                return
            raise WorkflowException(message)

        if not self._generation_orchestrator.is_configured():
            message = "Generation not configured (missing Azure credentials)"
            if self._is_local_env():
                logger.warning("generation.phase.skippedlocalnotconfigured workflow_run_id=%s", workflow_run_id)
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
        self._wf_cost_log(
            workflow_run_id,
            {
                "event": "generation_cost",
                "llm_cost_usd": cost_tracker.llm_cost_usd,
                "total_cost_usd": float(observability_summary.get("total_cost_usd", 0.0) or 0.0),
                "generated_sections": len(section_generation_results),
            },
        )
        logger.info(
            "generation.phase.completed workflow_run_id=%s completed=%s failed=%s llm_cost_usd=%s total_tokens_in=%s total_tokens_out=%s",
            workflow_run_id,
            completed,
            failed,
            cost_tracker.llm_cost_usd,
            cost_tracker.total_tokens_in,
            cost_tracker.total_tokens_out,
        )
        self._wf_log(
            workflow_run_id,
            "generation.phase.completed "
            f"completed={completed} failed={failed} llm_cost_usd={cost_tracker.llm_cost_usd}",
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
            logger.info("assembly.phase.skippednosections workflow_run_id=%s", workflow_run_id)
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
        logger.info(
            "assembly.phase.completed workflow_run_id=%s assembled_sections=%s warnings_added=%s",
            workflow_run_id,
            len(outcome.document.sections),
            len(outcome.warnings),
        )

    async def _phase_render_export(self, workflow_run_id: str) -> None:
        if self._output_service is None:
            logger.warning("renderexport.phase.skippednooutputservice workflow_run_id=%s", workflow_run_id)
            self._workflow_service.update(workflow_run_id, current_step_label="Export skipped (no output service)")
            return
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        logger.info(
            "renderexport.phase.enter workflow_run_id=%s",
            workflow_run_id,
        )
        ad = workflow.assembled_document or {}
        if not ad.get("sections"):
            logger.info("renderexport.phase.skippedemptydocument workflow_run_id=%s", workflow_run_id)
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
                placeholder_schema=template.placeholder_schema,
                section_placeholder_map=_resolved_section_placeholder_map(template),
            ),
            assembled=assembled,
            style_map=style_map,
            sheet_map=dict(workflow.sheet_map or {}),
        )
        wf2 = self._workflow_service.get_or_raise(workflow_run_id)
        render_warnings = list(wf2.warnings or []) + export_warnings
        has_critical_export_warning = any((w or {}).get("code") in SCHEMA_BLOCKING_CODES for w in export_warnings)
        has_docx_export_policy_block = any(
            (w or {}).get("code") in DOCX_EXPORT_POLICY_BLOCKING_CODES for w in export_warnings
        )
        has_docx_integrity_failure = any(
            (w or {}).get("code") in {
                "docx_header_footer_integrity_failed",
                "docx_relationship_integrity_failed",
                "docx_media_integrity_failed",
                "docx_forbidden_document_xml_mutation",
                "docx_document_part_missing",
            }
            for w in export_warnings
        )
        if workflow.doc_type == "UAT" and has_critical_export_warning:
            try:
                if out_path.exists():
                    out_path.unlink()
            except Exception:
                logger.exception("renderexport.cleanup.failed workflow_run_id=%s path=%s", workflow_run_id, str(out_path))
            raise WorkflowException("Critical schema mismatch detected during UAT export.")
        if has_docx_export_policy_block:
            try:
                if out_path.exists():
                    out_path.unlink()
            except Exception:
                logger.exception("renderexport.cleanup.failed workflow_run_id=%s path=%s", workflow_run_id, str(out_path))
            raise WorkflowException("Custom DOCX export blocked by template policy (see workflow warnings).")
        if settings.template_fidelity_media_integrity_blocking and has_docx_integrity_failure:
            try:
                if out_path.exists():
                    out_path.unlink()
            except Exception:
                logger.exception("renderexport.cleanup.failed workflow_run_id=%s path=%s", workflow_run_id, str(out_path))
            raise WorkflowException("Critical DOCX integrity mismatch detected during strict export.")

        record = self._output_service.create(
            workflow_run_id=workflow_run_id,
            document_id=document.document_id,
            doc_type=workflow.doc_type,
            file_path=out_path,
            filename=filename,
        )

        row_counts: dict[str, int] = {}
        for section in assembled.sections:
            content = (section.content or "").strip()
            row_counts[section.title] = len([line for line in content.splitlines() if line.strip().startswith("|")])

        schema_warning_count = len(
            [w for w in export_warnings if (w or {}).get("code") in {"schema_mismatch", "missing_required_columns"}]
        )
        warning_counts: dict[str, int] = {}
        for warn in export_warnings:
            code = str((warn or {}).get("code") or "").strip()
            if not code:
                continue
            warning_counts[code] = warning_counts.get(code, 0) + 1
        schema_compliance_rate = 1.0 if not assembled.sections else max(
            0.0, 1.0 - (schema_warning_count / len(assembled.sections))
        )
        observability_summary = dict(getattr(wf2, "observability_summary", None) or {})
        observability_summary["uat_sheet_row_counts"] = row_counts
        observability_summary["uat_schema_compliance_rate"] = schema_compliance_rate
        observability_summary["uat_low_evidence_sections"] = int(
            observability_summary.get("retrieval_zero_hit_sections", 0) or 0
        )
        observability_summary["uat_schema_warning_counts"] = warning_counts
        observability_summary["uat_schema_warning_codes"] = sorted(list(SCHEMA_WARNING_CODES))
        observability_summary["uat_schema_blocking_codes"] = sorted(list(SCHEMA_BLOCKING_CODES))
        observability_summary["header_footer_integrity"] = (
            "failed" if any(c == "docx_header_footer_integrity_failed" for c in warning_counts.keys()) else "pass"
        )
        observability_summary["media_integrity"] = (
            "failed"
            if any(c in {"docx_relationship_integrity_failed", "docx_media_integrity_failed"} for c in warning_counts.keys())
            else "pass"
        )
        self._workflow_service.update(
            workflow_run_id,
            output_id=record.output_id,
            warnings=render_warnings,
            current_step_label="Output file ready",
            observability_summary=observability_summary,
        )
        await self._event_service.emit(
            workflow_run_id,
            "output.ready",
            {"output_id": record.output_id, "filename": filename},
        )
        logger.info(
            "renderexport.phase.completed workflow_run_id=%s output_id=%s filename=%s warning_count=%s",
            workflow_run_id,
            record.output_id,
            filename,
            len(render_warnings),
        )

    async def _empty_retrieval_for_section(
        self,
        section: SectionDefinition,
    ) -> tuple[str, dict[str, object], float, int]:
        return (section.section_id, {"context_text": "", "citations": []}, 0.0, 0)

    async def _retrieve_one_section(
        self,
        document_id: str,
        section: SectionDefinition,
        cost_tracker: _RetrievalCostTracker,
    ) -> tuple[str, dict[str, object], float, int]:
        if self._section_retriever is None or self._evidence_packager is None:
            raise WorkflowException("Retrieval dependencies not configured.")

        chunks, embedding_cost_usd = await self._section_retriever.retrieve_for_section(
            section,
            document_id=document_id,
            cost_tracker=cost_tracker,
        )

        logger.info(
            "retrieval.section.completed document_id=%s section_id=%s chunk_count=%s embedding_cost_usd=%s",
            document_id,
            section.section_id,
            len(chunks),
            embedding_cost_usd,
        )

        bundle = self._evidence_packager.package(section.section_id, chunks)
        bundle_dict = {
            "context_text": bundle.context_text,
            "citations": [citation.model_dump() for citation in bundle.citations],
        }
        return section.section_id, bundle_dict, embedding_cost_usd, len(chunks)

    async def _run_ingestion_pipeline(
        self,
        workflow_run_id: str,
        document: DocumentRecord,
    ) -> IngestionRunResult:
        self._workflow_service.update(workflow_run_id, current_step_label="Parsing BRD document")
        file_path = Path(settings.documents_path) / document.file_path
        logger.info(
            "ingestion.pipeline.started workflow_run_id=%s document_id=%s file_path=%s content_type=%s",
            workflow_run_id,
            document.document_id,
            file_path,
            document.content_type,
        )
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
        self._wf_cost_log(
            workflow_run_id,
            {
                "event": "ingestion_cost",
                "embedding_cost_usd": result.embedding_cost_usd,
                "document_intelligence_cost_usd": result.document_intelligence_cost_usd,
                "total_cost_usd": float(merged.get("total_cost_usd", 0.0) or 0.0),
                "page_count": result.page_count,
                "indexed_chunk_count": result.chunk_count,
            },
        )
        logger.info(
            "ingestion.observability.updated workflow_run_id=%s embedding_cost_usd=%s document_intelligence_cost_usd=%s page_count=%s chunk_count=%s",
            workflow_run_id,
            result.embedding_cost_usd,
            result.document_intelligence_cost_usd,
            result.page_count,
            result.chunk_count,
        )

    def _is_local_env(self) -> bool:
        env = str(getattr(settings, "app_env", "") or "").strip().lower()
        return env in {"local", "development", "dev"}

    def _runtime_policy_mode(self) -> str:
        return "local-skip" if self._is_local_env() else "strict-fail"

    async def run(self, workflow_run_id: str) -> None:
        self._workflow_service.get_or_raise(workflow_run_id)
        logger.info("workflow.run.started workflow_run_id=%s", workflow_run_id)
        self._wf_log(workflow_run_id, "workflow.started")
        self._workflow_service.update(
            workflow_run_id,
            status=WorkflowStatus.RUNNING.value,
            started_at=utc_now_iso(),
            current_step_label="Workflow started",
        )
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        await self._event_service.emit(
            workflow_run_id,
            "workflow.started",
            {"doc_type": workflow.doc_type, "runtime_policy_mode": self._runtime_policy_mode()},
        )

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
            self._wf_cost_log(
                workflow_run_id,
                {
                    "event": "workflow_final_cost",
                    "status": WorkflowStatus.COMPLETED.value,
                    "total_cost_usd": total_cost,
                    "llm_cost_usd": float(summary.get("llm_cost_usd", 0.0) or 0.0),
                    "embedding_cost_usd": float(summary.get("embedding_cost_usd", 0.0) or 0.0),
                    "document_intelligence_cost_usd": float(summary.get("document_intelligence_cost_usd", 0.0) or 0.0),
                },
            )
            try:
                await self._event_service.emit(
                    workflow_run_id,
                    "workflow.completed",
                    {"output_id": workflow.output_id, "total_cost_usd": total_cost},
                )
            except Exception:
                logger.exception(
                    "workflow.emit.completedfailed workflow_run_id=%s",
                    workflow_run_id,
                )
            logger.info("workflow.run.completed workflow_run_id=%s", workflow_run_id)
            self._wf_log(workflow_run_id, "workflow.completed")
        except Exception as exc:
            logger.exception(
                "workflow.failed workflow_run_id=%s error=%s",
                workflow_run_id,
                str(exc),
            )
            self._wf_log(workflow_run_id, f"workflow.failed error={str(exc)}", level="ERROR")
            snapshot = self._workflow_service.get_or_raise(workflow_run_id)
            summary = dict(getattr(snapshot, "observability_summary", None) or {})
            self._wf_cost_log(
                workflow_run_id,
                {
                    "event": "workflow_final_cost",
                    "status": WorkflowStatus.FAILED.value,
                    "total_cost_usd": float(summary.get("total_cost_usd", 0.0) or 0.0),
                    "llm_cost_usd": float(summary.get("llm_cost_usd", 0.0) or 0.0),
                    "embedding_cost_usd": float(summary.get("embedding_cost_usd", 0.0) or 0.0),
                    "document_intelligence_cost_usd": float(summary.get("document_intelligence_cost_usd", 0.0) or 0.0),
                    "error": str(exc),
                },
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
                    "workflow.emit.failedfailed workflow_run_id=%s",
                    workflow_run_id,
                )
            # Do not re-raise: failure is persisted; terminal emit is best-effort for SSE clients.
