# 03 — Tech Stack, Dependencies & Configuration

---

## Runtime Requirements

- **Python 3.11+** — required minimum
- **Operating System:** Windows local dev (MS Word required for docx2pdf). Linux/Mac need LibreOffice.
- **Docker:** Kroki container must be running at `localhost:8000` for diagram generation
- **MS Word:** Required on Windows for docx2pdf DOCX→PDF conversion

---

## Python Dependencies

### Web Framework
| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.111.0 | HTTP API framework — routing, dependency injection, validation, OpenAPI docs |
| `uvicorn[standard]` | 0.29.0 | ASGI server — runs FastAPI, includes websockets + watchfiles for reload |
| `python-multipart` | 0.0.9 | Required for FastAPI file upload (multipart/form-data parsing) |

### Settings & Validation
| Package | Version | Purpose |
|---------|---------|---------|
| `pydantic` | 2.7.0 | Schema validation, typed models for all data structures |
| `pydantic-settings` | 2.2.1 | Auto-load settings from `.env` with type validation |
| `python-dotenv` | 1.0.1 | `.env` file loading |

### Azure AI
| Package | Version | Purpose |
|---------|---------|---------|
| `semantic-kernel` | 1.3.0 | LLM orchestration layer — unified adapter for Azure OpenAI |
| `openai` | 1.30.0 | Azure OpenAI SDK (used internally by Semantic Kernel) |
| `azure-identity` | 1.16.0 | DefaultAzureCredential for managed identity scenarios |
| `azure-search-documents` | 11.6.0 | Azure AI Search client (upsert, hybrid search, delete) |
| `azure-ai-documentintelligence` | 1.0.0 | Azure Document Intelligence client |

### Document Processing
| Package | Version | Purpose |
|---------|---------|---------|
| `python-docx` | 1.1.0 | Read/write DOCX files — template extraction + DOCX building/filling |
| `docx2pdf` | 0.1.8 | Convert DOCX to PDF before sending to Doc Intelligence |
| `openpyxl` | 3.1.2 | Read/write XLSX — UAT template parsing + Excel output generation |
| `pillow` | 10.3.0 | Image handling — embedding PNG diagrams into DOCX |
| `lxml` | 5.2.1 | XML parsing (python-docx dependency) |
| `pyyaml` | 6.0.1 | Parse YAML prompt files |
| `tiktoken` | 0.7.0 | Accurate token counting for chunk sizing (cl100k_base encoding) |

### HTTP & Async
| Package | Version | Purpose |
|---------|---------|---------|
| `httpx` | 0.27.0 | Async HTTP client — Kroki diagram rendering calls |
| `tenacity` | 8.3.0 | Retry policies (used in infrastructure adapters) |

### Logging & Serialization
| Package | Version | Purpose |
|---------|---------|---------|
| `structlog` | 24.1.0 | Structured logging with context binding (workflow_run_id attached automatically) |
| `orjson` | 3.10.3 | Fast JSON serialization (replaces stdlib json in response building) |

### Dev Only
| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | 8.2.0 | Test runner |
| `pytest-asyncio` | 0.23.6 | Async test support |
| `pytest-cov` | 5.0.0 | Coverage reporting |
| `ruff` | 0.4.4 | Linter + formatter (replaces black + flake8) |

---

## External Services

### Azure OpenAI
**Purpose:** All LLM inference (text generation, table generation, diagram generation, classification) + embeddings

**Deployments needed in your Azure resource:**

| Internal Alias | Model | Used For |
|---------------|-------|----------|
| `gpt5` | GPT-5 | Complex sections, diagram generation, diagram self-correction |
| `gpt5mini` | GPT-5-mini | Text generation, table generation, template classification, retrieval query generation |
| `text-embedding-3-large` | text-embedding-3-large | Document chunk embedding (3072 dimensions) |

**GPT-5 calling policy (CRITICAL — don't break this):**
- Use `max_completion_tokens` (NOT `max_tokens` — GPT-5 rejects it)
- Use `reasoning_effort` in `extra_body`: `"high"` / `"medium"` / `"low"`
- Do NOT set `temperature` — GPT-5 doesn't support it
- Do NOT set `max_tokens` — deprecated for GPT-5

**API version:** `2024-02-01`

---

### Azure AI Search
**Purpose:** Store and retrieve document chunks using hybrid search (vector + keyword BM25)

**Architecture decision:** Single shared index for all documents. Namespace isolation via `document_id` filter on every search call.

**Index name:** configured in `AZURE_SEARCH_INDEX_NAME` (default: `sdlc-chunks`)

**Required index schema fields:**

| Field | Type | Notes |
|-------|------|-------|
| `chunk_id` | Edm.String | Primary key |
| `document_id` | Edm.String | Filterable — namespace isolation |
| `workflow_run_id` | Edm.String | Filterable |
| `text` | Edm.String | Searchable, English Microsoft analyzer |
| `chunk_index` | Edm.Int32 | Sortable |
| `section_heading` | Edm.String | Searchable + filterable |
| `page_number` | Edm.Int32 | Filterable |
| `content_type` | Edm.String | Filterable ("text" or "table") |
| `embedding` | Collection(Edm.Single) | 3072 dimensions, HNSW, cosine metric |

Semantic configuration: `text` as content field, `section_heading` as keywords field.

**Must be pre-created** via Azure portal or CLI before first run.

---

### Azure Document Intelligence
**Purpose:** Parse BRD documents — extract text, headings, tables (as markdown), figure captions

**Model:** `prebuilt-layout` — best for structured documents with headings and tables

**Input:** PDF (primary) or DOCX (fallback when docx2pdf fails). Both supported natively.

**What it extracts:**
- All paragraphs (with heading role if applicable)
- Tables → rows and cells (converted to markdown internally)
- Figure captions / alt-text

---

### Kroki (Docker)
**Purpose:** Render PlantUML and Mermaid diagram source code → PNG images

**Why Kroki:** No Java dependency (PlantUML normally requires Java), supports multiple diagram formats, simple HTTP API, runs locally.

**Setup:** Use a port **different** from the FastAPI app (default API `APP_PORT=8000`). Kroki defaults to **8001** in `.env.example`.
```
docker run -d --name kroki -p 8001:8000 yuzutech/kroki
```

**Verify running:**
```
curl http://localhost:8001/health
Expected response: {"status":"pass"}
```

**How it's called:** HTTP GET with diagram source encoded in URL path:
```
base64url(zlib.compress(diagram_source_utf8)) → path component
GET http://localhost:8001/plantuml/png/{encoded}
GET http://localhost:8001/mermaid/png/{encoded}
Response: PNG image bytes (if valid) or 400/500 error
```

**Error handling:** HTTP 4xx = diagram syntax error (trigger self-correction). HTTP 5xx or connection refused = retry logic or fail gracefully.

---

## `.env` File — Complete Reference

```
# Application
APP_NAME=ai-sdlc-backend
APP_ENV=development          # development | production
APP_DEBUG=true               # true = human-readable logs, false = JSON logs
APP_HOST=0.0.0.0
APP_PORT=8000

# API
API_PREFIX=/api              # All routes mounted here

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Storage root (relative to backend/)
STORAGE_ROOT=storage         # All subdirs created automatically

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_GPT5_DEPLOYMENT=gpt5
AZURE_OPENAI_GPT5MINI_DEPLOYMENT=gpt5mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-key
AZURE_SEARCH_INDEX_NAME=sdlc-chunks

# Kroki (must not use the same port as the API server)
KROKI_URL=http://localhost:8001

# Cost model — Document Intelligence (USD per page, prebuilt-layout estimate)
DOCUMENT_INTELLIGENCE_USD_PER_PAGE=0.01

# Chunking settings
CHUNK_SIZE_TOKENS=512        # Max tokens per chunk
CHUNK_OVERLAP_TOKENS=64      # Overlap between consecutive chunks

# Retrieval
RETRIEVAL_TOP_K=5            # How many chunks to retrieve per section

# LLM token budgets (max_completion_tokens per call)
GENERATION_TEXT_BUDGET=1000
GENERATION_TABLE_BUDGET=2000
GENERATION_DIAGRAM_BUDGET=3000      # For each diagram attempt
GENERATION_COMPLEX_BUDGET=2500      # For is_complex=True sections
GENERATION_CLASSIFICATION_BUDGET=800
GENERATION_RETRIEVAL_QUERY_BUDGET=300
```

---

## LLM Task Routing Table

Defined in `core/constants.py`. The `sk_adapter.py` uses these to select model, effort, and budget.

| Task String | Model | Reasoning Effort | Token Budget |
|-------------|-------|-----------------|-------------|
| `diagram_generation` | gpt5 | high | 3000 |
| `diagram_correction` | gpt5 | high | 3000 |
| `complex_section` | gpt5 | high | 2500 |
| `text_generation` | gpt5mini | medium | 1000 |
| `table_generation` | gpt5mini | medium | 2000 |
| `template_classification` | gpt5mini | low | 800 |
| `retrieval_query_generation` | gpt5mini | low | 300 |

---

## Cost Tracking Rates

Stored in `core/constants.MODEL_PRICING`. Updated manually when Azure pricing changes.

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|----------------------|
| `gpt5` | $0.015 | $0.060 |
| `gpt5mini` | $0.00015 | $0.0006 |
| `text-embedding-3-large` | $0.00013 | $0 |

Cost formula per call: `(tokens_in / 1000 * input_rate) + (tokens_out / 1000 * output_rate)`

---

## Frontend Dependencies (Reference)

The frontend is a separate React + Vite project. Backend must maintain API compatibility with these consumers.

| Package | Version | Why Backend Cares |
|---------|---------|-------------------|
| `axios` | ^1.6.7 | All REST calls — depends on `{success, data, errors}` response envelope |
| `docx-preview` | ^0.3.7 | Downloads template binary from `/templates/{id}/download` and renders inline |
| `react-markdown` + `remark-gfm` | latest | Renders `section.content` markdown — backend must produce valid GFM |
| Event Source API | browser native | Connects to `/workflow-runs/{id}/events` SSE stream |

**Frontend-critical API contracts (never break these):**

1. `/status` response must contain: `workflow_run_id`, `status`, `current_phase`, `overall_progress_percent`, `current_step_label`, `output_id`
2. `status` values frontend reads: `"FAILED"` (show error), `"COMPLETED"` (enable download), anything else (show progress)
3. `assembled_document.sections[i]` must have: `section_id`, `title`, `level`, `output_type`, `content`, `citations`
4. All responses wrapped in `{success, message, data, errors, meta}` envelope
5. `/outputs/{id}/download` must return binary with correct Content-Type header

---

## docx2pdf Platform Notes

`docx2pdf` uses COM automation on Windows (Microsoft Word must be installed).

**Fallback behavior** (already handled in `ingestion/orchestrator.py`):
- If docx2pdf fails for any reason → log warning → send original DOCX directly to Azure Document Intelligence
- Azure Document Intelligence natively supports DOCX input
- No exception raised — ingestion continues

**On Linux/Mac (for deployment):** Replace docx2pdf with LibreOffice headless command:
```
libreoffice --headless --convert-to pdf --outdir /tmp /path/to/file.docx
```
