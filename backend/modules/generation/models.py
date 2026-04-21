"""Structured generation outputs persisted on ``WorkflowRecord.section_generation_results``."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GenerationSectionResult(BaseModel):
    """One section row after GENERATION (matches docs/04 contract)."""

    model_config = ConfigDict(extra="ignore")

    output_type: str
    content: str = ""
    diagram_path: str | None = None
    diagram_format: str | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    model: str = ""
    task: str = ""
    error: str | None = None
    citations: list[dict[str, object]] = Field(default_factory=list)
