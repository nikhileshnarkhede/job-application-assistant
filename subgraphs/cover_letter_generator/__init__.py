"""
Cover Letter Generator Subgraph

Generates personalized cover letters with:
1. Company research via DuckDuckGo (no API key required)
2. JD-aligned content matching required skills
3. Professional formatting following best practices
4. Compliance with cover letter guidelines

Usage:
    from subgraphs.cover_letter_generator import generate_cover_letter_for_job, get_cover_letter_summary
    
    result = generate_cover_letter_for_job(
        structured_jd=structured_jd,
        resume_json=resume_json,
        tone="professional",
        referral_name="John Smith"  # optional
    )
    
    cover_letter = result["cover_letter"]
    print(cover_letter.full_text)
    
    # Get summary
    summary = get_cover_letter_summary(cover_letter, result["company_research"])
    print(summary)
"""

from subgraphs.cover_letter_generator.graph import (
    build_cover_letter_generator_graph,
    create_cover_letter_generator_subgraph,
    generate_cover_letter_for_job,
    get_cover_letter_text,
    get_cover_letter_summary,
    quick_cover_letter
)

from subgraphs.cover_letter_generator.state import (
    CoverLetterGeneratorState,
    CompanyResearch,
    CoverLetterSection,
    CoverLetter,
    COVER_LETTER_GUIDELINES
)

from subgraphs.cover_letter_generator.nodes import (
    research_company,
    extract_candidate_highlights,
    generate_cover_letter,
    format_output,
    get_search_tool
)

__all__ = [
    # Main functions
    "generate_cover_letter_for_job",
    "get_cover_letter_text",
    "get_cover_letter_summary",
    "quick_cover_letter",
    
    # Graph builders
    "build_cover_letter_generator_graph",
    "create_cover_letter_generator_subgraph",
    
    # State & Models
    "CoverLetterGeneratorState",
    "CompanyResearch",
    "CoverLetterSection",
    "CoverLetter",
    "COVER_LETTER_GUIDELINES",
    
    # Nodes
    "research_company",
    "extract_candidate_highlights",
    "generate_cover_letter",
    "format_output",
    "get_search_tool"
]
