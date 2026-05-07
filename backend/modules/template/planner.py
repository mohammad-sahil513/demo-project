"""Build a normalized section plan for custom templates."""

from __future__ import annotations

import re
from typing import Any

from modules.template.models import ContentMode, DocumentSkeleton, ExtractedHeading, SectionDefinition


def _normalize_content_mode(raw: object) -> ContentMode:
    cm = str(raw or "generate").strip().lower()
    if cm in ("skip", "heading_only"):
        return cm  # type: ignore[return-value]
    return "generate"


class SectionPlanner:
    def build_from_skeleton_and_classifications(
        self,
        skeleton: DocumentSkeleton,
        classifications: list[dict[str, Any]],
    ) -> list[SectionDefinition]:
        heading_items = self._resolve_heading_items(skeleton)
        plan: list[SectionDefinition] = []

        # Maintain most recent section_id seen at each level
        parent_stack: dict[int, str] = {}

        by_heading_key, by_heading_text = self._classification_indexes(classifications)

        for index, heading_item in enumerate(heading_items):
            details = self._resolve_classification_for_heading(
                classifications,
                heading_item,
                index,
                by_heading_key,
                by_heading_text,
            )

            output_type = str(details.get("output_type") or "text").strip().lower()
            normalized_output_type = output_type if output_type in ("table", "diagram") else "text"

            level = max(1, int(heading_item.level))
            parent_section_id = self._resolve_parent_section_id(parent_stack, level)

            section = SectionDefinition(
                section_id=self._make_section_id(index, heading_item.text),
                title=heading_item.text,
                description=str(details.get("description") or ""),
                execution_order=index + 1,
                output_type=normalized_output_type,
                prompt_selector=str(details.get("prompt_selector") or "default"),
                retrieval_query=self._default_retrieval_query(heading_item.text),
                generation_hints=str(details.get("generation_hints") or ""),
                required_fields=[str(v) for v in (details.get("required_fields") or [])],
                table_headers=(
                    skeleton.table_headers_by_heading_order.get(heading_item.order, [])
                    or skeleton.table_headers_by_heading.get(heading_item.text, [])
                ),
                is_complex=bool(details.get("is_complex") or False),
                level=level,
                parent_section_id=parent_section_id,
                content_mode=_normalize_content_mode(details.get("content_mode")),
            )

            # Reset deeper levels when a new heading arrives at this level
            self._update_parent_stack(parent_stack, level, section.section_id)
            plan.append(section)

        return plan

    def _resolve_heading_items(self, skeleton: DocumentSkeleton) -> list[ExtractedHeading]:
        if skeleton.heading_items:
            return list(skeleton.heading_items)

        # Backward-compatible fallback if old skeletons exist
        return [
            ExtractedHeading(
                text=heading,
                level=1,
                order=index + 1,
                style_name=None,
                numbering=None,
            )
            for index, heading in enumerate(skeleton.headings)
        ]

    def _classification_for_index(self, classifications: list[dict[str, Any]], index: int) -> dict[str, Any]:
        if 0 <= index < len(classifications):
            item = classifications[index]
            if isinstance(item, dict):
                return item
        return {}

    @staticmethod
    def _normalize_heading_match(text: str) -> str:
        return " ".join(str(text or "").lower().split()).strip()

    def _classification_indexes(
        self,
        classifications: list[dict[str, Any]],
    ) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        by_key: dict[str, dict[str, Any]] = {}
        by_text: dict[str, dict[str, Any]] = {}
        for item in classifications:
            if not isinstance(item, dict):
                continue
            hk = item.get("heading_key")
            if hk is not None and str(hk).strip():
                by_key[str(hk).strip()] = item
            ht = item.get("heading")
            if ht is not None and str(ht).strip():
                by_text[self._normalize_heading_match(str(ht))] = item
        return by_key, by_text

    def _resolve_classification_for_heading(
        self,
        classifications: list[dict[str, Any]],
        heading_item: ExtractedHeading,
        index: int,
        by_heading_key: dict[str, dict[str, Any]],
        by_heading_text: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        key = str(heading_item.order)
        details = by_heading_key.get(key)
        if details:
            return details
        title_key = self._normalize_heading_match(heading_item.text)
        details = by_heading_text.get(title_key)
        if details:
            return details
        return self._classification_for_index(classifications, index)

    def _resolve_parent_section_id(self, parent_stack: dict[int, str], level: int) -> str | None:
        if level <= 1:
            return None

        for candidate_level in range(level - 1, 0, -1):
            parent_id = parent_stack.get(candidate_level)
            if parent_id:
                return parent_id

        return None

    def _update_parent_stack(self, parent_stack: dict[int, str], level: int, section_id: str) -> None:
        # Remove deeper levels when entering a new branch
        stale_levels = [lvl for lvl in parent_stack.keys() if lvl >= level]
        for lvl in stale_levels:
            parent_stack.pop(lvl, None)

        parent_stack[level] = section_id

    def _make_section_id(self, index: int, heading: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
        if not slug:
            slug = f"section-{index + 1}"
        return f"sec-custom-{index + 1}-{slug[:40]}"

    def _default_retrieval_query(self, heading: str) -> str:
        return f"{heading} requirements constraints dependencies"
