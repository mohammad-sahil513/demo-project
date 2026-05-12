# Backend Runtime Policy

## In-code documentation conventions

Every Python module under `backend/` follows the same documentation shape, and every TypeScript / TSX file under `frontend/src/` follows the parallel JSDoc shape. These are the rules to apply when adding new files or expanding existing ones:

- Top-of-file module docstring (8–20 lines for non-trivial modules) describing the module's role, the public types it exposes, which layers it may import from, notable failure modes, and a one-line pointer to `docs/ARCHITECTURE.md` when applicable.
- Docstrings on every public function, class, and method using Args / Returns / Raises blocks where behavior is non-obvious. Pydantic and dataclass fields get a short comment describing semantics and validation expectations.
- Inline comments explain *why* (intent, trade-off, OOXML / XML quirk, retry constant, magic number) — never narrate *what* the next line does.
- `__init__.py` files describe the package role and what lives under it; tests open with a short scenario-matrix docstring naming the contract under test.
- Frontend files use the same shape via JSDoc: a top-of-file block summarizing the route / API surface / env vars, JSDoc on exported components and hooks with `@param` / `@returns`, and inline comments on interceptor / polling / SSE logic.

Match the prevailing style of neighboring files rather than introducing new conventions; expand a one-line docstring to the verbose standard rather than mixing styles inside a module.

## Environment Behavior Matrix

The workflow executor follows a strict environment policy for missing external dependencies.

- `local` / `development` / `dev`:
  - Ingestion/Retrieval/Generation can be skipped when dependencies are not configured.
  - Workflow keeps moving with explicit step labels that indicate local skip behavior.
- any other environment (for example `production`, `staging`):
  - Ingestion/Retrieval/Generation missing configuration is treated as a hard failure.
  - Workflow moves to `FAILED` with explicit error details.

## Template Compile Failure Contract

Custom template compilation failures are persisted (not deleted):

- `status = FAILED`
- `compile_error` contains the reason
- `section_plan = []`
- preview artifacts are cleared

This ensures stable API diagnostics and better supportability in production.

## Setup Scripts

Backend setup scripts (run from `backend/`):

- `python .\scripts\storage_setup.py`
  - Reads `STORAGE_BACKEND` from `.env`.
  - `local`: creates local storage directories under `STORAGE_ROOT`.
  - `blob`: validates blob config and ensures container exists.

- `python .\scripts\ai_search_index.py list`
- `python .\scripts\ai_search_index.py create-if-missing`
- `python .\scripts\ai_search_index.py delete-if-exists`
- `python .\scripts\ai_search_index.py recreate`
  - Azure Search index lifecycle manager using env-based endpoint/key/index.

- `python .\scripts\validate_ai_search_index.py`
  - Confirms live index schema matches backend expectations.

These setup scripts are idempotent. Re-running them is safe and will skip/no-op when resources are already present.

Repo-level PowerShell orchestration scripts (run from repository root):

- `.\scripts\init-setup.ps1` (master setup script)
- `.\scripts\start-kroki.ps1`, `.\scripts\status-kroki.ps1`, `.\scripts\stop-kroki.ps1`
