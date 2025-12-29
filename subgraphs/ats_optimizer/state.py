"""
ATS Optimizer Subgraph State

This module defines the state specific to the ATS Optimizer subgraph.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Import from parent state
import sys
sys.path.append("../..")
from state.state_models import StructuredJD, ResumeJSON, ATSAnalysis, SkillMatchResult


class ATSOptimizerState(BaseModel):
    """
    State for ATS Optimizer subgraph.
    
    This subgraph handles:
    1. Extracting and weighting JD keywords
    2. Scanning resume content for keywords
    3. Calculating ATS score
    4. Checking format compliance
    5. Generating improvement suggestions
    6. Applying suggestions (iteratively)
    """
    
    # ===== INPUT =====
    structured_jd: Optional[StructuredJD] = None
    resume_json: Optional[ResumeJSON] = None
    skill_match_result: Optional[SkillMatchResult] = None
    
    # ===== KEYWORD ANALYSIS =====
    target_keywords: Dict[str, float] = Field(default_factory=dict)  # keyword: weight
    resume_text_by_section: Dict[str, str] = Field(default_factory=dict)
    resume_text_full: str = ""
    
    # ===== MATCHING RESULTS =====
    keywords_found: List[str] = Field(default_factory=list)
    keywords_missing: List[str] = Field(default_factory=list)
    keyword_locations: Dict[str, List[str]] = Field(default_factory=dict)  # keyword: [sections]
    
    # ===== SCORES =====
    ats_score: int = 0
    keyword_density: float = 0.0
    section_scores: Dict[str, int] = Field(default_factory=dict)
    
    # ===== FORMAT ANALYSIS =====
    format_issues: List[str] = Field(default_factory=list)
    format_score: int = 100
    
    # ===== SUGGESTIONS =====
    suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    applied_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # ===== OUTPUT =====
    ats_analysis: Optional[ATSAnalysis] = None
    optimized_resume: Optional[ResumeJSON] = None
    
    # ===== CONTROL =====
    iteration: int = 0
    max_iterations: int = 3
    target_score: int = 95
    optimization_complete: bool = False
    passed: bool = False
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# KEYWORD WEIGHTS
# ============================================================================

KEYWORD_WEIGHTS = {
    "required_skills": 3.0,      # Must have - highest weight
    "preferred_skills": 2.0,     # Nice to have
    "responsibilities": 1.5,     # Action words from responsibilities
    "qualifications": 1.5,       # Education, experience keywords
    "general_keywords": 1.0      # Other extracted keywords
}

# Section weights for where keywords appear
SECTION_WEIGHTS = {
    "summary": 1.5,       # Keywords here are highly visible
    "skills": 2.0,        # Skills section is critical for ATS
    "experience": 1.5,    # Experience bullets
    "projects": 1.2,      # Project descriptions
    "education": 1.0,     # Education section
    "certifications": 1.0
}

# Score component weights
SCORE_WEIGHTS = {
    "required_skills": 0.40,    # 40% of total score
    "preferred_skills": 0.25,   # 25% of total score
    "keyword_density": 0.20,    # 20% of total score
    "format_compliance": 0.15   # 15% of total score
}


# ============================================================================
# SKILL ALIASES FOR MATCHING
# ============================================================================

SKILL_ALIASES = {
    # Machine Learning
    "machine learning": ["machine learning", "ml", "m.l.", "machinelearning"],
    "deep learning": ["deep learning", "dl", "d.l.", "deeplearning"],
    "neural network": ["neural network", "neural networks", "nn", "nns", "neuralnet"],
    "natural language processing": ["natural language processing", "nlp", "n.l.p."],
    "computer vision": ["computer vision", "cv", "image processing", "vision"],
    "reinforcement learning": ["reinforcement learning", "rl", "r.l."],
    
    # Frameworks
    "pytorch": ["pytorch", "torch", "py torch"],
    "tensorflow": ["tensorflow", "tf", "tensor flow"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn", "sk-learn"],
    "keras": ["keras"],
    "huggingface": ["huggingface", "hugging face", "hf", "transformers"],
    
    # Cloud
    "amazon web services": ["amazon web services", "aws", "a.w.s."],
    "google cloud": ["google cloud", "gcp", "google cloud platform", "g.c.p."],
    "microsoft azure": ["microsoft azure", "azure", "ms azure"],
    "kubernetes": ["kubernetes", "k8s", "kube"],
    "docker": ["docker", "containerization", "containers"],
    
    # Data
    "apache spark": ["apache spark", "spark", "pyspark"],
    "apache kafka": ["apache kafka", "kafka"],
    "hadoop": ["hadoop", "hdfs", "mapreduce"],
    "sql": ["sql", "structured query language", "mysql", "postgresql", "postgres"],
    "nosql": ["nosql", "mongodb", "dynamodb", "cassandra", "redis"],
    
    # Programming
    "python": ["python", "py", "python3", "python 3"],
    "javascript": ["javascript", "js", "node.js", "nodejs"],
    "typescript": ["typescript", "ts"],
    "java": ["java", "jvm"],
    "c++": ["c++", "cpp", "c plus plus"],
    "r": ["r", "r language", "rstudio"],
    
    # Methods
    "a/b testing": ["a/b testing", "ab testing", "a-b testing", "split testing", "experimentation"],
    "statistical analysis": ["statistical analysis", "statistics", "statistical modeling"],
    "data analysis": ["data analysis", "data analytics", "analytics"],
    "etl": ["etl", "extract transform load", "data pipeline", "data pipelines"],
    
    # Soft Skills
    "leadership": ["leadership", "lead", "leading", "led"],
    "communication": ["communication", "communicate", "communicating"],
    "collaboration": ["collaboration", "collaborate", "collaborating", "team"],
}


# ============================================================================
# FORMAT CHECK RULES
# ============================================================================

FORMAT_CHECKS = {
    "section_headers": {
        "description": "Has clear section headers",
        "severity": "high",
        "points_deduction": 5
    },
    "action_verbs": {
        "description": "Bullets start with action verbs",
        "severity": "high",
        "points_deduction": 5
    },
    "no_pronouns": {
        "description": "No personal pronouns (I, me, my)",
        "severity": "medium",
        "points_deduction": 3
    },
    "contact_info": {
        "description": "Contact information complete",
        "severity": "high",
        "points_deduction": 5
    },
    "bullet_length": {
        "description": "Bullets under 150 characters",
        "severity": "low",
        "points_deduction": 2
    },
    "consistent_dates": {
        "description": "Dates in consistent format",
        "severity": "medium",
        "points_deduction": 3
    },
    "no_keyword_stuffing": {
        "description": "No excessive keyword repetition",
        "severity": "medium",
        "points_deduction": 5
    }
}


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "ATSOptimizerState",
    "KEYWORD_WEIGHTS",
    "SECTION_WEIGHTS",
    "SCORE_WEIGHTS",
    "SKILL_ALIASES",
    "FORMAT_CHECKS"
]
