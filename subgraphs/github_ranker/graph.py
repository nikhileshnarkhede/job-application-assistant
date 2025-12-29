"""
GitHub Ranker Subgraph Builder

This module builds the complete GitHub Ranker subgraph using LangGraph.

Graph Flow:
```
    START
      │
      ▼
┌─────────────────────┐
│   load_projects     │  ← Load from cache/JSON/API
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│extract_jd_requirements│  ← Get skills/keywords from JD
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   score_projects    │  ← Calculate relevance scores
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ select_top_projects │  ← Pick top N projects
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  generate_bullets   │  ← Create resume bullets (LLM)
└──────────┬──────────┘
           │
           ▼
         END
```
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END

# Import state and nodes
from subgraphs.github_ranker.state import GitHubRankerState
from subgraphs.github_ranker.nodes import (
    load_projects,
    extract_jd_requirements,
    score_projects,
    select_top_projects,
    generate_bullets
)


def build_github_ranker_graph() -> StateGraph:
    """
    Build the GitHub Ranker subgraph.
    
    Returns:
        Compiled StateGraph for project ranking
    """
    # Create graph with state schema
    graph = StateGraph(GitHubRankerState)
    
    # ===== ADD NODES =====
    graph.add_node("load_projects", load_projects)
    graph.add_node("extract_jd_requirements", extract_jd_requirements)
    graph.add_node("score_projects", score_projects)
    graph.add_node("select_top_projects", select_top_projects)
    graph.add_node("generate_bullets", generate_bullets)
    
    # ===== ADD EDGES =====
    # Linear flow for this subgraph
    graph.add_edge(START, "load_projects")
    graph.add_edge("load_projects", "extract_jd_requirements")
    graph.add_edge("extract_jd_requirements", "score_projects")
    graph.add_edge("score_projects", "select_top_projects")
    graph.add_edge("select_top_projects", "generate_bullets")
    graph.add_edge("generate_bullets", END)
    
    # Compile and return
    return graph.compile()


def create_github_ranker_subgraph():
    """
    Create and return the compiled GitHub Ranker subgraph.
    
    This is the main entry point for using the subgraph.
    """
    return build_github_ranker_graph()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def rank_github_projects(
    structured_jd,
    max_projects: int = 3
) -> Dict[str, Any]:
    """
    Rank GitHub projects by relevance to job description.
    
    Args:
        structured_jd: StructuredJD object from JD Extractor
        max_projects: Maximum number of projects to select (default: 3)
    
    Returns:
        Dict with selected_projects and any errors
    """
    graph = create_github_ranker_subgraph()
    
    initial_state = {
        "structured_jd": structured_jd,
        "max_projects": max_projects
    }
    
    result = graph.invoke(initial_state)
    
    return {
        "selected_projects": result.get("selected_projects", []),
        "all_projects_count": len(result.get("all_projects", [])),
        "projects_source": result.get("projects_source", ""),
        "error": result.get("error_message"),
        "ranking_complete": result.get("ranking_complete", False)
    }


def get_top_projects_for_jd(
    jd_skills: List[str],
    jd_keywords: List[str],
    role_type: str = "ml_ai",
    max_projects: int = 3
) -> Dict[str, Any]:
    """
    Quick project ranking without full JD structure.
    
    Useful for testing or simple ranking scenarios.
    
    Args:
        jd_skills: List of skills from JD
        jd_keywords: List of keywords from JD
        role_type: Type of role (ml_ai, data_science, etc.)
        max_projects: Maximum projects to return
    
    Returns:
        Dict with ranked projects
    """
    from state.state_models import StructuredJD
    
    # Create minimal structured JD
    jd = StructuredJD(
        skills_required=jd_skills,
        skills_preferred=[],
        keywords=jd_keywords,
        role_type=role_type
    )
    
    return rank_github_projects(
        structured_jd=jd,
        max_projects=max_projects
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "build_github_ranker_graph",
    "create_github_ranker_subgraph",
    "rank_github_projects",
    "get_top_projects_for_jd"
]
