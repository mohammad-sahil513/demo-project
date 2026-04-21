"""Build a normalized section plan for custom templates."""

from __future__ import annotations

import re
from typing import Any

from modules.template.models import DocumentSkeleton, SectionDefinition


class SectionPlanner:
    def build_from_skeleton_and_classifications(
        self,
        skeleton: DocumentSkeleton,
        classifications: list[dict[str, Any]],
    ) -> list[SectionDefinition]:
        by_heading = {str(item.get("heading", "")).strip(): item for item in classifications}
        plan: list[SectionDefinition] = []
        for index, heading in enumerate(skeleton.headings):
            details = by_heading.get(heading, {})
            output_type = str(details.get("output_type") or "text")
            section = SectionDefinition(
                section_id=self._make_section_id(index, heading),
                title=heading,
                description=str(details.get("description") or ""),
                execution_order=index + 1,
                output_type="table" if output_type == "table" else "diagram" if output_type == "diagram" else "text",
                prompt_selector=str(details.get("prompt_selector") or "default"),
                retrieval_query=self._default_retrieval_query(heading),
                generation_hints=str(details.get("generation_hints") or ""),
                required_fields=list(details.get("required_fields") or []),
                table_headers=skeleton.table_headers_by_heading.get(heading, []),
                is_complex=bool(details.get("is_complex") or False),
            )
            plan.append(section)
        return plan

    def _make_section_id(self, index: int, heading: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
        if not slug:
            slug = f"section-{index + 1}"
        return f"sec-custom-{slug[:40]}"

    def _default_retrieval_query(self, heading: str) -> str:
        return f"{heading} requirements constraints dependencies"
