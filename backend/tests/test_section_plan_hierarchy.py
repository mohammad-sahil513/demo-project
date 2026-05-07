"""Tests for section plan enrichment, hierarchy context, and workflow planning guards."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock
from zipfile import ZipFile

from openpyxl import Workbook

from core.constants import TemplateStatus
from core.ids import utc_now_iso
from modules.template.extractor import TemplateExtractor
from modules.template.models import DocumentSkeleton, ExtractedHeading, SectionDefinition
from modules.template.planner import SectionPlanner
from modules.template.section_plan_apply import apply_xlsx_sheet_schema_to_plan
from repositories.document_models import DocumentRecord
from repositories.document_repo import DocumentRepository
from repositories.template_models import TemplateRecord
from repositories.template_repo import TemplateRepository
from repositories.workflow_repo import WorkflowRepository
from services.event_service import EventService
from services.template_service import TemplateService
from services.workflow_executor import WorkflowExecutor, merge_workflow_warnings
from services.workflow_service import WorkflowService


def test_apply_xlsx_sheet_schema_to_plan_merges_headers() -> None:
    plan = [
        SectionDefinition(
            section_id="sec-1",
            title="Test Cases",
            execution_order=1,
            output_type="table",
        ),
        SectionDefinition(
            section_id="sec-2",
            title="Defects",
            execution_order=2,
            output_type="table",
        ),
    ]
    sheet_map = {
        "schema": [
            {"sheet_name": "Test Cases", "headers": ["ID", "Scenario"]},
            {"sheet_name": "Defects", "headers": ["Defect", "Severity"]},
        ],
    }
    out = apply_xlsx_sheet_schema_to_plan(plan, sheet_map)
    assert out[0].table_headers == ["ID", "Scenario"]
    assert out[0].required_fields == ["ID", "Scenario"]
    assert out[1].table_headers == ["Defect", "Severity"]


def test_merge_workflow_warnings_deduplicates() -> None:
    existing = [{"code": "a", "section_id": "", "message": "m1"}]
    new = [
        {"code": "a", "section_id": "", "message": "m1"},
        {"code": "b", "section_id": "s1", "message": "m2"},
    ]
    merged = merge_workflow_warnings(existing, new)
    assert len(merged) == 2
    assert merged[0]["code"] == "a"
    assert merged[1]["code"] == "b"


def test_planner_passes_content_mode_from_classifier() -> None:
    planner = SectionPlanner()
    skeleton = DocumentSkeleton(
        title="t",
        headings=["Only"],
        heading_items=[ExtractedHeading(text="Only", level=1, order=1)],
    )
    plan = planner.build_from_skeleton_and_classifications(
        skeleton,
        [
            {
                "heading": "Only",
                "heading_key": "1",
                "output_type": "text",
                "description": "",
                "prompt_selector": "default",
                "required_fields": [],
                "is_complex": False,
                "content_mode": "heading_only",
            },
        ],
    )
    assert len(plan) == 1
    assert plan[0].content_mode == "heading_only"


def test_planner_matches_classification_by_heading_key_not_index() -> None:
    planner = SectionPlanner()
    skeleton = DocumentSkeleton(
        title="t",
        headings=["Alpha", "Beta"],
        heading_items=[
            ExtractedHeading(text="Alpha", level=1, order=1),
            ExtractedHeading(text="Beta", level=1, order=2),
        ],
    )
    classifications = [
        {
            "heading": "wrong",
            "heading_key": "2",
            "output_type": "table",
            "description": "",
            "prompt_selector": "default",
            "required_fields": ["X"],
            "is_complex": False,
        },
        {
            "heading": "wrong2",
            "heading_key": "1",
            "output_type": "diagram",
            "description": "",
            "prompt_selector": "default",
            "required_fields": [],
            "is_complex": False,
        },
    ]
    plan = planner.build_from_skeleton_and_classifications(skeleton, classifications)
    assert plan[0].title == "Alpha"
    assert plan[0].output_type == "diagram"
    assert plan[1].title == "Beta"
    assert plan[1].output_type == "table"


def _write_docx_with_heading_and_table(path: Path) -> None:
    table_xml = (
        "<w:tbl>"
        "<w:tr>"
        '<w:tc><w:p><w:r><w:t>H1</w:t></w:r></w:p></w:tc>'
        '<w:tc><w:p><w:r><w:t>H2</w:t></w:r></w:p></w:tc>'
        "</w:tr>"
        "</w:tbl>"
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Section A</w:t></w:r></w:p>'
        f"{table_xml}"
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Section B</w:t></w:r></w:p>'
        "</w:body>"
        "</w:document>"
    )
    with ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)


def test_extractor_docx_picks_widest_table_under_heading(tmp_path: Path) -> None:
    narrow = (
        "<w:tbl><w:tr><w:tc><w:p><w:r><w:t>N</w:t></w:r></w:p></w:tc></w:tr></w:tbl>"
    )
    wide = (
        "<w:tbl><w:tr>"
        '<w:tc><w:p><w:r><w:t>A</w:t></w:r></w:p></w:tc>'
        '<w:tc><w:p><w:r><w:t>B</w:t></w:r></w:p></w:tc>'
        '<w:tc><w:p><w:r><w:t>C</w:t></w:r></w:p></w:tc>'
        "</w:tr></w:tbl>"
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Sec</w:t></w:r></w:p>'
        f"{narrow}{wide}"
        "</w:body></w:document>"
    )
    path = Path(tmp_path) / "two_tables.docx"
    with ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)
    skeleton, _, _ = TemplateExtractor().extract_docx(path)
    assert skeleton.table_headers_by_heading_order[1] == ["A", "B", "C"]


def test_extractor_docx_gridspan_expands_header_columns(tmp_path: Path) -> None:
    table_xml = (
        "<w:tbl><w:tr>"
        '<w:tc><w:tcPr><w:gridSpan w:val="2"/></w:tcPr>'
        "<w:p><w:r><w:t>Wide</w:t></w:r></w:p></w:tc>"
        '<w:tc><w:p><w:r><w:t>Z</w:t></w:r></w:p></w:tc>'
        "</w:tr></w:tbl>"
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>H</w:t></w:r></w:p>'
        f"{table_xml}</w:body></w:document>"
    )
    path = Path(tmp_path) / "gridspan.docx"
    with ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)
    skeleton, _, _ = TemplateExtractor().extract_docx(path)
    assert skeleton.table_headers_by_heading_order[1] == ["Wide", "Wide", "Z"]


def test_extractor_docx_table_headers_by_heading_order(tmp_path: Path) -> None:
    path = Path(tmp_path) / "heading_table.docx"
    _write_docx_with_heading_and_table(path)
    extractor = TemplateExtractor()
    skeleton, _, _ = extractor.extract_docx(path)
    assert skeleton.table_headers_by_heading_order[1] == ["H1", "H2"]
    assert "Section A" in skeleton.table_headers_by_heading


def test_uat_section_planning_no_false_schema_warning_for_docx_placeholder_schema(tmp_path: Path) -> None:
    now = utc_now_iso()
    document_repo = DocumentRepository(Path(tmp_path) / "documents")
    template_repo = TemplateRepository(Path(tmp_path) / "templates")
    workflow_repo = WorkflowRepository(Path(tmp_path) / "workflows")

    document_repo.save(
        DocumentRecord(
            document_id="doc-uat",
            filename="sample.pdf",
            content_type="application/pdf",
            size_bytes=10,
            file_path="doc-uat.bin",
            created_at=now,
            updated_at=now,
        ),
    )
    template_repo.save(
        TemplateRecord(
            template_id="tpl-uat-docx",
            filename="uat.docx",
            template_type="UAT",
            status=TemplateStatus.READY.value,
            file_path="x.bin",
            placeholder_schema={
                "schema_version": "1.0",
                "source_format": "docx",
                "placeholders": [{"placeholder_id": "ph1", "kind": "text", "required": True}],
            },
            created_at=now,
            updated_at=now,
        ),
    )

    workflow_service = WorkflowService(workflow_repo, document_repo=document_repo, template_repo=template_repo)
    workflow = workflow_service.create(document_id="doc-uat", template_id="tpl-uat-docx", doc_type="UAT")
    workflow_service.update(
        workflow.workflow_run_id,
        section_plan=[
            {
                "section_id": "sec-1",
                "title": "Signoff",
                "execution_order": 1,
                "output_type": "text",
                "level": 1,
            },
        ],
        sheet_map={},
        warnings=[],
    )

    executor = WorkflowExecutor(workflow_service=workflow_service, event_service=EventService())

    async def _run() -> None:
        await executor._phase_section_planning(workflow.workflow_run_id)

    asyncio.run(_run())

    updated = workflow_service.get_or_raise(workflow.workflow_run_id)
    assert not any(w.get("code") == "schema_not_ready" for w in (updated.warnings or []))
    assert updated.observability_summary.get("section_planning_warning_count") == 0
    assert updated.observability_summary.get("section_planning_warning_codes") == []


def test_compile_xlsx_merges_sheet_headers_into_plan(tmp_path: Path) -> None:
    async def _run() -> None:
        root = Path(tmp_path)
        tpl_dir = root / "templates"
        tpl_dir.mkdir(parents=True)
        xlsx_path = tpl_dir / "tpl-x.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.title = "SheetOne"
        ws.append(["ColA", "ColB"])
        wb.save(str(xlsx_path))

        repo = TemplateRepository(tpl_dir)
        now = utc_now_iso()
        repo.save(
            TemplateRecord(
                template_id="tpl-x",
                filename="book.xlsx",
                template_type="PDD",
                status=TemplateStatus.COMPILING.value,
                file_path="tpl-x.xlsx",
                created_at=now,
                updated_at=now,
            ),
        )

        service = TemplateService(repo)

        async def classify_stub(skeleton: DocumentSkeleton) -> list[dict[str, object]]:
            return [
                {
                    "heading": item.text,
                    "heading_key": str(item.order),
                    "output_type": "table",
                    "description": "",
                    "prompt_selector": "default",
                    "required_fields": [],
                    "is_complex": False,
                }
                for item in skeleton.heading_items
            ]

        service._classify_sections_resilient = AsyncMock(side_effect=classify_stub)  # type: ignore[method-assign]

        compiled = await service.compile_template("tpl-x")
        assert compiled.status == TemplateStatus.READY.value
        assert len(compiled.section_plan) == 1
        row = compiled.section_plan[0]
        assert row.get("title") == "SheetOne"
        assert row.get("table_headers") == ["ColA", "ColB"]

    asyncio.run(_run())
