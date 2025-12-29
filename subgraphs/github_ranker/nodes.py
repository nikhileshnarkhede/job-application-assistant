"""
GitHub Ranker Nodes

This module contains all node definitions for the GitHub Ranker subgraph:
1. load_projects - Load GitHub projects from API (LIVE)
2. extract_jd_requirements - Extract skills/keywords from JD
3. score_projects - Score each project by relevance
4. select_top_projects - Select top N projects
5. generate_bullets - Generate resume bullets using LLM

Node Flow:
    START → load_projects → extract_jd_requirements → score_projects → select_top_projects → generate_bullets → END
"""

import os
import json
from typing import Dict, Any, List, Set
from pathlib import Path

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# State imports
from subgraphs.github_ranker.state import (
    GitHubRankerState,
    SCORING_WEIGHTS,
    ROLE_TYPE_TAGS
)
from state.state_models import SelectedProject


# ============================================================================
# CONFIGURATION
# ============================================================================

def get_llm():
    """Get configured LLM instance."""
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


def get_data_path() -> str:
    """Get data directory path."""
    return os.getenv("DATA_PATH", "./data")


# ============================================================================
# NODE 1: LOAD PROJECTS (GITHUB API FIRST!)
# ============================================================================

def load_projects(state: GitHubRankerState) -> Dict[str, Any]:
    """
    Load GitHub projects from available sources.
    
    Priority (UPDATED - API FIRST):
    1. GitHub API (LIVE) - always try first for latest data
    2. Cached API data (github_projects_fetched.json) - fallback
    3. Manual JSON (github_projects.json) - customized overrides
    
    Returns:
        Updated state with all_projects and projects_source
    """
    projects = []
    source = ""
    
    data_path = get_data_path()
    
    # ===== TRY 1: GITHUB API (LIVE) =====
    try:
        from mcp_server.tools.github_project_loader import (
            load_projects_from_github_api, 
            project_to_dict,
            get_github_username,
            get_github_token
        )
        
        username = get_github_username()
        token = get_github_token()
        
        if username and token:
            print(f"  🌐 Fetching from GitHub API (@{username})...")
            api_projects = load_projects_from_github_api(fetch_details=False)  # Fast mode
            
            if api_projects:
                projects = [project_to_dict(p) for p in api_projects]
                source = "github_api"
                print(f"  ✅ Loaded {len(projects)} projects from GitHub API")
                
                # Merge with manual JSON for custom metrics/bullets
                manual_projects = _load_manual_overrides(data_path)
                if manual_projects:
                    projects = _merge_projects(projects, manual_projects)
                    print(f"  📝 Merged custom data for {len(manual_projects)} projects")
        else:
            print(f"  ⚠️  GitHub credentials not set (GITHUB_USERNAME, GITHUB_TOKEN)")
            
    except Exception as e:
        print(f"  ⚠️  GitHub API failed: {e}")
    
    # ===== TRY 2: Cached API data (fallback) =====
    if not projects:
        cached_path = os.path.join(data_path, "github_projects_fetched.json")
        if os.path.exists(cached_path):
            try:
                with open(cached_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    projects = data.get("projects", [])
                    source = "cache"
                    print(f"  📂 Loaded {len(projects)} projects from cache")
            except Exception as e:
                print(f"  ⚠️  Cache load failed: {e}")
    
    # ===== TRY 3: Manual JSON (last resort) =====
    if not projects:
        manual_path = os.path.join(data_path, "github_projects.json")
        if os.path.exists(manual_path):
            try:
                with open(manual_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    projects = data.get("projects", [])
                    # Filter out placeholders
                    projects = [p for p in projects if not p.get("name", "").startswith("Project Name")]
                    source = "json"
                    print(f"  📂 Loaded {len(projects)} projects from JSON")
            except Exception as e:
                print(f"  ⚠️  JSON load failed: {e}")
    
    if not projects:
        return {
            "all_projects": [],
            "projects_source": "none",
            "error_message": "No GitHub projects found. Set GITHUB_USERNAME and GITHUB_TOKEN in .env"
        }
    
    return {
        "all_projects": projects,
        "projects_source": source
    }


def _load_manual_overrides(data_path: str) -> List[Dict]:
    """Load manual project overrides (custom bullets, metrics, etc.)"""
    manual_path = os.path.join(data_path, "github_projects.json")
    if not os.path.exists(manual_path):
        return []
    
    try:
        with open(manual_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            projects = data.get("projects", [])
            # Filter out placeholders
            return [p for p in projects if not p.get("name", "").startswith("Project Name")]
    except:
        return []


def _merge_projects(api_projects: List[Dict], manual_projects: List[Dict]) -> List[Dict]:
    """Merge API projects with manual overrides (manual takes precedence for matching projects)."""
    manual_by_name = {p.get("name", "").lower(): p for p in manual_projects}
    
    merged = []
    for proj in api_projects:
        name_lower = proj.get("name", "").lower()
        
        if name_lower in manual_by_name:
            # Merge: keep API metadata, use manual bullets/metrics
            manual = manual_by_name[name_lower]
            proj["bullets_for_resume"] = manual.get("bullets_for_resume", proj.get("bullets_for_resume", []))
            proj["metrics"] = manual.get("metrics", proj.get("metrics", []))
            proj["key_features"] = manual.get("key_features", proj.get("key_features", []))
            proj["problem_solved"] = manual.get("problem_solved", proj.get("problem_solved", ""))
        
        merged.append(proj)
    
    return merged


# ============================================================================
# NODE 2: EXTRACT JD REQUIREMENTS
# ============================================================================

def extract_jd_requirements(state: GitHubRankerState) -> Dict[str, Any]:
    """
    Extract skills and keywords from structured JD for matching.
    
    Returns:
        Updated state with jd_skills, jd_keywords, role_type
    """
    jd = state.structured_jd
    
    if not jd:
        return {
            "error_message": "No structured JD provided",
            "ranking_complete": True
        }
    
    # Combine required and preferred skills
    jd_skills = list(set((jd.skills_required or []) + (jd.skills_preferred or [])))
    
    # Get keywords
    jd_keywords = jd.keywords or []
    
    # Get role type
    role_type = jd.role_type or "ml_ai"
    
    return {
        "jd_skills": jd_skills,
        "jd_keywords": jd_keywords,
        "role_type": role_type
    }


# ============================================================================
# NODE 3: SCORE PROJECTS
# ============================================================================

def calculate_tech_overlap(project: Dict, jd_skills: Set[str]) -> float:
    """Calculate tech stack overlap score."""
    project_tech = set()
    
    tech_stack = project.get("tech_stack", {})
    for tech_list in tech_stack.values():
        if isinstance(tech_list, list):
            for tech in tech_list:
                project_tech.add(tech.lower())
    
    # Also include language and topics
    if project.get("language"):
        project_tech.add(project["language"].lower())
    
    for topic in project.get("topics", []):
        project_tech.add(topic.lower())
    
    if not jd_skills:
        return 0.0
    
    overlap = len(project_tech & jd_skills)
    return min(overlap / len(jd_skills), 1.0)


def calculate_keyword_match(project: Dict, jd_keywords: Set[str]) -> float:
    """Calculate keyword match score."""
    project_keywords = set()
    
    # Add project keywords
    for kw in project.get("keywords", []):
        project_keywords.add(kw.lower())
    
    # Add topics
    for topic in project.get("topics", []):
        project_keywords.add(topic.lower())
    
    # Add description words
    description = project.get("description", "").lower()
    for kw in jd_keywords:
        if kw in description:
            project_keywords.add(kw)
    
    if not jd_keywords:
        return 0.0
    
    overlap = len(project_keywords & jd_keywords)
    return min(overlap / len(jd_keywords), 1.0)


def calculate_role_relevance(project: Dict, role_type: str) -> float:
    """Calculate role type relevance score."""
    project_tags = set(project.get("relevance_tags", []))
    
    # Get expected tags for this role
    expected_tags = set(ROLE_TYPE_TAGS.get(role_type, []))
    
    if not expected_tags:
        return 0.5  # Neutral score
    
    overlap = len(project_tags & expected_tags)
    if overlap > 0:
        return min(overlap / len(expected_tags) + 0.3, 1.0)
    
    return 0.0


def calculate_quality_score(project: Dict) -> float:
    """Calculate project quality score based on metrics and activity."""
    score = 0.0
    
    # Has metrics
    if project.get("metrics") and len(project.get("metrics", [])) > 0:
        score += 0.5
    
    # Has bullets
    if project.get("bullets_for_resume") and len(project.get("bullets_for_resume", [])) > 0:
        score += 0.2
    
    # Stars
    stars = project.get("stars", 0)
    if stars >= 5:
        score += 0.1
    if stars >= 20:
        score += 0.1
    if stars >= 50:
        score += 0.1
    
    return min(score, 1.0)


def score_projects(state: GitHubRankerState) -> Dict[str, Any]:
    """
    Score each project by relevance to JD.
    
    Uses weighted scoring:
    - Tech stack overlap: 35%
    - Keyword match: 25%
    - Role relevance: 20%
    - Quality/metrics: 20%
    
    Returns:
        Updated state with scored projects
    """
    projects = state.all_projects
    jd_skills = set(s.lower() for s in state.jd_skills)
    jd_keywords = set(k.lower() for k in state.jd_keywords)
    role_type = state.role_type
    
    if not projects:
        return {"error_message": "No projects to score"}
    
    scored_projects = []
    
    for project in projects:
        # Calculate component scores
        tech_score = calculate_tech_overlap(project, jd_skills)
        keyword_score = calculate_keyword_match(project, jd_keywords)
        role_score = calculate_role_relevance(project, role_type)
        quality_score = calculate_quality_score(project)
        
        # Calculate weighted total
        total_score = (
            tech_score * SCORING_WEIGHTS["tech_stack_overlap"] +
            keyword_score * SCORING_WEIGHTS["keyword_match"] +
            role_score * SCORING_WEIGHTS["relevance_tag_match"] +
            quality_score * (SCORING_WEIGHTS["has_metrics"] + SCORING_WEIGHTS["activity_bonus"])
        )
        
        # Scale to 100
        final_score = round(total_score * 100, 2)
        
        # Add score to project
        project["relevance_score"] = final_score
        project["score_breakdown"] = {
            "tech_overlap": round(tech_score * 100, 1),
            "keyword_match": round(keyword_score * 100, 1),
            "role_relevance": round(role_score * 100, 1),
            "quality": round(quality_score * 100, 1)
        }
        
        scored_projects.append(project)
    
    # Sort by score descending
    scored_projects.sort(key=lambda p: p.get("relevance_score", 0), reverse=True)
    
    return {"all_projects": scored_projects}


# ============================================================================
# NODE 4: SELECT TOP PROJECTS
# ============================================================================

def select_top_projects(state: GitHubRankerState) -> Dict[str, Any]:
    """
    Select top N projects based on scores.
    
    Returns:
        Updated state with selected_projects
    """
    projects = state.all_projects
    max_projects = state.max_projects or 3
    
    if not projects:
        return {
            "selected_projects": [],
            "error_message": "No scored projects available"
        }
    
    # Take top N
    top_projects = projects[:max_projects]
    
    # Convert to SelectedProject objects
    selected = []
    for idx, proj in enumerate(top_projects):
        # Find matching skills
        jd_skills_lower = set(s.lower() for s in state.jd_skills)
        project_tech = set()
        
        for tech_list in proj.get("tech_stack", {}).values():
            if isinstance(tech_list, list):
                for tech in tech_list:
                    project_tech.add(tech.lower())
        
        matching_skills = list(project_tech & jd_skills_lower)
        
        selected_proj = SelectedProject(
            name=proj.get("name", ""),
            github_url=proj.get("github_url", ""),
            description=proj.get("description", "")[:300],
            tech_stack=proj.get("tech_stack", {}),
            relevance_score=proj.get("relevance_score", 0),
            matching_skills=matching_skills,
            bullets=[],  # Will be generated in next node
            metrics=proj.get("metrics", []),
            key_features=proj.get("key_features", [])
        )
        
        selected.append(selected_proj)
    
    return {"selected_projects": selected}


# ============================================================================
# NODE 5: GENERATE BULLETS
# ============================================================================

def generate_bullets(state: GitHubRankerState) -> Dict[str, Any]:
    """
    Generate resume bullets for selected projects using LLM.
    
    If project already has bullets, use those.
    Otherwise, generate using LLM based on project details.
    
    Returns:
        Updated state with bullets populated
    """
    selected = state.selected_projects
    
    if not selected:
        return {
            "ranking_complete": True,
            "error_message": "No projects selected"
        }
    
    # Check if we have pre-written bullets in source data
    all_projects_dict = {p.get("name", "").lower(): p for p in state.all_projects}
    
    updated_projects = []
    projects_needing_bullets = []
    
    for proj in selected:
        source_proj = all_projects_dict.get(proj.name.lower(), {})
        existing_bullets = source_proj.get("bullets_for_resume", [])
        
        if existing_bullets and len(existing_bullets) > 0:
            # Use existing bullets
            proj.bullets = existing_bullets[:3]
            updated_projects.append(proj)
        else:
            # Need to generate
            projects_needing_bullets.append(proj)
            updated_projects.append(proj)
    
    # Generate bullets for projects that need them
    if projects_needing_bullets:
        try:
            system_prompt = load_prompt("system_prompt.txt")
            
            llm = get_llm()
            
            for proj in projects_needing_bullets:
                # Build context
                tech_stack_str = ", ".join([
                    t for ts in proj.tech_stack.values() 
                    for t in (ts if isinstance(ts, list) else [ts])
                ][:8])
                
                user_message = f"""
Generate 2-3 resume bullet points for this GitHub project:

**Project Name:** {proj.name}
**Description:** {proj.description}
**Tech Stack:** {tech_stack_str}
**Key Features:** {', '.join(proj.key_features[:3]) if proj.key_features else 'N/A'}
**Metrics:** {', '.join(proj.metrics[:2]) if proj.metrics else 'N/A'}
**Matching JD Skills:** {', '.join(proj.matching_skills[:5])}

Requirements:
- Start each bullet with a strong action verb
- Highlight the matching skills naturally
- Include quantifiable impact if possible
- Keep each bullet under 20 words
- Focus on what was built and the value delivered

Return ONLY the bullet points, one per line, no numbering.
"""
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_message)
                ]
                
                response = llm.invoke(messages)
                bullets = [b.strip() for b in response.content.strip().split("\n") if b.strip()]
                
                # Update project bullets
                for p in updated_projects:
                    if p.name == proj.name:
                        p.bullets = bullets[:3]
                        break
                        
        except Exception as e:
            # Fallback: generate basic bullets
            for proj in projects_needing_bullets:
                for p in updated_projects:
                    if p.name == proj.name:
                        p.bullets = generate_fallback_bullets(proj)
                        break
    
    return {
        "selected_projects": updated_projects,
        "ranking_complete": True
    }


def generate_fallback_bullets(project: SelectedProject) -> List[str]:
    """Generate basic bullets without LLM."""
    bullets = []
    
    # Tech stack bullet
    tech_list = []
    for ts in project.tech_stack.values():
        if isinstance(ts, list):
            tech_list.extend(ts[:2])
    
    if tech_list:
        bullets.append(f"Developed {project.name} using {', '.join(tech_list[:3])}")
    
    # Description bullet
    if project.description:
        desc = project.description[:80]
        if len(project.description) > 80:
            desc = desc.rsplit(" ", 1)[0] + "..."
        bullets.append(desc)
    
    # Metrics bullet
    if project.metrics:
        bullets.append(project.metrics[0])
    
    return bullets[:3]


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Nodes
    "load_projects",
    "extract_jd_requirements",
    "score_projects",
    "select_top_projects",
    "generate_bullets",
    
    # Utilities
    "get_llm",
    "load_prompt",
    "calculate_tech_overlap",
    "calculate_keyword_match",
    "calculate_role_relevance",
    "calculate_quality_score"
]
