# 05 — API Endpoints & Frontend Contracts

> Complete reference for all API endpoints. Includes request shape, response shape, and what the frontend expects.

---

## Response Envelope (All Endpoints)

Every response — success or error — uses this wrapper. Frontend Axios client unwraps `data` field.

**Success (2xx):**
```
{
  "success": true,
  "message": "Human readable message",
  "data": { ... },      ← actual payload
  "errors": [],
  "meta": {}
}
```

**Error (4xx/5xx):**
```
{
  "success": false,
  "message": "What went wrong",
  "data": null,
  "errors": [
    { "code": "NOT_FOUND", "detail": "Template not found: tpl-abc123" }
  ],
  "meta": {}
}
```

---

## Health Endpoints

### `GET /api/health`
**Purpose:** Liveness probe. Docker/K8s uses this.
**Response `data`:** `{ "status": "ok" }`
**Never fails** (except if Python process is dead).

### `GET /api/ready`
**Purpose:** Readiness check. Shows configuration state.
**Response `data`:**
```
{
  "status": "ready",
  "app": "ai-sdlc-backend",
  "env": "development",
  "azure_openai_configured": true,       ← bool, not actual connectivity check
  "azure_search_configured": true,
  "azure_doc_intelligence_configured": true,
  "kroki_url": "http://localhost:8000",
  "storage_root": "storage"
}
```

---

## Document Endpoints

### `POST /api/documents/upload`
**Content-Type:** `multipart/form-data`
**Form fields:** `file` — the BRD binary (PDF or DOCX only)

**Validation:**
- Rejects non-PDF / non-DOCX by content-type
- Rejects empty files

**Response (201):** Full `DocumentRecord` as data
```
{
  "document_id": "doc-3f2a1b9c8e12",
  "filename": "MyProject_BRD.pdf",
  "content_type": "application/pdf",
  "size_bytes": 245000,
  "status": "READY",
  "file_path": "doc-3f2a1b9c8e12.bin",
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z",
  "page_count": null,    ← populated after ingestion
  ...
}
```

### `GET /api/documents`
**Response `data`:**
```
{
  "items": [ ... list of DocumentRecord ... ],
  "total": 3
}
```

### `GET /api/documents/{document_id}`
**Response `data`:** Single `DocumentRecord`
**Error 404:** If document_id not found

### `DELETE /api/documents/{document_id}`
**Side effects:** Deletes binary file from disk AND JSON metadata, and removes indexed chunks for that `document_id` from Azure AI Search.
**Validation:** Returns **HTTP 400** if any workflow for this document is **`RUNNING`** (v1 — delete is blocked until runs finish).
**Response `data`:** `{ "document_id": "doc-abc123" }`

---

## Template Endpoints

### `POST /api/templates/upload`
**Content-Type:** `multipart/form-data`
**Form fields:**
- `file` — DOCX (PDD/SDD) or XLSX (UAT) template
- `template_type` — `"PDD"` | `"SDD"` | `"UAT"` (required)
- `version` — optional string label

**Behavior:**
- Saves file immediately
- Returns HTTP 201 with `status: "COMPILING"` — compilation happens in background
- Frontend should show a spinner and poll `/compile-status`

**Response (201) `data`:** `TemplateRecord` with `status: "COMPILING"`

### `GET /api/templates`
**Response `data`:**
```
{
  "items": [ ... TemplateRecord list ... ],
  "total": 5
}
```

### `GET /api/templates/{template_id}`
**Response `data`:** Full `TemplateRecord` including `section_plan` array (can be large)

### `GET /api/templates/{template_id}/compile-status`
**Purpose:** Frontend polls this every 2s after upload until status is READY or FAILED
**Response `data`:**
```
{
  "template_id": "tpl-xyz",
  "status": "COMPILING",     ← PENDING | COMPILING | READY | FAILED
  "error": null,             ← populated if FAILED
  "compiled_at": null,       ← ISO timestamp when done
  "section_count": 0         ← number of sections extracted (0 while compiling)
}
```

### `GET /api/templates/{template_id}/download`
**Purpose:** Frontend `docx-preview` library calls this to render template inline
**Response:** Binary file — `Content-Type: application/octet-stream`
**NOT wrapped in envelope** — direct binary stream

### `GET /api/templates/{template_id}/preview-html`
**Purpose:** UAT templates only — HTML table for sheet preview
**Response `data`:** `{ "html": "<table>...</table>" }`
**Frontend:** Renders in a div or iframe for UAT template preview

### `DELETE /api/templates/{template_id}`
**Response `data`:** `{ "template_id": "tpl-xyz" }`

---

## Workflow Endpoints

### `POST /api/workflow-runs`
**Purpose:** Create a workflow run (and optionally start it)
**Request body (JSON):**
```
{
  "document_id": "doc-abc123",
  "template_id": "tpl-xyz789",
  "doc_type": "PDD",            ← optional, auto-detected from template if omitted
  "start_immediately": true     ← default true
}
```

**Behavior:**
- Creates `WorkflowRecord` with `status: "PENDING"`
- Resolves `doc_type` from the request body or from the template record; **if `template.template_type` ≠ resolved `doc_type`, returns HTTP 400** — user must pick a matching template
- If `start_immediately: true` → dispatches `WorkflowExecutor.run()` as background task
- Returns HTTP 201 immediately — does NOT wait for pipeline to complete

**Response (201) `data`:** Full `WorkflowRecord`
**Frontend use:** Store `workflow_run_id` for subsequent status polling and SSE subscription

### `GET /api/workflow-runs`
**Response `data`:**
```
{
  "items": [ ... WorkflowRecord list ... ],
  "total": 3
}
```

### `GET /api/workflow-runs/{workflow_run_id}`
**Purpose:** Full detail including `assembled_document.sections` (large payload)
**Response `data`:** Complete `WorkflowRecord` as dict
**Use:** After workflow completes, frontend fetches this to render the preview page

### `GET /api/workflow-runs/{workflow_run_id}/status`
**Purpose:** LIGHTWEIGHT polling endpoint. Frontend polls every 3s when SSE is unavailable.

**Response `data` (EXACT shape frontend depends on):**
```
{
  "workflow_run_id": "wf-abc123",
  "status": "RUNNING",                      ← PENDING | RUNNING | COMPLETED | FAILED
  "current_phase": "GENERATION",
  "overall_progress_percent": 65.0,         ← 0.0 to 100.0
  "current_step_label": "Generating section 4 of 9",
  "document_id": "doc-xyz",
  "template_id": "tpl-xyz",
  "output_id": null                         ← set when COMPLETED
}
```

**Status semantics (frontend logic depends on this):**
- `"FAILED"` → show error state
- `"COMPLETED"` → show download button (`output_id` will be non-null)
- anything else → show progress bar

### `GET /api/workflow-runs/{workflow_run_id}/sections`
**Response `data`:**
```
{
  "section_plan": [
    {
      "section_id": "sec-abc",
      "title": "Executive Summary",
      "level": 1,
      "output_type": "text",
      "execution_order": 0,
      ...
    }
  ],
  "section_progress": {
    "total": 9,
    "completed": 4,
    "running": 1,
    "failed": 0,
    "pending": 4
  }
}
```

### `GET /api/workflow-runs/{workflow_run_id}/observability`
**Purpose:** Cost and token breakdown for debugging and cost tracking
**Response `data`:** Full observability summary dict
```
{
  "total_cost_usd": 0.42,
  "total_tokens_in": 28000,
  "total_tokens_out": 12000,
  "total_llm_calls": 24,
  "phases": {
    "INGESTION": { "cost_usd": 0.01, "tokens_in": 5000, "calls": 1 },
    "GENERATION": { "cost_usd": 0.41, "calls": 21 }
  }
}
```

### `GET /api/workflow-runs/{workflow_run_id}/errors`
**Response `data`:**
```
{
  "errors": [
    { "phase": "GENERATION", "message": "Diagram failed after 6 attempts", "timestamp": "..." }
  ],
  "warnings": [
    { "phase": "INGESTION", "message": "docx2pdf failed, using original DOCX", "timestamp": "..." }
  ]
}
```

### `GET /api/workflow-runs/{workflow_run_id}/diagnostics`
**Purpose:** Full debugging dump — phases with timing + observability + errors
**Response `data`:** Combines phases, section_progress, observability_summary, errors/warnings

### `GET /api/workflow-runs/{workflow_run_id}/events`
**Purpose:** SSE stream for real-time progress
**Response:** `text/event-stream` with `data: {json}\n\n` lines
**Headers set:** `Cache-Control: no-cache`, `X-Accel-Buffering: no`, `Connection: keep-alive`
**Closes:** Automatically after `workflow.completed` or `workflow.failed` event

**Frontend TypeScript usage:**
```typescript
const source = new EventSource(`/api/workflow-runs/${workflowRunId}/events`);
source.onmessage = (e) => {
  const event = JSON.parse(e.data);
  // event.type determines what changed
  // event.workflow_run_id confirms which workflow
};
source.onerror = () => source.close();
// When done:
source.close();
```

---

## Output Endpoints

### `GET /api/outputs/{output_id}`
**Response `data`:** Full `OutputRecord`
```
{
  "output_id": "out-abc123",
  "workflow_run_id": "wf-xyz",
  "doc_type": "PDD",
  "output_format": "DOCX",
  "status": "READY",
  "filename": "PDD_output.docx",
  "size_bytes": 185000,
  "ready_at": "2025-01-01T10:05:00Z"
}
```

### `GET /api/outputs/{output_id}/download`
**Purpose:** Download the generated DOCX or XLSX file
**Response:**
- For DOCX: `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- For XLSX: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Header: `Content-Disposition: attachment; filename="{filename}"`
- Body: Raw binary file

**NOT wrapped in JSON envelope** — direct FileResponse from FastAPI

---

## Frontend API Contract — Critical Fields

The frontend reads these exact field names. Never rename them.

### On `/workflow-runs/{id}/status`
```
workflow_run_id          string
status                   "PENDING" | "RUNNING" | "COMPLETED" | "FAILED"
current_phase            string (WorkflowPhase value)
overall_progress_percent float (0.0 – 100.0)
current_step_label       string (human readable)
output_id                string | null (set when COMPLETED)
```

### On `GET /workflow-runs/{id}` — assembled_document.sections items
```
section_id       string
title            string
level            int (1-6)
output_type      "text" | "table" | "diagram"
content          string (markdown — rendered by react-markdown + remark-gfm)
citations        list[{ path, page, content_type, chunk_id }]
execution_order  int
```

### On `POST /workflow-runs` response
```
workflow_run_id   string  ← MUST be in response for frontend to subscribe to SSE
status            string
```

### On `POST /documents/upload` response
```
document_id   string  ← MUST be in response to pass to workflow creation
```

### On `POST /templates/upload` response
```
template_id   string  ← for polling compile-status
status        "COMPILING"  ← triggers spinner in UI
```

---

## Error Codes Reference

| Code | HTTP Status | When |
|------|------------|------|
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid input |
| `WORKFLOW_ERROR` | 400 | Workflow-level problem |
| `INGESTION_ERROR` | 400 | Ingestion pipeline failure |
| `TEMPLATE_ERROR` | 400 | Template compile failure |
| `GENERATION_ERROR` | 400 | Section generation failure |
| `DIAGRAM_RENDER_ERROR` | 400 | Kroki render failure |
| `EXPORT_ERROR` | 400 | DOCX/XLSX build failure |
| `INFRASTRUCTURE_ERROR` | 400 | Azure service error |
| `INTERNAL_ERROR` | 500 | Unexpected exception |

---

## Frontend SSE Event Handling Pattern

```typescript
// Recommended pattern for ProgressPage component:

// 1. Try SSE first
const source = new EventSource(`/api/workflow-runs/${id}/events`);
let sseConnected = true;

source.onmessage = (e) => {
  const event = JSON.parse(e.data);
  updateProgressFromEvent(event);
};

source.onerror = () => {
  sseConnected = false;
  source.close();
  // Fall back to polling
  startPolling();
};

// 2. Polling fallback
function startPolling() {
  const interval = setInterval(async () => {
    const res = await axios.get(`/api/workflow-runs/${id}/status`);
    updateProgressFromStatus(res.data.data);
    if (["COMPLETED", "FAILED"].includes(res.data.data.status)) {
      clearInterval(interval);
    }
  }, 3000);
}
```
