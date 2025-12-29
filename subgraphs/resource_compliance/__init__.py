"""
Resource Compliance Subgraph

Validates resume against:
1. Resume Checklist (item-by-item verification)
2. Resume Rubric (1-4 scoring per category)
3. Best Practices from Resume Guide

Usage:
    from subgraphs.resource_compliance import validate_resume_compliance, get_compliance_summary
    
    result = validate_resume_compliance(resume_json)
    
    report = result["compliance_report"]
    print(f"Score: {report.overall_score}% (Grade: {report.grade})")
    print(f"Passed: {report.passed}")
    
    # Get formatted summary
    summary = get_compliance_summary(report)
    print(summary)
"""

from subgraphs.resource_compliance.graph import (
    build_resource_compliance_graph,
    create_resource_compliance_subgraph,
    validate_resume_compliance,
    get_compliance_summary,
    quick_compliance_check
)

from subgraphs.resource_compliance.state import (
    ResourceComplianceState,
    ChecklistResult,
    SectionCheckResult,
    RubricScore,
    ComplianceReport,
    RESUME_CHECKLIST,
    RESUME_RUBRIC,
    get_grade
)

from subgraphs.resource_compliance.nodes import (
    prepare_resume_text,
    validate_checklist,
    score_rubric,
    generate_feedback,
    compile_report
)

__all__ = [
    # Main functions
    "validate_resume_compliance",
    "get_compliance_summary",
    "quick_compliance_check",
    
    # Graph builders
    "build_resource_compliance_graph",
    "create_resource_compliance_subgraph",
    
    # State & Models
    "ResourceComplianceState",
    "ChecklistResult",
    "SectionCheckResult",
    "RubricScore",
    "ComplianceReport",
    "RESUME_CHECKLIST",
    "RESUME_RUBRIC",
    "get_grade",
    
    # Nodes
    "prepare_resume_text",
    "validate_checklist",
    "score_rubric",
    "generate_feedback",
    "compile_report"
]
