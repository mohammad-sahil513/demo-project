"""Registry for inbuilt section plans and style maps.

This is the lookup surface for inbuilt templates. The workflow calls
``get_inbuilt_section_plan`` and ``get_inbuilt_style_map`` once per run;
both return deep copies so the orchestrator can mutate plan entries
(e.g. annotate ``execution_order``) without leaking changes into the next
run.

``is_inbuilt_template_id`` and ``doc_type_for_inbuilt_template`` are used
by the export-hint and template-validator paths to branch between the
inbuilt DOCX builder and the custom DOCX filler.
"""

from __future__ import annotations

from copy import deepcopy

from core.constants import DocType, INBUILT_TEMPLATE_ID_BY_DOC_TYPE
from modules.template.inbuilt.pdd_sections import PDD_SECTIONS
from modules.template.inbuilt.sdd_sections import SDD_SECTIONS
from modules.template.inbuilt.styles.pdd_style import PDD_STYLE_MAP
from modules.template.inbuilt.styles.sdd_style import SDD_STYLE_MAP
from modules.template.inbuilt.styles.uat_style import UAT_STYLE_MAP
from modules.template.inbuilt.uat_sections import UAT_SECTIONS
from modules.template.models import SectionDefinition, StyleMap


_SECTION_REGISTRY: dict[DocType, list[SectionDefinition]] = {
    DocType.PDD: PDD_SECTIONS,
    DocType.SDD: SDD_SECTIONS,
    DocType.UAT: UAT_SECTIONS,
}

_STYLE_REGISTRY: dict[DocType, StyleMap] = {
    DocType.PDD: PDD_STYLE_MAP,
    DocType.SDD: SDD_STYLE_MAP,
    DocType.UAT: UAT_STYLE_MAP,
}


def get_inbuilt_section_plan(doc_type: str | DocType) -> list[SectionDefinition]:
    resolved = DocType(doc_type)
    # Return deep copies so callers can safely mutate without side effects.
    return [SectionDefinition.model_validate(item.model_dump()) for item in deepcopy(_SECTION_REGISTRY[resolved])]


def get_inbuilt_style_map(doc_type: str | DocType) -> StyleMap:
    resolved = DocType(doc_type)
    return StyleMap.model_validate(deepcopy(_STYLE_REGISTRY[resolved].model_dump()))


def is_inbuilt_template_id(template_id: str) -> bool:
    return template_id in set(INBUILT_TEMPLATE_ID_BY_DOC_TYPE.values())


def doc_type_for_inbuilt_template(template_id: str) -> DocType:
    for doc_type, inbuilt_id in INBUILT_TEMPLATE_ID_BY_DOC_TYPE.items():
        if inbuilt_id == template_id:
            return doc_type
    raise ValueError(f"Unknown inbuilt template id: {template_id}")
