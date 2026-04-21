"""Roll LLM, embedding, and Document Intelligence estimates into one observability summary."""

from __future__ import annotations

from typing import Any

from core.config import settings
from core.constants import MODEL_PRICING


def llm_call_cost_usd(*, model_key: str, tokens_in: int, tokens_out: int) -> float:
    rates = MODEL_PRICING[model_key]
    return (tokens_in / 1000.0) * rates["input"] + (tokens_out / 1000.0) * rates["output"]


def document_intelligence_cost_usd(page_count: int) -> float:
    return max(0, page_count) * settings.document_intelligence_usd_per_page


def merge_full_cost_summary(
    base: dict[str, Any] | None,
    *,
    llm_cost_usd: float = 0.0,
    embedding_cost_usd: float = 0.0,
    document_intelligence_cost_usd: float = 0.0,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build/extend ``observability_summary`` with full dollar estimates.

    WorkflowExecutor should pass cumulative costs as phases complete. Non-LLM lines use
    ``document_intelligence_usd`` and ``embedding_cost_usd`` explicitly so the UI can
    show a single ``total_cost_usd`` that matches invoices (within model accuracy).
    """
    out: dict[str, Any] = dict(base or {})
    out["llm_cost_usd"] = float(out.get("llm_cost_usd", 0.0)) + llm_cost_usd
    out["embedding_cost_usd"] = float(out.get("embedding_cost_usd", 0.0)) + embedding_cost_usd
    out["document_intelligence_cost_usd"] = float(
        out.get("document_intelligence_cost_usd", 0.0),
    ) + document_intelligence_cost_usd
    out["total_cost_usd"] = (
        out["llm_cost_usd"] + out["embedding_cost_usd"] + out["document_intelligence_cost_usd"]
    )
    if extra:
        out.update(extra)
    return out
