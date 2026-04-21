"""Inbuilt UAT section definitions."""

from __future__ import annotations

from modules.template.models import SectionDefinition


UAT_SECTIONS: list[SectionDefinition] = [
    SectionDefinition(
        section_id="sec-uat-summary",
        title="Test Summary",
        description="Summary of UAT goals, test scope, and assumptions.",
        execution_order=1,
        prompt_selector="overview",
    ),
    SectionDefinition(
        section_id="sec-uat-test-cases",
        title="Test Cases",
        description="UAT test case definitions and expected outcomes.",
        execution_order=2,
        output_type="table",
        prompt_selector="default",
        table_headers=["ID", "Scenario", "Steps", "Expected Result"],
    ),
    SectionDefinition(
        section_id="sec-uat-defects",
        title="Defect Log",
        description="Known defects captured during UAT.",
        execution_order=3,
        output_type="table",
        prompt_selector="risk_register",
        table_headers=["Defect", "Severity", "Status", "Owner"],
    ),
    SectionDefinition(
        section_id="sec-uat-signoff",
        title="Sign-Off",
        description="Final approval details and release recommendation.",
        execution_order=4,
        prompt_selector="overview",
        dependencies=["sec-uat-test-cases", "sec-uat-defects"],
    ),
]
