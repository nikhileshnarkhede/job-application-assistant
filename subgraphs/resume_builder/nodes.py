"""
Resume Builder Nodes

This module contains all node definitions for the Resume Builder subgraph:
1. load_candidate_data - Load header, education, certs, publications
2. tailor_summary - Generate JD-tailored professional summary
3. optimize_skills - Reorder skills by JD relevance
4. format_experiences - Structure rewritten experiences for resume
5. format_projects - Structure rewritten projects for resume
6. assemble_resume - Combine all into ResumeJSON

Node Flow:
    START → load_candidate_data → tailor_summary → optimize_skills → format_experiences → format_projects → assemble_resume → END
"""

import os
import re
from typing import Dict, Any, List, Set
from pathlib import Path
from datetime import datetime

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Optional Anthropic import
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# State imports
from subgraphs.resume_builder.state import (
    ResumeBuilderState,
    BULLET_LIMITS,
    DEFAULT_BULLET_LIMIT,
    PROJECT_BULLET_LIMIT,
    SKILLS_PER_CATEGORY_LIMIT,
    SKILL_CATEGORY_PRIORITY
)
from state.state_models import ResumeJSON


# ============================================================================
# CONFIGURATION
# ============================================================================

def get_llm():
    """Get configured LLM instance."""
    if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            temperature=0.4,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    else:
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.4,
            api_key=os.getenv("OPENAI_API_KEY")
        )


def load_prompt(filename: str) -> str:
    """Load prompt from file."""
    prompt_dir = Path(__file__).parent / "prompts"
    prompt_path = prompt_dir / filename
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


# ============================================================================
# NODE 1: LOAD CANDIDATE DATA
# ============================================================================

def load_candidate_data(state: ResumeBuilderState) -> Dict[str, Any]:
    """
    Load candidate base data from candidate_loader.
    
    Returns:
        Updated state with header, education, certifications, publications, skills
    """
    try:
        from mcp_server.tools.candidate_loader import (
            get_header,
            get_education,
            get_certifications_formatted,
            get_publications_formatted,
            get_skills_for_resume_lists,
            get_professional_summary
        )
        
        # Load all candidate data
        header = get_header()
        education = get_education()
        certifications = get_certifications_formatted()
        publications = get_publications_formatted()
        skills = get_skills_for_resume_lists()  # Returns Dict[str, List[str]]
        
        # Get base summary (use role_type from JD if available)
        role_type = "default"
        if state.structured_jd:
            role_type = state.structured_jd.role_type or "default"
        base_summary = get_professional_summary(role_type)
        
        print(f"  📂 Loaded candidate data:")
        print(f"     Header: {header.get('name', 'N/A')}")
        print(f"     Education: {len(education)} entries")
        print(f"     Certifications: {len(certifications)}")
        print(f"     Publications: {len(publications)}")
        print(f"     Skill categories: {len(skills)}")
        
        return {
            "candidate_header": header,
            "candidate_education": education,
            "candidate_certifications": certifications,
            "candidate_publications": publications,
            "candidate_skills": skills,
            "base_summary": base_summary
        }
        
    except Exception as e:
        print(f"  ⚠️ Error loading candidate data: {e}")
        return {
            "error_message": f"Failed to load candidate data: {str(e)}"
        }


# ============================================================================
# NODE 2: TAILOR SUMMARY
# ============================================================================

def extract_metrics_from_bullets(experiences: List) -> List[str]:
    """Extract metrics from experience bullets for summary."""
    metrics = []
    metric_pattern = r'(\d+[%xX]|\d+\.\d+%?|\$[\d,]+[KMB]?|\d+[KMB]\+?|\d+-\d+%)'
    
    for exp in experiences[:2]:  # Focus on top 2 experiences
        bullets = exp.rewritten_bullets if exp.rewritten_bullets else exp.original_bullets
        for bullet in bullets[:3]:
            matches = re.findall(metric_pattern, bullet)
            if matches:
                # Get the bullet with its metric context
                metrics.append(bullet)
                if len(metrics) >= 3:
                    break
        if len(metrics) >= 3:
            break
    
    return metrics[:3]


def tailor_summary(state: ResumeBuilderState) -> Dict[str, Any]:
    """
    Generate JD-tailored professional summary using LLM.
    
    Returns:
        Updated state with tailored_summary
    """
    jd = state.structured_jd
    experiences = state.rewritten_experiences
    skill_match = state.skill_match_result
    base_summary = state.base_summary
    
    if not jd:
        # Use base summary if no JD
        return {"tailored_summary": base_summary or "Experienced professional seeking new opportunities."}
    
    # Get matched skills
    matched_skills = []
    if skill_match:
        matched_skills = skill_match.matched_skills[:10]
    else:
        matched_skills = jd.skills_required[:10]
    
    # Get recent role info
    recent_role = "Professional"
    if experiences:
        recent_role = f"{experiences[0].role} at {experiences[0].company}"
    
    # Calculate years of experience (estimate from experiences)
    years_exp = "5+"
    if experiences:
        # Simple heuristic based on number of experiences
        years_exp = f"{len(experiences) + 2}+"
    
    # Extract top achievements with metrics
    top_achievements = extract_metrics_from_bullets(experiences)
    achievements_text = "\n".join([f"- {a}" for a in top_achievements]) if top_achievements else "- Strong technical background with proven results"
    
    # Load prompts
    system_prompt = load_prompt("summary_system_prompt.txt")
    generation_prompt = load_prompt("summary_generation_prompt.txt")
    
    # Format the prompt
    user_prompt = generation_prompt.format(
        company_name=jd.company_name or "Target Company",
        role_title=jd.role_title or "Target Role",
        role_type=jd.role_type or "ml_ai",
        matched_skills=", ".join(matched_skills),
        recent_role=recent_role,
        years_experience=years_exp,
        top_achievements=achievements_text,
        base_summary=base_summary or "Experienced professional in technology sector."
    )
    
    try:
        llm = get_llm()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        tailored_summary = response.content.strip()
        
        # Clean up - remove quotes if present
        tailored_summary = tailored_summary.strip('"\'')
        
        print(f"  ✍️ Generated tailored summary ({len(tailored_summary.split())} words)")
        
        return {"tailored_summary": tailored_summary}
        
    except Exception as e:
        print(f"  ⚠️ Summary generation failed: {e}, using base summary")
        return {"tailored_summary": base_summary or "Experienced professional seeking new opportunities."}


# ============================================================================
# NODE 3: OPTIMIZE SKILLS
# ============================================================================

def optimize_skills(state: ResumeBuilderState) -> Dict[str, Any]:
    """
    Reorder skills by JD relevance within each category.
    
    Returns:
        Updated state with optimized_skills
    """
    candidate_skills = state.candidate_skills
    jd = state.structured_jd
    skill_match = state.skill_match_result
    
    if not candidate_skills:
        return {"optimized_skills": {}}
    
    # Get JD skills for prioritization
    jd_skills_lower = set()
    if jd:
        for skill in (jd.skills_required or []):
            jd_skills_lower.add(skill.lower())
        for skill in (jd.skills_preferred or []):
            jd_skills_lower.add(skill.lower())
    
    if skill_match:
        for skill in skill_match.matched_skills:
            jd_skills_lower.add(skill.lower())
    
    optimized = {}
    
    # Process each category
    for category, skills in candidate_skills.items():
        if not skills:
            continue
        
        # Sort skills: matched first, then others
        matched = []
        others = []
        
        for skill in skills:
            if skill.lower() in jd_skills_lower:
                matched.append(skill)
            else:
                others.append(skill)
        
        # Combine: matched first, then others (up to limit)
        ordered_skills = matched + others
        ordered_skills = ordered_skills[:SKILLS_PER_CATEGORY_LIMIT]
        
        # Format as comma-separated string
        optimized[category] = ", ".join(ordered_skills)
    
    # Sort categories by priority
    sorted_optimized = {}
    for priority_cat in SKILL_CATEGORY_PRIORITY:
        for cat in optimized:
            if priority_cat.lower() in cat.lower() or cat.lower() in priority_cat.lower():
                sorted_optimized[cat] = optimized[cat]
                break
    
    # Add any remaining categories
    for cat, skills in optimized.items():
        if cat not in sorted_optimized:
            sorted_optimized[cat] = skills
    
    print(f"  🔧 Optimized {len(sorted_optimized)} skill categories")
    
    return {"optimized_skills": sorted_optimized}


# ============================================================================
# NODE 4: FORMAT EXPERIENCES
# ============================================================================

def format_experiences(state: ResumeBuilderState) -> Dict[str, Any]:
    """
    Format rewritten experiences for resume structure.
    
    Returns:
        Updated state with formatted_experiences
    """
    experiences = state.rewritten_experiences
    
    if not experiences:
        return {"formatted_experiences": []}
    
    formatted = []
    
    for idx, exp in enumerate(experiences):
        position = idx + 1  # 1-indexed position
        bullet_limit = BULLET_LIMITS.get(position, DEFAULT_BULLET_LIMIT)
        
        # Use rewritten bullets if available, otherwise original
        bullets = exp.rewritten_bullets if exp.rewritten_bullets else exp.original_bullets
        bullets = bullets[:bullet_limit]
        
        # Format dates
        dates_str = ""
        if exp.dates:
            start = exp.dates.get("start", "")
            end = exp.dates.get("end", "Present")
            if start:
                dates_str = f"{start} - {end}"
        
        # Format location
        location_str = ""
        if exp.location:
            if isinstance(exp.location, dict):
                city = exp.location.get("city", "")
                state_abbr = exp.location.get("state", "")
                country = exp.location.get("country", "")
                loc_type = exp.location.get("type", "")
                
                if city and state_abbr:
                    location_str = f"{city}, {state_abbr}"
                elif city:
                    location_str = city
                
                if loc_type and loc_type.lower() == "remote":
                    location_str = f"{location_str} (Remote)" if location_str else "Remote"
            elif isinstance(exp.location, str):
                location_str = exp.location
        
        formatted_exp = {
            "role": exp.role,
            "role_full": exp.role_full or exp.role,
            "company": exp.company,
            "location": location_str,
            "dates": dates_str,
            "employment_type": exp.employment_type or "",
            "bullets": bullets
        }
        
        # Add publication if present
        if exp.publication:
            formatted_exp["publication"] = exp.publication
        
        formatted.append(formatted_exp)
    
    print(f"  📋 Formatted {len(formatted)} experiences")
    
    return {"formatted_experiences": formatted}


# ============================================================================
# NODE 5: FORMAT PROJECTS
# ============================================================================

def format_projects(state: ResumeBuilderState) -> Dict[str, Any]:
    """
    Format rewritten projects for resume structure.
    
    Returns:
        Updated state with formatted_projects
    """
    projects = state.rewritten_projects
    
    if not projects:
        return {"formatted_projects": []}
    
    formatted = []
    
    for proj in projects:
        # Use rewritten bullets if available
        bullets = proj.rewritten_bullets if proj.rewritten_bullets else proj.bullets
        if not bullets and proj.original_bullets:
            bullets = proj.original_bullets
        bullets = bullets[:PROJECT_BULLET_LIMIT]
        
        # Format tech stack
        tech_list = []
        for category, techs in proj.tech_stack.items():
            if isinstance(techs, list):
                tech_list.extend(techs[:3])
        technologies = ", ".join(tech_list[:8])
        
        formatted_proj = {
            "name": proj.name,
            "technologies": technologies,
            "url": proj.github_url or "",
            "description": proj.description[:150] if proj.description else "",
            "bullets": bullets
        }
        
        formatted.append(formatted_proj)
    
    print(f"  📁 Formatted {len(formatted)} projects")
    
    return {"formatted_projects": formatted}


# ============================================================================
# NODE 6: ASSEMBLE RESUME
# ============================================================================

def assemble_resume(state: ResumeBuilderState) -> Dict[str, Any]:
    """
    Assemble all components into final ResumeJSON.
    
    Returns:
        Updated state with resume_json
    """
    jd = state.structured_jd
    
    # Format education
    formatted_education = []
    for edu in state.candidate_education:
        formatted_edu = {
            "institution": edu.get("institution", ""),
            "degree": f"{edu.get('degree', '')} in {edu.get('field', '')}".strip(" in "),
            "location": edu.get("location", ""),
            "graduation": edu.get("graduation", ""),
            "gpa": edu.get("gpa", ""),
            "highlights": edu.get("highlights", [])
        }
        formatted_education.append(formatted_edu)
    
    # Build tailored_for string
    tailored_for = ""
    if jd:
        tailored_for = f"{jd.company_name} - {jd.role_title}".strip(" - ")
    
    # Assemble the resume
    resume = ResumeJSON(
        header=state.candidate_header,
        summary=state.tailored_summary,
        education=formatted_education,
        certifications=state.candidate_certifications,
        experience=state.formatted_experiences,
        projects=state.formatted_projects,
        skills=state.optimized_skills,
        publications=state.candidate_publications,
        version=1,
        last_modified=datetime.now().isoformat(),
        tailored_for=tailored_for
    )
    
    # Validation
    sections_filled = 0
    if resume.header: sections_filled += 1
    if resume.summary: sections_filled += 1
    if resume.education: sections_filled += 1
    if resume.experience: sections_filled += 1
    if resume.skills: sections_filled += 1
    
    print(f"  ✅ Assembled resume: {sections_filled}/5 core sections filled")
    print(f"     Tailored for: {tailored_for or 'General'}")
    
    return {
        "resume_json": resume,
        "build_complete": True
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Nodes
    "load_candidate_data",
    "tailor_summary",
    "optimize_skills",
    "format_experiences",
    "format_projects",
    "assemble_resume",
    
    # Utilities
    "get_llm",
    "load_prompt",
    "extract_metrics_from_bullets"
]
