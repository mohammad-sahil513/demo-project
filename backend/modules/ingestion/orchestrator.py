"""Parse -> chunk -> index ingestion pipeline."""

from __future__ import annotations

from pathlib import Path

from core.logging import get_logger, verbose_logs_enabled
from modules.ingestion.chunker import DocumentChunker
from modules.ingestion.indexer import DocumentIndexer
from modules.ingestion.ingestion_coordinator import IngestionRunResult
from modules.ingestion.parser import DocumentParser
from modules.observability.cost_rollup import document_intelligence_cost_usd
from services.event_service import EventService

logger = get_logger(__name__)


class IngestionOrchestrator:
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
        return self._parser.is_configured() and self._indexer.is_configured()

    async def run(
        self,
        *,
        workflow_run_id: str,
        document_id: str,
        file_path: Path,
        content_type: str,
    ) -> IngestionRunResult:
        if verbose_logs_enabled():
            logger.info(
                "ingestion.pipeline.start workflow_run_id=%s document_id=%s file_path=%s content_type=%s",
                workflow_run_id,
                document_id,
                file_path,
                content_type,
            )
        parsed = await self._parser.parse(file_path, content_type=content_type)
        await self._event_service.emit(
            workflow_run_id,
            "ingestion.parse.completed",
            {"pages": parsed.page_count, "language": parsed.language},
        )

        chunks = self._chunker.chunk(
            document_id=document_id,
            workflow_run_id=workflow_run_id,
            parsed=parsed,
        )
        if verbose_logs_enabled():
            logger.info(
                "ingestion.chunk.completed workflow_run_id=%s document_id=%s chunk_count=%s",
                workflow_run_id,
                document_id,
                len(chunks),
            )
        await self._event_service.emit(
            workflow_run_id,
            "ingestion.chunk.completed",
            {"chunk_count": len(chunks)},
        )

        indexed_count, embedding_cost = await self._indexer.index_chunks(chunks)
        if verbose_logs_enabled():
            logger.info(
                "ingestion.index.completed workflow_run_id=%s document_id=%s indexed_count=%s embedding_cost_usd=%s",
                workflow_run_id,
                document_id,
                indexed_count,
                embedding_cost,
            )
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
