# Contributing Guide

This document defines the default contribution workflow for this repository.

## Before You Start

- Read [`README.md`](README.md) for setup and environment expectations.
- Use [`docs/README.md`](docs/README.md) for the documentation reading path.
- Follow backend layering and coding rules in [`docs/OPERATIONS.md`](docs/OPERATIONS.md).

## Branch and Commit Workflow

- Create feature branches from your active integration branch.
- Recommended branch naming:
  - `feat/<short-topic>`
  - `fix/<short-topic>`
  - `docs/<short-topic>`
  - `chore/<short-topic>`
- Keep commits focused and reviewable. Prefer small logical steps over one large commit.
- Use clear commit messages that explain intent and impact.

## Pull Request Expectations

Each PR should include:

- Clear summary of what changed and why.
- Impacted areas (backend, frontend, docs, scripts).
- Validation notes (what commands were run and results).
- Any known trade-offs or follow-up tasks.

If you change behavior, include a short test plan in the PR description.

## Minimum Local Quality Gates

Run relevant checks before opening a PR.

### Backend

```bash
cd backend
python -m pytest -q
```

### Frontend

```bash
cd frontend
npm test
```

Optional build verification for release-sensitive changes:

```bash
cd frontend
npm run build
```

## Documentation Update Policy

Update docs in the same PR whenever you change:

- API contracts -> update [`docs/API.md`](docs/API.md).
- Pipeline behavior -> update [`docs/PIPELINE.md`](docs/PIPELINE.md).
- Module/file responsibilities -> update [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
- Setup/runtime scripts -> update [`scripts/README.md`](scripts/README.md) and relevant README files.
- Frontend routing/state/API flow -> update [`frontend/README.md`](frontend/README.md).

## Code Review Focus Areas

Reviewers should prioritize:

- Layer boundaries and import rules (no cross-layer violations).
- API response contract consistency (`success/message/data/errors/meta` envelope behavior).
- Workflow phase transitions, retries, and failure handling.
- Observability and SSE event integrity for workflow progress.
- Template fidelity guarantees for DOCX/XLSX exports.

## Definition of Done

A change is done when:

- Feature/fix works end-to-end in local flow.
- Relevant tests pass locally.
- New behavior is documented in the right doc file(s).
- PR includes clear validation evidence for reviewers.
