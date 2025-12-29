# State Architecture

**Last Updated:** December 29, 2024

## Overview

The Job Application Assistant uses a two-level state architecture:

1. **Subgraph States** - Specific to each subgraph
2. **Parent Graph State** - Unified state for the pipeline

## State Models Location

```
state/
└── state_models.py    # All shared models (StructuredJD, ResumeJSON, etc.)

pipeline/
└── state.py           # ParentGraphState (pipeline-specific)

subgraphs/{name}/
└── state.py           # Subgraph-specific state
```

## Core Data Models

### StructuredJD (JD Extractor Output)

```python
class StructuredJD(BaseModel):
    company_name: str
    role_title: str
    role_type: str  # ml_ai, data_science, research, etc.
    location: str
    employment_type: str
    experience_required: str
    
    skills_required: List[str]
    skills_preferred: List[str]
    responsibilities: List[str]
    qualifications: List[str]
    keywords: List[str]  # ATS keywords
    
    company_info: str
    extraction_confidence: float
```

### SkillMatchResult (Skill Matcher Output)

```python
class SkillMatchResult(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    partial_matches: List[str]
    additional_skills: List[str]
    
    match_percentage: float
    skill_gap_analysis: str
    critical_missing: List[str]
```

### SelectedProject (GitHub Ranker Output)

```python
class SelectedProject(BaseModel):
    name: str
    github_url: str
    description: str
    tech_stack: Dict[str, List[str]]
    
    relevance_score: float
    matching_skills: List[str]
    
    bullets: List[str]
    metrics: List[str]
    key_features: List[str]
```

### SelectedExperience (Experience Selector Output)

```python
class SelectedExperience(BaseModel):
    id: int
    role: str
    company: str
    dates: Dict[str, Any]
    location: Dict[str, Any]
    
    relevance_score: float
    matching_keywords: List[str]
    
    original_bullets: List[str]
    rewritten_bullets: List[str]
    keywords_incorporated: List[str]
```

### ResumeJSON (Resume Builder Output)

```python
class ResumeJSON(BaseModel):
    header: Dict[str, str]  # name, email, phone, linkedin, github
    summary: str
    
    education: List[Dict]
    certifications: List[str]
    
    experience: List[Dict]
    projects: List[Dict]
    
    skills: Dict[str, str]  # Category: "skill1, skill2, ..."
    publications: List[str]
    
    version: int
    tailored_for: str
```

### ATSAnalysis (ATS Optimizer Output)

```python
class ATSAnalysis(BaseModel):
    score: int  # 0-100
    
    keyword_density: float
    keywords_found: List[str]
    keywords_missing: List[str]
    
    format_issues: List[str]
    section_scores: Dict[str, int]
    
    suggestions: List[str]
    passed: bool
```

### ComplianceResult (Resource Compliance Output)

```python
class ComplianceResult(BaseModel):
    checklist_passed: bool
    checklist_failures: List[str]
    
    rubric_score: float
    rubric_section_scores: Dict[str, int]
    rubric_passed: bool
    
    action_verb_compliance: float
    issues: List[str]
    suggestions: List[str]
```

## Pipeline State

### ParentGraphState

The parent graph uses a simplified state that holds outputs from each subgraph:

```python
class ParentGraphState(BaseModel):
    # Inputs
    jd_url: Optional[str] = None
    jd_text: Optional[str] = None
    
    # Stage 1: JD Extraction
    structured_jd: Optional[Any] = None
    extraction_error: Optional[str] = None
    
    # Stage 2: Skill Matching
    skill_match_result: Optional[Any] = None
    match_percentage: float = 0.0
    
    # Stage 3: Selection
    selected_experiences: List[Any] = []
    selected_projects: List[Any] = []
    
    # Stage 4: Rewriting
    rewritten_experiences: List[Any] = []
    rewritten_projects: List[Any] = []
    
    # Stage 5: Resume
    resume_json: Optional[Any] = None
    
    # Stage 6: ATS
    ats_score: float = 0.0
    ats_passed: bool = False
    ats_iteration: int = 0
    
    # Stage 7: Compliance
    compliance_score: float = 0.0
    compliance_passed: bool = False
    
    # Stage 8-9: Cover Letter
    cover_letter: Optional[Any] = None
    cover_letter_text: str = ""
    cl_compliance_score: float = 0.0
    
    # Stage 10: Email
    email: Optional[Any] = None
    email_text: str = ""
    
    # Stage 11: Excel
    excel_saved: bool = False
    
    # Stage 12: Outputs
    output_folder: str = ""
    
    # Control
    current_stage: str = ""
    error_message: Optional[str] = None
```

## State Flow

```
Input (jd_url/jd_text)
        │
        ▼
┌───────────────────┐
│ structured_jd     │ ← JD Extractor
└───────┬───────────┘
        │
        ├───────────────────────────────────┐
        │                                   │
        ▼                                   ▼
┌───────────────────┐             ┌───────────────────┐
│ skill_match_result│             │ selected_projects │
│                   │             │ selected_experiences│
└───────┬───────────┘             └───────┬───────────┘
        │                                 │
        │                                 ▼
        │                       ┌───────────────────┐
        │                       │ rewritten_*       │
        │                       └───────┬───────────┘
        │                               │
        └───────────────┬───────────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ resume_json       │ ← Resume Builder
              └───────┬───────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────────┐     ┌───────────────────┐
│ ats_score         │     │ compliance_score  │
│ ats_passed        │     │ compliance_passed │
└───────┬───────────┘     └───────┬───────────┘
        │                         │
        └───────────┬─────────────┘
                    │
                    ▼
          ┌───────────────────┐
          │ cover_letter      │
          │ cover_letter_text │
          └───────┬───────────┘
                  │
                  ▼
          ┌───────────────────┐
          │ email             │
          │ email_text        │
          └───────┬───────────┘
                  │
                  ▼
          ┌───────────────────┐
          │ excel_saved       │
          │ output_folder     │
          └───────────────────┘
```

## Subgraph State Pattern

Each subgraph has its own state that includes:

```python
class {Name}State(BaseModel):
    # Inputs (from parent or previous subgraph)
    structured_jd: Optional[StructuredJD] = None
    ...
    
    # Intermediate data
    ...
    
    # Outputs
    ...
    
    # Control flags
    {name}_complete: bool = False
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
```

## State Synchronization

Nodes in the parent graph call subgraph convenience functions and update parent state:

```python
def node_match_skills(state: ParentGraphState) -> Dict[str, Any]:
    # Call subgraph function
    result = match_skills_to_jd(structured_jd=state.structured_jd)
    
    # Return state updates
    return {
        "skill_match_result": result.get("skill_match_result"),
        "match_percentage": result.get("match_percentage", 0),
        "current_stage": "skills_matched"
    }
```

## Best Practices

1. **Use Optional types** for nullable fields
2. **Use `Field(default_factory=list)`** for mutable defaults
3. **Set `arbitrary_types_allowed = True`** for Pydantic models with complex types
4. **Return dict updates** from nodes (not full state objects)
5. **Keep state flat** - avoid deeply nested structures
