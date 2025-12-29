"""
JD Extractor Subgraph

Extracts structured information from job descriptions.
Supports both text input and URL input.

Usage:
    from subgraphs.jd_extractor import extract_jd_from_text, extract_jd_from_url
    
    # From text:
    result = extract_jd_from_text("Job description here...")
    structured_jd = result["structured_jd"]
    
    # From URL:
    result = extract_jd_from_url("https://example.com/job")
    structured_jd = result["structured_jd"]
"""

from subgraphs.jd_extractor.graph import (
    build_jd_extractor_graph,
    create_jd_extractor_subgraph,
    extract_jd_from_text,
    extract_jd_from_url
)

from subgraphs.jd_extractor.state import (
    JDExtractorState,
    JDInputType,
    validate_structured_jd
)

from subgraphs.jd_extractor.nodes import (
    input_router,
    url_fetcher,
    jd_extractor,
    validation_node,
    error_handler
)

__all__ = [
    # Main functions
    "extract_jd_from_text",
    "extract_jd_from_url",
    
    # Graph builders
    "build_jd_extractor_graph",
    "create_jd_extractor_subgraph",
    
    # State
    "JDExtractorState",
    "JDInputType",
    "validate_structured_jd",
    
    # Nodes (for custom graph building)
    "input_router",
    "url_fetcher",
    "jd_extractor",
    "validation_node",
    "error_handler"
]
