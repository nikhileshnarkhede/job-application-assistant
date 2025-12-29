"""
Experience Selector Subgraph State

This module defines the state specific to the Experience Selector subgraph.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Import from parent state
import sys
sys.path.append("../..")
from state.state_models import StructuredJD, SelectedExperience


class ExperienceSelectorState(BaseModel):
    """
    State for Experience Selector subgraph.
    
    This subgraph handles:
    1. Loading candidate experiences from candidate_loader
    2. Scoring experiences by JD relevance
    3. Selecting top experiences for resume
    4. Preparing bullets for rewriting
    """
    
    # ===== INPUT =====
    structured_jd: Optional[StructuredJD] = None
    max_experiences: int = Field(default=4, description="Max experiences to select")
    
    # ===== INTERMEDIATE =====
    # All available experiences
    all_experiences: List[Dict[str, Any]] = Field(default_factory=list)
    
    # JD requirements for matching
    jd_skills: List[str] = Field(default_factory=list)
    jd_keywords: List[str] = Field(default_factory=list)
    jd_responsibilities: List[str] = Field(default_factory=list)
    role_type: str = Field(default="ml_ai")
    
    # Pre-defined relevance mapping (from candidate data)
    relevance_mapping: Dict[str, Dict[str, List[int]]] = Field(default_factory=dict)
    
    # ===== OUTPUT =====
    selected_experiences: List[SelectedExperience] = Field(default_factory=list)
    
    # ===== CONTROL =====
    selection_complete: bool = False
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# EXPERIENCE SCORING WEIGHTS
# ============================================================================

SCORING_WEIGHTS = {
    "skill_match": 0.30,          # Skills match JD requirements
    "keyword_match": 0.25,        # Keywords align with JD
    "responsibility_match": 0.20, # Bullets match JD responsibilities
    "relevance_tier": 0.15,       # Primary/Secondary/Supporting tier
    "recency_bonus": 0.10         # More recent = higher score
}

# Maximum score bonuses
TIER_SCORES = {
    "primary": 1.0,
    "secondary": 0.6,
    "supporting": 0.3,
    "other": 0.1
}

RECENCY_SCORES = {
    1: 1.0,   # Most recent
    2: 0.8,
    3: 0.6,
    4: 0.4,
    5: 0.3,
    6: 0.2,
    7: 0.1
}


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "ExperienceSelectorState",
    "SCORING_WEIGHTS",
    "TIER_SCORES",
    "RECENCY_SCORES"
]
