# Go-Live Release Checklist

Use this checklist before every production release cut.

## 1) Branch and artifact hygiene
- Work from a clean release branch with only intentional changes.
- Confirm runtime artifacts are excluded from git (`backend/storage`, `frontend/dist`, caches).
- Remove temporary debug files and local-only scripts from release scope.

## 2) Backend safety gates
- `APP_ENV` is `staging` or `production` in deployment config.
- Strict template flags are set for prod profile:
  - `TEMPLATE_DOCX_PLACEHOLDER_NATIVE_ENABLED=true`
  - `TEMPLATE_SECTION_BINDING_STRICT=true`
  - `TEMPLATE_FIDELITY_STRICT_ENABLED=true`
  - `TEMPLATE_SCHEMA_VALIDATION_BLOCKING=true`
  - `TEMPLATE_FIDELITY_MEDIA_INTEGRITY_BLOCKING=true`
  - `TEMPLATE_DOCX_LEGACY_EXPORT_ALLOWED=false`
  - `TEMPLATE_DOCX_REQUIRE_NATIVE_FOR_CUSTOM=true`
  - `APP_DEBUG=false`
- `/api/ready` returns `200` in target environment.
- `/api/health` returns `200`.

## 3) Dependency and test integrity
- Backend dependencies install cleanly from `backend/requirements.txt`.
- Run `pytest -q` and ensure all tests pass.
- Resolve or explicitly accept any warnings.

## 4) Frontend build and verification
- Run `npm run build` in `frontend`.
- Run `npm run test` in `frontend`.
- Review bundle output and watch for regressions in chunk size warnings.

## 5) CI and deployment checks
- GitHub CI workflow passes on the release commit.
- Required environment variables are present in target environment.
- Rollback plan is documented and accessible to on-call owner.

## 6) Post-deploy smoke checks
- Create one end-to-end workflow run and verify output generation.
- Verify warning/error telemetry for `workflow.failed` and export integrity paths.
- Confirm downloads and preview endpoints operate correctly.
