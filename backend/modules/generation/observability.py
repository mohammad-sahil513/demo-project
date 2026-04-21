"""Merge generation-phase observability into workflow summary."""

from __future__ import annotations

from typing import Any

from modules.observability.cost_rollup import merge_full_cost_summary


def merge_generation_observability(
    base: dict[str, Any] | None,
    *,
    llm_cost_usd: float,
    generated_sections: int,
    total_tokens_in: int = 0,
    total_tokens_out: int = 0,
    total_llm_calls: int = 0,
) -> dict[str, Any]:
    prior_in = int(base.get("total_tokens_in", 0) if isinstance(base, dict) else 0)
    prior_out = int(base.get("total_tokens_out", 0) if isinstance(base, dict) else 0)
    prior_calls = int(base.get("total_llm_calls", 0) if isinstance(base, dict) else 0)
    return merge_full_cost_summary(
        base,
        llm_cost_usd=llm_cost_usd,
        extra={
            "generated_sections": generated_sections,
            "total_tokens_in": prior_in + total_tokens_in,
            "total_tokens_out": prior_out + total_tokens_out,
            "total_llm_calls": prior_calls + total_llm_calls,
        },
    )
