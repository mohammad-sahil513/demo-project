"""Shared enums, phase weights, and LLM routing / pricing tables.

This module is the single source of truth for status strings, workflow phase
identifiers, and the cost/model routing data used by the generation pipeline.
Other layers must import from here rather than spelling out raw strings — that
keeps SSE event names, persisted JSON, and frontend constants in lockstep.

Updating pricing
----------------
``MODEL_PRICING`` is denominated in **USD per 1,000 tokens** (input/output).
Update it when Azure OpenAI pricing changes. The keys must exactly match the
values used in ``TASK_TO_MODEL`` and the adapter aliases in
``infrastructure/sk_adapter.py``.

Updating workflow phase weights
-------------------------------
``PHASE_WEIGHTS`` values must sum to ``100.0`` so the progress bar on the
frontend lands at exactly 100 when the workflow completes. Increase a phase
weight when it is consistently slow and developers want finer-grained
progress visibility for it.

See ``docs/ARCHITECTURE.md`` for the persisted shapes that
reference these enums.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class WorkflowStatus(StrEnum):
    """Lifecycle state for a workflow run document.

    Transitions: ``PENDING -> RUNNING -> COMPLETED`` or ``... -> FAILED``.
    ``RUNNING`` is also the value reconciled on process restart by
    ``core.hosting.reconcile_interrupted_workflows``.
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowPhase(StrEnum):
    """The eight phases of a single workflow run, executed in order.

    Each value is emitted in SSE ``phase.started`` / ``phase.completed`` events
    and persisted on the workflow document so the UI can render progress.
    """

    INPUT_PREPARATION = "INPUT_PREPARATION"
    INGESTION = "INGESTION"
    TEMPLATE_PREPARATION = "TEMPLATE_PREPARATION"
    SECTION_PLANNING = "SECTION_PLANNING"
    RETRIEVAL = "RETRIEVAL"
    GENERATION = "GENERATION"
    ASSEMBLY_VALIDATION = "ASSEMBLY_VALIDATION"
    RENDER_EXPORT = "RENDER_EXPORT"


class DocType(StrEnum):
    """Top-level document type a workflow run targets.

    Each value has a corresponding inbuilt template (PDD/SDD/UAT) and at least
    one prompt YAML under ``backend/prompts/``.
    """

    PDD = "PDD"
    SDD = "SDD"
    UAT = "UAT"


class OutputFormat(StrEnum):
    """Final export format produced by ``modules.export``."""

    DOCX = "DOCX"
    XLSX = "XLSX"


class TemplateSource(StrEnum):
    """Origin of a template — either bundled with the app or user-uploaded."""

    INBUILT = "inbuilt"
    CUSTOM = "custom"


class TemplateStatus(StrEnum):
    """Per-template compilation state. ``READY`` is required for workflow use."""

    PENDING = "PENDING"
    COMPILING = "COMPILING"
    READY = "READY"
    FAILED = "FAILED"


class DocumentStatus(StrEnum):
    """Per-document upload state. ``READY`` means ingestion may begin."""

    UPLOADED = "UPLOADED"
    READY = "READY"
    FAILED = "FAILED"


class DocumentIngestionStatus(StrEnum):
    """BRD indexing lifecycle in Azure AI Search (once per document_id)."""

    NOT_STARTED = "NOT_STARTED"
    INDEXED = "INDEXED"
    FAILED = "FAILED"


# Same ID shape as custom uploads (`tpl-` prefix) but stable and discoverable in API lists.
# These IDs are intentionally human-readable; tests, fixtures, and the UI rely
# on them remaining unchanged across releases.
INBUILT_TEMPLATE_ID_PDD: Final[str] = "tpl-inbuilt-pdd"
INBUILT_TEMPLATE_ID_SDD: Final[str] = "tpl-inbuilt-sdd"
INBUILT_TEMPLATE_ID_UAT: Final[str] = "tpl-inbuilt-uat"

INBUILT_TEMPLATE_ID_BY_DOC_TYPE: Final[dict[DocType, str]] = {
    DocType.PDD: INBUILT_TEMPLATE_ID_PDD,
    DocType.SDD: INBUILT_TEMPLATE_ID_SDD,
    DocType.UAT: INBUILT_TEMPLATE_ID_UAT,
}


def inbuilt_template_id_for(doc_type: str | DocType) -> str:
    """Resolve the canonical template_id for an inbuilt document type.

    Accepts either the enum value or its string form so callers do not have to
    coerce before lookup. Raises ``ValueError`` (via ``DocType``) for unknown
    document types — this is intentional; we'd rather fail loudly than silently
    fall back to a wrong template.
    """
    return INBUILT_TEMPLATE_ID_BY_DOC_TYPE[DocType(doc_type)]


# Phase weight contract: values must sum to exactly 100.0 so the frontend
# progress bar reaches 100% on completion. When tweaking, run
# ``backend/tests/test_phase10_workers_sse.py`` to confirm cumulative progress
# still tracks the spec.
PHASE_WEIGHTS: Final[dict[WorkflowPhase, float]] = {
    WorkflowPhase.INPUT_PREPARATION: 2.0,
    WorkflowPhase.INGESTION: 25.0,
    WorkflowPhase.TEMPLATE_PREPARATION: 8.0,
    WorkflowPhase.SECTION_PLANNING: 5.0,
    WorkflowPhase.RETRIEVAL: 15.0,
    WorkflowPhase.GENERATION: 35.0,
    WorkflowPhase.ASSEMBLY_VALIDATION: 5.0,
    WorkflowPhase.RENDER_EXPORT: 5.0,
}

# --- LLM pricing ($ per 1K tokens) — update when Azure pricing changes ---
# IMPORTANT: keys match TASK_TO_MODEL values / adapter aliases.
# Embedding models have ``output: 0.0`` because they only consume input tokens.
MODEL_PRICING: Final[dict[str, dict[str, float]]] = {
    "gpt-5": {"input": 0.015, "output": 0.060},
    "gpt-5-mini": {"input": 0.00015, "output": 0.0006},
    "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
    "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
}

# --- LLM task routing ---
# Each generation task is mapped to a model deployment alias. ``gpt-5`` is the
# stronger (and more expensive) tier and is reserved for tasks where reasoning
# quality dominates cost — diagrams and complex narrative sections.
TASK_TO_MODEL: Final[dict[str, str]] = {
    "diagram_generation": "gpt-5",
    "diagram_correction": "gpt-5",
    "complex_section": "gpt-5",
    "text_generation": "gpt-5-mini",
    "table_generation": "gpt-5-mini",
    "template_classification": "gpt-5-mini",
    "retrieval_query_generation": "gpt-5-mini",
}

# Keep lightweight tasks lean; reserve stronger reasoning for genuinely harder tasks.
# These values are passed through to the OpenAI API ``reasoning.effort`` parameter.
TASK_TO_REASONING_EFFORT: Final[dict[str, str]] = {
    "diagram_generation": "medium",
    "diagram_correction": "low",
    "complex_section": "high",
    "text_generation": "low",
    "table_generation": "low",
    "template_classification": "low",
    "retrieval_query_generation": "low",
}

# Smaller, task-aware budgets reduce the chance of spending the whole completion budget
# in reasoning with no visible content. If a task starts truncating, bump its budget
# here rather than across-the-board.
TASK_TO_MAX_COMPLETION_TOKENS: Final[dict[str, int]] = {
    "diagram_generation": 10000,
    "diagram_correction": 12000,
    "complex_section": 10000,
    "text_generation": 8000,
    "table_generation": 8000,
    "template_classification": 2000,
    "retrieval_query_generation": 1000,
}

# Azure Document Intelligence — rough $ per page (prebuilt-layout); tune to your SKU/region.
DOCUMENT_INTELLIGENCE_USD_PER_PAGE: Final[float] = 0.01

# Maximum concurrent section retrieval calls during the RETRIEVAL phase.
# Higher values cut wall-clock latency but stress the Azure Search throttle.
retrieval_max_concurrent_sections: int = 3

# UAT schema validation severity policy.
# Codes in ``SCHEMA_WARNING_CODES`` are surfaced as observations but do not
# fail the workflow. Codes in ``SCHEMA_BLOCKING_CODES`` cause a hard failure.
SCHEMA_WARNING_CODES: Final[set[str]] = {
    "unmapped_generated_columns",
}
SCHEMA_BLOCKING_CODES: Final[set[str]] = {
    "schema_mismatch",
    "missing_required_columns",
    "docx_header_footer_integrity_failed",
    "docx_relationship_integrity_failed",
    "docx_media_integrity_failed",
    "docx_forbidden_document_xml_mutation",
    "docx_document_part_missing",
}

# Custom DOCX export policy: workflow fails and output is not persisted when any of these appear.
# ``frozenset`` so callers cannot accidentally mutate the policy at runtime.
DOCX_EXPORT_POLICY_BLOCKING_CODES: Final[frozenset[str]] = frozenset(
    {
        "docx_legacy_export_disallowed",
        "docx_native_prerequisites_unmet",
    }
)
