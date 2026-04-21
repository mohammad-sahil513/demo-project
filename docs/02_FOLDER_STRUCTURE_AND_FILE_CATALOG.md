# 02 — Folder Structure & File Catalog

> Every file in the backend. What it is. What it does. What it talks to.
> Read this before creating any file — use it as your map.

---

## Top-Level Layout

```
backend/
├── main.py                    ← FastAPI app factory (entry point)
├── .env                       ← NOT committed (copy from .env.example)
├── .env.example               ← All required env var keys with blank values
├── requirements.txt           ← All Python dependencies
│
├── core/                      ← Shared foundation — imported by everything
├── api/                       ← HTTP routing — calls services only
├── repositories/              ← JSON file persistence
├── services/                  ← Business orchestration
├── modules/                   ← Domain logic separated by concern
├── infrastructure/            ← Azure SDK adapters
├── workers/                   ← Async background task dispatch
└── prompts/                   ← YAML prompt files for all LLM calls
```

---

## `main.py`

**What it is:** FastAPI application factory. The entry point.

**What it does:**
- Creates the FastAPI app with lifespan context (startup + shutdown hooks)
- On startup: calls `configure_logging()` then `ensure_storage_dirs()`
- Registers CORS middleware (allows frontend origin)
- Registers request-ID middleware (adds X-Request-Id header to every response)
- Registers exception handlers for NotFoundException, SDLCBaseException, and generic Exception
- Mounts `api_router` at `settings.api_prefix` (which is `/api`)

**Important:** Never put business logic here. Configuration only.

---

## `core/` — Foundation Layer (6 files)

No file in `core/` may import from any other backend layer. It's the bedrock.

### `core/config.py`
**What it does:**
- Defines the `Settings` class using `pydantic-settings`, which auto-reads `.env` file
- Exposes all configuration as typed attributes (strings, ints, booleans, Paths)
- Storage subdirectories (`documents_path`, `templates_path`, etc.) are `@property` methods that compute from `storage_root`
- `ensure_storage_dirs()` creates all storage directories if missing — called once at startup
- Exports a module-level `settings` singleton — import this everywhere, never re-instantiate

**Key values it holds:** Azure endpoints/keys, CORS origins, storage root path, chunk sizes, retrieval top-K, generation token budgets per task type

### `core/constants.py`
**What it does:**
- Defines ALL enums used across the system as string enums (e.g. `WorkflowStatus.RUNNING == "RUNNING"`)
- Must be the single source of truth — never use raw status strings anywhere else
- Also defines `PHASE_WEIGHTS` dict (floats that sum to 100.0 — used to compute progress %)
- Defines `TASK_TO_MODEL`, `TASK_TO_REASONING_EFFORT`, `TASK_TO_TOKEN_BUDGET` — LLM routing tables
- Defines `MODEL_PRICING` — cost per 1K tokens per model (input + output separately)

**Enums exported:** `WorkflowStatus`, `WorkflowPhase`, `DocType`, `OutputType`, `OutputFormat`, `TemplateSource`, `TemplateStatus`, `DocumentStatus`, `SectionStatus`, `DiagramFormat`, `IngestionStage`, `SSEEventType`

### `core/exceptions.py`
**What it does:**
- Defines the custom exception hierarchy
- All exceptions extend `SDLCBaseException`, which carries `message` + `code`
- The API exception handlers in `main.py` catch these and map to HTTP responses
- Specific exceptions carry context (e.g. `NotFoundException` carries `resource` + `resource_id`)

**Exceptions defined:** `SDLCBaseException`, `NotFoundException`, `ValidationException`, `WorkflowException`, `IngestionException`, `TemplateException`, `GenerationException`, `DiagramRenderException`, `ExportException`, `InfrastructureException`

### `core/response.py`
**What it does:**
- Provides three helper functions that build standard JSON response envelopes
- Every API endpoint returns one of these — never raw dicts
- `success_response(data, message, meta, status_code=200)` → `{success:true, message, data, errors:[], meta}`
- `created_response(data, message)` → same but status 201
- `error_response(message, errors, status_code=400)` → `{success:false, message, data:null, errors:[{code,detail}]}`

**Why it matters:** Frontend Axios client parses the envelope. If this shape changes, frontend breaks.

### `core/ids.py`
**What it does:**
- Provides ID generation functions for every resource type
- Format: `"{prefix}-{12-char-hex-uuid}"` e.g. `"wf-3f2a1b9c8e12"`
- Functions: `workflow_id()`, `document_id()`, `template_id()`, `output_id()`, `section_id()`, `chunk_id()`, `call_id()`
- Also provides `utc_now()` → current UTC time as ISO 8601 string
- Consistency: every ID in the system has a type-readable prefix

### `core/logging.py`
**What it does:**
- Configures `structlog` for structured logging (JSON in prod, human-readable in dev)
- `configure_logging()` — sets up processors, log level, renderer. Called once at startup.
- `get_logger(name)` — returns a named bound logger. Used at the top of every module.
- `bind_workflow_context(workflow_run_id, doc_type)` — binds context vars so every log line in a workflow run includes the workflow ID automatically
- `get_workflow_log_path(id)` and `get_workflow_observability_path(id)` — return file paths for per-run logs

---

## `api/` — HTTP Layer (8 files)

**Rule:** API files call services only. Never directly call modules, repositories, or infrastructure.

### `api/router.py`
**What it does:**
- Creates the central `api_router`
- Uses `include_router()` to mount all 6 sub-routers with their prefix and tag
- Prefixes: health (`""`), documents (`/documents`), templates (`/templates`), workflows (`/workflow-runs`), outputs (`/outputs`), events (`/workflow-runs`)

### `api/deps.py`
**What it does:**
- Provides FastAPI `Depends()` provider functions for all repositories and services
- Two module-level singletons (created once when module loads): `EventService` and `TaskDispatcher` — these must NOT be re-created per request
- Every `get_*_service()` function instantiates the service with its injected repo
- `get_workflow_executor()` wires WorkflowExecutor with WorkflowService + EventService

### `api/routes/health.py`
**Endpoints:**
- `GET /api/health` — simple liveness check, always returns `{"status": "ok"}`
- `GET /api/ready` — readiness check, returns which Azure services are configured (checks if endpoint strings are non-empty), also shows storage root and Kroki URL

### `api/routes/documents.py`
**Endpoints:**
- `POST /api/documents/upload` — accepts multipart file (PDF or DOCX only), validates content-type, reads bytes, calls `DocumentService.save_document()`, returns document_id immediately. No processing triggered here.
- `GET /api/documents` — list all uploaded documents newest first
- `GET /api/documents/{document_id}` — get single document record
- `DELETE /api/documents/{document_id}` — delete file from disk and metadata record

### `api/routes/templates.py`
**Endpoints:**
- `POST /api/templates/upload` — accepts multipart file + `template_type` form field (PDD/SDD/UAT) + optional `version`. Saves file, creates COMPILING record, dispatches compile as background task, returns HTTP 201 with `status: COMPILING` immediately.
- `GET /api/templates` — list all templates
- `GET /api/templates/{id}` — single template record
- `GET /api/templates/{id}/compile-status` — lightweight endpoint frontend polls during compilation spinner. Returns `status`, `error`, `compiled_at`, `section_count`.
- `GET /api/templates/{id}/download` — returns raw binary file (for docx-preview in frontend)
- `GET /api/templates/{id}/preview-html` — UAT only: returns HTML table string for preview
- `DELETE /api/templates/{id}` — delete file + record

### `api/routes/workflows.py`
**Endpoints:**
- `POST /api/workflow-runs` — body: `{document_id, template_id, doc_type?, start_immediately}`. Auto-detects `doc_type` from template if not provided. Creates WorkflowRecord. If `start_immediately=true`, dispatches executor as background task. Returns HTTP 201 immediately.
- `GET /api/workflow-runs` — list all, newest first
- `GET /api/workflow-runs/{id}` — full record (includes assembled_document — large response)
- `GET /api/workflow-runs/{id}/status` — **lightweight polling endpoint**. Returns only: `workflow_run_id`, `status`, `current_phase`, `overall_progress_percent`, `current_step_label`, `document_id`, `template_id`, `output_id`. Frontend polls this every 3s when SSE unavailable.
- `GET /api/workflow-runs/{id}/sections` — section_plan + section_progress counters
- `GET /api/workflow-runs/{id}/observability` — cost/token breakdown from observability_summary
- `GET /api/workflow-runs/{id}/errors` — errors + warnings list
- `GET /api/workflow-runs/{id}/diagnostics` — full diagnostic dump: phases + timing + observability

### `api/routes/outputs.py`
**Endpoints:**
- `GET /api/outputs/{output_id}` — output metadata record
- `GET /api/outputs/{output_id}/download` — `FileResponse` with correct Content-Type (DOCX or XLSX) and `Content-Disposition: attachment`. This triggers browser download.

### `api/routes/events.py`
**Endpoint:**
- `GET /api/workflow-runs/{id}/events` — SSE stream via `StreamingResponse`
- Calls `EventService.subscribe(id)` to get a queue
- Generator loop: `await queue.get()` with 30s timeout → yield `data: {json}\n\n`
- On 30s timeout (no events): yield `": heartbeat\n\n"` (SSE comment line, keeps connection alive)
- On terminal event (`workflow.completed` or `workflow.failed`): break loop
- `finally`: call `EventService.unsubscribe(id, queue)` to clean up
- Response headers: `Cache-Control: no-cache`, `X-Accel-Buffering: no` (disables nginx buffering)

---

## `repositories/` — Persistence Layer (5 files)

One JSON file per record. No database. One repo class per resource type.

### `repositories/base.py`
**What it does:**
- Generic `BaseJsonRepository[T]` class. T is any Pydantic model.
- Constructor takes `storage_path: Path` and `model_class: Type[T]`
- `save(record)` — write model to `{storage_path}/{id}.json` (create or overwrite)
- `get(id)` — read JSON file, parse as model, return `None` if file missing
- `get_or_raise(id, resource_name)` — calls `get()`, raises `NotFoundException` if None
- `list_all()` — glob all `.json` files, parse all, sort newest-first by `created_at`
- `update(id, **fields)` — load + model_copy with new fields + `updated_at=utc_now()` + save
- `delete(id)` — unlink file, return True/False
- Subclasses override `_id_field()` to specify the primary key field name (e.g. `"document_id"`)

### `repositories/document_repo.py`
**Model: `DocumentRecord`**
Fields: `document_id`, `filename`, `content_type`, `size_bytes`, `status`, `file_path` (relative), `created_at`, `updated_at`
Post-parse fields (populated after Doc Intelligence): `page_count`, `language`, `doc_intelligence_confidence`

### `repositories/template_repo.py`
**Model: `TemplateRecord`**
Fields: `template_id`, `filename`, `template_type` (PDD/SDD/UAT), `template_source` (inbuilt/custom), `version`, `status`, `file_path`, `preview_path`, `created_at`, `updated_at`
Compile state: `compile_error`, `compiled_at`
Compiled artifacts: `section_plan` (list of SectionDefinition dicts), `style_map` (dict), `sheet_map` (dict, UAT only)

### `repositories/workflow_repo.py`
**Model: `WorkflowRecord`** — most complex record, stores complete pipeline state
Core: `workflow_run_id`, `document_id`, `template_id`, `doc_type`, `status`, `current_phase`, `overall_progress_percent`, `current_step_label`
Timestamps: `created_at`, `updated_at`, `started_at`, `completed_at`
Phase tracking: `phases` (list of PhaseRecord — each phase records its own timing + cost + status)
Pipeline data (grows as workflow progresses): `section_plan`, `section_progress`, `section_retrieval_results`, `section_generation_results`, `assembled_document`, `output_id`
Observability: `observability_summary` (rolled-up totals)
Errors: `errors` list, `warnings` list

**Extra method:** `list_by_document(document_id)` — filter workflows by document

### `repositories/output_repo.py`
**Model: `OutputRecord`**
Fields: `output_id`, `workflow_run_id`, `document_id`, `doc_type`, `output_format` (DOCX/XLSX), `status`, `file_path` (absolute path to output file), `filename` (user-visible name), `size_bytes`, `created_at`, `updated_at`, `ready_at`

---

## `services/` — Orchestration Layer (6 files)

Services coordinate between API layer, repositories, and domain modules.

### `services/document_service.py`
**What it does:**
- `save_document(filename, content_type, content: bytes)` — generates doc_id, writes bytes to `documents_path/{doc_id}.bin`, creates DocumentRecord, returns record
- `get_or_raise(document_id)` — delegates to repo
- `list_all()` — delegates to repo
- `delete(document_id)` — deletes binary file AND metadata JSON
- `get_file_path(document_id)` — returns absolute Path to the binary file

### `services/template_service.py`
**What it does:**
- `save_template(filename, content_type, template_type, content, version)` — saves binary, creates COMPILING record
- `compile_template(template_id)` — **async background method**, the full compile pipeline:
  - DOCX: extractor → classifier → planner → preview_generator → update record READY
  - XLSX: extractor → build SectionDefinitions from sheets → HTML preview → update record READY
  - On any exception: update record to FAILED + store error message
- `get_or_raise`, `list_all`, `delete`, `get_file_path` — standard CRUD
- `get_preview_html(template_id)` — reads the `.html` preview file from disk, returns as string (UAT only)

### `services/workflow_service.py`
**What it does:**
- `create(document_id, template_id, doc_type)` — creates WorkflowRecord with `status=PENDING`
- `get`, `get_or_raise`, `update(**fields)`, `list_all` — delegates to repo
- `get_document(document_id)` — helper: instantiates DocumentRepository and fetches document (used by WorkflowExecutor to get file paths)
- `get_template(template_id)` — same pattern for templates

### `services/output_service.py`
**What it does:**
- `create(workflow_run_id, document_id, doc_type, output_format, file_path, filename, size_bytes)` — creates OutputRecord with `status=READY`
- `get_or_raise(output_id)` — delegates to repo
- `get_download_info(record)` → `(Path, media_type_string, filename_string)` — determines correct Content-Type (DOCX vs XLSX) and user-visible filename for FileResponse

### `services/event_service.py`
**What it does:**
- In-memory SSE broker. Stores dict mapping `workflow_run_id → list[asyncio.Queue]`
- `subscribe(workflow_run_id)` — creates a new `asyncio.Queue(maxsize=200)`, appends to list, returns it. One queue per browser tab/connection.
- `unsubscribe(workflow_run_id, queue)` — removes queue from list, cleans up entry if list empty
- `emit(workflow_run_id, event_type, payload)` — builds event dict with `type`, `workflow_run_id`, `timestamp`, plus all payload fields. Puts into all subscriber queues (non-blocking `put_nowait`).

### `services/workflow_executor.py`
**What it does:** THE most important file. Runs all 8 phases end-to-end.
- Contains `WorkflowExecutor` class + inner `ObservabilityCostTracker` class
- `run(workflow_run_id)` — main entry point. Called by `TaskDispatcher`. Executes phases 1–8 in order. On success: marks COMPLETED + emits `workflow.completed`. On exception: marks FAILED + emits `workflow.failed`.
- `_run_phase(phase, fn, *args)` — wraps any phase function: emits `phase.started`, runs fn, emits `phase.completed`. On exception: retries once after 2s delay. If retry also fails: raises `WorkflowPhaseError`.
- `_compute_progress(completed_phase)` — uses PHASE_WEIGHTS to compute overall progress percentage
- 8 private `_phase_*` methods — one per pipeline phase, each calls the appropriate module

**`ObservabilityCostTracker`** (inner class):
- `record(call_result, task, phase, section_id)` — appends to in-memory list AND writes one JSON line to `observability.jsonl` file immediately
- `get_summary()` — returns dict with total cost, total tokens, total calls, breakdown by phase

---

## `workers/` — Background Task Dispatch (1 file)

### `workers/dispatcher.py`
**What it does:**
- `TaskDispatcher` class with one method: `dispatch(background_tasks, fn, *args)`
- If `background_tasks` (FastAPI `BackgroundTasks`) is available: uses `background_tasks.add_task()`
- If not available (direct call): gets running asyncio loop and calls `loop.create_task()`
- Wraps execution in try/catch to log errors without crashing the calling context
- Used for two things: template compilation (on upload) and workflow execution (on workflow create)

---

## `infrastructure/` — Azure SDK Wrappers (3 files)

**Rule:** No business logic. Only translate domain calls to/from Azure SDK calls.

### `infrastructure/sk_adapter.py`
**What it does:**
- `AzureSKAdapter` — central adapter for ALL LLM calls. Never call OpenAI directly outside this file.
- On init: creates two Semantic Kernel instances (one for gpt5 deployment, one for gpt5mini)
- `invoke_text(prompt, task, ...)` — looks up model + reasoning_effort + token_budget from TASK_TO_MODEL/etc. dicts. Calls SK. Extracts token usage from metadata. Creates `LLMCallResult`. If `cost_tracker` provided, calls `cost_tracker.record()`. Logs the call.
- `invoke_json(prompt, task, ...)` — same as invoke_text but strips markdown fences from response and parses as JSON. Raises `ValueError` if parse fails.
- `generate_embedding(text)` — calls Azure OpenAI embeddings endpoint with `text-embedding-3-large`. Returns `list[float]` (3072 dimensions).
- GPT-5 policy enforced here: uses `max_completion_tokens` + `reasoning_effort` in `extra_body`. NO `temperature`. NO `max_tokens`.

**`LLMCallResult`** object carries: `content`, `tokens_in`, `tokens_out`, `model`, `duration_ms`, `call_id`, `cost_usd` (computed from MODEL_PRICING)

### `infrastructure/search_client.py`
**What it does:**
- `AzureSearchClient` — wraps Azure AI Search async client
- `upsert_chunks(chunks: list[dict])` — calls `upload_documents()` to batch-upsert chunk records into the search index
- `hybrid_search(query_text, query_embedding, document_id, top_k)` — runs hybrid search: `VectorizedQuery` for vector similarity + `search_text` for BM25 keyword. Always filtered by `document_id` to namespace results per document. Returns list of result dicts.
- `delete_by_document(document_id)` — searches all chunks with that document_id, then deletes them (used when a document is deleted)

### `infrastructure/doc_intelligence.py`
**What it does:**
- `AzureDocIntelligenceClient` — wraps Azure Document Intelligence async client
- `analyze_document(file_path)` — reads file bytes, sends to `prebuilt-layout` model, awaits result
- Extracts: paragraphs (with heading context), tables (converted to markdown), figure captions
- Returns `ParsedDocument` with per-page `ParsedPage` objects (text, tables, image_captions)
- `full_text` field: all pages concatenated with `[Page N]` markers for downstream processing
- `_table_to_markdown(table)` — converts Azure table result to GFM markdown table format

---

## `modules/` — Domain Logic (19+ files)

### `modules/ingestion/` (4 files)

**`orchestrator.py`**
- `IngestionOrchestrator` — coordinates the 4 ingestion stages
- Calls parser → chunker → indexer in sequence
- Emits SSE events after each stage (`ingestion.parse.completed`, etc.)
- Returns `IngestionResult` with chunk_count, page_count, language, embedding_cost, duration

**`parser.py`**
- `DocumentParser` — thin wrapper around `AzureDocIntelligenceClient`
- Single method `parse(file_path)` → returns `ParsedDocument`

**`chunker.py`**
- `DocumentChunker` — implements hybrid chunking strategy
- Step 1: Tables → each table becomes its own `Chunk` with `content_type="table"`
- Step 2: Text → split `full_text` by heading-like patterns into sections
- Step 3: Each text section → fixed-size chunks with overlap using tiktoken
- Returns `list[Chunk]` — each Chunk has chunk_id, text, section_heading, page_number, content_type, token_count
- Uses `tiktoken` cl100k_base encoder for accurate token counting

**`indexer.py`**
- `DocumentIndexer` — embeds chunks and upserts to Azure AI Search
- For each chunk: calls `AzureSKAdapter.generate_embedding(text)` → gets 3072-dim vector
- Builds search document dict with all required index fields
- Batches upserts in groups of 50
- Returns float: total embedding cost in USD

---

### `modules/template/` (6 + 7 inbuilt files)

**`models.py`**
- Defines ALL shared data models for the template system
- `SectionDefinition` — THE canonical section schema. All other template paths produce this.
- `StyleMap`, `ParagraphStyle`, `TableStyle`, `PageSetup` — style extraction models
- `DocumentSkeleton` — intermediate extraction result from custom DOCX

**`extractor.py`**
- `TemplateExtractor` — reads DOCX or XLSX template files
- DOCX: `extract_docx(path)` → `(StyleMap, DocumentSkeleton)`
  - StyleMap: walks heading styles 1–6, body style, first table style, page margins
  - DocumentSkeleton: scans body elements, keeps ONLY headings (H1-H6) and table header rows, STRIPS all body paragraphs and data rows
  - Detects "faux headings" (bold paragraphs used as headings) and flags level=None for LLM classification
- XLSX: `extract_xlsx(path)` → `(sheet_map, list[sheet_structures])`
  - Opens workbook, reads sheet names, first row as headers, column widths, header fill colors

**`classifier.py`**
- `TemplateClassifier` — ONE LLM call classifies ALL sections at once
- Loads `prompts/template/classifier.yaml` prompt template
- Takes list of `{title, level, table_headers}` dicts for all headings
- Calls GPT-5-mini via `sk_adapter.invoke_json()` with low reasoning effort
- Returns list of classification dicts: `{output_type, description, generation_hints, retrieval_query, prompt_selector, is_complex, dependencies}`
- Graceful degradation: if LLM fails, returns empty list → sections get default classifications from planner

**`planner.py`**
- `SectionPlanner` — builds final `list[SectionDefinition]` from skeleton + classifications
- Walks skeleton elements in order, matches each heading to its classification
- Assigns section_ids, execution_order (0-indexed), parent_section_id (tracks heading level hierarchy)
- Resolves dependency strings (title text) → dependency section_ids using a title→id lookup map
- The output of this file is the unified SectionPlan consumed by all downstream phases

**`preview_generator.py`**
- `PreviewGenerator` — creates user-visible preview artifacts after compilation
- DOCX: builds a skeleton `.docx` file using python-docx with the template's StyleMap applied. Each section gets a placeholder paragraph instead of real content.
- XLSX: converts Sheet1 of the uploaded workbook to an HTML table string (max 20 rows). Saved as `.html` file on disk.

**`inbuilt/registry.py`**
- Single lookup: `get_inbuilt_section_plan(doc_type)` → imports and returns the correct hardcoded list
- Single lookup: `get_inbuilt_style_map(doc_type)` → imports and returns the correct StyleMap
- Supported doc_types: PDD, SDD, UAT

**`inbuilt/pdd_sections.py`**
- Hardcoded `PDD_SECTIONS: list[SectionDefinition]` with complete section definitions
- Includes: Executive Summary, Project Scope, Stakeholder Matrix (table), Business Requirements, High-Level Architecture (diagram), Risk Register (table), Assumptions & Constraints, Success Criteria
- Each section has tuned `generation_hints`, `retrieval_query`, `prompt_selector`, `is_complex` flags

**`inbuilt/sdd_sections.py`**
- Hardcoded `SDD_SECTIONS: list[SectionDefinition]`
- Includes: System Overview, Architecture Diagram, API Specification (table), Data Models, Component Diagram, Sequence Diagrams, Security Design, Deployment Architecture, Testing Strategy

**`inbuilt/uat_sections.py`**
- Hardcoded `UAT_SECTIONS: list[SectionDefinition]` — each section = one Excel sheet
- Sections: Summary (key-value table), Test Cases (full test matrix table), Defect Log (table), Sign-Off (approval table)

**`inbuilt/styles/pdd_style.py`**
- `PDD_STYLE_MAP: StyleMap` — formal corporate blue theme
- Heading 1: large, blue, bold. Heading 2: medium, dark blue. Body: Calibri 11pt.
- Standard page margins (1" all sides)

**`inbuilt/styles/sdd_style.py`**
- `SDD_STYLE_MAP: StyleMap` — technical grey/charcoal theme
- Slightly different heading hierarchy appropriate for technical documentation

**`inbuilt/styles/uat_style.py`**
- `UAT_STYLE_MAP: StyleMap` — Excel-compatible styling
- Header fill: blue (#4472C4). Alternating row fill. Column widths defined per UAT sheet.

---

### `modules/retrieval/` (2 files)

**`retriever.py`**
- `SectionRetriever` — retrieves relevant chunks per section
- `retrieve_for_section(section, document_id, ...)` → `list[RetrievedChunk]`
- Query resolution: if `section.retrieval_query` has ≥4 words → use it directly. Else → call GPT-5-mini to generate a better query (low reasoning, 300 tokens max).
- Embeds final query with `text-embedding-3-large`
- Calls `AzureSearchClient.hybrid_search()` filtered by `document_id`
- Returns `RetrievedChunk` objects with: chunk_id, text, section_heading, page_number, content_type, score

**`packager.py`**
- `EvidencePackager` — formats retrieved chunks for LLM consumption
- `package(section_id, chunks)` → `EvidenceBundle`
- Builds `context_text`: numbered source blocks with heading path and page reference
- Builds `citations`: list of `Citation` objects (path, page, content_type, chunk_id)
- Empty chunks → returns context_text = "[No relevant content found...]"

---

### `modules/generation/` (4 files)

**`orchestrator.py`**
- `GenerationOrchestrator` — dependency-aware parallel section generation
- `run_all_sections(sections, evidence_map, doc_metadata, workflow_run_id)` → `dict[section_id, GenerationResult]`
- Algorithm: repeatedly find all sections whose dependency IDs are all in `completed_ids` set → run that wave in `asyncio.gather` → add to completed set → repeat until all done
- Deadlock detection: if no sections are ready but some remain → force-run remaining
- Routes each section to correct generator based on `output_type`

**`text_generator.py`**
- `TextGenerator` — generates prose content for `output_type="text"` sections
- Loads prompt from `prompts/generation/text/{section.prompt_selector}.yaml` (falls back to `default.yaml`)
- Builds prompt with: section title, description, generation_hints, expected_length, tone, doc_type, filename, context_text from EvidenceBundle
- Calls `sk_adapter.invoke_text()` with `task="text_generation"` (or `"complex_section"` if `section.is_complex`)
- Returns `GenerationResult` with markdown text content + citations

**`table_generator.py`**
- `TableGenerator` — generates markdown table for `output_type="table"` sections
- Key difference: prompt includes column headers instruction
- If `section.table_headers` is set (from template): prompt demands EXACTLY those columns
- If only `section.required_fields`: prompt suggests those columns
- Calls GPT-5-mini `task="table_generation"`, returns markdown table string in `GenerationResult.content`

**`diagram_generator.py`**
- `DiagramGenerator` — handles full 6-attempt self-correcting diagram generation
- Uses GPT-5 for ALL attempts (both PlantUML and Mermaid) — reasoning_effort=high
- PlantUML rendering: base64url-encode(zlib.compress(source)) → GET Kroki `/plantuml/png/{encoded}`
- Self-correction: prompt includes previous failed code + Kroki error message
- PNG saved to `storage/diagrams/{workflow_run_id}/{section_id}_{format}_a{attempt}.png`
- Returns `GenerationResult` with `diagram_source`, `diagram_format`, `diagram_png_path`
- On total failure: returns placeholder content string, workflow continues

---

### `modules/assembly/` (1 file)

**`assembler.py`**
- `DocumentAssembler` — combines section plan + generation results into `AssembledDocument`
- `assemble(workflow_run_id, template_id, doc_type, sections, generation_results, document_metadata)` → `AssembledDocument`
- Sorts sections by `execution_order`
- Skips sections missing from `generation_results`
- Serializes Citation objects to dicts for JSON storage
- Includes all metadata per section (cost, tokens, error flag)

---

### `modules/export/` (4 files)

**`renderer.py`**
- `ExportRenderer` — routes to correct builder
- If `doc_type == UAT` → `XLSXBuilder`
- If `template_source == "custom"` and template file exists → `DocxFiller`
- Otherwise → `DocxBuilder`

**`docx_builder.py`**
- `DocxBuilder` — builds fresh DOCX from scratch using StyleMap (inbuilt template path)
- Creates: title page → page break → TOC placeholder → page break → sections → Appendix
- For each section: adds heading (styled from StyleMap), then renders content:
  - text → paragraphs
  - table → markdown parsed → python-docx Table
  - diagram → embedded PNG image (Inches(5.5) wide) or placeholder text if PNG missing
- Level-1 headings get page breaks after their content block

**`docx_filler.py`**
- `DocxFiller` — fills custom DOCX template with generated content
- Opens existing template DOCX as base document
- For each AssembledSection: finds the matching heading in the template by text comparison
- Clears placeholder paragraphs after the heading
- Inserts generated content preserving template paragraph styles
- Does NOT add citations to the document

**`xlsx_builder.py`**
- `XLSXBuilder` — fills UAT XLSX workbook with generated rows
- Opens template workbook if provided, else creates default UAT workbook (4 sheets: Summary, Test Cases, Defect Log, Sign-Off)
- For each AssembledSection: finds matching sheet by name, parses markdown table from content, writes rows
- Applies header styling: blue fill, white bold font, center alignment
- Alternating row fill for readability
- Returns path to saved `.xlsx` file

---

## `prompts/` — YAML Prompt Files

All LLM prompts live here as YAML files. Format: `prompt_template: |` key with the prompt string.
Variables injected with Python `.format()` syntax: `{section_title}`, `{context}`, etc.

```
prompts/
├── template/
│   └── classifier.yaml          ← Classify all custom template sections in one call
│
└── generation/
    ├── text/
    │   ├── default.yaml          ← Fallback for any text section
    │   ├── overview.yaml         ← Executive Summary, Project Overview
    │   ├── requirements.yaml     ← Business/Functional Requirements
    │   ├── architecture.yaml     ← Architecture description (text, not diagram)
    │   ├── scope.yaml            ← Project Scope
    │   ├── assumptions.yaml      ← Assumptions & Constraints
    │   └── risks.yaml            ← Risk description
    │
    ├── table/
    │   ├── default.yaml          ← Generic table
    │   ├── stakeholders.yaml     ← Stakeholder matrix
    │   ├── traceability_matrix.yaml
    │   ├── risk_register.yaml
    │   └── api_specification.yaml
    │
    └── diagram/
        ├── default.yaml          ← PlantUML default prompt
        ├── architecture.yaml     ← System architecture diagram
        ├── sequence.yaml         ← Sequence diagram
        ├── flowchart.yaml        ← Process flowchart
        └── mermaid_default.yaml  ← Mermaid fallback (all types)
```

**Key variables available in all generation prompts:**
- `{section_title}` — heading text
- `{section_description}` — what this section should contain
- `{generation_hints}` — comma-joined key topics
- `{expected_length}` — short/medium/long
- `{tone}` — formal/technical/structured
- `{doc_type}` — PDD/SDD/UAT
- `{context}` — evidence bundle context text from retrieval
- `{correction_block}` — (diagrams only) previous failed code + error message
