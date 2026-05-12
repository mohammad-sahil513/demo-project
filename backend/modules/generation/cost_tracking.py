"""Per-workflow generation phase LLM cost tracking.

Mirrors the retrieval tracker pattern: each generator pulls a snapshot
*before* its LLM call(s) and again *after*, then logs the delta into the
generation observability dict. The tracker silently ignores unknown models
(rate lookup miss) — that ensures a new model deployment without pricing
data does not poison cost tracking with NaNs.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.constants import MODEL_PRICING


@dataclass(frozen=True, slots=True)
class GenerationCostSnapshot:
    """Point-in-time snapshot used to compute deltas between operations."""

    llm_cost_usd: float
    total_tokens_in: int
    total_tokens_out: int
    total_llm_calls: int


class GenerationCostTracker:
    """Accumulate LLM usage for the GENERATION phase."""

    def __init__(self) -> None:
        self.llm_cost_usd: float = 0.0
        self.total_tokens_in: int = 0
        self.total_tokens_out: int = 0
        self.total_llm_calls: int = 0

    def track_call(self, *, model: str, task: str, input_tokens: int, output_tokens: int) -> None:
        """Record one LLM call. ``task`` is accepted for API parity but unused.

        Unknown models silently no-op (see module docstring) — keeps the
        workflow alive when a new deployment is added without pricing.
        """
        del task
        rates = MODEL_PRICING.get(model)
        if rates is None:
            return
        self.total_tokens_in += int(input_tokens)
        self.total_tokens_out += int(output_tokens)
        self.total_llm_calls += 1
        self.llm_cost_usd += (input_tokens / 1000.0) * rates["input"] + (output_tokens / 1000.0) * rates["output"]

    def snapshot(self) -> GenerationCostSnapshot:
        """Capture an immutable view of the tracker's current totals."""
        return GenerationCostSnapshot(
            llm_cost_usd=self.llm_cost_usd,
            total_tokens_in=self.total_tokens_in,
            total_tokens_out=self.total_tokens_out,
            total_llm_calls=self.total_llm_calls,
        )


def llm_delta_between_snapshots(
    before: GenerationCostSnapshot,
    after: GenerationCostSnapshot,
) -> tuple[int, int, float]:
    """Return ``(tokens_in, tokens_out, llm_cost_usd)`` added between two snapshots."""
    return (
        after.total_tokens_in - before.total_tokens_in,
        after.total_tokens_out - before.total_tokens_out,
        after.llm_cost_usd - before.llm_cost_usd,
    )
