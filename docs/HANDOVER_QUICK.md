# Handover Quick (Run + Setup Only)

Use this when you only need to get the project running locally in 10 minutes.

## 1) Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+
- Docker Desktop (running)

## 2) Clone + Open

```bash
git clone <repo-url>
cd demo-project
```

## 3) Backend Setup

```bash
cd backend
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend URL:
- `http://127.0.0.1:8000`

Health check:
- `GET http://127.0.0.1:8000/api/health`

## 4) Frontend Setup

Open a second terminal:

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend URL:
- `http://localhost:3000`

## 5) Optional One-Time Infra Bootstrap (Recommended)

From repo root:

```powershell
./scripts/init-setup.ps1 -VerboseSkip
```

This handles:
- Kroki startup/health
- storage setup
- Azure Search index setup/validation

## 6) Minimal Smoke Test

1. Open frontend at `http://localhost:3000`
2. Upload one BRD file
3. Select one template
4. Start workflow
5. Confirm progress updates and output download

## 7) If Something Fails

- Backend not starting: re-check `backend/.env` and Python venv activation.
- Frontend API errors: verify backend is running and `VITE_API_BASE=/api`.
- Diagram failures: verify Kroki is healthy (`./scripts/status-kroki.ps1`).
- Setup issues: run `./scripts/init-setup.ps1 -VerboseSkip` and inspect failed step.

## 8) Next Docs (Only If Needed)

- Full handover: `docs/HANDOVER.md`
- API contract: `docs/API.md`
- Pipeline behavior: `docs/PIPELINE.md`
