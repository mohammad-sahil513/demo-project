"""Section-level adaptive retrieval over Azure AI Search.

For each template section we want a small set of high-quality chunks from
the BRD. The retriever:

1. Picks a query — uses the section's ``retrieval_query`` directly when it
   has at least :data:`MIN_DIRECT_QUERY_WORDS` words, otherwise asks the LLM
   to synthesize one from the section title/description/hints.
2. Embeds the query (Azure OpenAI ``text-embedding-3-large``).
3. Runs a *hybrid* search (keyword + vector) on Azure AI Search filtered to
   the workflow's ``document_id``.

The result is the raw chunk list plus the embedding-USD cost for cost rollups.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from time import perf_counter


from core.config import settings
from core.constants import MODEL_PRICING
from infrastructure.search_client import AzureSearchClient
from infrastructure.sk_adapter import AzureSKAdapter
from modules.template.models import SectionDefinition
from modules.observability.cost_rollup import merge_full_cost_summary

# Below this word count the section's hard-coded retrieval query is too thin
# to be useful — we ask the LLM to generate a better one instead.
MIN_DIRECT_QUERY_WORDS = 4
logger = logging.getLogger(__name__)

@dataclass(slots=True)
class RetrievedChunk:
    """One chunk returned by Azure Search, with the relevance score attached."""

    chunk_id: str
    text: str
    section_heading: str | None
    page_number: int | None
    content_type: str
    score: float = 0.0


class SectionRetriever:
    """Resolve section query, search chunks, and return normalized retrieval hits."""

    def __init__(
        self,
        search_client: AzureSearchClient,
        sk_adapter: AzureSKAdapter,
        *,
        top_k: int | None = None,
    ) -> None:
        self._search_client = search_client
        self._sk_adapter = sk_adapter
        self._top_k = top_k if top_k is not None else settings.retrieval_top_k

    def is_configured(self) -> bool:
        return self._search_client.is_configured() and self._sk_adapter.is_configured()

    async def retrieve_for_section(
        self,
        section: SectionDefinition,
        *,
        document_id: str,
        cost_tracker: object | None = None,
    ) -> tuple[list[RetrievedChunk], float]:
        """Run one hybrid search for ``section`` and return chunks + USD cost."""
        started_at = perf_counter()

        query_text = await self._resolve_query(section, cost_tracker=cost_tracker)
        embedding_result = await self._sk_adapter.generate_embedding_with_usage(query_text)

        raw = await self._search_client.hybrid_search(
            search_text=query_text,
            embedding=embedding_result.embedding,
            document_id=document_id,
            top_k=self._top_k,
        )

        rate = MODEL_PRICING["text-embedding-3-large"]["input"]
        embedding_cost_usd = (embedding_result.prompt_tokens / 1000.0) * rate

        chunks: list[RetrievedChunk] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            chunks.append(
                RetrievedChunk(
                    chunk_id=str(item.get("chunk_id") or ""),
                    text=str(item.get("text") or ""),
                    section_heading=self._as_optional_str(item.get("section_heading")),
                    page_number=self._as_optional_int(item.get("page_number")),
                    content_type=str(item.get("content_type") or "text"),
                    score=float(item.get("@search.score") or item.get("score") or 0.0),
                ),
            )

        duration_ms = int((perf_counter() - started_at) * 1000)
        logger.info(
            "retrieval.section.metrics section_id=%s document_id=%s top_k=%s query_word_count=%s "
            "chunk_count=%s embedding_cost_usd=%s duration_ms=%s",
            section.section_id,
            document_id,
            self._top_k,
            len(query_text.split()),
            len(chunks),
            embedding_cost_usd,
            duration_ms,
        )

        return chunks, embedding_cost_usd

    async def _resolve_query(
        self,
        section: SectionDefinition,
        *,
        cost_tracker: object | None = None,
    ) -> str:
        """Pick the best query string for ``section`` (direct, generated, fallback)."""
        direct_query = (section.retrieval_query or "").strip()
        # Use the configured query verbatim when it's substantive.
        if len(direct_query.split()) >= MIN_DIRECT_QUERY_WORDS:
            return direct_query

        # Otherwise ask the LLM to synthesize a richer query. The
        # ``retrieval_query_generation`` task budget is intentionally small
        # (see TASK_TO_MAX_COMPLETION_TOKENS) — we want one line back.
        prompt = self._build_query_generation_prompt(section)
        generated = (
            await self._sk_adapter.invoke_text(
                prompt,
                task="retrieval_query_generation",
                cost_tracker=cost_tracker,
            )
        ).strip()
        if len(generated.split()) >= MIN_DIRECT_QUERY_WORDS:
            return generated
        # Final fall-backs: the original direct query (even if thin) or a
        # concatenation of the section's title + description as a last resort.
        if direct_query:
            return direct_query
        return f"{section.title} {section.description}".strip()

    @staticmethod
    def _build_query_generation_prompt(section: SectionDefinition) -> str:
        return (
            "Generate one concise enterprise-search query (8-12 words) for retrieving source evidence.\n"
            "Return plain text only.\n\n"
            f"Section title: {section.title}\n"
            f"Section description: {section.description}\n"
            f"Section hints: {section.generation_hints}\n"
            f"Current retrieval query: {section.retrieval_query}\n"
        )

    @staticmethod
    def _as_optional_int(value: object) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _as_optional_str(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None


def merge_retrieval_observability(
    base: dict[str, object] | None,
    *,
    llm_cost_usd: float = 0.0,
    embedding_cost_usd: float,
    retrieved_sections: int,
    total_tokens_in: int = 0,
    total_tokens_out: int = 0,
    total_llm_calls: int = 0,
) -> dict[str, object]:
    """Merge retrieval-phase metrics into a workflow's observability dict.

    Token / call counts are *added* to whatever was in ``base`` so re-runs and
    partial retrieves keep cumulative totals correct.
    """
    return merge_full_cost_summary(
        base,
        llm_cost_usd=llm_cost_usd,
        embedding_cost_usd=embedding_cost_usd,
        extra={
            "retrieved_sections": retrieved_sections,
            "total_tokens_in": int(base.get("total_tokens_in", 0) if isinstance(base, dict) else 0) + total_tokens_in,
            "total_tokens_out": int(base.get("total_tokens_out", 0) if isinstance(base, dict) else 0)
            + total_tokens_out,
            "total_llm_calls": int(base.get("total_llm_calls", 0) if isinstance(base, dict) else 0) + total_llm_calls,
        },
    )
