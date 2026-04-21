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
