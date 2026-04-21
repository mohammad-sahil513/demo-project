"""Inbuilt SDD section definitions."""

from __future__ import annotations

from modules.template.models import SectionDefinition


SDD_SECTIONS: list[SectionDefinition] = [
    SectionDefinition(
        section_id="sec-sdd-architecture-overview",
        title="Architecture Overview",
        description="High-level architecture summary.",
        execution_order=1,
        prompt_selector="architecture",
        is_complex=True,
    ),
    SectionDefinition(
        section_id="sec-sdd-architecture-diagram",
        title="System Architecture Diagram",
        description="Visual representation of major components and flows.",
        execution_order=2,
        output_type="diagram",
        prompt_selector="architecture",
        dependencies=["sec-sdd-architecture-overview"],
    ),
    SectionDefinition(
        section_id="sec-sdd-components",
        title="Component Design",
        description="Detailed component-level behavior and interfaces.",
        execution_order=3,
        prompt_selector="requirements",
        is_complex=True,
    ),
    SectionDefinition(
        section_id="sec-sdd-apis",
        title="API Specification",
        description="Core service contracts and payload expectations.",
        execution_order=4,
        output_type="table",
        prompt_selector="api_specification",
        table_headers=["API", "Method", "Request", "Response"],
    ),
    SectionDefinition(
        section_id="sec-sdd-security",
        title="Security Considerations",
        description="Security controls, data handling, and compliance notes.",
        execution_order=5,
        prompt_selector="risks",
    ),
    SectionDefinition(
        section_id="sec-sdd-deployment",
        title="Deployment and Operations",
        description="Deployment topology and runtime operations.",
        execution_order=6,
        prompt_selector="overview",
    ),
]
