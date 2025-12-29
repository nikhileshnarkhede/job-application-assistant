"""
Pipeline Control Parameters

Controls overall pipeline behavior, iterations, and thresholds.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class PipelineParams(BaseModel):
    """
    Parameters controlling the overall pipeline.
    """
    
    # =========================================================================
    # LOOP ITERATIONS
    # =========================================================================
    
    max_ats_iterations: int = Field(
        default=3,
        description="Maximum ATS optimization iterations"
    )
    
    max_compliance_iterations: int = Field(
        default=3,
        description="Maximum compliance check iterations"
    )
    
    max_cover_letter_iterations: int = Field(
        default=2,
        description="Maximum cover letter revision iterations"
    )
    
    max_rewrite_iterations: int = Field(
        default=2,
        description="Maximum experience rewrite iterations"
    )
    
    # =========================================================================
    # PASS THRESHOLDS
    # =========================================================================
    
    ats_pass_threshold: int = Field(
        default=95,
        description="ATS score threshold to pass"
    )
    
    compliance_pass_threshold: int = Field(
        default=85,
        description="Compliance score threshold to pass"
    )
    
    cover_letter_pass_threshold: int = Field(
        default=80,
        description="Cover letter score threshold to pass"
    )
    
    skill_match_threshold: float = Field(
        default=0.6,
        description="Minimum skill match percentage (60%)"
    )
    
    # =========================================================================
    # SELECTION LIMITS
    # =========================================================================
    
    max_experiences_to_select: int = Field(
        default=4,
        description="Maximum experiences to select from candidate data"
    )
    
    max_projects_to_select: int = Field(
        default=3,
        description="Maximum projects to select from GitHub"
    )
    
    min_relevance_score: float = Field(
        default=0.3,
        description="Minimum relevance score to include item"
    )
    
    # =========================================================================
    # LLM CONFIGURATION
    # =========================================================================
    
    llm_temperature: float = Field(
        default=0.7,
        description="LLM temperature for generation"
    )
    
    llm_temperature_rewrite: float = Field(
        default=0.5,
        description="Lower temperature for rewriting (more consistent)"
    )
    
    llm_temperature_extraction: float = Field(
        default=0.3,
        description="Low temperature for extraction (more deterministic)"
    )
    
    # =========================================================================
    # OUTPUT CONTROL
    # =========================================================================
    
    save_intermediate_outputs: bool = Field(
        default=True,
        description="Save intermediate outputs for debugging"
    )
    
    generate_all_outputs: bool = Field(
        default=True,
        description="Generate resume, cover letter, and email"
    )
    
    track_in_excel: bool = Field(
        default=True,
        description="Track application in Excel spreadsheet"
    )
    
    # =========================================================================
    # ERROR HANDLING
    # =========================================================================
    
    continue_on_error: bool = Field(
        default=False,
        description="Continue pipeline on non-critical errors"
    )
    
    retry_on_llm_error: bool = Field(
        default=True,
        description="Retry LLM calls on transient errors"
    )
    
    max_retries: int = Field(
        default=3,
        description="Maximum retries for LLM calls"
    )
    
    class Config:
        """Pydantic config."""
        validate_assignment = True


# =========================================================================
# DEFAULT INSTANCE
# =========================================================================

PIPELINE_PARAMS = PipelineParams()


# =========================================================================
# EXPORTS
# =========================================================================

__all__ = [
    "PipelineParams",
    "PIPELINE_PARAMS"
]
