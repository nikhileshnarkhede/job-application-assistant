"""
GitHub Ranker Subgraph State

This module defines the state specific to the GitHub Ranker subgraph.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Import from parent state
import sys
sys.path.append("../..")
from state.state_models import StructuredJD, SelectedProject


class GitHubRankerState(BaseModel):
    """
    State for GitHub Ranker subgraph.
    
    This subgraph handles:
    1. Loading GitHub projects from API/cache/JSON
    2. Ranking projects by JD relevance
    3. Selecting top projects for resume
    4. Generating project bullets using LLM
    """
    
    # ===== INPUT =====
    structured_jd: Optional[StructuredJD] = None
    max_projects: int = Field(default=3, description="Max projects to select")
    
    # ===== INTERMEDIATE =====
    # All available projects
    all_projects: List[Dict[str, Any]] = Field(default_factory=list)
    projects_source: str = Field(default="", description="Source: api, cache, json, local")
    
    # JD requirements for matching
    jd_skills: List[str] = Field(default_factory=list)
    jd_keywords: List[str] = Field(default_factory=list)
    role_type: str = Field(default="ml_ai")
    
    # ===== OUTPUT =====
    selected_projects: List[SelectedProject] = Field(default_factory=list)
    
    # ===== CONTROL =====
    ranking_complete: bool = False
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# PROJECT SCORING WEIGHTS
# ============================================================================

SCORING_WEIGHTS = {
    "tech_stack_overlap": 0.35,      # Tech stack matches JD skills
    "keyword_match": 0.25,           # Keywords/topics match JD
    "relevance_tag_match": 0.20,     # Role type alignment
    "has_metrics": 0.10,             # Project has quantifiable metrics
    "activity_bonus": 0.10           # Stars, recent updates
}

# Role type mappings for relevance scoring
ROLE_TYPE_TAGS = {
    "ml_ai": ["ml_ai", "deep_learning", "machine_learning", "neural_networks"],
    "data_science": ["data_science", "analytics", "ml_ai", "statistics"],
    "llm_ai_agents": ["rag_llm", "nlp", "ml_ai", "llm", "agents"],
    "nlp": ["nlp", "ml_ai", "rag_llm", "transformers"],
    "computer_vision": ["computer_vision", "ml_ai", "deep_learning"],
    "data_engineering": ["data_engineering", "etl", "pipelines"],
    "software_engineering": ["web_dev", "backend", "api", "devops"],
    "research": ["ml_ai", "research", "publications"],
    "robotics_automation": ["robotics", "automation", "ml_ai", "computer_vision"]
}


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "GitHubRankerState",
    "SCORING_WEIGHTS",
    "ROLE_TYPE_TAGS"
]
