# Pipeline Package

The parent graph implementation for the Job Application Assistant.

## Overview

The pipeline orchestrates all 12 subgraphs to process job applications end-to-end with:
- Conditional routing (skip stages on failure)
- Retry loops (ATS optimization until 95%)
- SQLite checkpointing (resume from any stage)
- Configurable parameters

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports |
| `config.py` | All configuration parameters |
| `state.py` | ParentGraphState definition |
| `nodes.py` | 12 node functions (one per subgraph) |
| `graph.py` | Graph builder with conditional edges |
| `runner.py` | Execution & checkpointing |

## Usage

### CLI

```bash
# Run with test JD
python main.py --test

# Run with URL
python main.py --jd-url "https://example.com/job"

# Show config
python main.py --config

# Resume from checkpoint
python main.py --resume <thread_id>
```

### Programmatic

```python
from pipeline import run_pipeline, print_config_summary

# Show configuration
print_config_summary()

# Run pipeline
result = run_pipeline(
    jd_url="https://example.com/job",
    enable_checkpoints=True
)

if result["success"]:
    print(f"ATS Score: {result['ats_score']}%")
    print(f"Output: {result['output_folder']}")
```

## Configuration

Edit `config.py` to customize:

```python
RESUME_CONFIG = {
    "max_experiences": 4,
    "max_projects": 3,
    "summary_max_words": 60,
}

ATS_CONFIG = {
    "target_score": 95,
    "max_iterations": 3,
}

PIPELINE_CONFIG = {
    "compliance_pass_threshold": 85,
    "enable_email_generation": True,
    "save_to_excel": True,
}
```

## Graph Flow

```
START → extract_jd → match_skills → select_experiences → rank_projects
                                                              ↓
      rewrite_content ← ─────────────────────────────────────┘
            ↓
      build_resume → optimize_ats ←──┐
            ↓              ↓         │
      [score < 95%]────────┘         │
            ↓                        │
      check_compliance               │
            ↓                        │
      generate_cover_letter          │
            ↓                        │
      check_cl_compliance            │
            ↓                        │
      generate_email                 │
            ↓                        │
      save_to_excel                  │
            ↓                        │
      save_outputs → END             │
```

## Conditional Edges

| After Node | Condition | Routes To |
|------------|-----------|-----------|
| `extract_jd` | extraction failed? | `save_outputs` |
| `build_resume` | no resume built? | `generate_cover_letter` |
| `optimize_ats` | score < 95%? | `optimize_ats` (retry) |
| `generate_cover_letter` | no cover letter? | `generate_email` |
