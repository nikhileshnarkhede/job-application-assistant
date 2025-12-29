"""
Experience Selector Subgraph

Selects and ranks candidate experiences by relevance to job description.

Usage:
    from subgraphs.experience_selector import select_experiences_for_jd
    
    # With structured JD (from JD Extractor):
    result = select_experiences_for_jd(structured_jd, max_experiences=4)
    
    for exp in result["selected_experiences"]:
        print(f"{exp.role} @ {exp.company} - Score: {exp.relevance_score}")
        for bullet in exp.original_bullets[:3]:
            print(f"  • {bullet}")
"""

from subgraphs.experience_selector.graph import (
    build_experience_selector_graph,
    create_experience_selector_subgraph,
    select_experiences_for_jd,
    quick_experience_selection
)

from subgraphs.experience_selector.state import (
    ExperienceSelectorState,
    SCORING_WEIGHTS,
    TIER_SCORES,
    RECENCY_SCORES
)

from subgraphs.experience_selector.nodes import (
    load_experiences,
    extract_jd_requirements,
    score_experiences,
    select_top_experiences,
    prepare_for_rewriting
)

__all__ = [
    # Main functions
    "select_experiences_for_jd",
    "quick_experience_selection",
    
    # Graph builders
    "build_experience_selector_graph",
    "create_experience_selector_subgraph",
    
    # State
    "ExperienceSelectorState",
    "SCORING_WEIGHTS",
    "TIER_SCORES",
    "RECENCY_SCORES",
    
    # Nodes (for custom graph building)
    "load_experiences",
    "extract_jd_requirements",
    "score_experiences",
    "select_top_experiences",
    "prepare_for_rewriting"
]
