"""Post-process saved DOCX so Word refreshes fields (TOC, page numbers) on open.

python-docx writes field codes (TOC, page numbers, hyperlinks) but does
not evaluate them — Word evaluates fields when the document is opened
the next time. Setting ``<w:updateFields w:val="true"/>`` on
``word/settings.xml`` tells Word to do that automatically, which matches
what mail-merge tools and template-driven document generators do.

This rewrite is idempotent: if the flag is already set we still re-write
the same value so multiple renders are safe.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", _W_NS)


def ensure_update_fields_on_open(docx_path: Path) -> None:
    """
    Set word/settings.xml <w:updateFields w:val="true"/> so Word updates all fields
    (including TOC \\h hyperlinks and page numbers) when the document is first opened.

    python-docx does not evaluate TOC fields; Word must do it client-side. This flag
    matches common mail-merge / generated-document behavior.
    """
    path = Path(docx_path)
    if not path.is_file():
        return

    inner = "word/settings.xml"
    with ZipFile(path, "r") as zin:
        try:
            raw = zin.read(inner)
        except KeyError:
            return

    root = ET.fromstring(raw)
    tag = f"{{{_W_NS}}}updateFields"
    val_attr = f"{{{_W_NS}}}val"
    found: ET.Element | None = None
    for child in list(root):
        if child.tag == tag:
            found = child
            break
    if found is not None:
        found.set(val_attr, "true")
    else:
        el = ET.Element(tag)
        el.set(val_attr, "true")
        root.append(el)

    decl = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    body = ET.tostring(root, encoding="utf-8", default_namespace=None)
    new_bytes = decl + body

    tmp = path.with_suffix(path.suffix + ".~upd")
    try:
        with ZipFile(path, "r") as zin, ZipFile(tmp, "w", ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                data = new_bytes if info.filename == inner else zin.read(info.filename)
                ni = ZipInfo(filename=info.filename, date_time=info.date_time)
                ni.compress_type = ZIP_DEFLATED
                ni.external_attr = info.external_attr
                zout.writestr(ni, data)
        tmp.replace(path)
    except Exception:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
        raise
