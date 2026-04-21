"""Workflow persistence model (minimal fields for guards and validation)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class WorkflowRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    workflow_run_id: str
    document_id: str
    template_id: str
    doc_type: str
    status: str = Field(default="PENDING")
    current_phase: str | None = None
    overall_progress_percent: float = 0.0
    current_step_label: str = ""
    output_id: str | None = None
    section_plan: list[dict[str, object]] = Field(default_factory=list)
    style_map: dict[str, object] = Field(default_factory=dict)
    sheet_map: dict[str, object] = Field(default_factory=dict)
    section_progress: dict[str, object] = Field(default_factory=dict)
    section_retrieval_results: dict[str, object] = Field(default_factory=dict)
    section_generation_results: dict[str, object] = Field(default_factory=dict)
    assembled_document: dict[str, object] = Field(default_factory=dict)
    observability_summary: dict[str, object] = Field(default_factory=dict)
    errors: list[dict[str, object]] = Field(default_factory=list)
    warnings: list[dict[str, object]] = Field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
