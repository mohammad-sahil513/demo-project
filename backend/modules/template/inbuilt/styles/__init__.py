"""Inbuilt template style maps (PDD / SDD / UAT).

Each module exports a single :class:`StyleMap` constant that the inbuilt
DOCX builder reads to apply heading fonts, body styles, table colors, and
page setup. Tweak fonts and colors here to change the visual identity of
the corresponding inbuilt template; downstream code reads the values via
the registry, so no other file needs to change.
"""
