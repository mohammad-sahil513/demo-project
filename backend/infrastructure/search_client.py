"""Azure AI Search adapter — indexing + hybrid retrieval.

Responsibilities
----------------
- Upsert chunked document text + embeddings into the Azure AI Search index.
- Run hybrid keyword + vector queries during the retrieval phase.
- Delete documents from the index (cleanup on re-ingestion).

Resilience
----------
Azure AI Search throttles aggressively under load (typically 503/429). The
adapter implements an exponential-backoff retry with jitter, honoring
``Retry-After`` when the server provides one. We never retry 4xx unless the
status is in :data:`SEARCH_RETRYABLE_STATUS_CODES` — that would mask real
client-side bugs.

Observability
-------------
Each request emits a structured log line with the operation, attempt count,
duration, and a payload summary (vector dim, top-k, filter shape). The
summary intentionally omits the embedding vector and full query text so
logs stay small and PII-light.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
from dataclasses import dataclass
from typing import Any
from time import perf_counter

import httpx

from core.config import settings
from core.exceptions import IngestionException

logger = logging.getLogger(__name__)

# Pin the API version — the search index schema and query DSL evolve.
SEARCH_API_VERSION = "2025-09-01"

# Retry / timeout knobs. ``SEARCH_INDEX_TIMEOUT_SECONDS`` is higher than the
# default because indexing batches with hundreds of chunks can take a while.
SEARCH_RETRYABLE_STATUS_CODES = {429, 502, 503, 504}
SEARCH_MAX_RETRY_ATTEMPTS = 4
SEARCH_RETRY_BASE_DELAY_SECONDS = 1.0
SEARCH_RETRY_MAX_DELAY_SECONDS = 8.0
SEARCH_RETRY_JITTER_MAX_SECONDS = 0.25

SEARCH_DEFAULT_TIMEOUT_SECONDS = 45.0
SEARCH_INDEX_TIMEOUT_SECONDS = 60.0


@dataclass(slots=True)
class SearchChunk:
    """One chunk ready for upsert into the search index.

    Field names match the index schema exactly — do not rename without
    updating the index definition in Azure.
    """

    chunk_id: str
    document_id: str
    workflow_run_id: str
    text: str
    chunk_index: int
    section_heading: str | None
    page_number: int | None
    content_type: str
    embedding: list[float]


class AzureSearchClient:
    """Adapter for Azure AI Search indexing and hybrid retrieval operations."""

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        api_key: str | None = None,
        index_name: str | None = None,
        api_version: str = SEARCH_API_VERSION,
    ) -> None:
        self._endpoint = (endpoint or settings.azure_search_endpoint).rstrip("/")
        self._api_key = api_key or settings.azure_search_api_key
        self._index_name = index_name or settings.azure_search_index_name
        self._api_version = api_version

        # Phase 3: reusable async HTTP client
        self._client: httpx.AsyncClient | None = None

    def is_configured(self) -> bool:
        return bool(self._endpoint and self._api_key and self._index_name)

    def _get_client(self, *, timeout_seconds: float) -> httpx.AsyncClient:
        """Lazily create and reuse a single :class:`httpx.AsyncClient`.

        Connection reuse matters here — Azure Search lives on HTTPS/2 and
        each fresh TCP+TLS handshake adds 100-200 ms. We intentionally keep
        the first-created timeout even if a later caller passes a different
        one because the default timeout is already long enough for every
        operation we issue.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=timeout_seconds)
        return self._client

    async def aclose(self) -> None:
        """Close the reusable HTTP client if it exists."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @staticmethod
    def _safe_json(response: httpx.Response):
        try:
            return response.json()
        except Exception:
            return None

    @staticmethod
    def _summarize_index_payload(payload: dict) -> dict:
        docs = payload.get("value") or []
        dims = []
        samples = []

        for doc in docs:
            emb = doc.get("embedding")
            if isinstance(emb, list):
                dims.append(len(emb))

        for doc in docs[:2]:
            sample = {k: v for k, v in doc.items() if k != "embedding"}
            emb = doc.get("embedding")
            if isinstance(emb, list):
                sample["embedding_dim"] = len(emb)
                sample["embedding_head"] = emb[:3]
            else:
                sample["embedding_dim"] = None
            samples.append(sample)

        return {
            "document_count": len(docs),
            "embedding_dimensions_seen": sorted(set(dims)),
            "sample_documents": samples,
        }

    def _log_http_status_error(self, operation: str, payload: dict, exc: httpx.HTTPStatusError) -> None:
        response = exc.response
        request = exc.request
        details = {
            "operation": operation,
            "method": request.method if request else None,
            "url": str(request.url) if request else None,
            "status_code": response.status_code if response else None,
            "reason_phrase": response.reason_phrase if response else None,
            "x_ms_request_id": response.headers.get("x-ms-request-id") if response else None,
            "x_ms_client_request_id": response.headers.get("x-ms-client-request-id") if response else None,
            "index_name": getattr(self, "_index_name", None),
            "api_version": getattr(self, "_api_version", None),
            "response_json": self._safe_json(response) if response else None,
            "response_text": (response.text[:8000] if response and response.text else None),
            "request_payload_summary": self._summarize_index_payload(payload),
        }
        logger.error(
            "Azure Search HTTP error during %s:\n%s",
            operation,
            json.dumps(details, indent=2, ensure_ascii=False, default=str),
        )

    def _compute_retry_delay_seconds(
        self,
        attempt: int,
        response: httpx.Response | None = None,
    ) -> float:
        """Compute the next retry delay.

        Strategy:
        1. Honor ``Retry-After`` (in seconds) if the server provides one.
        2. Otherwise exponential backoff (``base * 2^(attempt-1)``) capped at
           :data:`SEARCH_RETRY_MAX_DELAY_SECONDS`.
        3. Add up to 250 ms of jitter so concurrent retries don't thunder.
        """
        if response is not None:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    retry_after_seconds = float(retry_after)
                    if retry_after_seconds > 0:
                        return min(retry_after_seconds, SEARCH_RETRY_MAX_DELAY_SECONDS)
                except ValueError:
                    pass

        base_delay = min(
            SEARCH_RETRY_MAX_DELAY_SECONDS,
            SEARCH_RETRY_BASE_DELAY_SECONDS * (2 ** max(0, attempt - 1)),
        )
        jitter = random.uniform(0.0, SEARCH_RETRY_JITTER_MAX_SECONDS)
        return min(base_delay + jitter, SEARCH_RETRY_MAX_DELAY_SECONDS)

    async def _post_json_with_retry(
        self,
        *,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
        operation: str,
        timeout_seconds: float,
    ) -> httpx.Response:
        """POST with retry for transient Azure Search failures.

        Retries on:
        - Status codes in :data:`SEARCH_RETRYABLE_STATUS_CODES` (429/5xx),
        - :class:`httpx.RequestError` transport failures.

        Non-retryable :class:`httpx.HTTPStatusError` is re-raised immediately
        after a detailed error log so the root cause is obvious. Each retry
        attempt and the final outcome are logged with a payload summary.
        """
        client = self._get_client(timeout_seconds=timeout_seconds)
        last_request_error: httpx.RequestError | None = None
        started_at = perf_counter()

        for attempt in range(1, SEARCH_MAX_RETRY_ATTEMPTS + 1):
            attempt_started_at = perf_counter()

            try:
                response = await client.post(url, headers=headers, json=payload)
                attempt_duration_ms = int((perf_counter() - attempt_started_at) * 1000)

                if response.status_code in SEARCH_RETRYABLE_STATUS_CODES:
                    if attempt < SEARCH_MAX_RETRY_ATTEMPTS:
                        delay = self._compute_retry_delay_seconds(attempt, response)
                        logger.warning(
                            "search.retry.scheduled operation=%s attempt=%s/%s status_code=%s "
                            "delay_s=%.2f duration_ms=%s request_id=%s payload_summary=%s",
                            operation,
                            attempt,
                            SEARCH_MAX_RETRY_ATTEMPTS,
                            response.status_code,
                            delay,
                            attempt_duration_ms,
                            response.headers.get("x-ms-request-id"),
                            json.dumps(self._summarize_search_payload(payload), ensure_ascii=False, default=str),
                        )
                        await asyncio.sleep(delay)
                        continue

                response.raise_for_status()

                total_duration_ms = int((perf_counter() - started_at) * 1000)
                logger.info(
                    "search.request.succeeded operation=%s attempts=%s final_status=%s "
                    "duration_ms=%s request_id=%s payload_summary=%s",
                    operation,
                    attempt,
                    response.status_code,
                    total_duration_ms,
                    response.headers.get("x-ms-request-id"),
                    json.dumps(self._summarize_search_payload(payload), ensure_ascii=False, default=str),
                )
                return response

            except httpx.RequestError as exc:
                attempt_duration_ms = int((perf_counter() - attempt_started_at) * 1000)
                last_request_error = exc

                if attempt >= SEARCH_MAX_RETRY_ATTEMPTS:
                    total_duration_ms = int((perf_counter() - started_at) * 1000)
                    logger.exception(
                        "search.request.failed operation=%s attempts=%s error_type=request_error "
                        "duration_ms=%s payload_summary=%s error=%s",
                        operation,
                        attempt,
                        total_duration_ms,
                        json.dumps(self._summarize_search_payload(payload), ensure_ascii=False, default=str),
                        exc,
                    )
                    raise

                delay = self._compute_retry_delay_seconds(attempt, None)
                logger.warning(
                    "search.retry.scheduled operation=%s attempt=%s/%s error_type=request_error "
                    "delay_s=%.2f duration_ms=%s payload_summary=%s error=%s",
                    operation,
                    attempt,
                    SEARCH_MAX_RETRY_ATTEMPTS,
                    delay,
                    attempt_duration_ms,
                    json.dumps(self._summarize_search_payload(payload), ensure_ascii=False, default=str),
                    exc,
                )
                await asyncio.sleep(delay)

            except httpx.HTTPStatusError as exc:
                total_duration_ms = int((perf_counter() - started_at) * 1000)
                self._log_http_status_error(operation, payload, exc)
                logger.error(
                    "search.request.failed operation=%s attempts=%s error_type=http_status "
                    "status_code=%s duration_ms=%s request_id=%s payload_summary=%s",
                    operation,
                    attempt,
                    exc.response.status_code if exc.response is not None else "unknown",
                    total_duration_ms,
                    exc.response.headers.get("x-ms-request-id") if exc.response is not None else None,
                    json.dumps(self._summarize_search_payload(payload), ensure_ascii=False, default=str),
                )
                raise

        if last_request_error is not None:
            raise last_request_error

        raise RuntimeError(f"Unexpected Azure Search retry flow termination during {operation}")

    async def upsert_chunks(self, chunks: list[SearchChunk]) -> int:
        payload = {
            "value": [
                {
                    "@search.action": "mergeOrUpload",
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "workflow_run_id": chunk.workflow_run_id,
                    "text": chunk.text,
                    "chunk_index": chunk.chunk_index,
                    "section_heading": chunk.section_heading,
                    "page_number": chunk.page_number,
                    "content_type": chunk.content_type,
                    "embedding": chunk.embedding,
                }
                for chunk in chunks
            ]
        }
        url = (
            f"{self._endpoint}/indexes/{self._index_name}"
            f"/docs/index?api-version={self._api_version}"
        )
        headers = {
            "Content-Type": "application/json",
            "api-key": self._api_key,
        }

        logger.info(
            "Azure Search upsert summary: %s",
            json.dumps(self._summarize_index_payload(payload), ensure_ascii=False, default=str),
        )

        response = await self._post_json_with_retry(
            url=url,
            headers=headers,
            payload=payload,
            operation="upsert_chunks",
            timeout_seconds=SEARCH_INDEX_TIMEOUT_SECONDS,
        )

        body = self._safe_json(response) or {}
        results = body.get("value", [])
        failed = [item for item in results if not item.get("status", False)]
        if failed:
            logger.error(
                "Azure Search indexing reported per-document failures:\n%s",
                json.dumps(failed[:10], indent=2, ensure_ascii=False, default=str),
            )
            raise RuntimeError("Azure Search indexing completed with failed document statuses.")
        return len(results)

    async def hybrid_search(
        self,
        *,
        search_text: str,
        embedding: list[float],
        document_id: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        if not self.is_configured():
            raise IngestionException("Azure AI Search is not configured.")

        url = self._docs_search_url()
        payload = {
            "search": search_text,
            "filter": self.build_document_filter(document_id),
            "top": top_k,
            "vectorQueries": [
                {
                    "kind": "vector",
                    "vector": embedding,
                    "fields": "embedding",
                    "k": top_k,
                },
            ],
        }
        headers = {"Content-Type": "application/json", "api-key": self._api_key}

        logger.info(
            "search.request.started operation=hybrid_search index_name=%s payload_summary=%s",
            self._index_name,
            json.dumps(self._summarize_search_payload(payload), ensure_ascii=False, default=str),
        )

        response = await self._post_json_with_retry(
            url=url,
            headers=headers,
            payload=payload,
            operation="hybrid_search",
            timeout_seconds=SEARCH_DEFAULT_TIMEOUT_SECONDS,
        )

        body = response.json()
        value = body.get("value") or []
        return value if isinstance(value, list) else []

    async def delete_by_document(self, document_id: str) -> int:
        if not self.is_configured():
            raise IngestionException("Azure AI Search is not configured.")

        hits = await self._search_ids_for_document(document_id)
        ids = [str(item.get("chunk_id")) for item in hits if item.get("chunk_id")]
        if not ids:
            return 0

        actions = [{"@search.action": "delete", "chunk_id": chunk_id} for chunk_id in ids]
        payload = {"value": actions}
        headers = {"Content-Type": "application/json", "api-key": self._api_key}

        response = await self._post_json_with_retry(
            url=self._docs_index_url(),
            headers=headers,
            payload=payload,
            operation="delete_by_document",
            timeout_seconds=SEARCH_DEFAULT_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return len(ids)

    def build_document_filter(self, document_id: str) -> str:
        """Build the OData ``$filter`` clause that scopes results to one doc.

        Single quotes in the ID are doubled per the Azure Search OData spec
        to escape them — we generate IDs ourselves so this is defensive, but
        a future change to ID generation must not break filtering silently.
        """
        safe_document_id = document_id.replace("'", "''")
        return f"document_id eq '{safe_document_id}'"

    async def _search_ids_for_document(self, document_id: str) -> list[dict[str, Any]]:
        url = self._docs_search_url()
        payload = {
            "search": "*",
            "filter": self.build_document_filter(document_id),
            "top": 1000,
            "select": "chunk_id",
        }
        headers = {"Content-Type": "application/json", "api-key": self._api_key}

        response = await self._post_json_with_retry(
            url=url,
            headers=headers,
            payload=payload,
            operation="_search_ids_for_document",
            timeout_seconds=SEARCH_DEFAULT_TIMEOUT_SECONDS,
        )

        body = response.json()
        value = body.get("value") or []
        return value if isinstance(value, list) else []

    def _docs_index_url(self) -> str:
        return f"{self._endpoint}/indexes/{self._index_name}/docs/index?api-version={self._api_version}"

    def _docs_search_url(self) -> str:
        return f"{self._endpoint}/indexes/{self._index_name}/docs/search?api-version={self._api_version}"
   
    @staticmethod
    def _summarize_search_payload(payload: dict[str, Any]) -> dict[str, Any]:
        vector_queries = payload.get("vectorQueries") or []
        vector_dim = None
        if isinstance(vector_queries, list) and vector_queries:
            first = vector_queries[0]
            if isinstance(first, dict):
                vector = first.get("vector")
                if isinstance(vector, list):
                    vector_dim = len(vector)

        search_text = str(payload.get("search") or "")
        return {
            "search_text_length": len(search_text),
            "search_word_count": len(search_text.split()),
            "top": payload.get("top"),
            "has_filter": bool(payload.get("filter")),
            "vector_query_count": len(vector_queries) if isinstance(vector_queries, list) else 0,
            "vector_dimension": vector_dim,
        }
