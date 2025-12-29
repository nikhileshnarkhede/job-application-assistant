"""
Cover Letter Parameters

Controls cover letter generation for optimal length and impact.

COVER LETTER GUIDELINES:
- Total length: 250-400 words (one page)
- 3-4 paragraphs
- Opening: 2-3 sentences
- Body: 2 paragraphs, 3-5 sentences each
- Closing: 2-3 sentences
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class CoverLetterParams(BaseModel):
    """
    Parameters controlling cover letter generation.
    
    Optimized for one-page cover letter with standard formatting.
    """
    
    # =========================================================================
    # WORD COUNT LIMITS
    # =========================================================================
    
    target_total_words: int = Field(
        default=300,
        description="Target total word count"
    )
    max_total_words: int = Field(
        default=400,
        description="Maximum total word count"
    )
    min_total_words: int = Field(
        default=250,
        description="Minimum total word count"
    )
    
    # =========================================================================
    # PARAGRAPH STRUCTURE
    # =========================================================================
    
    num_body_paragraphs: int = Field(
        default=2,
        description="Number of body paragraphs"
    )
    max_body_paragraphs: int = Field(
        default=3,
        description="Maximum body paragraphs"
    )
    
    # Opening paragraph
    opening_min_sentences: int = Field(
        default=2,
        description="Minimum sentences in opening"
    )
    opening_max_sentences: int = Field(
        default=3,
        description="Maximum sentences in opening"
    )
    opening_max_words: int = Field(
        default=60,
        description="Maximum words in opening paragraph"
    )
    
    # Body paragraphs
    body_min_sentences: int = Field(
        default=3,
        description="Minimum sentences per body paragraph"
    )
    body_max_sentences: int = Field(
        default=5,
        description="Maximum sentences per body paragraph"
    )
    body_max_words: int = Field(
        default=120,
        description="Maximum words per body paragraph"
    )
    
    # Closing paragraph
    closing_min_sentences: int = Field(
        default=2,
        description="Minimum sentences in closing"
    )
    closing_max_sentences: int = Field(
        default=3,
        description="Maximum sentences in closing"
    )
    closing_max_words: int = Field(
        default=50,
        description="Maximum words in closing paragraph"
    )
    
    # =========================================================================
    # CONTENT REQUIREMENTS
    # =========================================================================
    
    # Company research
    include_company_research: bool = Field(
        default=True,
        description="Include company-specific details"
    )
    company_research_sentences: int = Field(
        default=1,
        description="Sentences dedicated to company research"
    )
    
    # Skills/Experience
    max_skills_to_highlight: int = Field(
        default=3,
        description="Maximum skills to specifically mention"
    )
    max_experiences_to_reference: int = Field(
        default=2,
        description="Maximum experiences to reference"
    )
    include_metrics: bool = Field(
        default=True,
        description="Include quantified achievements"
    )
    
    # =========================================================================
    # PERSONALIZATION
    # =========================================================================
    
    personalization_level: str = Field(
        default="high",
        description="Level of personalization: low, medium, high"
    )
    
    use_hiring_manager_name: bool = Field(
        default=True,
        description="Use hiring manager name if available"
    )
    
    reference_job_posting: bool = Field(
        default=True,
        description="Reference specific JD requirements"
    )
    
    # =========================================================================
    # TONE
    # =========================================================================
    
    tone: str = Field(
        default="professional",
        description="Tone: professional, enthusiastic, formal"
    )
    
    avoid_cliches: bool = Field(
        default=True,
        description="Avoid common cover letter clichés"
    )
    
    class Config:
        """Pydantic config."""
        validate_assignment = True


# =========================================================================
# DEFAULT INSTANCE
# =========================================================================

COVER_LETTER_PARAMS = CoverLetterParams()


# =========================================================================
# EXPORTS
# =========================================================================

__all__ = [
    "CoverLetterParams",
    "COVER_LETTER_PARAMS"
]
