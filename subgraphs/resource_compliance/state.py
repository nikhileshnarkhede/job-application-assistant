"""
Resource Compliance Subgraph State

Validates resume against:
1. Resume Checklist (detailed item-by-item check)
2. Resume Rubric (scoring across 4 categories)
3. Resume Guide (best practices validation)
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

import sys
sys.path.append("../..")
from state.state_models import ResumeJSON


# ============================================================================
# CHECKLIST ITEMS - Parsed from Resume Checklist.txt
# ============================================================================

RESUME_CHECKLIST = {
    "personal_info": {
        "name": "Personal Information",
        "items": [
            {"id": "pi_1", "text": "Located at the top of the page", "required": True},
            {"id": "pi_2", "text": "First and last name in larger font (14-16pt)", "required": True},
            {"id": "pi_3", "text": "One phone number included", "required": True},
            {"id": "pi_4", "text": "One professional email address", "required": True},
            {"id": "pi_5", "text": "LinkedIn URL included (if active)", "required": False},
            {"id": "pi_6", "text": "Does not take excessive space", "required": True},
        ]
    },
    "education": {
        "name": "Education Section",
        "items": [
            {"id": "ed_1", "text": "Institution name with city and state", "required": True},
            {"id": "ed_2", "text": "Degree listed accurately", "required": True},
            {"id": "ed_3", "text": "Graduation date or expected date", "required": True},
            {"id": "ed_4", "text": "Major/minor titles complete", "required": True},
            {"id": "ed_5", "text": "GPA included if above 3.0", "required": False},
            {"id": "ed_6", "text": "Dean's list or academic awards", "required": False},
            {"id": "ed_7", "text": "High school removed (if 2+ years in college)", "required": False},
        ]
    },
    "experience": {
        "name": "Experience Section",
        "items": [
            {"id": "ex_1", "text": "Employer name with city and state", "required": True},
            {"id": "ex_2", "text": "Dates in month-year format", "required": True},
            {"id": "ex_3", "text": "Position title clearly stated", "required": True},
            {"id": "ex_4", "text": "Bullets start with action verbs", "required": True},
            {"id": "ex_5", "text": "Action verbs in appropriate tense", "required": True},
            {"id": "ex_6", "text": "Achievements quantified with numbers/percentages", "required": True},
            {"id": "ex_7", "text": "Listed in reverse chronological order", "required": True},
            {"id": "ex_8", "text": "No passive phrases (worked with, responsible for)", "required": True},
            {"id": "ex_9", "text": "No repetition across similar experiences", "required": True},
        ]
    },
    "skills": {
        "name": "Skills Section",
        "items": [
            {"id": "sk_1", "text": "Skills organized by category", "required": True},
            {"id": "sk_2", "text": "Technical skills highlighted", "required": True},
            {"id": "sk_3", "text": "No soft skill adjectives (hardworking, punctual)", "required": True},
            {"id": "sk_4", "text": "Language proficiency specified (fluent/conversational)", "required": False},
            {"id": "sk_5", "text": "Certifications included if applicable", "required": False},
        ]
    },
    "format": {
        "name": "Format & Appearance",
        "items": [
            {"id": "fm_1", "text": "No text boxes, shading, or graphics", "required": True},
            {"id": "fm_2", "text": "No headers or footers", "required": True},
            {"id": "fm_3", "text": "No photos or images", "required": True},
            {"id": "fm_4", "text": "Original design, not a template", "required": False},
            {"id": "fm_5", "text": "Clear sections with ample white space", "required": True},
            {"id": "fm_6", "text": "Appropriate length (1-2 pages)", "required": True},
            {"id": "fm_7", "text": "Consistent margins on all sides", "required": True},
            {"id": "fm_8", "text": "Consistent font size and spacing", "required": True},
            {"id": "fm_9", "text": "Sections clearly labeled", "required": True},
        ]
    },
    "content": {
        "name": "Content Quality",
        "items": [
            {"id": "ct_1", "text": "No personal pronouns (I, me, my, we, our)", "required": True},
            {"id": "ct_2", "text": "No spelling errors", "required": True},
            {"id": "ct_3", "text": "No grammar errors", "required": True},
            {"id": "ct_4", "text": "Keyword-rich with industry terms", "required": True},
            {"id": "ct_5", "text": "Strong, varied action verbs", "required": True},
            {"id": "ct_6", "text": "Logical content flow", "required": True},
            {"id": "ct_7", "text": "Sections in optimal order for credentials", "required": True},
        ]
    }
}


# ============================================================================
# RUBRIC SCORING - From Resume rubric.xlsx
# ============================================================================

RESUME_RUBRIC = {
    "format": {
        "name": "Format",
        "weight": 0.20,
        "levels": {
            4: "Fills page but not overcrowded. No grammar/spelling errors. Easy to scan.",
            3: "Almost fills page with some uneven white space. May have single error.",
            2: "Font/spacing not appealing. Cannot be easily scanned. Multiple errors.",
            1: "Half page or 3+ pages. Too much white space. Multiple errors."
        }
    },
    "education": {
        "name": "Education Section",
        "weight": 0.20,
        "levels": {
            4: "Organized, clear, well-defined. Includes institution, location, date, major, degree, GPA, relevant coursework.",
            3: "Well organized. Includes institution, date, major, degree. Missing GPA or extras.",
            2: "Includes institution and major but missing degree/GPA. Not well organized.",
            1: "Missing crucial info. No location, graduation date, or degree listed."
        }
    },
    "experience": {
        "name": "Experience Section",
        "weight": 0.40,
        "levels": {
            4: "Well-defined, relates to career field. All info included. Bullets with action verbs.",
            3: "All info included. Bullets with action verbs but not detailed enough.",
            2: "Descriptions in paragraph form. Missing locations, dates, or titles.",
            1: "No order to descriptions. Missing locations and dates."
        }
    },
    "activities": {
        "name": "Honors/Activities",
        "weight": 0.20,
        "levels": {
            4: "Well organized. Activities listed with skills and leadership roles. Dates included.",
            3: "Includes info but difficult to follow. Leadership listed but skills not defined.",
            2: "Missing key info like leadership positions or dates.",
            1: "Missing or contains very little info. No descriptions."
        }
    }
}


# ============================================================================
# STATE MODEL
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
    score: int  # 1-4
    max_score: int = 4
    weight: float
    description: str
    feedback: str = ""


class ComplianceReport(BaseModel):
    """Full compliance report."""
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


class ResourceComplianceState(BaseModel):
    """State for Resource Compliance subgraph."""
    
    # Input
    resume_json: Optional[ResumeJSON] = None
    resume_text: str = ""
    
    # Checklist validation
    checklist_results: Dict[str, SectionCheckResult] = Field(default_factory=dict)
    
    # Rubric scoring
    rubric_scores: List[RubricScore] = Field(default_factory=list)
    
    # Output
    compliance_report: Optional[ComplianceReport] = None
    
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
    "ResourceComplianceState",
    "ChecklistResult",
    "SectionCheckResult",
    "RubricScore",
    "ComplianceReport",
    "RESUME_CHECKLIST",
    "RESUME_RUBRIC",
    "get_grade"
]
