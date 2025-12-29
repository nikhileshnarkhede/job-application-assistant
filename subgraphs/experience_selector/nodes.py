"""
Experience Selector Nodes

This module contains all node definitions for the Experience Selector subgraph:
1. load_experiences - Load candidate experiences from candidate_loader
2. extract_jd_requirements - Extract skills/keywords/responsibilities from JD
3. score_experiences - Score each experience by relevance
4. select_top_experiences - Select top N experiences
5. prepare_for_rewriting - Format selected experiences with bullets

Node Flow:
    START → load_experiences → extract_jd_requirements → score_experiences → select_top_experiences → prepare_for_rewriting → END
"""

import os
from typing import Dict, Any, List, Set
from pathlib import Path
from difflib import SequenceMatcher

# State imports
from subgraphs.experience_selector.state import (
    ExperienceSelectorState,
    SCORING_WEIGHTS,
    TIER_SCORES,
    RECENCY_SCORES
)
from state.state_models import SelectedExperience


# ============================================================================
# NODE 1: LOAD EXPERIENCES
# ============================================================================

def load_experiences(state: ExperienceSelectorState) -> Dict[str, Any]:
    """
    Load candidate experiences from candidate_loader.
    
    Returns:
        Updated state with all_experiences and relevance_mapping
    """
    try:
        from mcp_server.tools.candidate_loader import (
            get_all_experiences,
            load_candidate_data
        )
        
        experiences = get_all_experiences()
        
        if not experiences:
            return {
                "all_experiences": [],
                "error_message": "No candidate experiences found"
            }
        
        # Also load relevance mapping
        data = load_candidate_data()
        relevance_mapping = data.get("relevance_mapping", {})
        
        print(f"  📂 Loaded {len(experiences)} experiences")
        
        return {
            "all_experiences": experiences,
            "relevance_mapping": relevance_mapping
        }
        
    except Exception as e:
        return {
            "all_experiences": [],
            "error_message": f"Failed to load experiences: {str(e)}"
        }


# ============================================================================
# NODE 2: EXTRACT JD REQUIREMENTS
# ============================================================================

def extract_jd_requirements(state: ExperienceSelectorState) -> Dict[str, Any]:
    """
    Extract skills, keywords, and responsibilities from structured JD.
    
    Returns:
        Updated state with jd_skills, jd_keywords, jd_responsibilities, role_type
    """
    jd = state.structured_jd
    
    if not jd:
        return {
            "error_message": "No structured JD provided",
            "selection_complete": True
        }
    
    # Combine required and preferred skills
    jd_skills = list(set((jd.skills_required or []) + (jd.skills_preferred or [])))
    
    # Get keywords
    jd_keywords = jd.keywords or []
    
    # Get responsibilities
    jd_responsibilities = jd.responsibilities or []
    
    # Get role type
    role_type = jd.role_type or "ml_ai"
    
    print(f"  📋 JD: {len(jd_skills)} skills, {len(jd_keywords)} keywords, {len(jd_responsibilities)} responsibilities")
    
    return {
        "jd_skills": jd_skills,
        "jd_keywords": jd_keywords,
        "jd_responsibilities": jd_responsibilities,
        "role_type": role_type
    }


# ============================================================================
# NODE 3: SCORE EXPERIENCES
# ============================================================================

def calculate_skill_match(experience: Dict, jd_skills: Set[str]) -> float:
    """Calculate skill match score."""
    exp_skills = set()
    
    for skill in experience.get("skills", []):
        exp_skills.add(skill.lower())
    
    if not jd_skills:
        return 0.0
    
    overlap = len(exp_skills & jd_skills)
    return min(overlap / len(jd_skills), 1.0)


def calculate_keyword_match(experience: Dict, jd_keywords: Set[str]) -> float:
    """Calculate keyword match score."""
    exp_keywords = set()
    
    # Add explicit keywords
    for kw in experience.get("keywords", []):
        exp_keywords.add(kw.lower())
    
    # Add from bullets
    bullets_text = " ".join(experience.get("bullets_flat", [])).lower()
    for kw in jd_keywords:
        if kw in bullets_text:
            exp_keywords.add(kw)
    
    if not jd_keywords:
        return 0.0
    
    overlap = len(exp_keywords & jd_keywords)
    return min(overlap / len(jd_keywords), 1.0)


def calculate_responsibility_match(experience: Dict, jd_responsibilities: List[str]) -> float:
    """
    Calculate how well experience bullets match JD responsibilities.
    Uses fuzzy matching.
    """
    if not jd_responsibilities:
        return 0.5  # Neutral if no responsibilities listed
    
    bullets = experience.get("bullets_flat", [])
    if not bullets:
        return 0.0
    
    total_match = 0.0
    
    for resp in jd_responsibilities:
        resp_lower = resp.lower()
        best_match = 0.0
        
        for bullet in bullets:
            bullet_lower = bullet.lower()
            
            # Check for keyword overlap
            resp_words = set(resp_lower.split())
            bullet_words = set(bullet_lower.split())
            
            # Remove common words
            common_words = {"and", "the", "a", "an", "to", "for", "with", "in", "on", "of"}
            resp_words -= common_words
            bullet_words -= common_words
            
            if resp_words:
                word_overlap = len(resp_words & bullet_words) / len(resp_words)
                best_match = max(best_match, word_overlap)
        
        total_match += best_match
    
    return min(total_match / len(jd_responsibilities), 1.0)


def get_tier_score(exp_id: int, role_type: str, relevance_mapping: Dict) -> float:
    """Get tier score based on relevance mapping."""
    # Normalize role type
    role_key = role_type.lower().replace(" ", "_").replace("-", "_")
    
    # Find matching role in mapping
    mapping = None
    if role_key in relevance_mapping:
        mapping = relevance_mapping[role_key]
    else:
        # Try fuzzy match
        for key in relevance_mapping:
            if role_key in key or key in role_key:
                mapping = relevance_mapping[key]
                break
    
    if not mapping:
        # Default to ml_ai
        mapping = relevance_mapping.get("ml_ai", {})
    
    # Check tiers
    if exp_id in mapping.get("primary", []):
        return TIER_SCORES["primary"]
    elif exp_id in mapping.get("secondary", []):
        return TIER_SCORES["secondary"]
    elif exp_id in mapping.get("supporting", []):
        return TIER_SCORES["supporting"]
    else:
        return TIER_SCORES["other"]


def get_recency_score(exp_id: int) -> float:
    """Get recency score based on experience ID (lower = more recent)."""
    return RECENCY_SCORES.get(exp_id, 0.1)


def score_experiences(state: ExperienceSelectorState) -> Dict[str, Any]:
    """
    Score each experience by relevance to JD.
    
    Uses weighted scoring:
    - Skill match: 30%
    - Keyword match: 25%
    - Responsibility match: 20%
    - Relevance tier: 15%
    - Recency: 10%
    
    Returns:
        Updated state with scored experiences
    """
    experiences = state.all_experiences
    jd_skills = set(s.lower() for s in state.jd_skills)
    jd_keywords = set(k.lower() for k in state.jd_keywords)
    jd_responsibilities = state.jd_responsibilities
    role_type = state.role_type
    relevance_mapping = state.relevance_mapping
    
    if not experiences:
        return {"error_message": "No experiences to score"}
    
    scored_experiences = []
    
    for exp in experiences:
        exp_id = exp.get("id", 0)
        
        # Calculate component scores
        skill_score = calculate_skill_match(exp, jd_skills)
        keyword_score = calculate_keyword_match(exp, jd_keywords)
        resp_score = calculate_responsibility_match(exp, jd_responsibilities)
        tier_score = get_tier_score(exp_id, role_type, relevance_mapping)
        recency_score = get_recency_score(exp_id)
        
        # Calculate weighted total
        total_score = (
            skill_score * SCORING_WEIGHTS["skill_match"] +
            keyword_score * SCORING_WEIGHTS["keyword_match"] +
            resp_score * SCORING_WEIGHTS["responsibility_match"] +
            tier_score * SCORING_WEIGHTS["relevance_tier"] +
            recency_score * SCORING_WEIGHTS["recency_bonus"]
        )
        
        # Scale to 100
        final_score = round(total_score * 100, 2)
        
        # Add score to experience
        exp["relevance_score"] = final_score
        exp["score_breakdown"] = {
            "skill_match": round(skill_score * 100, 1),
            "keyword_match": round(keyword_score * 100, 1),
            "responsibility_match": round(resp_score * 100, 1),
            "tier": tier_score,
            "recency": recency_score
        }
        
        # Find matching keywords for later use
        exp_keywords = set(k.lower() for k in exp.get("keywords", []))
        exp_skills = set(s.lower() for s in exp.get("skills", []))
        matching = list((exp_keywords | exp_skills) & (jd_keywords | jd_skills))
        exp["matching_keywords"] = matching
        
        scored_experiences.append(exp)
    
    # Sort by score descending
    scored_experiences.sort(key=lambda e: e.get("relevance_score", 0), reverse=True)
    
    return {"all_experiences": scored_experiences}


# ============================================================================
# NODE 4: SELECT TOP EXPERIENCES
# ============================================================================

def select_top_experiences(state: ExperienceSelectorState) -> Dict[str, Any]:
    """
    Select top N experiences based on scores.
    
    Returns:
        Updated state with selected_experiences
    """
    experiences = state.all_experiences
    max_experiences = state.max_experiences or 4
    
    if not experiences:
        return {
            "selected_experiences": [],
            "error_message": "No scored experiences available"
        }
    
    # Take top N
    top_experiences = experiences[:max_experiences]
    
    # Convert to SelectedExperience objects
    selected = []
    
    for exp in top_experiences:
        # Build location dict
        location = {}
        if exp.get("location"):
            if isinstance(exp["location"], dict):
                location = exp["location"]
            elif isinstance(exp["location"], str):
                location = {"full": exp["location"]}
        
        # Build dates dict
        dates = {}
        if exp.get("dates"):
            if isinstance(exp["dates"], dict):
                dates = exp["dates"]
        if exp.get("duration"):
            dates["duration"] = exp["duration"]
        
        selected_exp = SelectedExperience(
            id=exp.get("id", 0),
            role=exp.get("role", ""),
            role_full=exp.get("role_full", exp.get("role", "")),
            company=exp.get("company", ""),
            employment_type=exp.get("employment_type", ""),
            dates=dates,
            location=location,
            relevance_score=exp.get("relevance_score", 0),
            matching_keywords=exp.get("matching_keywords", []),
            original_bullets=exp.get("bullets_flat", []),
            rewritten_bullets=[],  # Will be filled by Experience Rewriter
            keywords_incorporated=[],
            publication=exp.get("publication"),
            project=exp.get("project"),
            scope=exp.get("scope", "")
        )
        
        selected.append(selected_exp)
    
    return {"selected_experiences": selected}


# ============================================================================
# NODE 5: PREPARE FOR REWRITING
# ============================================================================

def prepare_for_rewriting(state: ExperienceSelectorState) -> Dict[str, Any]:
    """
    Finalize selected experiences and prepare for rewriting stage.
    
    This node:
    1. Ensures all required fields are populated
    2. Sorts bullets by relevance within each experience
    3. Marks selection as complete
    
    Returns:
        Updated state with finalized selected_experiences
    """
    selected = state.selected_experiences
    
    if not selected:
        return {
            "selection_complete": True,
            "error_message": "No experiences selected"
        }
    
    # Get JD keywords for bullet prioritization
    jd_keywords = set(k.lower() for k in state.jd_keywords)
    jd_skills = set(s.lower() for s in state.jd_skills)
    all_jd_terms = jd_keywords | jd_skills
    
    updated_experiences = []
    
    for exp in selected:
        # Sort bullets by relevance (those containing JD keywords first)
        original_bullets = exp.original_bullets
        
        def bullet_relevance(bullet: str) -> int:
            bullet_lower = bullet.lower()
            score = 0
            for term in all_jd_terms:
                if term in bullet_lower:
                    score += 1
            return score
        
        sorted_bullets = sorted(original_bullets, key=bullet_relevance, reverse=True)
        
        # Update experience with sorted bullets
        exp.original_bullets = sorted_bullets
        
        updated_experiences.append(exp)
    
    return {
        "selected_experiences": updated_experiences,
        "selection_complete": True
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Nodes
    "load_experiences",
    "extract_jd_requirements",
    "score_experiences",
    "select_top_experiences",
    "prepare_for_rewriting",
    
    # Utilities
    "calculate_skill_match",
    "calculate_keyword_match",
    "calculate_responsibility_match",
    "get_tier_score",
    "get_recency_score"
]
