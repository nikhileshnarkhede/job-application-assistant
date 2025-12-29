# Experience Selector Subgraph

Selects the most relevant work experiences for the resume.

## Overview

The Experience Selector subgraph analyzes candidate experiences and selects the top N most relevant based on:
- Skill overlap with JD requirements
- Keyword matching
- Role type relevance
- Recency and impact

## Graph Flow

```
START ──► load_experiences ──► extract_jd_requirements ──► score_experiences
                                                              │
                                                              ▼
                               END ◄── prepare_for_rewriting ◄── select_top_experiences
```

## Usage

```python
from subgraphs import select_experiences_for_jd, quick_experience_selection

# With structured JD
result = select_experiences_for_jd(structured_jd=jd, max_experiences=4)
for exp in result["selected_experiences"]:
    print(f"{exp.role} @ {exp.company}: {exp.relevance_score}%")

# Quick selection (for testing)
result = quick_experience_selection(
    jd_skills=["Python", "Machine Learning"],
    jd_keywords=["data science", "analytics"],
    role_type="ml_ai",
    max_experiences=4
)
```

## Output: SelectedExperience

```python
SelectedExperience(
    id=1,
    role="Machine Learning Engineer",
    role_full="Senior Machine Learning Engineer",
    company="Tech Corp",
    employment_type="Full-time",
    dates={"start": "Jan 2022", "end": "Present", "duration": "2 years"},
    location={"city": "San Francisco", "state": "CA", "type": "Hybrid"},
    relevance_score=90.5,
    matching_keywords=["Python", "TensorFlow", "ML pipelines"],
    original_bullets=[
        "Developed ML models for recommendation system",
        "Reduced inference latency by 40%"
    ],
    rewritten_bullets=[],  # Populated by Experience Rewriter
    keywords_incorporated=[]
)
```

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports |
| `state.py` | ExperienceSelectorState definition |
| `nodes.py` | Node functions |
| `graph.py` | Graph builder and convenience functions |
| `test.py` | Test script |

## Data Source

Experiences are loaded from `data/candidate_experience.json`:

```json
{
  "experiences": [
    {
      "id": 1,
      "role": "ML Engineer",
      "company": "Tech Corp",
      "bullets": ["..."],
      "skills_used": ["Python", "TensorFlow"]
    }
  ]
}
```

## Scoring Factors

| Factor | Weight |
|--------|--------|
| Skill overlap | 40% |
| Keyword match | 25% |
| Role relevance | 20% |
| Recency bonus | 15% |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `select_experiences_for_jd(structured_jd, max_experiences)` | Full selection with JD |
| `quick_experience_selection(jd_skills, jd_keywords, role_type, max_experiences)` | Quick selection |

## Return Value

```python
{
    "selected_experiences": [SelectedExperience],  # Ranked experiences
    "all_experiences_count": int,                   # Total experiences
    "error": str | None,
    "selection_complete": bool
}
```
