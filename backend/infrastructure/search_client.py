"""Azure AI Search adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from core.config import settings
from core.exceptions import IngestionException

SEARCH_API_VERSION = "2024-07-01"


@dataclass(slots=True)
class SearchChunk:
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
    """Adapter for indexing and hybrid retrieval operations."""

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

    def is_configured(self) -> bool:
        return bool(self._endpoint and self._api_key and self._index_name)

    async def upsert_chunks(self, chunks: list[SearchChunk]) -> int:
        if not self.is_configured():
            raise IngestionException("Azure AI Search is not configured.")
        if not chunks:
            return 0

        url = self._docs_index_url()
        actions = []
        for chunk in chunks:
            actions.append(
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
                },
            )
        payload = {"value": actions}
        headers = {"Content-Type": "application/json", "api-key": self._api_key}
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()

        results = body.get("value") or []
        if not isinstance(results, list):
            return len(chunks)
        succeeded = sum(1 for item in results if isinstance(item, dict) and item.get("status") is True)
        return succeeded

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
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
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
        headers = {"Content-Type": "application/json", "api-key": self._api_key}
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(self._docs_index_url(), headers=headers, json={"value": actions})
            response.raise_for_status()
        return len(ids)

    def build_document_filter(self, document_id: str) -> str:
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
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
        value = body.get("value") or []
        return value if isinstance(value, list) else []

    def _docs_index_url(self) -> str:
        return f"{self._endpoint}/indexes/{self._index_name}/docs/index?api-version={self._api_version}"

    def _docs_search_url(self) -> str:
        return f"{self._endpoint}/indexes/{self._index_name}/docs/search?api-version={self._api_version}"
