"""
State Definitions for Job Application Assistant Pipeline

This module defines:
1. Individual state models for each subgraph
2. The unified ParentState that is a superset of all subgraph states
3. Type definitions and Pydantic models

Core Principle:
ParentState = Subgraph1State + Subgraph2State + ... + ParentOnlyState
"""

from typing import List, Dict, Any, Optional, Annotated
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import operator


# ============================================================================
# ENUMS
# ============================================================================

class RoleType(str, Enum):
    """Supported role types for relevance mapping."""
    ML_AI = "ml_ai"
    DATA_SCIENCE = "data_science"
    RESEARCH = "research"
    ROBOTICS_AUTOMATION = "robotics_automation"
    SOFTWARE_ENGINEERING = "software_engineering"
    SCIENTIFIC_AI = "scientific_ai"
    LLM_AI_AGENTS = "llm_ai_agents"
    DATA_ENGINEERING = "data_engineering"
    OTHER = "other"


class PipelineStatus(str, Enum):
    """Pipeline execution status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVISION = "needs_revision"


# ============================================================================
# STRUCTURED JD (Output of JD Extractor)
# ============================================================================

class StructuredJD(BaseModel):
    """Structured representation of a job description."""
    company_name: str = ""
    role_title: str = ""
    role_type: str = "ml_ai"  # Maps to RoleType
    location: str = ""
    employment_type: str = ""  # full-time, contract, internship
    experience_required: str = ""
    salary_range: Optional[str] = None
    
    skills_required: List[str] = Field(default_factory=list)
    skills_preferred: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)  # ATS keywords
    
    company_info: str = ""
    benefits: List[str] = Field(default_factory=list)
    application_url: Optional[str] = None
    
    # Metadata
    extraction_confidence: float = 0.0
    raw_text_length: int = 0


# ============================================================================
# SKILL MATCH RESULT (Output of Skill Matcher)
# ============================================================================

class SkillMatchResult(BaseModel):
    """Result of matching candidate skills to JD requirements."""
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    partial_matches: List[str] = Field(default_factory=list)
    additional_skills: List[str] = Field(default_factory=list)  # Candidate has, JD doesn't require
    
    match_percentage: float = 0.0
    skill_gap_analysis: str = ""
    
    # For ATS optimization
    critical_missing: List[str] = Field(default_factory=list)  # Must-have skills missing


# ============================================================================
# SELECTED PROJECT (Output of GitHub Ranker)
# ============================================================================

class SelectedProject(BaseModel):
    """A GitHub project selected for the resume."""
    name: str
    github_url: str = ""
    description: str = ""
    tech_stack: Dict[str, List[str]] = Field(default_factory=dict)
    
    relevance_score: float = 0.0
    matching_skills: List[str] = Field(default_factory=list)
    
    # Project details
    key_features: List[str] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=list)
    
    # Bullets
    bullets: List[str] = Field(default_factory=list)  # Final bullets for resume
    original_bullets: List[str] = Field(default_factory=list)
    rewritten_bullets: List[str] = Field(default_factory=list)
    keywords_incorporated: List[str] = Field(default_factory=list)


# ============================================================================
# SELECTED EXPERIENCE (Output of Experience Selector)
# ============================================================================

class SelectedExperience(BaseModel):
    """An experience entry selected for the resume."""
    id: int
    role: str
    role_full: str = ""
    company: str
    employment_type: str = ""
    
    dates: Dict[str, Any] = Field(default_factory=dict)  # start, end, duration, duration_months
    location: Dict[str, Any] = Field(default_factory=dict)  # city, state, country, type
    
    relevance_score: float = 0.0
    matching_keywords: List[str] = Field(default_factory=list)
    
    # Bullets
    original_bullets: List[str] = Field(default_factory=list)
    rewritten_bullets: List[str] = Field(default_factory=list)
    keywords_incorporated: List[str] = Field(default_factory=list)
    
    # Additional info
    publication: Optional[Dict[str, Any]] = None
    project: Optional[str] = None
    scope: str = ""


# ============================================================================
# RESUME JSON (Output of Resume Builder)
# ============================================================================

class ResumeJSON(BaseModel):
    """Complete resume structure."""
    header: Dict[str, str] = Field(default_factory=dict)
    summary: str = ""
    
    education: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    
    skills: Dict[str, str] = Field(default_factory=dict)  # Category: "skill1, skill2, ..."
    publications: List[str] = Field(default_factory=list)
    
    # Metadata
    version: int = 1
    last_modified: str = ""
    tailored_for: str = ""  # Company + Role


# ============================================================================
# ATS ANALYSIS (Output of ATS Optimizer)
# ============================================================================

class ATSAnalysis(BaseModel):
    """ATS optimization analysis results."""
    score: int = 0  # 0-100
    
    keyword_density: float = 0.0
    keywords_found: List[str] = Field(default_factory=list)
    keywords_missing: List[str] = Field(default_factory=list)
    
    format_issues: List[str] = Field(default_factory=list)
    section_scores: Dict[str, int] = Field(default_factory=dict)
    
    suggestions: List[str] = Field(default_factory=list)
    passed: bool = False  # score >= 95


# ============================================================================
# COMPLIANCE RESULT (Output of Resource Compliance)
# ============================================================================

class ComplianceResult(BaseModel):
    """Resume compliance check results."""
    # Checklist
    checklist_passed: bool = False
    checklist_failures: List[str] = Field(default_factory=list)
    
    # Rubric (4-point scale)
    rubric_score: float = 0.0
    rubric_section_scores: Dict[str, int] = Field(default_factory=dict)
    rubric_passed: bool = False  # score >= 3.5
    
    # Action verb compliance
    action_verb_compliance: float = 0.0
    action_verb_issues: List[str] = Field(default_factory=list)
    
    # Overall
    all_passed: bool = False
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


# ============================================================================
# COVER LETTER (Output of Cover Letter Generator)
# ============================================================================

class CoverLetterJSON(BaseModel):
    """Structured cover letter."""
    header: Dict[str, str] = Field(default_factory=dict)
    date: str = ""
    
    recipient: Dict[str, str] = Field(default_factory=dict)  # name, title, company, address
    
    salutation: str = ""
    opening: str = ""
    body_paragraphs: List[str] = Field(default_factory=list)
    closing: str = ""
    signature: str = ""
    
    # Metadata
    version: int = 1
    word_count: int = 0


class CLComplianceResult(BaseModel):
    """Cover letter compliance check results."""
    # Checklist
    checklist_passed: bool = False
    checklist_failures: List[str] = Field(default_factory=list)
    
    # Rubric (3-point scale)
    rubric_score: float = 0.0
    rubric_section_scores: Dict[str, int] = Field(default_factory=dict)
    rubric_passed: bool = False  # score >= 2.5
    
    # Overall
    all_passed: bool = False
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


# ============================================================================
# RECRUITER EMAIL (Output of Email Generator)
# ============================================================================

class RecruiterEmail(BaseModel):
    """Email to recruiter."""
    subject: str = ""
    body: str = ""
    signature: str = ""
    attachments_note: str = ""


# ============================================================================
# OUTPUT FILES (Final outputs)
# ============================================================================

class OutputFiles(BaseModel):
    """Paths to generated output files."""
    resume_json_path: str = ""
    resume_docx_path: str = ""
    resume_pdf_path: str = ""
    cover_letter_docx_path: str = ""
    cover_letter_pdf_path: str = ""
    email_txt_path: str = ""
    application_folder: str = ""


# ============================================================================
# SUBGRAPH STATES
# ============================================================================

class JDExtractorState(BaseModel):
    """State for JD Extractor subgraph."""
    raw_jd_text: str = ""
    structured_jd: Optional[StructuredJD] = None
    extraction_error: Optional[str] = None


class SkillMatcherState(BaseModel):
    """State for Skill Matcher subgraph."""
    structured_jd: Optional[StructuredJD] = None
    candidate_skills: List[str] = Field(default_factory=list)
    skill_match_result: Optional[SkillMatchResult] = None


class GitHubRankerState(BaseModel):
    """State for GitHub Ranker subgraph."""
    structured_jd: Optional[StructuredJD] = None
    selected_projects: List[SelectedProject] = Field(default_factory=list)
    max_projects: int = 3


class ExperienceSelectorState(BaseModel):
    """State for Experience Selector subgraph."""
    structured_jd: Optional[StructuredJD] = None
    selected_experiences: List[SelectedExperience] = Field(default_factory=list)
    max_experiences: int = 4


class ExperienceRewriterState(BaseModel):
    """State for Experience Rewriter subgraph."""
    structured_jd: Optional[StructuredJD] = None
    selected_experiences: List[SelectedExperience] = Field(default_factory=list)
    selected_projects: List[SelectedProject] = Field(default_factory=list)
    rewritten_experiences: List[SelectedExperience] = Field(default_factory=list)
    rewritten_projects: List[SelectedProject] = Field(default_factory=list)
    rewrite_iteration: int = 0


class ResumeBuilderState(BaseModel):
    """State for Resume JSON Builder subgraph."""
    structured_jd: Optional[StructuredJD] = None
    rewritten_experiences: List[SelectedExperience] = Field(default_factory=list)
    rewritten_projects: List[SelectedProject] = Field(default_factory=list)
    resume_json: Optional[ResumeJSON] = None


class ATSOptimizerState(BaseModel):
    """State for ATS Optimizer subgraph."""
    structured_jd: Optional[StructuredJD] = None
    resume_json: Optional[ResumeJSON] = None
    ats_analysis: Optional[ATSAnalysis] = None
    ats_iteration: int = 0
    max_ats_iterations: int = 3


class ResourceComplianceState(BaseModel):
    """State for Resource Compliance subgraph."""
    resume_json: Optional[ResumeJSON] = None
    compliance_result: Optional[ComplianceResult] = None
    compliance_iteration: int = 0
    max_compliance_iterations: int = 3


class CoverLetterState(BaseModel):
    """State for Cover Letter Generator subgraph."""
    structured_jd: Optional[StructuredJD] = None
    skill_match_result: Optional[SkillMatchResult] = None
    selected_experiences: List[SelectedExperience] = Field(default_factory=list)
    cover_letter_text: str = ""
    cover_letter_json: Optional[CoverLetterJSON] = None
    cl_compliance_result: Optional[CLComplianceResult] = None
    cl_iteration: int = 0
    max_cl_iterations: int = 3


class EmailGeneratorState(BaseModel):
    """State for Recruiter Email Generator subgraph."""
    structured_jd: Optional[StructuredJD] = None
    recruiter_email: Optional[RecruiterEmail] = None


class ExcelWriterState(BaseModel):
    """State for Excel Writer subgraph."""
    structured_jd: Optional[StructuredJD] = None
    ats_analysis: Optional[ATSAnalysis] = None
    compliance_result: Optional[ComplianceResult] = None
    cl_compliance_result: Optional[CLComplianceResult] = None
    output_files: Optional[OutputFiles] = None
    excel_updated: bool = False
    application_id: str = ""


# ============================================================================
# PARENT STATE (SUPERSET OF ALL SUBGRAPH STATES)
# ============================================================================

class ParentState(BaseModel):
    """
    Unified parent state that is a superset of all subgraph states.
    
    This is the main state model used by the parent graph.
    All fields from all subgraphs are included here.
    """
    
    # ===== INPUT =====
    raw_jd_text: str = ""
    
    # ===== JD EXTRACTOR OUTPUT =====
    structured_jd: Optional[StructuredJD] = None
    extraction_error: Optional[str] = None
    
    # ===== CANDIDATE DATA (loaded from files) =====
    candidate_header: Dict[str, str] = Field(default_factory=dict)
    candidate_summary: str = ""
    candidate_education: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_certifications: List[str] = Field(default_factory=list)
    candidate_skills: Dict[str, str] = Field(default_factory=dict)
    candidate_skills_flat: List[str] = Field(default_factory=list)
    candidate_publications: List[str] = Field(default_factory=list)
    candidate_experiences: List[Dict[str, Any]] = Field(default_factory=list)
    
    # ===== SKILL MATCHER OUTPUT =====
    skill_match_result: Optional[SkillMatchResult] = None
    
    # ===== GITHUB RANKER OUTPUT =====
    selected_projects: List[SelectedProject] = Field(default_factory=list)
    max_projects: int = 3
    
    # ===== EXPERIENCE SELECTOR OUTPUT =====
    selected_experiences: List[SelectedExperience] = Field(default_factory=list)
    max_experiences: int = 4
    
    # ===== EXPERIENCE REWRITER OUTPUT =====
    rewritten_experiences: List[SelectedExperience] = Field(default_factory=list)
    rewritten_projects: List[SelectedProject] = Field(default_factory=list)
    rewrite_iteration: int = 0
    
    # ===== RESUME BUILDER OUTPUT =====
    resume_json: Optional[ResumeJSON] = None
    resume_version: int = 1
    
    # ===== ATS OPTIMIZER OUTPUT =====
    ats_analysis: Optional[ATSAnalysis] = None
    ats_iteration: int = 0
    max_ats_iterations: int = 3
    ats_passed: bool = False
    
    # ===== RESOURCE COMPLIANCE OUTPUT =====
    compliance_result: Optional[ComplianceResult] = None
    compliance_iteration: int = 0
    max_compliance_iterations: int = 3
    compliance_passed: bool = False
    
    # ===== COVER LETTER OUTPUT =====
    cover_letter_text: str = ""
    cover_letter_json: Optional[CoverLetterJSON] = None
    cl_compliance_result: Optional[CLComplianceResult] = None
    cl_iteration: int = 0
    max_cl_iterations: int = 3
    cl_passed: bool = False
    
    # ===== EMAIL OUTPUT =====
    recruiter_email: Optional[RecruiterEmail] = None
    
    # ===== FINAL OUTPUT =====
    output_files: Optional[OutputFiles] = None
    excel_updated: bool = False
    application_id: str = ""
    
    # ===== PIPELINE CONTROL =====
    pipeline_status: str = "not_started"
    current_stage: str = ""
    error_message: Optional[str] = None
    
    # ===== RESOURCES (loaded from files) =====
    action_verbs: Dict[str, List[str]] = Field(default_factory=dict)
    resume_checklist: Dict[str, List[str]] = Field(default_factory=dict)
    resume_rubric: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    cover_letter_checklist: Dict[str, List[str]] = Field(default_factory=dict)
    cover_letter_rubric: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    resume_guide: str = ""
    cover_letter_guide: str = ""
    
    # ===== METADATA =====
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = ""
    total_iterations: int = 0
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_initial_state(raw_jd_text: str) -> ParentState:
    """
    Create initial parent state with raw JD text.
    
    This is the entry point for the pipeline.
    """
    return ParentState(
        raw_jd_text=raw_jd_text,
        pipeline_status="not_started",
        current_stage="initialization",
        created_at=datetime.now().isoformat()
    )


def update_state_timestamp(state: ParentState) -> ParentState:
    """Update the last_updated timestamp."""
    state.last_updated = datetime.now().isoformat()
    return state


# ============================================================================
# STATE FIELD MAPPINGS (for subgraph integration)
# ============================================================================

# Maps subgraph state fields to parent state fields
# Used for automatic state synchronization

SUBGRAPH_FIELD_MAPPINGS = {
    "jd_extractor": {
        "inputs": ["raw_jd_text"],
        "outputs": ["structured_jd", "extraction_error"]
    },
    "skill_matcher": {
        "inputs": ["structured_jd", "candidate_skills_flat"],
        "outputs": ["skill_match_result"]
    },
    "github_ranker": {
        "inputs": ["structured_jd", "max_projects"],
        "outputs": ["selected_projects"]
    },
    "experience_selector": {
        "inputs": ["structured_jd", "candidate_experiences", "max_experiences"],
        "outputs": ["selected_experiences"]
    },
    "experience_rewriter": {
        "inputs": ["structured_jd", "selected_experiences", "selected_projects", 
                   "action_verbs", "resume_guide"],
        "outputs": ["rewritten_experiences", "rewritten_projects", "rewrite_iteration"]
    },
    "resume_builder": {
        "inputs": ["structured_jd", "candidate_header", "candidate_summary",
                   "candidate_education", "candidate_certifications", "candidate_skills",
                   "candidate_publications", "rewritten_experiences", "rewritten_projects"],
        "outputs": ["resume_json", "resume_version"]
    },
    "ats_optimizer": {
        "inputs": ["structured_jd", "resume_json", "max_ats_iterations"],
        "outputs": ["ats_analysis", "ats_iteration", "ats_passed", "resume_json"]
    },
    "resource_compliance": {
        "inputs": ["resume_json", "resume_checklist", "resume_rubric", 
                   "action_verbs", "max_compliance_iterations"],
        "outputs": ["compliance_result", "compliance_iteration", "compliance_passed", "resume_json"]
    },
    "cover_letter_generator": {
        "inputs": ["structured_jd", "candidate_header", "candidate_summary",
                   "skill_match_result", "selected_experiences", 
                   "cover_letter_guide", "cover_letter_checklist"],
        "outputs": ["cover_letter_text", "cover_letter_json", "cl_iteration"]
    },
    "cover_letter_compliance": {
        "inputs": ["cover_letter_text", "cover_letter_checklist", 
                   "cover_letter_rubric", "max_cl_iterations"],
        "outputs": ["cl_compliance_result", "cl_iteration", "cl_passed", "cover_letter_text"]
    },
    "email_generator": {
        "inputs": ["structured_jd", "candidate_header", "candidate_summary"],
        "outputs": ["recruiter_email"]
    },
    "excel_writer": {
        "inputs": ["structured_jd", "ats_analysis", "compliance_result",
                   "cl_compliance_result", "output_files"],
        "outputs": ["excel_updated", "application_id"]
    }
}


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "RoleType",
    "PipelineStatus",
    
    # Data Models
    "StructuredJD",
    "SkillMatchResult",
    "SelectedProject",
    "SelectedExperience",
    "ResumeJSON",
    "ATSAnalysis",
    "ComplianceResult",
    "CoverLetterJSON",
    "CLComplianceResult",
    "RecruiterEmail",
    "OutputFiles",
    
    # Subgraph States
    "JDExtractorState",
    "SkillMatcherState",
    "GitHubRankerState",
    "ExperienceSelectorState",
    "ExperienceRewriterState",
    "ResumeBuilderState",
    "ATSOptimizerState",
    "ResourceComplianceState",
    "CoverLetterState",
    "EmailGeneratorState",
    "ExcelWriterState",
    
    # Parent State
    "ParentState",
    
    # Helper Functions
    "create_initial_state",
    "update_state_timestamp",
    
    # Mappings
    "SUBGRAPH_FIELD_MAPPINGS"
]
