"""Inbuilt PDD (Project Definition Document) section definitions.

Static :class:`SectionDefinition` list that the workflow uses when a user
selects the built-in PDD template. Each entry pins the prompt selector,
retrieval query, and output type for one section; the ``execution_order``
becomes the wave key in :func:`compute_execution_waves`.

To add or reorder sections: update this file and re-run the section
contract tests in ``backend/tests``.
"""

from __future__ import annotations

from modules.template.models import SectionDefinition


PDD_SECTIONS: list[SectionDefinition] = [
    SectionDefinition(
        section_id="sec-pdd-overview",
        title="Project Overview",
        description="Describe the business context and expected outcomes.",
        execution_order=1,
        prompt_selector="overview",
        retrieval_query="project overview business goals scope",
    ),
    SectionDefinition(
        section_id="sec-pdd-scope",
        title="Scope",
        description="In-scope and out-of-scope boundaries.",
        execution_order=2,
        prompt_selector="scope",
        retrieval_query="scope boundaries in scope out of scope",
    ),
    SectionDefinition(
        section_id="sec-pdd-stakeholders",
        title="Stakeholder Matrix",
        description="Primary stakeholders and their responsibilities.",
        execution_order=3,
        output_type="table",
        prompt_selector="stakeholders",
        required_fields=["stakeholder", "role", "responsibility"],
        table_headers=["Stakeholder", "Role", "Responsibility"],
    ),
    SectionDefinition(
        section_id="sec-pdd-requirements",
        title="Functional Requirements",
        description="Prioritized business requirements.",
        execution_order=4,
        prompt_selector="requirements",
        retrieval_query="functional requirements business rules acceptance criteria",
        is_complex=True,
    ),
    SectionDefinition(
        section_id="sec-pdd-assumptions",
        title="Assumptions and Constraints",
        description="Constraints, assumptions, and dependencies.",
        execution_order=5,
        prompt_selector="assumptions",
    ),
    SectionDefinition(
        section_id="sec-pdd-risks",
        title="Risk Register",
        description="Known risks and proposed mitigations.",
        execution_order=6,
        output_type="table",
        prompt_selector="risk_register",
        table_headers=["Risk", "Impact", "Likelihood", "Mitigation"],
    ),
    SectionDefinition(
        section_id="sec-pdd-traceability",
        title="Traceability Matrix",
        description="Mapping of objectives to requirements and tests.",
        execution_order=7,
        output_type="table",
        prompt_selector="traceability_matrix",
        table_headers=["Objective", "Requirement", "Validation"],
    ),
    SectionDefinition(
        section_id="sec-pdd-summary",
        title="Executive Summary",
        description="Concise summary and implementation recommendation.",
        execution_order=8,
        prompt_selector="overview",
        dependencies=["sec-pdd-requirements", "sec-pdd-risks"],
    ),
]
