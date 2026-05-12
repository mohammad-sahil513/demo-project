"""Pydantic model for the workflow run JSON record.

A ``WorkflowRecord`` is the source of truth for a single end-to-end run:
input pointers (document + template), running status, progress, per-section
artifacts, the final assembled document, and any errors/warnings collected
along the way.

The frontend polls/streams this record via SSE — ``current_phase``,
``overall_progress_percent``, and ``current_step_label`` are the three
fields the progress page renders most heavily.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class WorkflowRecord(BaseModel):
    """Persistent state of a workflow run; mutated incrementally by phases."""

    # ``extra="ignore"`` allows forward-compatibility with older records.
    model_config = ConfigDict(extra="ignore")

    workflow_run_id: str
    document_id: str
    template_id: str
    doc_type: str
    # ``WorkflowStatus`` literal — PENDING/RUNNING/COMPLETED/FAILED.
    status: str = Field(default="PENDING")
    # Current phase enum value or ``None`` if not yet started.
    current_phase: str | None = None
    # 0.0..100.0; computed from ``PHASE_WEIGHTS`` and within-phase progress.
    overall_progress_percent: float = 0.0
    current_step_label: str = ""
    output_id: str | None = None

    # Per-phase artifacts. Stored as plain dicts/lists for forward-compat —
    # the modules that produce/consume them are responsible for their shape.
    section_plan: list[dict[str, object]] = Field(default_factory=list)
    style_map: dict[str, object] = Field(default_factory=dict)
    sheet_map: dict[str, object] = Field(default_factory=dict)
    section_progress: dict[str, object] = Field(default_factory=dict)
    section_retrieval_results: dict[str, object] = Field(default_factory=dict)
    section_generation_results: dict[str, object] = Field(default_factory=dict)
    assembled_document: dict[str, object] = Field(default_factory=dict)
    observability_summary: dict[str, object] = Field(default_factory=dict)
    # Each error/warning is ``{"code": str, "detail": str, "at": iso_ts, ...}``.
    errors: list[dict[str, object]] = Field(default_factory=list)
    warnings: list[dict[str, object]] = Field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
