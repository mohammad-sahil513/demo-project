"""Parse -> chunk -> index ingestion pipeline.

The orchestrator is the single entry point used by the workflow executor
when ingestion needs to run for a document. It emits three SSE events as
each sub-phase finishes so the UI can render granular progress.

The decision *whether* to run is owned by :class:`IngestionCoordinator`
(ingest-once policy); this class only knows how to ingest.
"""

from __future__ import annotations

from pathlib import Path

from modules.ingestion.chunker import DocumentChunker
from modules.ingestion.indexer import DocumentIndexer
from modules.ingestion.ingestion_coordinator import IngestionRunResult
from modules.ingestion.parser import DocumentParser
from modules.observability.cost_rollup import document_intelligence_cost_usd
from services.event_service import EventService


class IngestionOrchestrator:
    """Runs parse -> chunk -> index for a single document, with SSE events."""

    def __init__(
        self,
        parser: DocumentParser,
        chunker: DocumentChunker,
        indexer: DocumentIndexer,
        event_service: EventService,
    ) -> None:
        self._parser = parser
        self._chunker = chunker
        self._indexer = indexer
        self._event_service = event_service

    def is_configured(self) -> bool:
        """Both Document Intelligence and the indexer must be configured."""
        return self._parser.is_configured() and self._indexer.is_configured()

    async def run(
        self,
        *,
        workflow_run_id: str,
        document_id: str,
        file_path: Path,
        content_type: str,
    ) -> IngestionRunResult:
        """Execute the full ingestion pipeline for a single document."""
        # --- Parse ------------------------------------------------------
        parsed = await self._parser.parse(file_path, content_type=content_type)
        await self._event_service.emit(
            workflow_run_id,
            "ingestion.parse.completed",
            {"pages": parsed.page_count, "language": parsed.language},
        )

        # --- Chunk ------------------------------------------------------
        chunks = self._chunker.chunk(
            document_id=document_id,
            workflow_run_id=workflow_run_id,
            parsed=parsed,
        )
        await self._event_service.emit(
            workflow_run_id,
            "ingestion.chunk.completed",
            {"chunk_count": len(chunks)},
        )

        # --- Index ------------------------------------------------------
        indexed_count, embedding_cost = await self._indexer.index_chunks(chunks)
        await self._event_service.emit(
            workflow_run_id,
            "ingestion.index.completed",
            {"indexed_count": indexed_count, "embedding_cost_usd": embedding_cost},
        )

        return IngestionRunResult(
            chunk_count=indexed_count,
            page_count=parsed.page_count,
            language=parsed.language,
            embedding_cost_usd=embedding_cost,
            document_intelligence_cost_usd=document_intelligence_cost_usd(parsed.page_count),
        )
