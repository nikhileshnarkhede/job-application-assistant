# 🧠 LLM STRATEGIC GUIDE: Resource Files Usage

This document provides strategic guidance for how the LLM should interpret and use each resource file in the Job Application Assistant system.

---

## 📊 OVERVIEW OF RESOURCES

| File | Purpose | Usage Context |
|------|---------|---------------|
| `Action_Verbs.xlsx` | Provides categorized action verbs | Experience rewriting, Resume building |
| `Resume Checklist.txt` | Validation checklist | Resume compliance checking |
| `Resume guide.txt` | Best practices guide | Resume generation guidance |
| `Resume rubric.xlsx` | 4-level scoring rubric | Resume quality scoring |
| `Cover Letter Checklist.txt` | Validation checklist | Cover letter compliance |
| `Cover letter guide.txt` | Writing guide | Cover letter generation |
| `Cover letter rubric.xlsx` | 3-level scoring rubric | Cover letter quality scoring |

---

## 📁 FILE 1: Action_Verbs.xlsx

### Structure
- **4 Categories**: Management/Leadership, Communication, Computer/Technical, Financial/Mathematical
- **73 unique verbs** across categories
- Organized by skill type for contextual selection

### Strategic LLM Usage

#### 1. Category Selection Based on JD Role Type
```
IF role = "Manager" or "Lead" or "Director":
    → Prioritize: Management/Leadership Skills verbs
    → Examples: administered, coordinated, delegated, supervised

IF role = "Engineer" or "Developer" or "Technical":
    → Prioritize: Computer/Technical Skills verbs
    → Examples: debugged, engineered, programmed, computed

IF role = "Analyst" or "Finance" or "Data":
    → Prioritize: Financial/Mathematical Skills verbs
    → Examples: analyzed, calculated, forecasted, audited

IF role requires "Communication" or "Marketing" or "Sales":
    → Prioritize: Communication Skills verbs
    → Examples: presented, negotiated, collaborated, authored
```

#### 2. Verb Rotation Rule
- **NEVER** use the same verb twice in consecutive bullets
- **LIMIT** each verb to maximum 2 uses across entire resume
- **VARY** verb strength (mix strong verbs like "Engineered" with softer ones like "Supported")

#### 3. Tense Rules
- **Current position**: Present tense (e.g., "Develop", "Manage")
- **Past positions**: Past tense (e.g., "Developed", "Managed")

#### 4. ATS Optimization
- Match verbs to JD language when possible
- If JD says "Lead cross-functional teams" → use "Led" not "Managed"

### Sample Verb Categories for ML/AI Roles:
```
Technical: engineered, developed, implemented, optimized, debugged, computed
Research: analyzed, evaluated, investigated, researched, assessed
Leadership: led, coordinated, supervised, directed, mentored
Communication: presented, documented, collaborated, authored
```

---

## 📁 FILE 2: Resume Checklist.txt

### Key Sections to Validate

#### Personal Information (Header)
✅ Name in larger font (14-16pt)
✅ ONE phone number, ONE professional email
✅ LinkedIn URL (if active)
✅ Address optional (unless federal resume)

#### Education
✅ Institution name, city, state
✅ Degree title accurate
✅ Graduation date (month + year)
✅ GPA if > 3.0
✅ Dean's List if applicable
✅ Remove high school by 2nd year of college

#### Experience
✅ Employer name + city/state
✅ Dates: month-year to month-year
✅ Job title clearly stated
✅ Bullets start with ACTION VERBS
✅ Correct tense (present for current, past for prior)
✅ Quantified achievements (numbers, %, results)
✅ Reverse chronological order

#### Skills
✅ Organized by category
✅ Technical skills highlighted
✅ Language skills with proficiency level
✅ NO soft skill adjectives like "hardworking"

#### Format
✅ NO text boxes, shading, photos, graphs
✅ NO headers/footers
✅ NO "responsible for" or "worked with"
✅ NO repetition across positions
✅ Consistent spacing, font, bold/italics
✅ Keyword-rich for ATS
✅ No personal pronouns (I, me, my)
✅ ZERO typos or errors

---

## 📁 FILE 3: Resume guide.txt

### Experience Bullet Writing Formula
```
[ACTION VERB] + [WHAT you did] + [HOW/WITH WHAT] + [RESULT/IMPACT]

Examples:
❌ "Responsible for managing data pipelines"
✅ "Engineered data pipelines using Apache Airflow, reducing processing time by 40%"

❌ "Worked with team on ML models"
✅ "Collaborated with 5-member team to develop ML models achieving 95% accuracy"
```

#### Questions to Answer in Each Bullet
1. **WHAT** did you do?
2. **HOW** did you do it?
3. **HOW WELL** did you do it (metrics)?

---

## 📁 FILE 4: Resume rubric.xlsx

### 4-Level Scoring System

| Score | Level | Description |
|-------|-------|-------------|
| 4 | Excellent | "Resume should effectively land you an interview" |
| 3 | Good | "Resume could land you an interview (borderline case)" |
| 2 | Average | "Resume is average, needs improvement" |
| 1 | Poor | "Resume would be discarded during screening" |

### Scoring Weights
- FORMAT: 25%
- EDUCATION: 20%
- EXPERIENCE: 35%
- HONORS/ACTIVITIES: 20%

**Target Score: ≥ 3.5 (87.5%)**

---

## 📁 FILE 5: Cover Letter Checklist.txt

### Key Requirements
- ✅ Research company before writing
- ✅ Identify SPECIFIC position
- ✅ State how you heard about opening
- ✅ Be CREATIVE - catch attention quickly
- ✅ Use KEYWORDS from job description
- ✅ Provide SPECIFIC examples
- ✅ Tell a STORY (don't repeat resume)
- ✅ Thank the reader
- ✅ Describe SPECIFIC follow-up plan with timeline

---

## 📁 FILE 6: Cover letter guide.txt

### Cover Letter Structure
```
OPENING: [Hook] + [Position] + [How Heard] + [Interest]
BODY 1: Technical qualifications with metrics
BODY 2: Soft skills and culture fit
CLOSING: [Thank] + [Interest] + [Follow-up Plan]
```

### LLM Rules
1. **NEVER** start with "I am writing to apply for..."
2. **ALWAYS** include company-specific content
3. **LIMIT** to 3-4 paragraphs, ~300 words

---

## 📁 FILE 7: Cover letter rubric.xlsx

### 3-Level Scoring System

| Score | Level |
|-------|-------|
| 3 | Excellent - "Should get you the interview" |
| 2 | Average - "Could land you an interview" |
| 1 | Poor - "Would be discarded" |

### Scoring Weights
- FORMAT & WRITING: 25%
- INTRODUCTION: 25%
- SKILLS & EXPERIENCE: 30%
- CLOSING: 20%

**Target Score: ≥ 2.5 (83%)**

---

## 🎯 MINIMUM THRESHOLDS

| Document | Score Required |
|----------|----------------|
| Resume Rubric | ≥ 3.5 / 4.0 (87.5%) |
| Cover Letter Rubric | ≥ 2.5 / 3.0 (83.3%) |
| ATS Score | ≥ 95 / 100 |

The system loops until ALL thresholds are met.
