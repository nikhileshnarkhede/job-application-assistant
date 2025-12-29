"""
State module for Job Application Assistant Pipeline.

Contains shared data models used across multiple subgraphs:
- StructuredJD
- ResumeJSON  
- SkillMatchResult
- SelectedProject
- SelectedExperience
- And more...
"""

from state.state_models import (
    # Enums
    RoleType,
    PipelineStatus,
    
    # Core Data Models (used by multiple subgraphs)
    StructuredJD,
    SkillMatchResult,
    SelectedProject,
    SelectedExperience,
    ResumeJSON,
    ATSAnalysis,
    ComplianceResult,
    CoverLetterJSON,
    CLComplianceResult,
    RecruiterEmail,
    OutputFiles,
    
    # Parent State (for orchestration)
    ParentState,
    
    # Helper Functions
    create_initial_state,
    update_state_timestamp,
    
    # Mappings
    SUBGRAPH_FIELD_MAPPINGS
)

__all__ = [
    # Enums
    "RoleType",
    "PipelineStatus",
    
    # Core Data Models
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
    
    # Parent State
    "ParentState",
    
    # Helper Functions
    "create_initial_state",
    "update_state_timestamp",
    
    # Mappings
    "SUBGRAPH_FIELD_MAPPINGS"
]
