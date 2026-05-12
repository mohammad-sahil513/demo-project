"""Merge section plan + generation results into a single ordered document.

The assembler is a deterministic, side-effect-free step: take the template's
section plan (already ordered by ``execution_order``) and the dict of
generation results keyed by ``section_id``, and produce an
:class:`AssembledDocument` ready for export.

Anything unexpected (missing generation result, missing diagram image,
content that needed normalization) is recorded in ``warnings`` rather than
raised — the workflow continues so the user gets a partial output and a
clear explanation of what's missing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from core.ids import utc_now_iso
from modules.assembly.models import AssembledDocument, AssembledSection
from modules.assembly.normalizer import normalize_section_content
from modules.generation.models import GenerationSectionResult
from modules.template.models import SectionDefinition


@dataclass(frozen=True, slots=True)
class AssemblyOutcome:
    """Return value of :meth:`DocumentAssembler.assemble` — document + warnings."""

    document: AssembledDocument
    warnings: list[dict[str, object]] = field(default_factory=list)


class DocumentAssembler:
    """Stateless assembler. Construct once per process; safe to reuse."""

    def assemble(
        self,
        *,
        document_filename: str,
        doc_type: str,
        section_plan: list[SectionDefinition],
        section_generation_results: dict[str, dict[str, object]],
        export_mode: str = "final",
    ) -> AssemblyOutcome:
        """Materialize an :class:`AssembledDocument` from plan + results."""
        # The section plan may have been re-ordered by an upstream filter;
        # re-sort to make this step independent of the input order.
        ordered = sorted(section_plan, key=lambda s: s.execution_order)
        stem = Path(document_filename).stem
        # Document title pattern is read by the UI list; do not change without
        # updating frontend label assumptions.
        title = f"{stem} — {doc_type}"

        sections: list[AssembledSection] = []
        warnings: list[dict[str, object]] = []
        ts = utc_now_iso()

        for idx, section in enumerate(ordered):
            raw = section_generation_results.get(section.section_id)
            if not raw:
                warnings.append(
                    {
                        "phase": "ASSEMBLY_VALIDATION",
                        "code": "missing_generation",
                        "section_id": section.section_id,
                        "title": section.title,
                        "message": f"No generation result for section {section.title!r}; section omitted from export.",
                        "at": ts,
                    },
                )
                continue

            row = GenerationSectionResult.model_validate(raw)

            child_titles = self._collect_immediate_or_nested_child_titles(
                ordered_sections=ordered,
                current_index=idx,
            )

            normalized = normalize_section_content(
                section_title=section.title,
                content=row.content or "",
                child_titles=child_titles,
                export_mode=export_mode,
            )

            if normalized.notes:
                warnings.append(
                    {
                        "phase": "ASSEMBLY_NORMALIZATION",
                        "code": "content_normalized",
                        "section_id": section.section_id,
                        "title": section.title,
                        "message": f"Normalized content for section {section.title!r}.",
                        "notes": normalized.notes,
                        "at": ts,
                    },
                )

            if row.output_type == "diagram" and not row.diagram_path:
                warnings.append(
                    {
                        "phase": "ASSEMBLY_VALIDATION",
                        "code": "diagram_path_missing",
                        "section_id": section.section_id,
                        "title": section.title,
                        "message": (
                            f"Diagram section {section.title!r} has no diagram_path; "
                            "the final export may show a heading without an image."
                        ),
                        "at": ts,
                    },
                )

            sections.append(
                AssembledSection(
                    section_id=section.section_id,
                    title=section.title,
                    level=int(section.level),
                    output_type=row.output_type,
                    content=normalized.content,
                    diagram_path=row.diagram_path,
                    content_blocks=[],
                    export_mode=export_mode,
                ),
            )

        return AssemblyOutcome(
            document=AssembledDocument(
                title=title,
                doc_type=doc_type,
                sections=sections,
                export_mode=export_mode,
            ),
            warnings=warnings,
        )

    def _collect_immediate_or_nested_child_titles(
        self,
        *,
        ordered_sections: list[SectionDefinition],
        current_index: int,
    ) -> list[str]:
        """Collect titles of child sections nested under the current section.

        Walks forward until we hit a section at the same level or shallower
        (i.e. a sibling or parent), then stops. The titles list is used by
        the content normalizer to detect duplicated child headings inside
        the LLM's prose output.

        Example:
        current = level 1
        include subsequent level 2/3/... sections until we hit another level 1 or less.
        """
        current = ordered_sections[current_index]
        current_level = int(current.level)

        child_titles: list[str] = []
        for next_section in ordered_sections[current_index + 1:]:
            next_level = int(next_section.level)
            if next_level <= current_level:
                break
            child_titles.append(next_section.title)

        return child_titles
