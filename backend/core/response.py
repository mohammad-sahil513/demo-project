"""Standard JSON envelope helpers used by every API endpoint.

Contract (must match the frontend Axios interceptor in
``frontend/src/api/client.ts``):

```
{
  "success": <bool>,
  "message": <str>,
  "data":    <object | array | null>,
  "errors":  [{"code": <str>, "detail": <str>}, ...],
  "meta":    { ... }
}
```

If you ever need to change this shape, update both the backend helpers and
the frontend interceptor in the same commit — they're treated as a single
public contract.
"""

from __future__ import annotations

from fastapi.responses import JSONResponse


def success_response(
    data: object,
    message: str = "Success",
    meta: dict[str, object] | None = None,
    status_code: int = 200,
) -> JSONResponse:
    """Build a 200 (default) response with the standard envelope.

    Parameters
    ----------
    data:
        Payload — typically a serialized Pydantic model or a dict.
    message:
        Human-readable explanation; logged by the UI in some flows.
    meta:
        Optional metadata bag (pagination, counts, debug breadcrumbs).
    status_code:
        Override only when a non-200 success is appropriate (e.g. 202).
    """
    payload = {
        "success": True,
        "message": message,
        "data": data,
        # ``errors`` is always present (empty list) so callers can iterate
        # without null-checks.
        "errors": [],
        "meta": meta or {},
    }
    return JSONResponse(content=payload, status_code=status_code)


def created_response(
    data: object,
    message: str = "Created",
    meta: dict[str, object] | None = None,
) -> JSONResponse:
    """Convenience for ``POST`` handlers that materialize a new resource."""
    return success_response(data=data, message=message, meta=meta, status_code=201)


def error_response(
    message: str,
    errors: list[dict[str, object]] | None = None,
    status_code: int = 400,
    meta: dict[str, object] | None = None,
) -> JSONResponse:
    """Build an error envelope. ``data`` is ``None`` by contract.

    Used by the exception handlers in :mod:`main` and any route that wants to
    return a structured error without raising.
    """
    payload = {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors or [],
        "meta": meta or {},
    }
    return JSONResponse(content=payload, status_code=status_code)
