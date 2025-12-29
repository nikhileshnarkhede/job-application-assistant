"""
Parent Graph Builder

Constructs the LangGraph StateGraph with all nodes and edges.
"""

from langgraph.graph import StateGraph, START, END

from pipeline.state import ParentGraphState
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


def build_parent_graph(checkpointer=None):
    """
    Build the complete parent graph.
    
    Graph Flow:
    ```
    START
      │
      ▼
    extract_jd ──► match_skills ──► select_experiences ──► rank_projects
                                                              │
      ┌───────────────────────────────────────────────────────┘
      │
      ▼
    rewrite_content ──► build_resume ──► optimize_ats ──► check_compliance
                                                              │
      ┌───────────────────────────────────────────────────────┘
      │
      ▼
    generate_cover_letter ──► check_cl_compliance ──► generate_email
                                                           │
      ┌────────────────────────────────────────────────────┘
      │
      ▼
    save_to_excel ──► save_outputs ──► END
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
    # Linear flow through all 12 stages
    graph.add_edge(START, "extract_jd")
    graph.add_edge("extract_jd", "match_skills")
    graph.add_edge("match_skills", "select_experiences")
    graph.add_edge("select_experiences", "rank_projects")
    graph.add_edge("rank_projects", "rewrite_content")
    graph.add_edge("rewrite_content", "build_resume")
    graph.add_edge("build_resume", "optimize_ats")
    graph.add_edge("optimize_ats", "check_compliance")
    graph.add_edge("check_compliance", "generate_cover_letter")
    graph.add_edge("generate_cover_letter", "check_cl_compliance")
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
    └─────────────────────────────────────────────────────────────┘
    
    ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐
    │  1. Extract  │──►│  2. Match    │──►│  3a. Select          │
    │     JD       │   │    Skills    │   │      Experiences     │
    └──────────────┘   └──────────────┘   └──────────┬───────────┘
                                                      │
                                                      ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐
    │  4. Rewrite  │◄──│ 3b. Rank     │◄──│                      │
    │    Content   │   │   Projects   │   │                      │
    └──────┬───────┘   └──────────────┘   └──────────────────────┘
           │
           ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐
    │  5. Build    │──►│  6. ATS      │──►│  7. Compliance       │
    │    Resume    │   │   Optimize   │   │      Check           │
    └──────────────┘   └──────────────┘   └──────────┬───────────┘
                                                      │
                                                      ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐
    │  8. Cover    │──►│  9. CL       │──►│  10. Generate        │
    │    Letter    │   │  Compliance  │   │      Email           │
    └──────────────┘   └──────────────┘   └──────────┬───────────┘
                                                      │
                                                      ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐
    │ 11. Excel    │──►│ 12. Save     │──►│        END           │
    │    Tracker   │   │   Outputs    │   │                      │
    └──────────────┘   └──────────────┘   └──────────────────────┘
    """
