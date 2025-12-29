"""
Cover Letter Compliance Subgraph State

Validates cover letter against:
1. Cover Letter Checklist (detailed item-by-item check)
2. Cover Letter Rubric (scoring across 3 sections)
3. Cover Letter Guide (best practices validation)
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

import sys
sys.path.append("../..")
from state.state_models import StructuredJD

# Import CoverLetter from cover_letter_generator
try:
    from subgraphs.cover_letter_generator.state import CoverLetter
except ImportError:
    # Fallback definition if circular import
    class CoverLetter(BaseModel):
        full_text: str = ""
        word_count: int = 0


# ============================================================================
# CHECKLIST ITEMS - Parsed from Cover Letter Checklist.txt
# ============================================================================

COVER_LETTER_CHECKLIST = {
    "research": {
        "name": "Research & Preparation",
        "items": [
            {"id": "rs_1", "text": "Demonstrates review of position description", "required": True},
            {"id": "rs_2", "text": "Demonstrates review of company website", "required": True},
            {"id": "rs_3", "text": "Identifies qualifications, skills, and abilities for position", "required": True},
            {"id": "rs_4", "text": "Addresses why interested in the organization", "required": True},
            {"id": "rs_5", "text": "Explains why you are a fit for the specific position", "required": True},
            {"id": "rs_6", "text": "Follows all directions in the posting", "required": True},
        ]
    },
    "introduction": {
        "name": "Introduction Paragraph",
        "items": [
            {"id": "in_1", "text": "Identifies the position you are applying for", "required": True},
            {"id": "in_2", "text": "Describes how you heard about the opening", "required": False},
            {"id": "in_3", "text": "Mentions referral by name if applicable", "required": False},
            {"id": "in_4", "text": "Briefly highlights why interested in job and organization", "required": True},
            {"id": "in_5", "text": "Creative opening that catches employer attention", "required": True},
        ]
    },
    "body": {
        "name": "Body Paragraphs",
        "items": [
            {"id": "bd_1", "text": "Identifies strongest and most relevant qualifications", "required": True},
            {"id": "bd_2", "text": "Clearly states how qualifications apply to the position", "required": True},
            {"id": "bd_3", "text": "Incorporates keywords from position description", "required": True},
            {"id": "bd_4", "text": "Elaborates on interest in position, organization, industry", "required": True},
            {"id": "bd_5", "text": "Describes experiences where you developed relevant skills", "required": True},
            {"id": "bd_6", "text": "Provides clear examples that capture reader's interest", "required": True},
            {"id": "bd_7", "text": "Tells a story, does not just repeat resume", "required": True},
            {"id": "bd_8", "text": "Discusses how skills relate to job description", "required": True},
            {"id": "bd_9", "text": "Discusses how soft skills relate to qualifications", "required": False},
        ]
    },
    "closing": {
        "name": "Closing Paragraph",
        "items": [
            {"id": "cl_1", "text": "Thanks the reader for taking time to read", "required": True},
            {"id": "cl_2", "text": "Reinforces desire to work for the organization", "required": True},
            {"id": "cl_3", "text": "Reinforces fit for the position", "required": True},
            {"id": "cl_4", "text": "Identifies next steps", "required": True},
            {"id": "cl_5", "text": "Describes how you will follow up in specific time frame", "required": False},
        ]
    },
    "format": {
        "name": "Format & Signature",
        "items": [
            {"id": "fm_1", "text": "Stays within one page", "required": True},
            {"id": "fm_2", "text": "Contact information listed on cover letter", "required": True},
            {"id": "fm_3", "text": "Same header as resume for consistency", "required": False},
            {"id": "fm_4", "text": "Targeted toward specific employer", "required": True},
            {"id": "fm_5", "text": "Uses keywords from job description", "required": True},
            {"id": "fm_6", "text": "Uses same font and font size as resume", "required": False},
            {"id": "fm_7", "text": "Addressed to a specific person if possible", "required": False},
            {"id": "fm_8", "text": "Formal closing (Sincerely, Regards, Best regards)", "required": True},
            {"id": "fm_9", "text": "Full name after closing", "required": True},
            {"id": "fm_10", "text": "No spelling or grammatical errors", "required": True},
        ]
    }
}


# ============================================================================
# RUBRIC SCORING - From Cover Letter rubric.xlsx
# ============================================================================

COVER_LETTER_RUBRIC = {
    "format_quality": {
        "name": "Business Format & Writing Quality",
        "weight": 0.25,
        "levels": {
            3: "Correct business format with date and addresses. Clear, concise, grammatically correct. No spelling errors.",
            2: "Correct business format. Minimal grammar/spelling errors. Content decent but doesn't convince employer to call.",
            1: "Business formatting not used. No address or date. Not signed. Multiple grammar/spelling errors. Content unclear."
        }
    },
    "introduction": {
        "name": "Section 1: Introduction",
        "weight": 0.25,
        "levels": {
            3: "Identifies position, explains interest, describes how heard about opening. Creative, catches attention quickly.",
            2: "Identifies position but no description of how heard. Vague interest. Bland, might not catch attention.",
            1: "Does not identify position. No description of how heard or why interested. Will not grab attention."
        }
    },
    "skills_experience": {
        "name": "Section 2: Skills & Experience",
        "weight": 0.30,
        "levels": {
            3: "Identifies 1-2 strongest qualifications clearly related to job. Explains specifically why interested in position, company, location.",
            2: "Identifies qualifications not well related to position. Restates resume with minimal additions. Vague interest.",
            1: "Does not discuss relevant qualifications. Skills not related to position. No statement of interest."
        }
    },
    "closing": {
        "name": "Section 3: Closing",
        "weight": 0.20,
        "levels": {
            3: "Refers to resume/documents. Thanks reader. Assertive about follow-up in stated time period.",
            2: "Thanks reader but no reference to resume. Assumes employer will contact you.",
            1: "No thanks to reader. No reference to resume. No mention of follow-up plan."
        }
    }
}


# ============================================================================
# STATE MODELS
# ============================================================================

class ChecklistResult(BaseModel):
    """Result for a single checklist item."""
    item_id: str
    item_text: str
    passed: bool
    required: bool
    notes: str = ""


class SectionCheckResult(BaseModel):
    """Result for a checklist section."""
    section_name: str
    items_passed: int
    items_total: int
    required_passed: int
    required_total: int
    score: float  # 0-100
    results: List[ChecklistResult] = Field(default_factory=list)


class RubricScore(BaseModel):
    """Score for a rubric category."""
    category: str
    score: int  # 1-3
    max_score: int = 3
    weight: float
    description: str
    feedback: str = ""


class CoverLetterComplianceReport(BaseModel):
    """Full compliance report for cover letter."""
    # Checklist results
    checklist_score: float = 0.0  # 0-100
    checklist_sections: Dict[str, SectionCheckResult] = Field(default_factory=dict)
    checklist_passed: int = 0
    checklist_total: int = 0
    
    # Rubric results
    rubric_score: float = 0.0  # 0-100
    rubric_categories: List[RubricScore] = Field(default_factory=list)
    rubric_weighted_score: float = 0.0
    
    # Overall
    overall_score: float = 0.0  # 0-100
    grade: str = ""  # A, B, C, D, F
    passed: bool = False
    
    # Feedback
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    critical_issues: List[str] = Field(default_factory=list)


class CoverLetterComplianceState(BaseModel):
    """State for Cover Letter Compliance subgraph."""
    
    # Input
    cover_letter: Optional[CoverLetter] = None
    cover_letter_text: str = ""
    structured_jd: Optional[StructuredJD] = None
    
    # Checklist validation
    checklist_results: Dict[str, SectionCheckResult] = Field(default_factory=dict)
    
    # Rubric scoring
    rubric_scores: List[RubricScore] = Field(default_factory=list)
    
    # Output
    compliance_report: Optional[CoverLetterComplianceReport] = None
    
    # Control
    validation_complete: bool = False
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_grade(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "CoverLetterComplianceState",
    "ChecklistResult",
    "SectionCheckResult",
    "RubricScore",
    "CoverLetterComplianceReport",
    "COVER_LETTER_CHECKLIST",
    "COVER_LETTER_RUBRIC",
    "get_grade"
]
