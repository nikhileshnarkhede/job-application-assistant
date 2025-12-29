"""
Experience Rewriter Nodes

This module contains all node definitions for the Experience Rewriter subgraph:
1. load_resources - Load action verbs from resources
2. prepare_keywords - Combine and prioritize target keywords
3. rewrite_experiences - Rewrite experience bullets with LLM
4. rewrite_projects - Rewrite project bullets with LLM
5. validate_rewrites - Validate keyword incorporation and quality

Node Flow:
    START → load_resources → prepare_keywords → rewrite_experiences → rewrite_projects → validate_rewrites → END
"""

import os
import re
from typing import Dict, Any, List, Set
from pathlib import Path
from copy import deepcopy

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
from subgraphs.experience_rewriter.state import (
    ExperienceRewriterState,
    DEFAULT_ACTION_VERBS,
    METRIC_TEMPLATES,
    METRIC_RANGES
)
from state.state_models import SelectedExperience, SelectedProject


# ============================================================================
# CONFIGURATION
# ============================================================================

def get_llm():
    """Get configured LLM instance."""
    # Prefer Claude for better writing quality (if available)
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
# NODE 1: LOAD RESOURCES
# ============================================================================

def load_resources(state: ExperienceRewriterState) -> Dict[str, Any]:
    """
    Load action verbs and other resources.
    
    Returns:
        Updated state with action_verbs
    """
    action_verbs = {}
    
    try:
        from mcp_server.tools.resource_loader import get_action_verbs
        action_verbs = get_action_verbs()
        print(f"  📚 Loaded {sum(len(v) for v in action_verbs.values())} action verbs")
    except Exception as e:
        print(f"  ⚠️ Using default action verbs: {e}")
        action_verbs = DEFAULT_ACTION_VERBS
    
    return {"action_verbs": action_verbs}


# ============================================================================
# NODE 2: PREPARE KEYWORDS
# ============================================================================

def prepare_keywords(state: ExperienceRewriterState) -> Dict[str, Any]:
    """
    Extract and prioritize target keywords from JD.
    
    Returns:
        Updated state with jd_skills, jd_keywords, target_keywords
    """
    jd = state.structured_jd
    
    if not jd:
        return {
            "error_message": "No structured JD provided",
            "rewrite_complete": True
        }
    
    # Extract skills and keywords
    jd_skills = list(set((jd.skills_required or []) + (jd.skills_preferred or [])))
    jd_keywords = jd.keywords or []
    
    # Combine and prioritize (required skills first, then preferred, then keywords)
    target_keywords = []
    seen = set()
    
    # Priority 1: Required skills
    for skill in (jd.skills_required or []):
        skill_lower = skill.lower()
        if skill_lower not in seen:
            target_keywords.append(skill)
            seen.add(skill_lower)
    
    # Priority 2: Preferred skills
    for skill in (jd.skills_preferred or []):
        skill_lower = skill.lower()
        if skill_lower not in seen:
            target_keywords.append(skill)
            seen.add(skill_lower)
    
    # Priority 3: Keywords
    for kw in jd_keywords:
        kw_lower = kw.lower()
        if kw_lower not in seen:
            target_keywords.append(kw)
            seen.add(kw_lower)
    
    print(f"  🎯 Target keywords: {len(target_keywords)} (top: {', '.join(target_keywords[:8])})")
    
    return {
        "jd_skills": jd_skills,
        "jd_keywords": jd_keywords,
        "target_keywords": target_keywords
    }


# ============================================================================
# NODE 3: REWRITE EXPERIENCES
# ============================================================================

def rewrite_experiences(state: ExperienceRewriterState) -> Dict[str, Any]:
    """
    Rewrite experience bullets using LLM.
    
    Each bullet is rewritten to:
    - Start with action verb
    - Include quantifiable metrics
    - Incorporate target keywords
    
    Returns:
        Updated state with rewritten_experiences
    """
    experiences = state.selected_experiences
    
    if not experiences:
        return {"rewritten_experiences": []}
    
    jd = state.structured_jd
    target_keywords = state.target_keywords
    action_verbs = state.action_verbs
    
    # Load prompts
    system_prompt = load_prompt("system_prompt.txt")
    rewrite_template = load_prompt("experience_rewrite_prompt.txt")
    few_shot = load_prompt("few_shot_examples.txt")
    
    # Combine system prompt with few-shot examples
    full_system = f"{system_prompt}\n\n{few_shot}"
    
    llm = get_llm()
    rewritten = []
    all_keywords_used = []
    
    for exp in experiences:
        print(f"  ✍️ Rewriting: {exp.role} @ {exp.company}")
        
        # Format original bullets
        original_bullets_text = "\n".join([f"- {b}" for b in exp.original_bullets[:6]])
        
        # Format prompt
        user_prompt = rewrite_template.format(
            company_name=jd.company_name if jd else "Target Company",
            role_title=jd.role_title if jd else "Target Role",
            role_type=jd.role_type if jd else "ml_ai",
            target_keywords=", ".join(target_keywords[:20]),
            experience_role=exp.role,
            experience_company=exp.company,
            matching_keywords=", ".join(exp.matching_keywords[:10]),
            original_bullets=original_bullets_text
        )
        
        try:
            messages = [
                SystemMessage(content=full_system),
                HumanMessage(content=user_prompt)
            ]
            
            response = llm.invoke(messages)
            response_text = response.content
            
            # Parse response
            rewritten_bullets, keywords_used = parse_rewrite_response(response_text)
            
            # Update experience
            exp_copy = deepcopy(exp)
            exp_copy.rewritten_bullets = rewritten_bullets if rewritten_bullets else exp.original_bullets
            exp_copy.keywords_incorporated = keywords_used
            
            rewritten.append(exp_copy)
            all_keywords_used.extend(keywords_used)
            
            print(f"    ✅ Rewrote {len(rewritten_bullets)} bullets, used {len(keywords_used)} keywords")
            
        except Exception as e:
            print(f"    ⚠️ Rewrite failed: {e}, keeping original")
            exp_copy = deepcopy(exp)
            exp_copy.rewritten_bullets = exp.original_bullets
            rewritten.append(exp_copy)
    
    return {
        "rewritten_experiences": rewritten,
        "keywords_incorporated": list(set(all_keywords_used))
    }


def parse_rewrite_response(response: str) -> tuple:
    """Parse LLM response to extract bullets and keywords."""
    rewritten_bullets = []
    keywords_used = []
    
    lines = response.strip().split("\n")
    in_bullets_section = False
    in_keywords_section = False
    
    for line in lines:
        line = line.strip()
        
        if "REWRITTEN_BULLETS:" in line.upper():
            in_bullets_section = True
            in_keywords_section = False
            continue
        
        if "KEYWORDS_USED:" in line.upper() or "KEYWORDS USED:" in line.upper():
            in_bullets_section = False
            in_keywords_section = True
            continue
        
        if in_bullets_section and line:
            # Clean bullet
            bullet = line.lstrip("- •*").strip()
            if bullet and len(bullet) > 10:
                # Remove trailing period if present
                bullet = bullet.rstrip(".")
                rewritten_bullets.append(bullet)
        
        if in_keywords_section and line:
            # Parse comma-separated keywords
            kw_line = line.lstrip("- •*").strip()
            for kw in kw_line.split(","):
                kw = kw.strip()
                if kw:
                    keywords_used.append(kw)
    
    return rewritten_bullets, keywords_used


# ============================================================================
# NODE 4: REWRITE PROJECTS
# ============================================================================

def rewrite_projects(state: ExperienceRewriterState) -> Dict[str, Any]:
    """
    Rewrite project bullets using LLM.
    
    Returns:
        Updated state with rewritten_projects
    """
    projects = state.selected_projects
    
    if not projects:
        return {"rewritten_projects": []}
    
    jd = state.structured_jd
    target_keywords = state.target_keywords
    
    # Load prompts
    system_prompt = load_prompt("system_prompt.txt")
    project_template = load_prompt("project_rewrite_prompt.txt")
    
    llm = get_llm()
    rewritten = []
    all_keywords_used = list(state.keywords_incorporated)
    
    for proj in projects:
        print(f"  ✍️ Rewriting project: {proj.name}")
        
        # Get original bullets (use bullets field or generate from description)
        original_bullets = proj.bullets if proj.bullets else [proj.description[:150]]
        original_bullets_text = "\n".join([f"- {b}" for b in original_bullets[:4]])
        
        # Format tech stack
        tech_list = []
        for ts in proj.tech_stack.values():
            if isinstance(ts, list):
                tech_list.extend(ts[:3])
        tech_stack_str = ", ".join(tech_list[:8])
        
        # Format prompt
        user_prompt = project_template.format(
            company_name=jd.company_name if jd else "Target Company",
            role_title=jd.role_title if jd else "Target Role",
            target_keywords=", ".join(target_keywords[:15]),
            project_name=proj.name,
            project_description=proj.description[:200],
            tech_stack=tech_stack_str,
            matching_skills=", ".join(proj.matching_skills[:8]),
            original_bullets=original_bullets_text
        )
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = llm.invoke(messages)
            response_text = response.content
            
            # Parse response
            rewritten_bullets, keywords_used = parse_rewrite_response(response_text)
            
            # Update project
            proj_copy = deepcopy(proj)
            proj_copy.rewritten_bullets = rewritten_bullets if rewritten_bullets else original_bullets
            proj_copy.keywords_incorporated = keywords_used
            
            # Also update bullets field for consistency
            if rewritten_bullets:
                proj_copy.bullets = rewritten_bullets
            
            rewritten.append(proj_copy)
            all_keywords_used.extend(keywords_used)
            
            print(f"    ✅ Rewrote {len(rewritten_bullets)} bullets")
            
        except Exception as e:
            print(f"    ⚠️ Rewrite failed: {e}, keeping original")
            proj_copy = deepcopy(proj)
            proj_copy.rewritten_bullets = original_bullets
            rewritten.append(proj_copy)
    
    return {
        "rewritten_projects": rewritten,
        "keywords_incorporated": list(set(all_keywords_used))
    }


# ============================================================================
# NODE 5: VALIDATE REWRITES
# ============================================================================

def validate_rewrites(state: ExperienceRewriterState) -> Dict[str, Any]:
    """
    Validate rewritten bullets for quality:
    - Check keyword incorporation rate
    - Verify metrics are present
    - Check action verb usage
    
    Returns:
        Updated state with validation results
    """
    rewritten_exp = state.rewritten_experiences
    rewritten_proj = state.rewritten_projects
    target_keywords = set(k.lower() for k in state.target_keywords)
    keywords_used = set(k.lower() for k in state.keywords_incorporated)
    
    # Calculate incorporation rate
    if target_keywords:
        incorporation_rate = len(keywords_used & target_keywords) / len(target_keywords) * 100
    else:
        incorporation_rate = 0
    
    # Validate experiences
    exp_issues = []
    for exp in rewritten_exp:
        for i, bullet in enumerate(exp.rewritten_bullets):
            # Check for metrics (numbers, percentages)
            has_metric = bool(re.search(r'\d+[%xX]?|\d+\.\d+', bullet))
            if not has_metric:
                exp_issues.append(f"{exp.role} bullet {i+1}: Missing metric")
            
            # Check action verb (should start with capital verb)
            first_word = bullet.split()[0] if bullet else ""
            if not first_word[0].isupper():
                exp_issues.append(f"{exp.role} bullet {i+1}: Doesn't start with action verb")
    
    # Validate projects
    proj_issues = []
    for proj in rewritten_proj:
        for i, bullet in enumerate(proj.rewritten_bullets):
            has_metric = bool(re.search(r'\d+[%xX]?|\d+\.\d+', bullet))
            if not has_metric:
                proj_issues.append(f"{proj.name} bullet {i+1}: Missing metric")
    
    # Log validation results
    total_issues = len(exp_issues) + len(proj_issues)
    print(f"  📊 Keyword incorporation: {incorporation_rate:.1f}%")
    print(f"  📋 Validation issues: {total_issues}")
    
    if exp_issues:
        print(f"    Experience issues: {len(exp_issues)}")
    if proj_issues:
        print(f"    Project issues: {len(proj_issues)}")
    
    return {
        "incorporation_rate": incorporation_rate,
        "rewrite_complete": True,
        "rewrite_iteration": state.rewrite_iteration + 1
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Nodes
    "load_resources",
    "prepare_keywords",
    "rewrite_experiences",
    "rewrite_projects",
    "validate_rewrites",
    
    # Utilities
    "get_llm",
    "load_prompt",
    "parse_rewrite_response"
]
