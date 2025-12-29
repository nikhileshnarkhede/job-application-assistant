# 🧠 State Architecture for Job Application Pipeline

## Core Principle
```
ParentState = JDExtractor + SkillMatcher + GitHubRanker + ExperienceSelector 
            + ExperienceRewriter + ResumeBuilder + ATSOptimizer 
            + ResourceCompliance + CoverLetterGenerator + EmailGenerator 
            + ExcelWriter + PipelineControl + Resources + Metadata
```

---

## 📊 State Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PARENT STATE                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  INPUT                           CANDIDATE DATA (pre-loaded)                     │
│  ┌─────────────────┐            ┌──────────────────────────────┐                │
│  │ raw_jd_text     │            │ candidate_header             │                │
│  └────────┬────────┘            │ candidate_summary            │                │
│           │                     │ candidate_education          │                │
│           ▼                     │ candidate_certifications     │                │
│  ┌─────────────────┐            │ candidate_skills             │                │
│  │  JD EXTRACTOR   │            │ candidate_skills_flat        │                │
│  │                 │            │ candidate_publications       │                │
│  │ OUT:            │            │ candidate_experiences        │                │
│  │ structured_jd   │            └──────────────────────────────┘                │
│  └────────┬────────┘                                                            │
│           │                                                                      │
│           ├──────────────────┬─────────────────┬────────────────┐               │
│           ▼                  ▼                 ▼                ▼               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐                   │
│  │ SKILL MATCHER   │ │ GITHUB RANKER   │ │ EXP SELECTOR    │                   │
│  │                 │ │                 │ │                 │                   │
│  │ OUT:            │ │ OUT:            │ │ OUT:            │                   │
│  │ skill_match_    │ │ selected_       │ │ selected_       │                   │
│  │ result          │ │ projects        │ │ experiences     │                   │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘                   │
│           │                   │                   │                             │
│           │                   └─────────┬─────────┘                             │
│           │                             ▼                                       │
│           │                    ┌─────────────────┐                              │
│           │                    │ EXP REWRITER    │                              │
│           │                    │                 │                              │
│           │                    │ OUT:            │                              │
│           │                    │ rewritten_      │                              │
│           │                    │ experiences     │                              │
│           │                    │ rewritten_      │                              │
│           │                    │ projects        │                              │
│           │                    └────────┬────────┘                              │
│           │                             │                                       │
│           │                             ▼                                       │
│           │                    ┌─────────────────┐                              │
│           │                    │ RESUME BUILDER  │                              │
│           │                    │                 │                              │
│           │                    │ OUT:            │                              │
│           │                    │ resume_json     │                              │
│           │                    └────────┬────────┘                              │
│           │                             │                                       │
│           │                             ▼                                       │
│           │                    ┌─────────────────┐                              │
│           │                    │ ATS OPTIMIZER   │◄──┐                          │
│           │                    │                 │   │ Loop until               │
│           │                    │ OUT:            │   │ ats_passed=True          │
│           │                    │ ats_analysis    │   │ (score ≥ 95)             │
│           │                    │ ats_passed      │───┘                          │
│           │                    └────────┬────────┘                              │
│           │                             │                                       │
│           │                             ▼                                       │
│           │                    ┌─────────────────┐                              │
│           │                    │ RESOURCE        │◄──┐                          │
│           │                    │ COMPLIANCE      │   │ Loop until               │
│           │                    │                 │   │ compliance_passed=True   │
│           │                    │ OUT:            │   │ (rubric ≥ 3.5)           │
│           │                    │ compliance_     │───┘                          │
│           │                    │ result          │                              │
│           │                    │ compliance_     │                              │
│           │                    │ passed          │                              │
│           │                    └────────┬────────┘                              │
│           │                             │                                       │
│           ▼                             ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐               │
│  │                    COVER LETTER GENERATOR                    │               │
│  │                                                              │               │
│  │  OUT: cover_letter_text, cover_letter_json                   │               │
│  └─────────────────────────────┬───────────────────────────────┘               │
│                                │                                                │
│                                ▼                                                │
│                       ┌─────────────────┐                                       │
│                       │ CL COMPLIANCE   │◄──┐                                   │
│                       │                 │   │ Loop until                        │
│                       │ OUT:            │   │ cl_passed=True                    │
│                       │ cl_compliance_  │   │ (rubric ≥ 2.5)                    │
│                       │ result          │───┘                                   │
│                       │ cl_passed       │                                       │
│                       └────────┬────────┘                                       │
│                                │                                                │
│                                ▼                                                │
│                       ┌─────────────────┐                                       │
│                       │ EMAIL GENERATOR │                                       │
│                       │                 │                                       │
│                       │ OUT:            │                                       │
│                       │ recruiter_email │                                       │
│                       └────────┬────────┘                                       │
│                                │                                                │
│                                ▼                                                │
│                       ┌─────────────────┐                                       │
│                       │ EXCEL WRITER    │                                       │
│                       │                 │                                       │
│                       │ OUT:            │                                       │
│                       │ output_files    │                                       │
│                       │ excel_updated   │                                       │
│                       │ application_id  │                                       │
│                       └─────────────────┘                                       │
│                                                                                  │
│  RESOURCES (pre-loaded)              PIPELINE CONTROL                           │
│  ┌────────────────────────┐         ┌────────────────────────┐                 │
│  │ action_verbs           │         │ pipeline_status        │                 │
│  │ resume_checklist       │         │ current_stage          │                 │
│  │ resume_rubric          │         │ error_message          │                 │
│  │ cover_letter_checklist │         │ total_iterations       │                 │
│  │ cover_letter_rubric    │         │ created_at             │                 │
│  │ resume_guide           │         │ last_updated           │                 │
│  │ cover_letter_guide     │         └────────────────────────┘                 │
│  └────────────────────────┘                                                     │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Subgraph State Requirements

### 1️⃣ JD Extractor
| Input | Output |
|-------|--------|
| `raw_jd_text` | `structured_jd` |
|  | `extraction_error` |

### 2️⃣ Skill Matcher
| Input | Output |
|-------|--------|
| `structured_jd` | `skill_match_result` |
| `candidate_skills_flat` | |

### 3️⃣ GitHub Ranker
| Input | Output |
|-------|--------|
| `structured_jd` | `selected_projects` |
| `max_projects` | |

### 4️⃣ Experience Selector
| Input | Output |
|-------|--------|
| `structured_jd` | `selected_experiences` |
| `candidate_experiences` | |
| `max_experiences` | |

### 5️⃣ Experience Rewriter
| Input | Output |
|-------|--------|
| `structured_jd` | `rewritten_experiences` |
| `selected_experiences` | `rewritten_projects` |
| `selected_projects` | `rewrite_iteration` |
| `action_verbs` | |
| `resume_guide` | |

### 6️⃣ Resume Builder
| Input | Output |
|-------|--------|
| `structured_jd` | `resume_json` |
| `candidate_header` | `resume_version` |
| `candidate_summary` | |
| `candidate_education` | |
| `candidate_certifications` | |
| `candidate_skills` | |
| `candidate_publications` | |
| `rewritten_experiences` | |
| `rewritten_projects` | |

### 7️⃣ ATS Optimizer
| Input | Output |
|-------|--------|
| `structured_jd` | `ats_analysis` |
| `resume_json` | `ats_iteration` |
| `max_ats_iterations` | `ats_passed` |
| | `resume_json` (updated) |

### 8️⃣ Resource Compliance
| Input | Output |
|-------|--------|
| `resume_json` | `compliance_result` |
| `resume_checklist` | `compliance_iteration` |
| `resume_rubric` | `compliance_passed` |
| `action_verbs` | `resume_json` (updated) |
| `max_compliance_iterations` | |

### 9️⃣ Cover Letter Generator
| Input | Output |
|-------|--------|
| `structured_jd` | `cover_letter_text` |
| `candidate_header` | `cover_letter_json` |
| `candidate_summary` | `cl_iteration` |
| `skill_match_result` | |
| `selected_experiences` | |
| `cover_letter_guide` | |
| `cover_letter_checklist` | |

### 🔟 Cover Letter Compliance
| Input | Output |
|-------|--------|
| `cover_letter_text` | `cl_compliance_result` |
| `cover_letter_checklist` | `cl_iteration` |
| `cover_letter_rubric` | `cl_passed` |
| `max_cl_iterations` | `cover_letter_text` (updated) |

### 1️⃣1️⃣ Email Generator
| Input | Output |
|-------|--------|
| `structured_jd` | `recruiter_email` |
| `candidate_header` | |
| `candidate_summary` | |

### 1️⃣2️⃣ Excel Writer
| Input | Output |
|-------|--------|
| `structured_jd` | `excel_updated` |
| `ats_analysis` | `application_id` |
| `compliance_result` | |
| `cl_compliance_result` | |
| `output_files` | |

---

## 🎯 Key Data Models

### StructuredJD
```python
class StructuredJD:
    company_name: str
    role_title: str
    role_type: str          # ml_ai, data_science, etc.
    location: str
    employment_type: str
    experience_required: str
    skills_required: List[str]
    skills_preferred: List[str]
    responsibilities: List[str]
    qualifications: List[str]
    keywords: List[str]     # ATS keywords
    company_info: str
```

### SkillMatchResult
```python
class SkillMatchResult:
    matched_skills: List[str]
    missing_skills: List[str]
    partial_matches: List[str]
    additional_skills: List[str]
    match_percentage: float
    skill_gap_analysis: str
```

### SelectedExperience
```python
class SelectedExperience:
    id: int
    role: str
    company: str
    dates: Dict[str, str]
    location: Dict[str, str]
    relevance_score: float
    original_bullets: List[str]
    rewritten_bullets: List[str]
    keywords_incorporated: List[str]
```

### ResumeJSON
```python
class ResumeJSON:
    header: Dict[str, str]
    summary: str
    education: List[Dict]
    certifications: List[str]
    experience: List[Dict]
    projects: List[Dict]
    skills: Dict[str, str]
    publications: List[str]
```

### ATSAnalysis
```python
class ATSAnalysis:
    score: int              # 0-100
    keyword_density: float
    keywords_found: List[str]
    keywords_missing: List[str]
    format_issues: List[str]
    suggestions: List[str]
    passed: bool            # score >= 95
```

### ComplianceResult
```python
class ComplianceResult:
    checklist_passed: bool
    checklist_failures: List[str]
    rubric_score: float     # 0-4.0
    rubric_passed: bool     # score >= 3.5
    action_verb_compliance: float
    all_passed: bool
    suggestions: List[str]
```

---

## 🔄 Loop Conditions

| Loop | Condition | Max Iterations |
|------|-----------|----------------|
| **ATS Optimizer** | `ats_passed == False` | 3 |
| **Resource Compliance** | `compliance_passed == False` | 3 |
| **Cover Letter Compliance** | `cl_passed == False` | 3 |

---

## 📁 File Location
```
state/
├── __init__.py
└── state_models.py     # All state definitions
```

## 🔧 Usage
```python
from state import (
    ParentState,
    create_initial_state,
    StructuredJD,
    SkillMatchResult,
    # ... etc
)

# Create initial state
state = create_initial_state(raw_jd_text="...")

# Access fields
print(state.structured_jd)
print(state.ats_passed)
```
