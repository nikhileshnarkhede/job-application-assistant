"""
Pipeline Configuration

All configurable parameters for the parent graph pipeline.
"""

# ============================================================================
# RESUME CONFIGURATION
# ============================================================================

RESUME_CONFIG = {
    # Content limits
    "max_experiences": 4,
    "bullets_per_experience": 4,
    "max_projects": 3,
    "bullets_per_project": 2,
    
    # Word counts
    "summary_min_words": 40,
    "summary_max_words": 60,
    "target_total_words": 500,
    "max_total_words": 600,
}

# ============================================================================
# COVER LETTER CONFIGURATION
# ============================================================================

COVER_LETTER_CONFIG = {
    "target_words": 300,
    "max_words": 400,
    "min_words": 250,
    "body_paragraphs": 2,
    "tone": "professional",  # professional, enthusiastic, conversational
}

# ============================================================================
# ATS CONFIGURATION
# ============================================================================

ATS_CONFIG = {
    "target_score": 95,
    "min_acceptable_score": 85,
    "max_iterations": 3,
    "keyword_match_threshold": 70,
}

# ============================================================================
# PIPELINE CONFIGURATION
# ============================================================================

PIPELINE_CONFIG = {
    # Iteration limits
    "max_ats_iterations": 3,
    "max_compliance_iterations": 3,
    "max_cover_letter_iterations": 2,
    
    # Pass thresholds
    "ats_pass_threshold": 95,
    "compliance_pass_threshold": 85,
    "cover_letter_pass_threshold": 80,
    
    # Feature toggles
    "enable_company_research": True,
    "enable_email_generation": True,
    "save_to_excel": True,
    "save_intermediate_outputs": False,
}

# ============================================================================
# PATHS CONFIGURATION
# ============================================================================

PATHS_CONFIG = {
    "output_folder": "applications",
    "excel_file": "job_applications.xlsx",
    "checkpoints_folder": "data/checkpoints",
    "checkpoint_db": "data/checkpoints/pipeline.db",
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_config_summary():
    """Print a summary of current configuration."""
    print("\n" + "=" * 60)
    print("PIPELINE CONFIGURATION")
    print("=" * 60)
    
    print("\n📄 Resume:")
    print(f"   Max Experiences: {RESUME_CONFIG['max_experiences']}")
    print(f"   Max Projects: {RESUME_CONFIG['max_projects']}")
    print(f"   Target Words: {RESUME_CONFIG['target_total_words']}")
    
    print("\n📝 Cover Letter:")
    print(f"   Target Words: {COVER_LETTER_CONFIG['target_words']}")
    print(f"   Tone: {COVER_LETTER_CONFIG['tone']}")
    
    print("\n🎯 ATS:")
    print(f"   Target Score: {ATS_CONFIG['target_score']}%")
    print(f"   Max Iterations: {ATS_CONFIG['max_iterations']}")
    
    print("\n⚙️  Pipeline:")
    print(f"   Compliance Threshold: {PIPELINE_CONFIG['compliance_pass_threshold']}%")
    print(f"   Save to Excel: {PIPELINE_CONFIG['save_to_excel']}")
    
    print("\n📁 Paths:")
    print(f"   Output: {PATHS_CONFIG['output_folder']}")
    print(f"   Excel: {PATHS_CONFIG['excel_file']}")
    
    print("=" * 60 + "\n")
