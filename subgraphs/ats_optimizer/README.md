# ATS Optimizer Subgraph

Optimizes resume for Applicant Tracking System (ATS) scoring.

## Overview

The ATS Optimizer subgraph iteratively improves resume ATS score by:
- Scanning for JD keyword presence
- Checking keyword density
- Identifying format issues
- Applying optimization suggestions
- Looping until target score (95%) is reached

## Graph Flow

```
START ──► extract_jd_keywords ──► scan_resume_content ──► calculate_ats_score
                                                              │
                                                              ▼
                                                       check_format_issues
                                                              │
                                                              ▼
                                                       generate_suggestions
                                                              │
                                         ┌────────────────────┴────────────────────┐
                                         │                                         │
                                   [score < 95%]                            [score >= 95%]
                                         │                                         │
                                         ▼                                         │
                                  apply_suggestions ───┐                           │
                                         │             │                           │
                                         └─────────────┘ (loop)                    │
                                                                                   ▼
                                                                           finalize_analysis ──► END
```

## Usage

```python
from subgraphs import optimize_resume_for_ats, quick_ats_check, get_ats_report

# Full optimization (with retry loop)
result = optimize_resume_for_ats(
    structured_jd=jd,
    resume_json=resume,
    target_score=95,
    max_iterations=3
)
print(f"Final Score: {result['original_score']}%")
print(f"Passed: {result['passed']}")

# Quick check (no optimization)
result = quick_ats_check(
    resume_json=resume,
    jd_skills=["Python", "TensorFlow"],
    jd_keywords=["machine learning"]
)

# Get human-readable report
report = get_ats_report(result["ats_analysis"])
print(report)
```

## Output: ATSAnalysis

```python
ATSAnalysis(
    score=96,
    keyword_density=0.85,
    keywords_found=["Python", "TensorFlow", "machine learning"],
    keywords_missing=["Docker"],
    format_issues=["Summary too short"],
    section_scores={
        "summary": 90,
        "experience": 98,
        "skills": 95,
        "projects": 92
    },
    suggestions=["Add Docker to skills section"],
    passed=True
)
```

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports |
| `state.py` | ATSOptimizerState definition |
| `nodes.py` | Node functions |
| `graph.py` | Graph builder with conditional edges |
| `test.py` | Test script |

## Scoring Components

| Component | Weight | Description |
|-----------|--------|-------------|
| Keyword match | 40% | Required/preferred skills found |
| Keyword density | 20% | Keywords per section |
| Format compliance | 20% | Section structure, length |
| Section coverage | 20% | All sections present |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `optimize_resume_for_ats(structured_jd, resume_json, target_score, max_iterations)` | Full optimization |
| `quick_ats_check(resume_json, jd_skills, jd_keywords)` | Quick score without optimization |
| `get_ats_report(ats_analysis)` | Generate human-readable report |

## Return Value

```python
{
    "ats_analysis": ATSAnalysis,       # Analysis results
    "optimized_resume": ResumeJSON,    # Modified resume (if optimized)
    "original_score": int,             # Final score
    "keywords_found": list,
    "keywords_missing": list,
    "format_issues": list,
    "suggestions": list,
    "applied_suggestions": list,
    "iterations": int,                 # Number of iterations run
    "passed": bool,                    # Score >= target
    "error": str | None
}
```

## Optimization Strategies

1. **Add missing keywords** to skills section
2. **Reorder skills** by JD priority
3. **Expand summary** with key terms
4. **Add metrics** to bullet points
5. **Improve keyword density** per section
