# Excel Writer Subgraph

Saves job applications to an Excel tracking spreadsheet.

## Overview

The Excel Writer subgraph manages job application tracking by:
- Creating/updating tracking spreadsheet
- Recording application details and scores
- Supporting status updates
- Providing application statistics

## Graph Flow

```
START ──► prepare_record ──► load_or_create_workbook ──► write_record ──► format_spreadsheet ──► save_workbook ──► END
```

## Usage

```python
from subgraphs import (
    save_application_to_excel,
    quick_save_application,
    update_application_status,
    get_application_stats,
    get_applications_summary,
    ApplicationStatus,
    ApplicationSource
)

# Full save with all data
result = save_application_to_excel(
    structured_jd=jd,
    resume_json=resume,
    resume_score=92.0,
    cover_letter_score=85.0,
    file_path="job_applications.xlsx",
    status=ApplicationStatus.APPLIED,
    source=ApplicationSource.LINKEDIN,
    notes="Great match for my skills",
    why_interested="Leading ML team"
)
print(f"Saved to row: {result['row_number']}")

# Quick save (minimal data)
result = quick_save_application(
    company="Amazon",
    role="ML Engineer",
    job_url="https://amazon.jobs/...",
    status=ApplicationStatus.APPLIED,
    source=ApplicationSource.COMPANY_WEBSITE
)

# Update status
update_application_status(
    file_path="job_applications.xlsx",
    application_id="AMZN-20241229",
    new_status=ApplicationStatus.PHONE_SCREEN,
    notes="Scheduled for Jan 5"
)

# Get statistics
stats = get_application_stats("job_applications.xlsx")
print(f"Total: {stats['total']}")
print(f"By Status: {stats['by_status']}")

# Get summary
summary = get_applications_summary("job_applications.xlsx")
print(summary)
```

## Application Status

| Status | Description |
|--------|-------------|
| `NOT_APPLIED` | Saved but not applied |
| `APPLIED` | Application submitted |
| `PHONE_SCREEN` | Phone screen scheduled/completed |
| `TECHNICAL_INTERVIEW` | Technical interview stage |
| `ONSITE` | Onsite interview stage |
| `OFFER` | Offer received |
| `REJECTED` | Application rejected |
| `WITHDRAWN` | Withdrew application |

## Application Source

| Source | Description |
|--------|-------------|
| `LINKEDIN` | Found on LinkedIn |
| `INDEED` | Found on Indeed |
| `COMPANY_WEBSITE` | Direct company careers page |
| `REFERRAL` | Referred by someone |
| `RECRUITER` | Contacted by recruiter |
| `OTHER` | Other source |

## Output: ApplicationRecord

```python
ApplicationRecord(
    application_id="AMZN-20241229-001",
    company="Amazon",
    role="Machine Learning Engineer",
    department="AWS AI",
    location="Seattle, WA",
    employment_type="Full-time",
    salary_range="$180K-$250K",
    job_url="https://amazon.jobs/...",
    
    status=ApplicationStatus.APPLIED,
    source=ApplicationSource.LINKEDIN,
    
    date_found="2024-12-29",
    date_applied="2024-12-29",
    date_updated="2024-12-29",
    
    resume_score=92.0,
    cover_letter_score=85.0,
    match_percentage=88.5,
    
    recruiter_name="Jane Smith",
    recruiter_email="jsmith@amazon.com",
    recruiter_phone="",
    
    notes="Strong match, referred by colleague",
    why_interested="Leading ML research team",
    next_steps="Follow up in 1 week",
    
    resume_version=1,
    cover_letter_version=1,
    files_folder="applications/amazon_20241229/"
)
```

## Excel Columns (26 total)

| Column | Type | Description |
|--------|------|-------------|
| Application ID | String | Unique identifier |
| Company | String | Company name |
| Role | String | Job title |
| Status | Dropdown | Current status |
| Date Applied | Date | Application date |
| Resume Score | Number | ATS/Compliance score |
| ... | ... | (see full schema) |

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports |
| `state.py` | ExcelWriterState, ApplicationRecord, ApplicationStatus, ApplicationSource |
| `nodes.py` | Node functions |
| `graph.py` | Graph builder and convenience functions |
| `test.py` | Test script |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `save_application_to_excel(...)` | Full save with all fields |
| `quick_save_application(...)` | Quick save with minimal fields |
| `update_application_status(...)` | Update status of existing application |
| `get_application_stats(file_path)` | Get statistics |
| `get_applications_summary(file_path)` | Human-readable summary |

## Return Value

```python
{
    "file_path": str,                    # Path to Excel file
    "row_number": int,                   # Row where saved
    "write_complete": bool,
    "application_record": ApplicationRecord,
    "error": str | None
}
```

## Statistics Output

```python
{
    "total": 50,
    "by_status": {
        "APPLIED": 30,
        "PHONE_SCREEN": 10,
        "REJECTED": 8,
        "OFFER": 2
    },
    "by_source": {
        "LINKEDIN": 25,
        "COMPANY_WEBSITE": 15,
        "REFERRAL": 10
    },
    "unique_companies": 35,
    "top_companies": ["Amazon", "Google", "Meta"]
}
```
