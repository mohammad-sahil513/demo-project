"""Structured generation outputs persisted on ``WorkflowRecord.section_generation_results``.

The result is the public contract between the GENERATION phase and the
ASSEMBLY phase. See ``docs/ARCHITECTURE.md`` for model context and
``docs/PIPELINE.md`` for how each field is consumed downstream.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GenerationSectionResult(BaseModel):
    """One section row after GENERATION (matches docs/04 contract).

    ``output_type`` is one of ``"text"``/``"table"``/``"diagram"``. For
    diagrams, ``content`` holds the source (Mermaid/PlantUML) and
    ``diagram_path`` points at the rendered image on disk.
    ``error`` is only populated when generation failed but the section is
    still emitted (e.g. a placeholder when diagram rendering failed).
    """

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
