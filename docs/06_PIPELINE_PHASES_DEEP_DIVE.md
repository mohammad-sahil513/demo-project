# 06 — Pipeline Phases Deep Dive

> Every phase of the 8-phase workflow pipeline. What happens, what goes in, what comes out,
> what gets written to the WorkflowRecord, what SSE events are emitted.

---

## Phase Execution Framework

Before diving into individual phases, understand the wrapper:

**`WorkflowExecutor._run_phase(phase, fn, *args)`**
- Emits `phase.started` SSE event
- Calls `fn(*args)` — the actual phase logic
- If exception: waits 2 seconds, retries once
- If retry also fails: raises `WorkflowPhaseError` — halts entire pipeline
- On success: computes new `overall_progress_percent` using PHASE_WEIGHTS, emits `phase.completed`

**Phase weights (contribute to 0–100% progress bar):**
- INPUT_PREPARATION: 2%
- INGESTION: 25%
- TEMPLATE_PREPARATION: 8%
- SECTION_PLANNING: 5%
- RETRIEVAL: 15%
- GENERATION: 35%
- ASSEMBLY_VALIDATION: 5%
- RENDER_EXPORT: 5%

---

## Phase 1 — INPUT_PREPARATION

**Purpose:** Initialize the workflow. The first thing that runs.

**What happens:**
1. Load `WorkflowRecord` from repository — confirm it exists
2. Set `status = RUNNING`, record `started_at = utc_now()`
3. Set `current_step_label = "Initializing..."`

**Reads from workflow:** `document_id`, `template_id`, `doc_type`

**Writes to workflow:** `status`, `started_at`

**SSE events:** `phase.started`, `phase.completed`

**Cost:** $0 — no Azure calls

**Why it exists:** Creates a clean initialization checkpoint. If Phase 1 fails (e.g. workflow record missing), the error is caught before any expensive operations start.

---

## Phase 2 — INGESTION

**Purpose:** Transform the BRD binary file into searchable, retrievable chunks in Azure AI Search.

**Ingest-once:** If `DocumentRecord.ingestion_status` is already `INDEXED`, Phase 2 **skips** parse/chunk/index (PDD/SDD/UAT runs reuse the same chunks). The executor should still emit phase SSE events and advance progress so the UI stays consistent.

**What happens — 4 stages:**

### Stage A: DOCX → PDF Conversion
- Get document file path from `DocumentRepository`
- If `content_type` is DOCX: call `docx2pdf.convert()` to produce `.converted.pdf`
- If conversion fails: log warning, continue with original file (Azure Doc Intelligence also accepts DOCX)
- If already PDF: skip this stage

### Stage B: Azure Document Intelligence Parse
- Read file bytes
- Send to Azure Document Intelligence `prebuilt-layout` model
- Wait for result (can take 20–60s depending on document size)
- Extract from result:
  - **Paragraphs:** all text with heading role context, in page order
  - **Tables:** each table converted to GFM markdown format (pipe-separated cells)
  - **Figures:** caption/alt-text of images
- Build `ParsedDocument` with per-page `ParsedPage` objects
- Emit: `ingestion.parse.completed` with `{pages, language}`

### Stage C: Hybrid Chunking
- Process tables first: each table in the document becomes its own `Chunk` with `content_type="table"`
- Process text: split `full_text` by heading-like patterns using regex
  - Patterns detected: Markdown headings (`## Title`), ALL-CAPS headings, numbered headings (`3.2 Section`)
  - Produces sections: `(heading_text, section_body, approx_page_number)`
- For each text section: apply fixed-size sliding window with overlap
  - Uses `tiktoken` cl100k_base encoder for accurate token counting
  - `chunk_size` tokens max (default 512), with `overlap` token overlap (default 64)
  - Chunks under 10 tokens are discarded (trivially small)
- Each chunk gets a unique `chunk_id`, records its `section_heading`, `page_number`, `content_type`
- Emit: `ingestion.chunk.completed` with `{chunk_count}`

### Stage D: Embed + Index
- For each chunk: call `AzureSKAdapter.generate_embedding(text)` → 3072-dim float vector
- Build search document dict with all index schema fields
- Batch upsert to Azure AI Search in groups of 50
- Calculate total embedding cost from token count × price rate
- Emit: `ingestion.index.completed` with `{indexed_count, embedding_cost_usd}`

**Writes to workflow:** `current_step_label` updated at each sub-stage. After completion: `page_count`, `chunk_count` visible in logs.

**SSE events:** `phase.started`, 3 ingestion sub-stage events, `phase.completed`

**Typical cost:** $0.01–0.05 (only embedding costs, no generation LLM calls)

---

## Phase 3 — TEMPLATE_PREPARATION

**Purpose:** Ensure the section plan and style map are ready for this workflow.

**Two paths:**

### Inbuilt Template Path
- Call `get_inbuilt_section_plan(doc_type)` from registry — returns hardcoded `list[SectionDefinition]`
- Call `get_inbuilt_style_map(doc_type)` from registry — returns hardcoded `StyleMap`
- No LLM calls, no file reads — pure in-memory data structures
- Serialize both to dicts and store in WorkflowRecord

### Custom Template Path
- Load `TemplateRecord` from repository
- Check `template_record.status == "READY"` — if NOT ready (still compiling or failed), raise exception
- Load `section_plan` list from `template_record.section_plan` (already compiled on upload)
- Load `style_map` from `template_record.style_map`
- Deserialize into proper model objects

**Writes to workflow:** `section_plan` (list of SectionDefinition dicts), stored for all subsequent phases

**SSE events:** `phase.started`, `phase.completed`

**Cost:** $0 — no Azure calls (custom template was compiled at upload time)

**Important:** Custom template compilation (extractor → classifier → planner) happens at template UPLOAD, not here. Phase 3 just verifies the compiled result is ready.

---

## Phase 4 — SECTION_PLANNING

**Purpose:** Finalize execution structure and initialize progress tracking.

**What happens:**
1. Read `section_plan` from `WorkflowRecord` (set in Phase 3)
2. Compute `total = len(section_plan)`
3. Initialize `SectionProgressRecord`:
   - `total = N`
   - `pending = N`
   - `running = 0`
   - `completed = 0`
   - `failed = 0`
4. Update `current_step_label = f"Planned {N} sections"`

**Writes to workflow:** `section_progress` dict

**SSE events:** `phase.started`, `phase.completed`

**Cost:** $0

**Why it exists:** Provides the frontend with section count information so the progress bar can show `"Generating section X of N"`.

---

## Phase 5 — RETRIEVAL

**Purpose:** For every section, find the most relevant BRD content using hybrid search.

**What happens:**

For ALL sections simultaneously (`asyncio.gather`):

### Per-Section Retrieval:
1. **Query resolution:**
   - If `section.retrieval_query` has ≥4 words → use it directly as search query
   - If shorter (too vague) → call GPT-5-mini to generate a better query
     - Prompt: section title + description + generation_hints → produce 8-12 word search query
     - Cost: ~$0.0001 per section (very cheap, low reasoning)
2. **Embedding:** Call `AzureSKAdapter.generate_embedding(query_text)` → 3072-dim vector
3. **Hybrid search:** Call `AzureSearchClient.hybrid_search()`
   - `search_text = query_text` (BM25 keyword component)
   - `vector = embedding` (vector similarity component)
   - `filter = document_id eq '{document_id}'` (namespace isolation)
   - `top_k = RETRIEVAL_TOP_K` (default 5)
4. **Package:** `EvidencePackager.package(section_id, chunks)`:
   - Builds `context_text` string: numbered source blocks with heading path and page reference
   - Creates `Citation` objects from chunk metadata

**What goes into LLM context (context_text format):**
```
[Source 1 — 2.3 Business Requirements, p.8 (text)]
{chunk text content here}

---

[Source 2 — 4.1 Technical Constraints, p.12 (table)]
| Column 1 | Column 2 |
| -------- | -------- |
| ...      | ...      |
```

**Writes to workflow:** `section_retrieval_results` dict: `{section_id: {context_text, citations}}`

**SSE events:** `phase.started`, `phase.completed`

**Typical cost:** ~$0.001 (embedding queries only, no generation)

---

## Phase 6 — GENERATION

**Purpose:** Use AI to generate content for every section using retrieved evidence.

**What happens:**

### Wave-Based Parallel Execution:
1. Find all sections whose `dependencies` are empty → Wave 1 → `asyncio.gather`
2. Mark those completed → find sections whose deps are now all done → Wave 2 → `asyncio.gather`
3. Repeat until all sections done

### Per-Section Generation:

**Emit:** `section.generation.started`

**Route by `output_type`:**

#### Text sections (`output_type = "text"`)
- Load prompt from `prompts/generation/text/{section.prompt_selector}.yaml`
- Falls back to `default.yaml` if selector file missing
- Build prompt with: section title, description, generation_hints, expected_length, tone, doc_type, `context_text` from EvidenceBundle
- Call `sk_adapter.invoke_text(task="text_generation")` → GPT-5-mini, medium effort, 1000 tokens
- Exception: `section.is_complex == True` → use `task="complex_section"` → GPT-5, high effort, 2500 tokens
- Returns markdown prose string

#### Table sections (`output_type = "table"`)
- Similar prompt structure but includes column headers instruction
- If `section.table_headers` set: prompt demands EXACTLY those columns in that order
- If only `section.required_fields`: prompt suggests those columns
- Call `sk_adapter.invoke_text(task="table_generation")` → GPT-5-mini, medium effort, 2000 tokens
- Returns GFM markdown table string (pipe syntax)

#### Diagram sections (`output_type = "diagram"`)
- Attempt 1–3 PlantUML:
  - Build prompt from `prompts/generation/diagram/default.yaml`
  - GPT-5 generates PlantUML source (high reasoning, 3000 tokens)
  - Encode source: `base64url(zlib.compress(source))`
  - GET `{KROKI_URL}/plantuml/png/{encoded}` → expect PNG bytes
  - Success → save PNG → store path → done
  - Failure → store (failed_code, kroki_error_message)
  - Next attempt: prompt now includes failed_code + error → "fix this"
- If all 3 PlantUML attempts fail:
- Attempt 4–6 Mermaid:
  - Same loop but using `prompts/generation/diagram/mermaid_default.yaml`
  - GET `{KROKI_URL}/mermaid/png/{encoded}`
  - Self-correction same pattern
- If all 6 fail: `content = "[Diagram could not be generated]"`, `error = "diagram_exhausted"`

**Emit:** `section.generation.completed` with status, cost_usd, tokens

**After all sections complete:**

**Writes to workflow:** `section_generation_results` dict:
```
{
  "sec-abc123": {
    "output_type": "text",
    "content": "## Executive Summary\n\n...",
    "diagram_source": null,
    "diagram_format": null,
    "diagram_png_path": null,
    "citations": [...],
    "tokens_in": 1200,
    "tokens_out": 850,
    "cost_usd": 0.000645,
    "error": null
  }
}
```

**Typical cost:** $0.10–1.00 (dominant cost of the entire workflow)

---

## Phase 7 — ASSEMBLY_VALIDATION

**Purpose:** Combine all generated sections into a single ordered document structure.

**What happens:**
1. Load `section_plan` from WorkflowRecord (to get ordering and section metadata)
2. Load `section_generation_results` from WorkflowRecord
3. Sort sections by `execution_order` (ascending)
4. For each section:
   - Skip if no generation result (generation may have completely failed)
   - Serialize Citation objects to dicts
   - Combine into `AssembledSection` with all content + metadata
5. Compute document title: `"{BRD filename} — {doc_type}"`
6. Build `AssembledDocument` with ordered `list[AssembledSection]`

**Writes to workflow:** `assembled_document` (serialized to dict for JSON storage)

**SSE events:** `phase.started`, `phase.completed`

**Cost:** $0

**Why separate from generation?** Clean separation of concerns. Generation produces raw results. Assembly is the validation + ordering step. Also allows the assembled document to be read by the frontend before export completes.

---

## Phase 8 — RENDER_EXPORT

**Purpose:** Convert the assembled document into the final downloadable file.

**What happens:**

### Route to correct builder (via `ExportRenderer`):

**UAT → `XLSXBuilder`:**
- If template file exists: open template workbook as base
- Else: create default 4-sheet workbook (Summary, Test Cases, Defect Log, Sign-Off)
- For each AssembledSection: find matching sheet by name (first 31 chars), parse markdown table from `content`, write rows
- Apply header styling from template's SheetMap or defaults
- Save `.xlsx` file to `storage/outputs/{workflow_run_id}.xlsx`

**Custom DOCX template → `DocxFiller`:**
- Open the original custom template DOCX as base document (preserves template formatting)
- For each AssembledSection: find matching heading in template by text comparison
- Clear placeholder content after heading
- Insert generated content (text paragraphs, tables, or diagram images)
- Preserve template paragraph styles throughout
- Save to disk

**Inbuilt template → `DocxBuilder`:**
- Create fresh DOCX using `python-docx`
- Apply `StyleMap` settings to heading styles and page setup
- Structure: Title page → page break → TOC → page break → sections → Appendix
- Level-1 sections get page breaks
- Tables built from markdown (parse pipe syntax → python-docx Table)
- Diagrams embedded as PNG images if `diagram_png_path` is set
- Save to disk

### After file is created:
- Create `OutputRecord` via `OutputService.create()` with file path, filename, size_bytes
- Update `WorkflowRecord.output_id` with the new output_id
- Emit `output.ready` SSE event with output_id

**Writes to workflow:** `output_id`

**SSE events:** `output.ready`, `phase.started`, `phase.completed`

**Cost:** $0

---

## Post-Pipeline Completion

After Phase 8 succeeds:
1. Call `ObservabilityCostTracker.get_summary()` → rolled-up cost/token totals
2. Update WorkflowRecord: `status = COMPLETED`, `completed_at = utc_now()`, `overall_progress_percent = 100.0`, `observability_summary = {...}`
3. Emit `workflow.completed` with `{output_id, total_cost_usd}`
4. SSE stream in `events.py` detects terminal event type → breaks generator loop → connection closes

If any phase raises after all retries:
1. Log error with traceback
2. Update WorkflowRecord: `status = FAILED`, `errors = [{phase, message, timestamp}]`
3. Emit `workflow.failed` with error message
4. Observability summary saved with whatever was collected so far

---

## Phase Summary Table

| Phase | Calls Azure? | Parallel? | SSE Events | Typical Duration |
|-------|-------------|-----------|-----------|-----------------|
| 1 INPUT_PREPARATION | No | N/A | 2 | <1s |
| 2 INGESTION | Yes (Doc Intel + Search + OpenAI) | Sub-stages sequential | 5 | 30–90s |
| 3 TEMPLATE_PREPARATION | No | N/A | 2 | <1s |
| 4 SECTION_PLANNING | No | N/A | 2 | <1s |
| 5 RETRIEVAL | Yes (OpenAI + Search) | All sections parallel | 2 | 10–30s |
| 6 GENERATION | Yes (OpenAI + Kroki) | Parallel waves | 2 + 2 per section | 60–180s |
| 7 ASSEMBLY_VALIDATION | No | N/A | 2 | <1s |
| 8 RENDER_EXPORT | No (local file ops) | N/A | 3 | 5–15s |
