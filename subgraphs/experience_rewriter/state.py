"""
Experience Rewriter Subgraph State

This module defines the state specific to the Experience Rewriter subgraph.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Import from parent state
import sys
sys.path.append("../..")
from state.state_models import StructuredJD, SelectedExperience, SelectedProject


class ExperienceRewriterState(BaseModel):
    """
    State for Experience Rewriter subgraph.
    
    This subgraph handles:
    1. Loading action verbs from resources
    2. Rewriting experience bullets with action verbs + metrics
    3. Incorporating JD keywords naturally
    4. Rewriting project bullets similarly
    5. Validating keyword incorporation
    """
    
    # ===== INPUT =====
    structured_jd: Optional[StructuredJD] = None
    selected_experiences: List[SelectedExperience] = Field(default_factory=list)
    selected_projects: List[SelectedProject] = Field(default_factory=list)
    
    # ===== RESOURCES =====
    action_verbs: Dict[str, List[str]] = Field(default_factory=dict)
    
    # JD requirements for keyword incorporation
    jd_skills: List[str] = Field(default_factory=list)
    jd_keywords: List[str] = Field(default_factory=list)
    target_keywords: List[str] = Field(default_factory=list)  # Combined priority keywords
    
    # ===== OUTPUT =====
    rewritten_experiences: List[SelectedExperience] = Field(default_factory=list)
    rewritten_projects: List[SelectedProject] = Field(default_factory=list)
    
    # Tracking
    keywords_incorporated: List[str] = Field(default_factory=list)
    incorporation_rate: float = 0.0  # % of target keywords used
    
    # ===== CONTROL =====
    rewrite_complete: bool = False
    rewrite_iteration: int = 0
    max_iterations: int = 2
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# METRIC PATTERNS FOR ENHANCEMENT
# ============================================================================

# These patterns help the LLM add realistic metrics
METRIC_TEMPLATES = {
    "performance": [
        "improved {metric} by {percent}%",
        "reduced {metric} by {percent}%",
        "achieved {percent}% {improvement} in {metric}",
        "increased {metric} {percent}% over baseline"
    ],
    "scale": [
        "processing {number}+ {items} daily",
        "handling {number}K {items} per {timeframe}",
        "serving {number}+ users",
        "managing {number}+ {items}"
    ],
    "accuracy": [
        "achieving {percent}% accuracy",
        "with {percent}% precision/recall",
        "reaching {percent}% F1 score",
        "{percent}% reduction in error rate"
    ],
    "time": [
        "reducing latency by {percent}%",
        "cutting processing time from {old} to {new}",
        "achieving sub-{number}ms response time",
        "accelerating {process} by {multiplier}x"
    ],
    "cost": [
        "saving ${amount} annually",
        "reducing costs by {percent}%",
        "optimizing resource usage by {percent}%"
    ]
}

# Realistic metric ranges by category
METRIC_RANGES = {
    "ml_improvement": (10, 45),      # Model improvements typically 10-45%
    "latency_reduction": (20, 70),   # Latency can often be cut significantly
    "accuracy": (85, 99),            # ML accuracy ranges
    "scale_thousands": (10, 500),    # K scale
    "scale_millions": (1, 50),       # M scale
    "cost_savings": (15, 40),        # Cost reduction %
    "time_savings": (25, 60),        # Time savings %
    "throughput_multiplier": (2, 10) # 2x-10x improvements
}


# ============================================================================
# ACTION VERB CATEGORIES
# ============================================================================

# Fallback action verbs if resources not loaded
DEFAULT_ACTION_VERBS = {
    "leadership": ["Led", "Directed", "Spearheaded", "Orchestrated", "Pioneered", "Championed"],
    "development": ["Developed", "Engineered", "Built", "Created", "Designed", "Architected"],
    "improvement": ["Improved", "Enhanced", "Optimized", "Streamlined", "Accelerated", "Boosted"],
    "implementation": ["Implemented", "Deployed", "Integrated", "Launched", "Established", "Instituted"],
    "analysis": ["Analyzed", "Evaluated", "Assessed", "Investigated", "Researched", "Examined"],
    "collaboration": ["Collaborated", "Partnered", "Coordinated", "Facilitated", "Mentored", "Trained"],
    "achievement": ["Achieved", "Delivered", "Exceeded", "Accomplished", "Attained", "Secured"],
    "transformation": ["Transformed", "Revolutionized", "Modernized", "Overhauled", "Restructured"]
}


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "ExperienceRewriterState",
    "METRIC_TEMPLATES",
    "METRIC_RANGES",
    "DEFAULT_ACTION_VERBS"
]
