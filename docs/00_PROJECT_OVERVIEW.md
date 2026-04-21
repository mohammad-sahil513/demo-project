# 00 — Project Overview & System Context

---

## What This System Does

This is an **AI-powered SDLC document generation backend**. A user uploads a Business Requirements Document (BRD), selects output types and templates, and the system automatically generates fully formatted SDLC documents using a multi-phase AI pipeline.

### One-Line Summary
> Upload BRD → choose templates → system reads, understands, and writes your SDLC documents.

---

## The Three Output Documents

| Code | Full Name | Output | Primary Consumer |
|------|-----------|--------|-----------------|
| **PDD** | Project Definition Document | `.docx` | Project managers, sponsors |
| **SDD** | Software Design Document | `.docx` | Architects, senior devs |
| **UAT** | User Acceptance Testing Plan | `.xlsx` | QA teams, business analysts |

---

## End-to-End User Journey

```
1. User uploads BRD PDF or DOCX
       ↓
2. User selects: PDD + SDD + UAT (any combination)
       ↓
3. User selects a template per type:
   - Inbuilt (professional, ships with app)
   - Custom (user uploads their own DOCX or XLSX)
       ↓
4. User clicks "Generate"
   → Frontend makes 3 API calls → 3 workflow runs created in parallel
       ↓
5. Each workflow run independently executes 8 phases
       ↓
6. Frontend shows live progress (SSE events)
       ↓
7. User downloads PDD.docx + SDD.docx + UAT.xlsx
```

---

## System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                          │
│  Upload Page → Progress Page (SSE) → Output/Preview Page            │
│  docx-preview renders DOCX inline                                   │
│  Citation panel collapses/expands per section                       │
└────────────────────────────┬─────────────────────────────────────────┘
                             │ HTTP REST + SSE (EventSource)
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (Python 3.11)                    │
│                                                                      │
│  ┌─────────────────┐   ┌──────────────────┐   ┌──────────────────┐  │
│  │   API Layer     │   │  Services Layer  │   │  Workers Layer   │  │
│  │  6 route files  │──▶│  6 service files │──▶│  dispatcher.py   │  │
│  │  deps injection │   │  orchestration   │   │  background tasks│  │
│  └─────────────────┘   └────────┬─────────┘   └──────────────────┘  │
│                                 │                                    │
│  ┌──────────────────────────────▼─────────────────────────────────┐  │
│  │                    Domain Modules                              │  │
│  │  ingestion/ → template/ → retrieval/ → generation/            │  │
│  │  assembly/ → export/                                           │  │
│  └──────────────────────────────┬─────────────────────────────────┘  │
│                                 │                                    │
│  ┌──────────────────────────────▼─────────────────────────────────┐  │
│  │              Infrastructure + Repositories                     │  │
│  │  sk_adapter / search_client / doc_intelligence                 │  │
│  │  4 JSON-file repository classes                                │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    External Services                                 │
│  Azure OpenAI (GPT-5 + GPT-5-mini + text-embedding-3-large)         │
│  Azure AI Search (hybrid vector+keyword, single shared index)        │
│  Azure Document Intelligence (prebuilt-layout model)                │
│  Kroki Docker (localhost:8000) — PlantUML + Mermaid → PNG           │
└──────────────────────────────────────────────────────────────────────┘
```

---

## The 8-Phase Pipeline (Per Workflow Run)

Each workflow run is one document type (PDD or SDD or UAT). It runs all 8 phases sequentially.

```
PHASE 1 — INPUT_PREPARATION
  Purpose: Initialize state. Link document_id + template_id to this run.
  Duration: <1s | Cost: $0

PHASE 2 — INGESTION
  Purpose: Convert BRD → chunks in Azure AI Search (ready for retrieval).
  Sub-stages: DOCX→PDF → Doc Intelligence parse → hybrid chunk → embed + index
  Duration: 30–90s | Cost: ~$0.01–0.05 (embedding only)

PHASE 3 — TEMPLATE_PREPARATION
  Purpose: Confirm section plan + style map are ready from the template.
  For inbuilt: load hardcoded definitions. For custom: verify compile completed.
  Duration: ~1s | Cost: $0

PHASE 4 — SECTION_PLANNING
  Purpose: Finalize execution order, initialize section progress tracking counters.
  Duration: ~0.5s | Cost: $0

PHASE 5 — RETRIEVAL
  Purpose: For every section, run hybrid search to get the most relevant BRD chunks.
  All sections searched in parallel. Evidence packaged with citation metadata.
  Duration: 10–30s | Cost: ~$0.001

PHASE 6 — GENERATION
  Purpose: AI generates content for each section using retrieved evidence.
  Parallel waves (independent sections run together, dependents wait).
  Text → GPT-5-mini | Tables → GPT-5-mini | Diagrams → GPT-5 + Kroki
  Diagram self-correction: 3 PlantUML attempts + 3 Mermaid fallback = 6 max
  Duration: 60–180s | Cost: ~$0.10–1.00 (dominant cost)

PHASE 7 — ASSEMBLY_VALIDATION
  Purpose: Merge all generated sections into one ordered AssembledDocument.
  Attach citation metadata per section.
  Duration: ~1s | Cost: $0

PHASE 8 — RENDER_EXPORT
  Purpose: Convert AssembledDocument to the final file.
  PDD/SDD → DOCX (built fresh or filled into custom template)
  UAT → XLSX (filled into custom template or default workbook)
  Duration: 5–15s | Cost: $0
```

---

## Concurrency Model

```
User selects PDD + SDD + UAT
→ Frontend POSTs 3 separate /workflow-runs requests
→ 3 workflow runs dispatched as 3 parallel background tasks
→ wf-001 (PDD) + wf-002 (SDD) + wf-003 (UAT) all run simultaneously

Within one workflow run:
→ Phase 5 RETRIEVAL: all sections retrieved in parallel (asyncio.gather)
→ Phase 6 GENERATION: parallel waves based on dependency graph
   Wave 1: all sections with no dependencies → run together
   Wave 2: sections whose wave-1 deps finished → run together
   Wave N: continues until all sections done
```

---

## Failure & Retry Strategy

```
Phase-level failure:
  → Auto-retry once (2s delay)
  → If second attempt fails → mark workflow FAILED
  → Partial results saved. Which phase failed is recorded.

Diagram generation failure (within Phase 6):
  → PlantUML attempt 1 → fail → self-correction → attempt 2 → attempt 3
  → Switch to Mermaid → attempt 1 → correction → attempt 2 → attempt 3
  → 6 total attempts exhausted:
     section.content = "[Diagram could not be generated]"
     workflow CONTINUES — diagram failure is non-blocking

Section generation failure:
  → GenerationResult recorded with error flag
  → Other sections unaffected
  → Assembler skips failed sections
```

---

## Key Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Metadata storage | Local JSON files (one per record) | Simple, zero-dependency, readable |
| File storage | Local filesystem | No Blob Storage needed for local dev |
| Vector store | Azure AI Search | Hybrid search capability (vector + BM25) |
| LLM client | Semantic Kernel → Azure OpenAI | Unified adapter, SK handles retries |
| Diagram rendering | Kroki (Docker) | No Java, supports PlantUML + Mermaid |
| Citations in output | Preview UI only — DOCX is citation-free | Clean professional documents |
| Template system | Inbuilt + Custom → same SectionDefinition schema | Unified downstream pipeline |
| SSE | Primary progress mechanism, polling as fallback | Real-time UX |
| UAT format | XLSX (Excel) | Standard for test management teams |

---

## Data Persistence Layout

```
storage/
├── documents/      ← uploaded BRDs (binary files + JSON metadata)
├── templates/      ← uploaded custom templates + compiled preview artifacts
├── workflows/      ← one JSON file per workflow run (full state machine)
├── outputs/        ← generated DOCX/XLSX files + JSON metadata
├── diagrams/       ← rendered PNG diagrams per workflow run
└── logs/           ← structured log files + observability JSONL per workflow
```

All metadata is stored as individual `.json` files. No database. Inspectable with any text editor.

---

## SSE Event Catalog

Every event emitted carries: `type`, `workflow_run_id`, `timestamp`, plus event-specific fields.

```
workflow.started              → doc_type
workflow.completed            → output_id, total_cost_usd
workflow.failed               → error

phase.started                 → phase
phase.completed               → phase, duration_ms
phase.failed                  → phase, error, retrying (bool)

section.generation.started    → section_id, title, output_type
section.generation.completed  → section_id, title, status, cost_usd

ingestion.parse.completed     → pages, language
ingestion.chunk.completed     → chunk_count
ingestion.index.completed     → indexed_count, embedding_cost_usd

output.ready                  → output_id, format
```
