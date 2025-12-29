"""
Subgraphs for Job Application Assistant Pipeline

All 12 subgraphs for the complete job application workflow:

1. jd_extractor        - Extract structured info from job descriptions
2. skill_matcher       - Match candidate skills to JD requirements
3. github_ranker       - Rank GitHub projects by relevance
4. experience_selector - Select relevant experiences
5. experience_rewriter - Rewrite bullets with action verbs & metrics
6. resume_builder      - Assemble complete ResumeJSON
7. ats_optimizer       - Optimize for ATS score (95%+ target)
8. resource_compliance - Validate resume against checklists/rubrics
9. cover_letter_generator - Generate personalized cover letter
10. cover_letter_compliance - Validate cover letter against checklists/rubrics
11. email_generator    - Generate recruiter outreach emails
12. excel_writer       - Save application to tracking spreadsheet
"""

# ============================================================================
# 1. JD EXTRACTOR
# ============================================================================
from subgraphs.jd_extractor import (
    extract_jd_from_text,
    extract_jd_from_url,
    create_jd_extractor_subgraph,
    build_jd_extractor_graph,
    JDExtractorState
)

# ============================================================================
# 2. SKILL MATCHER
# ============================================================================
from subgraphs.skill_matcher import (
    match_skills_to_jd,
    quick_skill_match,
    create_skill_matcher_subgraph,
    build_skill_matcher_graph,
    SkillMatcherState
)

# ============================================================================
# 3. GITHUB RANKER
# ============================================================================
from subgraphs.github_ranker import (
    rank_github_projects,
    get_top_projects_for_jd,
    create_github_ranker_subgraph,
    build_github_ranker_graph,
    GitHubRankerState
)

# ============================================================================
# 4. EXPERIENCE SELECTOR
# ============================================================================
from subgraphs.experience_selector import (
    select_experiences_for_jd,
    quick_experience_selection,
    create_experience_selector_subgraph,
    build_experience_selector_graph,
    ExperienceSelectorState
)

# ============================================================================
# 5. EXPERIENCE REWRITER
# ============================================================================
from subgraphs.experience_rewriter import (
    rewrite_for_jd,
    quick_rewrite,
    create_experience_rewriter_subgraph,
    build_experience_rewriter_graph,
    ExperienceRewriterState
)

# ============================================================================
# 6. RESUME BUILDER
# ============================================================================
from subgraphs.resume_builder import (
    build_resume,
    build_general_resume,
    resume_to_dict,
    create_resume_builder_subgraph,
    build_resume_builder_graph,
    ResumeBuilderState
)

# ============================================================================
# 7. ATS OPTIMIZER
# ============================================================================
from subgraphs.ats_optimizer import (
    optimize_resume_for_ats,
    quick_ats_check,
    get_ats_report,
    create_ats_optimizer_subgraph,
    build_ats_optimizer_graph,
    ATSOptimizerState
)

# ============================================================================
# 8. RESOURCE COMPLIANCE
# ============================================================================
from subgraphs.resource_compliance import (
    validate_resume_compliance,
    get_compliance_summary,
    quick_compliance_check,
    create_resource_compliance_subgraph,
    build_resource_compliance_graph,
    ResourceComplianceState,
    RESUME_CHECKLIST,
    RESUME_RUBRIC
)

# ============================================================================
# 9. COVER LETTER GENERATOR
# ============================================================================
from subgraphs.cover_letter_generator import (
    generate_cover_letter_for_job,
    get_cover_letter_text,
    get_cover_letter_summary,
    quick_cover_letter,
    create_cover_letter_generator_subgraph,
    build_cover_letter_generator_graph,
    CoverLetterGeneratorState,
    CoverLetter,
    CompanyResearch
)

# ============================================================================
# 10. COVER LETTER COMPLIANCE
# ============================================================================
from subgraphs.cover_letter_compliance import (
    validate_cover_letter_compliance,
    get_cover_letter_compliance_summary,
    quick_cover_letter_compliance_check,
    create_cover_letter_compliance_subgraph,
    build_cover_letter_compliance_graph,
    CoverLetterComplianceState,
    CoverLetterComplianceReport,
    COVER_LETTER_CHECKLIST,
    COVER_LETTER_RUBRIC
)

# ============================================================================
# 11. EMAIL GENERATOR
# ============================================================================
from subgraphs.email_generator import (
    generate_outreach_email,
    generate_cold_outreach,
    generate_followup_email,
    generate_thank_you_email,
    get_email_text,
    get_email_summary,
    create_email_generator_subgraph,
    build_email_generator_graph,
    EmailGeneratorState,
    EmailType,
    EmailTone,
    EmailRecipient,
    GeneratedEmail
)

# ============================================================================
# 12. EXCEL WRITER
# ============================================================================
from subgraphs.excel_writer import (
    save_application_to_excel,
    quick_save_application,
    update_application_status,
    get_application_stats,
    get_applications_summary,
    create_excel_writer_subgraph,
    build_excel_writer_graph,
    ExcelWriterState,
    ApplicationStatus,
    ApplicationSource,
    ApplicationRecord
)

# ============================================================================
# SHARED TEST CONSTANTS
# ============================================================================
from subgraphs.test_constants import (
    STANDARD_JD_URL,
    STANDARD_JD_TEXT,
    get_standard_jd_url,
    get_standard_jd_text,
    get_structured_jd_for_testing
)


# ============================================================================
# ALL EXPORTS
# ============================================================================
__all__ = [
    # ----- 1. JD Extractor -----
    "extract_jd_from_text",
    "extract_jd_from_url",
    "create_jd_extractor_subgraph",
    "build_jd_extractor_graph",
    "JDExtractorState",
    
    # ----- 2. Skill Matcher -----
    "match_skills_to_jd",
    "quick_skill_match",
    "create_skill_matcher_subgraph",
    "build_skill_matcher_graph",
    "SkillMatcherState",
    
    # ----- 3. GitHub Ranker -----
    "rank_github_projects",
    "get_top_projects_for_jd",
    "create_github_ranker_subgraph",
    "build_github_ranker_graph",
    "GitHubRankerState",
    
    # ----- 4. Experience Selector -----
    "select_experiences_for_jd",
    "quick_experience_selection",
    "create_experience_selector_subgraph",
    "build_experience_selector_graph",
    "ExperienceSelectorState",
    
    # ----- 5. Experience Rewriter -----
    "rewrite_for_jd",
    "quick_rewrite",
    "create_experience_rewriter_subgraph",
    "build_experience_rewriter_graph",
    "ExperienceRewriterState",
    
    # ----- 6. Resume Builder -----
    "build_resume",
    "build_general_resume",
    "resume_to_dict",
    "create_resume_builder_subgraph",
    "build_resume_builder_graph",
    "ResumeBuilderState",
    
    # ----- 7. ATS Optimizer -----
    "optimize_resume_for_ats",
    "quick_ats_check",
    "get_ats_report",
    "create_ats_optimizer_subgraph",
    "build_ats_optimizer_graph",
    "ATSOptimizerState",
    
    # ----- 8. Resource Compliance -----
    "validate_resume_compliance",
    "get_compliance_summary",
    "quick_compliance_check",
    "create_resource_compliance_subgraph",
    "build_resource_compliance_graph",
    "ResourceComplianceState",
    "RESUME_CHECKLIST",
    "RESUME_RUBRIC",
    
    # ----- 9. Cover Letter Generator -----
    "generate_cover_letter_for_job",
    "get_cover_letter_text",
    "get_cover_letter_summary",
    "quick_cover_letter",
    "create_cover_letter_generator_subgraph",
    "build_cover_letter_generator_graph",
    "CoverLetterGeneratorState",
    "CoverLetter",
    "CompanyResearch",
    
    # ----- 10. Cover Letter Compliance -----
    "validate_cover_letter_compliance",
    "get_cover_letter_compliance_summary",
    "quick_cover_letter_compliance_check",
    "create_cover_letter_compliance_subgraph",
    "build_cover_letter_compliance_graph",
    "CoverLetterComplianceState",
    "CoverLetterComplianceReport",
    "COVER_LETTER_CHECKLIST",
    "COVER_LETTER_RUBRIC",
    
    # ----- 11. Email Generator -----
    "generate_outreach_email",
    "generate_cold_outreach",
    "generate_followup_email",
    "generate_thank_you_email",
    "get_email_text",
    "get_email_summary",
    "create_email_generator_subgraph",
    "build_email_generator_graph",
    "EmailGeneratorState",
    "EmailType",
    "EmailTone",
    "EmailRecipient",
    "GeneratedEmail",
    
    # ----- 12. Excel Writer -----
    "save_application_to_excel",
    "quick_save_application",
    "update_application_status",
    "get_application_stats",
    "get_applications_summary",
    "create_excel_writer_subgraph",
    "build_excel_writer_graph",
    "ExcelWriterState",
    "ApplicationStatus",
    "ApplicationSource",
    "ApplicationRecord",
    
    # ----- Test Constants -----
    "STANDARD_JD_URL",
    "STANDARD_JD_TEXT",
    "get_standard_jd_url",
    "get_standard_jd_text",
    "get_structured_jd_for_testing",
]
