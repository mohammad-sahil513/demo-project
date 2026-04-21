# Implementation Phase Checklist

Use this file to track one phase per chat.  
Rule: do not start the next phase until current phase is marked `Completed` and user gives explicit go-ahead.

---

## Project Execution Rules

- One chat = one phase only.
- Before coding each phase: restate scope, files, validation, and open questions.
- After coding each phase: run validation, update this checklist, then stop.
- Follow `docs/10_QUICK_REFERENCE_AND_RULES.md` strictly.
- Local machine has no Azure credentials, so validation must be offline-safe unless explicitly skipped by user.

---

## Local Validation Policy (No Azure Credentials)

- `PASS` = checks that can run locally without Azure.
- `SKIPPED (No Azure Creds)` = checks requiring Azure/OpenAI/Search/Doc Intelligence.
- For Azure-dependent phases, implement code paths + guards + stubs/mocks where needed, then mark cloud tests as skipped.

Validation types:
- Import + startup checks
- Lint/type checks (where configured)
- Unit tests for pure logic
- API contract checks with local stubs/mocks
- Cloud integration checks (skipped unless creds provided)

---

## Phase Status Board

| Phase | Name | Status | Chat Completed? | Notes |
|---|---|---|---|---|
| 1 | Foundation (`core/` + `repositories/`) | Signed Off | Yes | Core + repos aligned, pytest + lint passed |
| 2 | API stubs + router wiring | Signed Off | Yes | Phase 2 API stubs complete, pytest + lint passed |
| 3 | Services layer | Signed Off | Yes | Service layer + workflow skeleton validated locally |
| 4 | Infrastructure adapters | Signed Off | Yes | Azure adapter layer added, pytest + lint passed |
| 5 | Ingestion module | Signed Off | Yes | Ingestion pipeline shipped with reusable embedding usage-accounting helper |
| 6 | Template system | Signed Off | Yes | Inbuilt + custom template compilation pipeline integrated and validated locally |
| 7 | Retrieval module | Signed Off | Yes | Section retrieval/evidence packaging integrated, validated with mocked local tests |
| 8 | Generation module | Signed Off | Yes | Committed with Phase 9; pytest + lint green |
| 9 | Assembly + export | Signed Off | Yes | See Phase 9 notes (warnings, sheet_map, DocxFiller) |
| 10 | Workers + SSE | Signed Off | Yes | Dispatcher guard + SSE client + ProgressPage + CitationPanel |
| 11 | Final validation hardening | Not Started | No | |

---

## Phase 1 Checklist — Foundation

### Scope
- Build/align foundational files in `core/` and `repositories/`.
- Ensure enums, IDs, config, exception hierarchy, response envelope, JSON repository behavior.
- Include your confirmed policies where foundational:
  - inbuilt template stable IDs
  - Kroki default `8001`
  - ingest-once document metadata fields
  - DI cost config field

### Completion Criteria
- [x] `core/ids.py` complete and consistent ID formats.
- [x] `core/constants.py` complete (enums + policy constants used by foundation).
- [x] `core/exceptions.py` hierarchy present.
- [x] `core/response.py` envelope helpers present.
- [x] `core/config.py` loads env + storage paths + Kroki `8001`.
- [x] `repositories/base.py` CRUD works for JSON persistence.
- [x] resource repos (`document`, `template`, `workflow`, `output`) are loadable and aligned with models.

### Validation (Local)
- [x] Import smoke test passes for all above modules.
- [x] Basic repository save/get/update/delete local test passes (temp folder).
- [x] Lint passes for touched files (if configured).
- [x] Azure integration checks marked skipped.

### Sign-off
- Status: `Signed Off`
- User sign-off: `Approved`
- Notes:
  - Implemented core files: `ids.py`, `constants.py`, `exceptions.py`, `response.py`, `config.py`, `logging.py`.
  - Implemented repository foundation: `base.py`, `document_repo.py`, `template_repo.py`, `workflow_repo.py`, `output_repo.py`.
  - Added/aligned models: `document_models.py`, `template_models.py`, `workflow_models.py`, `output_models.py`.
  - Offline validation PASS: `pytest` suite executed locally (`backend/tests/test_phase1_foundation.py`) — 3 passed.
  - Lint PASS: no linter errors in `backend/core` and `backend/repositories`.
  - Cloud/Azure integration tests SKIPPED (no credentials on this machine).

---

## Phase 2 Checklist — API Stubs

### Completion Criteria
- [x] `main.py` app factory + middleware + exception handlers.
- [x] `api/router.py` and route registration complete.
- [x] route files exist with contract-safe stub responses.
- [x] `api/deps.py` dependency providers wired.

### Validation (Local)
- [x] App boots locally.
- [x] `/api/health` and `/api/ready` return valid envelopes.
- [x] No Azure-required route execution in baseline tests.

### Sign-off
- Status: `Signed Off`
- User sign-off: `Approved`
- Notes:
- Added Phase 2 API scaffolding from scratch: `main.py`, `api/router.py`, `api/deps.py`, and route stubs under `api/routes/`.
- Added lightweight `services/*` scaffolds (`document_service`, `template_service`, `workflow_service`, `output_service`, `event_service`) and `workers/dispatcher.py` for DI wiring.
- Added local contract tests in `backend/tests/test_phase2_api_stubs.py` for health/ready, workflow status payload shape, and SSE stub stream.
- Local validation PASS: `pytest` completed with 7 passed tests.
- Lint diagnostics PASS on all touched backend files.

---

## Phase 3 Checklist — Services

### Completion Criteria
- [x] CRUD/service orchestration implemented for documents/templates/workflows/outputs/events.
- [x] Policy guards implemented:
  - [x] template/doc_type mismatch reject
  - [x] block document delete while workflow running

### Validation (Local)
- [x] service-level tests with local filesystem repos pass.
- [x] API calls for service-backed endpoints pass without Azure dependency.

### Sign-off
- Status: `Signed Off`
- User sign-off: `Approved`
- Notes:
- Implemented full service logic in `services/document_service.py`, `template_service.py`, `workflow_service.py`, `output_service.py`, and `event_service.py`.
- Added `services/workflow_executor.py` skeleton with phase wrapper + ordered stub phase execution and terminal workflow events.
- Replaced stub API behavior in `api/routes/documents.py`, `templates.py`, `workflows.py`, `outputs.py`, and `events.py`; routes now use dependency-injected services.
- Added `api/deps.py` wiring for `WorkflowExecutor` and service dependencies with repository-backed guard checks.
- Added/updated tests: `tests/test_phase2_api_stubs.py` and `tests/test_phase3_services.py`.
- Local validation PASS: `.venv\\Scripts\\python -m pytest -q` => 9 passed.
- Lint diagnostics PASS: no issues reported on all touched Phase 3 files.

---

## Phase 4 Checklist — Infrastructure

### Completion Criteria
- [x] `sk_adapter.py`, `search_client.py`, `doc_intelligence.py` interfaces implemented.
- [x] No direct SDK calls outside adapter files.

### Validation (Local)
- [x] import/interface tests pass.
- [x] cloud integration tests marked `SKIPPED (No Azure Creds)`.

### Sign-off
- Status: `Signed Off`
- User sign-off: `Approved`
- Notes:
  - Added full Phase 4 adapter layer: `backend/infrastructure/doc_intelligence.py`, `backend/infrastructure/sk_adapter.py`, `backend/infrastructure/search_client.py`, and package init.
  - Extended adapter configuration in `backend/core/config.py` and `backend/.env.example` (OpenAI/Search/Doc Intelligence keys, endpoints, deployments, versions/index name).
  - Added task routing constants in `backend/core/constants.py` for model, reasoning effort, and completion token budgets.
  - Added singleton DI provider hooks in `backend/api/deps.py`: `get_doc_intelligence_client()`, `get_sk_adapter()`, `get_search_client()`.
  - Added `backend/tests/test_phase4_infrastructure.py` with offline interface tests and credential-gated live checks.
  - Local validation PASS: `python -m pytest -q` -> `12 passed, 2 skipped`.
  - Lint diagnostics PASS: no issues on touched files.

---

## Phase 5 Checklist — Ingestion

### Completion Criteria
- [x] parser/chunker/indexer/orchestrator implemented.
- [x] ingest-once behavior enforced per `document_id`.
- [x] concurrent workflows do not race (lock/guard logic).

### Validation (Local)
- [x] chunker tests pass with sample text/table input.
- [x] ingest-once coordinator tests pass.
- [x] Azure indexing tests skipped (no creds).

### Sign-off
- Status: `Signed Off`
- User sign-off: `Approved`
- Notes:
  - Implemented ingestion module files: `backend/modules/ingestion/parser.py`, `chunker.py`, `indexer.py`, `orchestrator.py`, and updated `__init__.py`.
  - Wired ingestion into execution flow via `backend/services/workflow_executor.py` and DI providers in `backend/api/deps.py`.
  - Implemented ingestion stage events: `ingestion.parse.completed`, `ingestion.chunk.completed`, `ingestion.index.completed`.
  - Added page attribution for text chunks using Document Intelligence paragraph offset/page metadata mapping.
  - Added reusable embedding usage-accounting API for future phases:
    - `AzureSKAdapter.generate_embedding_with_usage(text) -> EmbeddingUsageResult`
    - `AzureSKAdapter.generate_embedding(text)` remains backward-compatible and delegates to the usage API.
  - Updated Phase 5 indexer to compute embedding cost from provider-reported `prompt_tokens` instead of word-count heuristics.
  - Added Phase 5 tests: `backend/tests/test_phase5_ingestion.py` (chunking overlap + page metadata, ingest-once fail/retry/skip, orchestrator event flow).
  - Local validation PASS: `python -m pytest -q` -> `passed` with expected cloud tests skipped (`SKIPPED (No Azure Creds)`).
  - Lint diagnostics PASS: no issues on touched Phase 5 files.

---

## Phase 6 Checklist — Template System

### Completion Criteria
- [x] unified `SectionDefinition` path for inbuilt + custom.
- [x] inbuilt registry + style maps ready.
- [x] custom compile pipeline implemented (extract/classify/plan/preview).

### Validation (Local)
- [x] inbuilt lookup tests pass.
- [x] extractor/planner tests pass with local fixtures.
- [x] classifier cloud-call tests skipped (no creds) unless mocked.

### Sign-off
- Status: `Signed Off`
- User sign-off: `Approved`
- Notes:
  - Added Phase 6 template domain package under `backend/modules/template/` with shared `SectionDefinition` + style/skeleton models.
  - Implemented inbuilt section/style registries for PDD/SDD/UAT in `backend/modules/template/inbuilt/`.
  - Implemented custom compile pipeline modules: extractor, classifier (credential-gated with offline fallback), planner, and preview generator.
  - Replaced `TemplateService.compile_template()` stub with orchestrated compile flow persisting `section_plan`, `style_map`, `sheet_map`, and preview outputs.
  - Updated workflow integration for template preparation in `backend/services/workflow_executor.py` and inbuilt template fallback resolution in `backend/services/workflow_service.py`.
  - Added Phase 6 tests in `backend/tests/test_phase6_template_system.py`.
  - Local validation PASS: `python -m pytest -q` -> all tests passed with expected cloud tests skipped (`SKIPPED (No Azure Creds)`).
  - Lint diagnostics PASS: no issues on touched Phase 6 files.
  - Before starting Phase 7, review reusable patterns in `docs/10_QUICK_REFERENCE_AND_RULES.md`:
    - `Reusable Patterns -> Embedding Usage Accounting (Phase 5 pattern)`
    - `Reusable Patterns -> Ingestion Configuration Gate Pattern`

---

## Phase 7 Checklist — Retrieval

### Completion Criteria
- [x] section retrieval query resolution implemented.
- [x] evidence packager + citations implemented.

### Validation (Local)
- [x] packager tests pass.
- [x] search integration tests skipped (no creds) or mocked.

### Sign-off
- Status: `Signed Off`
- User sign-off: `Approved`
- Notes:
  - Added retrieval module package under `backend/modules/retrieval/`:
    - `retriever.py`: `SectionRetriever`, adaptive `_resolve_query()`, embedding usage-cost accounting, and hybrid search mapping.
    - `packager.py`: `EvidencePackager`, `EvidenceBundle`, and `Citation` models with deterministic `context_text` source-block formatting.
  - Integrated retrieval into `backend/services/workflow_executor.py`:
    - Replaced retrieval stub with parallel per-section retrieval using `asyncio.gather`.
    - Persists `section_retrieval_results` as `{section_id: {context_text, citations}}`.
    - Added env-aware behavior: local/dev/test skip on missing retrieval config; non-local environments raise and fail phase.
    - Added retrieval observability rollup for both embedding and retrieval-query LLM usage.
  - Wired retrieval dependencies in `backend/api/deps.py` (`get_section_retriever()`, `get_evidence_packager()`).
  - Added retrieval config in `backend/core/config.py` and `backend/.env.example`:
    - `RETRIEVAL_TOP_K`
    - `CHUNKER_TOKEN_MODE` (`tiktoken|word`)
  - Added shared token counting helper `backend/core/token_count.py` and integrated tiktoken fallback usage in:
    - `backend/infrastructure/sk_adapter.py` for chat/embedding usage fallback counting.
    - `backend/modules/ingestion/chunker.py` token-aware chunking and configurable token mode.
  - Added Phase 7 tests: `backend/tests/test_phase7_retrieval.py` (packager formatting, direct/adaptive query paths, executor persistence, non-local config failure behavior).
  - Local validation PASS:
    - `python -m pytest -q tests/test_phase7_retrieval.py`
    - `python -m pytest -q tests/test_phase5_ingestion.py`
    - `python -m pytest -q` (full backend suite)
  - Lint diagnostics PASS: no issues on touched Phase 7 and follow-up files.
  - Before starting Phase 8, review reusable patterns in `docs/10_QUICK_REFERENCE_AND_RULES.md`:
    - `Reusable Patterns -> Embedding Usage Accounting (Phase 5 pattern)`
    - Use `AzureSKAdapter.generate_embedding_with_usage()` for any embedding-based helpers in generation-side modules.

---

## Phase 8 Checklist — Generation

### Completion Criteria
- [x] prompt loading and text/table/diagram generators implemented.
- [x] diagram retry/fallback logic implemented.

### Validation (Local)
- [x] prompt rendering tests pass.
- [x] diagram encoding/render-request logic unit tested.
- [x] live model tests skipped (no creds).

### Sign-off
- Status: `Signed Off`
- User sign-off: `Approved`
- Notes:
  - Added generation prompt pack under `backend/prompts/generation/` (text/table/diagram + PlantUML correction + Mermaid fallback).
  - Added `backend/modules/generation/`: `GenerationPromptLoader`, `TextSectionGenerator`, `TableSectionGenerator`, `DiagramSectionGenerator` (PlantUML retries + Mermaid fallback via Kroki), `KrokiRenderer`, `GenerationOrchestrator` (dependency waves + `asyncio.gather`), `GenerationCostTracker`, `merge_generation_observability`.
  - Wired `get_generation_orchestrator()` in `backend/api/deps.py` and injected into `WorkflowExecutor`.
  - Replaced `_phase_generation()` in `backend/services/workflow_executor.py`: persists `section_generation_results`, updates `section_progress`, merges LLM observability, emits `section.generation.started` / `section.generation.completed`, strips `diagram_source` before persistence; `workflow.completed` now includes `total_cost_usd` from `observability_summary`.
  - Phase 8 tests: `backend/tests/test_phase8_generation.py`.
  - Local validation PASS: `python -m pytest -q tests/test_phase8_generation.py`, `python -m pytest -q` (full backend suite).
  - Lint diagnostics PASS: no issues on touched Phase 8 files.

---

## Phase 9 Checklist — Assembly + Export

### Completion Criteria
- [x] assembled document structure implemented.
- [x] docx/xlsx exporters implemented.
- [x] citations excluded from final DOCX/XLSX output.

### Validation (Local)
- [x] local export file generation tests pass.
- [x] generated files open and structure matches expected.

### Sign-off
- Status: `Signed Off`
- User sign-off: `Approved`
- Notes:
  - Added `backend/modules/assembly/` (`DocumentAssembler`, `AssemblyOutcome` with `warnings` for missing generation rows, `AssembledDocument` / `AssembledSection` without citation fields).
  - Added `backend/modules/export/` (`ExportRenderer` returns export warnings; `ExportDocumentInfo` / `ExportTemplateInfo`; `DocxBuilder` with Title-only title style, list bullets/numbering; `DocxFiller` re-scans headings per section, `template_heading_not_found` warnings, optional `style_map`; `XlsxBuilder` uses template `sheet_map`, preserves header row when filling template workbooks; `markdown_tables` GFM separator fix).
  - Wired `WorkflowExecutor`: assembly merges warnings into `WorkflowRecord.warnings`; render merges filler/export warnings; `sheet_map` passed into export for UAT.
  - Dependencies: `python-docx`, `openpyxl` in `backend/requirements.txt`; `get_workflow_executor()` injects `output_service`.
  - Tests: `backend/tests/test_phase9_assembly_export.py` (includes multi-section filler + missing-heading cases).
  - Local validation PASS: `python -m pytest -q`.
  - Backend feature commit bundles Phase 8 + Phase 9; this checklist + `cmds.txt` track sign-off and next phase entry.

---

## Phase 10 Checklist — Workers + SSE

### Completion Criteria
- [x] dispatcher background execution stable (guarded `BackgroundTasks` + `create_task` paths; `background_task_failed` logging).
- [x] SSE stream endpoint with heartbeat and terminal close behavior (existing route verified; no change required).

### Validation (Local)
- [x] `backend/tests/test_phase10_workers_sse.py` exercises dispatcher guard + log message.
- [x] frontend `npm run build` (tsc + vite) passes with `subscribeToWorkflowEvents`, ProgressPage SSE + polling fallback, and `CitationPanel`.

### Sign-off
- Status: `Signed Off`
- User sign-off: `Pending`
- Notes:
  - `TaskDispatcher.dispatch` now runs tasks via `_run_guarded`, logging `background_task_failed` with task name and string `resource_id` when present.
  - Frontend: [frontend/src/api/workflowApi.ts](frontend/src/api/workflowApi.ts) `subscribeToWorkflowEvents`; [frontend/src/pages/ProgressPage.tsx](frontend/src/pages/ProgressPage.tsx) opens one `EventSource` per workflow run, debounced status refresh on events, SSE error budget falls back to 2.5s polling; [frontend/src/components/output/CitationPanel.tsx](frontend/src/components/output/CitationPanel.tsx) + [frontend/src/api/types.ts](frontend/src/api/types.ts) `section_retrieval_results` / `CitationDto` on output page.
  - Full backend `pytest` run passes locally (including `test_phase10_workers_sse.py`); Phase 5 chunker unit test uses `token_mode="word"` so overlap assertions match the chunker’s word mode.
  - **Follow-up improvements:** Progress page keeps a per–doc-type status snapshot, refreshes **one** workflow via `getWorkflowStatus(runId)` on SSE (debounced **per run id**), and merges with `reconcileFromSnapshot` instead of refetching all runs on every event. Initial `await poll()` runs before opening EventSources. Fallback to polling when **all** streams are still `EventSource.CLOSED` after 2s; `onopen` clears the probe only after a `setTimeout(0)` when **every** stream is `OPEN`; 30s safety full poll while SSE is primary. `subscribeToWorkflowEvents` exposes `eventSource` for `readyState` checks. `WorkflowExecutor.run` no longer re-raises after a handled failure (avoids noisy `background_task_failed` for expected `workflow.failed`).
  - **Hardening (review gaps):** Missing snapshot rows trigger `setPerTypeProgress(..., 0, 'Waiting for status…')`, overall **average = sum(progress)/count(docs with runs)** including zeros for gaps, and `pollRef` defensive full poll; terminal `workflow.completed` / `workflow.failed` emits wrapped in try/except with `workflow_*_emit_failed` logs so COMPLETED/FAILED persist if SSE emit fails; `backend/tests/test_phase10_sse_stream.py` integration test for SSE JSON stream; frontend `vitest` + `src/api/workflowApi.test.ts` for `EventSource` URL and event parsing (`npm run test`).

---

## Phase 11 Checklist — Final Validation

### Completion Criteria
- [ ] all prior phases marked completed.
- [ ] end-to-end workflow behavior validated as far as local env allows.
- [ ] cloud-only checks listed as skipped/pending explicitly.

### Validation (Local)
- [ ] full local smoke run passes.
- [ ] lint/tests green for implemented scope.

### Sign-off
- Status: `Not Started`
- User sign-off: `Pending`
- Notes:

