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
| 3 | Services layer | Not Started | No | |
| 4 | Infrastructure adapters | Not Started | No | |
| 5 | Ingestion module | Not Started | No | |
| 6 | Template system | Not Started | No | |
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
- Status: `Completed`
- User sign-off: `Pending`
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
- [ ] `sk_adapter.py`, `search_client.py`, `doc_intelligence.py` interfaces implemented.
- [ ] No direct SDK calls outside adapter files.

### Validation (Local)
- [ ] import/interface tests pass.
- [ ] cloud integration tests marked `SKIPPED (No Azure Creds)`.

### Sign-off
- Status: `Not Started`
- User sign-off: `Pending`
- Notes:

---

## Phase 5 Checklist — Ingestion

### Completion Criteria
- [ ] parser/chunker/indexer/orchestrator implemented.
- [ ] ingest-once behavior enforced per `document_id`.
- [ ] concurrent workflows do not race (lock/guard logic).

### Validation (Local)
- [ ] chunker tests pass with sample text/table input.
- [ ] ingest-once coordinator tests pass.
- [ ] Azure indexing tests skipped (no creds).

### Sign-off
- Status: `Not Started`
- User sign-off: `Pending`
- Notes:

---

## Phase 6 Checklist — Template System

### Completion Criteria
- [ ] unified `SectionDefinition` path for inbuilt + custom.
- [ ] inbuilt registry + style maps ready.
- [ ] custom compile pipeline implemented (extract/classify/plan/preview).

### Validation (Local)
- [ ] inbuilt lookup tests pass.
- [ ] extractor/planner tests pass with local fixtures.
- [ ] classifier cloud-call tests skipped (no creds) unless mocked.

### Sign-off
- Status: `Not Started`
- User sign-off: `Pending`
- Notes:

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

