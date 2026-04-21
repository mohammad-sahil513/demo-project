"""Output persistence model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OutputRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    output_id: str
    workflow_run_id: str
    document_id: str
    doc_type: str
    output_format: str
    status: str
    file_path: str
    filename: str
    size_bytes: int
    created_at: str
    updated_at: str
    ready_at: str | None = None
