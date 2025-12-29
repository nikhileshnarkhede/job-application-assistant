"""
Experience Rewriter Subgraph

Rewrites resume bullets with action verbs, metrics, and JD keywords.

Key Features:
- Starts every bullet with strong action verb
- Adds quantifiable metrics (%, numbers, multipliers)
- Incorporates target keywords naturally for ATS optimization
- Validates quality and keyword incorporation rate

Usage:
    from subgraphs.experience_rewriter import rewrite_for_jd
    
    result = rewrite_for_jd(
        structured_jd=structured_jd,
        selected_experiences=selected_experiences,
        selected_projects=selected_projects
    )
    
    for exp in result["rewritten_experiences"]:
        print(f"{exp.role}:")
        for bullet in exp.rewritten_bullets:
            print(f"  • {bullet}")
    
    print(f"Keyword incorporation: {result['incorporation_rate']:.1f}%")
"""

from subgraphs.experience_rewriter.graph import (
    build_experience_rewriter_graph,
    create_experience_rewriter_subgraph,
    rewrite_for_jd,
    quick_rewrite
)

from subgraphs.experience_rewriter.state import (
    ExperienceRewriterState,
    DEFAULT_ACTION_VERBS,
    METRIC_TEMPLATES,
    METRIC_RANGES
)

from subgraphs.experience_rewriter.nodes import (
    load_resources,
    prepare_keywords,
    rewrite_experiences,
    rewrite_projects,
    validate_rewrites
)

__all__ = [
    # Main functions
    "rewrite_for_jd",
    "quick_rewrite",
    
    # Graph builders
    "build_experience_rewriter_graph",
    "create_experience_rewriter_subgraph",
    
    # State
    "ExperienceRewriterState",
    "DEFAULT_ACTION_VERBS",
    "METRIC_TEMPLATES",
    "METRIC_RANGES",
    
    # Nodes (for custom graph building)
    "load_resources",
    "prepare_keywords",
    "rewrite_experiences",
    "rewrite_projects",
    "validate_rewrites"
]
