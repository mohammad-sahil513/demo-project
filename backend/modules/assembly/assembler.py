"""Merge section plan + generation results into a single ordered document."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from core.ids import utc_now_iso
from modules.assembly.models import AssembledDocument, AssembledSection
from modules.generation.models import GenerationSectionResult
from modules.template.models import SectionDefinition


@dataclass(frozen=True, slots=True)
class AssemblyOutcome:
    document: AssembledDocument
    warnings: list[dict[str, object]] = field(default_factory=list)


class DocumentAssembler:
    def assemble(
        self,
        *,
        document_filename: str,
        doc_type: str,
        section_plan: list[SectionDefinition],
        section_generation_results: dict[str, dict[str, object]],
    ) -> AssemblyOutcome:
        ordered = sorted(section_plan, key=lambda s: s.execution_order)
        stem = Path(document_filename).stem
        title = f"{stem} — {doc_type}"
        sections: list[AssembledSection] = []
        warnings: list[dict[str, object]] = []
        ts = utc_now_iso()

        for section in ordered:
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
            sections.append(
                AssembledSection(
                    section_id=section.section_id,
                    title=section.title,
                    level=int(section.level),
                    output_type=row.output_type,
                    content=row.content or "",
                    diagram_path=row.diagram_path,
                ),
            )
        return AssemblyOutcome(document=AssembledDocument(title=title, doc_type=doc_type, sections=sections), warnings=warnings)
