"""Embed and upsert chunks into Azure AI Search."""

from __future__ import annotations

from modules.ingestion.chunker import IngestionChunk
from core.constants import MODEL_PRICING
from infrastructure.search_client import AzureSearchClient, SearchChunk
from infrastructure.sk_adapter import AzureSKAdapter


class DocumentIndexer:
    """Generate embeddings and upsert chunks in batches."""

    def __init__(
        self,
        search_client: AzureSearchClient,
        sk_adapter: AzureSKAdapter,
        *,
        batch_size: int = 50,
    ) -> None:
        self._search_client = search_client
        self._sk_adapter = sk_adapter
        self._batch_size = max(1, batch_size)

    def is_configured(self) -> bool:
        return self._search_client.is_configured() and self._sk_adapter.is_configured()

    async def index_chunks(self, chunks: list[IngestionChunk]) -> tuple[int, float]:
        if not chunks:
            return 0, 0.0

        with_vectors: list[SearchChunk] = []
        input_tokens = 0
        for chunk in chunks:
            embedding_result = await self._sk_adapter.generate_embedding_with_usage(chunk.text)
            input_tokens += embedding_result.prompt_tokens
            with_vectors.append(
                SearchChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    workflow_run_id=chunk.workflow_run_id,
                    text=chunk.text,
                    chunk_index=chunk.chunk_index,
                    section_heading=chunk.section_heading,
                    page_number=chunk.page_number,
                    content_type=chunk.content_type,
                    embedding=embedding_result.embedding,
                ),
            )

        indexed = 0
        for start in range(0, len(with_vectors), self._batch_size):
            batch = with_vectors[start : start + self._batch_size]
            indexed += await self._search_client.upsert_chunks(batch)

        rate = MODEL_PRICING["text-embedding-3-large"]["input"]
        embedding_cost = (input_tokens / 1000.0) * rate
        return indexed, embedding_cost
