"""Template subsystem: load, classify, plan, and validate templates.

A template is the source-of-truth for *structure* — section order, headings,
placeholder schema, and DOCX/XLSX styling. The compile step builds a
:class:`SectionDefinition` plan plus a :class:`StyleMap`/sheet map that the
generation, assembly, and export phases consume.

Re-exports core dataclasses used widely across the codebase; deeper
implementations (classifier, extractor, planner, validators) live in
sibling modules.
"""

from modules.template.models import (
    DocumentSkeleton,
    PageSetup,
    ParagraphStyle,
    SectionDefinition,
    StyleMap,
    TableStyle,
)

__all__ = [
    "DocumentSkeleton",
    "PageSetup",
    "ParagraphStyle",
    "SectionDefinition",
    "StyleMap",
    "TableStyle",
]
