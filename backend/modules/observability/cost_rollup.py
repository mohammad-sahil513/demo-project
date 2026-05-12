"""Roll LLM, embedding, and Document Intelligence estimates into one observability summary.

Three flavors of cost are tracked separately so the UI can attribute spend:

- **LLM** — input + output tokens × per-1K rates from ``MODEL_PRICING``.
- **Embedding** — input tokens × the embedding rate (output is free).
- **Document Intelligence** — flat per-page rate from settings.

The helpers here perform arithmetic only; collection lives in the per-phase
modules that have direct access to the call/usage records.
"""

from __future__ import annotations

from typing import Any

from core.config import settings
from core.constants import MODEL_PRICING


def llm_call_cost_usd(*, model_key: str, tokens_in: int, tokens_out: int) -> float:
    """Compute USD cost for one LLM call given token counts and pricing key.

    Raises ``KeyError`` if ``model_key`` is missing from ``MODEL_PRICING`` —
    that's intentional so cost is never silently zero when a new model is
    added but pricing wasn't.
    """
    rates = MODEL_PRICING[model_key]
    return (tokens_in / 1000.0) * rates["input"] + (tokens_out / 1000.0) * rates["output"]


def document_intelligence_cost_usd(page_count: int) -> float:
    """Per-page cost for Document Intelligence prebuilt-layout.

    Clamps negative page counts to zero — defensive against malformed
    upstream metadata.
    """
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
