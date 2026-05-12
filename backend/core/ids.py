"""Type-prefixed ID generators and ISO-8601 UTC timestamps.

Every domain object has a stable prefix so an ID alone tells you what it
refers to (and a quick ``grep`` over logs is enough to trace a request).

Prefixes
--------
- ``wf-``   workflow run
- ``doc-``  uploaded source document
- ``tpl-``  template
- ``out-``  exported output file
- ``sec-``  section (template plan / generated)
- ``chk-``  ingestion chunk
- ``call-`` LLM call observability record

IDs are 12-hex-char UUID slices — short enough to be readable in logs but
collision-resistant in practice for this workload (a few hundred runs per
day in the largest deployment).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string with ``Z`` suffix.

    The ``Z`` suffix matches the format expected by the frontend and most
    JSON consumers; ``datetime.isoformat`` emits ``+00:00`` which we rewrite
    for consistency.
    """
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _hex12() -> str:
    # Use ``uuid4`` for randomness — 48 bits is enough for our workload and
    # keeps IDs short. If you ever need globally unique IDs across data
    # exports, swap to full ``uuid4().hex``.
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
    """Stable chunk key for Azure Search upserts (ingest-once, idempotent).

    The chunk index is zero-padded to 6 digits so chunks sort lexicographically
    in storage and search results. Do not change the format — existing index
    documents key off this exact string.
    """
    return f"{document_id}_chunk_{chunk_index:06d}"
