"""
Resource Loader Tool for MCP Server.

Loads and parses compliance resources with full understanding of their structure:
- Action verbs (4 categories: Management, Communication, Technical, Financial)
- Resume checklist, guide, rubric (4-level scoring)
- Cover letter checklist, guide, rubric (3-level scoring)
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd


def get_resources_path() -> str:
    """Get the base path for resources."""
    return os.getenv("RESOURCES_PATH", "./resources")


def load_text_resource(filename: str) -> str:
    """Load a text resource file."""
    path = os.path.join(get_resources_path(), filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Resource not found: {filename}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_excel_resource(filename: str, sheet_name=0) -> pd.DataFrame:
    """Load an Excel resource file."""
    path = os.path.join(get_resources_path(), filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Resource not found: {filename}")
    return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")


# ============================================================================
# ACTION VERBS
# ============================================================================

def load_action_verbs() -> Dict[str, List[str]]:
    """
    Load action verbs from Excel file.
    
    Structure: 4 Categories with 73 total verbs
    - Management/ Leadership Skills (46 verbs)
    - Communication Skills (73 verbs)
    - Computer/ Technical Skills (33 verbs)
    - Financial/ Mathematical Skills (36 verbs)
    """
    try:
        df = load_excel_resource("Action_Verbs.xlsx")
        result = {}
        for column in df.columns:
            verbs = df[column].dropna().tolist()
            cleaned = [str(v).strip().capitalize() for v in verbs if str(v).strip()]
            result[column] = cleaned
        return result
    except FileNotFoundError:
        return get_default_action_verbs()


def get_default_action_verbs() -> Dict[str, List[str]]:
    """Default action verbs when file is not available."""
    return {
        "Management/ Leadership Skills": [
            "Administered", "Analyzed", "Appointed", "Approved", "Attained",
            "Coordinated", "Delegated", "Directed", "Evaluated", "Executed",
            "Led", "Managed", "Organized", "Oversaw", "Planned", "Prioritized",
            "Reorganized", "Replaced", "Reviewed", "Scheduled", "Secured", "Supervised"
        ],
        "Communication Skills": [
            "Accounted", "Addressed", "Advertised", "Advised", "Arbitrated",
            "Authored", "Collaborated", "Communicated", "Composed", "Convinced",
            "Corresponded", "Developed", "Drafted", "Edited", "Influenced",
            "Interpreted", "Interviewed", "Invented", "Involved", "Joined",
            "Judged", "Negotiated", "Presented", "Promoted", "Reported"
        ],
        "Computer/ Technical Skills": [
            "Adapted", "Applied", "Assembled", "Built", "Calculated", "Computed",
            "Conserved", "Constructed", "Converted", "Debugged", "Designed",
            "Developed", "Engineered", "Fabricated", "Implemented", "Installed",
            "Maintained", "Operated", "Overhauled", "Printed", "Programmed",
            "Rectified", "Regulated", "Remodeled", "Repaired", "Solved", "Upgraded"
        ],
        "Financial/ Mathematical Skills": [
            "Accounted", "Adjusted", "Administered", "Allocated", "Analyzed",
            "Appraised", "Articulated", "Assessed", "Audited", "Authorized",
            "Balanced", "Budgeted", "Calculated", "Computed", "Developed",
            "Forecasted", "Managed", "Marketed", "Planned", "Projected", "Researched"
        ]
    }


def get_action_verbs_for_role(role_type: str) -> List[str]:
    """Get relevant action verbs based on role type."""
    all_verbs = load_action_verbs()
    role_lower = role_type.lower()
    
    if any(kw in role_lower for kw in ["engineer", "developer", "technical", "programmer", "ml", "ai", "software"]):
        priority_categories = ["Computer/ Technical Skills", "Communication Skills"]
    elif any(kw in role_lower for kw in ["manager", "lead", "director", "supervisor", "head"]):
        priority_categories = ["Management/ Leadership Skills", "Communication Skills"]
    elif any(kw in role_lower for kw in ["analyst", "finance", "accountant", "data", "scientist"]):
        priority_categories = ["Financial/ Mathematical Skills", "Computer/ Technical Skills"]
    else:
        priority_categories = list(all_verbs.keys())
    
    result = []
    for cat in priority_categories:
        if cat in all_verbs:
            result.extend(all_verbs[cat])
    
    for cat, verbs in all_verbs.items():
        for v in verbs:
            if v not in result:
                result.append(v)
    
    return result


def get_all_action_verbs_flat() -> List[str]:
    """Get all action verbs as a flat, deduplicated list."""
    all_verbs = load_action_verbs()
    flat = []
    for verbs in all_verbs.values():
        for v in verbs:
            if v not in flat:
                flat.append(v)
    return flat


def get_action_verbs() -> Dict[str, List[str]]:
    """
    Get action verbs organized by category.
    Alias for load_action_verbs() for consistency.
    
    Returns:
        Dict with categories as keys and verb lists as values
    """
    return load_action_verbs()


# ============================================================================
# RESUME RESOURCES
# ============================================================================

def load_resume_checklist() -> Dict[str, List[str]]:
    """Load resume checklist organized by section."""
    try:
        content = load_text_resource("Resume Checklist.txt")
        return parse_resume_checklist(content)
    except FileNotFoundError:
        return get_default_resume_checklist()


def parse_resume_checklist(content: str) -> Dict[str, List[str]]:
    """Parse the resume checklist into structured sections."""
    sections = {
        "personal_information": [],
        "education": [],
        "experience": [],
        "skills": [],
        "format": [],
        "content_quality": []
    }
    
    current_section = "personal_information"
    
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        line_lower = line.lower()
        if "personal information" in line_lower:
            current_section = "personal_information"
        elif "education" in line_lower and len(line) < 30:
            current_section = "education"
        elif "experience" in line_lower and len(line) < 50:
            current_section = "experience"
        elif line_lower.startswith("skills"):
            current_section = "skills"
        elif "other things to avoid" in line_lower:
            current_section = "format"
        elif "content, punctuation" in line_lower:
            current_section = "content_quality"
        elif line and not line.endswith(":") and len(line) > 15:
            sections[current_section].append(line)
    
    return sections


def get_default_resume_checklist() -> Dict[str, List[str]]:
    """Default resume checklist."""
    return {
        "personal_information": [
            "Name in larger font (14-16pt)",
            "One phone number and one professional email",
            "LinkedIn URL if active on LinkedIn",
            "Address optional unless required"
        ],
        "education": [
            "Institution name, city and state",
            "Degree title accurate",
            "Graduation date (month and year)",
            "GPA if above 3.0",
            "Dean's list if applicable",
            "Remove high school by 2nd year of college"
        ],
        "experience": [
            "Employer name and location (city, state)",
            "Dates: month-year to month-year",
            "Job title clearly stated",
            "Bullets start with action verbs",
            "Correct tense (present for current, past for prior)",
            "Achievements quantified with numbers/percentages",
            "Reverse chronological order"
        ],
        "skills": [
            "Organized by category",
            "Technical skills highlighted",
            "Language proficiency levels included",
            "No soft skill adjectives like 'hardworking'"
        ],
        "format": [
            "No text boxes, shading, photos, graphs",
            "No headers or footers",
            "Avoid 'responsible for' and 'worked with'",
            "No repetition across positions"
        ],
        "content_quality": [
            "Resume looks original, not template-based",
            "Inviting to read with clear sections and white space",
            "Accomplishments begin with action verbs",
            "Keyword-rich for ATS",
            "No personal pronouns (I, me, my)",
            "Zero typos or errors"
        ]
    }


def load_resume_guide() -> str:
    """Load resume writing guide."""
    try:
        return load_text_resource("Resume guide.txt")
    except FileNotFoundError:
        return get_default_resume_guide()


def get_default_resume_guide() -> str:
    """Default resume guide."""
    return """Resume Writing Guide:

HEADING: Name, phone, professional email, LinkedIn URL

EDUCATION (before Experience for students):
- School name, city, state
- Degree and graduation date (month + year)
- GPA if > 3.0, Dean's List if applicable

EXPERIENCE (reverse chronological):
- Company, location, dates, job title
- Bullet points starting with action verbs
- Quantify achievements with numbers

BULLET WRITING FORMULA:
[ACTION VERB] + [WHAT you did] + [HOW/WITH WHAT] + [RESULT]

Questions to answer: WHAT, HOW, HOW WELL (metrics)

RULES:
- Never use "Responsible for" or "Duties included"
- Never use personal pronouns (I, me, my)
- Use present tense for current job, past tense for previous
- Quantify with numbers, percentages, dollar amounts
"""


def load_resume_rubric() -> Dict[str, Dict[str, Any]]:
    """
    Load resume scoring rubric.
    
    4-Level Scoring: Excellent (4), Good (3), Average (2), Poor (1)
    Categories: Format (25%), Education (20%), Experience (35%), Honors (20%)
    """
    try:
        df = load_excel_resource("Resume rubric.xlsx")
        return parse_resume_rubric(df)
    except FileNotFoundError:
        return get_default_resume_rubric()


def parse_resume_rubric(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Parse the resume rubric DataFrame."""
    rubric = {}
    
    category_weights = {
        "Format": 0.25,
        "Education Section": 0.20,
        "Experience Section": 0.35,
        "Honors Activities": 0.20
    }
    
    for idx, row in df.iterrows():
        if idx < 2:
            continue
        
        category = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None
        if not category or category == "NaN" or category == "nan":
            continue
        
        rubric[category] = {
            "weight": category_weights.get(category, 0.25),
            "scores": {
                "excellent": str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else "",
                "good": str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else "",
                "average": str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else "",
                "poor": str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else ""
            }
        }
    
    return rubric


def get_default_resume_rubric() -> Dict[str, Dict[str, Any]]:
    """Default resume rubric."""
    return {
        "Format": {
            "weight": 0.25,
            "scores": {
                "excellent": "Fills page, no errors, easily scanned",
                "good": "Almost fills page, single error possible",
                "average": "Font/spacing not appealing, spelling errors",
                "poor": "More white space than words, multiple errors"
            }
        },
        "Education Section": {
            "weight": 0.20,
            "scores": {
                "excellent": "Organized, includes institution, location, date, major, degree, GPA",
                "good": "Well organized, missing GPA or extras",
                "average": "Missing degree or GPA, not well organized",
                "poor": "Missing crucial info like location or date"
            }
        },
        "Experience Section": {
            "weight": 0.35,
            "scores": {
                "excellent": "Well-defined, action verb bullets, includes location/title/dates",
                "good": "All info included, bullets not detailed enough",
                "average": "Paragraph form instead of bullets, missing info",
                "poor": "No order, no descriptions, missing essential info"
            }
        },
        "Honors Activities": {
            "weight": 0.20,
            "scores": {
                "excellent": "Organized, includes skills gained, leadership, dates",
                "good": "Difficult to follow, leadership listed but skills not defined",
                "average": "Missing leadership positions or dates",
                "poor": "Section missing or minimal"
            }
        }
    }


# ============================================================================
# COVER LETTER RESOURCES
# ============================================================================

def load_cover_letter_checklist() -> Dict[str, List[str]]:
    """Load cover letter checklist organized by section."""
    try:
        content = load_text_resource("Cover Letter Checklist.txt")
        return parse_cover_letter_checklist(content)
    except FileNotFoundError:
        return get_default_cover_letter_checklist()


def parse_cover_letter_checklist(content: str) -> Dict[str, List[str]]:
    """Parse the cover letter checklist."""
    sections = {
        "research": [],
        "introduction": [],
        "body": [],
        "closing": [],
        "format": []
    }
    
    current_section = "research"
    
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        line_lower = line.lower()
        if "research" in line_lower and len(line) < 20:
            current_section = "research"
        elif "introduction" in line_lower:
            current_section = "introduction"
        elif "body" in line_lower:
            current_section = "body"
        elif "closing" in line_lower and "paragraph" in line_lower:
            current_section = "closing"
        elif "format" in line_lower and len(line) < 15:
            current_section = "format"
        elif line and not line.endswith(":") and len(line) > 15:
            sections[current_section].append(line)
    
    return sections


def get_default_cover_letter_checklist() -> Dict[str, List[str]]:
    """Default cover letter checklist."""
    return {
        "research": [
            "Review position description and company website",
            "Identify qualifications matching JD",
            "Follow all posting directions"
        ],
        "introduction": [
            "Identify position applying for",
            "Describe how heard about opening",
            "Name referral person if applicable",
            "Be creative and catch attention quickly"
        ],
        "body": [
            "Identify strongest qualifications",
            "Incorporate keywords from position description",
            "Provide clear examples",
            "Tell a story, don't repeat resume",
            "Discuss soft skills and personality fit"
        ],
        "closing": [
            "Thank the reader",
            "Reinforce desire to work there",
            "Describe specific follow-up plan with timeline",
            "Use formal closing (Sincerely, Best regards)"
        ],
        "format": [
            "Stay within one page",
            "Same header as resume",
            "Same font as resume",
            "Address to specific person if possible"
        ]
    }


def load_cover_letter_guide() -> str:
    """Load cover letter writing guide."""
    try:
        return load_text_resource("Cover letter guide.txt")
    except FileNotFoundError:
        return get_default_cover_letter_guide()


def get_default_cover_letter_guide() -> str:
    """Default cover letter guide."""
    return """Cover Letter Writing Guide:

THREE REASONS FOR COVER LETTERS:
1. Assess writing and communication skills
2. Highlight aspects not on resume with concrete examples
3. Stimulate interest in you and your resume

STRUCTURE:
1. OPENING: Hook + Position + Source + Interest
2. BODY 1: Technical qualifications with specific examples
3. BODY 2: Soft skills and culture fit
4. CLOSING: Thank + Reiterate interest + Specific follow-up plan

RULES:
- Never start with "I am writing to apply for..."
- Always include company-specific content
- Use keywords from JD naturally
- Limit to 3-4 paragraphs, ~300 words
- Each letter should be unique and personal
"""


def load_cover_letter_rubric() -> Dict[str, Dict[str, Any]]:
    """
    Load cover letter scoring rubric.
    
    3-Level Scoring: Excellent (3), Average (2), Poor (1)
    Categories: Format (25%), Introduction (25%), Skills (30%), Closing (20%)
    """
    try:
        df = load_excel_resource("Cover letter rubric.xlsx")
        return parse_cover_letter_rubric(df)
    except FileNotFoundError:
        return get_default_cover_letter_rubric()


def parse_cover_letter_rubric(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Parse the cover letter rubric DataFrame."""
    rubric = {}
    
    category_weights = {
        "Business format and overall quality of writing ability": 0.25,
        "Section 1: Introduction": 0.25,
        "Section 2: Identification of skills and experiences as related to position": 0.30,
        "Section 3: Closing": 0.20
    }
    
    for idx, row in df.iterrows():
        if idx < 2:
            continue
        
        category = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None
        if not category or category == "NaN" or category == "nan":
            continue
        
        rubric[category] = {
            "weight": category_weights.get(category, 0.25),
            "scores": {
                "excellent": str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else "",
                "average": str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else "",
                "poor": str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else ""
            }
        }
    
    return rubric


def get_default_cover_letter_rubric() -> Dict[str, Dict[str, Any]]:
    """Default cover letter rubric."""
    return {
        "Business Format & Writing": {
            "weight": 0.25,
            "scores": {
                "excellent": "Correct format, clear, concise, grammatically correct, no errors",
                "average": "Correct format, minimal errors, doesn't convince",
                "poor": "No business format, multiple errors, content unclear"
            }
        },
        "Introduction": {
            "weight": 0.25,
            "scores": {
                "excellent": "Identifies position, explains interest, creative attention-grabber",
                "average": "Identifies position, vague interest, bland",
                "poor": "Doesn't identify position, won't grab attention"
            }
        },
        "Skills & Experience": {
            "weight": 0.30,
            "scores": {
                "excellent": "Identifies strongest qualifications, relates to job, explains interest",
                "average": "Identifies qualification but not related, restates resume",
                "poor": "No relevant qualifications, no skill relation"
            }
        },
        "Closing": {
            "weight": 0.20,
            "scores": {
                "excellent": "Refers to resume, thanks reader, assertive follow-up with timeline",
                "average": "Thanks reader, no resume reference, assumes employer contacts",
                "poor": "No thanks, no resume reference, no follow-up plan"
            }
        }
    }


# ============================================================================
# CONVENIENCE FUNCTIONS FOR SCORING
# ============================================================================

def calculate_resume_rubric_score(section_scores: Dict[str, int]) -> float:
    """
    Calculate weighted resume rubric score.
    
    Args:
        section_scores: Dict with keys: format, education, experience, honors
                       Values should be 1-4
    
    Returns:
        Weighted score out of 4.0
    """
    weights = {
        "format": 0.25,
        "education": 0.20,
        "experience": 0.35,
        "honors": 0.20
    }
    
    total = 0.0
    for section, weight in weights.items():
        score = section_scores.get(section, 3)  # Default to "good"
        total += score * weight
    
    return round(total, 2)


def calculate_cover_letter_rubric_score(section_scores: Dict[str, int]) -> float:
    """
    Calculate weighted cover letter rubric score.
    
    Args:
        section_scores: Dict with keys: format, intro, skills, closing
                       Values should be 1-3
    
    Returns:
        Weighted score out of 3.0
    """
    weights = {
        "format": 0.25,
        "intro": 0.25,
        "skills": 0.30,
        "closing": 0.20
    }
    
    total = 0.0
    for section, weight in weights.items():
        score = section_scores.get(section, 2)  # Default to "average"
        total += score * weight
    
    return round(total, 2)


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("Testing Resource Loader...\n")
    
    # Test action verbs
    verbs = load_action_verbs()
    print(f"Action Verbs: {len(verbs)} categories")
    for cat, v_list in verbs.items():
        print(f"  {cat}: {len(v_list)} verbs")
    
    # Test role-specific verbs
    ml_verbs = get_action_verbs_for_role("ML Engineer")
    print(f"\nVerbs for 'ML Engineer': {len(ml_verbs)} prioritized verbs")
    print(f"  Top 10: {', '.join(ml_verbs[:10])}")
    
    # Test resume resources
    resume_checklist = load_resume_checklist()
    print(f"\nResume Checklist: {len(resume_checklist)} sections")
    for section, items in resume_checklist.items():
        print(f"  {section}: {len(items)} items")
    
    resume_rubric = load_resume_rubric()
    print(f"\nResume Rubric: {len(resume_rubric)} categories")
    for cat, data in resume_rubric.items():
        print(f"  {cat}: weight={data['weight']}")
    
    # Test cover letter resources
    cl_checklist = load_cover_letter_checklist()
    print(f"\nCover Letter Checklist: {len(cl_checklist)} sections")
    
    cl_rubric = load_cover_letter_rubric()
    print(f"Cover Letter Rubric: {len(cl_rubric)} categories")
    
    # Test scoring
    sample_resume_scores = {"format": 4, "education": 3, "experience": 4, "honors": 3}
    resume_score = calculate_resume_rubric_score(sample_resume_scores)
    print(f"\nSample Resume Score: {resume_score}/4.0 ({resume_score/4*100:.1f}%)")
    
    sample_cl_scores = {"format": 3, "intro": 3, "skills": 2, "closing": 3}
    cl_score = calculate_cover_letter_rubric_score(sample_cl_scores)
    print(f"Sample Cover Letter Score: {cl_score}/3.0 ({cl_score/3*100:.1f}%)")
    
    print("\nResource Loader tests complete!")
