"""
Skill Matcher Subgraph State

This module defines the state specific to the Skill Matcher subgraph.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field

# Import from parent state
import sys
sys.path.append("../..")
from state.state_models import StructuredJD, SkillMatchResult


class SkillMatcherState(BaseModel):
    """
    State for Skill Matcher subgraph.
    
    This subgraph handles:
    1. Loading candidate skills from data
    2. Matching skills against JD requirements
    3. Identifying gaps and additional skills
    4. Generating skill gap analysis
    """
    
    # ===== INPUT =====
    structured_jd: Optional[StructuredJD] = None
    candidate_skills_flat: List[str] = Field(default_factory=list)
    candidate_keywords: List[str] = Field(default_factory=list)
    
    # ===== INTERMEDIATE =====
    jd_skills_required: List[str] = Field(default_factory=list)
    jd_skills_preferred: List[str] = Field(default_factory=list)
    jd_keywords: List[str] = Field(default_factory=list)
    
    # Normalized versions for matching
    jd_skills_normalized: List[str] = Field(default_factory=list)
    candidate_skills_normalized: List[str] = Field(default_factory=list)
    
    # ===== OUTPUT =====
    skill_match_result: Optional[SkillMatchResult] = None
    
    # ===== CONTROL =====
    matching_complete: bool = False
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# SKILL NORMALIZATION MAPPINGS
# ============================================================================

# Common skill aliases and variations
SKILL_ALIASES = {
    # Programming Languages
    "python": ["python3", "python 3", "py"],
    "javascript": ["js", "ecmascript", "es6", "es2015"],
    "typescript": ["ts"],
    "c++": ["cpp", "c plus plus", "cplusplus"],
    "c#": ["csharp", "c sharp"],
    
    # ML/AI Frameworks
    "tensorflow": ["tf", "tensor flow"],
    "pytorch": ["torch"],
    "scikit-learn": ["sklearn", "scikit learn", "scikitlearn"],
    "keras": ["keras api"],
    "huggingface": ["hugging face", "hf", "transformers"],
    
    # Cloud Platforms
    "aws": ["amazon web services", "amazon aws"],
    "gcp": ["google cloud", "google cloud platform"],
    "azure": ["microsoft azure", "ms azure"],
    
    # Databases
    "postgresql": ["postgres", "psql"],
    "mongodb": ["mongo"],
    "mysql": ["my sql"],
    
    # Tools
    "docker": ["containerization", "containers"],
    "kubernetes": ["k8s", "kube"],
    "git": ["github", "gitlab", "version control"],
    
    # ML Concepts
    "machine learning": ["ml", "machine-learning"],
    "deep learning": ["dl", "deep-learning"],
    "natural language processing": ["nlp", "natural-language-processing"],
    "computer vision": ["cv", "image processing"],
    "reinforcement learning": ["rl"],
    "large language models": ["llm", "llms", "large language model"],
    
    # Data Science
    "data analysis": ["data analytics", "analytics"],
    "data visualization": ["dataviz", "data viz"],
    "exploratory data analysis": ["eda"],
    
    # Soft Skills
    "communication": ["communication skills", "written communication", "verbal communication"],
    "problem solving": ["problem-solving", "analytical thinking"],
    "teamwork": ["team collaboration", "collaboration", "team player"],
}

# Build reverse mapping for quick lookup
SKILL_REVERSE_MAP = {}
for canonical, aliases in SKILL_ALIASES.items():
    SKILL_REVERSE_MAP[canonical.lower()] = canonical
    for alias in aliases:
        SKILL_REVERSE_MAP[alias.lower()] = canonical


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name to its canonical form.
    
    Args:
        skill: Raw skill string
    
    Returns:
        Normalized skill name
    """
    skill_lower = skill.lower().strip()
    
    # Check if it's an alias
    if skill_lower in SKILL_REVERSE_MAP:
        return SKILL_REVERSE_MAP[skill_lower]
    
    # Return original with title case
    return skill.strip()


def normalize_skills_list(skills: List[str]) -> List[str]:
    """Normalize a list of skills."""
    normalized = []
    seen = set()
    
    for skill in skills:
        norm = normalize_skill(skill)
        norm_lower = norm.lower()
        
        if norm_lower not in seen:
            normalized.append(norm)
            seen.add(norm_lower)
    
    return normalized


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "SkillMatcherState",
    "SKILL_ALIASES",
    "SKILL_REVERSE_MAP",
    "normalize_skill",
    "normalize_skills_list"
]
