"""
Skill Matcher Subgraph

Matches candidate skills against job description requirements.
Provides match percentage, gap analysis, and recommendations.

Usage:
    from subgraphs.skill_matcher import match_skills_to_jd, quick_skill_match
    
    # With structured JD (from JD Extractor):
    result = match_skills_to_jd(structured_jd)
    print(result["skill_match_result"].match_percentage)
    print(result["skill_match_result"].matched_skills)
    print(result["skill_match_result"].missing_skills)
    
    # Quick match (for testing):
    result = quick_skill_match(
        jd_skills_required=["Python", "TensorFlow"],
        jd_skills_preferred=["Docker"],
        candidate_skills=["Python", "PyTorch", "Docker"]
    )
"""

from subgraphs.skill_matcher.graph import (
    build_skill_matcher_graph,
    create_skill_matcher_subgraph,
    match_skills_to_jd,
    quick_skill_match
)

from subgraphs.skill_matcher.state import (
    SkillMatcherState,
    normalize_skill,
    normalize_skills_list,
    SKILL_ALIASES
)

from subgraphs.skill_matcher.nodes import (
    load_candidate_skills,
    extract_jd_skills,
    match_skills,
    analyze_gaps,
    build_result
)

__all__ = [
    # Main functions
    "match_skills_to_jd",
    "quick_skill_match",
    
    # Graph builders
    "build_skill_matcher_graph",
    "create_skill_matcher_subgraph",
    
    # State
    "SkillMatcherState",
    "normalize_skill",
    "normalize_skills_list",
    "SKILL_ALIASES",
    
    # Nodes (for custom graph building)
    "load_candidate_skills",
    "extract_jd_skills",
    "match_skills",
    "analyze_gaps",
    "build_result"
]
