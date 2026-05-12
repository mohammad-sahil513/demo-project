"""Phase 8 (GENERATION) tests: orchestrator, generators, cost tracking, prompts.

Exercises the full generation surface:

- Text / table / diagram generators with stubbed Azure responses.
- :func:`compute_execution_waves` honors ``dependencies`` and orders by
  ``execution_order`` within each wave.
- Diagram fallback chain (PlantUML -> Mermaid -> deterministic stub).
- :class:`GenerationCostTracker` snapshots accumulate per model/task and
  surface in the workflow observability merge.
- Prompt loader resolves YAML files and merges the shared deliverable
  policy fragment.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import pytest
from core.config import settings
from core.exceptions import GenerationException
from core.ids import utc_now_iso
from modules.generation.context import build_prompt_mapping
from modules.generation.cost_tracking import GenerationCostTracker
from modules.generation.diagram_generator import DiagramSectionGenerator, extract_mermaid, extract_plantuml
from modules.generation.models import GenerationSectionResult
from modules.generation.orchestrator import GenerationOrchestrator, compute_execution_waves
from modules.generation.prompt_loader import GenerationPromptLoader
from modules.generation.table_generator import TableSectionGenerator
from modules.generation.text_generator import TextSectionGenerator
from modules.template.models import SectionDefinition
from repositories.document_models import DocumentRecord
from repositories.document_repo import DocumentRepository
from repositories.template_repo import TemplateRepository
from repositories.workflow_repo import WorkflowRepository
from services.event_service import EventService
from services.workflow_executor import WorkflowExecutor
from services.workflow_service import WorkflowService
from core.logging import get_workflow_cost_log_path, get_workflow_log_path


def test_prompt_loader_renders_with_defaults() -> None:
    loader = GenerationPromptLoader()
    template = loader.load_template("text", "default")
    section = SectionDefinition(
        section_id="sec-1",
        title="Overview",
        description="Scope and purpose",
        execution_order=0,
        prompt_selector="default",
    )
    mapping = build_prompt_mapping(section, "PDD", "Evidence line")
    rendered = loader.render_template(template, mapping)
    assert "Overview" in rendered
    assert "Evidence line" in rendered


def test_extract_plantuml_and_mermaid() -> None:
    puml = "```plantuml\n@startuml\nA -> B\n@enduml\n```"
    assert "@startuml" in extract_plantuml(puml)
    mer = "```mermaid\nflowchart TD\n  A-->B\n```"
    out = extract_mermaid(mer)
    assert "flowchart TD" in out


def test_compute_execution_waves_orders_dependencies() -> None:
    a = SectionDefinition(section_id="a", title="A", execution_order=0, dependencies=[])
    b = SectionDefinition(section_id="b", title="B", execution_order=1, dependencies=["a"])
    c = SectionDefinition(section_id="c", title="C", execution_order=2, dependencies=["a"])
    waves = compute_execution_waves([b, c, a])
    assert len(waves) == 2
    assert {s.section_id for s in waves[0]} == {"a"}
    assert {s.section_id for s in waves[1]} == {"b", "c"}


def test_orchestrator_parent_title_prefers_parent_section_id() -> None:
    orch = GenerationOrchestrator.__new__(GenerationOrchestrator)
    s1 = SectionDefinition(section_id="p", title="Parent", execution_order=1, level=1)
    s2 = SectionDefinition(
        section_id="c",
        title="Child",
        execution_order=2,
        level=2,
        parent_section_id="p",
    )
    ordered = [s1, s2]
    id_to_title = {s.section_id: s.title for s in ordered}
    assert orch._find_parent_title(ordered, "c", id_to_title) == "Parent"


def test_orchestrator_parent_title_mismatch_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    orch = GenerationOrchestrator.__new__(GenerationOrchestrator)
    s1 = SectionDefinition(section_id="wrong", title="WrongParent", execution_order=1, level=1)
    s2 = SectionDefinition(section_id="c", title="Child", execution_order=2, level=2, parent_section_id="p")
    s0 = SectionDefinition(section_id="p", title="RightParent", execution_order=0, level=1)
    ordered = [s0, s1, s2]
    id_to_title = {s.section_id: s.title for s in ordered}
    with caplog.at_level(logging.WARNING):
        title = orch._find_parent_title(ordered, "c", id_to_title)
    assert title == "RightParent"
    assert any("generation.hierarchy.mismatch" in r.message for r in caplog.records)


def test_orchestrator_collect_child_titles_uses_direct_parent_ids() -> None:
    s1 = SectionDefinition(section_id="p", title="P", execution_order=1, level=1)
    s2 = SectionDefinition(section_id="a", title="A", execution_order=2, level=2, parent_section_id="p")
    s3 = SectionDefinition(section_id="b", title="B", execution_order=3, level=2, parent_section_id="p")
    ordered = [s1, s2, s3]
    id_to_title = {s.section_id: s.title for s in ordered}
    assert GenerationOrchestrator._collect_child_titles(ordered, "p", id_to_title) == ["A", "B"]


class _NeverCallLlm:
    def is_configured(self) -> bool:
        return True

    async def invoke_text(self, *args: object, **kwargs: object) -> str:
        raise AssertionError("LLM should not run for content_mode skip/heading_only")


def test_generate_one_skips_llm_when_content_mode_skip(tmp_path: Path) -> None:
    async def _run() -> None:
        orch = GenerationOrchestrator(
            TextSectionGenerator(_NeverCallLlm()),  # type: ignore[arg-type]
            TableSectionGenerator(_NeverCallLlm()),  # type: ignore[arg-type]
            DiagramSectionGenerator(
                _NeverCallLlm(),  # type: ignore[arg-type]
                kroki=_FakeKroki(),  # type: ignore[arg-type]
                storage_root=tmp_path,
            ),
        )
        section = SectionDefinition(
            section_id="s-skip",
            title="Outline",
            execution_order=0,
            output_type="text",
            content_mode="skip",
        )
        out = await orch._generate_one(
            workflow_run_id="wf-x",
            section=section,
            retrieval_payload={"context_text": "x", "citations": []},
            doc_type="PDD",
            cost_tracker=GenerationCostTracker(),
            emit=None,
            parent_title=None,
            child_titles=[],
        )
        assert out.get("task") == "content_mode_skip"
        assert out.get("error") is None

    asyncio.run(_run())


def test_compute_execution_waves_logs_when_dependency_cycle(caplog: pytest.LogCaptureFixture) -> None:
    a = SectionDefinition(section_id="a", title="A", execution_order=0, dependencies=["b"])
    b = SectionDefinition(section_id="b", title="B", execution_order=1, dependencies=["a"])
    with caplog.at_level(logging.WARNING):
        waves = compute_execution_waves([a, b])
    assert any("dependency graph stalled" in rec.message for rec in caplog.records)
    assert sum(len(w) for w in waves) == 2


def test_generation_section_result_model_accepts_executor_shape() -> None:
    row = GenerationSectionResult.model_validate(
        {
            "output_type": "text",
            "content": "body",
            "diagram_path": None,
            "diagram_format": None,
            "tokens_in": 1,
            "tokens_out": 2,
            "cost_usd": 0.001,
            "model": "gpt5mini",
            "task": "text_generation",
            "error": None,
            "citations": [{"path": "Doc", "page": 1, "content_type": "text", "chunk_id": "c1"}],
        },
    )
    dumped = row.model_dump()
    assert dumped["output_type"] == "text"
    assert dumped["citations"][0]["chunk_id"] == "c1"


class _FakeKroki:
    def __init__(self) -> None:
        self.plant_calls = 0
        self.mermaid_calls = 0

    def is_configured(self) -> bool:
        return True

    async def render_png(self, diagram_type: str, source: str) -> bytes:
        if diagram_type == "plantuml":
            self.plant_calls += 1
            if "FIXED" not in source:
                raise GenerationException("invalid plantuml", code="KROKI_RENDER_FAILED")
            return b"\x89PNG\r\n\x1a\n\x00"
        if diagram_type == "mermaid":
            self.mermaid_calls += 1
            return b"\x89PNG\r\n\x1a\n\x01"
        raise GenerationException("unknown diagram type", code="KROKI_RENDER_FAILED")


class _FakeDiagramSk:
    def is_configured(self) -> bool:
        return True

    async def invoke_text(self, prompt: str, *, task: str, cost_tracker=None) -> str:
        del prompt, cost_tracker
        if task == "diagram_generation":
            return "@startuml\nbroken\n@enduml"
        if task == "diagram_correction":
            return "@startuml\nAlice -> Bob : FIXED\n@enduml"
        msg = f"unexpected {task}"
        raise AssertionError(msg)


def test_diagram_generator_retries_plantuml_then_writes_png(tmp_path: Path) -> None:
    async def _run() -> None:
        kroki = _FakeKroki()
        gen = DiagramSectionGenerator(
            _FakeDiagramSk(),  # type: ignore[arg-type]
            kroki=kroki,  # type: ignore[arg-type]
            storage_root=tmp_path,
        )
        section = SectionDefinition(
            section_id="sec-dia",
            title="Architecture",
            description="Diagram",
            execution_order=0,
            output_type="diagram",
        )
        tracker = GenerationCostTracker()
        result = await gen.generate(
            workflow_run_id="wf-test",
            section=section,
            retrieval_payload={"context_text": "SysA talks to SysB", "citations": []},
            doc_type="PDD",
            cost_tracker=tracker,
        )
        assert result.get("error") is None
        assert result.get("diagram_format") == "plantuml"
        path = result.get("diagram_path")
        assert isinstance(path, str)
        assert (tmp_path / path).is_file()
        assert kroki.plant_calls >= 2
        assert kroki.mermaid_calls == 0

    asyncio.run(_run())


class _MermaidFallbackSk:
    def __init__(self) -> None:
        self.n = 0

    def is_configured(self) -> bool:
        return True

    async def invoke_text(self, prompt: str, *, task: str, cost_tracker=None) -> str:
        del prompt, cost_tracker
        self.n += 1
        if task in ("diagram_generation", "diagram_correction"):
            if self.n <= 6:
                return "@startuml\nstill bad\n@enduml"
        if task == "diagram_generation" and self.n > 6:
            return "flowchart TD\n  A-->B\n"
        msg = f"unexpected task {task} n={self.n}"
        raise AssertionError(msg)


class _KrokiPlantFailMermaidOk:
    def __init__(self) -> None:
        self.plant = 0
        self.mermaid = 0

    def is_configured(self) -> bool:
        return True

    async def render_png(self, diagram_type: str, source: str) -> bytes:
        if diagram_type == "plantuml":
            self.plant += 1
            raise GenerationException("plantuml fail", code="X")
        if diagram_type == "mermaid":
            self.mermaid += 1
            if "flowchart" not in source:
                raise GenerationException("bad mermaid", code="X")
            return b"\x89PNG\r\n\x1a\n\x02"
        raise GenerationException("no", code="X")


def test_diagram_generator_falls_back_to_mermaid(tmp_path: Path) -> None:
    async def _run() -> None:
        kroki = _KrokiPlantFailMermaidOk()
        gen = DiagramSectionGenerator(
            _MermaidFallbackSk(),  # type: ignore[arg-type]
            kroki=kroki,  # type: ignore[arg-type]
            storage_root=tmp_path,
        )
        section = SectionDefinition(
            section_id="sec-m",
            title="Flow",
            description="Flow",
            execution_order=0,
            output_type="diagram",
        )
        result = await gen.generate(
            workflow_run_id="wf-m",
            section=section,
            retrieval_payload={"context_text": "Step1 then Step2", "citations": []},
            doc_type="SDD",
            cost_tracker=GenerationCostTracker(),
        )
        assert result.get("error") is None
        assert result.get("diagram_format") == "mermaid"
        assert kroki.mermaid >= 1

    asyncio.run(_run())


class _RecordingEventService(EventService):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[tuple[str, dict[str, object] | None]] = []

    async def emit(self, workflow_run_id: str, event_type: str, payload: dict[str, object] | None = None) -> None:
        self.events.append((event_type, payload))
        await super().emit(workflow_run_id, event_type, payload)


class _TableSk:
    def is_configured(self) -> bool:
        return True

    async def invoke_text(self, prompt: str, *, task: str, cost_tracker=None) -> str:
        del prompt
        assert task == "table_generation"
        if cost_tracker:
            cost_tracker.track_call(model="gpt-5-mini", task=task, input_tokens=12, output_tokens=6)
        return "| A | B |\n| --- | --- |\n| x | y |"


class _TableSkCapturePrompt(_TableSk):
    def __init__(self) -> None:
        self.last_prompt: str = ""

    async def invoke_text(self, prompt: str, *, task: str, cost_tracker=None) -> str:
        self.last_prompt = prompt
        return await super().invoke_text(prompt, task=task, cost_tracker=cost_tracker)


def test_table_generator_includes_hierarchy_in_prompt() -> None:
    async def _run() -> None:
        cap = _TableSkCapturePrompt()
        gen = TableSectionGenerator(cap)  # type: ignore[arg-type]
        section = SectionDefinition(
            section_id="sec-tab",
            title="Child table",
            description="",
            execution_order=2,
            output_type="table",
            level=2,
            table_headers=["C1", "C2"],
        )
        await gen.generate(
            section=section,
            retrieval_payload={"context_text": "evidence", "citations": []},
            doc_type="PDD",
            cost_tracker=GenerationCostTracker(),
            parent_title="Parent section",
            child_titles=["Later sibling"],
        )
        assert "Parent section" in cap.last_prompt
        assert "child_or_leaf" in cap.last_prompt or "Later sibling" in cap.last_prompt

    asyncio.run(_run())


class _TextSk:
    def is_configured(self) -> bool:
        return True

    async def invoke_text(self, prompt: str, *, task: str, cost_tracker=None) -> str:
        del prompt
        assert task == "text_generation"
        if cost_tracker:
            cost_tracker.track_call(model="gpt-5-mini", task=task, input_tokens=8, output_tokens=4)
        return "## Section body"


def test_workflow_executor_generation_phase_persists_and_emits(tmp_path: Path) -> None:
    async def _run() -> None:
        now = utc_now_iso()
        document_repo = DocumentRepository(Path(tmp_path) / "documents")
        template_repo = TemplateRepository(Path(tmp_path) / "templates")
        workflow_repo = WorkflowRepository(Path(tmp_path) / "workflows")
        workflow_service = WorkflowService(workflow_repo, document_repo=document_repo, template_repo=template_repo)
        document_repo.save(
            DocumentRecord(
                document_id="doc-g",
                filename="sample.pdf",
                content_type="application/pdf",
                size_bytes=10,
                file_path="doc-g.bin",
                created_at=now,
                updated_at=now,
            ),
        )
        workflow = workflow_service.create(document_id="doc-g", template_id="tpl-inbuilt-pdd", doc_type="PDD")
        citations = [{"path": "Doc", "page": 1, "content_type": "text", "chunk_id": "c1"}]
        workflow_service.update(
            workflow.workflow_run_id,
            section_plan=[
                {
                    "section_id": "sec-t",
                    "title": "Intro",
                    "description": "Intro",
                    "execution_order": 0,
                    "output_type": "text",
                    "retrieval_query": "intro scope",
                    "prompt_selector": "default",
                },
                {
                    "section_id": "sec-tab",
                    "title": "Matrix",
                    "description": "Matrix",
                    "execution_order": 1,
                    "output_type": "table",
                    "retrieval_query": "matrix",
                    "table_headers": ["Col1", "Col2"],
                    "prompt_selector": "default",
                },
            ],
            section_retrieval_results={
                "sec-t": {"context_text": "ctx1", "citations": citations},
                "sec-tab": {"context_text": "ctx2", "citations": citations},
            },
            observability_summary={"llm_cost_usd": 0.01},
        )
        events = _RecordingEventService()
        orch = GenerationOrchestrator(
            TextSectionGenerator(_TextSk()),  # type: ignore[arg-type]
            TableSectionGenerator(_TableSk()),  # type: ignore[arg-type]
            DiagramSectionGenerator(
                _TextSk(),  # type: ignore[arg-type] — unused in this workflow
                kroki=_FakeKroki(),  # type: ignore[arg-type]
                storage_root=Path(tmp_path),
            ),
        )
        executor = WorkflowExecutor(
            workflow_service=workflow_service,
            event_service=events,
            generation_orchestrator=orch,
        )
        await executor._phase_generation(workflow.workflow_run_id)

        updated = workflow_service.get_or_raise(workflow.workflow_run_id)
        assert set(updated.section_generation_results.keys()) == {"sec-t", "sec-tab"}
        row_t = updated.section_generation_results["sec-t"]
        assert isinstance(row_t, dict)
        assert row_t.get("output_type") == "text"
        assert row_t.get("citations") == citations
        types = [e[0] for e in events.events]
        assert types.count("section.generation.started") == 2
        assert types.count("section.generation.completed") == 2
        assert float(updated.observability_summary.get("llm_cost_usd", 0)) > 0.01
        assert get_workflow_log_path(workflow.workflow_run_id).is_file()
        cost_log = get_workflow_cost_log_path(workflow.workflow_run_id)
        assert cost_log.is_file()
        assert "generation_cost" in cost_log.read_text(encoding="utf-8")

    asyncio.run(_run())


def test_workflow_executor_generation_skips_when_not_configured_non_local(tmp_path: Path) -> None:
    async def _run() -> None:
        now = utc_now_iso()
        document_repo = DocumentRepository(Path(tmp_path) / "documents")
        template_repo = TemplateRepository(Path(tmp_path) / "templates")
        workflow_repo = WorkflowRepository(Path(tmp_path) / "workflows")
        workflow_service = WorkflowService(workflow_repo, document_repo=document_repo, template_repo=template_repo)
        document_repo.save(
            DocumentRecord(
                document_id="doc-x",
                filename="sample.pdf",
                content_type="application/pdf",
                size_bytes=10,
                file_path="doc-x.bin",
                created_at=now,
                updated_at=now,
            ),
        )
        workflow = workflow_service.create(document_id="doc-x", template_id="tpl-inbuilt-pdd", doc_type="PDD")
        workflow_service.update(
            workflow.workflow_run_id,
            section_plan=[
                {
                    "section_id": "sec-1",
                    "title": "A",
                    "description": "A",
                    "execution_order": 0,
                    "output_type": "text",
                },
            ],
        )

        class _Off:
            def is_configured(self) -> bool:
                return False

        orch = GenerationOrchestrator(
            TextSectionGenerator(_Off()),  # type: ignore[arg-type]
            TableSectionGenerator(_Off()),  # type: ignore[arg-type]
            DiagramSectionGenerator(
                _Off(),  # type: ignore[arg-type]
                kroki=_Off(),  # type: ignore[arg-type]
                storage_root=Path(tmp_path),
            ),
        )
        executor = WorkflowExecutor(
            workflow_service=workflow_service,
            event_service=EventService(),
            generation_orchestrator=orch,
        )
        old = settings.app_env
        settings.app_env = "production"
        try:
            with pytest.raises(Exception, match="Generation not configured"):
                await executor._phase_generation(workflow.workflow_run_id)
        finally:
            settings.app_env = old

    asyncio.run(_run())


def test_workflow_run_failed_writes_terminal_cost_log(tmp_path: Path) -> None:
    async def _run() -> None:
        now = utc_now_iso()
        document_repo = DocumentRepository(Path(tmp_path) / "documents")
        template_repo = TemplateRepository(Path(tmp_path) / "templates")
        workflow_repo = WorkflowRepository(Path(tmp_path) / "workflows")
        workflow_service = WorkflowService(workflow_repo, document_repo=document_repo, template_repo=template_repo)
        document_repo.save(
            DocumentRecord(
                document_id="doc-f",
                filename="sample.pdf",
                content_type="application/pdf",
                size_bytes=10,
                file_path="doc-f.bin",
                created_at=now,
                updated_at=now,
            ),
        )
        workflow = workflow_service.create(document_id="doc-f", template_id="tpl-inbuilt-pdd", doc_type="PDD")
        workflow_service.update(
            workflow.workflow_run_id,
            observability_summary={
                "llm_cost_usd": 0.12,
                "embedding_cost_usd": 0.34,
                "document_intelligence_cost_usd": 0.56,
                "total_cost_usd": 1.02,
            },
        )
        executor = WorkflowExecutor(
            workflow_service=workflow_service,
            event_service=EventService(),
            section_retriever=None,
            evidence_packager=None,
        )
        old_env = settings.app_env
        settings.app_env = "production"
        try:
            await executor.run(workflow.workflow_run_id)
        finally:
            settings.app_env = old_env
        updated = workflow_service.get_or_raise(workflow.workflow_run_id)
        assert updated.status == "FAILED"
        cost_log = get_workflow_cost_log_path(workflow.workflow_run_id)
        body = cost_log.read_text(encoding="utf-8")
        assert "workflow_final_cost" in body
        assert "\"status\": \"FAILED\"" in body
        assert "\"total_cost_usd\": 1.02" in body

    asyncio.run(_run())
