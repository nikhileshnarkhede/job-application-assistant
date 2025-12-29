"""
Cover Letter Generator Nodes

Generates personalized cover letters with company research.

Nodes:
1. research_company - Search for company info using DuckDuckGo
2. extract_candidate_highlights - Extract key achievements from resume
3. generate_cover_letter - Generate personalized cover letter
4. format_output - Format final cover letter
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# DuckDuckGo Search - No API key required
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False
    print("⚠️ DuckDuckGo not available. Install with: pip install duckduckgo-search")

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from subgraphs.cover_letter_generator.state import (
    CoverLetterGeneratorState,
    CompanyResearch,
    CoverLetter,
    COVER_LETTER_GUIDELINES
)

# Load candidate profile
try:
    from data.candidate_profile import candidate_profile
except ImportError:
    candidate_profile = None


# ============================================================================
# CONFIGURATION
# ============================================================================

def get_llm():
    """Get configured LLM instance."""
    if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            temperature=0.7,  # Slightly higher for creative writing
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    else:
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )


def load_prompt(filename: str) -> str:
    """Load prompt from file."""
    prompt_dir = Path(__file__).parent / "prompts"
    prompt_path = prompt_dir / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def get_search_tool():
    """Get DuckDuckGo search tool."""
    if DUCKDUCKGO_AVAILABLE:
        return DuckDuckGoSearchRun()
    return None


# ============================================================================
# NODE 1: RESEARCH COMPANY
# ============================================================================

def research_company(state: CoverLetterGeneratorState) -> Dict[str, Any]:
    """
    Research company using DuckDuckGo search.
    Gathers info about mission, values, culture, recent news.
    """
    jd = state.structured_jd
    
    if not jd:
        return {"error_message": "No structured JD provided"}
    
    company_name = jd.company_name
    
    if not company_name:
        return {"error_message": "Company name not found in JD"}
    
    print(f"  🔍 Researching company: {company_name}")
    
    search_tool = get_search_tool()
    
    if not search_tool:
        print("  ⚠️ Search not available, using JD info only")
        # Create basic research from JD
        research = CompanyResearch(
            company_name=company_name,
            research_summary=f"Company research based on job description for {jd.role_title} role."
        )
        return {"company_research": research}
    
    # Define search queries
    search_queries = [
        f"{company_name} company mission values culture",
        f"{company_name} recent news announcements 2024",
        f"{company_name} employee reviews work culture",
        f"{company_name} {jd.role_title} team technology stack",
    ]
    
    search_results = []
    
    # Execute searches with rate limiting
    import time
    for query in search_queries:
        try:
            print(f"    Searching: {query[:50]}...")
            result = search_tool.invoke(query)
            search_results.append({
                "query": query,
                "result": result
            })
            time.sleep(1)  # Rate limit
        except Exception as e:
            print(f"    ⚠️ Search failed: {e}")
            search_results.append({
                "query": query,
                "result": f"Search failed: {str(e)}"
            })
    
    # Parse search results into structured research
    research = parse_search_results(company_name, search_results, jd)
    
    print(f"  ✅ Research complete: {len(research.recent_news)} news items, {len(research.core_values)} values found")
    
    return {
        "company_research": research,
        "search_queries": search_queries,
        "search_results": search_results
    }


def parse_search_results(company_name: str, search_results: List[Dict], jd) -> CompanyResearch:
    """Parse search results into structured CompanyResearch."""
    
    all_text = " ".join([r.get("result", "") for r in search_results])
    
    research = CompanyResearch(
        company_name=company_name,
        industry=extract_industry(all_text, jd),
        sources=[r.get("query", "") for r in search_results]
    )
    
    # Extract mission/values
    mission_keywords = ["mission", "purpose", "vision", "believe", "committed"]
    for keyword in mission_keywords:
        if keyword in all_text.lower():
            # Find sentences containing the keyword
            sentences = all_text.split(".")
            for sentence in sentences:
                if keyword in sentence.lower() and len(sentence) > 30:
                    research.mission_statement = sentence.strip()[:300]
                    break
    
    # Extract values
    value_keywords = ["innovation", "customer", "integrity", "excellence", 
                      "collaboration", "diversity", "sustainability", "trust"]
    for value in value_keywords:
        if value in all_text.lower():
            research.core_values.append(value.title())
    
    # Extract recent news
    news_indicators = ["announced", "launched", "released", "raised", "acquired", "partnered"]
    sentences = all_text.split(".")
    for sentence in sentences:
        if any(ind in sentence.lower() for ind in news_indicators):
            if len(sentence) > 30 and len(research.recent_news) < 5:
                research.recent_news.append(sentence.strip()[:200])
    
    # Extract tech stack from JD
    if jd:
        research.tech_stack = list(jd.skills_required or [])[:10]
    
    # Create summary
    research.research_summary = f"""
{company_name} is a company in the {research.industry} industry.
Mission: {research.mission_statement[:100] if research.mission_statement else 'Not found'}
Values: {', '.join(research.core_values[:5]) if research.core_values else 'Not found'}
Recent: {research.recent_news[0][:100] if research.recent_news else 'No recent news found'}
    """.strip()
    
    return research


def extract_industry(text: str, jd) -> str:
    """Extract industry from text or JD."""
    industries = {
        "technology": ["software", "tech", "digital", "saas", "cloud"],
        "e-commerce": ["ecommerce", "retail", "marketplace", "shopping"],
        "finance": ["fintech", "banking", "financial", "investment"],
        "healthcare": ["health", "medical", "biotech", "pharma"],
        "ai/ml": ["artificial intelligence", "machine learning", "ai", "ml"],
        "gaming": ["gaming", "games", "entertainment"],
        "consulting": ["consulting", "advisory", "strategy"]
    }
    
    text_lower = text.lower()
    for industry, keywords in industries.items():
        if any(kw in text_lower for kw in keywords):
            return industry
    
    return "technology"  # Default


# ============================================================================
# NODE 2: EXTRACT CANDIDATE HIGHLIGHTS
# ============================================================================

def extract_candidate_highlights(state: CoverLetterGeneratorState) -> Dict[str, Any]:
    """
    Extract key achievements and highlights from resume.
    """
    resume = state.resume_json
    jd = state.structured_jd
    
    if not resume:
        return {"error_message": "No resume JSON provided"}
    
    print(f"  📋 Extracting candidate highlights...")
    
    highlights = {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "summary": "",
        "top_skills": [],
        "top_achievements": [],
        "relevant_experience": []
    }
    
    # Header info
    header = resume.header or {}
    highlights["name"] = header.get("name", "")
    highlights["email"] = header.get("email", "")
    highlights["phone"] = header.get("phone", "")
    highlights["location"] = header.get("location", "")
    
    # Summary
    highlights["summary"] = resume.summary or ""
    
    # Skills - prioritize required skills from JD
    all_skills = []
    for category, skills in (resume.skills or {}).items():
        all_skills.extend(skills.split(", "))
    
    # Match with JD requirements
    required = set(s.lower() for s in (jd.skills_required or []))
    matched_skills = [s for s in all_skills if s.lower() in required]
    other_skills = [s for s in all_skills if s.lower() not in required]
    
    highlights["top_skills"] = (matched_skills + other_skills)[:10]
    
    # Achievements - extract from experience bullets
    achievements = []
    for exp in (resume.experience or [])[:3]:
        for bullet in exp.get("bullets", [])[:3]:
            # Prioritize bullets with numbers/metrics
            if any(c.isdigit() for c in bullet) or "%" in bullet or "$" in bullet:
                achievements.append({
                    "company": exp.get("company", ""),
                    "role": exp.get("role", ""),
                    "achievement": bullet
                })
    
    highlights["top_achievements"] = achievements[:5]
    
    # Relevant experience summaries
    for exp in (resume.experience or [])[:2]:
        highlights["relevant_experience"].append({
            "company": exp.get("company", ""),
            "role": exp.get("role", ""),
            "dates": f"{exp.get('start_date', '')} - {exp.get('end_date', '')}"
        })
    
    print(f"  ✅ Extracted: {len(highlights['top_skills'])} skills, {len(highlights['top_achievements'])} achievements")
    
    return {"_candidate_highlights": highlights}


# ============================================================================
# NODE 3: GENERATE COVER LETTER
# ============================================================================

def generate_cover_letter(state: CoverLetterGeneratorState) -> Dict[str, Any]:
    """
    Generate personalized cover letter using LLM.
    """
    jd = state.structured_jd
    research = state.company_research
    highlights = getattr(state, '_candidate_highlights', {})
    
    if not jd:
        return {"error_message": "No structured JD provided"}
    
    print(f"  ✍️ Generating cover letter for {jd.company_name} - {jd.role_title}...")
    
    # Load prompts
    system_prompt = load_prompt("system_prompt.txt")
    generation_prompt = load_prompt("generation_prompt.txt")
    few_shot = load_prompt("few_shot_examples.txt")
    
    # Format candidate info
    candidate_experience = ""
    for exp in highlights.get("relevant_experience", []):
        candidate_experience += f"- {exp['role']} at {exp['company']} ({exp['dates']})\n"
    
    candidate_achievements = ""
    for ach in highlights.get("top_achievements", []):
        candidate_achievements += f"- {ach['achievement']}\n"
    
    # Format company research
    company_research_text = ""
    if research:
        company_research_text = f"""
**Company Overview:**
- Industry: {research.industry}
- Mission: {research.mission_statement or 'Not available'}
- Core Values: {', '.join(research.core_values[:5]) if research.core_values else 'Not available'}

**Recent News:**
{chr(10).join('- ' + news[:150] for news in research.recent_news[:3]) if research.recent_news else 'No recent news found'}

**Tech Stack:** {', '.join(research.tech_stack[:8]) if research.tech_stack else 'Not specified'}

**Research Summary:**
{research.research_summary}
        """.strip()
    else:
        company_research_text = "Company research not available. Focus on job description details."
    
    # Format the prompt
    user_prompt = generation_prompt.format(
        candidate_name=highlights.get("name", "Candidate"),
        candidate_email=highlights.get("email", "email@example.com"),
        candidate_phone=highlights.get("phone", "(555) 000-0000"),
        candidate_location=highlights.get("location", "Location"),
        candidate_summary=highlights.get("summary", "")[:300],
        candidate_skills=", ".join(highlights.get("top_skills", [])[:10]),
        candidate_experience=candidate_experience,
        candidate_achievements=candidate_achievements,
        company_name=jd.company_name,
        role_title=jd.role_title,
        job_location=jd.location or "Not specified",
        job_requirements=", ".join((jd.skills_required or [])[:8]),
        job_responsibilities="\n".join((jd.responsibilities or [])[:5]),
        required_skills=", ".join((jd.skills_required or [])[:8]),
        preferred_skills=", ".join((jd.skills_preferred or [])[:5]),
        company_research=company_research_text,
        tone=state.tone,
        focus_areas=", ".join(state.focus_areas) if state.focus_areas else "technical skills, company fit",
        referral_info=f"Referred by {state.referral_name}" if state.referral_name else "No referral",
        custom_hook=state.custom_hook or "None specified",
        date=datetime.now().strftime("%B %d, %Y")
    )
    
    try:
        llm = get_llm()
        messages = [
            SystemMessage(content=f"{system_prompt}\n\n{few_shot}"),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        cover_letter = parse_cover_letter_response(response.content, highlights, jd, research)
        
        print(f"  ✅ Cover letter generated: {cover_letter.word_count} words")
        
        return {"cover_letter": cover_letter}
        
    except Exception as e:
        print(f"  ❌ Generation failed: {e}")
        return {"error_message": str(e)}


def parse_cover_letter_response(response: str, highlights: Dict, jd, research) -> CoverLetter:
    """Parse LLM response into CoverLetter object."""
    
    cover_letter = CoverLetter(
        candidate_name=highlights.get("name", ""),
        candidate_email=highlights.get("email", ""),
        candidate_phone=highlights.get("phone", ""),
        candidate_location=highlights.get("location", ""),
        date=datetime.now().strftime("%B %d, %Y"),
        company_name=jd.company_name if jd else "",
        full_text=response
    )
    
    # Extract sections using markers
    sections = {
        "introduction": extract_section(response, "[INTRODUCTION]", "[BODY_1]"),
        "body_1": extract_section(response, "[BODY_1]", "[BODY_2]"),
        "body_2": extract_section(response, "[BODY_2]", "[CLOSING]"),
        "closing": extract_section(response, "[CLOSING]", "[SIGNOFF]")
    }
    
    cover_letter.introduction = sections["introduction"]
    cover_letter.body_paragraph_1 = sections["body_1"]
    cover_letter.body_paragraph_2 = sections["body_2"]
    cover_letter.closing = sections["closing"]
    
    # Clean up full text
    clean_text = response
    for marker in ["[HEADER]", "[SALUTATION]", "[INTRODUCTION]", "[BODY_1]", "[BODY_2]", "[CLOSING]", "[SIGNOFF]"]:
        clean_text = clean_text.replace(marker, "")
    clean_text = re.sub(r'```\n?', '', clean_text)
    clean_text = clean_text.strip()
    
    cover_letter.full_text = clean_text
    cover_letter.word_count = len(clean_text.split())
    cover_letter.paragraph_count = len([p for p in clean_text.split('\n\n') if p.strip()])
    
    # Count company mentions
    if jd:
        cover_letter.company_mentions = clean_text.lower().count(jd.company_name.lower())
    
    # Extract keywords used
    if jd:
        keywords = (jd.skills_required or []) + (jd.keywords or [])
        cover_letter.keywords_used = [kw for kw in keywords if kw.lower() in clean_text.lower()]
    
    # Calculate personalization score
    score = 0
    if cover_letter.company_mentions >= 2:
        score += 30
    if len(cover_letter.keywords_used) >= 3:
        score += 30
    if research and research.recent_news:
        for news in research.recent_news[:3]:
            if any(word in clean_text.lower() for word in news.lower().split()[:5]):
                score += 20
                break
    if cover_letter.word_count >= 250 and cover_letter.word_count <= 400:
        score += 20
    
    cover_letter.personalization_score = min(100, score)
    
    return cover_letter


def extract_section(text: str, start_marker: str, end_marker: str) -> str:
    """Extract section between markers."""
    try:
        start_idx = text.find(start_marker)
        end_idx = text.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            return text[start_idx + len(start_marker):end_idx].strip()
        elif start_idx != -1:
            return text[start_idx + len(start_marker):].strip()[:500]
    except:
        pass
    return ""


# ============================================================================
# NODE 4: FORMAT OUTPUT
# ============================================================================

def format_output(state: CoverLetterGeneratorState) -> Dict[str, Any]:
    """
    Format the final cover letter output.
    """
    cover_letter = state.cover_letter
    
    if not cover_letter:
        return {"error_message": "No cover letter generated"}
    
    print(f"  📄 Formatting final output...")
    
    # Create clean formatted version
    formatted = f"""
{cover_letter.candidate_name}
{cover_letter.candidate_email} | {cover_letter.candidate_phone}
{cover_letter.candidate_location}

{cover_letter.date}

{cover_letter.company_name}

Dear Hiring Manager,

{cover_letter.introduction}

{cover_letter.body_paragraph_1}

{cover_letter.body_paragraph_2}

{cover_letter.closing}

Sincerely,

{cover_letter.candidate_name}
    """.strip()
    
    # Update full text with clean version if sections were properly extracted
    if cover_letter.introduction and cover_letter.body_paragraph_1:
        cover_letter.full_text = formatted
    
    print(f"  ✅ Cover letter ready: {cover_letter.word_count} words, {cover_letter.personalization_score:.0f}% personalization")
    
    return {
        "cover_letter": cover_letter,
        "generation_complete": True
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "research_company",
    "extract_candidate_highlights",
    "generate_cover_letter",
    "format_output",
    "get_llm",
    "load_prompt",
    "get_search_tool"
]
