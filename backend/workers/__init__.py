"""Async background task dispatch helpers.

Currently only :mod:`workers.dispatcher` lives here. It abstracts over
two execution modes:

- Inside an HTTP request, scheduled via ``fastapi.BackgroundTasks`` (so
  the work runs after the response is flushed).
- Outside an HTTP request (tests, scripts), scheduled directly on the
  running event loop.

Either path is wrapped in a guard that swallows and logs exceptions so
a failing background task cannot crash the parent process.
"""
