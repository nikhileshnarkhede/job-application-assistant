"""
Resource Compliance Subgraph Builder

Validates resume against checklists and rubrics.

Graph Flow:
```
    START
      │
      ▼
┌─────────────────────────┐
│   prepare_resume_text   │  ← Extract text from ResumeJSON
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   validate_checklist    │  ← Check each item PASS/FAIL
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│      score_rubric       │  ← Score 1-4 per category
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   generate_feedback     │  ← Strengths & improvements
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    compile_report       │  ← Create ComplianceReport
└───────────┬─────────────┘
            │
            ▼
          END
```
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

from subgraphs.resource_compliance.state import (
    ResourceComplianceState,
    ComplianceReport
)
from subgraphs.resource_compliance.nodes import (
    prepare_resume_text,
    validate_checklist,
    score_rubric,
    generate_feedback,
    compile_report
)


def build_resource_compliance_graph() -> StateGraph:
    """
    Build the Resource Compliance subgraph.
    
    Returns:
        Compiled StateGraph for resume compliance validation
    """
    graph = StateGraph(ResourceComplianceState)
    
    # Add nodes
    graph.add_node("prepare_resume_text", prepare_resume_text)
    graph.add_node("validate_checklist", validate_checklist)
    graph.add_node("score_rubric", score_rubric)
    graph.add_node("generate_feedback", generate_feedback)
    graph.add_node("compile_report", compile_report)
    
    # Add edges
    graph.add_edge(START, "prepare_resume_text")
    graph.add_edge("prepare_resume_text", "validate_checklist")
    graph.add_edge("validate_checklist", "score_rubric")
    graph.add_edge("score_rubric", "generate_feedback")
    graph.add_edge("generate_feedback", "compile_report")
    graph.add_edge("compile_report", END)
    
    return graph.compile()


def create_resource_compliance_subgraph():
    """Create and return the compiled Resource Compliance subgraph."""
    return build_resource_compliance_graph()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def validate_resume_compliance(resume_json) -> Dict[str, Any]:
    """
    Validate a resume against checklists and rubrics.
    
    Args:
        resume_json: ResumeJSON object from Resume Builder
    
    Returns:
        Dict with compliance_report and validation results
    """
    graph = create_resource_compliance_subgraph()
    
    initial_state = {
        "resume_json": resume_json
    }
    
    result = graph.invoke(initial_state)
    
    return {
        "compliance_report": result.get("compliance_report"),
        "checklist_results": result.get("checklist_results", {}),
        "rubric_scores": result.get("rubric_scores", []),
        "validation_complete": result.get("validation_complete", False),
        "error": result.get("error_message")
    }


def get_compliance_summary(report: ComplianceReport) -> str:
    """
    Generate a human-readable compliance summary.
    
    Args:
        report: ComplianceReport object
    
    Returns:
        Formatted summary string
    """
    if not report:
        return "No compliance report available."
    
    lines = [
        "=" * 60,
        "RESUME COMPLIANCE REPORT",
        "=" * 60,
        "",
        f"📊 Overall Score: {report.overall_score}/100 (Grade: {report.grade})",
        f"   Status: {'✅ PASSED' if report.passed else '⚠️ NEEDS IMPROVEMENT'}",
        "",
        f"📋 Checklist: {report.checklist_score}% ({report.checklist_passed}/{report.checklist_total} items)",
        f"📊 Rubric: {report.rubric_score}%",
        "",
    ]
    
    # Rubric scores
    lines.append("📈 Rubric Scores (1-4 scale):")
    for score in report.rubric_categories:
        bar = "★" * score.score + "☆" * (4 - score.score)
        lines.append(f"   {score.category:15} [{bar}] {score.score}/4 (Weight: {int(score.weight*100)}%)")
    lines.append("")
    
    # Checklist sections
    lines.append("📋 Checklist by Section:")
    for section_name, section in report.checklist_sections.items():
        status = "✅" if section.score >= 80 else "⚠️" if section.score >= 60 else "❌"
        lines.append(f"   {status} {section.section_name}: {section.items_passed}/{section.items_total} ({section.score:.0f}%)")
    lines.append("")
    
    # Strengths
    if report.strengths:
        lines.append("💪 Strengths:")
        for s in report.strengths[:5]:
            lines.append(f"   ✓ {s}")
        lines.append("")
    
    # Critical Issues
    if report.critical_issues:
        lines.append("🚨 Critical Issues:")
        for issue in report.critical_issues[:5]:
            lines.append(f"   ✗ {issue}")
        lines.append("")
    
    # Improvements
    if report.improvements:
        lines.append("💡 Improvements:")
        for imp in report.improvements[:5]:
            lines.append(f"   • {imp}")
        lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


def quick_compliance_check(resume_json) -> Dict[str, Any]:
    """
    Quick compliance check returning just scores.
    
    Args:
        resume_json: ResumeJSON object
    
    Returns:
        Dict with scores and pass/fail status
    """
    result = validate_resume_compliance(resume_json)
    report = result.get("compliance_report")
    
    if not report:
        return {
            "overall_score": 0,
            "grade": "F",
            "passed": False,
            "error": result.get("error")
        }
    
    return {
        "overall_score": report.overall_score,
        "checklist_score": report.checklist_score,
        "rubric_score": report.rubric_score,
        "grade": report.grade,
        "passed": report.passed,
        "critical_issues_count": len(report.critical_issues)
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "build_resource_compliance_graph",
    "create_resource_compliance_subgraph",
    "validate_resume_compliance",
    "get_compliance_summary",
    "quick_compliance_check"
]
