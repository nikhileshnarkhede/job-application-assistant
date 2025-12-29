"""
Email Generation Parameters

Controls outreach email generation.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field


class EmailParams(BaseModel):
    """
    Parameters controlling email generation.
    """
    
    # =========================================================================
    # WORD COUNT BY TYPE
    # =========================================================================
    
    cold_outreach_words: tuple = Field(
        default=(100, 150),
        description="Word count range for cold outreach"
    )
    
    followup_words: tuple = Field(
        default=(80, 120),
        description="Word count range for follow-up"
    )
    
    referral_request_words: tuple = Field(
        default=(120, 180),
        description="Word count range for referral request"
    )
    
    thank_you_words: tuple = Field(
        default=(100, 150),
        description="Word count range for thank you"
    )
    
    networking_words: tuple = Field(
        default=(100, 150),
        description="Word count range for networking"
    )
    
    # =========================================================================
    # CONTENT REQUIREMENTS
    # =========================================================================
    
    require_clear_ask: bool = Field(
        default=True,
        description="Email must have clear call-to-action"
    )
    
    require_personalization: bool = Field(
        default=True,
        description="Email must be personalized"
    )
    
    max_paragraphs: int = Field(
        default=2,
        description="Maximum paragraphs in email body"
    )
    
    # =========================================================================
    # SUBJECT LINE
    # =========================================================================
    
    subject_max_words: int = Field(
        default=10,
        description="Maximum words in subject line"
    )
    
    subject_min_words: int = Field(
        default=4,
        description="Minimum words in subject line"
    )
    
    include_role_in_subject: bool = Field(
        default=True,
        description="Include role title in subject"
    )
    
    # =========================================================================
    # ALTERNATIVES
    # =========================================================================
    
    generate_subject_alternatives: bool = Field(
        default=True,
        description="Generate alternative subject lines"
    )
    
    num_subject_alternatives: int = Field(
        default=2,
        description="Number of alternative subjects to generate"
    )
    
    class Config:
        """Pydantic config."""
        validate_assignment = True


# =========================================================================
# DEFAULT INSTANCE
# =========================================================================

EMAIL_PARAMS = EmailParams()


# =========================================================================
# EXPORTS
# =========================================================================

__all__ = [
    "EmailParams",
    "EMAIL_PARAMS"
]
