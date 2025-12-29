# Pipeline Documentation

**Last Updated:** December 29, 2024

## Overview

The pipeline is the parent graph that orchestrates all 12 subgraphs to process job applications end-to-end.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              PIPELINE                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   pipeline/                                                              │
│   ├── config.py      # Configuration parameters                         │
│   ├── state.py       # ParentGraphState                                  │
│   ├── nodes.py       # 12 node functions                                 │
│   ├── graph.py       # Graph builder with conditional edges             │
│   └── runner.py      # Execution & checkpointing                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Graph Flow

```
START
  │
  ▼
┌──────────────────┐
│ 1. Extract JD    │──────[fail]──────────────────────────────────┐
└────────┬─────────┘                                              │
         │ [success]                                              │
         ▼                                                        │
┌──────────────────┐                                              │
│ 2. Match Skills  │                                              │
└────────┬─────────┘                                              │
         ▼                                                        │
┌──────────────────┐                                              │
│ 3a. Select Exp   │                                              │
└────────┬─────────┘                                              │
         ▼                                                        │
┌──────────────────┐                                              │
│ 3b. Rank Projects│  (GitHub API)                                │
└────────┬─────────┘                                              │
         ▼                                                        │
┌──────────────────┐                                              │
│ 4. Rewrite       │                                              │
└────────┬─────────┘                                              │
         ▼                                                        │
┌──────────────────┐                                              │
│ 5. Build Resume  │──────[no resume]─────────────────┐           │
└────────┬─────────┘                                  │           │
         │ [resume built]                             │           │
         ▼                                            │           │
┌──────────────────┐                                  │           │
│ 6. ATS Optimize  │◄──────┐                          │           │
└────────┬─────────┘       │                          │           │
         │                 │                          │           │
    [score < 95%]──────────┘                          │           │
         │                                            │           │
    [score >= 95%]                                    │           │
         ▼                                            │           │
┌──────────────────┐                                  │           │
│ 7. Compliance    │                                  │           │
└────────┬─────────┘                                  │           │
         │                                            │           │
         ▼                                            │           │
┌──────────────────┐◄─────────────────────────────────┘           │
│ 8. Cover Letter  │                                              │
└────────┬─────────┘                                              │
         │                                                        │
    [has CL]────────┐                                             │
         │          │                                             │
         ▼          │                                             │
┌──────────────────┐│                                             │
│ 9. CL Compliance ││                                             │
└────────┬─────────┘│                                             │
         │          │                                             │
         ▼          ▼                                             │
┌──────────────────┐◄──[no CL]                                    │
│ 10. Email        │                                              │
└────────┬─────────┘                                              │
         ▼                                                        │
┌──────────────────┐                                              │
│ 11. Excel Track  │                                              │
└────────┬─────────┘                                              │
         ▼                                                        │
┌──────────────────┐◄─────────────────────────────────────────────┘
│ 12. Save Outputs │
└────────┬─────────┘
         ▼
        END
```

## Conditional Edges

| After Node | Condition | Routes To |
|------------|-----------|-----------|
| `extract_jd` | extraction failed? | `save_outputs` (skip all) |
| `build_resume` | no resume built? | `generate_cover_letter` (skip ATS) |
| `optimize_ats` | score < 95% & iterations left? | `optimize_ats` (retry) |
| `generate_cover_letter` | no cover letter? | `generate_email` (skip CL compliance) |

## Configuration

### pipeline/config.py

```python
RESUME_CONFIG = {
    "max_experiences": 4,
    "bullets_per_experience": 4,
    "max_projects": 3,
    "summary_max_words": 60,
}

ATS_CONFIG = {
    "target_score": 95,
    "max_iterations": 3,
}

PIPELINE_CONFIG = {
    "max_ats_iterations": 3,
    "max_compliance_iterations": 3,
    "ats_pass_threshold": 95,
    "compliance_pass_threshold": 85,
    "enable_email_generation": True,
    "save_to_excel": True,
}

PATHS_CONFIG = {
    "output_folder": "applications",
    "excel_file": "job_applications.xlsx",
    "checkpoints_folder": "data/checkpoints",
}
```

## State Model

### pipeline/state.py

```python
class ParentGraphState(BaseModel):
    # Inputs
    jd_url: Optional[str] = None
    jd_text: Optional[str] = None
    
    # Stage outputs
    structured_jd: Optional[Any] = None
    skill_match_result: Optional[Any] = None
    selected_experiences: List[Any] = []
    selected_projects: List[Any] = []
    rewritten_experiences: List[Any] = []
    rewritten_projects: List[Any] = []
    resume_json: Optional[Any] = None
    
    # Scores
    ats_score: float = 0.0
    ats_passed: bool = False
    compliance_score: float = 0.0
    compliance_passed: bool = False
    
    # Cover letter & email
    cover_letter: Optional[Any] = None
    cover_letter_text: str = ""
    email: Optional[Any] = None
    email_text: str = ""
    
    # Control
    current_stage: str = ""
    error_message: Optional[str] = None
```

## Node Functions

### pipeline/nodes.py

Each node calls one subgraph's convenience function:

| Node | Subgraph | Function Called |
|------|----------|-----------------|
| `node_extract_jd` | jd_extractor | `extract_jd_from_url()` / `extract_jd_from_text()` |
| `node_match_skills` | skill_matcher | `match_skills_to_jd()` |
| `node_select_experiences` | experience_selector | `select_experiences_for_jd()` |
| `node_rank_projects` | github_ranker | `rank_github_projects()` |
| `node_rewrite_content` | experience_rewriter | `rewrite_for_jd()` |
| `node_build_resume` | resume_builder | `build_resume()` |
| `node_optimize_ats` | ats_optimizer | `optimize_resume_for_ats()` |
| `node_check_compliance` | resource_compliance | `validate_resume_compliance()` |
| `node_generate_cover_letter` | cover_letter_generator | `generate_cover_letter_for_job()` |
| `node_check_cl_compliance` | cover_letter_compliance | `validate_cover_letter_compliance()` |
| `node_generate_email` | email_generator | `generate_outreach_email()` |
| `node_save_to_excel` | excel_writer | `save_application_to_excel()` |
| `node_save_outputs` | (internal) | Saves files to disk |

## Execution

### CLI Usage

```bash
# Run with test JD
python main.py --test

# Run with URL
python main.py --jd-url "https://example.com/job"

# Run with text
python main.py --jd-text "Job description..."

# Show config
python main.py --config

# List checkpoints
python main.py --list-checkpoints

# Resume from checkpoint
python main.py --resume <thread_id>
```

### Programmatic Usage

```python
from pipeline import run_pipeline

result = run_pipeline(
    jd_url="https://example.com/job",
    enable_checkpoints=True
)

if result["success"]:
    print(f"ATS Score: {result['ats_score']}%")
    print(f"Output: {result['output_folder']}")
```

## Checkpointing

SQLite-based checkpointing allows resuming from any stage:

```python
from pipeline import list_checkpoints, run_pipeline

# List available checkpoints
threads = list_checkpoints()

# Resume from checkpoint
result = run_pipeline(resume_from="abc12345")
```

## Output Structure

```
applications/{company}_{timestamp}/
├── resume.json           # Structured resume data
├── cover_letter.txt      # Generated cover letter
├── email.txt             # Outreach email
└── metadata.json         # Scores and metrics
```
