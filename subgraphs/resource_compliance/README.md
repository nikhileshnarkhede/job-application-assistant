# Resource Compliance Subgraph

Validates resume against checklists and rubrics.

## Overview

The Resource Compliance subgraph validates the resume against:
- Resume checklist (binary pass/fail items)
- Resume rubric (4-point scale scoring)
- Action verb compliance
- Writing guide recommendations

## Graph Flow

```
START ──► prepare_resume_text ──► validate_checklist ──► score_rubric
                                                              │
                                                              ▼
                            END ◄── compile_report ◄── generate_feedback
```

## Usage

```python
from subgraphs import validate_resume_compliance, get_compliance_summary, quick_compliance_check

# Full validation
result = validate_resume_compliance(resume_json=resume)
report = result["compliance_report"]
print(f"Overall Score: {report.overall_score}%")
print(f"Grade: {report.grade}")
print(f"Passed: {report.passed}")

# Get human-readable summary
summary = get_compliance_summary(report)
print(summary)

# Quick check (just scores)
result = quick_compliance_check(resume_json=resume)
print(f"Overall: {result['overall_score']}%")
print(f"Passed: {result['passed']}")
```

## Output: ComplianceReport

```python
ComplianceReport(
    overall_score=88.5,
    grade="B+",
    passed=True,
    
    checklist_score=92.0,  # Percentage of items passed
    checklist_sections={
        "Formatting": {"passed": 5, "failed": 0, "items": [...]},
        "Content": {"passed": 8, "failed": 1, "items": [...]}
    },
    
    rubric_score=85.0,  # Average rubric score (scaled to 100)
    rubric_categories={
        "Impact & Metrics": {"score": 4, "max": 4, "feedback": "..."},
        "Technical Depth": {"score": 3, "max": 4, "feedback": "..."}
    },
    
    strengths=["Strong action verbs", "Good metrics"],
    critical_issues=["Missing quantifiable results in 2 bullets"],
    improvements=["Add more specific metrics", "Include team size"]
)
```

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports |
| `state.py` | ResourceComplianceState, ComplianceReport |
| `nodes.py` | Node functions |
| `graph.py` | Graph builder and convenience functions |
| `test.py` | Test script |

## Resources Used

| Resource | Description |
|----------|-------------|
| `RESUME_CHECKLIST` | Binary pass/fail validation items |
| `RESUME_RUBRIC` | 4-point scale scoring criteria |
| `action_verbs.json` | Valid action verbs for bullets |

## Checklist Categories

- **Formatting**: Layout, fonts, spacing
- **Content**: Sections, completeness
- **Language**: Grammar, tone, verbs
- **Technical**: Skills representation

## Rubric Scoring (4-point scale)

| Score | Description |
|-------|-------------|
| 4 | Excellent - Exceeds expectations |
| 3 | Good - Meets expectations |
| 2 | Fair - Partially meets expectations |
| 1 | Poor - Does not meet expectations |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `validate_resume_compliance(resume_json)` | Full validation with report |
| `get_compliance_summary(report)` | Human-readable summary |
| `quick_compliance_check(resume_json)` | Quick scores only |

## Return Value

```python
{
    "compliance_report": ComplianceReport,  # Full report
    "checklist_results": dict,              # Per-item results
    "rubric_scores": list,                  # Per-category scores
    "validation_complete": bool,
    "error": str | None
}
```

## Pass Thresholds

- **Checklist**: 80% of items must pass
- **Rubric**: Average score >= 3.0 (out of 4.0)
- **Overall**: 85% (configurable in `PIPELINE_CONFIG`)
