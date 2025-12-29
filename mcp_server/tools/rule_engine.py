"""
Rule Engine Tool for MCP Server.

Validates content against:
- Resume rules (guide, checklist, rubric)
- Cover letter rules (guide, checklist, rubric)
- Action verb compliance
"""

import re
from typing import List, Dict, Any, Optional


def get_action_verbs_flat() -> List[str]:
    """Get flat list of action verbs (fallback if loader not available)."""
    return [
        "Achieved", "Administered", "Analyzed", "Applied", "Assembled",
        "Built", "Calculated", "Collaborated", "Communicated", "Completed",
        "Conducted", "Constructed", "Coordinated", "Created", "Delivered",
        "Demonstrated", "Designed", "Developed", "Directed", "Documented",
        "Engineered", "Enhanced", "Established", "Evaluated", "Executed",
        "Facilitated", "Generated", "Guided", "Identified", "Implemented",
        "Improved", "Increased", "Initiated", "Integrated", "Led",
        "Maintained", "Managed", "Monitored", "Optimized", "Orchestrated",
        "Organized", "Performed", "Planned", "Prepared", "Presented",
        "Produced", "Proposed", "Provided", "Published", "Reduced",
        "Redesigned", "Refined", "Researched", "Resolved", "Reviewed",
        "Scheduled", "Spearheaded", "Streamlined", "Supervised", "Supported",
        "Trained", "Transformed", "Tuned", "Updated", "Utilized",
    ]


def check_action_verb_compliance(
    bullet_points: List[str],
    strict: bool = True
) -> Dict[str, Any]:
    """
    Check if bullet points start with valid action verbs.
    
    Args:
        bullet_points: List of bullet point strings
        strict: If True, require exact match; if False, allow similar words
        
    Returns:
        Dictionary with compliance results
    """
    action_verbs = get_action_verbs_flat()
    action_verbs_lower = {v.lower() for v in action_verbs}
    
    results = []
    compliant_count = 0
    
    for bullet in bullet_points:
        # Clean bullet point
        cleaned = bullet.strip()
        if cleaned.startswith("•") or cleaned.startswith("-"):
            cleaned = cleaned[1:].strip()
        
        # Get first word
        words = cleaned.split()
        if not words:
            results.append({
                "bullet": bullet,
                "first_word": "",
                "is_compliant": False,
                "suggestion": "Empty bullet point",
            })
            continue
        
        first_word = words[0].rstrip(".,;:")
        
        # Check compliance
        is_compliant = first_word.lower() in action_verbs_lower
        
        if is_compliant:
            compliant_count += 1
            results.append({
                "bullet": bullet,
                "first_word": first_word,
                "is_compliant": True,
                "suggestion": None,
            })
        else:
            # Find similar action verb
            suggestions = [v for v in action_verbs if v.lower().startswith(first_word.lower()[:3])]
            results.append({
                "bullet": bullet,
                "first_word": first_word,
                "is_compliant": False,
                "suggestion": suggestions[0] if suggestions else "Use an action verb like: Developed, Implemented, Designed",
            })
    
    return {
        "total_bullets": len(bullet_points),
        "compliant_count": compliant_count,
        "compliance_rate": compliant_count / len(bullet_points) if bullet_points else 1.0,
        "is_fully_compliant": compliant_count == len(bullet_points),
        "details": results,
    }


def _check_checklist_item(item: str, content: Dict[str, Any]) -> bool:
    """Check if a checklist item is satisfied."""
    item_lower = item.lower()
    
    # Contact information check
    if "contact" in item_lower:
        header = content.get("header", {})
        return bool(header.get("email") or header.get("phone"))
    
    # Summary check
    if "summary" in item_lower:
        summary = content.get("professional_summary", "")
        return len(summary) > 50
    
    # Action verbs check
    if "action verb" in item_lower:
        bullets = _extract_bullets_from_resume(content)
        result = check_action_verb_compliance(bullets)
        return result["compliance_rate"] >= 0.8
    
    # Quantifiable check
    if "quantif" in item_lower or "metric" in item_lower:
        text = str(content)
        # Look for numbers and percentages
        has_numbers = bool(re.search(r'\d+%|\d+\.\d+|>\s*\d+|<\s*\d+|\d+x', text))
        return has_numbers
    
    # Skills check
    if "skill" in item_lower:
        skills = content.get("skills", {})
        return len(str(skills)) > 20
    
    # Default: assume passed
    return True


def _score_rubric_category(
    category: str,
    criteria: Dict[str, Any],
    content: Dict[str, Any]
) -> float:
    """Score a single rubric category (0-1)."""
    category_lower = category.lower()
    
    # Content relevance
    if "content" in category_lower:
        # Check for experience and skills
        exp = content.get("experience", [])
        skills = content.get("skills", {})
        if exp and skills:
            return 0.9
        elif exp or skills:
            return 0.7
        return 0.5
    
    # Format check
    if "format" in category_lower:
        # Basic format checks
        has_sections = all(
            key in content
            for key in ["header", "professional_summary", "experience"]
        )
        return 0.9 if has_sections else 0.6
    
    # Keywords check
    if "keyword" in category_lower:
        text = str(content).lower()
        ml_keywords = ["python", "machine learning", "data", "model", "analysis"]
        found = sum(1 for kw in ml_keywords if kw in text)
        return min(1.0, found / 3)
    
    # Achievements check
    if "achievement" in category_lower:
        text = str(content)
        has_metrics = bool(re.search(r'\d+%|\d+\.\d+', text))
        return 0.9 if has_metrics else 0.6
    
    # Default score
    return 0.75


def _extract_bullets_from_resume(content: Dict[str, Any]) -> List[str]:
    """Extract all bullet points from resume content."""
    bullets = []
    
    # From experience
    for exp in content.get("experience", []):
        responsibilities = exp.get("responsibilities", [])
        if isinstance(responsibilities, list):
            bullets.extend(responsibilities)
        elif isinstance(responsibilities, str):
            bullets.extend(responsibilities.split("\n"))
    
    # From projects
    for proj in content.get("projects", []):
        details = proj.get("details", [])
        if isinstance(details, list):
            bullets.extend(details)
        elif isinstance(details, str):
            bullets.extend(details.split("\n"))
    
    return [b.strip() for b in bullets if b.strip()]


def validate_resume_rules(
    resume_content: Dict[str, Any],
    rubric_threshold: float = 0.85
) -> Dict[str, Any]:
    """
    Validate resume against all rules.
    
    Args:
        resume_content: Resume content dictionary
        rubric_threshold: Minimum rubric score (0-1)
        
    Returns:
        Dictionary with validation results
    """
    # Default checklist
    checklist = [
        "Contact information is complete",
        "Summary is present and concise",
        "Experience bullets start with action verbs",
        "Quantifiable achievements are included",
        "Skills section is complete",
    ]
    
    # Default rubric
    rubric = {
        "Content": {"weight": 0.3, "criteria": "Relevant experience"},
        "Format": {"weight": 0.2, "criteria": "Professional formatting"},
        "Keywords": {"weight": 0.25, "criteria": "ATS keywords"},
        "Achievements": {"weight": 0.25, "criteria": "Quantified results"},
    }
    
    results = {
        "is_valid": True,
        "checklist_results": [],
        "rubric_score": 0,
        "rubric_details": {},
        "action_verb_compliance": {},
        "issues": [],
        "suggestions": [],
    }
    
    # Check checklist items
    for item in checklist:
        passed = _check_checklist_item(item, resume_content)
        results["checklist_results"].append({
            "item": item,
            "passed": passed,
        })
        if not passed:
            results["issues"].append(f"Checklist failed: {item}")
    
    # Calculate rubric score
    total_weight = 0
    weighted_score = 0
    
    for category, criteria in rubric.items():
        weight = criteria.get("weight", 1.0)
        score = _score_rubric_category(category, criteria, resume_content)
        
        total_weight += weight
        weighted_score += weight * score
        
        results["rubric_details"][category] = {
            "score": score,
            "weight": weight,
            "criteria": criteria.get("criteria", ""),
        }
    
    results["rubric_score"] = weighted_score / total_weight if total_weight > 0 else 0
    
    # Check action verb compliance
    all_bullets = _extract_bullets_from_resume(resume_content)
    results["action_verb_compliance"] = check_action_verb_compliance(all_bullets)
    
    # Determine overall validity
    checklist_passed = all(r["passed"] for r in results["checklist_results"])
    rubric_passed = results["rubric_score"] >= rubric_threshold
    verbs_passed = results["action_verb_compliance"]["compliance_rate"] >= 0.8
    
    results["is_valid"] = checklist_passed and rubric_passed and verbs_passed
    
    # Generate suggestions
    if not rubric_passed:
        results["suggestions"].append(
            f"Improve rubric score from {results['rubric_score']:.0%} to {rubric_threshold:.0%}"
        )
    
    if not verbs_passed:
        results["suggestions"].append(
            "Start more bullet points with action verbs"
        )
    
    return results


def validate_cover_letter_rules(
    cover_letter: str,
    rubric_threshold: float = 0.85
) -> Dict[str, Any]:
    """
    Validate cover letter against all rules.
    
    Args:
        cover_letter: Cover letter text
        rubric_threshold: Minimum rubric score (0-1)
        
    Returns:
        Dictionary with validation results
    """
    # Default checklist
    checklist = [
        "Has greeting",
        "Has opening paragraph",
        "Has body paragraphs",
        "Has closing",
        "Mentions specific role",
    ]
    
    results = {
        "is_valid": True,
        "checklist_results": [],
        "rubric_score": 0,
        "rubric_details": {},
        "issues": [],
        "suggestions": [],
    }
    
    text_lower = cover_letter.lower()
    paragraphs = [p.strip() for p in cover_letter.split("\n\n") if p.strip()]
    
    # Check checklist
    checklist_checks = {
        "Has greeting": any(g in text_lower for g in ["dear", "hi ", "hello"]),
        "Has opening paragraph": len(paragraphs) >= 1 and len(paragraphs[0]) > 50,
        "Has body paragraphs": len(paragraphs) >= 3,
        "Has closing": any(c in text_lower for c in ["sincerely", "regards", "thank you"]),
        "Mentions specific role": any(r in text_lower for r in ["role", "position", "opportunity"]),
    }
    
    for item, passed in checklist_checks.items():
        results["checklist_results"].append({"item": item, "passed": passed})
        if not passed:
            results["issues"].append(f"Missing: {item}")
    
    # Calculate rubric score
    rubric = {
        "Personalization": {"weight": 0.25},
        "Relevance": {"weight": 0.30},
        "Structure": {"weight": 0.20},
        "Impact": {"weight": 0.25},
    }
    
    total_weight = 0
    weighted_score = 0
    
    for category, criteria in rubric.items():
        weight = criteria["weight"]
        
        # Simple scoring
        if category == "Personalization":
            score = 0.8 if any(w in text_lower for w in ["company", "team", "mission"]) else 0.5
        elif category == "Relevance":
            score = 0.8 if len(cover_letter) > 500 else 0.6
        elif category == "Structure":
            score = 0.9 if len(paragraphs) >= 4 else 0.6
        else:  # Impact
            score = 0.8 if any(w in text_lower for w in ["achieved", "improved", "led"]) else 0.6
        
        total_weight += weight
        weighted_score += weight * score
        
        results["rubric_details"][category] = {"score": score, "weight": weight}
    
    results["rubric_score"] = weighted_score / total_weight if total_weight > 0 else 0
    
    # Determine validity
    checklist_passed = sum(1 for r in results["checklist_results"] if r["passed"]) >= 3
    rubric_passed = results["rubric_score"] >= rubric_threshold
    
    results["is_valid"] = checklist_passed and rubric_passed
    
    return results


if __name__ == "__main__":
    # Test rule engine
    print("Testing Rule Engine...")
    
    # Test action verb compliance
    bullets = [
        "• Developed machine learning models",
        "• Was responsible for data analysis",
        "• Implemented deep learning pipelines",
        "Designed scalable architectures",
    ]
    
    result = check_action_verb_compliance(bullets)
    print(f"Action verb compliance: {result['compliance_rate']:.0%}")
    
    # Test resume validation
    resume = {
        "header": {"name": "Test User", "email": "test@example.com"},
        "professional_summary": "Experienced ML engineer with expertise in deep learning and NLP.",
        "experience": [
            {
                "company": "Test Corp",
                "responsibilities": [
                    "Developed ML models achieving 95% accuracy",
                    "Led team of 5 engineers",
                ]
            }
        ],
        "projects": [],
        "skills": {"Programming": "Python, SQL"},
    }
    
    result = validate_resume_rules(resume)
    print(f"Resume valid: {result['is_valid']}")
    print(f"Rubric score: {result['rubric_score']:.0%}")
    
    # Test cover letter validation
    cover_letter = """Dear Hiring Manager,

I am writing to express my interest in the Machine Learning Engineer position at your company.

With over 5 years of experience in developing production ML systems, I have achieved significant improvements in model accuracy and deployment efficiency.

I would welcome the opportunity to discuss how my experience aligns with your team's goals.

Sincerely,
Test User
"""
    
    result = validate_cover_letter_rules(cover_letter)
    print(f"Cover letter valid: {result['is_valid']}")
    print(f"Rubric score: {result['rubric_score']:.0%}")
    
    print("Rule Engine tests complete!")
