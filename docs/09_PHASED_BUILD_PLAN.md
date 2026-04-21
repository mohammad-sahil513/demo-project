# 09 — Phased Build Plan

> Step-by-step construction plan for the entire backend.
> Each phase is independently testable before moving to the next.
> Follow this order exactly — dependencies are strict.

---

## Build Order Rationale

```
Phase 1: Foundation    → core/ + repos/ + main.py    ← everything depends on this
Phase 2: API stubs     → api/ with stub responses     ← frontend connects immediately
Phase 3: Services      → real service logic           ← routes become functional
Phase 4: Infrastructure → Azure SDK adapters          ← real Azure connectivity
Phase 5: Ingestion     → parse + chunk + index        ← BRD becomes searchable
Phase 6: Templates     → inbuilt + custom compile     ← section plans available
Phase 7: Retrieval     → hybrid search per section    ← evidence bundles ready
Phase 8: Generation    → text + table + diagram       ← AI content created
Phase 9: Assembly + Export → merge + DOCX/XLSX build  ← files downloadable
Phase 10: Workers + SSE → background dispatch + events ← real-time UX complete
Phase 11: Validation   → end-to-end test checklist    ← production ready
```

---

## Phase 1 — Foundation (core/ + repositories/)

**Goal:** Create the shared foundation and data persistence layer. Nothing Azure-dependent.

### Step 1.1 — `core/` (6 files)

Write in this order — each file depends on the previous:

1. **`core/ids.py`** — ID generation + `utc_now()`
   - No dependencies. Write first.
   - Test: `from core.ids import workflow_id; print(workflow_id())` → should print `"wf-{12hex}"`

2. **`core/constants.py`** — All enums + PHASE_WEIGHTS + LLM routing tables
   - No dependencies. Pure Python enums.
   - Test: `from core.constants import WorkflowStatus; assert WorkflowStatus.RUNNING == "RUNNING"`

3. **`core/exceptions.py`** — Exception hierarchy
   - No dependencies.
   - Test: instantiate each exception, verify `code` and `message` attributes

4. **`core/response.py`** — Response envelope builders
   - Depends on: nothing yet (FastAPI JSONResponse import)
   - Test: `success_response({"key": "val"}).status_code == 200`

5. **`core/logging.py`** — Structlog setup
   - Depends on: `core/config.py` (for `app_debug` flag) — write config first

6. **`core/config.py`** — Settings singleton
   - Depends on: nothing backend
   - Create `.env` file from `.env.example` before testing
   - Test: `from core.config import settings; print(settings.api_prefix)` → `/api`
   - Also verify: `ensure_storage_dirs()` creates storage subdirectories

### Step 1.2 — `repositories/` (5 files)

1. **`repositories/base.py`** — Generic JSON repo
   - Depends on: `core/ids.py`, `core/exceptions.py`
   - Test: create a simple Pydantic model, save/get/update/delete round-trip

2. **`repositories/document_repo.py`** — DocumentRecord + DocumentRepository
3. **`repositories/template_repo.py`** — TemplateRecord + TemplateRepository
4. **`repositories/workflow_repo.py`** — WorkflowRecord + WorkflowRepository (most complex)
5. **`repositories/output_repo.py`** — OutputRecord + OutputRepository

For steps 2–5: create each repo, instantiate with a temp directory, do a save/get/list/delete cycle.

**Phase 1 complete when:** All 6 core files + 5 repo files work with unit tests. No Azure calls. No HTTP.

---

## Phase 2 — API Stubs

**Goal:** Get the frontend connecting to the backend with correct routes. All routes return stub responses.

### Step 2.1 — `main.py`

- Import core layer, set up FastAPI app with lifespan, CORS, exception handlers
- Mount `api_router` (even if it's empty)
- Run: `uvicorn backend.main:app --reload`
- Visit `http://localhost:8000/api/docs` → should see Swagger UI

### Step 2.2 — `api/router.py`

- Create central router with include_router calls for all 6 sub-routers
- All sub-router files can be stubs initially

### Step 2.3 — `api/routes/health.py`

- Both health endpoints working with real config data
- Test: `GET /api/health` → `{success: true, data: {status: "ok"}}`

### Step 2.4 — `api/routes/` stub files (5 remaining route files)

For each route file, implement the endpoints returning hardcoded stub data:
- `documents.py`: all endpoints with `{"items": [], "total": 0}` responses
- `templates.py`: same stub pattern
- `workflows.py`: `/workflow-runs` returns empty list; `/status` returns stub status
- `outputs.py`: 404 for everything (no outputs yet)
- `events.py`: SSE endpoint that sends one test event then closes

### Step 2.5 — `api/deps.py`

- Add all dependency providers
- Singletons: `EventService` and `TaskDispatcher` at module level
- All `get_*_service()` functions instantiate with appropriate repos

**Phase 2 complete when:** Frontend can connect to backend, all pages load without 404/500 errors. Upload page, template selection, and workflow list all show (empty) state.

---

## Phase 3 — Services

**Goal:** Real service logic in place. Routes become functional.

### Step 3.1 — `services/document_service.py`

- Implement `save_document()`, `get_or_raise()`, `list_all()`, `delete()`, `get_file_path()`
- Update `api/routes/documents.py` to use real service instead of stubs
- Test: Upload a PDF → verify file appears in `storage/documents/` → list shows it → delete it

### Step 3.2 — `services/template_service.py`

- Implement `save_template()` — save file + create COMPILING record
- `compile_template()` — leave as a stub that just sets status READY immediately (full compile in Phase 6)
- `get_or_raise()`, `list_all()`, `delete()`, `get_file_path()`, `get_preview_html()`
- Update `api/routes/templates.py` to use real service
- Test: Upload a DOCX template → status goes COMPILING → (stub) goes READY immediately

### Step 3.3 — `services/workflow_service.py`

- Implement `create()`, `get()`, `get_or_raise()`, `update()`, `list_all()`
- Add `get_document()` and `get_template()` helpers
- Update `api/routes/workflows.py` to use real service
- Test: Create a workflow record → check JSON file in storage → update status field

### Step 3.4 — `services/output_service.py`

- Implement `create()`, `get_or_raise()`, `get_download_info()`
- Update `api/routes/outputs.py`

### Step 3.5 — `services/event_service.py`

- Implement subscribe/unsubscribe/emit
- Test: Connect two SSE clients simultaneously, emit an event, both receive it

### Step 3.6 — `services/workflow_executor.py` (SKELETON)

- Write the class with all 8 `_phase_*` methods as stubs (just update `current_step_label`)
- The `_run_phase()` wrapper should be fully implemented
- `run()` method should call all 8 stubs in order and mark COMPLETED
- Wire `TaskDispatcher` and `WorkflowExecutor` into deps.py
- Test: Create workflow + start → poll status → should go COMPLETED (all stub phases)

**Phase 3 complete when:** Full CRUD works for documents, templates, workflows. Workflow runs (with stubs) and reaches COMPLETED state. SSE events stream correctly.

---

## Phase 4 — Infrastructure (Azure Adapters)

**Goal:** Real Azure connectivity. Test each adapter independently.

### Step 4.1 — `infrastructure/doc_intelligence.py`

- Implement `AzureDocIntelligenceClient.analyze_document()`
- Implement markdown table converter `_table_to_markdown()`
- **Requires:** `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` and `KEY` in `.env`
- Test: Pass a sample PDF → print page count, first 500 chars of full_text, table count

### Step 4.2 — `infrastructure/sk_adapter.py`

- Implement `AzureSKAdapter` with both kernel instances
- Implement `invoke_text()`, `invoke_json()`, `generate_embedding()`
- **Requires:** All `AZURE_OPENAI_*` env vars
- Test:
  - `invoke_text("Say hello", task="text_generation")` → content should be a greeting
  - `generate_embedding("test")` → should return list of 3072 floats
  - `invoke_json('Return {"key": "value"}', task="text_generation")` → should return parsed dict

### Step 4.3 — `infrastructure/search_client.py`

- Implement `AzureSearchClient.upsert_chunks()`, `hybrid_search()`, `delete_by_document()`
- **Requires:** `AZURE_SEARCH_*` env vars AND search index must already exist
- **Index creation:** Create the index schema (see Tech Stack doc) via Azure portal before testing
- Test:
  - Generate a fake embedding (list of 3072 zeros), upsert one chunk
  - Search for "test" → verify result returns
  - Delete the chunk

**Phase 4 complete when:** All 3 Azure adapters independently verified with real Azure calls.

---

## Phase 5 — Ingestion Module

**Goal:** BRD upload → chunks in Azure AI Search.

### Step 5.1 — `modules/ingestion/parser.py`

- Simple wrapper around `AzureDocIntelligenceClient`
- Test: Pass a real PDF → get ParsedDocument

### Step 5.2 — `modules/ingestion/chunker.py`

- Implement `DocumentChunker` with heading-split + fixed-size sliding window
- Test with a text string: verify chunks are correct size, overlap is working, tables get their own chunk

### Step 5.3 — `modules/ingestion/indexer.py`

- Implement `DocumentIndexer` — embed + batch upsert
- Test: Index a small set of fake chunks → verify they appear in Azure Search

### Step 5.4 — `modules/ingestion/orchestrator.py`

- Wire together parser → chunker → indexer
- Implement SSE event emission after each stage
- Wire into `WorkflowExecutor._phase_ingestion()` — replace stub

**Phase 5 complete test:**
1. Upload a PDF via API
2. Create a workflow run → start it
3. Watch logs: should see parse → chunk → index steps
4. SSE stream: should receive `ingestion.parse.completed`, `ingestion.chunk.completed`, `ingestion.index.completed`
5. Query Azure AI Search directly → should see chunks with `document_id` matching the document

---

## Phase 6 — Template System

**Goal:** Both inbuilt and custom templates produce a valid SectionPlan.

### Step 6.1 — `modules/template/models.py`

- Define all shared models: `SectionDefinition`, `StyleMap`, `ParagraphStyle`, `TableStyle`, `PageSetup`, `DocumentSkeleton`
- No logic — just Pydantic model definitions

### Step 6.2 — `modules/template/inbuilt/` (all files)

- Write `pdd_sections.py`, `sdd_sections.py`, `uat_sections.py` with complete SectionDefinition lists
- Write `styles/pdd_style.py`, `sdd_style.py`, `uat_style.py` with StyleMap definitions
- Write `registry.py` with lookup functions
- Test: `get_inbuilt_section_plan("PDD")` → list of SectionDefinition objects with all required fields

### Step 6.3 — `modules/template/extractor.py`

- Implement `extract_docx()` — StyleMap + DocumentSkeleton extraction
- Implement `extract_xlsx()` — SheetMap + sheet structures
- Test: Open a real custom template DOCX → verify headings are extracted, body stripped, tables have headers

### Step 6.4 — `modules/template/classifier.py` + prompt file

- Create `prompts/template/classifier.yaml` with full prompt
- Implement `TemplateClassifier.classify_sections()`
- Test: Pass a list of 5 headings → get back 5 classified section dicts

### Step 6.5 — `modules/template/planner.py`

- Implement `SectionPlanner.build_from_skeleton_and_classifications()`
- Test: Pass skeleton + classifications → get ordered SectionDefinition list with correct parent hierarchy

### Step 6.6 — `modules/template/preview_generator.py`

- Implement `build_preview_docx()` — skeleton DOCX with placeholders
- Implement `build_preview_html_from_xlsx()` — HTML table string
- Test: Generate preview from sample data → verify DOCX file opens correctly

### Step 6.7 — Update `TemplateService.compile_template()`

- Replace the stub with full compile pipeline: extractor → classifier → planner → preview_generator
- Wire `_phase_template_preparation()` in WorkflowExecutor to use registry + template record

**Phase 6 complete test:**
1. Upload a custom DOCX template with 5 sections
2. Wait for COMPILING → READY
3. Hit `/compile-status` → `section_count: 5`
4. Download preview → open in Word → should see skeleton with placeholder text
5. Create PDD workflow with inbuilt template → phase 3 should succeed with 8 sections in section_plan

---

## Phase 7 — Retrieval Module

**Goal:** Every section gets an EvidenceBundle with context text and citations.

### Step 7.1 — `modules/retrieval/retriever.py`

- Implement `SectionRetriever.retrieve_for_section()`
- Implement `_resolve_query()` — adaptive query logic
- Test: Create a fake SectionDefinition → retrieve for a document that has been ingested → verify chunks returned

### Step 7.2 — `modules/retrieval/packager.py`

- Implement `EvidencePackager.package()`
- Test: Pass list of RetrievedChunks → verify context_text format and Citation objects

### Step 7.3 — Wire into WorkflowExecutor

- Replace `_phase_retrieval()` stub with real implementation
- All sections retrieved in parallel with `asyncio.gather`

**Phase 7 complete test:**
1. Run a workflow through phases 1–5 (ingestion)
2. Continue to phase 5 (retrieval)
3. Check `WorkflowRecord.section_retrieval_results` → should have EvidenceBundle data per section_id
4. Verify citations have path/page/content_type fields

---

## Phase 8 — Generation Module

**Goal:** AI generates content for every section.

### Step 8.1 — Create all prompt YAML files

Create these files BEFORE implementing generators (generators load them on init):

```
prompts/generation/text/default.yaml
prompts/generation/text/overview.yaml
prompts/generation/text/requirements.yaml
prompts/generation/text/architecture.yaml
prompts/generation/text/scope.yaml
prompts/generation/text/assumptions.yaml
prompts/generation/text/risks.yaml
prompts/generation/table/default.yaml
prompts/generation/table/stakeholders.yaml
prompts/generation/table/traceability_matrix.yaml
prompts/generation/table/risk_register.yaml
prompts/generation/table/api_specification.yaml
prompts/generation/diagram/default.yaml        ← PlantUML
prompts/generation/diagram/mermaid_default.yaml ← Mermaid fallback
prompts/generation/diagram/architecture.yaml
prompts/generation/diagram/sequence.yaml
prompts/generation/diagram/flowchart.yaml
```

### Step 8.2 — `modules/generation/orchestrator.py`

- Implement `GenerationOrchestrator.run_all_sections()` with wave-based parallel execution
- Route to correct generator based on `output_type`
- Emit section SSE events

### Step 8.3 — `modules/generation/text_generator.py`

- Load YAML prompt, build prompt string, call `sk_adapter.invoke_text()`
- Test: Generate one text section with real evidence → should get markdown prose

### Step 8.4 — `modules/generation/table_generator.py`

- Same pattern, include table headers instruction in prompt
- Test: Generate stakeholder matrix → should get GFM markdown table with correct columns

### Step 8.5 — `modules/generation/diagram_generator.py`

- Start Kroki Docker: `docker run -d -p 8000:8000 yuzutech/kroki`
- Implement full 6-attempt loop with self-correction
- Test: Generate architecture diagram → should get PNG file in `storage/diagrams/`
- Test failure path: use bad PlantUML → verify Mermaid fallback triggers

### Step 8.6 — Wire into WorkflowExecutor

- Replace `_phase_generation()` stub with real implementation

**Phase 8 complete test:**
1. Run workflow through all phases 1–7
2. Watch generation phase — should see `section.generation.started` + `section.generation.completed` SSE events per section
3. After GENERATION phase: check `WorkflowRecord.section_generation_results` — all sections should have content
4. Diagram sections: verify PNG files exist in `storage/diagrams/`

---

## Phase 9 — Assembly + Export

**Goal:** Workflow produces a downloadable DOCX or XLSX file.

### Step 9.1 — `modules/assembly/assembler.py`

- Implement `DocumentAssembler.assemble()`
- Test: Pass 5 GenerationResults → get back ordered AssembledDocument

### Step 9.2 — `modules/export/renderer.py`

- Routing logic only — delegate to builders

### Step 9.3 — `modules/export/docx_builder.py`

- Build fresh DOCX from StyleMap + AssembledDocument
- Test: Build a DOCX from test data → open in Word → verify headings, tables, layout

### Step 9.4 — `modules/export/docx_filler.py`

- Fill custom template DOCX
- Test: Use a real custom template, fill with generated content → verify template styles preserved

### Step 9.5 — `modules/export/xlsx_builder.py`

- Fill UAT workbook
- Test: Build UAT XLSX → open in Excel → verify sheets, headers, data rows

### Step 9.6 — Wire into WorkflowExecutor

- Replace `_phase_assembly()` and `_phase_render_export()` stubs with real implementations
- Create OutputRecord and update WorkflowRecord.output_id

**Phase 9 complete test:**
1. Full PDD workflow → `GET /api/outputs/{id}/download` → valid DOCX opens in Word
2. Full UAT workflow → `GET /api/outputs/{id}/download` → valid XLSX opens in Excel
3. Custom template workflow → verify template styling preserved in output

---

## Phase 10 — Workers + SSE Finalization

**Goal:** Background dispatch and real-time events working end-to-end.

### Step 10.1 — `workers/dispatcher.py`

- Implement `TaskDispatcher` with BackgroundTasks + asyncio fallback
- Verify no tasks are being lost (check logs for `background_task_failed`)

### Step 10.2 — SSE Final Testing

- Connect EventSource in browser devtools → run workflow → verify all events stream correctly
- Test with multiple browser tabs open simultaneously
- Verify heartbeat `: heartbeat` lines appear every 30s
- Verify stream closes after `workflow.completed`

### Step 10.3 — Frontend SSE Update

- Add `subscribeToWorkflowEvents()` function to `workflowApi.ts`
- Update ProgressPage to use SSE with polling fallback
- Add `CitationPanel` component to output/preview page

---

## Phase 11 — Final Validation Checklist

Run ALL of these before considering the backend production-ready:

### Health & Config
```
□ GET /api/health → 200 {status: "ok"}
□ GET /api/ready → 200 with all azure_*_configured: true
□ .env has all required values and no placeholder strings
□ Kroki Docker container running: curl localhost:8000/health → {"status":"pass"}
□ Azure AI Search index exists with correct schema
```

### Document Operations
```
□ Upload PDF → document_id returned, file exists in storage/documents/
□ Upload DOCX → same
□ Upload PNG → rejected with 400 (wrong type)
□ List documents → returns uploaded docs
□ Delete document → file removed from disk AND metadata gone
```

### Template Operations
```
□ Upload PDD DOCX → status COMPILING → poll → READY
□ Upload SDD DOCX → same
□ Upload UAT XLSX → same → /preview-html returns HTML table
□ compile-status shows correct section_count after compile
□ /download returns binary file
□ Inbuilt PDD template returns 8 sections from registry
□ Inbuilt UAT template returns 4 sections
```

### Workflow Operations
```
□ POST /workflow-runs → 201 with workflow_run_id
□ Workflow starts running (status changes from PENDING to RUNNING)
□ SSE events stream while running
□ /status shows incrementing progress_percent
□ All 8 phase SSE events received
□ section.generation.started events received per section
□ Workflow reaches COMPLETED
□ /observability returns cost breakdown
```

### Output Validation
```
□ PDD output: valid DOCX, opens in Word, correct sections
□ SDD output: valid DOCX, contains embedded diagram PNG
□ UAT output: valid XLSX, 4 sheets with data
□ Custom template PDD: template styles preserved in output
□ Custom template UAT: custom sheet headers used in output
□ DOCX contains ZERO citation markup (clean document)
```

### Frontend Compatibility
```
□ Frontend progress page: SSE events update UI in real-time
□ Frontend output page: sections rendered with citation panel visible
□ Citation panel expands/collapses correctly
□ Download button works and browser downloads correct file type
□ Template preview: DOCX preview renders via docx-preview
□ UAT template: HTML table shows instead of docx-preview
□ Polling fallback: disconnect SSE, polling takes over, still reaches COMPLETED
```

### Error & Edge Cases
```
□ Non-existent workflow_run_id → 404
□ Non-existent template_id → 404
□ Workflow with uncompiled template → error captured, not server crash
□ Kroki unavailable → diagram sections get placeholder text, workflow continues
□ Azure Search unavailable → ingestion fails, workflow marked FAILED
□ Very large BRD (100+ pages) → chunking handles without memory issues
□ Custom template with 20+ sections → classification + planning completes
```

---

## Time Estimates

| Phase | Estimated Dev Time |
|-------|--------------------|
| Phase 1 — Foundation | 4–6 hours |
| Phase 2 — API stubs | 3–4 hours |
| Phase 3 — Services | 6–8 hours |
| Phase 4 — Infrastructure | 4–6 hours |
| Phase 5 — Ingestion | 6–8 hours |
| Phase 6 — Templates | 8–12 hours (most complex) |
| Phase 7 — Retrieval | 3–4 hours |
| Phase 8 — Generation | 8–12 hours (diagram loop is tricky) |
| Phase 9 — Assembly + Export | 6–8 hours |
| Phase 10 — Workers + SSE | 2–3 hours |
| Phase 11 — Validation | 4–6 hours |
| **Total** | **~55–75 hours** |
