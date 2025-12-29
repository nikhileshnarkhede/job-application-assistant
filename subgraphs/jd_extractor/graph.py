"""
JD Extractor Subgraph Builder

This module builds the complete JD Extractor subgraph using LangGraph.

Graph Flow:
```
                    ┌─────────────────────────────────────────────────┐
                    │                                                 │
    START ──► input_router ──┬──► url_fetcher ──► jd_extractor ──►─┤
                             │                         │             │
                             └─────────────────────►───┘             │
                                    (text input)                     │
                                                                     │
                             ┌───────────────────────────────────────┘
                             │
                             ▼
                      validation_node ──┬──► END (success)
                             │          │
                             │          └──► error_handler ──► END (failure)
                             │                    │
                             └────────────────────┘ (retry loop)
```
"""

from typing import Dict, Any, TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Import state and nodes
from subgraphs.jd_extractor.state import JDExtractorState
from subgraphs.jd_extractor.nodes import (
    input_router,
    url_fetcher,
    jd_extractor,
    validation_node,
    error_handler,
    route_by_input_type,
    route_after_validation
)


def build_jd_extractor_graph() -> StateGraph:
    """
    Build the JD Extractor subgraph.
    
    Returns:
        Compiled StateGraph for JD extraction
    """
    # Create graph with state schema
    graph = StateGraph(JDExtractorState)
    
    # ===== ADD NODES =====
    
    graph.add_node("input_router", input_router)
    graph.add_node("url_fetcher", url_fetcher)
    graph.add_node("jd_extractor", jd_extractor)
    graph.add_node("validation_node", validation_node)
    graph.add_node("error_handler", error_handler)
    
    # ===== ADD EDGES =====
    
    # Start -> Input Router
    graph.add_edge(START, "input_router")
    
    # Input Router -> Conditional routing
    graph.add_conditional_edges(
        "input_router",
        route_by_input_type,
        {
            "fetch_url": "url_fetcher",
            "extract": "jd_extractor",
            "error": "error_handler"
        }
    )
    
    # URL Fetcher -> JD Extractor
    graph.add_edge("url_fetcher", "jd_extractor")
    
    # JD Extractor -> Validation
    graph.add_edge("jd_extractor", "validation_node")
    
    # Validation -> Conditional routing
    graph.add_conditional_edges(
        "validation_node",
        route_after_validation,
        {
            "end": END,
            "retry": "jd_extractor",  # Retry extraction
            "error": "error_handler"
        }
    )
    
    # Error Handler -> End
    graph.add_edge("error_handler", END)
    
    # Compile and return
    return graph.compile()


def create_jd_extractor_subgraph():
    """
    Create and return the compiled JD Extractor subgraph.
    
    This is the main entry point for using the subgraph.
    
    Usage:
        subgraph = create_jd_extractor_subgraph()
        
        # For text input:
        result = subgraph.invoke({
            "raw_jd_text": "Job description text here..."
        })
        
        # For URL input:
        result = subgraph.invoke({
            "jd_url": "https://example.com/job-posting"
        })
    """
    return build_jd_extractor_graph()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def extract_jd_from_text(text: str) -> Dict[str, Any]:
    """
    Extract structured JD from text.
    
    Args:
        text: Raw job description text
    
    Returns:
        Dict with structured_jd and any errors
    """
    graph = create_jd_extractor_subgraph()
    
    initial_state = {
        "raw_jd_text": text,
        "input_type": "text"
    }
    
    result = graph.invoke(initial_state)
    
    return {
        "structured_jd": result.get("structured_jd"),
        "error": result.get("extraction_error"),
        "validation_passed": result.get("validation_passed", False)
    }


def extract_jd_from_url(url: str) -> Dict[str, Any]:
    """
    Extract structured JD from URL.
    
    Args:
        url: URL to job posting
    
    Returns:
        Dict with structured_jd and any errors
    """
    graph = create_jd_extractor_subgraph()
    
    initial_state = {
        "jd_url": url,
        "input_type": "url"
    }
    
    result = graph.invoke(initial_state)
    
    return {
        "structured_jd": result.get("structured_jd"),
        "fetched_content": result.get("fetched_content"),
        "error": result.get("extraction_error"),
        "validation_passed": result.get("validation_passed", False)
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "build_jd_extractor_graph",
    "create_jd_extractor_subgraph",
    "extract_jd_from_text",
    "extract_jd_from_url"
]
