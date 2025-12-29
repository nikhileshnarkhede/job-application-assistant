"""
Skill Matcher Subgraph Builder

This module builds the complete Skill Matcher subgraph using LangGraph.

Graph Flow:
```
    START
      │
      ▼
┌─────────────────────┐
│ load_candidate_skills│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   extract_jd_skills │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    match_skills     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    analyze_gaps     │  (LLM - optional)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    build_result     │
└──────────┬──────────┘
           │
           ▼
         END
```
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, START, END

# Import state and nodes
from subgraphs.skill_matcher.state import SkillMatcherState
from subgraphs.skill_matcher.nodes import (
    load_candidate_skills,
    extract_jd_skills,
    match_skills,
    analyze_gaps,
    build_result
)


def build_skill_matcher_graph() -> StateGraph:
    """
    Build the Skill Matcher subgraph.
    
    Returns:
        Compiled StateGraph for skill matching
    """
    # Create graph with state schema
    graph = StateGraph(SkillMatcherState)
    
    # ===== ADD NODES =====
    graph.add_node("load_candidate_skills", load_candidate_skills)
    graph.add_node("extract_jd_skills", extract_jd_skills)
    graph.add_node("match_skills", match_skills)
    graph.add_node("analyze_gaps", analyze_gaps)
    graph.add_node("build_result", build_result)
    
    # ===== ADD EDGES =====
    # Linear flow for this subgraph
    graph.add_edge(START, "load_candidate_skills")
    graph.add_edge("load_candidate_skills", "extract_jd_skills")
    graph.add_edge("extract_jd_skills", "match_skills")
    graph.add_edge("match_skills", "analyze_gaps")
    graph.add_edge("analyze_gaps", "build_result")
    graph.add_edge("build_result", END)
    
    # Compile and return
    return graph.compile()


def create_skill_matcher_subgraph():
    """
    Create and return the compiled Skill Matcher subgraph.
    
    This is the main entry point for using the subgraph.
    
    Usage:
        from subgraphs.skill_matcher import match_skills_to_jd
        
        result = match_skills_to_jd(structured_jd)
        print(result["skill_match_result"].match_percentage)
    """
    return build_skill_matcher_graph()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def match_skills_to_jd(
    structured_jd,
    candidate_skills: list = None,
    candidate_keywords: list = None
) -> Dict[str, Any]:
    """
    Match candidate skills against a job description.
    
    Args:
        structured_jd: StructuredJD object from JD Extractor
        candidate_skills: Optional list of candidate skills (loads from file if not provided)
        candidate_keywords: Optional list of candidate keywords
    
    Returns:
        Dict with skill_match_result and any errors
    """
    graph = create_skill_matcher_subgraph()
    
    initial_state = {
        "structured_jd": structured_jd,
        "candidate_skills_flat": candidate_skills or [],
        "candidate_keywords": candidate_keywords or []
    }
    
    result = graph.invoke(initial_state)
    
    return {
        "skill_match_result": result.get("skill_match_result"),
        "error": result.get("error_message"),
        "matching_complete": result.get("matching_complete", False)
    }


def quick_skill_match(
    jd_skills_required: list,
    jd_skills_preferred: list,
    candidate_skills: list
) -> Dict[str, Any]:
    """
    Quick skill matching without full JD structure.
    
    Useful for testing or simple matching scenarios.
    
    Args:
        jd_skills_required: List of required skills from JD
        jd_skills_preferred: List of preferred skills from JD
        candidate_skills: List of candidate skills
    
    Returns:
        Dict with match results
    """
    from state.state_models import StructuredJD
    
    # Create minimal structured JD
    jd = StructuredJD(
        skills_required=jd_skills_required,
        skills_preferred=jd_skills_preferred,
        keywords=jd_skills_required + jd_skills_preferred
    )
    
    return match_skills_to_jd(
        structured_jd=jd,
        candidate_skills=candidate_skills
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "build_skill_matcher_graph",
    "create_skill_matcher_subgraph",
    "match_skills_to_jd",
    "quick_skill_match"
]
