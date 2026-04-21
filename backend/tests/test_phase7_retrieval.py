from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest
from core.config import settings
from core.ids import utc_now_iso
from modules.retrieval.packager import EvidencePackager
from modules.retrieval.retriever import RetrievedChunk, SectionRetriever
from modules.template.models import SectionDefinition
from repositories.document_models import DocumentRecord
from repositories.document_repo import DocumentRepository
from repositories.template_repo import TemplateRepository
from repositories.workflow_repo import WorkflowRepository
from services.event_service import EventService
from services.workflow_executor import WorkflowExecutor
from services.workflow_service import WorkflowService


class _FakeSearchClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def is_configured(self) -> bool:
        return True

    async def hybrid_search(
        self,
        *,
        search_text: str,
        embedding: list[float],
        document_id: str,
        top_k: int = 5,
    ) -> list[dict[str, object]]:
        self.calls.append(
            {
                "search_text": search_text,
                "embedding": embedding,
                "document_id": document_id,
                "top_k": top_k,
            },
        )
        return [
            {
                "chunk_id": "doc-1:chunk:000001",
                "text": "Business requirement details",
                "section_heading": "2.3 Business Requirements",
                "page_number": 8,
                "content_type": "text",
                "@search.score": 1.23,
            },
            {
                "chunk_id": "doc-1:chunk:000002",
                "text": "| Constraint | Value |",
                "section_heading": "4.1 Technical Constraints",
                "page_number": 12,
                "content_type": "table",
                "@search.score": 1.11,
            },
        ]


class _FakeSKAdapter:
    def __init__(self) -> None:
        self.query_prompts: list[str] = []

    def is_configured(self) -> bool:
        return True

    async def invoke_text(self, prompt: str, *, task: str, cost_tracker=None) -> str:
        assert task == "retrieval_query_generation"
        self.query_prompts.append(prompt)
        if hasattr(cost_tracker, "track_call"):
            cost_tracker.track_call(model="gpt5mini", task=task, input_tokens=20, output_tokens=8)
        return "security requirements identity access controls policy coverage"

    async def generate_embedding_with_usage(self, text: str):
        return SimpleNamespace(embedding=[0.5, 0.6, 0.7], prompt_tokens=12)


def test_evidence_packager_formats_context_and_citations() -> None:
    packager = EvidencePackager()
    chunks = [
        RetrievedChunk(
            chunk_id="doc-1:chunk:000001",
            text="A requirement sentence.",
            section_heading="1. Overview",
            page_number=3,
            content_type="text",
            score=0.8,
        ),
        RetrievedChunk(
            chunk_id="doc-1:chunk:000002",
            text="| A | B |",
            section_heading=None,
            page_number=None,
            content_type="table",
            score=0.7,
        ),
    ]

    bundle = packager.package("sec-1", chunks)

    assert bundle.section_id == "sec-1"
    assert "[Source 1 - 1. Overview, p.3 (text)]" in bundle.context_text
    assert "[Source 2 - Document, p.? (table)]" in bundle.context_text
    assert len(bundle.citations) == 2
    assert bundle.citations[0].path == "1. Overview"
    assert bundle.citations[1].path == "Document"
    assert bundle.citations[1].page is None


def test_section_retriever_uses_direct_or_generated_query() -> None:
    async def _run() -> None:
        fake_search = _FakeSearchClient()
        fake_sk = _FakeSKAdapter()
        retriever = SectionRetriever(fake_search, fake_sk, top_k=3)  # type: ignore[arg-type]

        direct_section = SectionDefinition(
            section_id="sec-a",
            title="Executive Summary",
            description="Summarize scope",
            execution_order=0,
            retrieval_query="enterprise architecture integration requirements summary",
        )
        generated_section = SectionDefinition(
            section_id="sec-b",
            title="Security Controls",
            description="Capture control requirements",
            execution_order=1,
            retrieval_query="security",
        )

        direct_chunks, direct_cost = await retriever.retrieve_for_section(
            direct_section,
            document_id="doc-1",
        )
        generated_chunks, generated_cost = await retriever.retrieve_for_section(
            generated_section,
            document_id="doc-1",
        )

        assert direct_chunks
        assert generated_chunks
        assert direct_cost > 0
        assert generated_cost > 0
        assert fake_search.calls[0]["search_text"] == direct_section.retrieval_query
        assert fake_search.calls[1]["search_text"] == "security requirements identity access controls policy coverage"
        assert len(fake_sk.query_prompts) == 1

    asyncio.run(_run())


def test_workflow_executor_retrieval_phase_persists_results(tmp_path) -> None:
    async def _run() -> None:
        now = utc_now_iso()
        document_repo = DocumentRepository(Path(tmp_path) / "documents")
        template_repo = TemplateRepository(Path(tmp_path) / "templates")
        workflow_repo = WorkflowRepository(Path(tmp_path) / "workflows")
        workflow_service = WorkflowService(workflow_repo, document_repo=document_repo, template_repo=template_repo)

        document_repo.save(
            DocumentRecord(
                document_id="doc-1",
                filename="sample.pdf",
                content_type="application/pdf",
                size_bytes=100,
                file_path="doc-1.bin",
                created_at=now,
                updated_at=now,
            ),
        )
        workflow = workflow_service.create(document_id="doc-1", template_id="tpl-inbuilt-pdd", doc_type="PDD")
        workflow_service.update(
            workflow.workflow_run_id,
            section_plan=[
                {
                    "section_id": "sec-1",
                    "title": "Overview",
                    "description": "Overview section",
                    "execution_order": 0,
                    "retrieval_query": "overview business objectives scope assumptions",
                    "output_type": "text",
                },
                {
                    "section_id": "sec-2",
                    "title": "Constraints",
                    "description": "Constraints section",
                    "execution_order": 1,
                    "retrieval_query": "constraints",
                    "output_type": "table",
                },
            ],
        )

        executor = WorkflowExecutor(
            workflow_service=workflow_service,
            event_service=EventService(),
            section_retriever=SectionRetriever(_FakeSearchClient(), _FakeSKAdapter(), top_k=2),  # type: ignore[arg-type]
            evidence_packager=EvidencePackager(),
        )
        await executor._phase_retrieval(workflow.workflow_run_id)

        updated = workflow_service.get_or_raise(workflow.workflow_run_id)
        assert set(updated.section_retrieval_results.keys()) == {"sec-1", "sec-2"}
        section_payload = updated.section_retrieval_results["sec-1"]
        assert isinstance(section_payload, dict)
        assert "context_text" in section_payload
        assert "citations" in section_payload
        citations = section_payload["citations"]
        assert isinstance(citations, list)
        assert citations
        assert {"path", "page", "content_type", "chunk_id"}.issubset(set(citations[0].keys()))
        assert updated.observability_summary.get("embedding_cost_usd", 0) > 0
        assert updated.observability_summary.get("llm_cost_usd", 0) > 0
        assert updated.observability_summary.get("total_llm_calls", 0) > 0
        assert updated.observability_summary.get("total_tokens_in", 0) > 0

    asyncio.run(_run())


def test_workflow_executor_retrieval_non_local_env_raises_on_missing_config(tmp_path) -> None:
    async def _run() -> None:
        now = utc_now_iso()
        document_repo = DocumentRepository(Path(tmp_path) / "documents")
        template_repo = TemplateRepository(Path(tmp_path) / "templates")
        workflow_repo = WorkflowRepository(Path(tmp_path) / "workflows")
        workflow_service = WorkflowService(workflow_repo, document_repo=document_repo, template_repo=template_repo)
        document_repo.save(
            DocumentRecord(
                document_id="doc-2",
                filename="sample.pdf",
                content_type="application/pdf",
                size_bytes=100,
                file_path="doc-2.bin",
                created_at=now,
                updated_at=now,
            ),
        )
        workflow = workflow_service.create(document_id="doc-2", template_id="tpl-inbuilt-pdd", doc_type="PDD")
        workflow_service.update(
            workflow.workflow_run_id,
            section_plan=[
                {
                    "section_id": "sec-1",
                    "title": "Overview",
                    "description": "Overview section",
                    "execution_order": 0,
                    "retrieval_query": "overview business objectives scope assumptions",
                    "output_type": "text",
                },
            ],
        )

        class _UnconfiguredRetriever:
            def is_configured(self) -> bool:
                return False

        executor = WorkflowExecutor(
            workflow_service=workflow_service,
            event_service=EventService(),
            section_retriever=_UnconfiguredRetriever(),  # type: ignore[arg-type]
            evidence_packager=EvidencePackager(),
        )

        old_env = settings.app_env
        settings.app_env = "production"
        try:
            with pytest.raises(Exception, match="Retrieval not configured"):
                await executor._phase_retrieval(workflow.workflow_run_id)
        finally:
            settings.app_env = old_env

    asyncio.run(_run())
