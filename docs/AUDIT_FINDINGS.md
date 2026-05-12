# Codebase audit findings (2026-05-12)

Scope: general inventory with release and security signals. Automated checks plus targeted config and dependency review.

## Commands executed

| Check | Result |
|--------|--------|
| `backend`: `python -m pytest -q --tb=no` | **Pass** (exit 0), ~54s; **2 skipped** (conditional Azure-related tests) |
| `frontend`: `npm run build` (`tsc && vite build`) | **Pass** |
| `frontend`: `npm test` (`vitest run`) | **Pass** (4 tests, 2 files) |
| Secret-pattern grep (`api_key`/`secret`/`password` literals in app code) | Only test doubles in `test_phase4_infrastructure.py` |

## Severity summary

| Severity | Count | Meaning |
|----------|-------|---------|
| P0 | 0 | No blocker observed from tests/build or quick security grep |
| P1 | 3 | Fix or explicitly accept before production |
| P2 | 4 | Hygiene, docs, or hardening backlog |

---

## P1 — release / security / correctness

1. **Production configuration defaults (`.env.example` vs runtime)**  
   Example file documents `CORS_ORIGINS=*`, `APP_DEBUG=true`, and permissive dev posture. For release, operators must set explicit origins, `APP_DEBUG=false` in production, and align Azure deployment names with the account. This is expected for a demo template but is **release-critical** if copied verbatim.

2. **`.env.example` drift from `core/config.py` defaults** *(remediated 2026-05-12)*  
   `backend/.env.example` now matches `Settings` defaults for Azure deployment env vars and documents that production values must match the Azure portal. Header and template fidelity knobs are listed with code-default values; operators should still override deployments per resource.

3. **Kroki HTTP client trust boundary** *(partially mitigated in code, 2026-05-12)*  
   `KrokiRenderer` still posts to configured `KROKI_URL`; misconfiguration remains an operational risk. ``core.kroki_url.validate_kroki_base_url`` and ``Settings`` validation now reject non-HTTP(S) schemes, missing host, userinfo, query/fragment, and a small metadata host blocklist. Network policy and a dedicated sidecar remain required for production.

---

## P2 — hygiene and documentation

1. **Template fidelity / chunking env knobs** *(partially remediated 2026-05-12)*  
   `backend/.env.example` now lists `template_*` and `header_*` defaults aligned with `Settings`. Operators should still read `docs/TEMPLATE_OPERATIONS.md` for semantics and production overrides (especially under strict release profile).

2. **Health surface**  
   Health responses include `kroki_url` (see `api/routes/health.py`). Low sensitivity but slightly increases reconnaissance surface; acceptable for internal ops, optional to redact in public deployments.

3. **Repository cleanliness**  
   Git status previously showed many untracked `__pycache__` / `.pytest_cache` paths. `.gitignore` already excludes them; ensure they are never added (`git add` scope, fresh clones). Prefer `git clean` / not staging build artifacts.

4. **Local shell profile noise**  
   PowerShell profile references missing `oh-my-posh.exe`, which pollutes every command log but does not affect project CI.

---

## Tests skipped (inventory)

Pytest reported **2 skips** in the full run (typical pattern: `@pytest.mark.skipif` when Azure credentials or live services are absent). Review `backend/tests/test_phase4_infrastructure.py` and any other `skipif` markers for CI policy: either supply secrets in secure CI or document these as optional integration tests.

---

## Suggested next actions (ordered)

1. ~~Reconcile `.env.example` with `Settings`~~ *(done 2026-05-12)*  
2. ~~Extend `docs/RELEASE_OPERATIONS.md` with CORS / Kroki / Azure deployment guidance~~ *(done 2026-05-12)*  
3. In CI, run the same three commands as this audit on every merge.  
4. ~~Optionally add Kroki URL validation~~ *(basic validation added 2026-05-12; extend with host allowlists if needed.)*

---

## Sign-off criteria (for “audit complete”)

- [x] Backend pytest green  
- [x] Frontend build and vitest green  
- [x] P0/P1/P2 findings recorded (this document)  
- [ ] Product owner acknowledges P1 items for any production target  
