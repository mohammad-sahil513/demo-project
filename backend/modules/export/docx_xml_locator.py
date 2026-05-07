"""Utilities for locating DOCX nodes by schema path."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class XmlTarget:
    part: str
    xml_path: str
    placeholder_id: str


def parse_xml_target(placeholder: dict[str, object]) -> XmlTarget | None:
    location = placeholder.get("location")
    if not isinstance(location, dict):
        return None
    part = str(location.get("part") or "").strip()
    xml_path = str(location.get("xml_path") or "").strip()
    placeholder_id = str(placeholder.get("placeholder_id") or "").strip()
    if not part or not xml_path or not placeholder_id:
        return None
    return XmlTarget(part=part, xml_path=xml_path, placeholder_id=placeholder_id)

