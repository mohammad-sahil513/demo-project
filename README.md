# AI SDLC Demo Project

End-to-end document workflow system with a FastAPI backend and a React + Vite frontend.

The app supports:
- Document upload
- Template upload/selection (PDD / SDD / UAT)
- Workflow execution with progress and SSE updates
- Assembled output download

## Project Structure

- `backend/` FastAPI API, workflow orchestration, storage repositories, Azure integrations
- `frontend/` React UI (Vite + TypeScript + Tailwind)
- `docs/` phase checklists and implementation notes

## Handover and documentation

This codebase ships two layers of documentation that are intentionally
complementary:

- Architectural prose lives under `docs/`. Start with
  [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the
  high-level system overview and structure,
  [docs/API.md](docs/API.md) for the public contract, and
  [docs/PIPELINE.md](docs/PIPELINE.md) for workflow behavior.
  Operational guidance lives in `docs/OPERATIONS.md`,
  `docs/TEMPLATE_OPERATIONS.md`, and `docs/RELEASE_OPERATIONS.md`.
- Every Python module under `backend/` and every TypeScript / TSX file
  under `frontend/src/` carries a verbose top-of-file header describing
  its role, invariants, and key collaborators, plus JSDoc / docstrings
  on the public API. These in-code comments are the day-to-day map for
  implementers; the `docs/` prose is the source of truth when an
  in-code comment and a `docs/` section disagree.

## Requirements

- Python 3.11+
- Node.js 18+
- npm 9+

## Local Development

### 1) Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend base URL: `http://127.0.0.1:8000`

### 1.1) Initial setup automation

Run full first-time setup (Docker + storage + Azure index):

```powershell
.\scripts\init-setup.ps1
```

Show compact skip/execution summary:

```powershell
.\scripts\init-setup.ps1 -VerboseSkip
```

Skip selected phases if needed:

```powershell
.\scripts\init-setup.ps1 -SkipDocker
.\scripts\init-setup.ps1 -SkipStorage
.\scripts\init-setup.ps1 -SkipIndex
```

Common combinations:

```powershell
# Docker already running, do storage + index only
.\scripts\init-setup.ps1 -SkipDocker -VerboseSkip

# Only verify/prepare Docker (Kroki)
.\scripts\init-setup.ps1 -SkipStorage -SkipIndex -VerboseSkip
```

Individual setup scripts:

- Kroki start: `.\scripts\start-kroki.ps1`
- Kroki status/health: `.\scripts\status-kroki.ps1`
- Kroki stop: `.\scripts\stop-kroki.ps1`
- Storage bootstrap: `cd backend && python .\scripts\storage_setup.py`
- Azure index list: `cd backend && python .\scripts\ai_search_index.py list`
- Azure index create if missing: `cd backend && python .\scripts\ai_search_index.py create-if-missing`
- Azure index recreate: `cd backend && python .\scripts\ai_search_index.py recreate`
- Azure index delete if exists: `cd backend && python .\scripts\ai_search_index.py delete-if-exists`
- Azure index schema validate: `cd backend && python .\scripts\validate_ai_search_index.py`

All setup scripts are safe to re-run. When setup is already ready, they skip or no-op where applicable.

Quick troubleshooting:
- If Docker step fails, ensure Docker Desktop and Docker CLI are installed and available in `PATH`.
- If blob setup fails, confirm `STORAGE_BACKEND=blob` and blob env vars are set in `backend/.env`.
- If index setup fails, verify Azure Search endpoint/key/index values in `backend/.env`.

### 2) Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend dev URL: `http://localhost:3000`

In dev, Vite proxies `/api` to backend (`BACKEND_ORIGIN` or `VITE_DEV_PROXY_TARGET`, default `http://127.0.0.1:8000`).

## Environment Configuration

### Backend (`backend/.env`)

Important variables:
- `APP_ENV` (`development` or `production`)
- `APP_DEBUG` (`false` in production)
- `STORAGE_ROOT` (must be persistent and writable in production)
- `STORAGE_BACKEND` (`local` or `blob`)
- Blob-mode variables (used when `STORAGE_BACKEND=blob`):
  - `AZURE_STORAGE_CONNECTION_STRING` or `AZURE_STORAGE_ACCOUNT_URL`
  - `AZURE_STORAGE_CONTAINER`
- `API_PREFIX` (default `/api`)
- `CORS_ORIGINS` (comma-separated frontend origins; use `*` for local dev only)
- `KROKI_URL`
- Azure settings:
  - `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`
  - `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_API_KEY`, `AZURE_SEARCH_INDEX_NAME`
  - `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`, `AZURE_DOCUMENT_INTELLIGENCE_KEY`

### Frontend (`frontend/.env`)

- `VITE_API_BASE=/api` for same-origin/proxied dev
- For cross-origin production deployment, set full backend path at build time, for example:
  - `VITE_API_BASE=https://your-api.azurewebsites.net/api`

SSE and output downloads use the same API base.

## API Highlights

- `GET /api/health` basic liveness
- `GET /api/ready` readiness with integration flags and `storage_writable`
- `POST /api/documents/upload`
- `POST /api/templates/upload`
- `POST /api/workflow-runs`
- `GET /api/workflow-runs/{workflow_run_id}/events` (SSE)
- `GET /api/outputs/{output_id}/download`

## Production Notes

- Persistent storage is required for uploaded files, workflow JSON, and outputs.
- Workflow execution currently uses in-process FastAPI background tasks.
- On restart, interrupted `RUNNING` workflows are reconciled to `FAILED` at startup.
- Restrict `CORS_ORIGINS` to trusted frontend domains in production.

## Testing

Backend:

```bash
cd backend
python -m pytest -q
```

Frontend:

```bash
cd frontend
npm test
```

## Live Smoke Test Checklist

1. Deploy backend and frontend with production env values.
2. Verify:
   - `GET /api/health` returns success
   - `GET /api/ready` reports `storage_writable=true`
3. Upload one document.
4. Select/upload one template.
5. Start a workflow run.
6. Confirm progress/SSE updates and final output download.
