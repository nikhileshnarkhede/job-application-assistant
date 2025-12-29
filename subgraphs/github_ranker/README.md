# GitHub Ranker Subgraph

Ranks GitHub projects by relevance to job description.

## Overview

The GitHub Ranker subgraph fetches projects from GitHub API and ranks them by:
- Tech stack overlap with JD skills
- Keyword matching
- Role type relevance
- Project quality (stars, metrics)

## Graph Flow

```
START ──► load_projects ──► extract_jd_requirements ──► score_projects
                                                            │
                                                            ▼
                            END ◄── generate_bullets ◄── select_top_projects
```

## Usage

```python
from subgraphs import rank_github_projects, get_top_projects_for_jd

# With structured JD
result = rank_github_projects(structured_jd=jd, max_projects=3)
for project in result["selected_projects"]:
    print(f"{project.name}: {project.relevance_score}%")

# Quick ranking (for testing)
result = get_top_projects_for_jd(
    jd_skills=["Python", "TensorFlow", "Docker"],
    jd_keywords=["machine learning", "deep learning"],
    role_type="ml_ai",
    max_projects=3
)
```

## Output: SelectedProject

```python
SelectedProject(
    name="ml-pipeline",
    github_url="https://github.com/user/ml-pipeline",
    description="End-to-end ML pipeline with TensorFlow",
    tech_stack={"languages": ["Python"], "frameworks": ["TensorFlow", "FastAPI"]},
    relevance_score=85.5,
    matching_skills=["Python", "TensorFlow"],
    bullets=[
        "Developed end-to-end ML pipeline reducing model deployment time by 60%",
        "Implemented FastAPI service handling 10K+ requests/day"
    ],
    metrics=["60% faster deployment", "10K+ daily requests"]
)
```

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports |
| `state.py` | GitHubRankerState, scoring weights, role type tags |
| `nodes.py` | Node functions |
| `graph.py` | Graph builder and convenience functions |
| `prompts/` | LLM prompts for bullet generation |
| `test.py` | Test script |

## Data Sources (Priority Order)

1. **GitHub API (LIVE)** - Always tried first if credentials available
2. **Cached JSON** - `data/github_projects_fetched.json`
3. **Manual JSON** - `data/github_projects.json` (for custom bullets/metrics)

## Configuration

```bash
# Required for GitHub API
GITHUB_USERNAME=your-username
GITHUB_TOKEN=github_pat_xxx
```

## Scoring Weights

| Factor | Weight |
|--------|--------|
| Tech stack overlap | 35% |
| Keyword match | 25% |
| Role relevance tags | 20% |
| Quality (metrics, stars) | 20% |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `rank_github_projects(structured_jd, max_projects)` | Full ranking with JD |
| `get_top_projects_for_jd(jd_skills, jd_keywords, role_type, max_projects)` | Quick ranking |

## Return Value

```python
{
    "selected_projects": [SelectedProject],  # Ranked projects
    "all_projects_count": int,               # Total projects found
    "projects_source": str,                  # "github_api", "cache", or "json"
    "error": str | None,
    "ranking_complete": bool
}
```

## Bullet Generation

If projects don't have pre-written bullets, LLM generates them:
- Action verb + quantifiable impact
- Matching JD skills highlighted
- 2-3 bullets per project
