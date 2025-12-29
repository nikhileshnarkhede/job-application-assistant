"""
ATS Optimizer Subgraph Builder

This module builds the complete ATS Optimizer subgraph using LangGraph.

Graph Flow:
```
    START
      │
      ▼
┌─────────────────────────┐
│   extract_jd_keywords   │  ← Extract & weight keywords from JD
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   scan_resume_content   │  ← Extract text from all sections
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   calculate_ats_score   │  ← Match keywords, calculate score
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   check_format_issues   │  ← Validate ATS-friendly formatting
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   generate_suggestions  │  ← LLM: Generate improvement suggestions
└───────────┬─────────────┘
            │
            ▼
        ◆ should_continue?
       ╱              ╲
    "apply"        "finalize"
      │                │
      ▼                │
┌─────────────────┐    │
│ apply_suggestions│   │
└────────┬────────┘    │
         │             │
         └──►scan──────│
             (loop)    │
                       ▼
              ┌─────────────────┐
              │ finalize_analysis│
              └────────┬────────┘
                       │
                       ▼
                     END
```
"""

from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, START, END

# Import state and nodes
from subgraphs.ats_optimizer.state import ATSOptimizerState
from subgraphs.ats_optimizer.nodes import (
    extract_jd_keywords,
    scan_resume_content,
    calculate_ats_score,
    check_format_issues,
    generate_suggestions,
    apply_suggestions,
    finalize_analysis,
    should_continue_optimization
)


def build_ats_optimizer_graph() -> StateGraph:
    """
    Build the ATS Optimizer subgraph.
    
    Returns:
        Compiled StateGraph for ATS optimization
    """
    # Create graph with state schema
    graph = StateGraph(ATSOptimizerState)
    
    # ===== ADD NODES =====
    graph.add_node("extract_jd_keywords", extract_jd_keywords)
    graph.add_node("scan_resume_content", scan_resume_content)
    graph.add_node("calculate_ats_score", calculate_ats_score)
    graph.add_node("check_format_issues", check_format_issues)
    graph.add_node("generate_suggestions", generate_suggestions)
    graph.add_node("apply_suggestions", apply_suggestions)
    graph.add_node("finalize_analysis", finalize_analysis)
    
    # ===== ADD EDGES =====
    # Initial flow
    graph.add_edge(START, "extract_jd_keywords")
    graph.add_edge("extract_jd_keywords", "scan_resume_content")
    graph.add_edge("scan_resume_content", "calculate_ats_score")
    graph.add_edge("calculate_ats_score", "check_format_issues")
    graph.add_edge("check_format_issues", "generate_suggestions")
    
    # Conditional routing after suggestions
    graph.add_conditional_edges(
        "generate_suggestions",
        should_continue_optimization,
        {
            "apply": "apply_suggestions",
            "finalize": "finalize_analysis"
        }
    )
    
    # Loop back after applying suggestions
    graph.add_edge("apply_suggestions", "scan_resume_content")
    
    # Final node to end
    graph.add_edge("finalize_analysis", END)
    
    # Compile and return
    return graph.compile()


def create_ats_optimizer_subgraph():
    """
    Create and return the compiled ATS Optimizer subgraph.
    
    This is the main entry point for using the subgraph.
    """
    return build_ats_optimizer_graph()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def optimize_resume_for_ats(
    structured_jd,
    resume_json,
    target_score: int = 95,
    max_iterations: int = 3
) -> Dict[str, Any]:
    """
    Optimize a resume for ATS compliance.
    
    Args:
        structured_jd: StructuredJD object from JD Extractor
        resume_json: ResumeJSON object from Resume Builder
        target_score: Target ATS score (default: 95)
        max_iterations: Maximum optimization iterations (default: 3)
    
    Returns:
        Dict with ats_analysis, optimized_resume, and status
    """
    graph = create_ats_optimizer_subgraph()
    
    initial_state = {
        "structured_jd": structured_jd,
        "resume_json": resume_json,
        "target_score": target_score,
        "max_iterations": max_iterations
    }
    
    result = graph.invoke(initial_state)
    
    return {
        "ats_analysis": result.get("ats_analysis"),
        "optimized_resume": result.get("optimized_resume") or result.get("resume_json"),
        "original_score": result.get("ats_score", 0),
        "keywords_found": result.get("keywords_found", []),
        "keywords_missing": result.get("keywords_missing", []),
        "format_issues": result.get("format_issues", []),
        "suggestions": result.get("suggestions", []),
        "applied_suggestions": result.get("applied_suggestions", []),
        "iterations": result.get("iteration", 0),
        "passed": result.get("passed", False),
        "error": result.get("error_message")
    }


def quick_ats_check(
    resume_json,
    jd_skills: List[str],
    jd_keywords: List[str]
) -> Dict[str, Any]:
    """
    Quick ATS check without full JD structure.
    
    Useful for rapid scoring without optimization.
    """
    from state.state_models import StructuredJD
    
    # Create minimal structured JD
    jd = StructuredJD(
        skills_required=jd_skills,
        keywords=jd_keywords
    )
    
    # Run just the scoring nodes (not full optimization)
    state = ATSOptimizerState(
        structured_jd=jd,
        resume_json=resume_json
    )
    
    # Extract keywords
    result = extract_jd_keywords(state)
    state.target_keywords = result.get("target_keywords", {})
    
    # Scan resume
    result = scan_resume_content(state)
    state.resume_text_by_section = result.get("resume_text_by_section", {})
    state.resume_text_full = result.get("resume_text_full", "")
    
    # Calculate score
    result = calculate_ats_score(state)
    
    return {
        "score": result.get("ats_score", 0),
        "keywords_found": result.get("keywords_found", []),
        "keywords_missing": result.get("keywords_missing", []),
        "keyword_density": result.get("keyword_density", 0)
    }


def get_ats_report(ats_analysis) -> str:
    """
    Generate a human-readable ATS report.
    
    Args:
        ats_analysis: ATSAnalysis object
    
    Returns:
        Formatted report string
    """
    if not ats_analysis:
        return "No ATS analysis available."
    
    lines = [
        "=" * 60,
        "ATS ANALYSIS REPORT",
        "=" * 60,
        "",
        f"📊 Overall Score: {ats_analysis.score}/100",
        f"   Status: {'✅ PASSED' if ats_analysis.passed else '⚠️ NEEDS IMPROVEMENT'}",
        "",
        f"📈 Keyword Coverage: {ats_analysis.keyword_density*100:.1f}%",
        f"   Found: {len(ats_analysis.keywords_found)} keywords",
        f"   Missing: {len(ats_analysis.keywords_missing)} keywords",
        "",
    ]
    
    if ats_analysis.keywords_found:
        lines.append("✅ Keywords Found:")
        lines.append(f"   {', '.join(ats_analysis.keywords_found[:15])}")
        if len(ats_analysis.keywords_found) > 15:
            lines.append(f"   ... +{len(ats_analysis.keywords_found) - 15} more")
        lines.append("")
    
    if ats_analysis.keywords_missing:
        lines.append("❌ Keywords Missing:")
        lines.append(f"   {', '.join(ats_analysis.keywords_missing[:15])}")
        if len(ats_analysis.keywords_missing) > 15:
            lines.append(f"   ... +{len(ats_analysis.keywords_missing) - 15} more")
        lines.append("")
    
    if ats_analysis.format_issues:
        lines.append("⚠️ Format Issues:")
        for issue in ats_analysis.format_issues[:5]:
            lines.append(f"   • {issue}")
        lines.append("")
    
    if ats_analysis.section_scores:
        lines.append("📋 Section Scores:")
        for section, score in ats_analysis.section_scores.items():
            lines.append(f"   {section}: {score}/100")
        lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "build_ats_optimizer_graph",
    "create_ats_optimizer_subgraph",
    "optimize_resume_for_ats",
    "quick_ats_check",
    "get_ats_report"
]
