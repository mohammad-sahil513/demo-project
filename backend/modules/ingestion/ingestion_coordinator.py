"""Serialize ingest per BRD and skip Phase 2 when chunks already indexed (ingest-once)."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.constants import DocumentIngestionStatus
from core.ids import utc_now_iso

if TYPE_CHECKING:
    from repositories.document_models import DocumentRecord
    from repositories.document_repo import DocumentRepository


@dataclass(frozen=True, slots=True)
class IngestionRunResult:
    """Result when ingestion actually runs (not skipped)."""

    chunk_count: int
    page_count: int | None
    language: str | None
    embedding_cost_usd: float
    document_intelligence_cost_usd: float


class IngestionCoordinator:
    """Per-process asyncio lock per document_id + persisted INDEXED flag.

    Policy:
    - Chunks in Azure AI Search are keyed by stable ``chunk_id`` (see ``chunk_id_for_document``).
    - Only one ingest pipeline runs at a time for a given ``document_id`` (concurrent workflows wait).
    - If ``DocumentRecord.ingestion_status == INDEXED``, Phase 2 is skipped (PDD+SDD+UAT reuse the same index).
    - Re-running after FAILED is allowed; upserts remain idempotent.
    """

    def __init__(self, document_repo: DocumentRepository) -> None:
        self._document_repo = document_repo
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock(self, document_id: str) -> asyncio.Lock:
        if document_id not in self._locks:
            self._locks[document_id] = asyncio.Lock()
        return self._locks[document_id]

    async def run_ingestion_if_needed(
        self,
        document_id: str,
        ingest: Callable[[DocumentRecord], Awaitable[IngestionRunResult]],
    ) -> tuple[bool, IngestionRunResult | None]:
        """Return ``(skipped, result)`` where ``skipped`` means Phase 2 did not run."""
        async with self._lock(document_id):
            doc = self._document_repo.get_or_raise(document_id)
            if doc.ingestion_status == DocumentIngestionStatus.INDEXED:
                return True, None

            try:
                result = await ingest(doc)
            except Exception as exc:  # noqa: BLE001 — surface to workflow layer
                self._document_repo.update(
                    document_id,
                    ingestion_status=DocumentIngestionStatus.FAILED,
                    last_ingestion_error=str(exc),
                )
                raise

            self._document_repo.update(
                document_id,
                ingestion_status=DocumentIngestionStatus.INDEXED,
                indexed_chunk_count=result.chunk_count,
                indexed_at=utc_now_iso(),
                last_ingestion_error=None,
                page_count=result.page_count if result.page_count is not None else doc.page_count,
                language=result.language if result.language is not None else doc.language,
            )
            return False, result
