"""Document parsing wrapper for ingestion."""

from __future__ import annotations

from pathlib import Path

from core.exceptions import IngestionException
from core.logging import get_logger, verbose_logs_enabled
from infrastructure.doc_intelligence import AzureDocIntelligenceClient, ParsedDocument

logger = get_logger(__name__)


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
        if verbose_logs_enabled():
            logger.info(
                "ingestion.parse.start file_path=%s content_type=%s size_bytes=%s",
                file_path,
                content_type,
                len(payload),
            )
        try:
            parsed = await self._doc_client.analyze_document(payload, content_type=content_type)
            if verbose_logs_enabled():
                logger.info(
                    "ingestion.parse.completed file_path=%s pages=%s tables=%s language=%s",
                    file_path,
                    parsed.page_count,
                    len(parsed.tables),
                    parsed.language,
                )
            return parsed
        except Exception as exc:
            logger.exception(
                "ingestion.parse.failed file_path=%s content_type=%s error=%s",
                file_path,
                content_type,
                str(exc),
            )
            raise
