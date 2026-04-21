"""Document parsing wrapper for ingestion."""

from __future__ import annotations

from pathlib import Path

from core.exceptions import IngestionException
from infrastructure.doc_intelligence import AzureDocIntelligenceClient, ParsedDocument


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
        return await self._doc_client.analyze_document(payload, content_type=content_type)
