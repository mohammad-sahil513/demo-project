# Pipeline

Consolidated workflow pipeline reference (replaces numbered phase/template/observability docs).

## Purpose
- Explain end-to-end workflow execution, template processing, generation behavior, and observability/citation flow.

## Inputs
- Workflow request (`document_id`, `template_id`, optional `doc_type`).
- Parsed/compiled template artifacts.
- Retrieved evidence from indexed BRD content.

## Outputs
- Completed workflow state transitions.
- Assembled document data with section outputs.
- Exported DOCX/XLSX artifacts and observability summaries.

## Failure Modes
- Missing dependencies/config can force skip/fail modes by environment policy.
- Template compile/binding issues can block export.
- Generation/diagram failures can degrade section quality or output completeness.

## 1) 8-Phase Execution Model

1. `INPUT_PREPARATION`
2. `INGESTION`
3. `TEMPLATE_PREPARATION`
4. `SECTION_PLANNING`
5. `RETRIEVAL`
6. `GENERATION`
7. `ASSEMBLY_VALIDATION`
8. `RENDER_EXPORT`

Phase wrapper behavior:
- emit `phase.started`
- run phase logic
- retry once on failure (2s delay)
- emit `phase.completed` or `phase.failed`

## 2) Ingestion and Retrieval

Ingestion:
- parse BRD (Document Intelligence),
- chunk text/tables,
- embed and index in Search.

Retrieval:
- per-section query resolution,
- hybrid retrieval (vector + keyword),
- evidence packaging with citations.

## 3) Template System in Pipeline

Template preparation converges to unified section schema:
- inbuilt templates -> static section plans/style maps,
- custom templates -> extract/classify/plan/preview pipeline.

Output of both paths:
- `list[SectionDefinition]` (shared downstream contract).

## 4) Generation Behavior

Generation runs dependency-aware waves:
- independent sections run in parallel,
- dependent sections wait for prerequisites.

Content generators:
- text sections,
- table sections,
- diagram sections (Kroki render flow).

Diagram policy:
- up to 3 PlantUML attempts,
- fallback up to 2 Mermaid attempts,
- deterministic stub fallback when needed.

## 5) Assembly and Export

Assembly:
- order sections,
- merge generation outputs,
- attach citation metadata for UI use.

Export:
- DOCX paths (inbuilt/custom with feature-flagged modes),
- XLSX paths for UAT/custom workbook flows,
- integrity/fidelity checks and output record creation.

## 6) Observability and Citations

Observability:
- per-call tracking,
- per-phase aggregation,
- per-workflow summary persistence.

Citations:
- retrieval -> packager -> generator -> assembler,
- used in preview/UI; not embedded into final deliverables unless explicitly designed.

## 7) Frontend Integration Notes

- Progress page uses SSE-first updates.
- Polling fallback via status endpoint.
- Output page consumes assembled sections and download endpoints.

## 8) Related Docs

- System/layers/models: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Endpoint contracts: [`API.md`](API.md)
- Template/release operations: [`TEMPLATE_OPERATIONS.md`](TEMPLATE_OPERATIONS.md), [`RELEASE_OPERATIONS.md`](RELEASE_OPERATIONS.md)
