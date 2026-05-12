"""Assembly: produce an ordered, normalized document before export.

The assembler stitches generated text/table/diagram sections together in
section-plan order, applies content hygiene (whitespace, heading prefixes)
and surfaces issues as warnings — the export layer takes the result as-is.
"""

from __future__ import annotations

from modules.assembly.assembler import AssemblyOutcome, DocumentAssembler
from modules.assembly.models import AssembledDocument, AssembledSection

__all__ = ["AssembledDocument", "AssembledSection", "AssemblyOutcome", "DocumentAssembler"]
