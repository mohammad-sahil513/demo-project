# Backend Runtime Policy

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
