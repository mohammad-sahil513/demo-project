"""Shared enums and pricing tables."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class WorkflowStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowPhase(StrEnum):
    INPUT_PREPARATION = "INPUT_PREPARATION"
    INGESTION = "INGESTION"
    TEMPLATE_PREPARATION = "TEMPLATE_PREPARATION"
    SECTION_PLANNING = "SECTION_PLANNING"
    RETRIEVAL = "RETRIEVAL"
    GENERATION = "GENERATION"
    ASSEMBLY_VALIDATION = "ASSEMBLY_VALIDATION"
    RENDER_EXPORT = "RENDER_EXPORT"


class DocType(StrEnum):
    PDD = "PDD"
    SDD = "SDD"
    UAT = "UAT"


class OutputFormat(StrEnum):
    DOCX = "DOCX"
    XLSX = "XLSX"


class TemplateSource(StrEnum):
    INBUILT = "inbuilt"
    CUSTOM = "custom"


class TemplateStatus(StrEnum):
    PENDING = "PENDING"
    COMPILING = "COMPILING"
    READY = "READY"
    FAILED = "FAILED"


class DocumentStatus(StrEnum):
    UPLOADED = "UPLOADED"
    READY = "READY"
    FAILED = "FAILED"


class DocumentIngestionStatus(StrEnum):
    """BRD indexing lifecycle in Azure AI Search (once per document_id)."""

    NOT_STARTED = "NOT_STARTED"
    INDEXED = "INDEXED"
    FAILED = "FAILED"


# Same ID shape as custom uploads (`tpl-` prefix) but stable and discoverable in API lists.
INBUILT_TEMPLATE_ID_PDD: Final[str] = "tpl-inbuilt-pdd"
INBUILT_TEMPLATE_ID_SDD: Final[str] = "tpl-inbuilt-sdd"
INBUILT_TEMPLATE_ID_UAT: Final[str] = "tpl-inbuilt-uat"

INBUILT_TEMPLATE_ID_BY_DOC_TYPE: Final[dict[DocType, str]] = {
    DocType.PDD: INBUILT_TEMPLATE_ID_PDD,
    DocType.SDD: INBUILT_TEMPLATE_ID_SDD,
    DocType.UAT: INBUILT_TEMPLATE_ID_UAT,
}


def inbuilt_template_id_for(doc_type: str | DocType) -> str:
    """Resolve the canonical template_id for an inbuilt document type."""
    return INBUILT_TEMPLATE_ID_BY_DOC_TYPE[DocType(doc_type)]


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
MODEL_PRICING: Final[dict[str, dict[str, float]]] = {
    "gpt5": {"input": 0.015, "output": 0.060},
    "gpt5mini": {"input": 0.00015, "output": 0.0006},
    "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
}

# Azure Document Intelligence — rough $ per page (prebuilt-layout); tune to your SKU/region.
DOCUMENT_INTELLIGENCE_USD_PER_PAGE: Final[float] = 0.01
