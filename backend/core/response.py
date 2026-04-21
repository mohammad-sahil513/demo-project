"""Standard API response envelope helpers."""

from __future__ import annotations

from fastapi.responses import JSONResponse


def success_response(
    data: object,
    message: str = "Success",
    meta: dict[str, object] | None = None,
    status_code: int = 200,
) -> JSONResponse:
    payload = {
        "success": True,
        "message": message,
        "data": data,
        "errors": [],
        "meta": meta or {},
    }
    return JSONResponse(content=payload, status_code=status_code)


def created_response(
    data: object,
    message: str = "Created",
    meta: dict[str, object] | None = None,
) -> JSONResponse:
    return success_response(data=data, message=message, meta=meta, status_code=201)


def error_response(
    message: str,
    errors: list[dict[str, object]] | None = None,
    status_code: int = 400,
    meta: dict[str, object] | None = None,
) -> JSONResponse:
    payload = {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors or [],
        "meta": meta or {},
    }
    return JSONResponse(content=payload, status_code=status_code)
