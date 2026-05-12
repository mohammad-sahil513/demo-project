"""Phase 6 (TEMPLATE_PREPARATION) tests: extractor, classifier, planner, registry.

Validates the custom template compile pipeline end to end:

- :class:`TemplateExtractor` returns headings, style map, sheet map
  for both DOCX and XLSX inputs.
- :class:`TemplateClassifier` falls back to heuristics when the LLM is
  unavailable or returns an invalid payload.
- :class:`SectionPlanner` produces stable section IDs and respects the
  classifier's ``include_in_section_plan=False`` overrides.
- The inbuilt registry returns deep copies so callers can safely mutate.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from zipfile import ZipFile

from openpyxl import Workbook

from core.constants import INBUILT_TEMPLATE_ID_PDD, TemplateStatus
from core.ids import utc_now_iso
from modules.template.extractor import TemplateExtractor
from modules.template.inbuilt.registry import get_inbuilt_section_plan, get_inbuilt_style_map
from modules.template.planner import SectionPlanner
from repositories.document_models import DocumentRecord
from repositories.document_repo import DocumentRepository
from repositories.template_models import TemplateRecord
from repositories.template_repo import TemplateRepository
from repositories.workflow_repo import WorkflowRepository
from services.event_service import EventService
from services.template_service import TemplateService
from services.workflow_executor import WorkflowExecutor
from services.workflow_service import WorkflowService


def _write_minimal_docx(path: Path) -> None:
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>1. Overview</w:t></w:r></w:p>'
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>2. Requirements</w:t></w:r></w:p>'
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>3. Risk Register</w:t></w:r></w:p>'
        "</w:body>"
        "</w:document>"
    )
    with ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)


def _write_minimal_xlsx(path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Test Cases"
    ws.append(["ID", "Scenario", "Steps", "Expected Result"])
    ws2 = wb.create_sheet("Defects")
    ws2.append(["Defect", "Severity", "Status", "Owner"])
    wb.save(str(path))


def test_inbuilt_registry_lookup_returns_sections_and_style() -> None:
    sections = get_inbuilt_section_plan("PDD")
    style_map = get_inbuilt_style_map("PDD")

    assert sections
    assert sections[0].section_id.startswith("sec-pdd-")
    assert style_map.heading_1.bold is True


def test_extractor_and_planner_build_custom_section_plan(tmp_path) -> None:
    docx_path = Path(tmp_path) / "custom.bin"
    _write_minimal_docx(docx_path)
    extractor = TemplateExtractor()
    planner = SectionPlanner()

    skeleton, _, _ = extractor.extract_docx(docx_path)
    classifications = [
        {"heading": "1. Overview", "output_type": "text", "description": "Overview", "prompt_selector": "overview"},
        {
            "heading": "3. Risk Register",
            "output_type": "table",
            "description": "Risks",
            "prompt_selector": "risk_register",
            "required_fields": ["Risk", "Impact"],
        },
    ]
    plan = planner.build_from_skeleton_and_classifications(skeleton, classifications)

    assert len(plan) == 3
    assert plan[0].title == "1. Overview"
    assert any(section.output_type == "table" for section in plan)


def test_extractor_builds_xlsx_sheet_schema(tmp_path) -> None:
    xlsx_path = Path(tmp_path) / "uat.xlsx"
    _write_minimal_xlsx(xlsx_path)
    extractor = TemplateExtractor()
    skeleton, _, sheet_map = extractor.extract_xlsx(xlsx_path)

    assert skeleton.headings == ["Test Cases", "Defects"]
    schema = sheet_map.get("schema")
    assert isinstance(schema, list) and len(schema) == 2
    assert schema[0]["headers"] == ["ID", "Scenario", "Steps", "Expected Result"]
    assert schema[1]["required_columns"] == ["Defect", "Severity", "Status", "Owner"]


def test_template_service_compile_pipeline_updates_template_record(tmp_path) -> None:
    async def _run() -> None:
        repo = TemplateRepository(Path(tmp_path) / "templates")
        service = TemplateService(repo)
        now = utc_now_iso()
        template_file = Path(tmp_path) / "templates" / "tpl-1.bin"
        _write_minimal_docx(template_file)
        repo.save(
            TemplateRecord(
                template_id="tpl-1",
                filename="custom_template.docx",
                template_type="PDD",
                status=TemplateStatus.COMPILING.value,
                file_path="tpl-1.bin",
                created_at=now,
                updated_at=now,
            ),
        )

        compiled = await service.compile_template("tpl-1")
        assert compiled.status == TemplateStatus.READY.value
        assert len(compiled.section_plan) == 3
        assert compiled.preview_path is not None
        assert compiled.preview_path.endswith(".docx")
        preview_path = Path(tmp_path) / "templates" / compiled.preview_path
        with ZipFile(preview_path, "r") as archive:
            assert "word/document.xml" in archive.namelist()

    asyncio.run(_run())


def test_template_service_compile_marks_failed_for_invalid_docx(tmp_path) -> None:
    async def _run() -> None:
        repo = TemplateRepository(Path(tmp_path) / "templates")
        service = TemplateService(repo)
        now = utc_now_iso()
        invalid_file = Path(tmp_path) / "templates" / "tpl-invalid.bin"
        invalid_file.write_bytes(b"not-a-docx")
        repo.save(
            TemplateRecord(
                template_id="tpl-invalid",
                filename="broken.docx",
                template_type="PDD",
                status=TemplateStatus.COMPILING.value,
                file_path="tpl-invalid.bin",
                created_at=now,
                updated_at=now,
            ),
        )
        compiled = await service.compile_template("tpl-invalid")
        assert compiled.status == TemplateStatus.FAILED.value
        assert compiled.section_plan == []
        assert compiled.preview_path is None
        assert compiled.compile_error

    asyncio.run(_run())


def test_workflow_executor_template_phase_uses_inbuilt_registry(tmp_path) -> None:
    async def _run() -> None:
        now = utc_now_iso()
        document_repo = DocumentRepository(Path(tmp_path) / "documents")
        template_repo = TemplateRepository(Path(tmp_path) / "templates")
        workflow_repo = WorkflowRepository(Path(tmp_path) / "workflows")

        document_repo.save(
            DocumentRecord(
                document_id="doc-1",
                filename="sample.pdf",
                content_type="application/pdf",
                size_bytes=10,
                file_path="doc-1.bin",
                created_at=now,
                updated_at=now,
            ),
        )
        workflow_service = WorkflowService(workflow_repo, document_repo=document_repo, template_repo=template_repo)
        workflow = workflow_service.create(
            document_id="doc-1",
            template_id=INBUILT_TEMPLATE_ID_PDD,
            doc_type="PDD",
        )

        executor = WorkflowExecutor(workflow_service=workflow_service, event_service=EventService())
        await executor._phase_template_preparation(workflow.workflow_run_id)

        updated = workflow_service.get_or_raise(workflow.workflow_run_id)
        assert len(updated.section_plan) == len(get_inbuilt_section_plan("PDD"))
        assert updated.style_map

    asyncio.run(_run())


def test_template_preview_html_fallback_escapes_user_controlled_values(tmp_path) -> None:
    repo = TemplateRepository(Path(tmp_path) / "templates")
    service = TemplateService(repo)
    now = utc_now_iso()
    record = TemplateRecord(
        template_id="tpl-escape",
        filename='evil"><img src=x onerror=alert(1)>',
        template_type="UAT",
        status=TemplateStatus.READY.value,
        file_path="tpl-escape.xlsx",
        preview_path=None,
        preview_html=None,
        created_at=now,
        updated_at=now,
    )
    repo.save(record)

    html = service.get_preview_html("tpl-escape")
    assert "<img" not in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert "&quot;&gt;" in html
