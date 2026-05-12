"""Optional DOCX normalization on compile (conservative table row trim).

Many uploaded templates carry filler/example rows under their tables that
the author meant only as visual guidance. When the renderer fills those
tables it appends rows for actual content, so the extra filler rows leak
into the exported document. To keep the surface clean, on compile we
conservatively trim every ``w:tbl`` to at most two rows — header + one
canonical body row.

This step is best-effort: any OOXML parsing or zip rewrite failure is
captured as a warning and the original file is left untouched. The
warnings are persisted on the :class:`TemplateRecord` so authors can see
what was changed.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

_WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
_W_MAIN = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def apply_docx_template_normalize(docx_path: Path) -> list[dict[str, object]]:
    """
    Trim each w:tbl to at most two rows (intended: header + one body row).
    Modifies docx_path in place. Returns warnings (never raises for OOXML quirks).
    """
    warnings: list[dict[str, object]] = []
    inner = "word/document.xml"
    try:
        with ZipFile(docx_path, "r") as zin:
            if inner not in zin.namelist():
                return warnings
            raw = zin.read(inner)
            names = zin.namelist()
            part_bytes = {n: zin.read(n) for n in names}
    except OSError:
        warnings.append(
            {
                "code": "normalize_read_failed",
                "severity": "warning",
                "message": "Could not read DOCX for normalization.",
            }
        )
        return warnings

    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        warnings.append(
            {
                "code": "normalize_parse_failed",
                "severity": "warning",
                "message": "document.xml parse failed; skipping normalization.",
            }
        )
        return warnings

    trimmed = 0
    for tbl in root.findall(".//w:tbl", _WORD_NS):
        trs = tbl.findall("w:tr", _WORD_NS)
        while len(trs) > 2:
            tbl.remove(trs[-1])
            trs = tbl.findall("w:tr", _WORD_NS)
            trimmed += 1

    if trimmed:
        warnings.append(
            {
                "code": "normalize_table_rows_trimmed",
                "severity": "warning",
                "message": f"Trimmed extra table rows (tables affected: {trimmed}).",
            }
        )

    new_body = ET.tostring(root, encoding="utf-8")
    decl = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    part_bytes[inner] = decl + new_body

    tmp = docx_path.with_suffix(docx_path.suffix + ".~norm")
    try:
        with ZipFile(tmp, "w", ZIP_DEFLATED) as zout:
            for name in names:
                data = part_bytes[name]
                info = ZipInfo(filename=name)
                info.compress_type = ZIP_DEFLATED
                zout.writestr(info, data)
        tmp.replace(docx_path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        warnings.append(
            {
                "code": "normalize_write_failed",
                "severity": "warning",
                "message": "Failed to write normalized DOCX; left original file.",
            }
        )
    return warnings
