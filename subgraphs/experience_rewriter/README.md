# Experience Rewriter Subgraph

Rewrites experience and project bullets with JD keywords and action verbs.

## Overview

The Experience Rewriter subgraph transforms original bullets into ATS-optimized versions by:
- Incorporating JD keywords naturally
- Starting with strong action verbs
- Adding quantifiable metrics
- Maintaining technical accuracy

## Graph Flow

```
START ──► load_resources ──► prepare_keywords ──► rewrite_experiences
                                                        │
                                                        ▼
                            END ◄── validate_rewrites ◄── rewrite_projects
```

## Usage

```python
from subgraphs import rewrite_for_jd, quick_rewrite

# With structured JD and selected content
result = rewrite_for_jd(
    structured_jd=jd,
    selected_experiences=experiences,
    selected_projects=projects
)
print(f"Keyword incorporation: {result['incorporation_rate']:.1f}%")

# Quick rewrite (for testing)
result = quick_rewrite(
    experiences=experiences,
    projects=projects,
    target_keywords=["Python", "machine learning", "deep learning"],
    company_name="Amazon"
)
```

## Example Transformation

**Original:**
```
Developed ML models for the recommendation system
```

**Rewritten:**
```
Engineered production-grade machine learning models for recommendation 
system using Python and TensorFlow, improving click-through rate by 25%
```

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports |
| `state.py` | ExperienceRewriterState definition |
| `nodes.py` | Node functions |
| `graph.py` | Graph builder and convenience functions |
| `prompts/` | LLM prompts for rewriting |
| `test.py` | Test script |

## Resources Used

- `resources/action_verbs.json` - Strong action verbs by category
- `resources/resume_writing_guide.md` - Writing best practices

## Convenience Functions

| Function | Description |
|----------|-------------|
| `rewrite_for_jd(structured_jd, selected_experiences, selected_projects)` | Full rewrite with JD |
| `quick_rewrite(experiences, projects, target_keywords, company_name)` | Quick rewrite |

## Return Value

```python
{
    "rewritten_experiences": [SelectedExperience],  # With rewritten_bullets
    "rewritten_projects": [SelectedProject],         # With rewritten bullets
    "keywords_incorporated": ["Python", "ML"],       # Keywords used
    "incorporation_rate": 85.5,                      # Percentage
    "target_keywords": ["Python", "ML", "..."],      # Target keywords
    "error": str | None,
    "rewrite_complete": bool
}
```

## Action Verb Categories

| Category | Examples |
|----------|----------|
| Technical | Engineered, Developed, Implemented, Architected |
| Leadership | Led, Directed, Coordinated, Mentored |
| Achievement | Achieved, Delivered, Exceeded, Improved |
| Analysis | Analyzed, Evaluated, Assessed, Identified |

## Rewriting Guidelines

1. **Start with action verb** - Never use "Responsible for"
2. **Incorporate keywords** - Natural placement, not keyword stuffing
3. **Add metrics** - Numbers, percentages, timeframes
4. **Keep concise** - Under 20 words per bullet
5. **Technical accuracy** - Don't exaggerate capabilities
