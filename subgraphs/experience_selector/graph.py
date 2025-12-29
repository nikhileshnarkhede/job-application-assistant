"""
Experience Selector Subgraph Builder

This module builds the complete Experience Selector subgraph using LangGraph.

Graph Flow:
```
    START
      │
      ▼
┌─────────────────────┐
│   load_experiences  │  ← Load from candidate_loader
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│extract_jd_requirements│  ← Get skills/keywords from JD
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  score_experiences  │  ← Calculate relevance scores
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│select_top_experiences│  ← Pick top N experiences
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│prepare_for_rewriting│  ← Sort bullets, finalize
└──────────┬──────────┘
           │
           ▼
         END
```
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END

# Import state and nodes
from subgraphs.experience_selector.state import ExperienceSelectorState
from subgraphs.experience_selector.nodes import (
    load_experiences,
    extract_jd_requirements,
    score_experiences,
    select_top_experiences,
    prepare_for_rewriting
)


def build_experience_selector_graph() -> StateGraph:
    """
    Build the Experience Selector subgraph.
    
    Returns:
        Compiled StateGraph for experience selection
    """
    # Create graph with state schema
    graph = StateGraph(ExperienceSelectorState)
    
    # ===== ADD NODES =====
    graph.add_node("load_experiences", load_experiences)
    graph.add_node("extract_jd_requirements", extract_jd_requirements)
    graph.add_node("score_experiences", score_experiences)
    graph.add_node("select_top_experiences", select_top_experiences)
    graph.add_node("prepare_for_rewriting", prepare_for_rewriting)
    
    # ===== ADD EDGES =====
    # Linear flow for this subgraph
    graph.add_edge(START, "load_experiences")
    graph.add_edge("load_experiences", "extract_jd_requirements")
    graph.add_edge("extract_jd_requirements", "score_experiences")
    graph.add_edge("score_experiences", "select_top_experiences")
    graph.add_edge("select_top_experiences", "prepare_for_rewriting")
    graph.add_edge("prepare_for_rewriting", END)
    
    # Compile and return
    return graph.compile()


def create_experience_selector_subgraph():
    """
    Create and return the compiled Experience Selector subgraph.
    
    This is the main entry point for using the subgraph.
    """
    return build_experience_selector_graph()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def select_experiences_for_jd(
    structured_jd,
    max_experiences: int = 4
) -> Dict[str, Any]:
    """
    Select candidate experiences relevant to job description.
    
    Args:
        structured_jd: StructuredJD object from JD Extractor
        max_experiences: Maximum number of experiences to select (default: 4)
    
    Returns:
        Dict with selected_experiences and any errors
    """
    graph = create_experience_selector_subgraph()
    
    initial_state = {
        "structured_jd": structured_jd,
        "max_experiences": max_experiences
    }
    
    result = graph.invoke(initial_state)
    
    return {
        "selected_experiences": result.get("selected_experiences", []),
        "all_experiences_count": len(result.get("all_experiences", [])),
        "error": result.get("error_message"),
        "selection_complete": result.get("selection_complete", False)
    }


def quick_experience_selection(
    jd_skills: List[str],
    jd_keywords: List[str],
    role_type: str = "ml_ai",
    max_experiences: int = 4
) -> Dict[str, Any]:
    """
    Quick experience selection without full JD structure.
    
    Useful for testing or simple selection scenarios.
    
    Args:
        jd_skills: List of skills from JD
        jd_keywords: List of keywords from JD
        role_type: Type of role (ml_ai, data_science, etc.)
        max_experiences: Maximum experiences to return
    
    Returns:
        Dict with selected experiences
    """
    from state.state_models import StructuredJD
    
    # Create minimal structured JD
    jd = StructuredJD(
        skills_required=jd_skills,
        skills_preferred=[],
        keywords=jd_keywords,
        role_type=role_type,
        responsibilities=[]
    )
    
    return select_experiences_for_jd(
        structured_jd=jd,
        max_experiences=max_experiences
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "build_experience_selector_graph",
    "create_experience_selector_subgraph",
    "select_experiences_for_jd",
    "quick_experience_selection"
]
