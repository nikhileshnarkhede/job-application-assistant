"""
Experience Rewriter Subgraph Builder

This module builds the complete Experience Rewriter subgraph using LangGraph.

Graph Flow:
```
    START
      │
      ▼
┌─────────────────────┐
│   load_resources    │  ← Load action verbs
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  prepare_keywords   │  ← Extract target keywords from JD
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ rewrite_experiences │  ← LLM rewriting with metrics
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  rewrite_projects   │  ← LLM rewriting for projects
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  validate_rewrites  │  ← Check quality & keywords
└──────────┬──────────┘
           │
           ▼
         END
```
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END

# Import state and nodes
from subgraphs.experience_rewriter.state import ExperienceRewriterState
from subgraphs.experience_rewriter.nodes import (
    load_resources,
    prepare_keywords,
    rewrite_experiences,
    rewrite_projects,
    validate_rewrites
)


def build_experience_rewriter_graph() -> StateGraph:
    """
    Build the Experience Rewriter subgraph.
    
    Returns:
        Compiled StateGraph for experience rewriting
    """
    # Create graph with state schema
    graph = StateGraph(ExperienceRewriterState)
    
    # ===== ADD NODES =====
    graph.add_node("load_resources", load_resources)
    graph.add_node("prepare_keywords", prepare_keywords)
    graph.add_node("rewrite_experiences", rewrite_experiences)
    graph.add_node("rewrite_projects", rewrite_projects)
    graph.add_node("validate_rewrites", validate_rewrites)
    
    # ===== ADD EDGES =====
    # Linear flow for this subgraph
    graph.add_edge(START, "load_resources")
    graph.add_edge("load_resources", "prepare_keywords")
    graph.add_edge("prepare_keywords", "rewrite_experiences")
    graph.add_edge("rewrite_experiences", "rewrite_projects")
    graph.add_edge("rewrite_projects", "validate_rewrites")
    graph.add_edge("validate_rewrites", END)
    
    # Compile and return
    return graph.compile()


def create_experience_rewriter_subgraph():
    """
    Create and return the compiled Experience Rewriter subgraph.
    
    This is the main entry point for using the subgraph.
    """
    return build_experience_rewriter_graph()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def rewrite_for_jd(
    structured_jd,
    selected_experiences: List,
    selected_projects: List
) -> Dict[str, Any]:
    """
    Rewrite experiences and projects for a job description.
    
    Args:
        structured_jd: StructuredJD object from JD Extractor
        selected_experiences: List of SelectedExperience from Experience Selector
        selected_projects: List of SelectedProject from GitHub Ranker
    
    Returns:
        Dict with rewritten_experiences, rewritten_projects, and metrics
    """
    graph = create_experience_rewriter_subgraph()
    
    initial_state = {
        "structured_jd": structured_jd,
        "selected_experiences": selected_experiences,
        "selected_projects": selected_projects
    }
    
    result = graph.invoke(initial_state)
    
    return {
        "rewritten_experiences": result.get("rewritten_experiences", []),
        "rewritten_projects": result.get("rewritten_projects", []),
        "keywords_incorporated": result.get("keywords_incorporated", []),
        "incorporation_rate": result.get("incorporation_rate", 0),
        "target_keywords": result.get("target_keywords", []),
        "error": result.get("error_message"),
        "rewrite_complete": result.get("rewrite_complete", False)
    }


def quick_rewrite(
    experiences: List,
    projects: List,
    target_keywords: List[str],
    company_name: str = "Target Company",
    role_title: str = "Target Role"
) -> Dict[str, Any]:
    """
    Quick rewrite without full JD structure.
    
    Useful for testing or simple rewriting scenarios.
    """
    from state.state_models import StructuredJD
    
    # Create minimal structured JD
    jd = StructuredJD(
        company_name=company_name,
        role_title=role_title,
        skills_required=target_keywords[:10],
        skills_preferred=target_keywords[10:20],
        keywords=target_keywords
    )
    
    return rewrite_for_jd(
        structured_jd=jd,
        selected_experiences=experiences,
        selected_projects=projects
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "build_experience_rewriter_graph",
    "create_experience_rewriter_subgraph",
    "rewrite_for_jd",
    "quick_rewrite"
]
