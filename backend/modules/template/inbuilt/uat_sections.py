"""Inbuilt UAT (User Acceptance Test) section definitions.

Mirror of :mod:`pdd_sections` for the UAT template. The plan is mostly
``output_type="table"`` — test case registers, traceability matrices, and
defect logs — which routes generation through the table generator with
strict GFM table normalization.
"""

from __future__ import annotations

from modules.template.models import SectionDefinition


UAT_SECTIONS: list[SectionDefinition] = [
    SectionDefinition(
        section_id="sec-uat-summary",
        title="Test Summary",
        description="Summary of UAT goals, test scope, and assumptions.",
        execution_order=1,
        prompt_selector="uat_signoff",
        retrieval_query="Business requirements acceptance goals entry and exit criteria",
    ),
    SectionDefinition(
        section_id="sec-uat-test-cases",
        title="Test Cases",
        description="UAT test case definitions and expected outcomes.",
        execution_order=2,
        output_type="table",
        prompt_selector="uat_test_cases",
        retrieval_query="User acceptance test scenarios steps expected results business process",
        table_headers=["ID", "Scenario", "Steps", "Expected Result"],
        required_fields=["ID", "Scenario", "Steps", "Expected Result", "Evidence"],
    ),
    SectionDefinition(
        section_id="sec-uat-defects",
        title="Defect Log",
        description="Known defects captured during UAT.",
        execution_order=3,
        output_type="table",
        prompt_selector="uat_defect_log",
        retrieval_query="Known defects UAT blockers severity owner mitigation",
        table_headers=["Defect", "Severity", "Status", "Owner"],
        required_fields=["Defect", "Severity", "Status", "Owner", "Evidence"],
    ),
    SectionDefinition(
        section_id="sec-uat-signoff",
        title="Sign-Off",
        description="Final approval details and release recommendation.",
        execution_order=4,
        prompt_selector="uat_signoff",
        retrieval_query="UAT signoff approvals stakeholders release recommendation",
        dependencies=["sec-uat-test-cases", "sec-uat-defects"],
    ),
]
