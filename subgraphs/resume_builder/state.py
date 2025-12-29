"""
Resume Builder Subgraph State

This module defines the state specific to the Resume Builder subgraph.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Import from parent state
import sys
sys.path.append("../..")
from state.state_models import (
    StructuredJD, 
    SelectedExperience, 
    SelectedProject,
    SkillMatchResult,
    ResumeJSON
)


class ResumeBuilderState(BaseModel):
    """
    State for Resume Builder subgraph.
    
    This subgraph handles:
    1. Loading candidate base data (header, education, etc.)
    2. Tailoring professional summary for JD
    3. Optimizing skills order by relevance
    4. Formatting experiences and projects
    5. Assembling complete ResumeJSON
    """
    
    # ===== INPUT =====
    structured_jd: Optional[StructuredJD] = None
    skill_match_result: Optional[SkillMatchResult] = None
    rewritten_experiences: List[SelectedExperience] = Field(default_factory=list)
    rewritten_projects: List[SelectedProject] = Field(default_factory=list)
    
    # ===== CANDIDATE BASE DATA =====
    candidate_header: Dict[str, str] = Field(default_factory=dict)
    candidate_education: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_certifications: List[str] = Field(default_factory=list)
    candidate_publications: List[str] = Field(default_factory=list)
    candidate_skills: Dict[str, List[str]] = Field(default_factory=dict)
    base_summary: str = ""
    
    # ===== PROCESSED DATA =====
    tailored_summary: str = ""
    optimized_skills: Dict[str, str] = Field(default_factory=dict)  # Category: "skill1, skill2"
    formatted_experiences: List[Dict[str, Any]] = Field(default_factory=list)
    formatted_projects: List[Dict[str, Any]] = Field(default_factory=list)
    formatted_education: List[Dict[str, Any]] = Field(default_factory=list)
    
    # ===== OUTPUT =====
    resume_json: Optional[ResumeJSON] = None
    
    # ===== CONTROL =====
    build_complete: bool = False
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# RESUME SECTION CONFIGURATION
# ============================================================================

# Bullet limits per experience position
BULLET_LIMITS = {
    1: 5,  # Most recent: up to 5 bullets
    2: 4,  # Second: up to 4 bullets
    3: 3,  # Third: up to 3 bullets
    4: 2,  # Fourth+: up to 2 bullets
}

# Default bullet limit for older experiences
DEFAULT_BULLET_LIMIT = 2

# Project bullet limits
PROJECT_BULLET_LIMIT = 3

# Skills per category limit
SKILLS_PER_CATEGORY_LIMIT = 12

# Section order in final resume
SECTION_ORDER = [
    "header",
    "summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
    "publications"
]

# Skill category priority (for ordering)
SKILL_CATEGORY_PRIORITY = [
    "Programming Languages",
    "Languages & Frameworks",
    "ML/AI & Data Science",
    "Machine Learning",
    "Cloud & Infrastructure",
    "Tools & Platforms",
    "Databases",
    "Other"
]


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "ResumeBuilderState",
    "BULLET_LIMITS",
    "DEFAULT_BULLET_LIMIT",
    "PROJECT_BULLET_LIMIT",
    "SKILLS_PER_CATEGORY_LIMIT",
    "SECTION_ORDER",
    "SKILL_CATEGORY_PRIORITY"
]
