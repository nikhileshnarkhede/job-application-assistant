# Cover Letter Compliance Subgraph

Validates cover letters against checklists and rubrics.

## Overview

The Cover Letter Compliance subgraph validates cover letters against:
- Cover letter checklist (binary pass/fail items)
- Cover letter rubric (3-point scale scoring)
- Word count and formatting rules
- Personalization and relevance checks

## Graph Flow

```
START ──► prepare_cover_letter_text ──► validate_checklist ──► score_rubric
                                                                  │
                                                                  ▼
                                END ◄── compile_report ◄── generate_feedback
```

## Usage

```python
from subgraphs import (
    validate_cover_letter_compliance,
    get_cover_letter_compliance_summary,
    quick_cover_letter_compliance_check
)

# Full validation
result = validate_cover_letter_compliance(
    cover_letter=cover_letter,
    cover_letter_text=text,
    structured_jd=jd
)
report = result["compliance_report"]
print(f"Score: {report.overall_score}%")
print(f"Passed: {report.passed}")

# Get human-readable summary
summary = get_cover_letter_compliance_summary(report)
print(summary)

# Quick check
result = quick_cover_letter_compliance_check(cover_letter_text=text)
print(f"Score: {result['overall_score']}%")
```

## Output: CoverLetterComplianceReport

```python
CoverLetterComplianceReport(
    overall_score=85.0,
    grade="B",
    passed=True,
    
    checklist_score=90.0,
    checklist_sections={
        "Structure": {"passed": 4, "failed": 0},
        "Content": {"passed": 5, "failed": 1}
    },
    
    rubric_score=80.0,
    rubric_categories={
        "Personalization": {"score": 3, "max": 3},
        "Value Proposition": {"score": 2, "max": 3}
    },
    
    strengths=["Good company research", "Clear structure"],
    critical_issues=["Missing specific role mention"],
    improvements=["Add more specific achievements"]
)
```

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports |
| `state.py` | CoverLetterComplianceState, CoverLetterComplianceReport |
| `nodes.py` | Node functions |
| `graph.py` | Graph builder and convenience functions |
| `test.py` | Test script |

## Resources Used

| Resource | Description |
|----------|-------------|
| `COVER_LETTER_CHECKLIST` | Binary validation items |
| `COVER_LETTER_RUBRIC` | 3-point scale criteria |

## Checklist Categories

- **Structure**: Opening, body, closing
- **Content**: Personalization, relevance
- **Formatting**: Length, paragraphs
- **Professionalism**: Tone, grammar

## Rubric Scoring (3-point scale)

| Score | Description |
|-------|-------------|
| 3 | Excellent |
| 2 | Good |
| 1 | Needs Improvement |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `validate_cover_letter_compliance(cover_letter, cover_letter_text, structured_jd)` | Full validation |
| `get_cover_letter_compliance_summary(report)` | Human-readable summary |
| `quick_cover_letter_compliance_check(cover_letter_text)` | Quick scores only |

## Return Value

```python
{
    "compliance_report": CoverLetterComplianceReport,
    "checklist_results": dict,
    "rubric_scores": list,
    "validation_complete": bool,
    "error": str | None
}
```

## Validation Rules

- **Word count**: 250-400 words
- **Paragraphs**: 3-5 paragraphs
- **Company mention**: At least 2 times
- **Role mention**: At least 1 time
- **No generic phrases**: "I am writing to apply..."
