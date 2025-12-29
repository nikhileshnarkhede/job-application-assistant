"""
Cover Letter Generator Subgraph Builder

Generates personalized cover letters with company research.

Graph Flow:
```
    START
      │
      ▼
┌─────────────────────────┐
│   research_company      │  ← DuckDuckGo search for company info
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ extract_candidate_highlights │  ← Key achievements from resume
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  generate_cover_letter  │  ← LLM generates personalized letter
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│     format_output       │  ← Clean formatting
└───────────┬─────────────┘
            │
            ▼
          END
```
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

from subgraphs.cover_letter_generator.state import (
    CoverLetterGeneratorState,
    CoverLetter,
    CompanyResearch
)
from subgraphs.cover_letter_generator.nodes import (
    research_company,
    extract_candidate_highlights,
    generate_cover_letter,
    format_output
)


def build_cover_letter_generator_graph() -> StateGraph:
    """
    Build the Cover Letter Generator subgraph.
    
    Returns:
        Compiled StateGraph for cover letter generation
    """
    graph = StateGraph(CoverLetterGeneratorState)
    
    # Add nodes
    graph.add_node("research_company", research_company)
    graph.add_node("extract_candidate_highlights", extract_candidate_highlights)
    graph.add_node("generate_cover_letter", generate_cover_letter)
    graph.add_node("format_output", format_output)
    
    # Add edges
    graph.add_edge(START, "research_company")
    graph.add_edge("research_company", "extract_candidate_highlights")
    graph.add_edge("extract_candidate_highlights", "generate_cover_letter")
    graph.add_edge("generate_cover_letter", "format_output")
    graph.add_edge("format_output", END)
    
    return graph.compile()


def create_cover_letter_generator_subgraph():
    """Create and return the compiled Cover Letter Generator subgraph."""
    return build_cover_letter_generator_graph()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def generate_cover_letter_for_job(
    structured_jd,
    resume_json,
    tone: str = "professional",
    focus_areas: list = None,
    referral_name: str = None,
    custom_hook: str = None
) -> Dict[str, Any]:
    """
    Generate a personalized cover letter for a job.
    
    Args:
        structured_jd: StructuredJD object from JD Extractor
        resume_json: ResumeJSON object from Resume Builder
        tone: Writing tone (professional, enthusiastic, conversational)
        focus_areas: List of areas to emphasize (technical, leadership, culture)
        referral_name: Name of person who referred you (optional)
        custom_hook: Custom opening hook to use (optional)
    
    Returns:
        Dict with cover_letter, company_research, and generation status
    """
    graph = create_cover_letter_generator_subgraph()
    
    initial_state = {
        "structured_jd": structured_jd,
        "resume_json": resume_json,
        "tone": tone,
        "focus_areas": focus_areas or [],
        "referral_name": referral_name,
        "custom_hook": custom_hook
    }
    
    result = graph.invoke(initial_state)
    
    return {
        "cover_letter": result.get("cover_letter"),
        "company_research": result.get("company_research"),
        "search_results": result.get("search_results", []),
        "generation_complete": result.get("generation_complete", False),
        "error": result.get("error_message")
    }


def get_cover_letter_text(cover_letter: CoverLetter) -> str:
    """
    Get the full text of a cover letter.
    
    Args:
        cover_letter: CoverLetter object
    
    Returns:
        Full text string
    """
    if not cover_letter:
        return ""
    
    return cover_letter.full_text


def get_cover_letter_summary(cover_letter: CoverLetter, research: CompanyResearch = None) -> str:
    """
    Generate a summary of the cover letter generation.
    
    Args:
        cover_letter: CoverLetter object
        research: CompanyResearch object (optional)
    
    Returns:
        Formatted summary string
    """
    if not cover_letter:
        return "No cover letter generated."
    
    lines = [
        "=" * 60,
        "COVER LETTER SUMMARY",
        "=" * 60,
        "",
        f"📧 Candidate: {cover_letter.candidate_name}",
        f"🏢 Company: {cover_letter.company_name}",
        f"📅 Date: {cover_letter.date}",
        "",
        f"📊 Statistics:",
        f"   Word Count: {cover_letter.word_count}",
        f"   Paragraphs: {cover_letter.paragraph_count}",
        f"   Company Mentions: {cover_letter.company_mentions}",
        f"   Keywords Used: {len(cover_letter.keywords_used)}",
        f"   Personalization Score: {cover_letter.personalization_score:.0f}%",
        "",
    ]
    
    if cover_letter.keywords_used:
        lines.append(f"🔑 Keywords Incorporated:")
        lines.append(f"   {', '.join(cover_letter.keywords_used[:10])}")
        lines.append("")
    
    if research:
        lines.append(f"🔍 Company Research:")
        lines.append(f"   Industry: {research.industry}")
        if research.core_values:
            lines.append(f"   Values: {', '.join(research.core_values[:5])}")
        if research.recent_news:
            lines.append(f"   Recent News: {len(research.recent_news)} items found")
        lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


def quick_cover_letter(structured_jd, resume_json) -> str:
    """
    Quick cover letter generation with defaults.
    
    Args:
        structured_jd: StructuredJD object
        resume_json: ResumeJSON object
    
    Returns:
        Cover letter text string
    """
    result = generate_cover_letter_for_job(structured_jd, resume_json)
    
    if result.get("error"):
        return f"Error generating cover letter: {result['error']}"
    
    cover_letter = result.get("cover_letter")
    if cover_letter:
        return cover_letter.full_text
    
    return "Cover letter generation failed."


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "build_cover_letter_generator_graph",
    "create_cover_letter_generator_subgraph",
    "generate_cover_letter_for_job",
    "get_cover_letter_text",
    "get_cover_letter_summary",
    "quick_cover_letter"
]
