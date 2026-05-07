from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace
import pytest

from core.constants import DocumentIngestionStatus
from core.ids import utc_now_iso
from infrastructure.doc_intelligence import ParsedDocument, ParsedTable
from modules.ingestion.chunker import DocumentChunker
from modules.ingestion.indexer import DocumentIndexer
from modules.ingestion.ingestion_coordinator import IngestionCoordinator, IngestionRunResult
from modules.ingestion.orchestrator import IngestionOrchestrator
from modules.ingestion.parser import DocumentParser
from repositories.document_models import DocumentRecord
from repositories.document_repo import DocumentRepository
from services.event_service import EventService


class _FakeDocClient:
    def __init__(self, parsed: ParsedDocument) -> None:
        self._parsed = parsed

    async def analyze_document(self, payload: bytes, *, content_type: str) -> ParsedDocument:
        assert payload
        assert content_type
        return self._parsed


class _FakeSKAdapter:
    def is_configured(self) -> bool:
        return True

    async def generate_embedding(self, text: str) -> list[float]:
        size = min(8, max(2, len(text.split())))
        return [0.1 for _ in range(size)]

    async def generate_embedding_with_usage(self, text: str):
        vector = await self.generate_embedding(text)
        return SimpleNamespace(embedding=vector, prompt_tokens=len(text.split()))


class _FakeSearchClient:
    def __init__(self) -> None:
        self.saved = []

    def is_configured(self) -> bool:
        return True

    async def upsert_chunks(self, chunks):
        self.saved.extend(chunks)
        return len(chunks)


def _sample_parsed_document() -> ParsedDocument:
    long_text = (
        "1. Introduction "
        + " ".join(f"word{i}" for i in range(140))
        + "\n2. Requirements "
        + " ".join(f"req{i}" for i in range(140))
    )
    return ParsedDocument(
        full_text=long_text,
        page_count=3,
        language="en",
        tables=[ParsedTable(markdown="| A | B |\n| --- | --- |\n| 1 | 2 |", page_number=2, row_count=2, column_count=2)],
        raw_result={
            "paragraphs": [
                {"spans": [{"offset": 0}], "boundingRegions": [{"pageNumber": 1}]},
                {"spans": [{"offset": 300}], "boundingRegions": [{"pageNumber": 2}]},
            ],
        },
    )


def test_chunker_creates_table_and_overlapping_text_chunks() -> None:
    parsed = _sample_parsed_document()
    chunker = DocumentChunker(chunk_size=40, overlap=10, token_mode="word")

    chunks = chunker.chunk(document_id="doc-1", workflow_run_id="wf-1", parsed=parsed)

    assert chunks
    assert chunks[0].content_type == "table"
    assert chunks[0].page_number == 2

    text_chunks = [chunk for chunk in chunks if chunk.content_type == "text"]
    assert len(text_chunks) >= 2
    assert text_chunks[0].chunk_id == "doc-1_chunk_000001"
    assert text_chunks[1].chunk_id == "doc-1_chunk_000002"
    assert text_chunks[0].page_number is not None

    first_tokens = text_chunks[0].text.split()
    second_tokens = text_chunks[1].text.split()
    assert first_tokens[-10:] == second_tokens[:10]


def test_ingestion_coordinator_skip_then_fail_then_retry_success(tmp_path) -> None:
    async def _run() -> None:
        now = utc_now_iso()
        repo = DocumentRepository(tmp_path / "documents")
        repo.save(
            DocumentRecord(
                document_id="doc-1",
                filename="sample.pdf",
                content_type="application/pdf",
                size_bytes=5,
                file_path="doc-1.bin",
                created_at=now,
                updated_at=now,
            ),
        )
        coordinator = IngestionCoordinator(repo)

        async def fail_once(_doc: DocumentRecord) -> IngestionRunResult:
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            await coordinator.run_ingestion_if_needed("doc-1", fail_once)
        updated = repo.get_or_raise("doc-1")
        assert updated.ingestion_status == DocumentIngestionStatus.FAILED

        async def succeed(_doc: DocumentRecord) -> IngestionRunResult:
            return IngestionRunResult(
                chunk_count=4,
                page_count=2,
                language="en",
                embedding_cost_usd=0.001,
                document_intelligence_cost_usd=0.02,
            )

        skipped, result = await coordinator.run_ingestion_if_needed("doc-1", succeed)
        assert skipped is False
        assert result is not None
        updated = repo.get_or_raise("doc-1")
        assert updated.ingestion_status == DocumentIngestionStatus.INDEXED

        skipped, result = await coordinator.run_ingestion_if_needed("doc-1", succeed)
        assert skipped is True
        assert result is None

    asyncio.run(_run())


def test_orchestrator_emits_stage_events_and_returns_costs(tmp_path) -> None:
    async def _run() -> None:
        parsed = _sample_parsed_document()
        doc_client = _FakeDocClient(parsed)
        sk_adapter = _FakeSKAdapter()
        search_client = _FakeSearchClient()
        parser = DocumentParser(doc_client)  # type: ignore[arg-type]
        chunker = DocumentChunker(chunk_size=60, overlap=15)
        indexer = DocumentIndexer(search_client, sk_adapter, batch_size=2)  # type: ignore[arg-type]
        events = EventService()
        orchestrator = IngestionOrchestrator(parser, chunker, indexer, events)

        queue = events.subscribe("wf-1")
        file_path = Path(tmp_path / "sample.bin")
        file_path.write_bytes(b"test-bytes")

        result = await orchestrator.run(
            workflow_run_id="wf-1",
            document_id="doc-1",
            file_path=file_path,
            content_type="application/pdf",
        )

        event_types = []
        while not queue.empty():
            event_types.append((await queue.get())["type"])

        assert result.chunk_count > 0
        assert result.document_intelligence_cost_usd > 0
        assert "ingestion.parse.completed" in event_types
        assert "ingestion.chunk.completed" in event_types
        assert "ingestion.index.completed" in event_types

    asyncio.run(_run())
