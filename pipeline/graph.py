"""
Parent Graph Builder

Constructs the LangGraph StateGraph with all nodes and conditional edges.
"""

from langgraph.graph import StateGraph, START, END

from pipeline.state import ParentGraphState
from pipeline.config import PIPELINE_CONFIG, ATS_CONFIG
from pipeline.nodes import (
    # Node functions
    node_extract_jd,
    node_match_skills,
    node_select_experiences,
    node_rank_projects,
    node_rewrite_content,
    node_build_resume,
    node_optimize_ats,
    node_check_compliance,
    node_generate_cover_letter,
    node_check_cl_compliance,
    node_generate_email,
    node_save_to_excel,
    node_save_outputs,
)


# ============================================================================
# CONDITIONAL EDGE FUNCTIONS
# ============================================================================

def route_after_extraction(state: ParentGraphState) -> str:
    """
    Route after JD extraction.
    
    Returns:
        "continue" if extraction succeeded
        "end_early" if extraction failed (skip everything)
    """
    if state.extraction_error:
        print(f"   ⚠️  Extraction failed, ending pipeline early")
        return "end_early"
    
    if not state.structured_jd:
        print(f"   ⚠️  No structured JD, ending pipeline early")
        return "end_early"
    
    return "continue"


def route_after_resume_build(state: ParentGraphState) -> str:
    """
    Route after resume building.
    
    Returns:
        "optimize" if resume was built
        "skip_optimization" if no resume (go to cover letter)
    """
    if not state.resume_json:
        print(f"   ⚠️  No resume built, skipping optimization")
        return "skip_optimization"
    
    return "optimize"


def route_after_ats(state: ParentGraphState) -> str:
    """
    Route after ATS optimization.
    
    Returns:
        "retry_ats" if score below threshold and iterations remaining
        "continue" to proceed to compliance check
    """
    target = ATS_CONFIG["target_score"]
    max_iter = PIPELINE_CONFIG["max_ats_iterations"]
    
    if state.ats_passed:
        return "continue"
    
    if state.ats_score >= target:
        return "continue"
    
    if state.ats_iteration < max_iter:
        print(f"   🔄 ATS score {state.ats_score:.1f}% < {target}%, retrying...")
        return "retry_ats"
    
    print(f"   ⚠️  Max ATS iterations ({max_iter}) reached")
    return "continue"


def route_after_compliance(state: ParentGraphState) -> str:
    """
    Route after compliance check.
    
    Returns:
        "retry_compliance" if score below threshold and iterations remaining
        "continue" to proceed to cover letter
    """
    threshold = PIPELINE_CONFIG["compliance_pass_threshold"]
    max_iter = PIPELINE_CONFIG["max_compliance_iterations"]
    
    if state.compliance_passed:
        return "continue"
    
    if state.compliance_score >= threshold:
        return "continue"
    
    # For now, don't retry compliance (would need resume modification logic)
    # Just continue even if below threshold
    return "continue"


def route_after_cover_letter(state: ParentGraphState) -> str:
    """
    Route after cover letter generation.
    
    Returns:
        "check_compliance" if cover letter was generated
        "skip_cl_compliance" if no cover letter
    """
    if not state.cover_letter_text:
        return "skip_cl_compliance"
    
    return "check_compliance"


# ============================================================================
# GRAPH BUILDER
# ============================================================================

def build_parent_graph(checkpointer=None):
    """
    Build the complete parent graph with conditional edges.
    
    Graph Flow:
    ```
    START
      │
      ▼
    extract_jd ──────────────────────────────────────────┐
      │                                                  │
      ├─[extraction_failed]─────────────────────────────►│
      │                                                  │
      ▼ [continue]                                       │
    match_skills                                         │
      │                                                  │
      ▼                                                  │
    select_experiences                                   │
      │                                                  │
      ▼                                                  │
    rank_projects                                        │
      │                                                  │
      ▼                                                  │
    rewrite_content                                      │
      │                                                  │
      ▼                                                  │
    build_resume ────────────────────────┐               │
      │                                  │               │
      ├─[no_resume]─────────────────────►├──────────────►│
      │                                  │               │
      ▼ [optimize]                       │               │
    optimize_ats ◄───────────────────┐   │               │
      │                              │   │               │
      ├─[retry_ats]──────────────────┘   │               │
      │                                  │               │
      ▼ [continue]                       │               │
    check_compliance                     │               │
      │                                  │               │
      ▼                                  │               │
    generate_cover_letter ◄──────────────┘               │
      │                                                  │
      ├─[no_cover_letter]────────────────┐               │
      │                                  │               │
      ▼ [check_compliance]               │               │
    check_cl_compliance                  │               │
      │                                  │               │
      ▼                                  ▼               │
    generate_email ◄─────────────────────┘               │
      │                                                  │
      ▼                                                  │
    save_to_excel                                        │
      │                                                  │
      ▼                                                  │
    save_outputs ◄───────────────────────────────────────┘
      │
      ▼
     END
    ```
    
    Args:
        checkpointer: Optional checkpointer for state persistence
        
    Returns:
        Compiled StateGraph
    """
    # Create graph with state schema
    graph = StateGraph(ParentGraphState)
    
    # ========== ADD NODES ==========
    graph.add_node("extract_jd", node_extract_jd)
    graph.add_node("match_skills", node_match_skills)
    graph.add_node("select_experiences", node_select_experiences)
    graph.add_node("rank_projects", node_rank_projects)
    graph.add_node("rewrite_content", node_rewrite_content)
    graph.add_node("build_resume", node_build_resume)
    graph.add_node("optimize_ats", node_optimize_ats)
    graph.add_node("check_compliance", node_check_compliance)
    graph.add_node("generate_cover_letter", node_generate_cover_letter)
    graph.add_node("check_cl_compliance", node_check_cl_compliance)
    graph.add_node("generate_email", node_generate_email)
    graph.add_node("save_to_excel", node_save_to_excel)
    graph.add_node("save_outputs", node_save_outputs)
    
    # ========== ADD EDGES ==========
    
    # START -> extract_jd
    graph.add_edge(START, "extract_jd")
    
    # extract_jd -> (conditional)
    graph.add_conditional_edges(
        "extract_jd",
        route_after_extraction,
        {
            "continue": "match_skills",
            "end_early": "save_outputs"  # Skip to end if extraction failed
        }
    )
    
    # Linear flow through selection stages
    graph.add_edge("match_skills", "select_experiences")
    graph.add_edge("select_experiences", "rank_projects")
    graph.add_edge("rank_projects", "rewrite_content")
    graph.add_edge("rewrite_content", "build_resume")
    
    # build_resume -> (conditional)
    graph.add_conditional_edges(
        "build_resume",
        route_after_resume_build,
        {
            "optimize": "optimize_ats",
            "skip_optimization": "generate_cover_letter"  # Skip ATS/compliance if no resume
        }
    )
    
    # optimize_ats -> (conditional with retry loop)
    graph.add_conditional_edges(
        "optimize_ats",
        route_after_ats,
        {
            "retry_ats": "optimize_ats",  # Retry loop
            "continue": "check_compliance"
        }
    )
    
    # check_compliance -> (conditional - could add retry loop here too)
    graph.add_conditional_edges(
        "check_compliance",
        route_after_compliance,
        {
            "retry_compliance": "build_resume",  # Would rebuild resume (not implemented)
            "continue": "generate_cover_letter"
        }
    )
    
    # generate_cover_letter -> (conditional)
    graph.add_conditional_edges(
        "generate_cover_letter",
        route_after_cover_letter,
        {
            "check_compliance": "check_cl_compliance",
            "skip_cl_compliance": "generate_email"
        }
    )
    
    # Linear flow to end
    graph.add_edge("check_cl_compliance", "generate_email")
    graph.add_edge("generate_email", "save_to_excel")
    graph.add_edge("save_to_excel", "save_outputs")
    graph.add_edge("save_outputs", END)
    
    # Compile with optional checkpointer
    if checkpointer:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()


def get_graph_visualization():
    """Get ASCII visualization of the graph."""
    return """
    ┌─────────────────────────────────────────────────────────────┐
    │                    JOB APPLICATION PIPELINE                  │
    │                    (with conditional edges)                  │
    └─────────────────────────────────────────────────────────────┘
    
                              START
                                │
                                ▼
                        ┌──────────────┐
                        │  1. Extract  │
                        │      JD      │
                        └──────┬───────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
              [continue]            [end_early]
                    │                     │
                    ▼                     │
            ┌──────────────┐              │
            │  2. Match    │              │
            │    Skills    │              │
            └──────┬───────┘              │
                   │                      │
                   ▼                      │
            ┌──────────────┐              │
            │ 3a. Select   │              │
            │  Experiences │              │
            └──────┬───────┘              │
                   │                      │
                   ▼                      │
            ┌──────────────┐              │
            │ 3b. Rank     │              │
            │   Projects   │              │
            └──────┬───────┘              │
                   │                      │
                   ▼                      │
            ┌──────────────┐              │
            │  4. Rewrite  │              │
            │    Content   │              │
            └──────┬───────┘              │
                   │                      │
                   ▼                      │
            ┌──────────────┐              │
            │  5. Build    │              │
            │    Resume    │              │
            └──────┬───────┘              │
                   │                      │
         ┌─────────┴─────────┐            │
         │                   │            │
    [optimize]        [skip_optimization] │
         │                   │            │
         ▼                   │            │
    ┌──────────────┐         │            │
    │  6. ATS      │◄──┐     │            │
    │   Optimize   │   │     │            │
    └──────┬───────┘   │     │            │
           │           │     │            │
    ┌──────┴──────┐    │     │            │
    │             │    │     │            │
[continue]  [retry_ats]│     │            │
    │             │    │     │            │
    │             └────┘     │            │
    ▼                        │            │
    ┌──────────────┐         │            │
    │ 7. Compliance│         │            │
    │    Check     │         │            │
    └──────┬───────┘         │            │
           │                 │            │
           ▼                 │            │
    ┌──────────────┐◄────────┘            │
    │  8. Cover    │                      │
    │    Letter    │                      │
    └──────┬───────┘                      │
           │                              │
    ┌──────┴──────┐                       │
    │             │                       │
[check_cl]  [skip_cl]                     │
    │             │                       │
    ▼             │                       │
    ┌──────────────┐  │                   │
    │  9. CL       │  │                   │
    │  Compliance  │  │                   │
    └──────┬───────┘  │                   │
           │          │                   │
           ▼          ▼                   │
    ┌──────────────┐◄─┘                   │
    │ 10. Generate │                      │
    │    Email     │                      │
    └──────┬───────┘                      │
           │                              │
           ▼                              │
    ┌──────────────┐                      │
    │ 11. Excel    │                      │
    │   Tracker    │                      │
    └──────┬───────┘                      │
           │                              │
           ▼                              │
    ┌──────────────┐◄─────────────────────┘
    │ 12. Save     │
    │   Outputs    │
    └──────┬───────┘
           │
           ▼
          END
    """
