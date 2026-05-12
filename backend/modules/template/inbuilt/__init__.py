"""Inbuilt template definitions (PDD / SDD / UAT).

Each inbuilt template ships as Python data: a flat list of
:class:`SectionDefinition` and a :class:`StyleMap`. The registry exposes
them by :class:`DocType` so the workflow can decide between the inbuilt
DOCX builder and the custom DOCX filler without inspecting files.

See ``modules.template.inbuilt.registry`` for the lookup helpers and
``docs/ARCHITECTURE.md`` for the catalog entry.
"""
