# 01 — Architecture Diagrams

> All structural diagrams for the system. Read these before writing any file.

---

## Diagram 1 — Full Layer Architecture

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  main.py                                                                    ║
║  FastAPI application factory                                                ║
║  Registers: CORS middleware, request-ID middleware, exception handlers,      ║
║             api_router at /api prefix, lifespan hooks (startup + shutdown)   ║
╚══════════════════════════╦══════════════════════════════════════════════════╝
                           ║ mounts
╔══════════════════════════╩══════════════════════════════════════════════════╗
║  api/router.py                                                              ║
║  Single central router. Includes 6 sub-routers:                             ║
║  health · documents · templates · workflow-runs · outputs · events (SSE)    ║
╚═══════════════╦═══════════════════════════════════════════════════════════ ╝
                ║ each route calls service via Depends()
╔═══════════════╩══════════════════════════════════════════════════════════╗
║  api/deps.py                                                              ║
║  Dependency injection providers for all services and repos               ║
║  Two module-level singletons: EventService + TaskDispatcher              ║
╚════╦═══════════╦═══════════════╦═════════════════╦═════════════════╦═════╝
     ║           ║               ║                 ║                 ║
╔════╩═══╗ ╔════╩═══╗  ╔════════╩═════╗  ╔════════╩═════╗  ╔════════╩══════╗
║Document║ ║Template║  ║   Workflow   ║  ║   Output     ║  ║  Event        ║
║Service ║ ║Service ║  ║   Service   ║  ║   Service    ║  ║  Service      ║
╚════╦═══╝ ╚════╦═══╝  ╚═══════╦══════╝  ╚════════╦═════╝  ╚═══════╦═══════╝
     ║           ║              ║                  ║                ║
╔════╩══════════╩══════════════╩══════════════════╩════╗           ║
║              Repositories (JSON files)               ║           ║
║  document_repo · template_repo · workflow_repo       ║           ║
║  output_repo · base.py                               ║           ║
╚══════════════════════════════════════════════════════╝           ║
                                                                   ║
╔═══════════════════════════════════════════════════════════════════╩══════╗
║              WorkflowExecutor  (services/workflow_executor.py)           ║
║  THE core orchestrator. Runs all 8 phases end-to-end.                    ║
║  Calls every domain module in sequence.                                  ║
╚═══════════════════╦══════════════════════════════════════════════════════╝
                    ║ calls in sequence
     ┌──────────────┼──────────────────────────────────┐
     ▼              ▼              ▼                    ▼
modules/       modules/       modules/           modules/
ingestion/     template/      retrieval/         generation/
               assembly/      export/
     │              │              │                    │
     └──────────────┴──────────────┴────────────────────┘
                    ▼
╔══════════════════════════════════════════════════════════╗
║             Infrastructure (Azure SDK wrappers)          ║
║   sk_adapter.py   search_client.py   doc_intelligence.py ║
╚══════════════════════════════════════════════════════════╝
```

---

## Diagram 2 — WorkflowExecutor Phase Flow

```
WorkflowExecutor.run(workflow_run_id)
│
├── emit: workflow.started
│
├── PHASE 1: _phase_input_preparation()
│     Load workflow + document + template records.
│     Set status = RUNNING. Record started_at.
│     emit: phase.started → phase.completed
│
├── PHASE 2: _phase_ingestion()
│     Get document file path from DocumentRepository.
│     Call IngestionOrchestrator.run().
│     ├── convert DOCX→PDF if needed (docx2pdf)
│     ├── Azure Doc Intelligence → ParsedDocument
│     │   emit: ingestion.parse.completed
│     ├── DocumentChunker → List[Chunk]
│     │   emit: ingestion.chunk.completed
│     └── DocumentIndexer → embed + upsert Azure AI Search
│         emit: ingestion.index.completed
│     emit: phase.started → phase.completed
│
├── PHASE 3: _phase_template_preparation()
│     If inbuilt: load SectionPlan from registry (no Azure call)
│     If custom: verify template.status == READY (compiled on upload)
│     Store section_plan + style_map in WorkflowRecord
│     emit: phase.started → phase.completed
│
├── PHASE 4: _phase_section_planning()
│     Count sections. Initialize SectionProgressRecord.
│     {total, pending, running, completed, failed}
│     emit: phase.started → phase.completed
│
├── PHASE 5: _phase_retrieval()
│     asyncio.gather([retrieve_for_section(s) for each section])
│     Each section:
│       → resolve query (use retrieval_query if ≥4 words, else GPT-5-mini)
│       → embed query
│       → hybrid_search (vector + BM25) filtered by document_id
│       → package chunks into EvidenceBundle with citations
│     Store all bundles in workflow.section_retrieval_results
│     emit: phase.started → phase.completed
│
├── PHASE 6: _phase_generation()
│     GenerationOrchestrator.run_all_sections()
│     Topological wave execution:
│       Wave 1: asyncio.gather(all sections with no deps)
│         → each emits section.generation.started
│         → TextGenerator (GPT-5-mini) for text sections
│         → TableGenerator (GPT-5-mini) for table sections
│         → DiagramGenerator (GPT-5 + Kroki) for diagram sections
│             [PlantUML × 3 self-correction → Mermaid × 3 fallback]
│         → each emits section.generation.completed
│       Wave 2: sections whose wave-1 deps are done
│       Wave N: continues until all done
│     Store results in workflow.section_generation_results
│     emit: phase.started → phase.completed
│
├── PHASE 7: _phase_assembly()
│     DocumentAssembler.assemble()
│     Order by execution_order → build AssembledDocument
│     Attach citation dicts per section
│     Store assembled_document in WorkflowRecord
│     emit: phase.started → phase.completed
│
└── PHASE 8: _phase_render_export()
      ExportRenderer.render() routes to:
        UAT → XLSXBuilder (openpyxl fills workbook)
        custom DOCX → DocxFiller (heading-match fill)
        inbuilt DOCX → DocxBuilder (build from scratch)
      Create OutputRecord. Save output_id to WorkflowRecord.
      emit: output.ready
      emit: phase.started → phase.completed

└── update status = COMPLETED
    emit: workflow.completed
```

---

## Diagram 3 — Template Compilation Flow

```
User uploads custom template (DOCX or XLSX)
        │
        ▼
POST /api/templates/upload
   TemplateService.save_template()
        │
        ├── Save binary file to disk
        ├── Create TemplateRecord {status: COMPILING}
        ├── Return HTTP 201 immediately
        │
        └── TaskDispatcher dispatches compile in background
                │
                ▼
        TemplateService.compile_template(template_id)
                │
        ┌───────┴──────────────────────────────────┐
        │ DOCX path (PDD/SDD)                      │ XLSX path (UAT)
        │                                          │
        ▼                                          ▼
  TemplateExtractor.extract_docx()      TemplateExtractor.extract_xlsx()
    Produces:                             Produces:
    - StyleMap (fonts, colors,            - SheetMap {sheet names + headers}
      table styles, page layout)          - List of sheet structures
    - DocumentSkeleton
      (only headings + table shells)
        │                                          │
        ▼                                          ▼
  TemplateClassifier.classify_sections()   Each sheet → SectionDefinition
    One LLM call for ALL sections            output_type = "table"
    GPT-5-mini, low reasoning effort         table_headers = column headers
    Returns output_type, description,        execution_order = sheet order
    generation_hints, retrieval_query,
    prompt_selector, is_complex, etc.
        │                                          │
        ▼                                          ▼
  SectionPlanner.build()                 SectionPlanner.build()
    Assigns section_ids                    Same process
    Resolves parent hierarchy
    Resolves dependency IDs
        │                                          │
        └──────────────────┬────────────────────────┘
                           ▼
           List[SectionDefinition]  ← IDENTICAL SCHEMA for both paths
                           │
                           ▼
        PreviewGenerator.build_preview()
          DOCX: skeleton DOCX with placeholder content per section
          XLSX: Sheet1 → HTML table string
                           │
                           ▼
        TemplateRecord updated:
          status = READY
          section_plan = [...]
          style_map = {...} or sheet_map = {...}
          preview_path = "..."
          compiled_at = timestamp
```

---

## Diagram 4 — Diagram Generation Self-Correction Loop

```
DiagramGenerator.generate(section)

Context: gather evidence from EvidenceBundle
         load PlantUML prompt template

──────── PlantUML Attempt 1 ────────────
Send prompt to GPT-5 (reasoning_effort=high, 3000 tokens)
GPT-5 returns PlantUML source code
Strip markdown fences from response
Encode: base64url(zlib.compress(plantuml_code))
HTTP GET Kroki: /plantuml/png/{encoded}
    │
    ├── HTTP 200 → save PNG → return success ✅
    │
    └── HTTP 4xx/5xx or connection error
          Store (failed_code, error_message)

──────── PlantUML Attempt 2 (self-correction) ────────────
Prompt now includes:
  - Original section context
  - Failed code from attempt 1
  - Error message from Kroki
  - "Fix this error. Do not repeat the same mistake."
GPT-5 returns corrected PlantUML
Kroki render attempt
    ├── 200 → save PNG → return ✅
    └── fail → store error

──────── PlantUML Attempt 3 (final) ────────────
Same self-correction pattern
    ├── 200 → return ✅
    └── ALL 3 PlantUML attempts failed

──────── SWITCH TO MERMAID ────────────
Load mermaid_default.yaml prompt template

Attempt 1 (fresh Mermaid): GPT-5 → Mermaid code → Kroki /mermaid/png/
    ├── 200 → return GenerationResult(format="mermaid") ✅
    └── fail

Attempt 2 (Mermaid self-correction): include failed_code + error
Attempt 3 (Mermaid final attempt)
    ├── 200 → return ✅
    └── ALL 6 attempts exhausted

──────── EXHAUSTION RESULT ────────────
GenerationResult(
  content = "[Diagram could not be generated after 6 attempts]",
  error = "diagram_exhausted",
  diagram_png_path = None
)
→ Assembler includes this placeholder text
→ DOCX gets placeholder text (no image)
→ Workflow continues normally — NOT a fatal error
```

---

## Diagram 5 — SSE Event Subscription Flow

```
Frontend                     EventService (in-memory)       WorkflowExecutor
    │                              │                              │
    │ GET /api/workflow-runs/      │                              │
    │     {id}/events ────────────▶│                              │
    │                              │ subscribe(workflow_run_id)   │
    │                              │ → create asyncio.Queue(200)  │
    │                              │ → add to dict[id][queues]    │
    │◀── SSE stream opens ─────────│                              │
    │                              │                              │
    │                              │◀─────── emit(WORKFLOW_STARTED)─┤
    │◀── data: {type:"workflow.    │                              │
    │    started", ...} ───────────│                              │
    │                              │◀─────── emit(PHASE_STARTED) ──┤
    │◀── data: {phase:"INGESTION"} │                              │
    │                              │                              │
    │   (no events for 30s)        │                              │
    │◀── : heartbeat ──────────────│  ← comment line keeps alive  │
    │                              │                              │
    │                              │◀─ emit(INGESTION_PARSE_DONE) ─┤
    │◀── data: {pages:15,...} ─────│                              │
    │                              │                              │
    │         ... events ...       │                              │
    │                              │                              │
    │                              │◀─────── emit(OUTPUT_READY) ───┤
    │◀── data: {type:"output.      │                              │
    │    ready", output_id:"..."} ─│                              │
    │                              │                              │
    │                              │◀── emit(WORKFLOW_COMPLETED) ──┤
    │◀── data: {type:"workflow.    │                              │
    │    completed",...} ──────────│                              │
    │                              │ stream generator detects     │
    │                              │ terminal event → break loop  │
    │  EventSource auto-closes ◀───│ StreamingResponse ends       │
    │  Frontend: enable download   │ unsubscribe(id, queue)       │
```

---

## Diagram 6 — Citation Flow (Retrieval → Preview)

```
Phase 5 — RETRIEVAL:
  Azure Search returns chunk:
    { text, section_heading: "3.2 Auth", page_number: 12, content_type: "text" }
                │
                ▼
  RetrievedChunk object created
  → chunk_id, text, section_heading, page_number, content_type, score
                │
                ▼
  EvidencePackager.package():
    context_text = "[Source 1 — 3.2 Auth, p.12 (text)]\n{chunk text}"
    Citation = { path: "3.2 Auth", page: 12, content_type: "text", chunk_id: "chk-xyz" }
                │
                ▼
Phase 6 — GENERATION:
  Prompt built with context_text
  LLM generates section content
  GenerationResult.citations = [same Citation objects] ← attached unchanged
                │
                ▼
Phase 7 — ASSEMBLY:
  AssembledSection.citations = [
    { "path": "3.2 Auth", "page": 12, "content_type": "text", "chunk_id": "chk-xyz" }
  ]
                │
     ┌──────────┴──────────────────────────────┐
     │                                         │
     ▼  API response                           ▼  DOCX/XLSX export
  sections[i].citations                   COMPLETELY IGNORED
  → Frontend renders:                     → Clean professional doc
    "📎 Sources (1) ▼"                      Zero citation markup
    "3.2 Auth, p.12 [text]"
```

---

## Diagram 7 — Storage Directory Map

```
storage/
│
├── documents/
│   ├── doc-abc123.bin          ← raw PDF or DOCX binary (as uploaded)
│   └── doc-abc123.json         ← DocumentRecord metadata
│
├── templates/
│   ├── tpl-xyz789.bin          ← raw uploaded DOCX or XLSX template
│   ├── tpl-xyz789.json         ← TemplateRecord (status, section_plan, style_map)
│   ├── tpl-xyz789_preview.docx ← skeleton preview with placeholders
│   └── tpl-xyz789_preview.html ← HTML table preview (UAT templates only)
│
├── workflows/
│   └── wf-001.json             ← Full WorkflowRecord (ALL state: plan, results, assembled_doc)
│
├── outputs/
│   ├── wf-001.docx             ← Final generated PDD document (download-ready)
│   ├── wf-002.docx             ← Final generated SDD document
│   ├── wf-003.xlsx             ← Final generated UAT Excel
│   └── out-aaa.json            ← OutputRecord metadata
│
├── diagrams/
│   └── wf-001/
│       ├── sec-abc_plantuml_a1.png   ← first attempt
│       ├── sec-abc_plantuml_a2.png   ← self-corrected second attempt
│       └── sec-def_mermaid_a1.png    ← Mermaid fallback rendered
│
└── logs/
    ├── wf-001.log                    ← structured log lines (structlog)
    └── wf-001_observability.jsonl    ← one JSON line per LLM call (real-time append)
```
