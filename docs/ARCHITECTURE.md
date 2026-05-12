# Architecture

Consolidated architecture reference (replaces the former numbered overview/structure/stack/model docs).

## Purpose
- Provide one place to understand system shape, runtime dependencies, and core data contracts.

## Inputs
- Backend layer design and module boundaries.
- Frontend to backend interaction model.
- Runtime dependency/configuration surface.

## Outputs
- End-to-end system mental model.
- Clear ownership boundaries for implementation.
- Canonical model of persisted entities and key schemas.

## Failure Modes
- Architecture drift can create wrong assumptions during implementation.
- Missing dependency/config details can break setup or deployments.
- Schema misunderstandings can cause API/storage regressions.

## 1) System Overview

The platform generates SDLC deliverables from a BRD:
- `PDD` (`.docx`)
- `SDD` (`.docx`)
- `UAT` (`.xlsx`)

User journey:
1. Upload BRD.
2. Select output types and templates.
3. Start workflow runs.
4. Track progress via SSE/status.
5. Download generated outputs.

## 2) Layered Backend Structure

- `main.py`: app composition, middleware, exception handlers, startup checks.
- `api/`: HTTP + SSE route layer.
- `services/`: orchestration and workflow execution coordination.
- `modules/`: domain logic (ingestion/template/retrieval/generation/assembly/export/observability).
- `repositories/`: JSON-file persistence.
- `infrastructure/`: Azure adapters (OpenAI/Search/Document Intelligence).
- `workers/`: background task dispatch.

Import boundary rule (high level):
- API -> services only
- modules do not import API/services
- infrastructure/repositories remain adapter/persistence focused

## 3) Frontend Integration Shape

- React + Vite frontend calls REST endpoints under `/api`.
- Progress is SSE-first with polling fallback.
- Output view consumes assembled workflow data and output download endpoints.

## 4) Runtime Stack and External Dependencies

Core runtime:
- Python 3.11+
- FastAPI + Uvicorn
- React 18 + Vite + TypeScript

External services:
- Azure OpenAI
- Azure AI Search
- Azure Document Intelligence
- Kroki (diagram rendering)

Storage:
- Local filesystem by default (JSON metadata + binary artifacts).
- Optional Azure Blob backend via configuration.

## 5) Key Persisted Models

- `DocumentRecord`: uploaded BRD metadata.
- `TemplateRecord`: custom template lifecycle and compiled artifacts.
- `WorkflowRecord`: full pipeline state machine and observability summary.
- `OutputRecord`: generated file metadata and download information.

Shared template/generation schemas:
- `SectionDefinition`
- `StyleMap`
- retrieval and citation payload models
- generation result models

## 6) Architectural Invariants

- Responses follow the standard envelope for JSON endpoints.
- Workflow status transitions are explicit (`PENDING` -> `RUNNING` -> `COMPLETED|FAILED`).
- File outputs and workflow state are persisted under storage root.
- Template source (inbuilt/custom) converges to a unified section schema.

## 7) Related Docs

- API contracts: [`API.md`](API.md)
- Pipeline internals and template/generation details: [`PIPELINE.md`](PIPELINE.md)
- Rules and release/run operations: [`OPERATIONS.md`](OPERATIONS.md), [`TEMPLATE_OPERATIONS.md`](TEMPLATE_OPERATIONS.md), [`RELEASE_OPERATIONS.md`](RELEASE_OPERATIONS.md)
