from __future__ import annotations

from modules.template.section_bindings import resolve_section_placeholder_bindings


def test_resolve_explicit_binding_overrides() -> None:
    schema = {
        "placeholders": [
            {
                "placeholder_id": "body_a",
                "kind": "text",
                "location": {"part": "word/document.xml", "xml_path": "/w:document/w:body/w:p[1]", "mask_scope": "path_node"},
            }
        ],
        "section_placeholder_bindings": {"sec-1": "body_a"},
    }
    plan = [{"section_id": "sec-1", "execution_order": 1}]
    bindings, err, _warn = resolve_section_placeholder_bindings(section_plan=plan, placeholder_schema=schema)
    assert bindings == {"sec-1": ["body_a"]}
    assert not err


def test_resolve_exact_section_id_matches_placeholder() -> None:
    schema = {
        "placeholders": [
            {
                "placeholder_id": "sec-custom-1-overview",
                "kind": "text",
                "location": {"part": "word/document.xml", "xml_path": "/w:document/w:body/w:p[1]", "mask_scope": "path_node"},
            }
        ],
        "section_placeholder_bindings": {},
    }
    plan = [{"section_id": "sec-custom-1-overview", "execution_order": 1}]
    bindings, err, _warn = resolve_section_placeholder_bindings(section_plan=plan, placeholder_schema=schema)
    assert bindings == {"sec-custom-1-overview": ["sec-custom-1-overview"]}
    assert not err


def test_resolve_errors_on_unknown_placeholder_in_map() -> None:
    schema = {
        "placeholders": [],
        "section_placeholder_bindings": {"sec-1": "missing_ph"},
    }
    plan = [{"section_id": "sec-1", "execution_order": 1}]
    _bindings, err, _warn = resolve_section_placeholder_bindings(section_plan=plan, placeholder_schema=schema)
    assert any(e.get("code") == "binding_unknown_placeholder" for e in err)


def test_resolve_errors_on_unbound_section() -> None:
    schema = {"placeholders": [{"placeholder_id": "x", "location": {"part": "word/document.xml", "xml_path": "/w:document/w:body/w:p[1]", "mask_scope": "path_node"}}]}
    plan = [{"section_id": "sec-unbound", "execution_order": 1}]
    _bindings, err, _warn = resolve_section_placeholder_bindings(section_plan=plan, placeholder_schema=schema)
    assert any(e.get("code") == "section_placeholder_unbound" for e in err)
