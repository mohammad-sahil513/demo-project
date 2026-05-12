# Setup Scripts Runbook

This folder contains repository-level PowerShell scripts used to bootstrap local dependencies safely.

All scripts are designed for reruns (idempotent behavior where possible): if a dependency is already healthy, scripts skip or no-op rather than rebuilding from scratch.

## Prerequisites

- Windows PowerShell
- Docker Desktop + Docker CLI in `PATH`
- Python installed and available as `python`
- Repository root as current directory (`D:/demo-project`)

## Recommended Execution Order

1. `./scripts/init-setup.ps1` (preferred all-in-one path)
2. Use the individual scripts below only for targeted checks or recovery.

## Script Reference

### `init-setup.ps1`

Master setup script that orchestrates three phases:

1. Kroki Docker start + health check
2. Storage bootstrap (`backend/scripts/storage_setup.py`)
3. Azure Search index setup + schema validation

#### Usage

```powershell
./scripts/init-setup.ps1
```

Optional flags:

- `-SkipDocker` - skip Kroki Docker start/health.
- `-SkipStorage` - skip backend storage bootstrap.
- `-SkipIndex` - skip Azure Search index setup and validation.
- `-VerboseSkip` - print compact executed/skipped/failed summary.

Examples:

```powershell
# Docker already running; do storage + index only
./scripts/init-setup.ps1 -SkipDocker -VerboseSkip

# Validate only Docker/Kroki path
./scripts/init-setup.ps1 -SkipStorage -SkipIndex -VerboseSkip
```

#### Expected Success Signals

- Script prints `Initial setup workflow completed.`
- With `-VerboseSkip`, each step shows `Executed` or `Skipped`.

#### Common Failure Symptoms

- Docker command missing -> Docker CLI not installed or not in `PATH`.
- Python script failure in storage step -> check backend env in `backend/.env`.
- Index validation failure -> Azure Search endpoint/key/index configuration mismatch.

### `start-kroki.ps1`

Starts Docker Desktop if needed, then starts Kroki via `docker-compose.kroki.yml`.

#### Usage

```powershell
./scripts/start-kroki.ps1
./scripts/start-kroki.ps1 -HostPort 8001
```

#### Parameters

- `-HostPort` (default `8001`) - host port mapped to Kroki container port `8000`.

#### Expected Success Signals

- If already running: `Kroki is already healthy ... Skipping start.`
- Otherwise: `docker compose ... up -d` succeeds and `docker compose ... ps` shows running container.

#### Common Failure Symptoms

- Docker Desktop path not found -> install Docker Desktop.
- Docker engine does not become ready -> start Docker manually and rerun.
- Custom `HostPort` used without backend config update -> set `KROKI_URL` accordingly in `backend/.env`.

### `status-kroki.ps1`

Shows Kroki container status and performs a health check on `/health`.

#### Usage

```powershell
./scripts/status-kroki.ps1
./scripts/status-kroki.ps1 -HostPort 8001
```

#### Expected Success Signals

- `docker compose ... ps` shows service status.
- Health check prints `Kroki is healthy.`

#### Common Failure Symptoms

- Health check failed -> container not running, wrong port, or startup still in progress.

### `stop-kroki.ps1`

Stops and removes the Kroki compose stack.

#### Usage

```powershell
./scripts/stop-kroki.ps1
```

#### Expected Success Signals

- `docker compose ... down` exits successfully.

## Backend Setup Scripts (Called by init workflow)

Executed from `backend/` by `init-setup.ps1`:

- `python ./scripts/storage_setup.py`
- `python ./scripts/ai_search_index.py create-if-missing`
- `python ./scripts/validate_ai_search_index.py`

For details and additional commands (`list`, `recreate`, `delete-if-exists`), see [`../backend/README.md`](../backend/README.md).

## Troubleshooting Quick Checklist

- Confirm current path is repository root before running scripts.
- Ensure `backend/.env` exists (copy from `backend/.env.example` if needed).
- Verify Docker is installed, running, and accessible from PowerShell.
- Re-run `./scripts/init-setup.ps1 -VerboseSkip` to isolate the failing step quickly.
