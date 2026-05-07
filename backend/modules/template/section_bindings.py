"""Resolve section plan to placeholder IDs (hybrid: explicit map + exact section_id match)."""

from __future__ import annotations

from typing import Any


def _coerce_binding_value(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        s = value.strip()
        return [s] if s else []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            s = str(item).strip()
            if s:
                out.append(s)
        return out
    return []


def merge_explicit_bindings(raw: dict[str, Any] | None) -> dict[str, list[str]]:
    """Normalize section_placeholder_bindings dict to section_id -> [placeholder_id, ...]."""
    if not raw:
        return {}
    out: dict[str, list[str]] = {}
    for sid, val in raw.items():
        key = str(sid).strip()
        if not key:
            continue
        ids = _coerce_binding_value(val)
        if ids:
            out[key] = ids
    return out


def resolve_section_placeholder_bindings(
    *,
    section_plan: list[dict[str, object]],
    placeholder_schema: dict[str, object],
) -> tuple[dict[str, list[str]], list[dict[str, object]], list[dict[str, object]]]:
    """
    Returns (bindings, errors, warnings).

    Resolution order per section_id:
    1. Explicit entry in schema['section_placeholder_bindings']
    2. Exact match: a placeholder with placeholder_id == section_id
    """
    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []

    raw_placeholders = placeholder_schema.get("placeholders")
    if not isinstance(raw_placeholders, list):
        raw_placeholders = []

    known_ids: set[str] = set()
    by_id: dict[str, dict[str, object]] = {}
    for item in raw_placeholders:
        if not isinstance(item, dict):
            continue
        pid = str(item.get("placeholder_id") or "").strip()
        if pid:
            known_ids.add(pid)
            by_id[pid] = item

    explicit = merge_explicit_bindings(
        placeholder_schema.get("section_placeholder_bindings")
        if isinstance(placeholder_schema.get("section_placeholder_bindings"), dict)
        else None,
    )

    bindings: dict[str, list[str]] = {}
    used_placeholders: set[str] = set()

    for raw in section_plan:
        sid = str(raw.get("section_id") or "").strip()
        if not sid:
            continue

        if sid in explicit:
            pids = list(explicit[sid])
            for pid in pids:
                if pid not in known_ids:
                    errors.append(
                        {
                            "code": "binding_unknown_placeholder",
                            "message": f"Binding references unknown placeholder_id: {pid}",
                            "section_id": sid,
                            "placeholder_id": pid,
                            "level": "error",
                        }
                    )
            if pids and all(p in known_ids for p in pids):
                bindings[sid] = pids
                used_placeholders.update(pids)
            continue

        if sid in known_ids:
            bindings[sid] = [sid]
            used_placeholders.add(sid)
            continue

        errors.append(
            {
                "code": "section_placeholder_unbound",
                "message": (
                    f"No placeholder binding for section {sid!r}: "
                    "add section_placeholder_bindings or use a placeholder_id equal to section_id."
                ),
                "section_id": sid,
                "level": "error",
            }
        )

    unused = known_ids - used_placeholders
    for pid in sorted(unused):
        warnings.append(
            {
                "code": "placeholder_unused",
                "message": f"Placeholder {pid!r} is not bound to any section in the current plan.",
                "placeholder_id": pid,
                "level": "warning",
            }
        )

    return bindings, errors, warnings
