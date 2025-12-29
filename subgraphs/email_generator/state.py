"""
Email Generator Subgraph State

Generates professional outreach emails for:
1. Cold outreach to recruiters
2. Follow-up after application
3. Networking/referral requests
4. Thank you after interview
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

import sys
sys.path.append("../..")
from state.state_models import StructuredJD, ResumeJSON


# ============================================================================
# EMAIL TYPES
# ============================================================================

class EmailType(str, Enum):
    """Types of professional emails."""
    COLD_OUTREACH = "cold_outreach"          # Initial contact with recruiter
    APPLICATION_FOLLOWUP = "application_followup"  # After submitting application
    REFERRAL_REQUEST = "referral_request"    # Asking for internal referral
    NETWORKING = "networking"                 # General networking
    THANK_YOU = "thank_you"                  # After interview
    INFORMATION_REQUEST = "information_request"  # Asking about role/company


class EmailTone(str, Enum):
    """Tone of the email."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    ENTHUSIASTIC = "enthusiastic"
    FORMAL = "formal"


# ============================================================================
# EMAIL TEMPLATES GUIDELINES
# ============================================================================

EMAIL_GUIDELINES = {
    "cold_outreach": {
        "subject_templates": [
            "{Role} Opportunity - {Candidate Name}",
            "Experienced {Skill} Professional Interested in {Company}",
            "Inquiry: {Role} Position at {Company}"
        ],
        "ideal_length": (100, 150),  # words
        "key_elements": [
            "Brief introduction",
            "Why contacting them specifically",
            "Relevant qualification highlight",
            "Clear ask/call to action",
            "Respect for their time"
        ],
        "avoid": [
            "Long paragraphs",
            "Attaching resume unsolicited",
            "Being too casual",
            "Generic content"
        ]
    },
    "application_followup": {
        "subject_templates": [
            "Following Up: {Role} Application - {Candidate Name}",
            "Application Follow-up: {Role} Position",
            "{Role} Application Status Inquiry"
        ],
        "ideal_length": (80, 120),
        "key_elements": [
            "Reference to application date",
            "Position applied for",
            "Continued interest",
            "Polite inquiry about status",
            "Availability for next steps"
        ],
        "timing": "1-2 weeks after application"
    },
    "referral_request": {
        "subject_templates": [
            "Referral Request: {Role} at {Company}",
            "Would You Refer Me for {Role}?",
            "Seeking Your Help: {Company} Opportunity"
        ],
        "ideal_length": (120, 180),
        "key_elements": [
            "How you know them/connection",
            "Specific role interested in",
            "Why you're qualified",
            "What you're asking for",
            "Make it easy for them"
        ]
    },
    "thank_you": {
        "subject_templates": [
            "Thank You - {Role} Interview",
            "Following Up: {Role} Conversation",
            "Appreciation for Your Time - {Role}"
        ],
        "ideal_length": (100, 150),
        "key_elements": [
            "Gratitude for their time",
            "Reference to specific discussion point",
            "Reiterate interest and fit",
            "Next steps acknowledgment"
        ],
        "timing": "Within 24 hours of interview"
    },
    "networking": {
        "subject_templates": [
            "Connecting: {Industry/Skill} Professional",
            "Introduction from {Mutual Connection}",
            "Seeking Advice: {Topic}"
        ],
        "ideal_length": (100, 150),
        "key_elements": [
            "Clear reason for reaching out",
            "Mutual connection if any",
            "Specific ask (coffee chat, advice)",
            "Respect for their time"
        ]
    }
}


# ============================================================================
# RECIPIENT MODEL
# ============================================================================

class EmailRecipient(BaseModel):
    """Information about email recipient."""
    name: str = ""
    title: str = ""
    company: str = ""
    email: str = ""
    linkedin_url: str = ""
    
    # Context
    how_found: str = ""  # LinkedIn, company website, referral
    mutual_connections: List[str] = Field(default_factory=list)
    notes: str = ""


# ============================================================================
# EMAIL MODEL
# ============================================================================

class GeneratedEmail(BaseModel):
    """Generated email content."""
    # Email fields
    subject: str = ""
    greeting: str = ""
    body: str = ""
    closing: str = ""
    signature: str = ""
    
    # Full email
    full_text: str = ""
    
    # Metadata
    email_type: str = ""
    tone: str = ""
    word_count: int = 0
    
    # Recipient
    recipient_name: str = ""
    recipient_company: str = ""
    
    # Quality metrics
    personalization_score: float = 0.0  # 0-100
    has_clear_ask: bool = False
    has_value_proposition: bool = False
    
    # Alternative versions
    subject_alternatives: List[str] = Field(default_factory=list)


# ============================================================================
# STATE MODEL
# ============================================================================

class EmailGeneratorState(BaseModel):
    """State for Email Generator subgraph."""
    
    # Input
    structured_jd: Optional[StructuredJD] = None
    resume_json: Optional[ResumeJSON] = None
    recipient: Optional[EmailRecipient] = None
    
    # Configuration
    email_type: EmailType = EmailType.COLD_OUTREACH
    tone: EmailTone = EmailTone.PROFESSIONAL
    custom_context: str = ""  # Any additional context
    referral_name: Optional[str] = None
    application_date: Optional[str] = None
    interview_date: Optional[str] = None
    
    # Intermediate data (for passing between nodes)
    context_data: Dict[str, Any] = Field(default_factory=dict)
    template_info: Dict[str, Any] = Field(default_factory=dict)
    
    # Generation
    generated_email: Optional[GeneratedEmail] = None
    
    # Control
    generation_complete: bool = False
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "EmailGeneratorState",
    "EmailType",
    "EmailTone",
    "EmailRecipient",
    "GeneratedEmail",
    "EMAIL_GUIDELINES"
]
