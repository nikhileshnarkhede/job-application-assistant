# Cover Letter Generator Subgraph

Generates personalized cover letters with company research.

## Overview

The Cover Letter Generator subgraph creates tailored cover letters by:
- Researching company information (web search)
- Extracting candidate highlights from resume
- Generating personalized content with LLM
- Formatting for professional presentation

## Graph Flow

```
START ──► research_company ──► extract_candidate_highlights ──► generate_cover_letter ──► format_output ──► END
```

## Usage

```python
from subgraphs import generate_cover_letter_for_job, get_cover_letter_text, quick_cover_letter

# Full generation with options
result = generate_cover_letter_for_job(
    structured_jd=jd,
    resume_json=resume,
    tone="professional",  # professional, enthusiastic, conversational
    focus_areas=["machine learning", "team leadership"],
    referral_name="Jane Smith",  # Optional
    custom_hook="I was excited to see..."  # Optional opening
)
cover_letter = result["cover_letter"]

# Get plain text
text = get_cover_letter_text(cover_letter)

# Quick generation
text = quick_cover_letter(structured_jd=jd, resume_json=resume)
```

## Output: CoverLetter

```python
CoverLetter(
    full_text="Dear Hiring Manager,\n\nI am writing to express...",
    candidate_name="John Doe",
    company_name="Amazon",
    date="December 29, 2024",
    word_count=285,
    paragraph_count=4,
    company_mentions=3,
    keywords_used=["machine learning", "Python", "leadership"],
    personalization_score=85.5
)

CompanyResearch(
    industry="Technology / E-commerce",
    core_values=["Customer obsession", "Innovation"],
    recent_news=["AWS launches new ML service..."],
    culture_notes="Fast-paced, data-driven"
)
```

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports |
| `state.py` | CoverLetterGeneratorState, CoverLetter, CompanyResearch |
| `nodes.py` | Node functions |
| `graph.py` | Graph builder and convenience functions |
| `prompts/` | LLM prompts for generation |
| `test.py` | Test script |

## Generation Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `tone` | Writing style | `"professional"` |
| `focus_areas` | Skills to highlight | Auto from JD |
| `referral_name` | Referral contact | None |
| `custom_hook` | Custom opening line | None |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `generate_cover_letter_for_job(structured_jd, resume_json, tone, focus_areas, referral_name, custom_hook)` | Full generation |
| `get_cover_letter_text(cover_letter)` | Extract plain text |
| `get_cover_letter_summary(cover_letter, research)` | Stats summary |
| `quick_cover_letter(structured_jd, resume_json)` | Quick generation |

## Return Value

```python
{
    "cover_letter": CoverLetter,        # Generated letter
    "company_research": CompanyResearch, # Research data
    "search_results": list,              # Web search results
    "generation_complete": bool,
    "error": str | None
}
```

## Cover Letter Structure

1. **Header**: Date, recipient info
2. **Salutation**: "Dear [Name]" or "Dear Hiring Manager"
3. **Opening**: Hook + position + source
4. **Body Paragraph 1**: Relevant experience
5. **Body Paragraph 2**: Skills match + value proposition
6. **Closing**: Call to action + thanks
7. **Signature**: Name + contact

## Company Research

If enabled (`PIPELINE_CONFIG["enable_company_research"]`):
- Web search for company news
- Extract values and culture
- Find recent announcements
- Identify products/services
