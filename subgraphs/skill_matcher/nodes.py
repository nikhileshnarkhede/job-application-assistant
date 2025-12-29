"""
Skill Matcher Nodes

This module contains all node definitions for the Skill Matcher subgraph:
1. load_candidate_skills - Load skills from candidate data
2. extract_jd_skills - Extract skills from structured JD
3. match_skills - Perform skill matching algorithm
4. analyze_gaps - Generate gap analysis using LLM (optional)
5. build_result - Build final SkillMatchResult

Node Flow:
    START → load_candidate_skills → extract_jd_skills → match_skills → analyze_gaps → build_result → END
"""

import os
import re
from typing import Dict, Any, List, Set, Tuple
from difflib import SequenceMatcher

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# State imports
from subgraphs.skill_matcher.state import (
    SkillMatcherState,
    normalize_skill,
    normalize_skills_list,
    SKILL_REVERSE_MAP
)
from state.state_models import SkillMatchResult


# ============================================================================
# CONFIGURATION
# ============================================================================

# Minimum similarity score for fuzzy matching (0.0 - 1.0)
FUZZY_MATCH_THRESHOLD = 0.75

# Skills that should always be highlighted as critical if missing
CRITICAL_SKILL_PATTERNS = [
    "python", "sql", "machine learning", "deep learning",
    "tensorflow", "pytorch", "data science"
]


def get_llm():
    """Get configured LLM instance."""
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY")
    )


def load_prompt(filename: str) -> str:
    """Load prompt from file."""
    prompt_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(prompt_dir, "prompts", filename)
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


# ============================================================================
# NODE 1: LOAD CANDIDATE SKILLS
# ============================================================================

def load_candidate_skills(state: SkillMatcherState) -> Dict[str, Any]:
    """
    Load candidate skills from data files.
    
    If skills are already in state (passed from parent), use those.
    Otherwise, load from candidate_loader.
    
    Returns:
        Updated state dict with candidate skills
    """
    # If skills already provided in state, use them
    if state.candidate_skills_flat and len(state.candidate_skills_flat) > 0:
        return {
            "candidate_skills_normalized": normalize_skills_list(state.candidate_skills_flat),
            "candidate_keywords": state.candidate_keywords or []
        }
    
    # Load from candidate_loader
    try:
        from mcp_server.tools.candidate_loader import (
            get_all_candidate_skills,
            get_all_candidate_keywords
        )
        
        skills = get_all_candidate_skills()
        keywords = get_all_candidate_keywords()
        
        return {
            "candidate_skills_flat": skills,
            "candidate_skills_normalized": normalize_skills_list(skills),
            "candidate_keywords": keywords
        }
        
    except ImportError as e:
        # Fallback: return empty with error
        return {
            "candidate_skills_flat": [],
            "candidate_skills_normalized": [],
            "candidate_keywords": [],
            "error_message": f"Could not load candidate skills: {str(e)}"
        }


# ============================================================================
# NODE 2: EXTRACT JD SKILLS
# ============================================================================

def extract_jd_skills(state: SkillMatcherState) -> Dict[str, Any]:
    """
    Extract and normalize skills from structured JD.
    
    Returns:
        Updated state dict with JD skills
    """
    jd = state.structured_jd
    
    if not jd:
        return {
            "error_message": "No structured JD provided",
            "matching_complete": True
        }
    
    # Extract skills from JD
    skills_required = jd.skills_required or []
    skills_preferred = jd.skills_preferred or []
    keywords = jd.keywords or []
    
    # Combine all JD skills for matching
    all_jd_skills = list(set(skills_required + skills_preferred))
    
    return {
        "jd_skills_required": skills_required,
        "jd_skills_preferred": skills_preferred,
        "jd_keywords": keywords,
        "jd_skills_normalized": normalize_skills_list(all_jd_skills)
    }


# ============================================================================
# NODE 3: MATCH SKILLS
# ============================================================================

def calculate_similarity(skill1: str, skill2: str) -> float:
    """Calculate similarity between two skill strings."""
    # Normalize for comparison
    s1 = skill1.lower().strip()
    s2 = skill2.lower().strip()
    
    # Exact match
    if s1 == s2:
        return 1.0
    
    # Check if one contains the other
    if s1 in s2 or s2 in s1:
        return 0.9
    
    # Fuzzy match using SequenceMatcher
    return SequenceMatcher(None, s1, s2).ratio()


def find_best_match(skill: str, candidate_skills: List[str]) -> Tuple[str, float]:
    """
    Find the best matching candidate skill for a JD skill.
    
    Returns:
        Tuple of (matched_skill, similarity_score)
    """
    best_match = None
    best_score = 0.0
    
    skill_lower = skill.lower().strip()
    
    # First check canonical mapping
    canonical = SKILL_REVERSE_MAP.get(skill_lower)
    if canonical:
        for cand in candidate_skills:
            if cand.lower() == canonical.lower():
                return (cand, 1.0)
    
    # Then check each candidate skill
    for cand in candidate_skills:
        score = calculate_similarity(skill, cand)
        if score > best_score:
            best_score = score
            best_match = cand
    
    return (best_match, best_score)


def match_skills(state: SkillMatcherState) -> Dict[str, Any]:
    """
    Perform skill matching between JD and candidate.
    
    Matching strategy:
    1. Exact match (case-insensitive)
    2. Canonical match (using alias mapping)
    3. Fuzzy match (using string similarity)
    
    Returns:
        Updated state dict with match results
    """
    jd_required = state.jd_skills_required or []
    jd_preferred = state.jd_skills_preferred or []
    jd_keywords = state.jd_keywords or []
    
    candidate_skills = state.candidate_skills_normalized or []
    candidate_keywords = state.candidate_keywords or []
    
    # Combine candidate skills and keywords for matching
    all_candidate = list(set(candidate_skills + candidate_keywords))
    all_candidate_lower = {s.lower() for s in all_candidate}
    
    matched_skills = []
    missing_skills = []
    partial_matches = []
    critical_missing = []
    
    # Match required skills
    for skill in jd_required:
        match, score = find_best_match(skill, all_candidate)
        
        if score >= 1.0:
            # Exact match
            matched_skills.append(skill)
        elif score >= FUZZY_MATCH_THRESHOLD:
            # Partial match
            partial_matches.append(f"{skill} (≈ {match})")
            matched_skills.append(skill)  # Count as matched
        else:
            # No match
            missing_skills.append(skill)
            
            # Check if it's a critical skill
            for pattern in CRITICAL_SKILL_PATTERNS:
                if pattern in skill.lower():
                    critical_missing.append(skill)
                    break
    
    # Match preferred skills
    for skill in jd_preferred:
        match, score = find_best_match(skill, all_candidate)
        
        if score >= FUZZY_MATCH_THRESHOLD:
            if skill not in matched_skills:
                matched_skills.append(skill)
                if score < 1.0:
                    partial_matches.append(f"{skill} (≈ {match})")
        else:
            if skill not in missing_skills:
                missing_skills.append(skill)
    
    # Find additional candidate skills not in JD
    jd_all_lower = {s.lower() for s in jd_required + jd_preferred}
    additional_skills = []
    
    for skill in candidate_skills:
        if skill.lower() not in jd_all_lower:
            # Check if it's not a close match to any JD skill
            is_match = False
            for jd_skill in jd_required + jd_preferred:
                if calculate_similarity(skill, jd_skill) >= FUZZY_MATCH_THRESHOLD:
                    is_match = True
                    break
            
            if not is_match:
                additional_skills.append(skill)
    
    # Calculate match percentage
    total_jd_skills = len(set(jd_required + jd_preferred))
    if total_jd_skills > 0:
        match_percentage = (len(matched_skills) / total_jd_skills) * 100
    else:
        match_percentage = 100.0 if not jd_required else 0.0
    
    # Build result
    result = SkillMatchResult(
        matched_skills=list(set(matched_skills)),
        missing_skills=list(set(missing_skills)),
        partial_matches=list(set(partial_matches)),
        additional_skills=additional_skills[:15],  # Limit to top 15
        match_percentage=round(match_percentage, 1),
        skill_gap_analysis="",  # Will be filled by analyze_gaps
        critical_missing=list(set(critical_missing))
    )
    
    return {
        "skill_match_result": result
    }


# ============================================================================
# NODE 4: ANALYZE GAPS (Optional LLM)
# ============================================================================

def analyze_gaps(state: SkillMatcherState) -> Dict[str, Any]:
    """
    Generate skill gap analysis using LLM.
    
    This provides:
    - Summary of skill alignment
    - Recommendations for highlighting transferable skills
    - Suggestions for addressing gaps
    
    Returns:
        Updated state dict with gap analysis
    """
    result = state.skill_match_result
    
    if not result:
        return {"error_message": "No skill match result to analyze"}
    
    # Skip LLM if match is very high
    if result.match_percentage >= 90 and len(result.critical_missing) == 0:
        analysis = (
            f"Excellent skill match ({result.match_percentage:.0f}%). "
            f"Candidate has {len(result.matched_skills)} matching skills. "
            "Resume should highlight these directly matching skills."
        )
        
        result.skill_gap_analysis = analysis
        return {"skill_match_result": result}
    
    # Use LLM for gap analysis
    try:
        system_prompt = load_prompt("system_prompt.txt")
        
        user_message = f"""
Analyze this skill matching result and provide a brief gap analysis:

## JD Required Skills:
{', '.join(state.jd_skills_required)}

## JD Preferred Skills:
{', '.join(state.jd_skills_preferred)}

## Candidate Matched Skills:
{', '.join(result.matched_skills)}

## Missing Skills:
{', '.join(result.missing_skills)}

## Critical Missing:
{', '.join(result.critical_missing) if result.critical_missing else 'None'}

## Additional Candidate Skills:
{', '.join(result.additional_skills[:10])}

## Match Percentage: {result.match_percentage:.1f}%

Provide a 2-3 sentence analysis focusing on:
1. Overall alignment assessment
2. Key gaps to address (if any)
3. Transferable skills to highlight
"""
        
        llm = get_llm()
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = llm.invoke(messages)
        analysis = response.content.strip()
        
        result.skill_gap_analysis = analysis
        
        return {"skill_match_result": result}
        
    except Exception as e:
        # Fallback to basic analysis
        analysis = (
            f"Skill match: {result.match_percentage:.0f}%. "
            f"Matched: {len(result.matched_skills)}, Missing: {len(result.missing_skills)}. "
            f"Critical gaps: {', '.join(result.critical_missing) if result.critical_missing else 'None'}."
        )
        
        result.skill_gap_analysis = analysis
        
        return {"skill_match_result": result}


# ============================================================================
# NODE 5: BUILD RESULT
# ============================================================================

def build_result(state: SkillMatcherState) -> Dict[str, Any]:
    """
    Finalize and validate the skill match result.
    
    Returns:
        Updated state dict with final result
    """
    result = state.skill_match_result
    
    if not result:
        return {
            "matching_complete": True,
            "error_message": "No skill match result generated"
        }
    
    # Ensure all lists are properly set
    if not result.matched_skills:
        result.matched_skills = []
    if not result.missing_skills:
        result.missing_skills = []
    if not result.partial_matches:
        result.partial_matches = []
    if not result.additional_skills:
        result.additional_skills = []
    
    return {
        "skill_match_result": result,
        "matching_complete": True,
        "error_message": None
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Nodes
    "load_candidate_skills",
    "extract_jd_skills",
    "match_skills",
    "analyze_gaps",
    "build_result",
    
    # Utilities
    "calculate_similarity",
    "find_best_match",
    "get_llm",
    "load_prompt"
]
