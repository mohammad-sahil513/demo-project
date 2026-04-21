"""Document persistence model."""

from __future__ import annotations

from pydantic import BaseModel, Field

from core.constants import DocumentIngestionStatus, DocumentStatus


class DocumentRecord(BaseModel):
    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    status: str = Field(default=DocumentStatus.READY)
    file_path: str
    created_at: str
    updated_at: str

    # Populated after Document Intelligence (first successful ingestion parse path).
    page_count: int | None = None
    language: str | None = None
    doc_intelligence_confidence: float | None = None

    # Ingest-once policy: index chunks under document_id; skip Phase 2 when INDEXED.
    ingestion_status: str = Field(default=DocumentIngestionStatus.NOT_STARTED)
    indexed_chunk_count: int | None = None
    indexed_at: str | None = None
    last_ingestion_error: str | None = None
