"""Document parsing wrapper for ingestion."""
from __future__ import annotations

from mimetypes import guess_type
from pathlib import Path

from core.exceptions import IngestionException
from infrastructure.doc_intelligence import AzureDocIntelligenceClient, ParsedDocument


def _normalize_content_type(file_path: Path, content_type: str | None) -> str:
    """
    Normalize content type before sending bytes to Azure Document Intelligence.

    Why:
    - Upstream callers may pass generic content types like application/octet-stream.
    - For Office/PDF files, it's safer to send an explicit MIME type when possible.
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
        return self._doc_client.is_configured()

    async def parse(self, file_path: Path, *, content_type: str) -> ParsedDocument:
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
