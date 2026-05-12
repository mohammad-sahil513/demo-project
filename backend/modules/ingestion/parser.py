"""Document parsing wrapper for ingestion.

Thin adapter that:

1. Reads the document bytes from disk.
2. Normalizes the content type into the explicit MIME the Document
   Intelligence API expects (see :func:`_normalize_content_type`).
3. Delegates to :class:`infrastructure.doc_intelligence.AzureDocIntelligenceClient`
   which performs the actual submit/poll.

The wrapper exists so the ingestion pipeline can be unit-tested without
touching either the file system or the network.
"""
from __future__ import annotations

from mimetypes import guess_type
from pathlib import Path

from core.exceptions import IngestionException
from infrastructure.doc_intelligence import AzureDocIntelligenceClient, ParsedDocument


def _normalize_content_type(file_path: Path, content_type: str | None) -> str:
    """Normalize content type before sending bytes to Azure Document Intelligence.

    Why this exists:
    - Upstream callers (multipart upload) may pass generic content types like
      ``application/octet-stream``, which Document Intelligence handles less
      reliably than a specific MIME.
    - For Office/PDF files, sending the explicit MIME yields better parse
      quality and avoids extension-sniffing edge cases on the server.

    Resolution order: explicit non-generic input -> :mod:`mimetypes` guess
    -> hard-coded extension table -> ``application/octet-stream`` fallback.
    """
    raw = (content_type or "").strip().lower()

    # Keep non-generic explicit content types as-is
    if raw and raw not in {"application/octet-stream", "binary/octet-stream"}:
        return raw

    # Try Python's mimetype inference first
    guessed, _ = guess_type(str(file_path))
    if guessed:
        return guessed

    # Strong fallback by extension
    suffix = file_path.suffix.lower()
    if suffix == ".docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if suffix == ".xlsx":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if suffix == ".pptx":
        return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    if suffix == ".pdf":
        return "application/pdf"

    return "application/octet-stream"


class DocumentParser:
    """Load a document from disk and parse with Azure Document Intelligence."""

    def __init__(self, doc_client: AzureDocIntelligenceClient) -> None:
        self._doc_client = doc_client

    def is_configured(self) -> bool:
        """``True`` when the underlying Document Intelligence client has creds."""
        return self._doc_client.is_configured()

    async def parse(self, file_path: Path, *, content_type: str) -> ParsedDocument:
        """Read ``file_path`` and submit it for analysis.

        Raises
        ------
        IngestionException
            File missing on disk, or zero-byte payload — neither is a valid
            input and we'd rather fail loudly here than send a useless
            request to Azure.
        """
        if not file_path.exists():
            raise IngestionException(f"Document file not found: {file_path}")

        payload = file_path.read_bytes()
        if not payload:
            raise IngestionException(f"Document file is empty: {file_path}")

        normalized_content_type = _normalize_content_type(file_path, content_type)

        return await self._doc_client.analyze_document(
            payload,
            content_type=normalized_content_type,
        )
