# 08 — Observability, Citations & Frontend Integration

---

## Observability System

### Purpose
Track the cost and performance of every LLM call in the system, at three levels of granularity:
1. **Per LLM call** — logged in real-time to JSONL file
2. **Per phase** — accumulated by `ObservabilityCostTracker`
3. **Per workflow** — rolled-up summary stored in `WorkflowRecord`

### `ObservabilityCostTracker` (inner class of `WorkflowExecutor`)

**Created:** Once per workflow run, at the start of `WorkflowExecutor.run()`

**Passed to:** Every module that makes LLM calls — `IngestionOrchestrator`, `SectionRetriever`, `TextGenerator`, `TableGenerator`, `DiagramGenerator`, `TemplateClassifier`

**`record(call_result, task, phase, section_id, workflow_run_id, attempt)`:**
- Builds a `LLMCallRecord` dict from the call result
- Appends as one JSON line to `storage/logs/{workflow_run_id}_observability.jsonl` (immediate, append-only)
- Adds to in-memory accumulator: `phase_totals[phase]` += tokens_in, tokens_out, cost_usd, calls

**`get_summary()`:**
- Computes grand totals across all phases
- Returns summary dict with total_cost_usd, total_tokens_in, total_tokens_out, total_llm_calls
- Plus per-phase breakdown dict
- Called at end of workflow → stored in `WorkflowRecord.observability_summary`

### Where Costs Come From

| Source | Model | How Cost Computed |
|--------|-------|-------------------|
| Ingestion - embedding | text-embedding-3-large | token_count × $0.00013/1K |
| Retrieval - query generation | gpt5mini | (tokens_in + tokens_out) × pricing |
| Retrieval - embedding | text-embedding-3-large | token_count × $0.00013/1K |
| Generation - text sections | gpt5mini | (tokens_in + tokens_out) × pricing |
| Generation - table sections | gpt5mini | same |
| Generation - complex/diagram | gpt5 | (tokens_in + tokens_out) × gpt5 pricing |
| Template - classification | gpt5mini | same |

### Accessing Observability Data

**During workflow:** `GET /api/workflow-runs/{id}/observability`
Returns whatever has been accumulated so far in `observability_summary`.

**After workflow:** Same endpoint — full summary with all phases.

**JSONL file:** `storage/logs/{workflow_run_id}_observability.jsonl`
Each line is one JSON object — one LLM call. Useful for:
- Debugging which section cost the most
- Auditing model usage
- Cost optimization (identifying expensive sections)

### Typical Cost Breakdown

For a standard PDD (8-10 sections, moderate BRD):
```
INGESTION:    ~$0.01   (embedding ~50K tokens at $0.00013/1K)
RETRIEVAL:    ~$0.001  (5-10 query generations + embeddings)
GENERATION:   ~$0.20   (10 sections × avg $0.02 per section)
  - text sections: cheap ($0.001-0.005 each)
  - table sections: moderate ($0.005-0.010 each)
  - diagram sections: expensive ($0.05-0.15 each, up to 6 attempts)
TOTAL:        ~$0.21   typical range, can vary $0.10-$1.00
```

---

## Citations System

### What Citations Are

For every section in the generated document, citations record **which parts of the source BRD** were used as evidence for the AI generation. They provide traceability: the user can verify that the generated content is grounded in their BRD.

### Citation Data Journey

```
1. Azure AI Search chunk:
   { text, section_heading: "3.2 Authentication", page_number: 12, content_type: "text" }
   
2. RetrievedChunk (retriever.py):
   { chunk_id, text, section_heading, page_number, content_type, score }
   
3. Citation object (packager.py):
   { path: "3.2 Authentication", page: 12, content_type: "text", chunk_id: "chk-xyz" }
   
4. EvidenceBundle:
   citations = [Citation, Citation, ...]  ← per section
   
5. GenerationResult:
   citations = [same citations]  ← passed through from evidence, unchanged
   
6. AssembledSection:
   citations = [{ "path": "3.2 Authentication", "page": 12, 
                  "content_type": "text", "chunk_id": "chk-xyz" }]
   
7. API response:
   assembled_document.sections[i].citations = [above dicts]
   
8. DOCX/XLSX output:
   IGNORED — not included in any downloaded file
```

### Citation Display Format in UI

For each citation: `"{path}, p.{page} [{content_type}]"`

Examples:
- `"3.2 Authentication Requirements, p.12 [text]"`
- `"4.1 System Integrations, p.18 [table]"`
- `"Document, p.? [text]"` — when heading or page unknown

### Frontend Citation Component Specification

**Component name:** `CitationPanel` (to be added to output/preview page)

**Location in UI:** Below each section's content in the preview page

**Default state:** Collapsed — shows only: `"📎 Sources (N) ▼"` where N = citation count

**Expanded state:** Shows list of citations in the display format above

**Visibility rule:** Only show if `section.citations.length > 0`

**Zero citations:** Section still generated but labeled as `"📎 Sources (0)"` (LLM had no relevant chunks to cite)

---

## Frontend Integration Guide

### Current Frontend State

The frontend is a React + Vite app. The backend must maintain full backward compatibility. Only these changes are needed:

1. **Add SSE subscription** in the progress page
2. **Add CitationPanel component** in the output/preview page

Everything else continues working with zero changes.

---

### Change 1 — SSE Subscription (`src/api/workflowApi.ts`)

**New function to add:**

`subscribeToWorkflowEvents(workflowRunId, onEvent, onError)`:
- Creates an `EventSource` connected to `/api/workflow-runs/{id}/events`
- On each message: parse `event.data` as JSON, call `onEvent(parsedEvent)`
- On error: call `onError(e)`, close the EventSource
- Returns a cleanup function that calls `source.close()`

**TypeScript interface for events:**
```
WorkflowSSEEvent {
  type: string
  workflow_run_id: string
  timestamp: string
  // Optional fields depending on event type:
  phase?: string
  section_id?: string
  title?: string
  output_type?: string
  cost_usd?: number
  error?: string
  output_id?: string
  pages?: number
  chunk_count?: number
  progress_percent?: number
}
```

**Terminal event types:** `"workflow.completed"` and `"workflow.failed"` — close source after receiving either.

---

### Change 2 — Progress Page Update (`ProgressPage.tsx`)

**SSE-first with polling fallback:**

1. On component mount: call `subscribeToWorkflowEvents()` — store cleanup fn in ref
2. If SSE `onError` fires: stop SSE, start polling fallback (every 3s via `/status`)
3. On SSE events:
   - `phase.started` / `phase.completed` → update phase indicator UI
   - `section.generation.started` / `section.generation.completed` → update section counter
   - `workflow.completed` → navigate to output page, pass `output_id`
   - `workflow.failed` → show error state
4. On component unmount: call cleanup fn

**Handle heartbeat comments:** SSE heartbeat lines (`: heartbeat`) are comments — `EventSource` ignores them automatically, no special handling needed.

---

### Change 3 — Citation Panel (`CitationPanel.tsx`)

**Add to output/preview page** next to or below each section card.

**Props:**
- `citations: Citation[]`
- `sectionTitle: string` (for accessible aria label)

**Behavior:**
- If `citations.length === 0`: render nothing (or small greyed text "no sources")
- If `citations.length > 0`:
  - Render collapsed toggle: `📎 Sources ({N}) ▼`
  - On click: expand → show list of citation strings
  - Second click: collapse
- State: local `useState(false)` for open/closed

**Where to show:** In the section preview card, after the content markdown renderer, before the next section.

---

### Polling Fallback Specification

The `/status` endpoint is the fallback when SSE is unavailable (network issues, proxy stripping SSE headers, etc.).

**Poll every:** 3 seconds

**Stop polling when:** `status === "COMPLETED"` or `status === "FAILED"`

**On COMPLETED:** Same as receiving `workflow.completed` SSE event — navigate to output page with `output_id`

**Progress calculation:** Use `overall_progress_percent` directly for the progress bar.

**Phase label:** Use `current_phase` for the phase indicator, `current_step_label` for human-readable sub-label.

---

### UAT Template Preview Difference

When a template has `template_type === "UAT"`:
- Do NOT call `/templates/{id}/download` → `docx-preview` (DOCX only)
- Instead: call `/templates/{id}/preview-html` → render returned HTML string in a `div`
- Simple `dangerouslySetInnerHTML` or an iframe with `srcdoc`

---

## Logging System

### Structlog Configuration

**Development mode** (`APP_DEBUG=true`):
- Human-readable colored console output
- Format: `[LEVEL] timestamp logger_name: message key=value key=value`

**Production mode** (`APP_DEBUG=false`):
- JSON lines output
- Each log line is a parseable JSON object

### Per-Workflow Context Binding

At the start of `WorkflowExecutor.run()`, `bind_workflow_context(workflow_run_id, doc_type)` is called. This binds context variables to the current async context using `structlog.contextvars`. Every subsequent log call within that execution context automatically includes `workflow_run_id` and `doc_type` — no need to pass them to every function.

### Log Files

**Structured log:** `storage/logs/{workflow_run_id}.log` — all log lines from this workflow run
**Observability JSONL:** `storage/logs/{workflow_run_id}_observability.jsonl` — LLM calls only

### Key Log Events to Monitor

| Log Event | What It Means |
|-----------|--------------|
| `startup_complete` | App started successfully |
| `ingestion_start` | Phase 2 beginning |
| `doc_intelligence_done` | BRD parsed, chunks ready to create |
| `chunking_complete` | Chunks created, ready to index |
| `chunks_upserted` | Chunks in Azure AI Search |
| `retrieval_done` | Evidence bundle ready for a section |
| `llm_call_complete` | One LLM API call finished (includes cost, tokens, duration) |
| `diagram_success` | Diagram rendered successfully (format + attempt number) |
| `diagram_generation_exhausted` | All 6 diagram attempts failed |
| `template_compile_failed` | Custom template compilation error |
| `workflow_failed` | Workflow reached failed state |
| `background_task_failed` | Background task crashed (check for stack trace) |

---

## Diagnostics Endpoint

`GET /api/workflow-runs/{id}/diagnostics` returns a comprehensive debugging payload:

```
{
  "workflow_run_id": "wf-abc123",
  "status": "COMPLETED",
  "phases": [
    {
      "phase": "INGESTION",
      "status": "COMPLETED",
      "started_at": "...",
      "completed_at": "...",
      "duration_ms": 45200,
      "retry_count": 0,
      "error": null,
      "cost_usd": 0.012
    },
    ...
  ],
  "section_progress": {
    "total": 9, "completed": 9, "running": 0, "failed": 0, "pending": 0
  },
  "observability_summary": {
    "total_cost_usd": 0.42,
    "total_llm_calls": 24,
    "phases": { ... }
  },
  "errors": [...],
  "warnings": [
    {
      "phase": "INGESTION",
      "message": "docx2pdf failed, sending original DOCX to Doc Intelligence",
      "timestamp": "..."
    }
  ]
}
```

Use this endpoint when debugging a failed workflow to see exactly which phase failed and what the error was.
