# 04 — Data Models & Schemas

> Every important data model in the system. What each field means and when it gets populated.
> These are the structures that flow through the pipeline. Understand these before writing any module.

---

## Repository Models (Persisted as JSON)

### `DocumentRecord` — `repositories/document_repo.py`

Stores metadata for an uploaded BRD file.

| Field | Type | Set When | Description |
|-------|------|----------|-------------|
| `document_id` | str | On upload | Prefixed ID: `"doc-3f2a1b9c8e12"` |
| `filename` | str | On upload | Original filename as uploaded |
| `content_type` | str | On upload | MIME type: `"application/pdf"` or docx MIME |
| `size_bytes` | int | On upload | File size in bytes |
| `status` | str | On upload → READY | `DocumentStatus` enum value |
| `file_path` | str | On upload | Relative path: `"doc-abc123.bin"` |
| `created_at` | str | On create | ISO 8601 UTC timestamp |
| `updated_at` | str | On update | ISO 8601 UTC timestamp |
| `page_count` | int | After parse | Populated from Azure Doc Intelligence result |
| `language` | str | After parse | Detected language code (e.g. `"en"`) |
| `doc_intelligence_confidence` | float | After parse | Language detection confidence score |
| `ingestion_status` | str | After Phase 2 | `NOT_STARTED` → `INDEXED` or `FAILED` — **ingest-once per BRD** (shared by PDD+SDD+UAT) |
| `indexed_chunk_count` | int | After index | Number of chunks written to Azure AI Search for this `document_id` |
| `indexed_at` | str | After index | ISO timestamp when indexing succeeded |
| `last_ingestion_error` | str | If ingest fails | Last error message from a failed ingest attempt |

**Ingest-once policy:** Phase 2 (INGESTION) runs the full parse → chunk → embed → upsert path **only until** `ingestion_status` is `INDEXED`. Additional workflow runs that reference the same `document_id` **skip** re-ingestion and reuse the same indexed chunks (filter retrieval by `document_id`). Concurrent workflows on the same BRD are serialized with a per-`document_id` **asyncio lock** in-process (v1 single-node). Chunk keys are **stable** (`chunk_id` derived from `document_id` + chunk index) so upserts stay idempotent.

---

### `TemplateRecord` — `repositories/template_repo.py`

Stores metadata for both inbuilt and custom templates.

| Field | Type | Set When | Description |
|-------|------|----------|-------------|
| `template_id` | str | On save | Prefixed ID: `"tpl-xyz789abc012"` |
| `filename` | str | On upload | Original filename |
| `template_type` | str | On upload | `DocType` value: `"PDD"`, `"SDD"`, or `"UAT"` |
| `template_source` | str | On create | `"inbuilt"` or `"custom"` |
| `version` | str | Optional | User-provided version label |
| `status` | str | Updates during compile | `"PENDING"` → `"COMPILING"` → `"READY"` or `"FAILED"` |
| `file_path` | str | On upload | Binary file path (custom only) |
| `preview_path` | str | After compile | Path to preview DOCX or HTML file |
| `compile_error` | str | If failed | Error message from compile attempt |
| `compiled_at` | str | After compile | ISO 8601 UTC timestamp |
| `section_plan` | list[dict] | After compile | Serialized `list[SectionDefinition]` — the entire section structure |
| `style_map` | dict | After compile | Serialized `StyleMap` — fonts, colors, margins |
| `sheet_map` | dict | After compile (UAT) | Sheet names + header structure from XLSX |

**Inbuilt templates (same contract as custom):** Stable `template_id` values — `tpl-inbuilt-pdd`, `tpl-inbuilt-sdd`, `tpl-inbuilt-uat` — with `template_source: "inbuilt"`. On application startup, the backend ensures corresponding `TemplateRecord` files exist (READY) so `POST /workflow-runs` always uses `{ document_id, template_id }` for both paths.

---

### `WorkflowRecord` — `repositories/workflow_repo.py`

The complete state machine for one workflow run. Updated continuously as phases progress.

**Core identity fields:**

| Field | Type | Description |
|-------|------|-------------|
| `workflow_run_id` | str | Prefixed ID: `"wf-abc123def456"` |
| `document_id` | str | Which BRD was uploaded |
| `template_id` | str | Which template to use |
| `doc_type` | str | `"PDD"`, `"SDD"`, or `"UAT"` |

**Status tracking:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | str | `"PENDING"` → `"RUNNING"` → `"COMPLETED"` or `"FAILED"` |
| `current_phase` | str | Name of the phase currently executing |
| `overall_progress_percent` | float | 0.0 to 100.0, computed from PHASE_WEIGHTS |
| `current_step_label` | str | Human-readable description (e.g. "Indexed 47 chunks") |

**Timestamps:**

| Field | Type | Set When |
|-------|------|----------|
| `created_at` | str | On create |
| `updated_at` | str | Every update |
| `started_at` | str | When executor begins phase 1 |
| `completed_at` | str | When phase 8 finishes |

**Phase tracking:**
`phases: list[PhaseRecord]` — each `PhaseRecord` contains:
- `phase`: phase name
- `status`: PENDING/RUNNING/COMPLETED/FAILED
- `started_at`, `completed_at`, `duration_ms`
- `error`: error message if failed
- `retry_count`: 0 or 1
- `tokens_in`, `tokens_out`, `cost_usd`: phase-level totals

**Pipeline data (grows as workflow progresses):**

| Field | Type | Populated After |
|-------|------|----------------|
| `section_plan` | list[dict] | Phase 3 — list of serialized SectionDefinition objects |
| `section_progress` | dict | Phase 4 — `{total, pending, running, completed, failed}` counts; **`failed` reflects phase-level failures**, not per-section row failures (section-level issues are recorded under `section_generation_results` / `warnings`) |
| `section_retrieval_results` | dict | Phase 5 — `{section_id: {context_text, citations: [...]}}` |
| `section_generation_results` | dict | Phase 6 — `{section_id: {output_type, content, diagram_*, citations, tokens_in, tokens_out, cost_usd, error}}` |
| `assembled_document` | dict | Phase 7 — serialized `AssembledDocument` (all sections merged) |
| `output_id` | str | Phase 8 — ID of the generated output record |

**Observability:**
`observability_summary`: dict with **full dollar estimates**: `llm_cost_usd`, `embedding_cost_usd`, `document_intelligence_cost_usd` (estimated from page count × configured rate), and `total_cost_usd` (**sum of the above**), plus `total_tokens_in`, `total_tokens_out`, `total_llm_calls`, and per-phase breakdown dict

**Errors:**
`errors: list[dict]` — each: `{phase, message, timestamp}`
`warnings: list[dict]` — same structure, non-fatal issues

---

### `OutputRecord` — `repositories/output_repo.py`

Created when Phase 8 completes and the file is ready for download.

| Field | Type | Description |
|-------|------|-------------|
| `output_id` | str | Prefixed ID: `"out-abc123"` |
| `workflow_run_id` | str | Parent workflow |
| `document_id` | str | Source document |
| `doc_type` | str | PDD / SDD / UAT |
| `output_format` | str | `"DOCX"` or `"XLSX"` |
| `status` | str | `"READY"` once file exists |
| `file_path` | str | Absolute path to the output file |
| `filename` | str | User-visible download filename (e.g. `"PDD_output.docx"`) |
| `size_bytes` | int | File size |
| `ready_at` | str | When file was created |

---

## Template System Models

### `SectionDefinition` — `modules/template/models.py`

THE canonical section schema. Every section in every document type — inbuilt or custom — becomes a `SectionDefinition`. The pipeline only knows this one shape.

| Field | Type | Description |
|-------|------|-------------|
| `section_id` | str | Unique section ID within this workflow |
| `title` | str | Section heading text (e.g. "Executive Summary") |
| `level` | int | Heading depth 1–6 (1 = top-level H1) |
| `parent_section_id` | str\|None | Links to parent heading's section_id |
| `output_type` | str | `"text"` \| `"table"` \| `"diagram"` |
| `description` | str | 1-2 sentence explanation of what content belongs here |
| `generation_hints` | list[str] | 3-6 specific topics/keywords for the LLM |
| `retrieval_query` | str | Optimised search query for Azure AI Search (≥4 words preferred) |
| `execution_order` | int | 0-indexed. Lower = generated first. Determines display order in output. |
| `dependencies` | list[str] | section_ids that must complete before this one starts |
| `expected_length` | str | `"short"` / `"medium"` / `"long"` — guidance for LLM |
| `tone` | str | `"formal"` / `"technical"` / `"structured"` |
| `required_fields` | list[str] | Generic expected column names (for tables) |
| `table_headers` | list[str]\|None | EXACT column headers from template (overrides `required_fields` when set) |
| `prompt_selector` | str | Filename (no `.yaml`) of the generation prompt to use |
| `is_complex` | bool | If True → use GPT-5 instead of GPT-5-mini for this section |

---

### `StyleMap` — `modules/template/models.py`

Carries all visual styling extracted from a DOCX template (or defined for inbuilt templates).

| Field | Type | Description |
|-------|------|-------------|
| `heading_styles` | dict[int, ParagraphStyle] | Keys 1–6. Style per heading level. |
| `body_style` | ParagraphStyle | Default body text style |
| `table_style` | TableStyle | Table borders, header colors, alternating rows |
| `page_setup` | PageSetup | Margins, orientation, paper size |
| `caption_style` | ParagraphStyle\|None | Style for figure captions (optional) |

**`ParagraphStyle`:** `font_name`, `font_size` (pt), `bold`, `italic`, `color` (hex), `space_before` (pt), `space_after` (pt), `line_spacing`

**`TableStyle`:** `border_color`, `header_bg`, `header_font_color`, `row_alt_bg`, `border_width`, `col_widths` (list of inches per column)

**`PageSetup`:** `margin_top`, `margin_bottom`, `margin_left`, `margin_right` (all inches), `orientation`, `paper_size`, `header_text`, `footer_text`

---

### `DocumentSkeleton` — `modules/template/models.py`

Intermediate extraction result from a custom DOCX. Used only during template compilation.

Contains `elements: list[SkeletonElement]` in document order.

**`SkeletonElement`:**
| Field | Value When |
|-------|-----------|
| `element_type` | `"heading"` for all headings; `"table_shell"` for tables |
| `level` | 1–6 for standard headings; `None` for faux-headings (bold paragraphs) |
| `text` | Heading text (cleaned of examples in brackets) |
| `table_headers` | First row of table cells (for table_shell elements) |
| `style_name` | Original DOCX style name (e.g. `"Heading 2"` or `"faux_heading"`) |

---

## Retrieval & Evidence Models

### `RetrievedChunk` — `modules/retrieval/retriever.py`

One chunk returned from Azure AI Search hybrid search.

| Field | Description |
|-------|-------------|
| `chunk_id` | Azure Search document key |
| `text` | The chunk text content |
| `section_heading` | Source section heading from original BRD (can be None) |
| `page_number` | Source page number (can be None) |
| `content_type` | `"text"` or `"table"` |
| `score` | Azure hybrid search relevance score |

---

### `Citation` — `modules/retrieval/packager.py`

Citation metadata attached to each generated section for frontend display.

| Field | Description |
|-------|-------------|
| `path` | Source heading path: `"3.2 Authentication Requirements"` |
| `page` | Source page number (or None if unknown) |
| `content_type` | `"text"` or `"table"` |
| `chunk_id` | Original chunk ID for traceability |

**Display format in UI:** `"{path}, p.{page} [{content_type}]"`

---

### `EvidenceBundle` — `modules/retrieval/packager.py`

Packaged retrieval result for one section — consumed by generators.

| Field | Description |
|-------|-------------|
| `section_id` | Links back to the section |
| `context_text` | Formatted multi-source text: `"[Source 1 — heading, p.N (type)]\n{text}\n\n---\n\n[Source 2...]"` |
| `citations` | `list[Citation]` — one per retrieved chunk |

---

## Generation Models

### `GenerationResult` — `modules/generation/orchestrator.py`

Result of generating one section. Created by text/table/diagram generators.

| Field | Description |
|-------|-------------|
| `section_id` | Links back to section plan |
| `output_type` | `"text"` / `"table"` / `"diagram"` |
| `content` | Generated markdown string — main deliverable |
| `diagram_source` | Raw PlantUML or Mermaid source code (diagram sections only) |
| `diagram_format` | `"plantuml"` or `"mermaid"` (which format succeeded) |
| `diagram_png_path` | Absolute path to rendered PNG on disk |
| `citations` | `list[Citation]` passed through from EvidenceBundle |
| `tokens_in` | Total input tokens used (all attempts summed for diagrams) |
| `tokens_out` | Total output tokens used |
| `cost_usd` | Total cost for this section's generation |
| `error` | Error message if generation failed or was partially degraded |

---

## Assembly Model

### `AssembledDocument` — `modules/assembly/assembler.py`

The full document ready for export. Stored in `WorkflowRecord.assembled_document` (as dict).

| Field | Description |
|-------|-------------|
| `workflow_run_id` | Parent workflow |
| `template_id` | Template used |
| `doc_type` | PDD / SDD / UAT |
| `title` | Document title: `"{filename} — {doc_type}"` |
| `total_sections` | Count of successfully assembled sections |
| `sections` | `list[AssembledSection]` ordered by `execution_order` |

**`AssembledSection`:**

| Field | Description |
|-------|-------------|
| `section_id` | Section identifier |
| `title` | Section heading text |
| `level` | Heading depth 1–6 |
| `output_type` | `"text"` / `"table"` / `"diagram"` |
| `content` | Generated markdown content (SAME string used in DOCX and API response) |
| `diagram_source` | Raw diagram code (stored but not shown in DOCX) |
| `diagram_format` | Format string or None |
| `diagram_png_path` | Path to PNG (embedded in DOCX) or None |
| `citations` | `list[dict]` — serialized Citation objects for frontend display |
| `execution_order` | Integer for ordering |
| `metadata` | Dict with: `parent_section_id`, `prompt_selector`, `cost_usd`, `tokens_in`, `tokens_out`, `error`, `is_complex` |

---

## Observability Models

### `LLMCallRecord` — logged to `observability.jsonl`

One line written per LLM API call. Append-only. Used for cost tracking and debugging.

| Field | Description |
|-------|-------------|
| `workflow_run_id` | Parent workflow |
| `phase` | Which phase triggered this call |
| `section_id` | Which section (if generation phase) |
| `model` | `"gpt5"` or `"gpt5mini"` |
| `purpose` | Task name: `"text_generation"`, `"diagram_generation"`, etc. |
| `attempt` | 1, 2, or 3 (for self-correction loops) |
| `tokens_in` | Input token count |
| `tokens_out` | Output token count |
| `duration_ms` | Wall-clock duration of the API call |
| `cost_usd` | Computed cost for this call |
| `timestamp` | ISO 8601 UTC |
| `success` | True/False |
| `error` | Error message if failed |

### Observability Summary (stored in WorkflowRecord)

```
{
  "llm_cost_usd": 0.40,
  "embedding_cost_usd": 0.01,
  "document_intelligence_cost_usd": 0.15,
  "total_cost_usd": 0.56,
  "total_tokens_in": 28000,
  "total_tokens_out": 12000,
  "total_llm_calls": 24,
  "phases": {
    "INGESTION": { "cost_usd": 0.01, "tokens_in": 5000, "tokens_out": 0, "calls": 1 },
    "RETRIEVAL": { "cost_usd": 0.001, "tokens_in": 300, "tokens_out": 0, "calls": 2 },
    "GENERATION": { "cost_usd": 0.41, "tokens_in": 22000, "tokens_out": 12000, "calls": 21 }
  }
}
```

---

## SSE Event Schema

Every SSE event data payload:

```
{
  "type": "<SSEEventType value>",
  "workflow_run_id": "wf-abc123",
  "timestamp": "2025-01-01T12:00:00.000Z",
  // ... event-specific fields
}
```

**Event-specific additional fields:**

| Event Type | Additional Fields |
|------------|------------------|
| `workflow.started` | `doc_type` |
| `workflow.completed` | `output_id`, `total_cost_usd` |
| `workflow.failed` | `error` |
| `phase.started` | `phase` |
| `phase.completed` | `phase`, `duration_ms` |
| `phase.failed` | `phase`, `error`, `retrying` (bool) |
| `section.generation.started` | `section_id`, `title`, `output_type` |
| `section.generation.completed` | `section_id`, `title`, `status`, `cost_usd`, `tokens` |
| `ingestion.parse.completed` | `pages`, `language` |
| `ingestion.chunk.completed` | `chunk_count` |
| `ingestion.index.completed` | `indexed_count`, `embedding_cost_usd` |
| `output.ready` | `output_id`, `format` |

---

## Azure AI Search Chunk Document Schema

What gets stored in the Azure search index per chunk:

| Field | Type | Description |
|-------|------|-------------|
| `chunk_id` | string (key) | Stable unique id per BRD (e.g. `{document_id}:chunk:{index}`) — **not** tied to a workflow run |
| `document_id` | string | Namespace filter — isolates chunks per BRD |
| `workflow_run_id` | string | Optional; omit or set empty when using ingest-once (index is shared across workflows) |
| `text` | string | The actual chunk text (searchable) |
| `embedding` | vector(3072) | text-embedding-3-large output |
| `chunk_index` | int | Sequential index within document |
| `section_heading` | string | Heading under which this chunk falls |
| `page_number` | int | Source page in original document |
| `content_type` | string | `"text"` or `"table"` |
