"""
JD Extractor Subgraph State

This module defines the state specific to the JD Extractor subgraph.
It inherits from the parent state models but adds subgraph-specific fields.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum

# Import from parent state
import sys
sys.path.append("../..")
from state.state_models import StructuredJD


class JDInputType(str, Enum):
    """Type of JD input."""
    TEXT = "text"
    URL = "url"


class JDExtractorState(BaseModel):
    """
    State for JD Extractor subgraph.
    
    This subgraph handles:
    1. Receiving raw JD (text or URL)
    2. Fetching content if URL
    3. Extracting structured information using LLM
    4. Validating the extraction
    """
    
    # ===== INPUT =====
    raw_jd_text: str = ""
    jd_url: Optional[str] = None
    input_type: str = "text"  # "text" or "url"
    
    # ===== INTERMEDIATE =====
    fetched_content: str = ""  # Content fetched from URL
    fetch_error: Optional[str] = None
    
    # ===== OUTPUT =====
    structured_jd: Optional[StructuredJD] = None
    extraction_error: Optional[str] = None
    
    # ===== CONTROL =====
    extraction_complete: bool = False
    validation_passed: bool = False
    retry_count: int = 0
    max_retries: int = 2
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# STATE UPDATE FUNCTIONS
# ============================================================================

def set_input_text(state: JDExtractorState, text: str) -> JDExtractorState:
    """Set raw JD text as input."""
    state.raw_jd_text = text
    state.input_type = "text"
    return state


def set_input_url(state: JDExtractorState, url: str) -> JDExtractorState:
    """Set URL as input."""
    state.jd_url = url
    state.input_type = "url"
    return state


def set_fetched_content(state: JDExtractorState, content: str) -> JDExtractorState:
    """Set content fetched from URL."""
    state.fetched_content = content
    state.raw_jd_text = content  # Also set as raw_jd_text for processing
    return state


def set_structured_jd(state: JDExtractorState, jd: StructuredJD) -> JDExtractorState:
    """Set the extracted structured JD."""
    state.structured_jd = jd
    state.extraction_complete = True
    return state


def set_extraction_error(state: JDExtractorState, error: str) -> JDExtractorState:
    """Set extraction error."""
    state.extraction_error = error
    state.retry_count += 1
    return state


# ============================================================================
# VALIDATION
# ============================================================================

def validate_structured_jd(jd: StructuredJD) -> tuple[bool, list[str]]:
    """
    Validate the extracted structured JD.
    
    Returns:
        tuple: (is_valid, list of issues)
    """
    issues = []
    
    # Required fields check
    if not jd.company_name:
        issues.append("Missing company_name")
    
    if not jd.role_title:
        issues.append("Missing role_title")
    
    if not jd.skills_required and not jd.skills_preferred:
        issues.append("No skills extracted")
    
    if not jd.keywords:
        issues.append("No keywords extracted for ATS")
    
    if not jd.responsibilities:
        issues.append("No responsibilities extracted")
    
    # Role type validation
    valid_role_types = [
        "ml_ai", "data_science", "research", "software_engineering",
        "data_engineering", "scientific_ai", "llm_ai_agents", 
        "robotics_automation", "other"
    ]
    if jd.role_type not in valid_role_types:
        issues.append(f"Invalid role_type: {jd.role_type}")
    
    # Confidence check
    if jd.extraction_confidence < 0.5:
        issues.append(f"Low extraction confidence: {jd.extraction_confidence}")
    
    is_valid = len(issues) == 0
    
    return is_valid, issues


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "JDInputType",
    "JDExtractorState",
    "set_input_text",
    "set_input_url",
    "set_fetched_content",
    "set_structured_jd",
    "set_extraction_error",
    "validate_structured_jd"
]
