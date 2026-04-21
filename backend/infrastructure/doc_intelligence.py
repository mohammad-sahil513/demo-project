"""Azure Document Intelligence adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from core.config import settings
from core.exceptions import IngestionException
from core.logging import get_logger, verbose_logs_enabled

logger = get_logger(__name__)

DOC_INTELLIGENCE_API_VERSION = "2024-11-30"


@dataclass(slots=True)
class ParsedTable:
    markdown: str
    page_number: int | None
    row_count: int
    column_count: int


@dataclass(slots=True)
class ParsedDocument:
    full_text: str
    page_count: int
    language: str | None
    tables: list[ParsedTable]
    raw_result: dict[str, Any]


class AzureDocIntelligenceClient:
    """Thin adapter around Azure Document Intelligence REST API."""

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        api_key: str | None = None,
        api_version: str = DOC_INTELLIGENCE_API_VERSION,
    ) -> None:
        self._endpoint = (endpoint or settings.azure_document_intelligence_endpoint).rstrip("/")
        self._api_key = api_key or settings.azure_document_intelligence_key
        self._api_version = api_version

    def is_configured(self) -> bool:
        return bool(self._endpoint and self._api_key)

    async def analyze_document(self, payload: bytes, *, content_type: str = "application/octet-stream") -> ParsedDocument:
        if not self.is_configured():
            raise IngestionException("Azure Document Intelligence is not configured.")

        analyze_url = (
            f"{self._endpoint}/documentintelligence/documentModels/prebuilt-layout:analyze"
            f"?api-version={self._api_version}"
        )
        headers = {
            "Ocp-Apim-Subscription-Key": self._api_key,
            "Content-Type": content_type,
        }
        if verbose_logs_enabled():
            logger.info(
                "doc_intelligence.submit endpoint=%s content_type=%s payload_bytes=%s api_version=%s",
                self._endpoint,
                content_type,
                len(payload),
                self._api_version,
            )

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                analyze_response = await client.post(analyze_url, headers=headers, content=payload)
                analyze_response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response_body = exc.response.text[:4000] if exc.response is not None else ""
                logger.exception(
                    "doc_intelligence.submit_http_error status_code=%s body=%s",
                    exc.response.status_code if exc.response is not None else "unknown",
                    response_body,
                )
                raise IngestionException(
                    f"Document Intelligence submit failed with status "
                    f"{exc.response.status_code if exc.response is not None else 'unknown'}: {response_body}"
                ) from exc
            except Exception as exc:
                logger.exception("doc_intelligence.submit_failed error=%s", str(exc))
                raise IngestionException(f"Document Intelligence submit failed: {exc}") from exc

            operation_location = analyze_response.headers.get("operation-location")
            if not operation_location:
                raise IngestionException("Document Intelligence response missing operation-location header.")
            if verbose_logs_enabled():
                logger.info("doc_intelligence.submitted operation_location=%s", operation_location)

            result = await self._poll_operation(client, operation_location, headers)
            return self._to_parsed_document(result)

    async def _poll_operation(
        self,
        client: httpx.AsyncClient,
        operation_location: str,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        for attempt in range(60):
            try:
                response = await client.get(operation_location, headers=headers)
                response.raise_for_status()
                body = response.json()
            except httpx.HTTPStatusError as exc:
                response_body = exc.response.text[:4000] if exc.response is not None else ""
                logger.exception(
                    "doc_intelligence.poll_http_error attempt=%s status_code=%s body=%s",
                    attempt + 1,
                    exc.response.status_code if exc.response is not None else "unknown",
                    response_body,
                )
                raise IngestionException(
                    f"Document Intelligence polling failed with status "
                    f"{exc.response.status_code if exc.response is not None else 'unknown'}: {response_body}"
                ) from exc
            except Exception as exc:
                logger.exception("doc_intelligence.poll_failed attempt=%s error=%s", attempt + 1, str(exc))
                raise IngestionException(f"Document Intelligence polling failed: {exc}") from exc
            status = str(body.get("status", "")).lower()
            if verbose_logs_enabled():
                logger.info("doc_intelligence.poll_status attempt=%s status=%s", attempt + 1, status)
            if status == "succeeded":
                analyze_result = body.get("analyzeResult")
                if not isinstance(analyze_result, dict):
                    raise IngestionException("Document Intelligence returned invalid analyzeResult payload.")
                return analyze_result
            if status == "failed":
                raise IngestionException(f"Document Intelligence analysis failed: {body}")
        raise IngestionException("Timed out waiting for Document Intelligence analysis result.")

    def _to_parsed_document(self, result: dict[str, Any]) -> ParsedDocument:
        content = str(result.get("content") or "")
        pages = result.get("pages") or []
        page_count = len(pages) if isinstance(pages, list) else 0
        languages = result.get("languages") or []
        language = None
        if isinstance(languages, list) and languages:
            first = languages[0]
            if isinstance(first, dict):
                language = first.get("locale")
        tables: list[ParsedTable] = []
        for table in result.get("tables") or []:
            if not isinstance(table, dict):
                continue
            markdown = self._table_to_markdown(table)
            tables.append(
                ParsedTable(
                    markdown=markdown,
                    page_number=self._resolve_table_page(table),
                    row_count=int(table.get("rowCount") or 0),
                    column_count=int(table.get("columnCount") or 0),
                ),
            )
        logger.info(
            "doc_intelligence.analyzed page_count=%s table_count=%s language=%s text_len=%s",
            page_count,
            len(tables),
            language,
            len(content),
        )
        return ParsedDocument(
            full_text=content,
            page_count=page_count,
            language=language,
            tables=tables,
            raw_result=result,
        )

    def _resolve_table_page(self, table: dict[str, Any]) -> int | None:
        spans = table.get("boundingRegions") or []
        if not spans or not isinstance(spans, list):
            return None
        first = spans[0]
        if not isinstance(first, dict):
            return None
        page = first.get("pageNumber")
        return int(page) if isinstance(page, int | float) else None

    def _table_to_markdown(self, table: dict[str, Any]) -> str:
        rows = int(table.get("rowCount") or 0)
        cols = int(table.get("columnCount") or 0)
        if rows <= 0 or cols <= 0:
            return ""

        matrix = [["" for _ in range(cols)] for _ in range(rows)]
        for cell in table.get("cells") or []:
            if not isinstance(cell, dict):
                continue
            row_idx = int(cell.get("rowIndex") or 0)
            col_idx = int(cell.get("columnIndex") or 0)
            if 0 <= row_idx < rows and 0 <= col_idx < cols:
                matrix[row_idx][col_idx] = str(cell.get("content") or "").strip().replace("\n", " ")

        header = matrix[0]
        lines = [
            f"| {' | '.join(header)} |",
            f"| {' | '.join(['---'] * cols)} |",
        ]
        for row in matrix[1:]:
            lines.append(f"| {' | '.join(row)} |")
        return "\n".join(lines)
