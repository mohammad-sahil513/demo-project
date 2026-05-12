"""Serialize ingest per BRD and skip Phase 2 when chunks already indexed (ingest-once).

This coordinator owns the policy:

- Concurrent workflows for the same document wait on a single asyncio lock.
- A document that is already :class:`DocumentIngestionStatus.INDEXED` skips
  ingestion entirely — PDD, SDD, and UAT runs share the same index entries.
- :class:`DocumentIngestionStatus.FAILED` documents may be retried; upserts
  are idempotent (search action ``mergeOrUpload`` keyed on ``chunk_id``).
"""

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
        # Process-local locks. A multi-process deployment would need an
        # out-of-band coordination mechanism (Redis lock, queue worker) but
        # the current FastAPI service is single-process.
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock(self, document_id: str) -> asyncio.Lock:
        """Lazily create and return the lock for one document."""
        if document_id not in self._locks:
            self._locks[document_id] = asyncio.Lock()
        return self._locks[document_id]

    async def run_ingestion_if_needed(
        self,
        document_id: str,
        ingest: Callable[[DocumentRecord], Awaitable[IngestionRunResult]],
    ) -> tuple[bool, IngestionRunResult | None]:
        """Return ``(skipped, result)`` where ``skipped`` means Phase 2 did not run.

        The caller (``services.workflow_executor``) supplies the ``ingest``
        callable so this coordinator stays free of the orchestrator details
        and is easy to unit-test with a mock callable.
        """
        async with self._lock(document_id):
            doc = self._document_repo.get_or_raise(document_id)
            # Ingest-once short-circuit. The current call site already has
            # the lock, so we won't race with another workflow re-indexing.
            if doc.ingestion_status == DocumentIngestionStatus.INDEXED:
                return True, None

            try:
                result = await ingest(doc)
            except Exception as exc:  # noqa: BLE001 — surface to workflow layer
                # Persist FAILED + the error message so operators can audit
                # what happened without diving into the per-workflow log.
                self._document_repo.update(
                    document_id,
                    ingestion_status=DocumentIngestionStatus.FAILED,
                    last_ingestion_error=str(exc),
                )
                raise

            # Success — flip to INDEXED and clear any prior failure. We
            # preserve ``page_count`` / ``language`` from the existing
            # record when this run did not return new values (re-ingest).
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
