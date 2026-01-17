"""
Candidate Experience Loader

Loads and queries candidate experience data for resume tailoring.
Supports the simplified JSON template structure.

Template Structure:
- header: name, location, email, phone, linkedin_url, github_url, portfolio_url
- professional_summary: string
- education: list of {institution, graduation_date, degree, location}
- experience: list of {company, date_range, job_title, location, bullets}
- research: {title, doi_url, doi_text}
- projects: list of {name, subtitle, technologies, github_url, bullets}
- skills: {ai_ml, ai_applications, mlops, frameworks} - all strings
- certifications: list of {name, issuer, year}
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
        Dict with name, location, email, phone, linkedin, github, portfolio
    """
    data = load_candidate_data()
    header = data.get("header", {})
    
    # Normalize to standard format for resume builder
    return {
        "name": header.get("name", ""),
        "location": header.get("location", ""),
        "email": header.get("email", ""),
        "phone": header.get("phone", ""),
        "linkedin": header.get("linkedin_url", ""),
        "github": header.get("github_url", ""),
        "portfolio": header.get("portfolio_url", ""),
        # Legacy field for backward compatibility
        "contact_line": f"{header.get('location', '')}  •  {header.get('phone', '')}  •  {header.get('email', '')}  •  {header.get('linkedin_url', '')}  •  {header.get('github_url', '')}"
    }


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
    Get professional summary.
    
    Args:
        role_type: Role type (ignored in simplified template - single summary)
    
    Returns:
        Professional summary string
    """
    data = load_candidate_data()
    return data.get("professional_summary", "")


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
        List of formatted education entries with standard keys
    """
    education = get_education()
    formatted = []
    
    for edu in education:
        entry = {
            "institution": edu.get("institution", ""),
            "location": edu.get("location", ""),
            "degree": edu.get("degree", ""),
            "graduation": edu.get("graduation_date", ""),
            # Parse GPA from degree string if present
            "gpa": "",
            "coursework": "",
            "highlights": []
        }
        
        # Try to extract GPA from degree string (e.g., "M.S. in Data Science, GPA: 4.0; Coursework: ML, NLP")
        degree_str = edu.get("degree", "")
        if "GPA:" in degree_str:
            parts = degree_str.split("GPA:")
            if len(parts) > 1:
                gpa_part = parts[1].split(";")[0].strip()
                entry["gpa"] = gpa_part
        
        if "Coursework:" in degree_str:
            parts = degree_str.split("Coursework:")
            if len(parts) > 1:
                entry["coursework"] = parts[1].strip()
        
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
    """
    Get all experience entries.
    
    Returns:
        List of experience dictionaries with normalized keys
    """
    data = load_candidate_data()
    experiences = data.get("experience", [])
    
    # Normalize to standard format expected by pipeline
    normalized = []
    for idx, exp in enumerate(experiences):
        normalized_exp = {
            "id": idx + 1,
            "role": exp.get("job_title", ""),
            "role_full": exp.get("job_title", ""),
            "company": exp.get("company", ""),
            "employment_type": "",
            "dates": {
                "start": exp.get("date_range", "").split(" -- ")[0] if " -- " in exp.get("date_range", "") else "",
                "end": exp.get("date_range", "").split(" -- ")[1] if " -- " in exp.get("date_range", "") else "",
                "duration": exp.get("date_range", "")
            },
            "location": {
                "city": exp.get("location", "").split(",")[0].strip() if "," in exp.get("location", "") else exp.get("location", ""),
                "state": exp.get("location", "").split(",")[1].strip() if "," in exp.get("location", "") else "",
                "country": "",
                "type": "Remote" if "Remote" in exp.get("location", "") else "On-site"
            },
            "bullets_flat": exp.get("bullets", []),
            "skills": extract_skills_from_bullets(exp.get("bullets", [])),
            "keywords": extract_keywords_from_bullets(exp.get("bullets", [])),
            "relevance_tags": ["ml_ai"]  # Default tag
        }
        normalized.append(normalized_exp)
    
    return normalized


def extract_skills_from_bullets(bullets: List[str]) -> List[str]:
    """Extract skills from bullet points (looks for 'Skills:' line)."""
    skills = []
    for bullet in bullets:
        if bullet.startswith("Skills:"):
            skills_text = bullet.replace("Skills:", "").strip()
            skills = [s.strip() for s in skills_text.split(",")]
            break
    return skills


def extract_keywords_from_bullets(bullets: List[str]) -> List[str]:
    """Extract keywords from bullet points."""
    keywords = set()
    tech_terms = [
        "Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning",
        "NLP", "LLM", "API", "Git", "Docker", "AWS", "ML", "AI", "RAG",
        "Scikit-learn", "Keras", "Data", "Model", "Pipeline"
    ]
    
    for bullet in bullets:
        for term in tech_terms:
            if term.lower() in bullet.lower():
                keywords.add(term)
    
    return list(keywords)


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
    In simplified template, all experiences are treated as primary.
    
    Returns:
        Dict with 'primary', 'secondary', 'supporting' experience lists
    """
    experiences = get_all_experiences()
    
    # In simplified template, prioritize by order (first = most relevant)
    return {
        "primary": experiences[:2] if len(experiences) >= 2 else experiences,
        "secondary": experiences[2:3] if len(experiences) >= 3 else [],
        "supporting": experiences[3:] if len(experiences) >= 4 else []
    }


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
        exp_text = " ".join(exp.get("bullets_flat", [])).lower()
        score = sum(1 for kw in jd_keywords_lower if kw in exp_text)
        
        # Bonus for recent experience
        if exp.get("id") == 1:
            score += 2
        elif exp.get("id") == 2:
            score += 1
        
        scored_experiences.append({
            "experience": exp,
            "score": score
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
    experiences = get_all_experiences()
    return experiences[:max_experiences]


# ============================================================================
# SKILLS
# ============================================================================

def get_all_candidate_skills() -> List[str]:
    """Get flat list of all candidate skills."""
    data = load_candidate_data()
    skills = data.get("skills", {})
    
    all_skills = []
    for category, skill_string in skills.items():
        if isinstance(skill_string, str):
            all_skills.extend([s.strip() for s in skill_string.split(",")])
        elif isinstance(skill_string, list):
            all_skills.extend(skill_string)
    
    return list(set(all_skills))


def get_all_candidate_keywords() -> List[str]:
    """Get flat list of all candidate keywords (same as skills in simplified template)."""
    return get_all_candidate_skills()


def get_skills_summary() -> Dict[str, Any]:
    """Get categorized skills summary."""
    data = load_candidate_data()
    skills = data.get("skills", {})
    
    # Convert strings to lists for detailed summary
    summary = {}
    for category, skill_string in skills.items():
        if isinstance(skill_string, str):
            summary[category] = [s.strip() for s in skill_string.split(",")]
        elif isinstance(skill_string, list):
            summary[category] = skill_string
    
    return summary


def get_skills_for_resume() -> Dict[str, str]:
    """
    Get skills in resume-ready format (category: comma-separated string).
    
    Returns:
        Dict like {"AI/ML": "Python, TensorFlow, ...", ...}
    """
    data = load_candidate_data()
    skills = data.get("skills", {})
    
    # Map internal keys to display names
    display_names = {
        "ai_ml": "AI/ML",
        "ai_applications": "AI Applications",
        "mlops": "MLOps & Tools",
        "frameworks": "Frameworks"
    }
    
    formatted = {}
    for key, value in skills.items():
        display_key = display_names.get(key, key.replace("_", " ").title())
        formatted[display_key] = value if isinstance(value, str) else ", ".join(value)
    
    return formatted


def get_skills_for_resume_lists() -> Dict[str, List[str]]:
    """
    Get skills as lists per category.
    
    Returns:
        Dict like {"AI/ML": ["Python", "TensorFlow", ...], ...}
    """
    data = load_candidate_data()
    skills = data.get("skills", {})
    
    # Map internal keys to display names
    display_names = {
        "ai_ml": "AI/ML",
        "ai_applications": "AI Applications",
        "mlops": "MLOps & Tools",
        "frameworks": "Frameworks"
    }
    
    formatted = {}
    for key, value in skills.items():
        display_key = display_names.get(key, key.replace("_", " ").title())
        if isinstance(value, str):
            formatted[display_key] = [s.strip() for s in value.split(",")]
        elif isinstance(value, list):
            formatted[display_key] = value
    
    return formatted


def get_skills_line(category: str) -> str:
    """
    Get a single skills line for a category.
    
    Args:
        category: Category name (e.g., 'ai_ml', 'frameworks')
    
    Returns:
        Comma-separated string of skills
    """
    skills = get_skills_for_resume()
    
    # Try exact match
    if category in skills:
        return skills[category]
    
    # Try normalized match
    for key, value in skills.items():
        if category.lower().replace("_", "") in key.lower().replace(" ", "").replace("/", ""):
            return value
    
    return ""


def get_skills_by_category(category: str) -> List[str]:
    """
    Get skills for a specific category.
    
    Args:
        category: Category name
    
    Returns:
        List of skills in that category
    """
    skills_lists = get_skills_for_resume_lists()
    
    if category in skills_lists:
        return skills_lists[category]
    
    # Try normalized match
    for key, value in skills_lists.items():
        if category.lower().replace("_", "") in key.lower().replace(" ", "").replace("/", ""):
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
    jd_skills_lower = set(skill.lower() for skill in jd_skills)
    
    matched = []
    missing = []
    
    for skill in jd_skills:
        skill_lower = skill.lower()
        if skill_lower in candidate_skills:
            matched.append(skill)
        else:
            # Check for partial matches
            partial_match = False
            for cand_skill in candidate_skills:
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
        "additional": additional[:10]
    }


# ============================================================================
# PROJECTS
# ============================================================================

def get_projects() -> List[Dict[str, Any]]:
    """Get all projects."""
    data = load_candidate_data()
    projects = data.get("projects", [])
    
    # Normalize to standard format
    normalized = []
    for idx, proj in enumerate(projects):
        normalized_proj = {
            "id": idx + 1,
            "name": proj.get("name", ""),
            "github_url": proj.get("github_url", ""),
            "description": proj.get("subtitle", ""),
            "technologies": proj.get("technologies", ""),
            "tech_stack": {
                "main": [t.strip() for t in proj.get("technologies", "").split(",")]
            },
            "bullets": proj.get("bullets", []),
            "bullets_for_resume": proj.get("bullets", []),
            "relevance_tags": ["ml_ai"]
        }
        normalized.append(normalized_proj)
    
    return normalized


def get_projects_for_resume(max_projects: int = 3) -> List[Dict[str, Any]]:
    """Get projects formatted for resume."""
    return get_projects()[:max_projects]


# ============================================================================
# PUBLICATIONS / RESEARCH
# ============================================================================

def get_publications() -> List[Dict[str, Any]]:
    """Get all publications."""
    data = load_candidate_data()
    research = data.get("research", {})
    
    if research:
        return [{
            "title": research.get("title", ""),
            "journal": "",
            "year": "",
            "doi": research.get("doi_url", ""),
            "doi_text": research.get("doi_text", "")
        }]
    
    return []


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
        doi = pub.get("doi_text", "")
        
        if doi:
            formatted.append(f"{title} ({doi})")
        else:
            formatted.append(title)
    
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
        "projects": get_projects_for_resume(),
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
    print("Testing Candidate Data Loader (Simplified Template)")
    print("=" * 60)
    
    # Test header
    print("\n📋 HEADER:")
    header = get_header()
    print(f"  Name: {header.get('name')}")
    print(f"  Email: {header.get('email')}")
    print(f"  Location: {header.get('location')}")
    print(f"  LinkedIn: {header.get('linkedin')}")
    print(f"  GitHub: {header.get('github')}")
    
    # Test professional summary
    print("\n📝 PROFESSIONAL SUMMARY:")
    summary = get_professional_summary()
    print(f"  {summary[:100]}...")
    
    # Test education
    print("\n🎓 EDUCATION:")
    for edu in get_education_formatted():
        print(f"  • {edu['degree']}")
        print(f"    {edu['institution']}, {edu['location']}")
    
    # Test certifications
    print("\n🏆 CERTIFICATIONS:")
    for cert in get_certifications_formatted():
        print(f"  • {cert}")
    
    # Test skills
    print("\n🔧 SKILLS:")
    skills = get_skills_for_resume()
    for category, skill_line in skills.items():
        print(f"  {category}: {skill_line[:50]}...")
    
    # Test experiences
    print("\n💼 EXPERIENCES:")
    experiences = get_all_experiences()
    print(f"  Total: {len(experiences)}")
    for exp in experiences:
        print(f"  {exp['id']}. {exp['role']} @ {exp['company']}")
        print(f"     Bullets: {len(exp['bullets_flat'])}")
    
    # Test projects
    print("\n🚀 PROJECTS:")
    projects = get_projects()
    for proj in projects:
        print(f"  • {proj['name']} ({proj['technologies']})")
    
    # Test publications
    print("\n📚 PUBLICATIONS:")
    for pub in get_publications_formatted():
        print(f"  • {pub[:70]}...")
    
    # Test all skills flat
    print("\n🔍 ALL SKILLS (flat):")
    all_skills = get_all_candidate_skills()
    print(f"  Total: {len(all_skills)}")
    print(f"  Sample: {all_skills[:5]}")
    
    # Test complete resume data
    print("\n📄 COMPLETE RESUME DATA:")
    resume = get_complete_resume_data("ml_ai", 3)
    print(f"  Header: ✓")
    print(f"  Summary: {len(resume['professional_summary'])} chars")
    print(f"  Education: {len(resume['education'])} entries")
    print(f"  Certifications: {len(resume['certifications'])} entries")
    print(f"  Experiences: {len(resume['experiences'])} entries")
    print(f"  Projects: {len(resume['projects'])} entries")
    print(f"  Skills Categories: {len(resume['skills'])} categories")
    print(f"  Publications: {len(resume['publications'])} entries")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
