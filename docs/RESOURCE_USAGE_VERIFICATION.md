# 🔍 Resource Usage Verification

This document explains exactly **WHERE** and **HOW** each resource file is used in the pipeline.

---

## 📊 RESOURCE USAGE MAP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PIPELINE FLOW                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  JD Extraction ──► Skill Matching ──► GitHub Ranking ──► Experience Rewrite │
│                                                               │              │
│                                                               ▼              │
│                                                    ┌──────────────────────┐  │
│                                                    │  RESOURCES USED:     │  │
│                                                    │  • Action_Verbs.xlsx │  │
│                                                    │  • Resume guide.txt  │  │
│                                                    └──────────────────────┘  │
│                                                               │              │
│                                                               ▼              │
│  Resume JSON Builder ◄─────────────────────────────────────────             │
│         │                                                                    │
│         ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    ATS OPTIMIZATION LOOP                              │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │  RESOURCES USED:                                                │  │   │
│  │  │  • Action_Verbs.xlsx (validate bullet starts)                   │  │   │
│  │  │  • Resume Checklist.txt (compliance check)                      │  │   │
│  │  │  • Resume guide.txt (rewriting guidance)                        │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                       │   │
│  │  Loop until ATS Score ≥ 95                                           │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│         │                                                                    │
│         ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                 RESOURCE COMPLIANCE LOOP                              │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │  RESOURCES USED:                                                │  │   │
│  │  │  • Resume Checklist.txt (all items must pass)                   │  │   │
│  │  │  • Resume rubric.xlsx (score ≥ 3.5/4.0)                         │  │   │
│  │  │  • Action_Verbs.xlsx (verb compliance)                          │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                       │   │
│  │  Loop until all compliance checks pass                               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│         │                                                                    │
│         ▼                                                                    │
│  Cover Letter Generation                                                     │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │  RESOURCES USED:                                                │         │
│  │  • Cover letter guide.txt (structure & rules)                   │         │
│  │  • Cover Letter Checklist.txt (validation)                      │         │
│  │  • Cover letter rubric.xlsx (score ≥ 2.5/3.0)                   │         │
│  └────────────────────────────────────────────────────────────────┘         │
│         │                                                                    │
│         ▼                                                                    │
│  Recruiter Email ──► Excel Writer ──► DONE                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 FILE 1: Action_Verbs.xlsx

### Used In:
1. **Experience Rewriter Subgraph** - Select appropriate verbs for bullets
2. **ATS Optimizer Subgraph** - Validate bullets start with action verbs
3. **Resource Compliance Subgraph** - Final verb compliance check
4. **Rule Engine (MCP Tool)** - `check_action_verb_compliance()`

### How It's Loaded:
```python
from mcp_server.tools.resource_loader import load_action_verbs, get_action_verbs_for_role

# Load all verbs by category
all_verbs = load_action_verbs()
# Returns: {
#   "Management/ Leadership Skills": ["Administered", "Analyzed", ...],
#   "Communication Skills": ["Accounted", "Addressed", ...],
#   "Computer/ Technical Skills": ["Adapted", "Applied", ...],
#   "Financial/ Mathematical Skills": ["Accounted", "Adjusted", ...]
# }

# Get prioritized verbs for a specific role
ml_verbs = get_action_verbs_for_role("Machine Learning Engineer")
# Returns: Technical verbs first, then Communication, then others
```

### How It's Used in Experience Rewriter:
```python
# In modules/experience_rewriter/nodes.py

from mcp_server.tools.resource_loader import get_action_verbs_for_role

def rewrite_experience_node(state):
    role = state.jd_role  # e.g., "ML Engineer"
    
    # Get prioritized verbs for this role type
    prioritized_verbs = get_action_verbs_for_role(role)
    
    # Build prompt with verb guidance
    prompt = f"""
    Rewrite these experience bullets using these action verbs:
    PRIORITIZED VERBS: {', '.join(prioritized_verbs[:20])}
    
    RULES:
    - Start EVERY bullet with an action verb from the list
    - NEVER use the same verb twice consecutively
    - Use past tense for previous jobs, present for current
    
    Original bullets:
    {state.original_bullets}
    """
    
    # LLM rewrites with proper verbs
    rewritten = llm.invoke(prompt)
    return {"rewritten_experience": rewritten}
```

### How It's Used in Rule Engine Validation:
```python
# In mcp_server/tools/rule_engine.py

from mcp_server.tools.resource_loader import get_all_action_verbs_flat

def check_action_verb_compliance(bullet_points: List[str]) -> Dict:
    valid_verbs = get_all_action_verbs_flat()
    valid_verbs_lower = {v.lower() for v in valid_verbs}
    
    results = []
    for bullet in bullet_points:
        first_word = bullet.strip().lstrip("•-").split()[0].rstrip(".,")
        is_valid = first_word.lower() in valid_verbs_lower
        
        results.append({
            "bullet": bullet,
            "first_word": first_word,
            "is_compliant": is_valid,
            "suggestion": None if is_valid else f"Start with: {valid_verbs[:5]}"
        })
    
    compliance_rate = sum(r["is_compliant"] for r in results) / len(results)
    return {
        "compliance_rate": compliance_rate,
        "is_fully_compliant": compliance_rate == 1.0,
        "details": results
    }
```

---

## 📁 FILE 2: Resume Checklist.txt

### Used In:
1. **Resource Compliance Subgraph** - Validate all checklist items
2. **Rule Engine (MCP Tool)** - `validate_resume_rules()`

### How It's Loaded:
```python
from mcp_server.tools.resource_loader import load_resume_checklist

checklist = load_resume_checklist()
# Returns: {
#   "personal_information": ["Name in larger font...", "One phone number..."],
#   "education": ["Institution name...", "Degree title..."],
#   "experience": ["Employer name...", "Bullets start with action verbs..."],
#   "skills": ["Organized by category...", "Technical skills highlighted..."],
#   "format": ["No text boxes...", "Avoid 'responsible for'..."],
#   "content_quality": ["Resume looks original...", "Zero typos..."]
# }
```

### How It's Used in Compliance Validation:
```python
# In modules/resource_compliance/nodes.py

from mcp_server.tools.resource_loader import load_resume_checklist

def check_resume_compliance_node(state):
    checklist = load_resume_checklist()
    resume = state.resume_json
    
    failures = []
    
    # Check personal_information section
    for item in checklist["personal_information"]:
        if "email" in item.lower() and not resume.get("header", {}).get("email"):
            failures.append(f"FAIL: {item}")
        if "phone" in item.lower() and not resume.get("header", {}).get("phone"):
            failures.append(f"FAIL: {item}")
    
    # Check experience section
    for item in checklist["experience"]:
        if "action verbs" in item.lower():
            # Verify all bullets start with action verbs
            for exp in resume.get("experience", []):
                for bullet in exp.get("responsibilities", []):
                    if not starts_with_action_verb(bullet):
                        failures.append(f"FAIL: {item} - '{bullet[:50]}...'")
        
        if "quantified" in item.lower():
            # Check for numbers/percentages
            text = str(resume)
            if not re.search(r'\d+%|\$\d+|\d+x', text):
                failures.append(f"FAIL: {item}")
    
    # Check format section
    for item in checklist["format"]:
        if "responsible for" in item.lower():
            if "responsible for" in str(resume).lower():
                failures.append(f"FAIL: {item}")
    
    return {
        "checklist_passed": len(failures) == 0,
        "failures": failures
    }
```

---

## 📁 FILE 3: Resume guide.txt

### Used In:
1. **Experience Rewriter Subgraph** - Provides writing formula
2. **Resume JSON Builder Subgraph** - Structure guidance
3. **Prompt templates** - Injected into LLM prompts

### How It's Loaded:
```python
from mcp_server.tools.resource_loader import load_resume_guide

guide = load_resume_guide()
# Returns the full text content of the guide
```

### How It's Used in Prompts:
```python
# In modules/experience_rewriter/prompts/main_prompt.txt

You are an expert resume writer. Follow this guide:

{resume_guide}

KEY FORMULA FROM GUIDE:
[ACTION VERB] + [WHAT you did] + [HOW/WITH WHAT] + [RESULT]

QUESTIONS TO ANSWER (from guide):
1. WHAT did you do?
2. HOW did you do it?
3. HOW WELL did you do it (metrics)?

Now rewrite the following experience bullets for this JD:
{jd_requirements}

Original bullets:
{original_bullets}
```

### How It's Loaded in Node:
```python
# In modules/experience_rewriter/nodes.py

from mcp_server.tools.resource_loader import load_resume_guide
from mcp_server.tools.prompt_loader import load_main_prompt

def rewrite_experience_node(state):
    # Load the guide
    guide = load_resume_guide()
    
    # Load prompt template
    prompt_template = load_main_prompt("experience_rewriter")
    
    # Inject guide into prompt
    prompt = prompt_template.format(
        resume_guide=guide,
        jd_requirements=state.jd_requirements,
        original_bullets=state.original_bullets
    )
    
    # LLM generates rewritten bullets following the guide
    result = llm.invoke(prompt)
    return {"rewritten_experience": result}
```

---

## 📁 FILE 4: Resume rubric.xlsx

### Used In:
1. **Resource Compliance Subgraph** - Score resume quality
2. **ATS Optimizer Subgraph** - Quality gate check
3. **Rule Engine (MCP Tool)** - `validate_resume_rules()`

### How It's Loaded:
```python
from mcp_server.tools.resource_loader import load_resume_rubric, calculate_resume_rubric_score

rubric = load_resume_rubric()
# Returns: {
#   "Format": {
#       "weight": 0.25,
#       "scores": {
#           "excellent": "Fills page, no errors, easily scanned",
#           "good": "Almost fills page, single error possible",
#           "average": "Font/spacing not appealing...",
#           "poor": "More white space than words..."
#       }
#   },
#   "Education Section": { "weight": 0.20, "scores": {...} },
#   "Experience Section": { "weight": 0.35, "scores": {...} },
#   "Honors Activities": { "weight": 0.20, "scores": {...} }
# }
```

### How It's Used for Scoring:
```python
# In modules/resource_compliance/nodes.py

from mcp_server.tools.resource_loader import load_resume_rubric, calculate_resume_rubric_score

def score_resume_node(state):
    rubric = load_resume_rubric()
    resume = state.resume_json
    
    # LLM scores each section based on rubric criteria
    section_scores = {}
    
    for category, criteria in rubric.items():
        prompt = f"""
        Score this resume section from 1-4 based on this rubric:
        
        Category: {category}
        Weight: {criteria['weight']}
        
        Scoring Criteria:
        4 (Excellent): {criteria['scores']['excellent']}
        3 (Good): {criteria['scores']['good']}
        2 (Average): {criteria['scores']['average']}
        1 (Poor): {criteria['scores']['poor']}
        
        Resume Section to Score:
        {get_section_content(resume, category)}
        
        Return only the score (1, 2, 3, or 4):
        """
        
        score = int(llm.invoke(prompt).strip())
        section_scores[category.lower().split()[0]] = score
    
    # Calculate weighted score
    # format=4, education=3, experience=4, honors=3
    final_score = calculate_resume_rubric_score({
        "format": section_scores.get("format", 3),
        "education": section_scores.get("education", 3),
        "experience": section_scores.get("experience", 3),
        "honors": section_scores.get("honors", 3)
    })
    
    # Check if passes threshold (3.5/4.0 = 87.5%)
    passes = final_score >= 3.5
    
    return {
        "rubric_score": final_score,
        "section_scores": section_scores,
        "rubric_passed": passes
    }
```

---

## 📁 FILE 5: Cover Letter Checklist.txt

### Used In:
1. **Cover Letter Generator Subgraph** - Generation guidance
2. **Resource Compliance Subgraph** - Validation check

### How It's Used:
```python
# In modules/cover_letter_generator/nodes.py

from mcp_server.tools.resource_loader import load_cover_letter_checklist

def generate_cover_letter_node(state):
    checklist = load_cover_letter_checklist()
    
    prompt = f"""
    Generate a cover letter following this checklist:
    
    RESEARCH (already done):
    {checklist['research']}
    
    INTRODUCTION MUST:
    {chr(10).join('- ' + item for item in checklist['introduction'])}
    
    BODY PARAGRAPHS MUST:
    {chr(10).join('- ' + item for item in checklist['body'])}
    
    CLOSING MUST:
    {chr(10).join('- ' + item for item in checklist['closing'])}
    
    FORMAT REQUIREMENTS:
    {chr(10).join('- ' + item for item in checklist['format'])}
    
    JD Info: {state.structured_jd}
    Candidate Info: {state.resume_summary}
    """
    
    cover_letter = llm.invoke(prompt)
    return {"cover_letter": cover_letter}
```

---

## 📁 FILE 6: Cover letter guide.txt

### Used In:
1. **Cover Letter Generator Subgraph** - Writing guidance
2. **Prompt templates** - Structure and rules

### How It's Used:
```python
# In modules/cover_letter_generator/prompts/main_prompt.txt

You are an expert cover letter writer. Follow this guide:

{cover_letter_guide}

STRUCTURE (from guide):
1. OPENING: Hook + Position + Source + Interest
2. BODY 1: Technical qualifications with specific examples
3. BODY 2: Soft skills and culture fit
4. CLOSING: Thank + Reiterate interest + Specific follow-up plan

CRITICAL RULES (from guide):
- NEVER start with "I am writing to apply for..."
- ALWAYS include company-specific content
- USE keywords from JD naturally
- LIMIT to 3-4 paragraphs, ~300 words

Generate a cover letter for:
Company: {company}
Role: {role}
JD Keywords: {keywords}
Candidate Highlights: {highlights}
```

---

## 📁 FILE 7: Cover letter rubric.xlsx

### Used In:
1. **Resource Compliance Subgraph** - Score cover letter quality
2. **Rule Engine (MCP Tool)** - `validate_cover_letter_rules()`

### How It's Used:
```python
# In modules/resource_compliance/nodes.py

from mcp_server.tools.resource_loader import load_cover_letter_rubric, calculate_cover_letter_rubric_score

def score_cover_letter_node(state):
    rubric = load_cover_letter_rubric()
    cover_letter = state.cover_letter
    
    # Score each section (1-3 scale)
    section_scores = {}
    
    for category, criteria in rubric.items():
        prompt = f"""
        Score this cover letter section from 1-3:
        
        Category: {category}
        
        3 (Excellent): {criteria['scores']['excellent']}
        2 (Average): {criteria['scores']['average']}
        1 (Poor): {criteria['scores']['poor']}
        
        Cover Letter:
        {cover_letter}
        
        Return only the score (1, 2, or 3):
        """
        
        score = int(llm.invoke(prompt).strip())
        section_scores[get_short_name(category)] = score
    
    # Calculate weighted score
    final_score = calculate_cover_letter_rubric_score(section_scores)
    
    # Check threshold (2.5/3.0 = 83.3%)
    passes = final_score >= 2.5
    
    return {
        "cl_rubric_score": final_score,
        "cl_section_scores": section_scores,
        "cl_rubric_passed": passes
    }
```

---

## 🔄 COMPLETE INTEGRATION EXAMPLE

Here's how ALL resources work together in the Resource Compliance node:

```python
# In modules/resource_compliance/nodes.py

from mcp_server.tools.resource_loader import (
    load_action_verbs,
    get_all_action_verbs_flat,
    load_resume_checklist,
    load_resume_rubric,
    calculate_resume_rubric_score,
    load_cover_letter_checklist,
    load_cover_letter_rubric,
    calculate_cover_letter_rubric_score
)
from mcp_server.tools.rule_engine import check_action_verb_compliance

def full_compliance_check_node(state):
    """
    Comprehensive compliance check using ALL resources.
    """
    results = {
        "all_passed": False,
        "resume_checks": {},
        "cover_letter_checks": {},
        "issues": [],
        "suggestions": []
    }
    
    resume = state.resume_json
    cover_letter = state.cover_letter
    
    # =========================================
    # 1. ACTION VERB COMPLIANCE
    # =========================================
    all_bullets = extract_all_bullets(resume)
    verb_result = check_action_verb_compliance(all_bullets)
    
    results["resume_checks"]["action_verbs"] = {
        "passed": verb_result["compliance_rate"] >= 0.95,
        "rate": verb_result["compliance_rate"],
        "details": verb_result["details"]
    }
    
    if not results["resume_checks"]["action_verbs"]["passed"]:
        results["issues"].append("Some bullets don't start with action verbs")
        results["suggestions"].append("Use verbs like: Developed, Implemented, Designed")
    
    # =========================================
    # 2. RESUME CHECKLIST COMPLIANCE
    # =========================================
    checklist = load_resume_checklist()
    checklist_failures = []
    
    # Check each section
    for section, items in checklist.items():
        for item in items:
            if not check_item(resume, item):
                checklist_failures.append(f"{section}: {item}")
    
    results["resume_checks"]["checklist"] = {
        "passed": len(checklist_failures) == 0,
        "failures": checklist_failures
    }
    
    # =========================================
    # 3. RESUME RUBRIC SCORING
    # =========================================
    rubric = load_resume_rubric()
    section_scores = score_resume_sections(resume, rubric)
    rubric_score = calculate_resume_rubric_score(section_scores)
    
    results["resume_checks"]["rubric"] = {
        "passed": rubric_score >= 3.5,
        "score": rubric_score,
        "max_score": 4.0,
        "percentage": rubric_score / 4.0 * 100,
        "section_scores": section_scores
    }
    
    if not results["resume_checks"]["rubric"]["passed"]:
        # Find lowest scoring sections
        lowest = min(section_scores.items(), key=lambda x: x[1])
        results["suggestions"].append(f"Improve {lowest[0]} section (score: {lowest[1]}/4)")
    
    # =========================================
    # 4. COVER LETTER CHECKLIST
    # =========================================
    cl_checklist = load_cover_letter_checklist()
    cl_failures = []
    
    for section, items in cl_checklist.items():
        for item in items:
            if not check_cl_item(cover_letter, item):
                cl_failures.append(f"{section}: {item}")
    
    results["cover_letter_checks"]["checklist"] = {
        "passed": len(cl_failures) == 0,
        "failures": cl_failures
    }
    
    # =========================================
    # 5. COVER LETTER RUBRIC SCORING
    # =========================================
    cl_rubric = load_cover_letter_rubric()
    cl_section_scores = score_cl_sections(cover_letter, cl_rubric)
    cl_rubric_score = calculate_cover_letter_rubric_score(cl_section_scores)
    
    results["cover_letter_checks"]["rubric"] = {
        "passed": cl_rubric_score >= 2.5,
        "score": cl_rubric_score,
        "max_score": 3.0,
        "percentage": cl_rubric_score / 3.0 * 100,
        "section_scores": cl_section_scores
    }
    
    # =========================================
    # 6. FINAL DETERMINATION
    # =========================================
    all_resume_passed = all(
        check["passed"] for check in results["resume_checks"].values()
    )
    all_cl_passed = all(
        check["passed"] for check in results["cover_letter_checks"].values()
    )
    
    results["all_passed"] = all_resume_passed and all_cl_passed
    
    return results
```

---

## 📊 SUMMARY: RESOURCE → MODULE MAPPING

| Resource File | Loaded By | Used In Modules |
|---------------|-----------|-----------------|
| `Action_Verbs.xlsx` | `load_action_verbs()`, `get_action_verbs_for_role()` | Experience Rewriter, ATS Optimizer, Resource Compliance, Rule Engine |
| `Resume Checklist.txt` | `load_resume_checklist()` | Resource Compliance, Rule Engine |
| `Resume guide.txt` | `load_resume_guide()` | Experience Rewriter, Resume JSON Builder |
| `Resume rubric.xlsx` | `load_resume_rubric()`, `calculate_resume_rubric_score()` | Resource Compliance, ATS Optimizer |
| `Cover Letter Checklist.txt` | `load_cover_letter_checklist()` | Cover Letter Generator, Resource Compliance |
| `Cover letter guide.txt` | `load_cover_letter_guide()` | Cover Letter Generator |
| `Cover letter rubric.xlsx` | `load_cover_letter_rubric()`, `calculate_cover_letter_rubric_score()` | Resource Compliance |

---

## ✅ THRESHOLDS FOR PASSING

| Check | Threshold | If Fails |
|-------|-----------|----------|
| Action Verb Compliance | ≥ 95% bullets valid | Loop back to Experience Rewriter |
| Resume Checklist | 100% items pass | Loop back to Experience Rewriter |
| Resume Rubric Score | ≥ 3.5/4.0 (87.5%) | Loop back to Experience Rewriter |
| ATS Score | ≥ 95/100 | Loop back to Experience Rewriter |
| Cover Letter Checklist | 100% items pass | Regenerate Cover Letter |
| Cover Letter Rubric | ≥ 2.5/3.0 (83.3%) | Regenerate Cover Letter |
