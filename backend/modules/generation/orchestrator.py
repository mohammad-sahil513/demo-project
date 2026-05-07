"""Parallel, dependency-aware section generation orchestration."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from time import perf_counter
from typing import Any

from core.exceptions import SDLCBaseException
from core.logging import get_logger
from modules.generation.context import citations_from_retrieval
from modules.generation.cost_tracking import GenerationCostTracker
from modules.generation.diagram_generator import DiagramSectionGenerator
from modules.generation.table_generator import TableSectionGenerator
from modules.generation.text_generator import TextSectionGenerator
from modules.template.models import SectionDefinition

logger = get_logger(__name__)

EmitFn = Callable[[str, str, dict[str, object] | None], Awaitable[None]]

DEFAULT_MAX_CONCURRENT_SECTIONS = 3


def compute_execution_waves(sections: list[SectionDefinition]) -> list[list[SectionDefinition]]:
    """Group sections into waves so dependencies run before dependents."""
    remaining: dict[str, SectionDefinition] = {s.section_id: s for s in sections}
    completed: set[str] = set()
    waves: list[list[SectionDefinition]] = []

    while remaining:
        wave = [
            s
            for s in remaining.values()
            if all(dep in completed for dep in (s.dependencies or []))
        ]

        if not wave:
            fallback = sorted(remaining.values(), key=lambda x: x.execution_order)[0]
            logger.warning(
                "generation.graph.stalled detail=dependency graph stalled "
                "section_id=%s remaining_ids=%s",
                fallback.section_id,
                sorted(remaining.keys()),
            )
            wave = [fallback]

        for s in wave:
            del remaining[s.section_id]

        waves.append(wave)
        completed.update(s.section_id for s in wave)

    return waves


class GenerationOrchestrator:
    def __init__(
        self,
        text_generator: TextSectionGenerator,
        table_generator: TableSectionGenerator,
        diagram_generator: DiagramSectionGenerator,
        *,
        max_concurrent_sections: int = DEFAULT_MAX_CONCURRENT_SECTIONS,
    ) -> None:
        self._text = text_generator
        self._table = table_generator
        self._diagram = diagram_generator
        self._max_concurrent = max(1, int(max_concurrent_sections))
        self._semaphore = asyncio.Semaphore(self._max_concurrent)

    def is_configured(self) -> bool:
        return (
            self._text.is_configured()
            and self._table.is_configured()
            and self._diagram.is_configured()
        )

    async def run_all_sections(
        self,
        *,
        workflow_run_id: str,
        sections: list[SectionDefinition],
        section_retrieval_results: dict[str, object],
        doc_type: str,
        cost_tracker: GenerationCostTracker,
        emit: EmitFn | None = None,
    ) -> dict[str, dict[str, Any]]:
        ordered = sorted(sections, key=lambda s: s.execution_order)
        waves = compute_execution_waves(ordered)

        logger.info(
            "generation.orchestrator.start workflow_run_id=%s "
            "total_sections=%s wave_count=%s max_concurrent=%s",
            workflow_run_id,
            len(ordered),
            len(waves),
            self._max_concurrent,
        )

        results: dict[str, dict[str, Any]] = {}
        id_to_title = {s.section_id: s.title for s in ordered}

        for wave_index, wave in enumerate(waves, start=1):
            logger.info(
                "generation.wave.started workflow_run_id=%s wave_index=%s "
                "wave_size=%s section_ids=%s",
                workflow_run_id,
                wave_index,
                len(wave),
                [s.section_id for s in wave],
            )

            tasks: list[Awaitable[dict[str, Any]]] = []
            for section in wave:
                parent_title = self._find_parent_title(ordered, section.section_id, id_to_title)
                child_titles = self._collect_child_titles(ordered, section.section_id, id_to_title)

                tasks.append(
                    self._run_with_semaphore(
                        self._generate_one(
                            workflow_run_id=workflow_run_id,
                            section=section,
                            retrieval_payload=self._payload_for_section(
                                section_retrieval_results,
                                section.section_id,
                            ),
                            doc_type=doc_type,
                            cost_tracker=cost_tracker,
                            emit=emit,
                            parent_title=parent_title,
                            child_titles=child_titles,
                        )
                    )
                )

            outputs = await asyncio.gather(*tasks)

            for section, out in zip(wave, outputs):
                results[section.section_id] = out

            failures = sum(1 for out in outputs if out.get("error"))
            logger.info(
                "generation.wave.completed workflow_run_id=%s wave_index=%s "
                "completed=%s failed=%s",
                workflow_run_id,
                wave_index,
                len(outputs) - failures,
                failures,
            )

        logger.info(
            "generation.orchestrator.completed workflow_run_id=%s generated_sections=%s",
            workflow_run_id,
            len(results),
        )
        return results

    async def _run_with_semaphore(self, coro: Awaitable[dict[str, Any]]) -> dict[str, Any]:
        async with self._semaphore:
            return await coro

    @staticmethod
    def _payload_for_section(
        store: dict[str, object],
        section_id: str,
    ) -> dict[str, object] | None:
        raw = store.get(section_id)
        if isinstance(raw, dict):
            return dict(raw)
        return None

    @staticmethod
    def _parent_title_level_scan(
        ordered_sections: list[SectionDefinition],
        section_id: str,
    ) -> str | None:
        current_index = next(
            (idx for idx, sec in enumerate(ordered_sections) if sec.section_id == section_id),
            None,
        )
        if current_index is None:
            return None

        current = ordered_sections[current_index]
        current_level = int(current.level)

        for idx in range(current_index - 1, -1, -1):
            candidate = ordered_sections[idx]
            if int(candidate.level) < current_level:
                return candidate.title

        return None

    def _find_parent_title(
        self,
        ordered_sections: list[SectionDefinition],
        section_id: str,
        id_to_title: dict[str, str],
    ) -> str | None:
        current_index = next(
            (idx for idx, sec in enumerate(ordered_sections) if sec.section_id == section_id),
            None,
        )
        if current_index is None:
            return None

        current = ordered_sections[current_index]
        by_parent_id: str | None = None
        pid = current.parent_section_id
        if pid and pid in id_to_title:
            by_parent_id = id_to_title[pid]

        by_level = self._parent_title_level_scan(ordered_sections, section_id)

        if by_parent_id and by_level and by_parent_id != by_level:
            logger.warning(
                "generation.hierarchy.mismatch section_id=%s parent_section_id=%s "
                "parent_title_by_id=%s parent_title_by_level=%s",
                section_id,
                pid,
                by_parent_id,
                by_level,
            )

        if by_parent_id:
            return by_parent_id
        return by_level

    @staticmethod
    def _collect_child_titles_level_walk(
        ordered_sections: list[SectionDefinition],
        section_id: str,
    ) -> list[str]:
        current_index = next(
            (idx for idx, sec in enumerate(ordered_sections) if sec.section_id == section_id),
            None,
        )
        if current_index is None:
            return []

        current = ordered_sections[current_index]
        current_level = int(current.level)
        child_titles: list[str] = []

        for next_section in ordered_sections[current_index + 1:]:
            next_level = int(next_section.level)
            if next_level <= current_level:
                break
            child_titles.append(next_section.title)

        return child_titles

    @staticmethod
    def _collect_child_titles(
        ordered_sections: list[SectionDefinition],
        section_id: str,
        id_to_title: dict[str, str],
    ) -> list[str]:
        current_index = next(
            (idx for idx, sec in enumerate(ordered_sections) if sec.section_id == section_id),
            None,
        )
        if current_index is None:
            return []

        current = ordered_sections[current_index]
        direct: list[str] = []
        for sec in ordered_sections:
            if sec.parent_section_id == current.section_id:
                direct.append(sec.title)

        if direct:
            return direct

        return GenerationOrchestrator._collect_child_titles_level_walk(ordered_sections, section_id)

    async def _generate_one(
        self,
        *,
        workflow_run_id: str,
        section: SectionDefinition,
        retrieval_payload: dict[str, object] | None,
        doc_type: str,
        cost_tracker: GenerationCostTracker,
        emit: EmitFn | None,
        parent_title: str | None,
        child_titles: list[str],
    ) -> dict[str, Any]:
        citations = citations_from_retrieval(retrieval_payload)
        started_at = perf_counter()

        logger.info(
            "generation.section.started workflow_run_id=%s section_id=%s "
            "output_type=%s has_retrieval_payload=%s citation_count=%s "
            "parent_title=%s child_count=%s",
            workflow_run_id,
            section.section_id,
            section.output_type,
            retrieval_payload is not None,
            len(citations),
            parent_title,
            len(child_titles),
        )

        if emit:
            await emit(
                workflow_run_id,
                "section.generation.started",
                {
                    "section_id": section.section_id,
                    "output_type": section.output_type,
                },
            )

        if section.content_mode == "skip":
            result = {
                "output_type": section.output_type,
                "content": "",
                "diagram_path": None,
                "diagram_format": None,
                "tokens_in": 0,
                "tokens_out": 0,
                "cost_usd": 0.0,
                "model": "",
                "task": "content_mode_skip",
                "error": None,
            }
        elif section.content_mode == "heading_only":
            result = {
                "output_type": "text",
                "content": "",
                "diagram_path": None,
                "diagram_format": None,
                "tokens_in": 0,
                "tokens_out": 0,
                "cost_usd": 0.0,
                "model": "",
                "task": "content_mode_heading_only",
                "error": None,
            }
        else:
            try:
                if section.output_type == "text":
                    result = await self._text.generate(
                        section=section,
                        retrieval_payload=retrieval_payload,
                        doc_type=doc_type,
                        cost_tracker=cost_tracker,
                        parent_title=parent_title,
                        child_titles=child_titles,
                    )
                elif section.output_type == "table":
                    result = await self._table.generate(
                        section=section,
                        retrieval_payload=retrieval_payload,
                        doc_type=doc_type,
                        cost_tracker=cost_tracker,
                        parent_title=parent_title,
                        child_titles=child_titles,
                    )
                elif section.output_type == "diagram":
                    result = await self._diagram.generate(
                        workflow_run_id=workflow_run_id,
                        section=section,
                        retrieval_payload=retrieval_payload,
                        doc_type=doc_type,
                        cost_tracker=cost_tracker,
                        parent_title=parent_title,
                        child_titles=child_titles,
                    )
                else:
                    result = {
                        "output_type": str(section.output_type),
                        "content": "",
                        "diagram_path": None,
                        "diagram_format": None,
                        "tokens_in": 0,
                        "tokens_out": 0,
                        "cost_usd": 0.0,
                        "model": "",
                        "task": "",
                        "error": f"Unsupported output_type: {section.output_type}",
                    }

            except asyncio.CancelledError:
                raise
            except SDLCBaseException as exc:
                result = {
                    "output_type": section.output_type,
                    "content": "",
                    "diagram_path": None,
                    "diagram_format": None,
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "cost_usd": 0.0,
                    "model": "",
                    "task": "",
                    "error": exc.message,
                }
            except Exception as exc:
                logger.exception(
                    "generation.section.failed",
                    extra={
                        "section_id": section.section_id,
                        "workflow_run_id": workflow_run_id,
                    },
                )
                result = {
                    "output_type": section.output_type,
                    "content": "",
                    "diagram_path": None,
                    "diagram_format": None,
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "cost_usd": 0.0,
                    "model": "",
                    "task": "",
                    "error": str(exc),
                }

        result["citations"] = citations
        duration_ms = int((perf_counter() - started_at) * 1000)

        logger.info(
            "generation.section.completed workflow_run_id=%s section_id=%s "
            "output_type=%s duration_ms=%s error=%s tokens_in=%s tokens_out=%s",
            workflow_run_id,
            section.section_id,
            result.get("output_type"),
            duration_ms,
            result.get("error"),
            result.get("tokens_in"),
            result.get("tokens_out"),
        )

        if emit:
            await emit(
                workflow_run_id,
                "section.generation.completed",
                {
                    "section_id": section.section_id,
                    "output_type": result.get("output_type"),
                    "error": result.get("error"),
                },
            )

        return result
