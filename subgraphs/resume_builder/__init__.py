"""
Resume Builder Subgraph

Assembles a complete, JD-tailored resume from all processed components.

Key Features:
- Loads candidate base data (header, education, certifications, publications)
- Generates JD-tailored professional summary with metrics
- Optimizes skill ordering by JD relevance
- Formats experiences and projects with proper bullet limits
- Outputs complete ResumeJSON ready for document generation

Usage:
    from subgraphs.resume_builder import build_resume, resume_to_dict
    
    result = build_resume(
        structured_jd=structured_jd,
        rewritten_experiences=rewritten_experiences,
        rewritten_projects=rewritten_projects,
        skill_match_result=skill_match_result
    )
    
    resume = result["resume_json"]
    print(f"Summary: {resume.summary}")
    print(f"Tailored for: {resume.tailored_for}")
    
    # Convert to dict for serialization
    resume_dict = resume_to_dict(resume)
"""

from subgraphs.resume_builder.graph import (
    build_resume_builder_graph,
    create_resume_builder_subgraph,
    build_resume,
    build_general_resume,
    resume_to_dict
)

from subgraphs.resume_builder.state import (
    ResumeBuilderState,
    BULLET_LIMITS,
    PROJECT_BULLET_LIMIT,
    SKILLS_PER_CATEGORY_LIMIT,
    SECTION_ORDER,
    SKILL_CATEGORY_PRIORITY
)

from subgraphs.resume_builder.nodes import (
    load_candidate_data,
    tailor_summary,
    optimize_skills,
    format_experiences,
    format_projects,
    assemble_resume
)

__all__ = [
    # Main functions
    "build_resume",
    "build_general_resume",
    "resume_to_dict",
    
    # Graph builders
    "build_resume_builder_graph",
    "create_resume_builder_subgraph",
    
    # State & Config
    "ResumeBuilderState",
    "BULLET_LIMITS",
    "PROJECT_BULLET_LIMIT",
    "SKILLS_PER_CATEGORY_LIMIT",
    "SECTION_ORDER",
    "SKILL_CATEGORY_PRIORITY",
    
    # Nodes (for custom graph building)
    "load_candidate_data",
    "tailor_summary",
    "optimize_skills",
    "format_experiences",
    "format_projects",
    "assemble_resume"
]
