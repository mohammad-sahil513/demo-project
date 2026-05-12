"""Strip internal or technical leakage from deliverable markdown (template-agnostic).

This is the final pass run by :func:`modules.assembly.normalizer.normalize_section_content`
in final-mode exports. It catches three classes of leak:

- Diagram error prose (``"Diagram generation failed: ..."``).
- Fallback diagram notices (``"Fallback diagram used because ..."``).
- Transport-layer noise (Kroki errors, HTTP statuses, tracebacks).

Replacing diagram errors with :data:`NEUTRAL_DIAGRAM_PLACEHOLDER` preserves
the section's visual rhythm without leaking implementation details to the
final reader.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Neutral copy when diagram pipeline could not produce a figure (no API/tool text in body).
NEUTRAL_DIAGRAM_PLACEHOLDER = (
    "*(Diagram placeholder — a renderable figure was not produced. "
    "Details are not shown in the exported document.)*"
)

_DIAGRAM_FAIL_LINE = re.compile(
    r"^\s*_?\s*Diagram generation failed:\s*.+_?\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)
_FALLBACK_DIAGRAM_LINE = re.compile(
    r"^\s*_?\s*Fallback diagram used because model generation failed\.?\s*_?\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)
_KROKI_OR_HTTP_LINE = re.compile(
    r"^\s*(kroki|http/\d|connection refused|timeout|traceback|generationexception)\b",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class HygieneResult:
    """Output of :func:`sanitize_deliverable_markdown` — cleaned text + applied-rule notes."""

    text: str
    notes: list[str]


def sanitize_deliverable_markdown(text: str) -> HygieneResult:
    """Remove known internal diagram messages and obvious transport-layer lines.

    Intended for final-mode exports; idempotent for already-clean text. Any
    rule that fires appends a short identifier to ``HygieneResult.notes``
    so callers can include the audit trail in their warnings.
    """
    if not (text or "").strip():
        return HygieneResult(text=(text or "").strip(), notes=[])

    notes: list[str] = []
    cleaned = text

    if _DIAGRAM_FAIL_LINE.search(cleaned):
        cleaned = _DIAGRAM_FAIL_LINE.sub(NEUTRAL_DIAGRAM_PLACEHOLDER, cleaned).strip()
        notes.append("diagram_failure_prose_sanitized")

    if _FALLBACK_DIAGRAM_LINE.search(cleaned):
        cleaned = _FALLBACK_DIAGRAM_LINE.sub("", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
        notes.append("fallback_diagram_notice_removed")

    lines_out: list[str] = []
    removed_transport = False
    for line in cleaned.splitlines():
        if _KROKI_OR_HTTP_LINE.search(line):
            removed_transport = True
            continue
        lines_out.append(line)

    if removed_transport:
        notes.append("transport_diagnostic_lines_removed")

    out = "\n".join(lines_out).strip()
    return HygieneResult(text=out, notes=notes)
