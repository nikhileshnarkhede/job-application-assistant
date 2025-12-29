# JD Extractor Subgraph

Extracts structured information from job descriptions using LLM.

## Overview

The JD Extractor subgraph parses raw job descriptions (from URLs or text) and extracts structured data including:
- Company name and role title
- Required and preferred skills
- Keywords for ATS optimization
- Responsibilities and qualifications
- Role type classification

## Graph Flow

```
START ──► input_router ──┬──► url_fetcher ──► jd_extractor ──►─┤
                         │                         │            │
                         └─────────────────────►───┘            │
                                (text input)                    │
                                                                │
                         ┌──────────────────────────────────────┘
                         │
                         ▼
                  validation_node ──┬──► END (success)
                         │          │
                         │          └──► error_handler ──► END (failure)
                         │                    │
                         └────────────────────┘ (retry loop, max 2)
```

## Usage

```python
from subgraphs import extract_jd_from_text, extract_jd_from_url

# From URL
result = extract_jd_from_url("https://example.com/job-posting")
structured_jd = result["structured_jd"]

# From text
result = extract_jd_from_text("We are looking for a Machine Learning Engineer...")
structured_jd = result["structured_jd"]
```

## Output: StructuredJD

```python
StructuredJD(
    company_name="Amazon",
    role_title="Applied Scientist",
    role_type="ml_ai",  # ml_ai, data_science, research, etc.
    location="Seattle, WA",
    employment_type="Full-time",
    experience_required="3+ years",
    skills_required=["Python", "Machine Learning", "Deep Learning"],
    skills_preferred=["NLP", "Computer Vision"],
    responsibilities=["Design ML models", "Deploy to production"],
    qualifications=["PhD or Master's in CS/ML"],
    keywords=["machine learning", "python", "tensorflow"],
    extraction_confidence=0.95
)
```

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports |
| `state.py` | JDExtractorState definition |
| `nodes.py` | Node functions (input_router, url_fetcher, jd_extractor, validation_node) |
| `graph.py` | Graph builder and convenience functions |
| `test.py` | Test script |
| `prompts/` | LLM prompts (system, main, few-shot examples) |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `extract_jd_from_text(text)` | Extract from raw text |
| `extract_jd_from_url(url)` | Extract from URL (fetches page content) |
| `create_jd_extractor_subgraph()` | Get compiled graph for direct invocation |

## Return Value

```python
{
    "structured_jd": StructuredJD,  # Extracted data
    "error": str | None,            # Error message if failed
    "validation_passed": bool,       # Whether validation passed
    "fetched_content": str           # (URL only) Raw page content
}
```

## Supported URL Formats

- LinkedIn job postings
- Greenhouse job boards
- Lever job boards
- Indeed listings
- Generic HTML pages with job content

## Configuration

The LLM model is configured via environment variable:
```bash
OPENAI_MODEL=gpt-4o-mini  # Default
```

## Error Handling

- **URL fetch failures**: Falls back to STANDARD_JD_TEXT for Amazon URLs
- **LLM parsing errors**: Retries up to 2 times
- **Validation failures**: Accepts with warnings after max retries
