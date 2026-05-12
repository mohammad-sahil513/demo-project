# Handover Documentation

This document is the detailed handover package for engineers taking ownership of this repository.

## Purpose
- Provide a practical transfer-of-ownership guide for development, debugging, release, and operations.

## Inputs
- Current repository state and architecture docs.
- Runtime dependencies and environment variables.
- API/pipeline contracts and operational runbooks.

## Outputs
- Fast onboarding for new contributors.
- Clear execution and troubleshooting paths.
- Reduced risk during maintenance and releases.

## Failure Modes
- Missing environment setup blocks local execution.
- Contract misunderstanding causes frontend/backend integration bugs.
- Incomplete release checks cause avoidable production incidents.

## 1) What This System Is

AI-powered SDLC document generation platform:
- Input: BRD file upload (PDF/DOCX).
- Processing: workflow pipeline with retrieval + generation.
- Output: `PDD.docx`, `SDD.docx`, `UAT.xlsx`.

Key workflow characteristics:
- One workflow run per selected deliverable type.
- Parallel run orchestration (PDD/SDD/UAT can run together).
- SSE progress stream with polling fallback.

## 2) Repository Layout (Operational View)

- `backend/` - FastAPI backend, workflow execution, storage/repository logic, Azure integrations.
- `frontend/` - React/Vite UI, API client integration, progress/output pages.
- `docs/` - grouped architecture/API/pipeline/operations docs.
- `scripts/` - setup and local dependency bootstrap scripts.

Primary docs to read in order:
1. `docs/ARCHITECTURE.md`
2. `docs/API.md`
3. `docs/PIPELINE.md`
4. `docs/OPERATIONS.md`
5. `docs/TEMPLATE_OPERATIONS.md`
6. `docs/RELEASE_OPERATIONS.md`

## 3) Local Development Setup

## Purpose
- Bring backend and frontend up in a reproducible local environment.

## Inputs
- Python 3.11+
- Node.js 18+
- Docker Desktop
- Repository checkout

## Outputs
- Running backend + frontend with working API and workflow flow.

## Failure Modes
- Missing Docker/Python/Node tooling.
- Invalid `.env` values for backend or frontend.
- Missing cloud credentials for non-local behaviors.

### Backend setup

```bash
cd backend
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend setup

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

### One-command infra/bootstrap path

From repo root:

```powershell
./scripts/init-setup.ps1 -VerboseSkip
```

Use `scripts/README.md` for script-by-script behavior and flags.

## 4) Environment and Configuration Handover

Critical backend variables to verify before first run:
- `APP_ENV`, `APP_DEBUG`
- `STORAGE_ROOT`, `STORAGE_BACKEND`
- `KROKI_URL`
- `AZURE_OPENAI_*`
- `AZURE_SEARCH_*`
- `AZURE_DOCUMENT_INTELLIGENCE_*`
- Template strictness flags (`TEMPLATE_*`) in production-like environments

Critical frontend variable:
- `VITE_API_BASE` (default `/api` in local proxy mode)

Production-like posture:
- Use strict template/export settings documented in `docs/TEMPLATE_OPERATIONS.md`.

## 5) API Handover (What Consumers Depend On)

Primary endpoint groups:
- Health/readiness: `/api/health`, `/api/ready`
- Documents: `/api/documents/*`
- Templates: `/api/templates/*`
- Workflows: `/api/workflow-runs/*`
- Outputs: `/api/outputs/*`

Frontend-critical workflow status fields:
- `workflow_run_id`
- `status`
- `current_phase`
- `overall_progress_percent`
- `current_step_label`
- `output_id`

SSE endpoint:
- `GET /api/workflow-runs/{workflow_run_id}/events`

Full contract: `docs/API.md`.

## 6) Pipeline Handover (How It Actually Runs)

Workflow phases:
1. `INPUT_PREPARATION`
2. `INGESTION`
3. `TEMPLATE_PREPARATION`
4. `SECTION_PLANNING`
5. `RETRIEVAL`
6. `GENERATION`
7. `ASSEMBLY_VALIDATION`
8. `RENDER_EXPORT`

Important behaviors:
- Phase wrapper retries once on failure.
- Generation runs in dependency-aware waves.
- Diagram generation has multi-step fallback behavior.
- Export mode/path varies by template source and flags.

Detailed behavior: `docs/PIPELINE.md`.

## 7) Template Handover (High-Risk Area)

Template source types:
- Inbuilt templates
- Custom uploaded templates

Operational priorities:
- Stable placeholder strategy
- Correct section bindings
- Strict fidelity checks in production
- UAT observability keys monitored

All template policy/runbook content is consolidated in:
- `docs/TEMPLATE_OPERATIONS.md`

## 8) Testing and Validation Handover

### Backend

```bash
cd backend
python -m pytest -q
```

### Frontend

```bash
cd frontend
npm test
npm run build
```

Smoke flow after deployment/local readiness:
1. Upload BRD
2. Select template(s)
3. Start workflow
4. Observe progress/SSE
5. Download outputs

## 9) Troubleshooting Playbook

### Backend does not start
- Validate `backend/.env` exists and values parse correctly.
- Verify Python venv and dependencies are installed.
- Check for storage path permission issues.

### `/api/ready` fails
- Check `failed_checks` payload fields.
- Verify storage writable and required cloud config.

### Workflow stuck/failing
- Inspect workflow diagnostics endpoint:
  - `/api/workflow-runs/{id}/diagnostics`
- Inspect logs under storage/logs.
- Verify external dependencies (Kroki/Azure services).

### Frontend progress not updating
- Check SSE connection in browser devtools.
- Validate fallback polling returns status payload.
- Confirm `workflow_run_id` is set and valid.

### Output generation issues
- Check template compile/binding status.
- Verify strict template flags and validation warnings.
- Validate diagram renderer availability (Kroki).

## 10) Release and Ownership Checklist

Before release:
- Follow `docs/RELEASE_OPERATIONS.md`.
- Ensure required tests and smoke checks pass.
- Confirm environment variables are complete in target env.

When handing over to another engineer/team:
- Share this document + `docs/README.md`.
- Share known open issues and expected follow-ups.
- Confirm access to runtime services/secrets and CI pipelines.

## 11) Source of Truth Pointers

- Architecture and models: `docs/ARCHITECTURE.md`
- API contract: `docs/API.md`
- Pipeline behavior: `docs/PIPELINE.md`
- Engineering rules: `docs/OPERATIONS.md`
- Template operations: `docs/TEMPLATE_OPERATIONS.md`
- Release operations: `docs/RELEASE_OPERATIONS.md`
- Contribution workflow: `CONTRIBUTING.md`
