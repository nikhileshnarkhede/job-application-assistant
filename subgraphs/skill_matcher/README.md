# Skill Matcher Subgraph

Matches candidate skills against job description requirements.

## Overview

The Skill Matcher subgraph compares candidate skills to JD requirements and provides:
- Match percentage
- Matched and missing skills
- Skill gap analysis
- Partial matches (similar skills)

## Graph Flow

```
START ──► load_candidate_skills ──► extract_jd_skills ──► match_skills
                                                              │
                                                              ▼
                                    END ◄── build_result ◄── analyze_gaps
```

## Usage

```python
from subgraphs import match_skills_to_jd, quick_skill_match

# With structured JD (from JD Extractor)
result = match_skills_to_jd(structured_jd=jd)
print(f"Match: {result['skill_match_result'].match_percentage}%")
print(f"Matched: {result['skill_match_result'].matched_skills}")
print(f"Missing: {result['skill_match_result'].missing_skills}")

# Quick match (for testing)
result = quick_skill_match(
    jd_skills_required=["Python", "TensorFlow", "SQL"],
    jd_skills_preferred=["Docker", "Kubernetes"],
    candidate_skills=["Python", "PyTorch", "Docker", "SQL"]
)
```

## Output: SkillMatchResult

```python
SkillMatchResult(
    matched_skills=["Python", "SQL", "Docker"],
    missing_skills=["TensorFlow", "Kubernetes"],
    partial_matches=["PyTorch → TensorFlow"],  # Similar technologies
    additional_skills=["React", "Node.js"],     # Candidate has, JD doesn't need
    match_percentage=75.0,
    skill_gap_analysis="Strong Python foundation. Consider TensorFlow certification.",
    critical_missing=["TensorFlow"]  # Must-have skills missing
)
```

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports |
| `state.py` | SkillMatcherState, skill aliases, normalization |
| `nodes.py` | Node functions |
| `graph.py` | Graph builder and convenience functions |
| `test.py` | Test script |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `match_skills_to_jd(structured_jd, candidate_skills, candidate_keywords)` | Full matching with JD |
| `quick_skill_match(jd_skills_required, jd_skills_preferred, candidate_skills)` | Quick match without JD |

## Skill Normalization

Skills are normalized for matching:
- Case-insensitive: `"Python"` = `"python"` = `"PYTHON"`
- Aliases: `"ML"` = `"Machine Learning"`, `"DL"` = `"Deep Learning"`
- Variants: `"TensorFlow"` = `"TF"` = `"tensorflow 2.0"`

## Return Value

```python
{
    "skill_match_result": SkillMatchResult,  # Match data
    "error": str | None,                      # Error message if failed
    "matching_complete": bool                 # Whether matching completed
}
```

## Data Sources

Candidate skills are loaded from:
1. `data/candidate_experience.json` - Primary source
2. Function parameter - Override if provided
