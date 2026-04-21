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
| 7 | Retrieval module | Not Started | No | |
| 8 | Generation module | Not Started | No | |
| 9 | Assembly + export | Not Started | No | |
| 10 | Workers + SSE | Not Started | No | |
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
- [ ] section retrieval query resolution implemented.
- [ ] evidence packager + citations implemented.

### Validation (Local)
- [ ] packager tests pass.
- [ ] search integration tests skipped (no creds) or mocked.

### Sign-off
- Status: `Not Started`
- User sign-off: `Pending`
- Notes:
  - Before starting Phase 8, review reusable patterns in `docs/10_QUICK_REFERENCE_AND_RULES.md`:
    - `Reusable Patterns -> Embedding Usage Accounting (Phase 5 pattern)`
    - Use `AzureSKAdapter.generate_embedding_with_usage()` for any embedding-based helpers in generation-side modules.

---

## Phase 8 Checklist — Generation

### Completion Criteria
- [ ] prompt loading and text/table/diagram generators implemented.
- [ ] diagram retry/fallback logic implemented.

### Validation (Local)
- [ ] prompt rendering tests pass.
- [ ] diagram encoding/render-request logic unit tested.
- [ ] live model tests skipped (no creds).

### Sign-off
- Status: `Not Started`
- User sign-off: `Pending`
- Notes:

---

## Phase 9 Checklist — Assembly + Export

### Completion Criteria
- [ ] assembled document structure implemented.
- [ ] docx/xlsx exporters implemented.
- [ ] citations excluded from final DOCX/XLSX output.

### Validation (Local)
- [ ] local export file generation tests pass.
- [ ] generated files open and structure matches expected.

### Sign-off
- Status: `Not Started`
- User sign-off: `Pending`
- Notes:

---

## Phase 10 Checklist — Workers + SSE

### Completion Criteria
- [ ] dispatcher background execution stable.
- [ ] SSE stream endpoint with heartbeat and terminal close behavior.

### Validation (Local)
- [ ] multi-subscriber local SSE behavior validated.
- [ ] polling fallback contract still valid.

### Sign-off
- Status: `Not Started`
- User sign-off: `Pending`
- Notes:

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

