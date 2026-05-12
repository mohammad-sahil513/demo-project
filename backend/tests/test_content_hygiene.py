"""Content hygiene contract: strip diagram failure prose and fallback notices.

Protects the final deliverable surface from leaking internal error
messages (e.g. Kroki HTTP status lines, diagram fallback notices). Each
test asserts that the offending content is replaced with the neutral
placeholder and that the hygiene notes record the right reason code.
"""

from __future__ import annotations

from modules.assembly.content_hygiene import NEUTRAL_DIAGRAM_PLACEHOLDER, sanitize_deliverable_markdown


def test_sanitize_replaces_diagram_failure_line() -> None:
    raw = "_Diagram generation failed: HTTP 500 from Kroki._\n\nSome body."
    hy = sanitize_deliverable_markdown(raw)
    assert "Kroki" not in hy.text
    assert "HTTP" not in hy.text
    assert NEUTRAL_DIAGRAM_PLACEHOLDER in hy.text
    assert "diagram_failure_prose_sanitized" in hy.notes


def test_sanitize_removes_fallback_notice() -> None:
    raw = "Intro\n\n_Fallback diagram used because model generation failed._\n\nMore."
    hy = sanitize_deliverable_markdown(raw)
    assert "Fallback diagram" not in hy.text
    assert "fallback_diagram_notice_removed" in hy.notes
