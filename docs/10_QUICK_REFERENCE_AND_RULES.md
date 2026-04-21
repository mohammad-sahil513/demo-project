# 10 — Quick Reference, Naming Conventions & Rules

> Keep this open while writing code. These rules apply to every single file.

---

## Layer Import Rules (ENFORCED — Never Break These)

```
core/          ← imports nothing from backend (only stdlib, pydantic)
infrastructure/ ← imports from core/ only
repositories/  ← imports from core/ only
modules/       ← imports from core/, infrastructure/, modules/
               ← NEVER imports from services/ or api/
services/      ← imports from core/, repositories/, modules/, infrastructure/
               ← NEVER imports from api/
api/           ← imports from core/, services/ ONLY
               ← NEVER imports directly from modules/, repositories/, infrastructure/
workers/       ← imports from core/ only
```

**Why this matters:** If a route file imports a repository directly, that bypasses service logic. If a module imports a service, that creates circular dependencies. The layer boundaries are what keep the code testable and maintainable.

---

## Naming Conventions

### Files
- All Python files: `snake_case.py`
- All YAML prompt files: `snake_case.yaml`

### Classes
- All classes: `PascalCase`
- Examples: `WorkflowExecutor`, `DocumentChunker`, `AzureSKAdapter`

### Functions and Methods
- All functions: `snake_case()`
- Private methods: `_leading_underscore()`
- Async functions: same naming, just add `async def` prefix

### Constants
- Module-level constants: `UPPER_SNAKE_CASE`
- Examples: `PHASE_WEIGHTS`, `MODEL_PRICING`, `TASK_TO_MODEL`

### IDs
- Always prefixed: `"wf-{12hex}"`, `"doc-{12hex}"`, `"tpl-{12hex}"`, `"out-{12hex}"`, `"sec-{12hex}"`
- Never use raw UUIDs without prefix
- ID field names: `workflow_run_id`, `document_id`, `template_id`, `output_id`, `section_id`, `chunk_id`

### Enum Values
- All enum values are UPPER_SNAKE strings: `"RUNNING"`, `"GENERATION"`, `"COMPLETED"`
- Import from `core/constants.py` — never hardcode status strings

### Route Paths
- Use plural nouns: `/documents`, `/templates`, `/workflow-runs`, `/outputs`
- Use kebab-case for multi-word segments: `/workflow-runs`, `/compile-status`, `/preview-html`

---

## Async Rules

- All route handlers: `async def`
- All service methods that call async modules: `async def`
- All module orchestrators: `async def`
- All infrastructure adapter calls: `async def`
- Use `asyncio.gather()` for parallel operations, never sequential loops for parallel work
- Never use `time.sleep()` — use `await asyncio.sleep()`
- Never use sync blocking IO in async context (file reads are fine; network calls must be async)

---

## File and Path Rules

- Always use `pathlib.Path` — never string concatenation for file paths
- Never hardcode `/` or `\` in path construction
- All storage paths computed from `settings.storage_root` via property methods
- Binary files saved with `.bin` extension (avoids content-type confusion)
- JSON metadata files: same name as resource ID + `.json`

---

## Error Handling Rules

- Raise `NotFoundException` when a resource doesn't exist by ID
- Raise `ValidationException` for invalid input
- Use domain-specific exceptions (IngestionException, TemplateException, etc.) for clarity
- Never raise generic `Exception` with a descriptive message — use the hierarchy
- Background tasks: wrap in try/catch, log error, never let crash propagate silently
- Phase failures: caught by `_run_phase()` wrapper, auto-retried once, then propagates as `WorkflowPhaseError`

---

## Response Rules

- Every route returns one of: `success_response()`, `created_response()`, `error_response()`
- Never return raw dicts from routes
- File downloads: use `FileResponse` directly (not JSON envelope)
- SSE: use `StreamingResponse` with `text/event-stream` media type

---

## Azure SDK Rules

- **Never call Azure OpenAI SDK directly** outside `sk_adapter.py`
- **Never call Azure Search SDK directly** outside `search_client.py`
- **Never call Azure Doc Intelligence SDK directly** outside `doc_intelligence.py`
- All Azure clients: use async context manager pattern (`async with client as c:`)
- All API keys: only read from `settings` object, never hardcoded

---

## LLM Call Rules

- **Always use `sk_adapter.invoke_text()` or `invoke_json()`** — never call Semantic Kernel directly
- **Always specify `task`** parameter — this determines model + reasoning effort + token budget
- **Always pass `cost_tracker`** when available — needed for observability
- GPT-5 policy (enforced in sk_adapter): `max_completion_tokens` + `reasoning_effort` in `extra_body`; NO `temperature`, NO `max_tokens`
- JSON responses: use `invoke_json()`, not `invoke_text()` + manual parsing
- Prompt variables: use `.format()` substitution — all variables in `{curly_braces}`

---

## Observability Rules

- Every LLM call must be tracked by passing `cost_tracker` to `invoke_text()`/`invoke_json()`
- `ObservabilityCostTracker` is created once per workflow run and passed through the call chain
- Never create multiple cost trackers for one workflow
- Observability JSONL is append-only — never overwrite
- Summary is only computed and saved at workflow completion

---

## Reusable Patterns (Use In Future Phases)

### Embedding Usage Accounting (Phase 5 pattern)

- **Preferred API:** `AzureSKAdapter.generate_embedding_with_usage(text)` returns:
  - `embedding: list[float]`
  - `prompt_tokens: int` (provider-reported usage)
- **Compatibility API:** `AzureSKAdapter.generate_embedding(text)` still returns only `list[float]` for legacy callsites.
- **Cost rule:** For embedding-cost math, always use `prompt_tokens` from usage; do not use heuristic token counts (`split()`, char length, etc.).
- **Where to apply next:** Retrieval, reranking, and any module that calls embeddings in phases 7+.
- **Testing rule:** In unit tests, fake adapters should expose both methods and return deterministic `prompt_tokens` so cost assertions are stable.

### Ingestion Configuration Gate Pattern

- Add/keep `is_configured()` on orchestration dependencies (parser/indexer/orchestrator).
- In executor phases, prefer dependency-level readiness checks over direct env-field checks.
- Use skip labels/messages for local no-credential runs; do not crash the workflow in offline mode.

---

## SSE Rules

- Emit events using `await self._event_service.emit(workflow_run_id, event_type, payload)`
- Always emit both `phase.started` and `phase.completed` (or `phase.failed`) per phase
- Section events: emit `section.generation.started` BEFORE calling LLM, `section.generation.completed` AFTER
- Terminal events that close the stream: `workflow.completed` and `workflow.failed` only
- Heartbeat is handled by the SSE route generator — no need to emit from executor

---

## Citation Rules

- Citations flow from retriever → packager → generator → assembler unchanged
- Never modify or filter citations in any intermediate step
- Citations are NEVER written to DOCX or XLSX output — UI only
- Citation format: `{path}, p.{page} [{content_type}]`
- If `page` is None: display as `p.?`
- If `section_heading` is None: display path as `"Document"`

---

## Template Rules

- Inbuilt templates: defined entirely in Python, shipped with the app, no file upload needed
- Custom templates: compiled on upload, compilation result stored in TemplateRecord JSON
- Both paths produce IDENTICAL `list[SectionDefinition]` — downstream code knows nothing about the source
- Template compilation is a background task — never make the user wait for it synchronously
- `section.table_headers` overrides `section.required_fields` when generating table content

---

## Storage Rules

- Binary files: `storage/{resource_type}/{resource_id}.bin`
- JSON metadata: `storage/{resource_type}/{resource_id}.json`
- Generated outputs: `storage/outputs/{workflow_run_id}.docx` or `.xlsx`
- Diagram PNGs: `storage/diagrams/{workflow_run_id}/{section_id}_{format}_a{attempt}.png`
- Log files: `storage/logs/{workflow_run_id}.log`
- Observability: `storage/logs/{workflow_run_id}_observability.jsonl`
- All storage paths: created at startup by `ensure_storage_dirs()`

---

## Common Mistakes to Avoid

| Mistake | Correct Approach |
|---------|-----------------|
| `import json` then `json.loads()` | Use `orjson.loads()` for consistency |
| Hardcoded status strings like `"running"` | Use `WorkflowStatus.RUNNING.value` |
| Direct `open("storage/doc.json")` with strings | Use `settings.documents_path / f"{id}.json"` |
| `asyncio.sleep(0)` to yield | Let `asyncio.gather()` handle parallelism |
| Calling `sk_adapter` from a route handler | Route → service → module → sk_adapter |
| Creating new Azure clients per request | Use the adapter classes; they manage client creation |
| Printing to stdout for debugging | Use `logger = get_logger(__name__)` |
| Returning partial workflow state on error | Always save what you have; mark FAILED cleanly |
| Catching all exceptions silently | Catch specific exceptions, log with traceback |
| Embedding PNGs by path into DOCX without checking file exists | Check `Path.exists()` first |

---

## Key File Locations Quick Reference

```
Config & settings:   core/config.py → settings singleton
All enums:           core/constants.py
Exception hierarchy: core/exceptions.py
Response envelope:   core/response.py → success_response()
ID generation:       core/ids.py
Logging setup:       core/logging.py → get_logger(__name__)

All LLM calls:       infrastructure/sk_adapter.py → sk_adapter.invoke_text()
All search calls:    infrastructure/search_client.py → search_client.hybrid_search()
All doc parse calls: infrastructure/doc_intelligence.py → analyze_document()

Section schema:      modules/template/models.py → SectionDefinition
Inbuilt sections:    modules/template/inbuilt/registry.py → get_inbuilt_section_plan()
Custom compile:      services/template_service.py → compile_template()

Main pipeline:       services/workflow_executor.py → WorkflowExecutor.run()
Cost tracking:       services/workflow_executor.py → ObservabilityCostTracker
SSE broadcast:       services/event_service.py → emit()

Background tasks:    workers/dispatcher.py → TaskDispatcher.dispatch()
```

---

## Workflow State Quick Reference

```
WorkflowRecord.status:
  PENDING    → created, not started
  RUNNING    → pipeline executing
  COMPLETED  → all 8 phases done, output ready
  FAILED     → unrecoverable error, partial results saved

WorkflowRecord.current_phase (updated at start of each phase):
  INPUT_PREPARATION → INGESTION → TEMPLATE_PREPARATION → SECTION_PLANNING
  → RETRIEVAL → GENERATION → ASSEMBLY_VALIDATION → RENDER_EXPORT

TemplateRecord.status:
  PENDING    → just created (transitional, almost never seen)
  COMPILING  → background compilation in progress
  READY      → compiled successfully, section_plan available
  FAILED     → compilation error, compile_error has the message

DocumentRecord.status:
  UPLOADED   → file saved, not yet parsed
  READY      → available for use in workflows
  FAILED     → (reserved for future parse-on-upload scenario)
```
