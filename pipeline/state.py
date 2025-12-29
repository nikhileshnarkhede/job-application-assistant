"""
Parent Graph State

Unified state for the entire pipeline, containing all data passed between nodes.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ParentGraphState(BaseModel):
    """
    Parent graph state - contains all fields needed across pipeline stages.
    
    This is NOT a superset of all subgraph states. Instead, it holds:
    - Input parameters
    - Outputs from each subgraph (as returned by convenience functions)
    - Pipeline control fields
    """
    
    # ===== INPUTS =====
    jd_url: Optional[str] = None
    jd_text: Optional[str] = None
    
    # ===== STAGE 1: JD EXTRACTION =====
    structured_jd: Optional[Any] = None  # StructuredJD object or dict
    extraction_error: Optional[str] = None
    
    # ===== STAGE 2: SKILL MATCHING =====
    skill_match_result: Optional[Any] = None  # SkillMatchResult object or dict
    match_percentage: float = 0.0
    
    # ===== STAGE 3a: EXPERIENCE SELECTION =====
    selected_experiences: List[Any] = Field(default_factory=list)
    
    # ===== STAGE 3b: PROJECT RANKING =====
    selected_projects: List[Any] = Field(default_factory=list)
    
    # ===== STAGE 4: CONTENT REWRITING =====
    rewritten_experiences: List[Any] = Field(default_factory=list)
    rewritten_projects: List[Any] = Field(default_factory=list)
    
    # ===== STAGE 5: RESUME BUILDING =====
    resume_json: Optional[Any] = None  # ResumeJSON object or dict
    
    # ===== STAGE 6: ATS OPTIMIZATION =====
    ats_score: float = 0.0
    ats_passed: bool = False
    ats_iteration: int = 0
    ats_report: Optional[Any] = None
    
    # ===== STAGE 7: COMPLIANCE CHECK =====
    compliance_score: float = 0.0
    compliance_passed: bool = False
    compliance_iteration: int = 0
    compliance_report: Optional[Any] = None
    
    # ===== STAGE 8: COVER LETTER =====
    cover_letter: Optional[Any] = None  # CoverLetter object or dict
    cover_letter_text: str = ""
    
    # ===== STAGE 9: COVER LETTER COMPLIANCE =====
    cl_compliance_score: float = 0.0
    cl_compliance_passed: bool = False
    
    # ===== STAGE 10: EMAIL =====
    email: Optional[Any] = None  # GeneratedEmail object or dict
    email_text: str = ""
    
    # ===== STAGE 11: EXCEL =====
    excel_saved: bool = False
    
    # ===== STAGE 12: OUTPUT FILES =====
    output_folder: str = ""
    
    # ===== PIPELINE CONTROL =====
    current_stage: str = ""
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


def create_initial_state(
    jd_url: Optional[str] = None,
    jd_text: Optional[str] = None
) -> dict:
    """
    Create initial state dictionary for pipeline invocation.
    
    Args:
        jd_url: URL to job posting
        jd_text: Raw job description text
        
    Returns:
        Dictionary suitable for graph.invoke()
    """
    return {
        "jd_url": jd_url,
        "jd_text": jd_text,
        "current_stage": "initialized"
    }
