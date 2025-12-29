"""
Cover Letter Compliance Subgraph

Validates cover letter against:
1. Cover Letter Checklist (item-by-item verification)
2. Cover Letter Rubric (1-3 scoring per section)
3. Best Practices from Cover Letter Guide

Usage:
    from subgraphs.cover_letter_compliance import (
        validate_cover_letter_compliance,
        get_cover_letter_compliance_summary
    )
    
    result = validate_cover_letter_compliance(
        cover_letter=cover_letter,  # CoverLetter object
        structured_jd=structured_jd  # For keyword matching
    )
    
    report = result["compliance_report"]
    print(f"Score: {report.overall_score}% (Grade: {report.grade})")
    print(f"Passed: {report.passed}")
    
    # Get formatted summary
    summary = get_cover_letter_compliance_summary(report)
    print(summary)
"""

from subgraphs.cover_letter_compliance.graph import (
    build_cover_letter_compliance_graph,
    create_cover_letter_compliance_subgraph,
    validate_cover_letter_compliance,
    get_cover_letter_compliance_summary,
    quick_cover_letter_compliance_check
)

from subgraphs.cover_letter_compliance.state import (
    CoverLetterComplianceState,
    ChecklistResult,
    SectionCheckResult,
    RubricScore,
    CoverLetterComplianceReport,
    COVER_LETTER_CHECKLIST,
    COVER_LETTER_RUBRIC,
    get_grade
)

from subgraphs.cover_letter_compliance.nodes import (
    prepare_cover_letter_text,
    validate_checklist,
    score_rubric,
    generate_feedback,
    compile_report
)

__all__ = [
    # Main functions
    "validate_cover_letter_compliance",
    "get_cover_letter_compliance_summary",
    "quick_cover_letter_compliance_check",
    
    # Graph builders
    "build_cover_letter_compliance_graph",
    "create_cover_letter_compliance_subgraph",
    
    # State & Models
    "CoverLetterComplianceState",
    "ChecklistResult",
    "SectionCheckResult",
    "RubricScore",
    "CoverLetterComplianceReport",
    "COVER_LETTER_CHECKLIST",
    "COVER_LETTER_RUBRIC",
    "get_grade",
    
    # Nodes
    "prepare_cover_letter_text",
    "validate_checklist",
    "score_rubric",
    "generate_feedback",
    "compile_report"
]
