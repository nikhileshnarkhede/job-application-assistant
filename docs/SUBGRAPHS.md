# Subgraphs Overview

**Last Updated:** December 29, 2024

## Summary

The Job Application Assistant consists of 12 self-contained subgraphs, each handling a specific stage of the job application process.

## Subgraph List

| # | Subgraph | Purpose | Key Output |
|---|----------|---------|------------|
| 1 | `jd_extractor` | Extract structured JD from URL/text | `StructuredJD` |
| 2 | `skill_matcher` | Match candidate skills to JD | `SkillMatchResult` |
| 3 | `github_ranker` | Rank GitHub projects by relevance | `[SelectedProject]` |
| 4 | `experience_selector` | Select relevant experiences | `[SelectedExperience]` |
| 5 | `experience_rewriter` | Rewrite bullets with keywords | Rewritten content |
| 6 | `resume_builder` | Assemble complete resume | `ResumeJSON` |
| 7 | `ats_optimizer` | Optimize for ATS score | `ATSAnalysis` |
| 8 | `resource_compliance` | Validate against checklists | `ComplianceReport` |
| 9 | `cover_letter_generator` | Generate cover letter | `CoverLetter` |
| 10 | `cover_letter_compliance` | Validate cover letter | `CoverLetterComplianceReport` |
| 11 | `email_generator` | Generate outreach emails | `GeneratedEmail` |
| 12 | `excel_writer` | Save to tracking spreadsheet | `ApplicationRecord` |

## Data Flow

```
                    ┌─────────────────────┐
                    │   JD URL / Text     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   1. JD Extractor   │
                    │   StructuredJD      │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
    │ 2. Skill Match  │ │ 3. GitHub   │ │ 4. Experience   │
    │ SkillMatchResult│ │ Ranker      │ │ Selector        │
    └────────┬────────┘ └──────┬──────┘ └────────┬────────┘
             │                 │                  │
             └─────────────────┼──────────────────┘
                               │
                               ▼
                  ┌─────────────────────┐
                  │ 5. Experience       │
                  │ Rewriter            │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ 6. Resume Builder   │
                  │ ResumeJSON          │
                  └──────────┬──────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
       ┌─────────────────┐   ┌─────────────────────┐
       │ 7. ATS Optimizer│   │ 8. Compliance Check │
       └────────┬────────┘   └──────────┬──────────┘
                │                       │
                └───────────┬───────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ 9. Cover Letter Gen │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ 10. CL Compliance   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ 11. Email Generator │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ 12. Excel Writer    │
                 └─────────────────────┘
```

## Common Patterns

### 1. Subgraph Structure

Every subgraph follows this standard structure:

```
subgraphs/{name}/
├── __init__.py       # Package exports
├── state.py          # Subgraph-specific state model
├── nodes.py          # Node function definitions
├── graph.py          # Graph builder + convenience functions
├── test.py           # Test script
├── README.md         # Documentation
└── prompts/          # LLM prompts (if applicable)
    ├── system_prompt.txt
    ├── main_prompt.txt
    └── few_shot_examples.txt
```

### 2. Convenience Functions

Each subgraph exports high-level functions that hide graph complexity:

```python
# Primary function (full parameters)
result = match_skills_to_jd(structured_jd, candidate_skills, candidate_keywords)

# Quick function (minimal parameters, for testing)
result = quick_skill_match(jd_skills_required, jd_skills_preferred, candidate_skills)
```

### 3. Return Pattern

All convenience functions return a dictionary:

```python
{
    "primary_output": ...,      # Main result (e.g., "structured_jd", "resume_json")
    "status_flag": bool,        # e.g., "validation_passed", "build_complete"
    "error": str | None,        # Error message if failed
    ...additional_metadata
}
```

### 4. Graph Builder Functions

```python
# Build compiled graph
graph = build_{name}_graph()

# Create subgraph (alias for build)
subgraph = create_{name}_subgraph()

# Direct invocation
result = subgraph.invoke(initial_state)
```

## Using Subgraphs

### Import from Central Package

```python
from subgraphs import (
    # JD Extractor
    extract_jd_from_url,
    extract_jd_from_text,
    
    # Skill Matcher
    match_skills_to_jd,
    
    # GitHub Ranker
    rank_github_projects,
    
    # Experience
    select_experiences_for_jd,
    rewrite_for_jd,
    
    # Resume
    build_resume,
    optimize_resume_for_ats,
    validate_resume_compliance,
    
    # Cover Letter
    generate_cover_letter_for_job,
    validate_cover_letter_compliance,
    
    # Email & Excel
    generate_outreach_email,
    save_application_to_excel,
)
```

### Direct Subgraph Import

```python
from subgraphs.jd_extractor import (
    extract_jd_from_url,
    JDExtractorState,
    build_jd_extractor_graph
)
```

## Testing Subgraphs

### Using Test Constants

```python
from subgraphs import STANDARD_JD_URL, STANDARD_JD_TEXT

# Test with standard Amazon JD
result = extract_jd_from_url(STANDARD_JD_URL)

# Or use text directly
result = extract_jd_from_text(STANDARD_JD_TEXT)
```

### Running Individual Tests

```bash
# Run subgraph test
python -m subgraphs.jd_extractor.test
python -m subgraphs.skill_matcher.test
```

## Subgraph Dependencies

| Subgraph | Requires |
|----------|----------|
| jd_extractor | - |
| skill_matcher | StructuredJD, candidate_skills |
| github_ranker | StructuredJD |
| experience_selector | StructuredJD |
| experience_rewriter | StructuredJD, selected content |
| resume_builder | StructuredJD, rewritten content |
| ats_optimizer | StructuredJD, ResumeJSON |
| resource_compliance | ResumeJSON |
| cover_letter_generator | StructuredJD, ResumeJSON |
| cover_letter_compliance | CoverLetter |
| email_generator | StructuredJD, ResumeJSON |
| excel_writer | StructuredJD, scores |

## External Dependencies

| Subgraph | External Service |
|----------|------------------|
| jd_extractor | OpenAI API (LLM) |
| github_ranker | GitHub API |
| experience_rewriter | OpenAI API (LLM) |
| resume_builder | OpenAI API (LLM) |
| cover_letter_generator | OpenAI API, Web Search |
| email_generator | OpenAI API (LLM) |

## Quick Reference

### Extracting JD
```python
result = extract_jd_from_url("https://example.com/job")
jd = result["structured_jd"]
```

### Matching Skills
```python
result = match_skills_to_jd(structured_jd=jd)
match = result["skill_match_result"]
print(f"Match: {match.match_percentage}%")
```

### Building Resume
```python
result = build_resume(
    structured_jd=jd,
    rewritten_experiences=experiences,
    rewritten_projects=projects
)
resume = result["resume_json"]
```

### Optimizing for ATS
```python
result = optimize_resume_for_ats(
    structured_jd=jd,
    resume_json=resume,
    target_score=95
)
print(f"Score: {result['original_score']}%")
```

### Generating Cover Letter
```python
result = generate_cover_letter_for_job(
    structured_jd=jd,
    resume_json=resume
)
text = result["cover_letter"].full_text
```
