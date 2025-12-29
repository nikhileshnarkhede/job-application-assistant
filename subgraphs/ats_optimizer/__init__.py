"""
ATS Optimizer Subgraph

Optimizes resumes for Applicant Tracking Systems (ATS) with 95%+ keyword match.

Key Features:
- Extracts and weights keywords from job description
- Scans resume for keyword matches (exact + fuzzy + aliases)
- Calculates weighted ATS score (0-100)
- Checks format compliance
- Generates specific improvement suggestions via LLM
- Applies suggestions iteratively until target score reached

Usage:
    from subgraphs.ats_optimizer import optimize_resume_for_ats, get_ats_report
    
    result = optimize_resume_for_ats(
        structured_jd=structured_jd,
        resume_json=resume_json,
        target_score=95,
        max_iterations=3
    )
    
    print(f"ATS Score: {result['ats_analysis'].score}/100")
    print(f"Passed: {result['passed']}")
    
    # Get formatted report
    report = get_ats_report(result['ats_analysis'])
    print(report)
"""

from subgraphs.ats_optimizer.graph import (
    build_ats_optimizer_graph,
    create_ats_optimizer_subgraph,
    optimize_resume_for_ats,
    quick_ats_check,
    get_ats_report
)

from subgraphs.ats_optimizer.state import (
    ATSOptimizerState,
    KEYWORD_WEIGHTS,
    SECTION_WEIGHTS,
    SCORE_WEIGHTS,
    SKILL_ALIASES,
    FORMAT_CHECKS
)

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

__all__ = [
    # Main functions
    "optimize_resume_for_ats",
    "quick_ats_check",
    "get_ats_report",
    
    # Graph builders
    "build_ats_optimizer_graph",
    "create_ats_optimizer_subgraph",
    
    # State & Config
    "ATSOptimizerState",
    "KEYWORD_WEIGHTS",
    "SECTION_WEIGHTS",
    "SCORE_WEIGHTS",
    "SKILL_ALIASES",
    "FORMAT_CHECKS",
    
    # Nodes (for custom graph building)
    "extract_jd_keywords",
    "scan_resume_content",
    "calculate_ats_score",
    "check_format_issues",
    "generate_suggestions",
    "apply_suggestions",
    "finalize_analysis",
    "should_continue_optimization"
]
