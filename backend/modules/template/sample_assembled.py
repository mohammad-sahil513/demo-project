"""Build a minimal :class:`AssembledDocument` for template preview / fidelity probes.

Used by the template compile pipeline to run a sample export through the
same renderer that real workflows use — gives us an export-parity preview
file and lets the integrity checker (``docx_integrity``) run before a real
workflow runs against the template.

Each section is filled with a short ``[Preview sample - ...]`` blurb so
authors can visually confirm headings, ordering, and structure without
making the previews look like real content.
"""

from __future__ import annotations

from pathlib import Path

from modules.assembly.models import AssembledDocument, AssembledSection


def assembled_document_from_section_plan(
    *,
    template_type: str,
    filename: str,
    section_plan: list[dict[str, object]],
) -> AssembledDocument:
    title = Path(filename).stem or "Document"
    sections: list[AssembledSection] = []
    indexed = list(enumerate(section_plan))

    def sort_key(item: tuple[int, dict[str, object]]) -> tuple[int, int]:
        _, raw = item
        order = raw.get("execution_order")
        try:
            eo = int(order) if order is not None else 10**9
        except (TypeError, ValueError):
            eo = 10**9
        return (eo, item[0])

    for _, raw in sorted(indexed, key=sort_key):
        sid = str(raw.get("section_id") or "").strip()
        stitle = str(raw.get("title") or "Section").strip() or "Section"
        out_type = str(raw.get("output_type") or "text").strip().lower()
        if out_type not in {"text", "table", "diagram"}:
            out_type = "text"
        level = int(raw.get("level") or 1)
        sample = (
            f"[Preview sample — {stitle}] Placeholder body text. "
            "Final workflow output would replace this block under each heading."
        )
        sections.append(
            AssembledSection(
                section_id=sid or stitle,
                title=stitle,
                level=level,
                output_type=out_type,
                content=sample,
            )
        )

    return AssembledDocument(
        title=title,
        doc_type=template_type,
        sections=sections,
        export_mode="final",
    )
