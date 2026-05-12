"""Pydantic model for the exported output JSON record.

An ``OutputRecord`` points at the final ``.docx``/``.xlsx`` artifact produced
by the render-export phase. The actual binary lives on disk; the record
captures size, status (``READY`` once written successfully), and the link
back to the originating workflow and document.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OutputRecord(BaseModel):
    """Final exported file metadata. The file itself lives at ``file_path``."""

    model_config = ConfigDict(extra="ignore")

    output_id: str
    workflow_run_id: str
    document_id: str
    doc_type: str
    output_format: str  # ``DOCX`` | ``XLSX``
    status: str
    file_path: str
    filename: str
    size_bytes: int
    created_at: str
    updated_at: str
    # ``ready_at`` is set when the output file is fully written and verified.
    # Useful for diagnosing partial writes from the timestamp pair.
    ready_at: str | None = None
