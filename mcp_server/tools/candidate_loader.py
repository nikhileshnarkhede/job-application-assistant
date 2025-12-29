"""
Candidate Experience Loader

Loads and queries candidate experience data for resume tailoring.
Includes: Header, Education, Experience, Skills, Certifications, Publications
"""

import json
import os
from typing import List, Dict, Any, Optional


def get_data_path() -> str:
    """Get the base path for data files."""
    return os.getenv("DATA_PATH", "./data")


def load_candidate_data() -> Dict[str, Any]:
    """
    Load complete candidate data from JSON file.
    
    Returns:
        Complete candidate data dictionary
    """
    path = os.path.join(get_data_path(), "candidate_experience.json")
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Candidate data file not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Alias for backward compatibility
load_candidate_experience = load_candidate_data


# ============================================================================
# HEADER / CONTACT INFO
# ============================================================================

def get_header() -> Dict[str, str]:
    """
    Get candidate header/contact information.
    
    Returns:
        Dict with name, title, phone, email, location, linkedin, github
    """
    data = load_candidate_data()
    return data.get("header", {})


def get_name() -> str:
    """Get candidate's full name."""
    return get_header().get("name", "")


def get_contact_line() -> str:
    """Get formatted contact line for resume header."""
    return get_header().get("contact_line", "")


# ============================================================================
# PROFESSIONAL SUMMARY
# ============================================================================

def get_professional_summary(role_type: str = "default") -> str:
    """
    Get professional summary tailored to role type.
    
    Args:
        role_type: One of: default, ml_engineer, data_scientist, research_scientist
    
    Returns:
        Professional summary string
    """
    data = load_candidate_data()
    summaries = data.get("professional_summary", {})
    
    # Normalize role type
    role_key = role_type.lower().replace(" ", "_").replace("-", "_")
    
    # Try exact match first
    if role_key in summaries:
        return summaries[role_key]
    
    # Try partial match
    for key in summaries:
        if role_key in key or key in role_key:
            return summaries[key]
    
    # Default
    return summaries.get("default", "")


# ============================================================================
# EDUCATION
# ============================================================================

def get_education() -> List[Dict[str, Any]]:
    """
    Get all education entries.
    
    Returns:
        List of education dictionaries
    """
    data = load_candidate_data()
    return data.get("education", [])


def get_education_formatted() -> List[Dict[str, str]]:
    """
    Get education formatted for resume.
    
    Returns:
        List of formatted education entries
    """
    education = get_education()
    formatted = []
    
    for edu in education:
        entry = {
            "institution": edu.get("institution", ""),
            "location": edu.get("location", ""),
            "degree": f"{edu.get('degree', '')} in {edu.get('field', '')}",
            "graduation": edu.get("graduation", ""),
            "gpa": edu.get("gpa", ""),
            "coursework": ", ".join(edu.get("coursework", [])),
            "highlights": edu.get("highlights", [])
        }
        formatted.append(entry)
    
    return formatted


# ============================================================================
# CERTIFICATIONS
# ============================================================================

def get_certifications() -> List[Dict[str, Any]]:
    """Get all certifications."""
    data = load_candidate_data()
    return data.get("certifications", [])


def get_certifications_formatted() -> List[str]:
    """
    Get certifications formatted for resume.
    
    Returns:
        List of formatted certification strings
    """
    certifications = get_certifications()
    formatted = []
    
    for cert in certifications:
        name = cert.get("name", "")
        issuer = cert.get("issuer", "")
        year = cert.get("year", "")
        
        if year:
            formatted.append(f"{name} — {issuer} ({year})")
        else:
            formatted.append(f"{name} — {issuer}")
    
    return formatted


# ============================================================================
# EXPERIENCES
# ============================================================================

def get_all_experiences() -> List[Dict[str, Any]]:
    """Get all experience entries."""
    data = load_candidate_data()
    return data.get("experiences", [])


def get_experience_by_id(exp_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific experience by ID."""
    experiences = get_all_experiences()
    for exp in experiences:
        if exp.get("id") == exp_id:
            return exp
    return None


def get_experiences_by_relevance(role_type: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get experiences sorted by relevance for a given role type.
    
    Args:
        role_type: One of: ml_ai, data_science, research, robotics_automation,
                   technical_writing, software_engineering, simulation_engineering,
                   scientific_ai, llm_ai_agents
    
    Returns:
        Dict with 'primary', 'secondary', 'supporting' experience lists
    """
    data = load_candidate_data()
    relevance_mapping = data.get("relevance_mapping", {})
    experiences = data.get("experiences", [])
    
    # Normalize role type
    role_key = role_type.lower().replace(" ", "_").replace("-", "_")
    
    # Try to find matching role type
    if role_key not in relevance_mapping:
        # Try fuzzy matching
        for key in relevance_mapping:
            if role_key in key or key in role_key:
                role_key = key
                break
        else:
            # Default to ml_ai if no match
            role_key = "ml_ai"
    
    mapping = relevance_mapping.get(role_key, {"primary": [], "secondary": [], "supporting": []})
    
    result = {
        "primary": [],
        "secondary": [],
        "supporting": []
    }
    
    for exp in experiences:
        exp_id = exp.get("id")
        if exp_id in mapping.get("primary", []):
            result["primary"].append(exp)
        elif exp_id in mapping.get("secondary", []):
            result["secondary"].append(exp)
        elif exp_id in mapping.get("supporting", []):
            result["supporting"].append(exp)
    
    return result


def get_relevant_experiences_for_jd(jd_keywords: List[str], top_n: int = 4) -> List[Dict[str, Any]]:
    """
    Get most relevant experiences based on JD keywords.
    
    Args:
        jd_keywords: List of keywords/skills from job description
        top_n: Number of top experiences to return
    
    Returns:
        List of experiences sorted by relevance score
    """
    experiences = get_all_experiences()
    jd_keywords_lower = {kw.lower() for kw in jd_keywords}
    
    scored_experiences = []
    
    for exp in experiences:
        # Calculate relevance score
        exp_keywords = set()
        
        # Add skills
        for skill in exp.get("skills", []):
            exp_keywords.add(skill.lower())
        
        # Add keywords
        for kw in exp.get("keywords", []):
            exp_keywords.add(kw.lower())
        
        # Calculate overlap
        overlap = len(exp_keywords & jd_keywords_lower)
        
        # Bonus for recent experience
        recency_bonus = 0
        if exp.get("id") == 1:  # Most recent
            recency_bonus = 2
        elif exp.get("id") <= 3:
            recency_bonus = 1
        
        score = overlap + recency_bonus
        
        scored_experiences.append({
            "experience": exp,
            "score": score,
            "matching_keywords": list(exp_keywords & jd_keywords_lower)
        })
    
    # Sort by score descending
    scored_experiences.sort(key=lambda x: x["score"], reverse=True)
    
    return [item["experience"] for item in scored_experiences[:top_n]]


def get_all_bullets_for_experience(exp_id: int) -> List[str]:
    """Get all bullet points for a specific experience."""
    exp = get_experience_by_id(exp_id)
    if exp:
        return exp.get("bullets_flat", [])
    return []


def get_experience_for_resume(role_type: str, max_experiences: int = 4) -> List[Dict[str, Any]]:
    """
    Get experiences formatted for resume generation.
    
    Args:
        role_type: Type of role being applied for
        max_experiences: Maximum number of experiences to include
    
    Returns:
        List of experiences with selected bullets
    """
    relevance = get_experiences_by_relevance(role_type)
    
    selected = []
    
    # Add primary experiences first
    for exp in relevance["primary"]:
        if len(selected) < max_experiences:
            selected.append(exp)
    
    # Add secondary if room
    for exp in relevance["secondary"]:
        if len(selected) < max_experiences:
            selected.append(exp)
    
    # Add supporting if still room
    for exp in relevance["supporting"]:
        if len(selected) < max_experiences:
            selected.append(exp)
    
    # If still not enough, add remaining by ID order
    if len(selected) < max_experiences:
        all_exp = get_all_experiences()
        selected_ids = {e["id"] for e in selected}
        for exp in all_exp:
            if exp["id"] not in selected_ids and len(selected) < max_experiences:
                selected.append(exp)
    
    return selected


# ============================================================================
# SKILLS
# ============================================================================

def get_all_candidate_skills() -> List[str]:
    """Get flat list of all candidate skills."""
    data = load_candidate_data()
    return data.get("all_skills_flat", [])


def get_all_candidate_keywords() -> List[str]:
    """Get flat list of all candidate keywords."""
    data = load_candidate_data()
    return data.get("all_keywords_flat", [])


def get_skills_summary() -> Dict[str, Any]:
    """Get categorized skills summary (detailed)."""
    data = load_candidate_data()
    return data.get("skills_summary", {})


def get_skills_for_resume() -> Dict[str, str]:
    """
    Get skills in resume-ready format (category: comma-separated string).
    
    Returns:
        Dict like {"Programming": "Python, SQL, MATLAB", ...}
    """
    data = load_candidate_data()
    return data.get("skills", {})


def get_skills_for_resume_lists() -> Dict[str, List[str]]:
    """
    Get skills as lists per category.
    
    Returns:
        Dict like {"Programming": ["Python", "SQL", "MATLAB"], ...}
    """
    data = load_candidate_data()
    return data.get("skills_for_resume", {})


def get_skills_line(category: str) -> str:
    """
    Get a single skills line for a category.
    
    Args:
        category: One of: Programming, Frameworks, Scientific_AI, Core_Expertise, Databases_Tools
    
    Returns:
        Comma-separated string of skills
    """
    skills = get_skills_for_resume()
    return skills.get(category, "")


def get_skills_by_category(category: str) -> List[str]:
    """
    Get skills for a specific category from detailed summary.
    
    Args:
        category: One of: programming_languages, ml_ai_frameworks, scientific_ai,
                  core_expertise, databases_tools, simulation_modeling, soft_skills
    
    Returns:
        List of skills in that category
    """
    summary = get_skills_summary()
    
    if category in summary:
        value = summary[category]
        if isinstance(value, dict):
            # For programming_languages which has sub-categories
            all_skills = []
            for level_skills in value.values():
                all_skills.extend(level_skills)
            return all_skills
        elif isinstance(value, list):
            return value
    
    return []


def match_candidate_skills_to_jd(jd_skills: List[str]) -> Dict[str, List[str]]:
    """
    Match candidate skills against JD requirements.
    
    Args:
        jd_skills: List of skills from job description
    
    Returns:
        Dict with 'matched', 'missing', 'additional' skill lists
    """
    candidate_skills = set(skill.lower() for skill in get_all_candidate_skills())
    candidate_keywords = set(kw.lower() for kw in get_all_candidate_keywords())
    all_candidate = candidate_skills | candidate_keywords
    
    jd_skills_lower = set(skill.lower() for skill in jd_skills)
    
    matched = []
    missing = []
    
    for skill in jd_skills:
        skill_lower = skill.lower()
        if skill_lower in all_candidate:
            matched.append(skill)
        else:
            # Check for partial matches
            partial_match = False
            for cand_skill in all_candidate:
                if skill_lower in cand_skill or cand_skill in skill_lower:
                    matched.append(skill)
                    partial_match = True
                    break
            if not partial_match:
                missing.append(skill)
    
    # Additional skills candidate has but not in JD
    additional = [s for s in get_all_candidate_skills() if s.lower() not in jd_skills_lower]
    
    return {
        "matched": matched,
        "missing": missing,
        "additional": additional[:10]  # Limit to top 10
    }


# ============================================================================
# PUBLICATIONS
# ============================================================================

def get_publications() -> List[Dict[str, Any]]:
    """Get all publications."""
    data = load_candidate_data()
    return data.get("publications", [])


def get_publications_formatted() -> List[str]:
    """
    Get publications formatted for resume.
    
    Returns:
        List of formatted publication strings
    """
    publications = get_publications()
    formatted = []
    
    for pub in publications:
        title = pub.get("title", "")
        journal = pub.get("journal", "")
        year = pub.get("year", "")
        
        formatted.append(f'"{title}" - {journal} ({year})')
    
    return formatted


# ============================================================================
# COMPLETE RESUME DATA
# ============================================================================

def get_complete_resume_data(role_type: str = "ml_ai", max_experiences: int = 4) -> Dict[str, Any]:
    """
    Get all data needed for resume generation.
    
    Args:
        role_type: Type of role being applied for
        max_experiences: Maximum number of experiences to include
    
    Returns:
        Complete resume data dictionary
    """
    return {
        "header": get_header(),
        "professional_summary": get_professional_summary(role_type),
        "education": get_education_formatted(),
        "certifications": get_certifications_formatted(),
        "experiences": get_experience_for_resume(role_type, max_experiences),
        "skills": get_skills_for_resume(),
        "skills_detailed": get_skills_summary(),
        "publications": get_publications_formatted(),
        "all_skills": get_all_candidate_skills()
    }


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Candidate Data Loader")
    print("=" * 60)
    
    # Test header
    print("\n📋 HEADER:")
    header = get_header()
    print(f"  Name: {header.get('name')}")
    print(f"  Title: {header.get('title')}")
    print(f"  Email: {header.get('email')}")
    print(f"  Phone: {header.get('phone')}")
    print(f"  Location: {header.get('location')}")
    
    # Test professional summary
    print("\n📝 PROFESSIONAL SUMMARY (ML Engineer):")
    summary = get_professional_summary("ml_engineer")
    print(f"  {summary[:100]}...")
    
    # Test education
    print("\n🎓 EDUCATION:")
    for edu in get_education_formatted():
        print(f"  • {edu['degree']}")
        print(f"    {edu['institution']}, {edu['location']}")
        print(f"    GPA: {edu['gpa']} | Graduation: {edu['graduation']}")
    
    # Test certifications
    print("\n🏆 CERTIFICATIONS:")
    for cert in get_certifications_formatted():
        print(f"  • {cert}")
    
    # Test skills (resume format)
    print("\n🔧 SKILLS (Resume Format):")
    skills = get_skills_for_resume()
    for category, skill_line in skills.items():
        print(f"  {category}: {skill_line[:60]}...")
    
    # Test experiences
    print("\n💼 EXPERIENCES:")
    experiences = get_all_experiences()
    print(f"  Total: {len(experiences)}")
    for exp in experiences:
        print(f"  {exp['id']}. {exp['role']} @ {exp['company']}")
    
    # Test relevance mapping
    print("\n🎯 RELEVANCE FOR ML/AI ROLE:")
    ml_exp = get_experiences_by_relevance("ml_ai")
    print(f"  Primary: {[e['role'] for e in ml_exp['primary']]}")
    print(f"  Secondary: {[e['role'] for e in ml_exp['secondary']]}")
    print(f"  Supporting: {[e['role'] for e in ml_exp['supporting']]}")
    
    # Test skill matching
    print("\n🔍 SKILL MATCHING:")
    jd_skills = ["Python", "TensorFlow", "PyTorch", "AWS", "Docker", "LangChain", "XGBoost"]
    match = match_candidate_skills_to_jd(jd_skills)
    print(f"  JD Skills: {jd_skills}")
    print(f"  Matched: {match['matched']}")
    print(f"  Missing: {match['missing']}")
    
    # Test publications
    print("\n📚 PUBLICATIONS:")
    for pub in get_publications_formatted():
        print(f"  • {pub[:80]}...")
    
    # Test complete resume data
    print("\n📄 COMPLETE RESUME DATA:")
    resume = get_complete_resume_data("ml_ai", 3)
    print(f"  Header: ✓")
    print(f"  Summary: {len(resume['professional_summary'])} chars")
    print(f"  Education: {len(resume['education'])} entries")
    print(f"  Certifications: {len(resume['certifications'])} entries")
    print(f"  Experiences: {len(resume['experiences'])} entries")
    print(f"  Skills Categories: {len(resume['skills'])} categories")
    print(f"  Publications: {len(resume['publications'])} entries")
    print(f"  All Skills: {len(resume['all_skills'])} skills")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
