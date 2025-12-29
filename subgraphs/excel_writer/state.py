"""
Excel Writer Subgraph State

Saves job application data to Excel tracking spreadsheet:
1. Application details (company, role, date, status)
2. Resume version used
3. Cover letter version used
4. Contact information
5. Follow-up tracking
6. Notes and outcomes
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

import sys
sys.path.append("../..")
from state.state_models import StructuredJD, ResumeJSON


# ============================================================================
# APPLICATION STATUS
# ============================================================================

class ApplicationStatus(str, Enum):
    """Status of job application."""
    NOT_APPLIED = "Not Applied"
    APPLIED = "Applied"
    REFERRED = "Referred"
    PHONE_SCREEN = "Phone Screen"
    TECHNICAL_INTERVIEW = "Technical Interview"
    ONSITE = "Onsite"
    FINAL_ROUND = "Final Round"
    OFFER = "Offer"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"
    NO_RESPONSE = "No Response"


class ApplicationSource(str, Enum):
    """How the application was sourced."""
    COMPANY_WEBSITE = "Company Website"
    LINKEDIN = "LinkedIn"
    INDEED = "Indeed"
    GLASSDOOR = "Glassdoor"
    REFERRAL = "Referral"
    RECRUITER = "Recruiter"
    CAREER_FAIR = "Career Fair"
    NETWORKING = "Networking"
    OTHER = "Other"


# ============================================================================
# SPREADSHEET COLUMNS
# ============================================================================

SPREADSHEET_COLUMNS = [
    # Basic Info
    "Application ID",
    "Company",
    "Role",
    "Location",
    "Job URL",
    
    # Dates
    "Date Found",
    "Date Applied",
    "Last Updated",
    
    # Status
    "Status",
    "Source",
    "Referral Name",
    
    # Compensation
    "Salary Range",
    "Remote/Hybrid/Onsite",
    
    # Documents
    "Resume Version",
    "Cover Letter Version",
    "Resume Score",
    "Cover Letter Score",
    
    # Contacts
    "Recruiter Name",
    "Recruiter Email",
    "Hiring Manager",
    
    # Tracking
    "Next Follow-Up",
    "Last Contact Date",
    "Interview Dates",
    
    # Outcomes
    "Offer Amount",
    "Response Time (Days)",
    
    # Notes
    "Notes",
    "Key Requirements",
    "Why Interested"
]


# ============================================================================
# APPLICATION RECORD
# ============================================================================

class ApplicationRecord(BaseModel):
    """Single job application record."""
    # Basic Info
    application_id: str = ""
    company: str = ""
    role: str = ""
    location: str = ""
    job_url: str = ""
    
    # Dates
    date_found: str = ""
    date_applied: str = ""
    last_updated: str = ""
    
    # Status
    status: ApplicationStatus = ApplicationStatus.NOT_APPLIED
    source: ApplicationSource = ApplicationSource.COMPANY_WEBSITE
    referral_name: str = ""
    
    # Compensation
    salary_range: str = ""
    work_type: str = ""  # Remote/Hybrid/Onsite
    
    # Documents
    resume_version: str = ""
    cover_letter_version: str = ""
    resume_score: float = 0.0
    cover_letter_score: float = 0.0
    
    # Contacts
    recruiter_name: str = ""
    recruiter_email: str = ""
    hiring_manager: str = ""
    
    # Tracking
    next_followup: str = ""
    last_contact_date: str = ""
    interview_dates: str = ""
    
    # Outcomes
    offer_amount: str = ""
    response_time_days: int = 0
    
    # Notes
    notes: str = ""
    key_requirements: str = ""
    why_interested: str = ""


# ============================================================================
# SPREADSHEET CONFIG
# ============================================================================

class SpreadsheetConfig(BaseModel):
    """Configuration for Excel spreadsheet."""
    file_path: str = "job_applications.xlsx"
    sheet_name: str = "Applications"
    
    # Formatting
    header_color: str = "4472C4"  # Blue
    alternate_row_color: str = "D9E2F3"  # Light blue
    date_format: str = "YYYY-MM-DD"
    
    # Column widths
    column_widths: Dict[str, int] = Field(default_factory=lambda: {
        "Application ID": 15,
        "Company": 20,
        "Role": 30,
        "Location": 15,
        "Job URL": 40,
        "Status": 15,
        "Notes": 50
    })
    
    # Auto-filter
    enable_filter: bool = True
    freeze_header: bool = True


# ============================================================================
# STATE MODEL
# ============================================================================

class ExcelWriterState(BaseModel):
    """State for Excel Writer subgraph."""
    
    # Input
    structured_jd: Optional[StructuredJD] = None
    resume_json: Optional[ResumeJSON] = None
    
    # Scores from compliance checks
    resume_score: float = 0.0
    cover_letter_score: float = 0.0
    
    # Application details
    application_record: Optional[ApplicationRecord] = None
    
    # Configuration
    config: SpreadsheetConfig = Field(default_factory=SpreadsheetConfig)
    
    # Output
    file_path: str = ""
    row_number: int = 0
    
    # Control
    write_complete: bool = False
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_application_id() -> str:
    """Generate unique application ID."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"APP-{timestamp}"


def get_today() -> str:
    """Get today's date formatted."""
    return datetime.now().strftime("%Y-%m-%d")


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "ExcelWriterState",
    "ApplicationStatus",
    "ApplicationSource",
    "ApplicationRecord",
    "SpreadsheetConfig",
    "SPREADSHEET_COLUMNS",
    "generate_application_id",
    "get_today"
]
