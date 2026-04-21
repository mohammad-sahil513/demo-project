"""ID helpers and timestamps."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _hex12() -> str:
    return uuid.uuid4().hex[:12]


def workflow_id() -> str:
    return f"wf-{_hex12()}"


def document_id() -> str:
    return f"doc-{_hex12()}"


def template_id() -> str:
    return f"tpl-{_hex12()}"


def output_id() -> str:
    return f"out-{_hex12()}"


def section_id() -> str:
    return f"sec-{_hex12()}"


def chunk_id() -> str:
    return f"chk-{_hex12()}"


def call_id() -> str:
    return f"call-{_hex12()}"


def chunk_id_for_document(document_id: str, chunk_index: int) -> str:
    """Stable chunk key for Azure Search upserts (ingest-once, idempotent)."""
    return f"{document_id}:chunk:{chunk_index:06d}"
