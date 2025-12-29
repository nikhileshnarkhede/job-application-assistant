"""
ATS Optimization Parameters

Controls ATS scoring and optimization iterations.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class ATSParams(BaseModel):
    """
    Parameters controlling ATS optimization.
    """
    
    # =========================================================================
    # SCORE THRESHOLDS
    # =========================================================================
    
    target_score: int = Field(
        default=95,
        description="Target ATS score (0-100)"
    )
    min_acceptable_score: int = Field(
        default=85,
        description="Minimum acceptable ATS score"
    )
    
    # =========================================================================
    # ITERATION CONTROL
    # =========================================================================
    
    max_iterations: int = Field(
        default=3,
        description="Maximum optimization iterations"
    )
    stop_on_target: bool = Field(
        default=True,
        description="Stop iterating once target score reached"
    )
    
    # =========================================================================
    # KEYWORD OPTIMIZATION
    # =========================================================================
    
    min_keyword_density: float = Field(
        default=0.02,
        description="Minimum keyword density (2%)"
    )
    max_keyword_density: float = Field(
        default=0.05,
        description="Maximum keyword density (5%) - avoid stuffing"
    )
    
    required_keyword_match_pct: float = Field(
        default=0.7,
        description="Percentage of required skills that must appear (70%)"
    )
    preferred_keyword_match_pct: float = Field(
        default=0.5,
        description="Percentage of preferred skills that should appear (50%)"
    )
    
    # =========================================================================
    # SECTION WEIGHTS
    # =========================================================================
    
    section_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "skills": 0.30,
            "experience": 0.35,
            "summary": 0.15,
            "projects": 0.10,
            "education": 0.10
        },
        description="Weight of each section in ATS score"
    )
    
    # =========================================================================
    # FORMAT REQUIREMENTS
    # =========================================================================
    
    check_format_issues: bool = Field(
        default=True,
        description="Check for ATS format issues"
    )
    
    penalize_tables: bool = Field(
        default=True,
        description="Penalize use of tables (ATS unfriendly)"
    )
    
    penalize_graphics: bool = Field(
        default=True,
        description="Penalize graphics/images"
    )
    
    require_standard_sections: bool = Field(
        default=True,
        description="Require standard section headings"
    )
    
    standard_section_names: List[str] = Field(
        default_factory=lambda: [
            "Summary", "Professional Summary",
            "Experience", "Work Experience", "Professional Experience",
            "Education",
            "Skills", "Technical Skills",
            "Projects",
            "Certifications"
        ],
        description="Acceptable standard section names"
    )
    
    class Config:
        """Pydantic config."""
        validate_assignment = True


# =========================================================================
# DEFAULT INSTANCE
# =========================================================================

ATS_PARAMS = ATSParams()


# =========================================================================
# EXPORTS
# =========================================================================

__all__ = [
    "ATSParams",
    "ATS_PARAMS"
]
