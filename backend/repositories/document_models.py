"""Pydantic model for the document JSON record.

A ``DocumentRecord`` is created when a user uploads a BRD (Business
Requirements Document) PDF/DOCX. It tracks the upload itself plus the result
of Azure Document Intelligence parsing and Azure AI Search indexing.

The ``ingestion_status`` is the ingest-once switch — Phase 2 of the workflow
will skip re-indexing when this is ``INDEXED`` for the document.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from core.constants import DocumentIngestionStatus, DocumentStatus


class DocumentRecord(BaseModel):
    """One uploaded source document on disk."""

    # Stable ``doc-<hex12>`` identifier from :func:`core.ids.document_id`.
    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    # ``DocumentStatus`` — UPLOADED right after the bytes land, READY once the
    # request handler has accepted it as parseable, FAILED on hard errors.
    status: str = Field(default=DocumentStatus.READY)
    # Absolute path under ``storage/documents/``.
    file_path: str
    created_at: str
    updated_at: str

    # Populated after Document Intelligence (first successful ingestion parse path).
    page_count: int | None = None
    language: str | None = None
    doc_intelligence_confidence: float | None = None

    # Ingest-once policy: index chunks under document_id; skip Phase 2 when INDEXED.
    # ``last_ingestion_error`` is retained even after a successful re-ingest so
    # operators can audit transient failures.
    ingestion_status: str = Field(default=DocumentIngestionStatus.NOT_STARTED)
    indexed_chunk_count: int | None = None
    indexed_at: str | None = None
    last_ingestion_error: str | None = None
