"""
Pipeline Configuration

Unified configuration combining all parameter modules.
Provides presets and easy access to all parameters.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from parameters.resume_params import ResumeParams, RESUME_PARAMS
from parameters.cover_letter_params import CoverLetterParams, COVER_LETTER_PARAMS
from parameters.pipeline_params import PipelineParams, PIPELINE_PARAMS
from parameters.ats_params import ATSParams, ATS_PARAMS
from parameters.email_params import EmailParams, EMAIL_PARAMS


class PipelineConfig(BaseModel):
    """
    Unified configuration for the entire pipeline.
    
    Usage:
        from parameters import params
        
        # Access parameters
        params.resume.max_experiences
        params.ats.target_score
        params.pipeline.max_iterations
        
        # Modify parameters
        params.resume.bullets_per_experience = 3
        
        # Use presets
        from parameters import ONE_PAGE_PRESET
        config = PipelineConfig(**ONE_PAGE_PRESET)
    """
    
    resume: ResumeParams = Field(default_factory=ResumeParams)
    cover_letter: CoverLetterParams = Field(default_factory=CoverLetterParams)
    pipeline: PipelineParams = Field(default_factory=PipelineParams)
    ats: ATSParams = Field(default_factory=ATSParams)
    email: EmailParams = Field(default_factory=EmailParams)
    
    class Config:
        """Pydantic config."""
        validate_assignment = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire config to dictionary."""
        return {
            "resume": self.resume.model_dump(),
            "cover_letter": self.cover_letter.model_dump(),
            "pipeline": self.pipeline.model_dump(),
            "ats": self.ats.model_dump(),
            "email": self.email.model_dump()
        }
    
    def summary(self) -> str:
        """Get a human-readable summary of key parameters."""
        return f"""
Pipeline Configuration Summary
==============================

RESUME (One Page Target):
  - Max Experiences: {self.resume.max_experiences}
  - Bullets/Experience: {self.resume.bullets_per_experience}
  - Max Projects: {self.resume.max_projects}
  - Bullets/Project: {self.resume.bullets_per_project}
  - Bullet Words: {self.resume.bullet_min_words}-{self.resume.bullet_max_words}
  - Target Total Words: {self.resume.target_total_words}
  - Summary Words: {self.resume.summary_min_words}-{self.resume.summary_max_words}
  - Skill Categories: {self.resume.max_skill_categories}

COVER LETTER:
  - Target Words: {self.cover_letter.target_total_words}
  - Body Paragraphs: {self.cover_letter.num_body_paragraphs}
  - Personalization: {self.cover_letter.personalization_level}

ATS:
  - Target Score: {self.ats.target_score}%
  - Max Iterations: {self.ats.max_iterations}
  - Keyword Match: {self.ats.required_keyword_match_pct * 100:.0f}%

PIPELINE:
  - Max ATS Iterations: {self.pipeline.max_ats_iterations}
  - Max Compliance Iterations: {self.pipeline.max_compliance_iterations}
  - ATS Pass Threshold: {self.pipeline.ats_pass_threshold}%
  - Compliance Pass Threshold: {self.pipeline.compliance_pass_threshold}%
"""


# =========================================================================
# GLOBAL INSTANCE
# =========================================================================

_config: Optional[PipelineConfig] = None


def get_config() -> PipelineConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = PipelineConfig()
    return _config


def update_config(**kwargs) -> PipelineConfig:
    """
    Update configuration parameters.
    
    Usage:
        update_config(
            resume={"max_experiences": 3, "bullets_per_experience": 3},
            ats={"target_score": 90}
        )
    """
    global _config
    config = get_config()
    
    if "resume" in kwargs:
        for key, value in kwargs["resume"].items():
            setattr(config.resume, key, value)
    
    if "cover_letter" in kwargs:
        for key, value in kwargs["cover_letter"].items():
            setattr(config.cover_letter, key, value)
    
    if "pipeline" in kwargs:
        for key, value in kwargs["pipeline"].items():
            setattr(config.pipeline, key, value)
    
    if "ats" in kwargs:
        for key, value in kwargs["ats"].items():
            setattr(config.ats, key, value)
    
    if "email" in kwargs:
        for key, value in kwargs["email"].items():
            setattr(config.email, key, value)
    
    return config


def reset_config() -> PipelineConfig:
    """Reset configuration to defaults."""
    global _config
    _config = PipelineConfig()
    return _config


def apply_preset(preset: Dict[str, Any]) -> PipelineConfig:
    """Apply a preset configuration."""
    global _config
    _config = PipelineConfig(**preset)
    return _config


# =========================================================================
# PRESETS
# =========================================================================

ONE_PAGE_PRESET = {
    "resume": ResumeParams(
        target_total_words=500,
        max_total_words=550,
        max_experiences=4,
        bullets_per_experience=4,
        max_bullets_per_experience=4,
        bullet_max_words=22,
        max_projects=2,
        bullets_per_project=2,
        summary_max_words=45,
        max_skill_categories=5,
        max_skills_per_category=8,
        include_coursework=False,
        max_certifications=3,
        max_publications=1
    ),
    "cover_letter": CoverLetterParams(
        target_total_words=300,
        max_total_words=350,
        num_body_paragraphs=2
    ),
    "pipeline": PipelineParams(
        max_experiences_to_select=4,
        max_projects_to_select=2
    ),
    "ats": ATSParams(
        target_score=95,
        max_iterations=3
    )
}

TWO_PAGE_PRESET = {
    "resume": ResumeParams(
        target_total_words=900,
        max_total_words=1100,
        max_experiences=6,
        bullets_per_experience=5,
        max_bullets_per_experience=6,
        bullet_max_words=28,
        max_projects=4,
        bullets_per_project=3,
        summary_max_words=70,
        max_skill_categories=8,
        max_skills_per_category=12,
        include_coursework=True,
        max_coursework_items=6,
        max_certifications=6,
        max_publications=3
    ),
    "cover_letter": CoverLetterParams(
        target_total_words=400,
        max_total_words=450,
        num_body_paragraphs=3
    ),
    "pipeline": PipelineParams(
        max_experiences_to_select=6,
        max_projects_to_select=4
    )
}

COMPACT_PRESET = {
    "resume": ResumeParams(
        target_total_words=400,
        max_total_words=450,
        max_experiences=3,
        bullets_per_experience=3,
        max_bullets_per_experience=3,
        bullet_max_words=18,
        max_projects=2,
        bullets_per_project=2,
        project_bullet_max_words=18,
        summary_max_words=35,
        max_skill_categories=4,
        max_skills_per_category=6,
        include_coursework=False,
        max_certifications=2,
        max_publications=1,
        include_publications=False
    ),
    "cover_letter": CoverLetterParams(
        target_total_words=250,
        max_total_words=280,
        num_body_paragraphs=2
    ),
    "pipeline": PipelineParams(
        max_experiences_to_select=3,
        max_projects_to_select=2
    )
}

DETAILED_PRESET = {
    "resume": ResumeParams(
        target_total_words=600,
        max_total_words=650,
        max_experiences=4,
        bullets_per_experience=5,
        max_bullets_per_experience=5,
        bullet_max_words=25,
        max_projects=3,
        bullets_per_project=3,
        summary_max_words=55,
        max_skill_categories=6,
        max_skills_per_category=10,
        include_coursework=True,
        max_coursework_items=4
    ),
    "cover_letter": CoverLetterParams(
        target_total_words=350,
        max_total_words=400,
        num_body_paragraphs=2,
        include_metrics=True
    ),
    "pipeline": PipelineParams(
        max_experiences_to_select=4,
        max_projects_to_select=3
    )
}


# =========================================================================
# EXPORTS
# =========================================================================

__all__ = [
    "PipelineConfig",
    "get_config",
    "update_config",
    "reset_config",
    "apply_preset",
    "ONE_PAGE_PRESET",
    "TWO_PAGE_PRESET",
    "COMPACT_PRESET",
    "DETAILED_PRESET"
]
