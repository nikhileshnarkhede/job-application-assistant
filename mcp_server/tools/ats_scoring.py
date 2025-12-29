"""
ATS Scoring Tool for MCP Server.

Calculates ATS (Applicant Tracking System) compatibility scores.
Provides feedback and improvement suggestions.
"""

import re
from typing import List, Dict, Any, Optional, Set


def calculate_ats_score(
    resume_content: Dict[str, Any],
    jd_keywords: List[str],
    jd_skills_required: Optional[List[str]] = None,
    jd_skills_preferred: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Calculate ATS compatibility score for a resume.
    
    Scoring breakdown:
    - 40%: Hard technical skills match
    - 20%: Soft skills match
    - 20%: Keyword density
    - 10%: Structure compliance
    - 10%: JD responsibility alignment
    
    Args:
        resume_content: Resume content dictionary
        jd_keywords: Keywords extracted from JD
        jd_skills_required: Required skills from JD
        jd_skills_preferred: Preferred skills from JD
        
    Returns:
        Dictionary with score and breakdown
    """
    jd_skills_required = jd_skills_required or []
    jd_skills_preferred = jd_skills_preferred or []
    
    # Convert resume to searchable text
    resume_text = _extract_full_text(resume_content).lower()
    
    # 1. Hard technical skills match (40%)
    hard_skill_score = _calculate_skill_match(
        resume_text,
        jd_skills_required + jd_skills_preferred,
        weight_required=0.7,
        weight_preferred=0.3
    )
    
    # 2. Soft skills match (20%)
    soft_skills = ["communication", "leadership", "teamwork", "problem-solving", 
                   "analytical", "collaborative", "detail-oriented"]
    jd_soft_skills = [s for s in jd_keywords if s.lower() in soft_skills]
    soft_skill_score = _calculate_keyword_presence(resume_text, jd_soft_skills)
    
    # 3. Keyword density (20%)
    keyword_score = _calculate_keyword_density(resume_text, jd_keywords)
    
    # 4. Structure compliance (10%)
    structure_score = _check_structure_compliance(resume_content)
    
    # 5. JD alignment (10%)
    alignment_score = _calculate_jd_alignment(resume_text, jd_keywords)
    
    # Calculate weighted total
    total_score = (
        hard_skill_score * 0.40 +
        soft_skill_score * 0.20 +
        keyword_score * 0.20 +
        structure_score * 0.10 +
        alignment_score * 0.10
    )
    
    # Convert to 0-100 scale
    final_score = min(100, max(0, total_score * 100))
    
    return {
        "score": round(final_score, 1),
        "breakdown": {
            "hard_skills": round(hard_skill_score * 100, 1),
            "soft_skills": round(soft_skill_score * 100, 1),
            "keywords": round(keyword_score * 100, 1),
            "structure": round(structure_score * 100, 1),
            "alignment": round(alignment_score * 100, 1),
        },
        "weights": {
            "hard_skills": 0.40,
            "soft_skills": 0.20,
            "keywords": 0.20,
            "structure": 0.10,
            "alignment": 0.10,
        },
        "matched_skills": _get_matched_skills(resume_text, jd_skills_required + jd_skills_preferred),
        "missing_skills": _get_missing_skills(resume_text, jd_skills_required),
    }


def get_ats_feedback(
    ats_result: Dict[str, Any],
    target_score: int = 95
) -> Dict[str, Any]:
    """
    Generate feedback and improvement suggestions based on ATS score.
    
    Args:
        ats_result: Result from calculate_ats_score
        target_score: Target ATS score to achieve
        
    Returns:
        Dictionary with feedback and suggestions
    """
    current_score = ats_result["score"]
    breakdown = ats_result["breakdown"]
    missing_skills = ats_result.get("missing_skills", [])
    
    feedback = {
        "current_score": current_score,
        "target_score": target_score,
        "gap": max(0, target_score - current_score),
        "status": "pass" if current_score >= target_score else "needs_improvement",
        "priority_areas": [],
        "suggestions": [],
        "missing_skills_to_add": missing_skills[:5],
    }
    
    # Identify priority areas (lowest scores)
    sorted_breakdown = sorted(
        breakdown.items(),
        key=lambda x: x[1]
    )
    
    for area, score in sorted_breakdown[:3]:
        if score < 80:
            feedback["priority_areas"].append({
                "area": area,
                "current_score": score,
                "improvement_needed": 80 - score,
            })
    
    # Generate specific suggestions
    if breakdown["hard_skills"] < 80:
        feedback["suggestions"].append({
            "area": "Technical Skills",
            "action": "Add more technical keywords from the job description",
            "examples": missing_skills[:3] if missing_skills else ["Python", "TensorFlow", "SQL"],
        })
    
    if breakdown["keywords"] < 80:
        feedback["suggestions"].append({
            "area": "Keyword Optimization",
            "action": "Increase keyword density by naturally incorporating JD terms",
            "tip": "Use exact phrases from the job description where appropriate",
        })
    
    if breakdown["structure"] < 90:
        feedback["suggestions"].append({
            "area": "Resume Structure",
            "action": "Ensure all standard sections are present and well-formatted",
            "tip": "Include: Summary, Skills, Experience, Projects, Education",
        })
    
    if breakdown["alignment"] < 80:
        feedback["suggestions"].append({
            "area": "JD Alignment",
            "action": "Tailor experience bullets to match job responsibilities",
            "tip": "Mirror the language and priorities from the job description",
        })
    
    # Add missing skills suggestion
    if missing_skills:
        feedback["suggestions"].append({
            "area": "Missing Skills",
            "action": f"Add these skills if you have them: {', '.join(missing_skills[:5])}",
            "tip": "Only add skills you actually possess",
        })
    
    return feedback


def _extract_full_text(resume_content: Dict[str, Any]) -> str:
    """Extract all text from resume content."""
    parts = []
    
    # Header
    header = resume_content.get("header", {})
    if isinstance(header, dict):
        parts.extend(str(v) for v in header.values())
    
    # Summary
    summary = resume_content.get("professional_summary", "")
    if summary:
        parts.append(str(summary))
    
    # Skills
    skills = resume_content.get("skills", {})
    if isinstance(skills, dict):
        parts.extend(str(v) for v in skills.values())
    elif isinstance(skills, str):
        parts.append(skills)
    
    # Experience
    for exp in resume_content.get("experience", []):
        if isinstance(exp, dict):
            parts.append(str(exp.get("role", "")))
            parts.append(str(exp.get("company", "")))
            responsibilities = exp.get("responsibilities", [])
            if isinstance(responsibilities, list):
                parts.extend(str(r) for r in responsibilities)
            else:
                parts.append(str(responsibilities))
    
    # Projects
    for proj in resume_content.get("projects", []):
        if isinstance(proj, dict):
            parts.append(str(proj.get("title", "")))
            details = proj.get("details", [])
            if isinstance(details, list):
                parts.extend(str(d) for d in details)
            else:
                parts.append(str(details))
    
    return " ".join(parts)


def _calculate_skill_match(
    resume_text: str,
    skills: List[str],
    weight_required: float = 0.7,
    weight_preferred: float = 0.3
) -> float:
    """Calculate skill match score."""
    if not skills:
        return 1.0
    
    matched = 0
    for skill in skills:
        if skill.lower() in resume_text:
            matched += 1
    
    return matched / len(skills) if skills else 1.0


def _calculate_keyword_presence(
    resume_text: str,
    keywords: List[str]
) -> float:
    """Calculate keyword presence score."""
    if not keywords:
        return 1.0
    
    found = sum(1 for kw in keywords if kw.lower() in resume_text)
    return found / len(keywords)


def _calculate_keyword_density(
    resume_text: str,
    keywords: List[str]
) -> float:
    """Calculate keyword density in the resume."""
    if not keywords or not resume_text:
        return 0.5
    
    word_count = len(resume_text.split())
    keyword_count = sum(
        resume_text.count(kw.lower())
        for kw in keywords
    )
    
    # Ideal density is around 2-5%
    density = keyword_count / word_count if word_count > 0 else 0
    
    # Score based on optimal density range
    if 0.02 <= density <= 0.05:
        return 1.0
    elif density < 0.01:
        return 0.5
    elif density > 0.08:
        return 0.7  # Too keyword-stuffed
    else:
        return 0.8


def _check_structure_compliance(resume_content: Dict[str, Any]) -> float:
    """Check if resume has proper structure."""
    required_sections = [
        "header",
        "professional_summary",
        "skills",
        "experience",
    ]
    
    optional_sections = [
        "projects",
        "education",
        "certifications",
    ]
    
    # Check required sections
    required_present = sum(
        1 for section in required_sections
        if resume_content.get(section)
    )
    required_score = required_present / len(required_sections)
    
    # Check optional sections (bonus)
    optional_present = sum(
        1 for section in optional_sections
        if resume_content.get(section)
    )
    optional_score = optional_present / len(optional_sections) * 0.2
    
    return min(1.0, required_score + optional_score)


def _calculate_jd_alignment(
    resume_text: str,
    jd_keywords: List[str]
) -> float:
    """Calculate alignment between resume and JD."""
    if not jd_keywords:
        return 1.0
    
    # Check for presence of top keywords
    top_keywords = jd_keywords[:20]
    found = sum(1 for kw in top_keywords if kw.lower() in resume_text)
    
    return found / len(top_keywords)


def _get_matched_skills(
    resume_text: str,
    skills: List[str]
) -> List[str]:
    """Get list of skills found in resume."""
    return [s for s in skills if s.lower() in resume_text]


def _get_missing_skills(
    resume_text: str,
    required_skills: List[str]
) -> List[str]:
    """Get list of required skills not found in resume."""
    return [s for s in required_skills if s.lower() not in resume_text]


if __name__ == "__main__":
    # Test ATS scoring
    print("Testing ATS Scoring...")
    
    resume = {
        "header": {"name": "Test User", "email": "test@example.com"},
        "professional_summary": "Machine learning engineer with experience in Python, TensorFlow, and deep learning.",
        "skills": {
            "Programming": "Python, SQL, Java",
            "ML": "TensorFlow, PyTorch, Scikit-learn",
        },
        "experience": [
            {
                "role": "ML Engineer",
                "company": "Tech Corp",
                "responsibilities": [
                    "Developed deep learning models achieving 95% accuracy",
                    "Implemented NLP pipelines for text classification",
                ]
            }
        ],
        "projects": [
            {
                "title": "Stock Prediction Model",
                "details": ["Built LSTM model for financial forecasting"],
            }
        ],
    }
    
    jd_keywords = [
        "machine learning", "python", "tensorflow", "deep learning",
        "nlp", "data science", "sql", "model deployment",
    ]
    
    jd_skills_required = ["Python", "TensorFlow", "Machine Learning", "SQL"]
    jd_skills_preferred = ["PyTorch", "NLP", "AWS", "Docker"]
    
    result = calculate_ats_score(
        resume,
        jd_keywords,
        jd_skills_required,
        jd_skills_preferred
    )
    
    print(f"ATS Score: {result['score']}")
    print(f"Breakdown: {result['breakdown']}")
    print(f"Matched: {result['matched_skills']}")
    print(f"Missing: {result['missing_skills']}")
    
    # Get feedback
    feedback = get_ats_feedback(result)
    print(f"Status: {feedback['status']}")
    print(f"Priority areas: {len(feedback['priority_areas'])}")
    print(f"Suggestions: {len(feedback['suggestions'])}")
    
    print("ATS Scoring tests complete!")
