"""
Resume Builder Subgraph

This module builds the complete Resume Builder subgraph using LangGraph.

Graph Flow:
```
    START
      │
      ▼
┌─────────────────────────┐
│   load_candidate_data   │  ← Header, education, certs, publications
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│     tailor_summary      │  ← LLM: JD-tailored professional summary
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    optimize_skills      │  ← Reorder by JD relevance
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   format_experiences    │  ← Structure for resume
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    format_projects      │  ← Structure for resume
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    assemble_resume      │  ← Combine into ResumeJSON
└───────────┬─────────────┘
            │
            ▼
          END
```
"""

from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, START, END

# Import state and nodes
from subgraphs.resume_builder.state import ResumeBuilderState
from subgraphs.resume_builder.nodes import (
    load_candidate_data,
    tailor_summary,
    optimize_skills,
    format_experiences,
    format_projects,
    assemble_resume
)


def build_resume_builder_graph() -> StateGraph:
    """
    Build the Resume Builder subgraph.
    
    Returns:
        Compiled StateGraph for resume building
    """
    # Create graph with state schema
    graph = StateGraph(ResumeBuilderState)
    
    # ===== ADD NODES =====
    graph.add_node("load_candidate_data", load_candidate_data)
    graph.add_node("tailor_summary", tailor_summary)
    graph.add_node("optimize_skills", optimize_skills)
    graph.add_node("format_experiences", format_experiences)
    graph.add_node("format_projects", format_projects)
    graph.add_node("assemble_resume", assemble_resume)
    
    # ===== ADD EDGES =====
    # Linear flow
    graph.add_edge(START, "load_candidate_data")
    graph.add_edge("load_candidate_data", "tailor_summary")
    graph.add_edge("tailor_summary", "optimize_skills")
    graph.add_edge("optimize_skills", "format_experiences")
    graph.add_edge("format_experiences", "format_projects")
    graph.add_edge("format_projects", "assemble_resume")
    graph.add_edge("assemble_resume", END)
    
    # Compile and return
    return graph.compile()


def create_resume_builder_subgraph():
    """
    Create and return the compiled Resume Builder subgraph.
    
    This is the main entry point for using the subgraph.
    """
    return build_resume_builder_graph()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def build_resume(
    structured_jd,
    rewritten_experiences: List,
    rewritten_projects: List,
    skill_match_result=None
) -> Dict[str, Any]:
    """
    Build a complete resume tailored to a job description.
    
    Args:
        structured_jd: StructuredJD object from JD Extractor
        rewritten_experiences: List of SelectedExperience from Experience Rewriter
        rewritten_projects: List of SelectedProject from Experience Rewriter
        skill_match_result: Optional SkillMatchResult from Skill Matcher
    
    Returns:
        Dict with resume_json and build status
    """
    graph = create_resume_builder_subgraph()
    
    initial_state = {
        "structured_jd": structured_jd,
        "rewritten_experiences": rewritten_experiences,
        "rewritten_projects": rewritten_projects,
        "skill_match_result": skill_match_result
    }
    
    result = graph.invoke(initial_state)
    
    return {
        "resume_json": result.get("resume_json"),
        "tailored_summary": result.get("tailored_summary", ""),
        "optimized_skills": result.get("optimized_skills", {}),
        "error": result.get("error_message"),
        "build_complete": result.get("build_complete", False)
    }


def build_general_resume(
    rewritten_experiences: List,
    rewritten_projects: List
) -> Dict[str, Any]:
    """
    Build a general resume without JD tailoring.
    
    Useful for creating a base resume.
    """
    return build_resume(
        structured_jd=None,
        rewritten_experiences=rewritten_experiences,
        rewritten_projects=rewritten_projects,
        skill_match_result=None
    )


def resume_to_dict(resume_json) -> Dict[str, Any]:
    """
    Convert ResumeJSON to a plain dictionary.
    
    Useful for serialization or template rendering.
    """
    if resume_json is None:
        return {}
    
    return {
        "header": resume_json.header,
        "summary": resume_json.summary,
        "education": resume_json.education,
        "certifications": resume_json.certifications,
        "experience": resume_json.experience,
        "projects": resume_json.projects,
        "skills": resume_json.skills,
        "publications": resume_json.publications,
        "metadata": {
            "version": resume_json.version,
            "last_modified": resume_json.last_modified,
            "tailored_for": resume_json.tailored_for
        }
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "build_resume_builder_graph",
    "create_resume_builder_subgraph",
    "build_resume",
    "build_general_resume",
    "resume_to_dict"
]
