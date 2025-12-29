"""
Pipeline Parameters Configuration

Centralized parameters for controlling the job application pipeline.
These parameters help ensure resume fits on one page and maintain quality.

Usage:
    from parameters import params, ResumeParams, CoverLetterParams
    
    # Access parameters
    max_bullets = params.resume.bullets_per_experience
    
    # Override for specific run
    params.resume.bullets_per_experience = 3
"""

from parameters.resume_params import ResumeParams, RESUME_PARAMS
from parameters.cover_letter_params import CoverLetterParams, COVER_LETTER_PARAMS
from parameters.pipeline_params import PipelineParams, PIPELINE_PARAMS
from parameters.ats_params import ATSParams, ATS_PARAMS
from parameters.email_params import EmailParams, EMAIL_PARAMS

from parameters.config import (
    PipelineConfig,
    get_config,
    update_config,
    reset_config,
    ONE_PAGE_PRESET,
    TWO_PAGE_PRESET,
    COMPACT_PRESET,
    DETAILED_PRESET
)


# Global config instance
params = get_config()


__all__ = [
    # Parameter Classes
    "ResumeParams",
    "CoverLetterParams", 
    "PipelineParams",
    "ATSParams",
    "EmailParams",
    
    # Default Instances
    "RESUME_PARAMS",
    "COVER_LETTER_PARAMS",
    "PIPELINE_PARAMS",
    "ATS_PARAMS",
    "EMAIL_PARAMS",
    
    # Config
    "PipelineConfig",
    "get_config",
    "update_config",
    "reset_config",
    "params",
    
    # Presets
    "ONE_PAGE_PRESET",
    "TWO_PAGE_PRESET",
    "COMPACT_PRESET",
    "DETAILED_PRESET"
]
