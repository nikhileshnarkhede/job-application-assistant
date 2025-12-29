"""
Cover Letter Generator Subgraph State

Generates personalized cover letters with:
1. Company research via DuckDuckGo
2. JD-aligned content
3. Professional formatting
4. Compliance with cover letter guidelines
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

import sys
sys.path.append("../..")
from state.state_models import StructuredJD, ResumeJSON


# ============================================================================
# COMPANY RESEARCH MODEL
# ============================================================================

class CompanyResearch(BaseModel):
    """Research findings about the company."""
    company_name: str = ""
    industry: str = ""
    company_size: str = ""  # startup, mid-size, enterprise
    founded: str = ""
    headquarters: str = ""
    
    # Mission & Values
    mission_statement: str = ""
    core_values: List[str] = Field(default_factory=list)
    company_culture: str = ""
    
    # Business Info
    products_services: List[str] = Field(default_factory=list)
    target_market: str = ""
    competitors: List[str] = Field(default_factory=list)
    
    # Recent News & Achievements
    recent_news: List[str] = Field(default_factory=list)
    recent_achievements: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    
    # Why Work Here
    employee_benefits: List[str] = Field(default_factory=list)
    work_environment: str = ""
    growth_opportunities: str = ""
    
    # Search Sources
    sources: List[str] = Field(default_factory=list)
    research_summary: str = ""


# ============================================================================
# COVER LETTER STRUCTURE
# ============================================================================

class CoverLetterSection(BaseModel):
    """A section of the cover letter."""
    name: str
    content: str
    word_count: int = 0


class CoverLetter(BaseModel):
    """Complete cover letter."""
    # Header
    candidate_name: str = ""
    candidate_email: str = ""
    candidate_phone: str = ""
    candidate_location: str = ""
    
    date: str = ""
    
    # Recipient
    recipient_name: str = ""
    recipient_title: str = ""
    company_name: str = ""
    company_address: str = ""
    
    # Salutation
    salutation: str = "Dear Hiring Manager,"
    
    # Body paragraphs
    introduction: str = ""  # Why you're applying, how you heard
    body_paragraph_1: str = ""  # Skills & qualifications
    body_paragraph_2: str = ""  # Why this company/role
    body_paragraph_3: str = ""  # Soft skills & culture fit (optional)
    closing: str = ""  # Thank you, call to action
    
    # Sign-off
    sign_off: str = "Sincerely,"
    signature: str = ""
    
    # Full text
    full_text: str = ""
    
    # Metadata
    word_count: int = 0
    paragraph_count: int = 0
    keywords_used: List[str] = Field(default_factory=list)
    company_mentions: int = 0
    
    # Quality
    tone: str = "professional"  # professional, enthusiastic, conversational
    personalization_score: float = 0.0  # 0-100


# ============================================================================
# COVER LETTER GUIDELINES
# ============================================================================

COVER_LETTER_GUIDELINES = {
    "format": {
        "max_pages": 1,
        "ideal_word_count": (250, 400),
        "paragraphs": (3, 4),
        "font_size": "10-12pt",
        "margins": "1 inch"
    },
    "introduction": {
        "purpose": "Identify position, explain interest, mention referral if any",
        "ideal_sentences": (2, 4),
        "hooks": ["specific company achievement", "shared values", "industry passion", "mutual connection"]
    },
    "body": {
        "purpose": "Highlight relevant skills, provide examples, connect to JD",
        "ideal_paragraphs": (1, 2),
        "must_include": ["quantified achievements", "relevant skills", "company-specific reasons"]
    },
    "closing": {
        "purpose": "Thank reader, express enthusiasm, call to action",
        "ideal_sentences": (2, 3),
        "must_include": ["gratitude", "follow-up intention", "contact availability"]
    },
    "tone": {
        "professional": True,
        "enthusiastic": True,
        "confident_not_arrogant": True,
        "specific_not_generic": True
    },
    "avoid": [
        "Starting with 'I'",
        "Generic statements",
        "Repeating resume verbatim",
        "Negative language",
        "Salary discussions",
        "Personal pronouns overuse",
        "Typos and grammar errors"
    ]
}


# ============================================================================
# STATE MODEL
# ============================================================================

class CoverLetterGeneratorState(BaseModel):
    """State for Cover Letter Generator subgraph."""
    
    # Input
    structured_jd: Optional[StructuredJD] = None
    resume_json: Optional[ResumeJSON] = None
    
    # Research
    company_research: Optional[CompanyResearch] = None
    search_queries: List[str] = Field(default_factory=list)
    search_results: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Generation
    cover_letter: Optional[CoverLetter] = None
    draft_versions: List[CoverLetter] = Field(default_factory=list)
    
    # Customization
    tone: str = "professional"  # professional, enthusiastic, conversational
    focus_areas: List[str] = Field(default_factory=list)  # technical, leadership, culture
    referral_name: Optional[str] = None
    custom_hook: Optional[str] = None
    
    # Control
    generation_complete: bool = False
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "CoverLetterGeneratorState",
    "CompanyResearch",
    "CoverLetterSection",
    "CoverLetter",
    "COVER_LETTER_GUIDELINES"
]
