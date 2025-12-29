"""
Resume Parameters

Controls resume generation to ensure it fits on one page.
Adjust these parameters based on font size, margins, and layout.

ONE PAGE RESUME GUIDELINES (Standard formatting):
- Total word count: 400-600 words
- Summary: 30-50 words (2-3 lines)
- Experience: 3-4 positions, 3-4 bullets each
- Projects: 2-3 projects, 2-3 bullets each
- Skills: 4-6 categories, 6-10 skills per category
- Bullet length: 15-25 words each
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ResumeParams(BaseModel):
    """
    Parameters controlling resume generation.
    
    These values are tuned for a one-page resume with standard formatting:
    - Font: 10-11pt
    - Margins: 0.5-0.75 inch
    - Single column layout
    """
    
    # =========================================================================
    # WORD COUNT LIMITS
    # =========================================================================
    
    # Total resume target (one page ≈ 400-600 words)
    target_total_words: int = Field(
        default=500,
        description="Target total word count for entire resume"
    )
    max_total_words: int = Field(
        default=600,
        description="Maximum total word count (hard limit)"
    )
    min_total_words: int = Field(
        default=400,
        description="Minimum total word count"
    )
    
    # =========================================================================
    # SUMMARY SECTION
    # =========================================================================
    
    summary_min_words: int = Field(
        default=30,
        description="Minimum words in professional summary"
    )
    summary_max_words: int = Field(
        default=50,
        description="Maximum words in professional summary"
    )
    summary_sentences: int = Field(
        default=3,
        description="Target number of sentences in summary"
    )
    
    # =========================================================================
    # EXPERIENCE SECTION
    # =========================================================================
    
    max_experiences: int = Field(
        default=4,
        description="Maximum number of experience entries"
    )
    min_experiences: int = Field(
        default=2,
        description="Minimum number of experience entries"
    )
    
    bullets_per_experience: int = Field(
        default=4,
        description="Target bullets per experience entry"
    )
    max_bullets_per_experience: int = Field(
        default=5,
        description="Maximum bullets per experience entry"
    )
    min_bullets_per_experience: int = Field(
        default=3,
        description="Minimum bullets per experience entry"
    )
    
    bullet_min_words: int = Field(
        default=12,
        description="Minimum words per bullet point"
    )
    bullet_max_words: int = Field(
        default=25,
        description="Maximum words per bullet point"
    )
    bullet_target_words: int = Field(
        default=18,
        description="Target words per bullet point"
    )
    
    # Experience prioritization
    prioritize_recent: bool = Field(
        default=True,
        description="Give more bullets to recent experiences"
    )
    recent_experience_extra_bullets: int = Field(
        default=1,
        description="Extra bullets for most recent experience"
    )
    
    # =========================================================================
    # PROJECTS SECTION
    # =========================================================================
    
    max_projects: int = Field(
        default=3,
        description="Maximum number of project entries"
    )
    min_projects: int = Field(
        default=2,
        description="Minimum number of project entries"
    )
    
    bullets_per_project: int = Field(
        default=2,
        description="Target bullets per project"
    )
    max_bullets_per_project: int = Field(
        default=3,
        description="Maximum bullets per project"
    )
    min_bullets_per_project: int = Field(
        default=2,
        description="Minimum bullets per project"
    )
    
    project_bullet_max_words: int = Field(
        default=20,
        description="Maximum words per project bullet"
    )
    
    # =========================================================================
    # SKILLS SECTION
    # =========================================================================
    
    max_skill_categories: int = Field(
        default=6,
        description="Maximum skill categories to show"
    )
    min_skill_categories: int = Field(
        default=4,
        description="Minimum skill categories to show"
    )
    
    max_skills_per_category: int = Field(
        default=10,
        description="Maximum skills per category"
    )
    min_skills_per_category: int = Field(
        default=4,
        description="Minimum skills per category"
    )
    
    # Skill prioritization
    prioritize_matched_skills: bool = Field(
        default=True,
        description="Put JD-matched skills first in each category"
    )
    
    # =========================================================================
    # EDUCATION SECTION
    # =========================================================================
    
    max_education_entries: int = Field(
        default=2,
        description="Maximum education entries"
    )
    include_coursework: bool = Field(
        default=False,
        description="Include relevant coursework (takes space)"
    )
    max_coursework_items: int = Field(
        default=4,
        description="Maximum coursework items if included"
    )
    include_gpa: bool = Field(
        default=True,
        description="Include GPA if above threshold"
    )
    gpa_threshold: float = Field(
        default=3.5,
        description="Only show GPA if above this value"
    )
    
    # =========================================================================
    # CERTIFICATIONS SECTION
    # =========================================================================
    
    max_certifications: int = Field(
        default=4,
        description="Maximum certifications to show"
    )
    prioritize_relevant_certs: bool = Field(
        default=True,
        description="Prioritize JD-relevant certifications"
    )
    
    # =========================================================================
    # PUBLICATIONS SECTION
    # =========================================================================
    
    max_publications: int = Field(
        default=2,
        description="Maximum publications to show"
    )
    include_publications: bool = Field(
        default=True,
        description="Include publications section"
    )
    
    # =========================================================================
    # FORMATTING HINTS
    # =========================================================================
    
    use_abbreviations: bool = Field(
        default=True,
        description="Use common abbreviations to save space (ML, AI, NLP)"
    )
    
    use_symbols_for_metrics: bool = Field(
        default=True,
        description="Use symbols like %, $, + instead of words"
    )
    
    # =========================================================================
    # CONTENT QUALITY
    # =========================================================================
    
    require_metrics_percentage: float = Field(
        default=0.6,
        description="Percentage of bullets that should have metrics (60%)"
    )
    
    require_action_verbs: bool = Field(
        default=True,
        description="All bullets must start with action verbs"
    )
    
    avoid_weak_verbs: bool = Field(
        default=True,
        description="Avoid weak verbs like 'helped', 'assisted'"
    )
    
    class Config:
        """Pydantic config."""
        validate_assignment = True


# =========================================================================
# DEFAULT INSTANCE
# =========================================================================

RESUME_PARAMS = ResumeParams()


# =========================================================================
# PRESET CONFIGURATIONS
# =========================================================================

def get_one_page_params() -> ResumeParams:
    """Get parameters optimized for one-page resume."""
    return ResumeParams(
        target_total_words=500,
        max_total_words=550,
        max_experiences=4,
        bullets_per_experience=4,
        max_bullets_per_experience=4,
        max_projects=2,
        bullets_per_project=2,
        summary_max_words=45,
        max_skill_categories=5,
        max_skills_per_category=8,
        include_coursework=False
    )


def get_two_page_params() -> ResumeParams:
    """Get parameters for two-page resume."""
    return ResumeParams(
        target_total_words=900,
        max_total_words=1100,
        max_experiences=6,
        bullets_per_experience=5,
        max_bullets_per_experience=6,
        max_projects=4,
        bullets_per_project=3,
        summary_max_words=70,
        max_skill_categories=8,
        max_skills_per_category=12,
        include_coursework=True,
        max_coursework_items=6
    )


def get_compact_params() -> ResumeParams:
    """Get parameters for very compact resume."""
    return ResumeParams(
        target_total_words=400,
        max_total_words=450,
        max_experiences=3,
        bullets_per_experience=3,
        max_bullets_per_experience=3,
        bullet_max_words=20,
        max_projects=2,
        bullets_per_project=2,
        summary_max_words=35,
        max_skill_categories=4,
        max_skills_per_category=6,
        include_coursework=False,
        max_certifications=2,
        max_publications=1
    )


# =========================================================================
# EXPORTS
# =========================================================================

__all__ = [
    "ResumeParams",
    "RESUME_PARAMS",
    "get_one_page_params",
    "get_two_page_params",
    "get_compact_params"
]
