"""
ATS Optimizer Nodes

Focus: Aggressively add missing keywords to Skills, Experience, Projects, and Summary.
PRIORITY: Skills section should contain as many keywords as possible.
"""

import os
import re
import json
from typing import Dict, Any, List, Set, Tuple
from pathlib import Path
from copy import deepcopy

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from subgraphs.ats_optimizer.state import (
    ATSOptimizerState,
    KEYWORD_WEIGHTS,
    SECTION_WEIGHTS,
    SCORE_WEIGHTS,
    SKILL_ALIASES,
    FORMAT_CHECKS
)
from state.state_models import ATSAnalysis, ResumeJSON


# ============================================================================
# CONFIGURATION
# ============================================================================

def get_llm():
    """Get configured LLM instance."""
    if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            temperature=0.3,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    else:
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )


def load_prompt(filename: str) -> str:
    """Load prompt from file."""
    prompt_dir = Path(__file__).parent / "prompts"
    prompt_path = prompt_dir / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


# ============================================================================
# KEYWORD TO CATEGORY MAPPING - COMPREHENSIVE
# ============================================================================

KEYWORD_CATEGORY_MAP = {
    # Programming Languages
    "java": "Programming Languages",
    "python": "Programming Languages",
    "c++": "Programming Languages",
    "c": "Programming Languages",
    "sql": "Programming Languages",
    "r": "Programming Languages",
    "scala": "Programming Languages",
    "javascript": "Programming Languages",
    "typescript": "Programming Languages",
    "go": "Programming Languages",
    "rust": "Programming Languages",
    "matlab": "Programming Languages",
    
    # ML/AI
    "machine learning": "ML/AI & Data Science",
    "deep learning": "ML/AI & Data Science",
    "neural networks": "ML/AI & Data Science",
    "nlp": "ML/AI & Data Science",
    "natural language processing": "ML/AI & Data Science",
    "computer vision": "ML/AI & Data Science",
    "reinforcement learning": "ML/AI & Data Science",
    "data mining": "ML/AI & Data Science",
    "data science": "ML/AI & Data Science",
    
    # Core CS/Engineering
    "algorithms": "Core Expertise",
    "data structures": "Core Expertise",
    "numerical optimization": "Core Expertise",
    "parallel computing": "Core Expertise",
    "distributed computing": "Core Expertise",
    "high-performance computing": "Core Expertise",
    "software development": "Core Expertise",
    "professional software development": "Core Expertise",
    "system design": "Core Expertise",
    
    # Tools & Platforms
    "unix": "Tools & Platforms",
    "linux": "Tools & Platforms",
    "unix/linux": "Tools & Platforms",
    "aws": "Tools & Platforms",
    "docker": "Tools & Platforms",
    "kubernetes": "Tools & Platforms",
    "git": "Tools & Platforms",
    
    # Methodologies (these go to summary, not skills)
    "investigating": None,  # Action verb - summary
    "designing": None,
    "prototyping": None,
    "delivering": None,
    "delivering new solutions": None,
}


# ============================================================================
# NODE 1: EXTRACT JD KEYWORDS
# ============================================================================

def extract_jd_keywords(state: ATSOptimizerState) -> Dict[str, Any]:
    """Extract and weight all keywords from job description."""
    jd = state.structured_jd
    
    if not jd:
        return {"error_message": "No structured JD provided"}
    
    target_keywords = {}
    
    # Required skills - highest weight
    for skill in (jd.skills_required or []):
        skill_lower = skill.lower().strip()
        if skill_lower and len(skill_lower) > 1:
            target_keywords[skill_lower] = KEYWORD_WEIGHTS["required_skills"]
    
    # Preferred skills
    for skill in (jd.skills_preferred or []):
        skill_lower = skill.lower().strip()
        if skill_lower and skill_lower not in target_keywords and len(skill_lower) > 1:
            target_keywords[skill_lower] = KEYWORD_WEIGHTS["preferred_skills"]
    
    # General keywords
    for kw in (jd.keywords or []):
        kw_lower = kw.lower().strip()
        if kw_lower and kw_lower not in target_keywords and len(kw_lower) > 1:
            target_keywords[kw_lower] = KEYWORD_WEIGHTS["general_keywords"]
    
    print(f"  🎯 Extracted {len(target_keywords)} target keywords")
    print(f"     Required: {sum(1 for v in target_keywords.values() if v == 3.0)}")
    print(f"     Preferred: {sum(1 for v in target_keywords.values() if v == 2.0)}")
    print(f"     Other: {sum(1 for v in target_keywords.values() if v < 2.0)}")
    
    return {"target_keywords": target_keywords}


# ============================================================================
# NODE 2: SCAN RESUME CONTENT
# ============================================================================

def scan_resume_content(state: ATSOptimizerState) -> Dict[str, Any]:
    """Extract all text content from resume sections."""
    resume = state.optimized_resume or state.resume_json
    
    if not resume:
        return {"error_message": "No resume JSON provided"}
    
    sections = {}
    
    # Summary
    sections["summary"] = resume.summary or ""
    
    # Skills - IMPORTANT: Include category names AND skill values
    skills_text = []
    for category, skills in (resume.skills or {}).items():
        skills_text.append(f"{category}: {skills}")
    sections["skills"] = " ".join(skills_text)
    
    # Experience
    exp_text = []
    for exp in (resume.experience or []):
        exp_text.append(exp.get("role", ""))
        exp_text.append(exp.get("company", ""))
        for bullet in exp.get("bullets", []):
            exp_text.append(bullet)
    sections["experience"] = " ".join(exp_text)
    
    # Projects
    proj_text = []
    for proj in (resume.projects or []):
        proj_text.append(proj.get("name", ""))
        proj_text.append(proj.get("technologies", ""))
        for bullet in proj.get("bullets", []):
            proj_text.append(bullet)
    sections["projects"] = " ".join(proj_text)
    
    # Education
    edu_text = []
    for edu in (resume.education or []):
        edu_text.append(edu.get("degree", ""))
        edu_text.append(edu.get("institution", ""))
        edu_text.extend(edu.get("highlights", []))
    sections["education"] = " ".join(edu_text)
    
    # Certifications
    sections["certifications"] = " ".join(resume.certifications or [])
    
    full_text = " ".join(sections.values())
    
    print(f"  📄 Scanned resume: {len(full_text)} characters")
    print(f"     Skills section: {len(sections['skills'])} chars")
    
    return {
        "resume_text_by_section": sections,
        "resume_text_full": full_text
    }


# ============================================================================
# NODE 3: CALCULATE ATS SCORE
# ============================================================================

def calculate_ats_score(state: ATSOptimizerState) -> Dict[str, Any]:
    """Match keywords and calculate weighted ATS score."""
    target_keywords = state.target_keywords
    resume_text = state.resume_text_full.lower()
    sections = state.resume_text_by_section
    
    if not target_keywords:
        return {"error_message": "No target keywords to match"}
    
    keywords_found = []
    keywords_missing = []
    keyword_locations = {}
    
    total_weight = sum(target_keywords.values())
    matched_weight = 0.0
    
    for keyword, weight in target_keywords.items():
        found = False
        locations = []
        
        # Check for exact match
        if keyword in resume_text:
            found = True
        else:
            # Check aliases
            aliases = SKILL_ALIASES.get(keyword, [keyword])
            for alias in aliases:
                if alias.lower() in resume_text:
                    found = True
                    break
        
        if found:
            keywords_found.append(keyword)
            matched_weight += weight
            
            for section_name, section_text in sections.items():
                section_lower = section_text.lower()
                if keyword in section_lower:
                    locations.append(section_name)
            
            keyword_locations[keyword] = locations
        else:
            keywords_missing.append(keyword)
    
    keyword_score = (matched_weight / total_weight * 100) if total_weight > 0 else 0
    
    # Section scores
    section_scores = {}
    for section_name, section_text in sections.items():
        section_lower = section_text.lower()
        section_found = sum(1 for kw in keywords_found if kw in section_lower)
        section_total = len(target_keywords)
        section_scores[section_name] = int((section_found / section_total) * 100) if section_total > 0 else 0
    
    keyword_density = len(keywords_found) / len(target_keywords) if target_keywords else 0
    
    print(f"  📊 Keyword Analysis:")
    print(f"     Found: {len(keywords_found)}/{len(target_keywords)} ({keyword_density*100:.1f}%)")
    print(f"     Weighted Score: {keyword_score:.1f}/100")
    if keywords_missing:
        print(f"     Missing: {', '.join(keywords_missing[:5])}")
    
    return {
        "keywords_found": keywords_found,
        "keywords_missing": keywords_missing,
        "keyword_locations": keyword_locations,
        "keyword_density": keyword_density,
        "section_scores": section_scores,
        "ats_score": int(keyword_score)
    }


# ============================================================================
# NODE 4: CHECK FORMAT ISSUES
# ============================================================================

def check_format_issues(state: ATSOptimizerState) -> Dict[str, Any]:
    """Check for ATS-unfriendly formatting issues."""
    resume = state.optimized_resume or state.resume_json
    
    issues = []
    format_score = 100
    
    header = resume.header or {}
    required_fields = ["name", "email", "phone"]
    missing_contact = [f for f in required_fields if not header.get(f)]
    if missing_contact:
        issues.append(f"Missing contact info: {', '.join(missing_contact)}")
        format_score -= 5
    
    action_verb_issues = check_action_verbs_in_bullets(resume)
    if action_verb_issues:
        issues.extend(action_verb_issues[:3])
        format_score -= 5
    
    pronouns = [" i ", " me ", " my ", " we ", " our "]
    text_lower = state.resume_text_full.lower()
    found_pronouns = [p.strip() for p in pronouns if p in text_lower]
    if found_pronouns:
        issues.append(f"Personal pronouns found: {', '.join(set(found_pronouns))}")
        format_score -= 3
    
    long_bullets = check_bullet_lengths(resume)
    if long_bullets:
        issues.append(f"{len(long_bullets)} bullets exceed recommended length")
        format_score -= 2
    
    stuffing_issues = check_keyword_stuffing(state.resume_text_full, state.target_keywords)
    if stuffing_issues:
        issues.extend(stuffing_issues)
        format_score -= 5
    
    format_score = max(0, format_score)
    
    print(f"  📋 Format Check: {format_score}/100")
    
    return {"format_issues": issues, "format_score": format_score}


def check_action_verbs_in_bullets(resume: ResumeJSON) -> List[str]:
    issues = []
    action_verbs = {
        "achieved", "administered", "analyzed", "applied", "architected",
        "built", "collaborated", "conducted", "created", "delivered",
        "designed", "developed", "directed", "drove", "enabled",
        "engineered", "established", "evaluated", "executed", "expanded",
        "grew", "identified", "implemented", "improved", "increased",
        "initiated", "integrated", "launched", "led", "managed",
        "mentored", "optimized", "orchestrated", "organized", "pioneered",
        "planned", "produced", "reduced", "resolved", "scaled",
        "secured", "spearheaded", "streamlined", "strengthened", "transformed",
        "authored", "investigated", "prototyped", "deployed", "automated"
    }
    
    for exp in (resume.experience or []):
        for bullet in exp.get("bullets", []):
            first_word = bullet.split()[0].lower().rstrip(",.:;") if bullet else ""
            if first_word and first_word not in action_verbs:
                issues.append(f"Bullet may not start with action verb: '{bullet[:50]}...'")
    return issues


def check_bullet_lengths(resume: ResumeJSON, max_length: int = 150) -> List[str]:
    long_bullets = []
    for exp in (resume.experience or []):
        for bullet in exp.get("bullets", []):
            if len(bullet) > max_length:
                long_bullets.append(bullet[:50])
    for proj in (resume.projects or []):
        for bullet in proj.get("bullets", []):
            if len(bullet) > max_length:
                long_bullets.append(bullet[:50])
    return long_bullets


def check_keyword_stuffing(text: str, keywords: Dict[str, float], max_occurrences: int = 4) -> List[str]:
    issues = []
    text_lower = text.lower()
    for keyword in keywords:
        count = text_lower.count(keyword)
        if count > max_occurrences:
            issues.append(f"Keyword '{keyword}' appears {count} times (max: {max_occurrences})")
    return issues


# ============================================================================
# NODE 5: GENERATE SUGGESTIONS
# ============================================================================

def generate_suggestions(state: ATSOptimizerState) -> Dict[str, Any]:
    """Generate suggestions - PRIORITIZE adding ALL missing keywords to skills."""
    
    if state.ats_score >= state.target_score:
        print(f"  ✅ Score {state.ats_score} >= target {state.target_score}")
        return {"suggestions": [], "passed": True}
    
    resume = state.optimized_resume or state.resume_json
    suggestions = []
    
    # =========================================================================
    # STEP 1: DIRECTLY ADD ALL MISSING KEYWORDS TO SKILLS
    # This is the most reliable way to improve ATS score
    # =========================================================================
    
    for keyword in state.keywords_missing:
        kw_lower = keyword.lower()
        
        # Determine category
        category = KEYWORD_CATEGORY_MAP.get(kw_lower)
        
        if category is None:
            # It's an action verb - add to summary instead
            suggestions.append({
                "keyword": keyword,
                "section": "summary",
                "action": "add_to_summary",
                "priority": "MEDIUM"
            })
        else:
            # It's a skill - add to skills section
            suggestions.append({
                "keyword": keyword,
                "section": "skills",
                "category": category,
                "action": "add_skill",
                "priority": "HIGH"
            })
            
            # ALSO add to projects if it's a technical skill
            if category in ["Programming Languages", "Tools & Platforms", "ML/AI & Data Science"]:
                suggestions.append({
                    "keyword": keyword,
                    "section": "projects",
                    "action": "add_to_project_tech",
                    "priority": "MEDIUM"
                })
    
    # =========================================================================
    # STEP 2: Also try LLM for experience bullet improvements
    # =========================================================================
    
    if state.keywords_missing:
        try:
            llm_suggestions = generate_llm_suggestions(state)
            suggestions.extend(llm_suggestions)
        except Exception as e:
            print(f"  ⚠️ LLM suggestions failed: {e}")
    
    print(f"  💡 Generated {len(suggestions)} total suggestions")
    print(f"     Skills additions: {sum(1 for s in suggestions if s.get('action') == 'add_skill')}")
    print(f"     Project additions: {sum(1 for s in suggestions if s.get('action') == 'add_to_project_tech')}")
    print(f"     Summary additions: {sum(1 for s in suggestions if s.get('action') == 'add_to_summary')}")
    
    return {"suggestions": suggestions}


def generate_llm_suggestions(state: ATSOptimizerState) -> List[Dict]:
    """Generate LLM-based suggestions for bullet modifications."""
    
    system_prompt = load_prompt("system_prompt.txt")
    suggestion_prompt = load_prompt("suggestion_generation_prompt.txt")
    few_shot = load_prompt("few_shot_examples.txt")
    
    resume = state.optimized_resume or state.resume_json
    
    # Prepare content
    exp_bullets = []
    for exp in (resume.experience or [])[:2]:
        exp_bullets.append(f"**{exp.get('role', '')} @ {exp.get('company', '')}**")
        for b in exp.get("bullets", [])[:3]:
            exp_bullets.append(f"- {b}")
    
    proj_bullets = []
    for proj in (resume.projects or []):
        proj_bullets.append(f"**{proj.get('name', '')}** | {proj.get('technologies', '')}")
        for b in proj.get("bullets", []):
            proj_bullets.append(f"- {b}")
    
    high_priority = [kw for kw in state.keywords_missing if state.target_keywords.get(kw, 1) >= 3]
    medium_priority = [kw for kw in state.keywords_missing if 2 <= state.target_keywords.get(kw, 1) < 3]
    low_priority = [kw for kw in state.keywords_missing if state.target_keywords.get(kw, 1) < 2]
    
    jd = state.structured_jd
    user_prompt = suggestion_prompt.format(
        company_name=jd.company_name if jd else "Target Company",
        role_title=jd.role_title if jd else "Target Role",
        current_score=state.ats_score,
        target_score=state.target_score,
        score_gap=state.target_score - state.ats_score,
        found_count=len(state.keywords_found),
        keywords_found=", ".join(state.keywords_found[:15]),
        missing_count=len(state.keywords_missing),
        high_priority_missing=", ".join(high_priority) or "None",
        medium_priority_missing=", ".join(medium_priority) or "None",
        low_priority_missing=", ".join(low_priority) or "None",
        current_summary=resume.summary or "",
        current_skills=json.dumps(resume.skills or {}, indent=2),
        current_experience_bullets="\n".join(exp_bullets),
        current_project_bullets="\n".join(proj_bullets),
        num_suggestions=min(5, len(state.keywords_missing))
    )
    
    llm = get_llm()
    messages = [
        SystemMessage(content=f"{system_prompt}\n\n{few_shot}"),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    return parse_suggestions(response.content)


def parse_suggestions(response: str) -> List[Dict[str, Any]]:
    """Parse LLM response to extract suggestions."""
    suggestions = []
    suggestion_blocks = re.split(r'SUGGESTION\s*\d+:', response, flags=re.IGNORECASE)
    
    for block in suggestion_blocks[1:]:
        keyword_match = re.search(r'KEYWORD:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        section_match = re.search(r'(?:TARGET_)?SECTION:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        original_match = re.search(r'ORIGINAL(?:_TEXT)?:\s*(.+?)(?=MODIFIED)', block, re.IGNORECASE | re.DOTALL)
        modified_match = re.search(r'MODIFIED(?:_TEXT)?:\s*(.+?)(?=WHY|RATIONALE|POINT|EXPECTED|\n\n|$)', block, re.IGNORECASE | re.DOTALL)
        
        if keyword_match and modified_match:
            modified_text = modified_match.group(1).strip().split('\n')[0].strip()
            suggestions.append({
                "keyword": keyword_match.group(1).strip(),
                "section": section_match.group(1).strip().lower() if section_match else "experience",
                "original": original_match.group(1).strip() if original_match else "",
                "modified": modified_text,
                "action": "modify"
            })
    
    return suggestions


# ============================================================================
# NODE 6: APPLY SUGGESTIONS - AGGRESSIVE SKILL INJECTION
# ============================================================================

def apply_suggestions(state: ATSOptimizerState) -> Dict[str, Any]:
    """Apply suggestions - AGGRESSIVELY add to skills section."""
    
    suggestions = state.suggestions
    resume = state.optimized_resume or state.resume_json
    
    if not suggestions:
        return {"optimized_resume": resume, "iteration": state.iteration + 1}
    
    optimized = deepcopy(resume)
    applied = []
    
    # =========================================================================
    # STEP 1: ADD ALL MISSING KEYWORDS TO SKILLS SECTION
    # =========================================================================
    
    for sugg in suggestions:
        if sugg.get("action") == "add_skill":
            keyword = sugg.get("keyword", "")
            target_category = sugg.get("category", "Core Expertise")
            
            if not keyword or not optimized.skills:
                continue
            
            # Check if keyword already exists in any skill category
            already_exists = False
            for cat, skills in optimized.skills.items():
                if keyword.lower() in skills.lower():
                    already_exists = True
                    break
            
            if already_exists:
                continue
            
            # Find best category to add the keyword
            best_cat = find_matching_category(optimized.skills, target_category)
            
            if best_cat:
                current = optimized.skills[best_cat]
                optimized.skills[best_cat] = f"{current}, {keyword}"
                applied.append(sugg)
                print(f"    ✓ SKILL: Added '{keyword}' → {best_cat}")
            else:
                # Create new category if needed
                if target_category not in optimized.skills:
                    optimized.skills[target_category] = keyword
                else:
                    optimized.skills[target_category] += f", {keyword}"
                applied.append(sugg)
                print(f"    ✓ SKILL: Added '{keyword}' → {target_category} (new)")
    
    # =========================================================================
    # STEP 2: ADD TO PROJECT TECHNOLOGIES
    # =========================================================================
    
    for sugg in suggestions:
        if sugg.get("action") == "add_to_project_tech":
            keyword = sugg.get("keyword", "")
            
            if keyword and optimized.projects:
                # Add to first project that doesn't have it
                for proj in optimized.projects:
                    tech = proj.get("technologies", "")
                    if keyword.lower() not in tech.lower():
                        proj["technologies"] = f"{tech}, {keyword}" if tech else keyword
                        applied.append(sugg)
                        print(f"    ✓ PROJECT: Added '{keyword}' → {proj.get('name', '')[:30]}")
                        break
    
    # =========================================================================
    # STEP 3: ADD TO SUMMARY
    # =========================================================================
    
    for sugg in suggestions:
        if sugg.get("action") == "add_to_summary":
            keyword = sugg.get("keyword", "")
            
            if keyword and optimized.summary and keyword.lower() not in optimized.summary.lower():
                # Add keyword naturally to summary
                optimized.summary = optimized.summary.rstrip(".") + f", with expertise in {keyword}."
                applied.append(sugg)
                print(f"    ✓ SUMMARY: Added '{keyword}'")
    
    # =========================================================================
    # STEP 4: APPLY LLM BULLET MODIFICATIONS
    # =========================================================================
    
    for sugg in suggestions:
        if sugg.get("action") == "modify" and sugg.get("section") == "experience":
            original = sugg.get("original", "").strip()
            modified = sugg.get("modified", "").strip()
            
            if modified and original and len(modified) > 20:
                for exp in optimized.experience:
                    bullets = exp.get("bullets", [])
                    for i, bullet in enumerate(bullets):
                        if original[:25].lower() in bullet.lower():
                            bullets[i] = modified
                            applied.append(sugg)
                            print(f"    ✓ EXP BULLET: Modified")
                            break
                    exp["bullets"] = bullets
    
    print(f"  ✏️ Applied {len(applied)}/{len(suggestions)} suggestions")
    
    return {
        "optimized_resume": optimized,
        "resume_json": optimized,
        "applied_suggestions": applied,
        "iteration": state.iteration + 1
    }


def find_matching_category(skills: Dict[str, str], target: str) -> str:
    """Find the best matching skill category."""
    target_lower = target.lower()
    
    # Direct match
    for cat in skills:
        if target_lower in cat.lower() or cat.lower() in target_lower:
            return cat
    
    # Keyword-based matching
    matches = {
        "programming": ["programming", "language", "code"],
        "ml": ["ml", "ai", "machine", "learning", "data"],
        "core": ["core", "expertise", "fundamental", "computer science"],
        "tools": ["tool", "platform", "infrastructure", "devops"],
    }
    
    for cat in skills:
        cat_lower = cat.lower()
        for key, keywords in matches.items():
            if any(kw in cat_lower for kw in keywords):
                if any(kw in target_lower for kw in keywords):
                    return cat
    
    # Return first category as fallback
    return list(skills.keys())[0] if skills else None


# ============================================================================
# NODE 7: FINALIZE ANALYSIS
# ============================================================================

def finalize_analysis(state: ATSOptimizerState) -> Dict[str, Any]:
    """Create final ATSAnalysis object."""
    
    final_score = int(state.ats_score * 0.85 + state.format_score * 0.15)
    passed = final_score >= state.target_score
    
    analysis = ATSAnalysis(
        score=final_score,
        keyword_density=state.keyword_density,
        keywords_found=state.keywords_found,
        keywords_missing=state.keywords_missing,
        format_issues=state.format_issues,
        section_scores=state.section_scores,
        suggestions=[],
        passed=passed
    )
    
    print(f"  📊 Final ATS Score: {final_score}/100")
    print(f"     Status: {'✅ PASSED' if passed else '⚠️ Below target'}")
    
    return {
        "ats_analysis": analysis,
        "ats_score": final_score,
        "passed": passed,
        "optimization_complete": True
    }


# ============================================================================
# ROUTING
# ============================================================================

def should_continue_optimization(state: ATSOptimizerState) -> str:
    """Determine if optimization should continue."""
    if state.ats_score >= state.target_score:
        return "finalize"
    if state.iteration >= state.max_iterations:
        return "finalize"
    if not state.suggestions:
        return "finalize"
    return "apply"


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "extract_jd_keywords",
    "scan_resume_content", 
    "calculate_ats_score",
    "check_format_issues",
    "generate_suggestions",
    "apply_suggestions",
    "finalize_analysis",
    "should_continue_optimization",
    "get_llm",
    "load_prompt",
    "parse_suggestions"
]
