"""Shared foundation layer for the AI SDLC backend.

The ``core`` package is the bedrock of the application. Modules here may be
imported by **every** other layer (``api``, ``services``, ``repositories``,
``modules``, ``infrastructure``, ``workers``) but ``core`` itself must not
import upward into any of those layers. This rule keeps the dependency graph
acyclic and lets us reason about startup, configuration, and IDs without
worrying about side effects from business logic.

Modules
-------
- ``config``       — Pydantic ``Settings`` (env-driven), storage paths.
- ``constants``    — Enums, phase weights, LLM routing/pricing tables.
- ``exceptions``   — Domain exception hierarchy (mapped to HTTP in ``main``).
- ``ids``          — Type-prefixed IDs and ISO-8601 UTC timestamps.
- ``logging``      — Console + per-workflow file logging helpers.
- ``response``     — Standard JSON envelope helpers used by API routes.
- ``hosting``      — Production lifespan checks (strict-mode, storage probe).
- ``token_count``  — Token counting via tiktoken with whitespace fallback.

See ``docs/ARCHITECTURE.md`` for the catalog entry.
"""
