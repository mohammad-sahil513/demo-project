"""Front-matter heading filter: skip cover/TOC headings before section planning.

The filter keeps the banner heading when no numbered or "Introduction"
heading exists below it, and drops everything before the main body when
the heuristic finds a clear start point. Tests pin both branches to keep
behavior stable as we tune the heuristic.
"""

from __future__ import annotations

from modules.template.heading_plan_filter import filter_heading_items_for_section_plan
from modules.template.models import DocumentSkeleton, ExtractedHeading
from modules.template.planner import SectionPlanner


def test_filter_keeps_banner_when_no_intro_or_numbering() -> None:
    items = [
        ExtractedHeading(text="SOFTWARE DESIGN DOCUMENT (SDD)", level=1, order=1),
        ExtractedHeading(text="Architecture overview", level=1, order=2),
    ]
    out = filter_heading_items_for_section_plan(items)
    assert [h.text for h in out] == ["SOFTWARE DESIGN DOCUMENT (SDD)", "Architecture overview"]


def test_filter_keeps_pdd_banner_when_no_intro_or_numbering() -> None:
    items = [
        ExtractedHeading(text="PRODUCT DESIGN DOCUMENT (PDD)", level=1, order=1),
        ExtractedHeading(text="Overview", level=1, order=2),
        ExtractedHeading(text="Scope and objectives", level=1, order=3),
    ]
    out = filter_heading_items_for_section_plan(items)
    assert [h.text for h in out] == [h.text for h in items]


def test_filter_starts_at_introduction() -> None:
    items = [
        ExtractedHeading(text="PRODUCT DESIGN DOCUMENT (PDD)", level=1, order=1),
        ExtractedHeading(text="Foreword", level=1, order=2),
        ExtractedHeading(text="Introduction", level=1, order=3),
        ExtractedHeading(text="Goals", level=1, order=4),
    ]
    out = filter_heading_items_for_section_plan(items)
    assert [h.text for h in out][0] == "Introduction"


def test_filter_starts_at_numbered_heading_text() -> None:
    items = [
        ExtractedHeading(text="PROCESS DESIGN DOCUMENT", level=1, order=1),
        ExtractedHeading(text="1 Purpose", level=1, order=2, numbering=None),
    ]
    out = filter_heading_items_for_section_plan(items)
    assert [h.text for h in out] == ["1 Purpose"]


def test_filter_respects_numbering_field() -> None:
    items = [
        ExtractedHeading(text="Cover", level=1, order=1),
        ExtractedHeading(text="Purpose", level=1, order=2, numbering="1"),
    ]
    out = filter_heading_items_for_section_plan(items)
    assert [h.text for h in out] == ["Purpose"]


def test_filter_single_title_only_keeps_heading() -> None:
    items = [ExtractedHeading(text="PRODUCT DESIGN DOCUMENT (PDD)", level=1, order=1)]
    out = filter_heading_items_for_section_plan(items)
    assert len(out) == 1


def test_planner_execution_order_restarts_after_filter() -> None:
    planner = SectionPlanner()
    skeleton = DocumentSkeleton(
        title="x",
        headings=["PRODUCT DESIGN DOCUMENT (PDD)", "Overview"],
        heading_items=[
            ExtractedHeading(text="PRODUCT DESIGN DOCUMENT (PDD)", level=1, order=1),
            ExtractedHeading(text="Overview", level=1, order=2),
        ],
    )
    plan = planner.build_from_skeleton_and_classifications(
        skeleton,
        [
            {
                "heading": "PRODUCT DESIGN DOCUMENT (PDD)",
                "heading_key": "1",
                "output_type": "text",
                "description": "",
                "prompt_selector": "default",
                "required_fields": [],
                "is_complex": False,
                "include_in_section_plan": False,
            },
            {
                "heading": "Overview",
                "heading_key": "2",
                "output_type": "text",
                "description": "ov",
                "prompt_selector": "default",
                "required_fields": [],
                "is_complex": False,
            },
        ],
    )
    assert len(plan) == 1
    assert plan[0].title == "Overview"
    assert plan[0].execution_order == 1
    assert plan[0].description == "ov"


def test_planner_keeps_two_headings_without_classifier_exclusion() -> None:
    planner = SectionPlanner()
    skeleton = DocumentSkeleton(
        title="x",
        headings=["Banner", "Section A"],
        heading_items=[
            ExtractedHeading(text="Banner", level=1, order=1),
            ExtractedHeading(text="Section A", level=1, order=2),
        ],
    )
    plan = planner.build_from_skeleton_and_classifications(
        skeleton,
        [
            {
                "heading": "Banner",
                "output_type": "text",
                "description": "",
                "prompt_selector": "default",
                "required_fields": [],
                "is_complex": False,
            },
            {
                "heading": "Section A",
                "output_type": "text",
                "description": "a",
                "prompt_selector": "default",
                "required_fields": [],
                "is_complex": False,
            },
        ],
    )
    assert len(plan) == 2
    assert [p.title for p in plan] == ["Banner", "Section A"]
