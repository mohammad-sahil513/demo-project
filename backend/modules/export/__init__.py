"""Export: render the assembled document into final DOCX or XLSX bytes.

The :class:`ExportRenderer` is the public entry point used by
:mod:`services.workflow_executor`. Internally it dispatches to the right
filler (heading-based, placeholder-native DOCX, or XLSX) based on template
shape and feature flags. See ``docs/TEMPLATE_OPERATIONS.md`` for the
fidelity guarantees each path provides.
"""

from __future__ import annotations

from modules.export.renderer import ExportRenderer

__all__ = ["ExportRenderer"]
