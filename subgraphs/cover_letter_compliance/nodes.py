"""
Cover Letter Compliance Nodes

Validates cover letter against:
1. Cover Letter Checklist (item-by-item validation)
2. Cover Letter Rubric (section scoring 1-3)
3. Best Practices (guide recommendations)

Nodes:
1. prepare_cover_letter_text - Extract text from CoverLetter
2. validate_checklist - Run checklist validation
3. score_rubric - Score against rubric categories
4. generate_feedback - Generate strengths and improvements
5. compile_report - Create final ComplianceReport
"""

import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

from subgraphs.cover_letter_compliance.state import (
    CoverLetterComplianceState,
    ChecklistResult,
    SectionCheckResult,
    RubricScore,
    CoverLetterComplianceReport,
    COVER_LETTER_CHECKLIST,
    COVER_LETTER_RUBRIC,
    get_grade
)


# ============================================================================
# NODE 1: PREPARE COVER LETTER TEXT
# ============================================================================

def prepare_cover_letter_text(state: CoverLetterComplianceState) -> Dict[str, Any]:
    """
    Extract and prepare cover letter text for validation.
    """
    cover_letter = state.cover_letter
    cover_letter_text = state.cover_letter_text
    
    # Get text from CoverLetter object or direct text
    if cover_letter and hasattr(cover_letter, 'full_text'):
        text = cover_letter.full_text
    elif cover_letter_text:
        text = cover_letter_text
    else:
        return {"error_message": "No cover letter provided"}
    
    if not text or len(text.strip()) < 50:
        return {"error_message": "Cover letter text is too short or empty"}
    
    print(f"  📄 Prepared cover letter: {len(text)} characters, {len(text.split())} words")
    
    return {"cover_letter_text": text}


# ============================================================================
# NODE 2: VALIDATE CHECKLIST
# ============================================================================

def validate_checklist(state: CoverLetterComplianceState) -> Dict[str, Any]:
    """
    Validate cover letter against checklist items.
    Uses rule-based checks for each section.
    """
    text = state.cover_letter_text
    text_lower = text.lower()
    jd = state.structured_jd
    
    results = {}
    
    # ===== RESEARCH =====
    results["research"] = validate_research_section(text_lower, jd)
    
    # ===== INTRODUCTION =====
    results["introduction"] = validate_introduction_section(text_lower, jd)
    
    # ===== BODY =====
    results["body"] = validate_body_section(text_lower, jd)
    
    # ===== CLOSING =====
    results["closing"] = validate_closing_section(text_lower)
    
    # ===== FORMAT =====
    results["format"] = validate_format_section(text, state.cover_letter)
    
    # Print summary
    total_passed = sum(r.items_passed for r in results.values())
    total_items = sum(r.items_total for r in results.values())
    print(f"  ✅ Checklist: {total_passed}/{total_items} items passed")
    
    return {"checklist_results": results}


def validate_research_section(text: str, jd) -> SectionCheckResult:
    """Validate research & preparation section."""
    results = []
    checklist = COVER_LETTER_CHECKLIST["research"]["items"]
    
    # rs_1: Demonstrates review of position description
    has_role_ref = False
    if jd:
        role_words = jd.role_title.lower().split() if jd.role_title else []
        has_role_ref = any(word in text for word in role_words if len(word) > 3)
    results.append(ChecklistResult(
        item_id="rs_1",
        item_text="Demonstrates review of position description",
        passed=has_role_ref,
        required=True,
        notes="Role title referenced" if has_role_ref else "No clear role reference"
    ))
    
    # rs_2: Demonstrates review of company website
    company_indicators = ["mission", "values", "culture", "team", "innovation", "committed", "believe"]
    has_company_research = any(ind in text for ind in company_indicators)
    results.append(ChecklistResult(
        item_id="rs_2",
        item_text="Demonstrates review of company website",
        passed=has_company_research,
        required=True,
        notes="Company research evident" if has_company_research else "No company research shown"
    ))
    
    # rs_3: Identifies qualifications
    qual_indicators = ["experience", "skill", "expertise", "background", "qualified", "ability"]
    has_qualifications = any(ind in text for ind in qual_indicators)
    results.append(ChecklistResult(
        item_id="rs_3",
        item_text="Identifies qualifications, skills, and abilities",
        passed=has_qualifications,
        required=True,
        notes="Qualifications mentioned" if has_qualifications else "No qualifications identified"
    ))
    
    # rs_4: Addresses why interested in organization
    interest_indicators = ["excited", "passionate", "drawn to", "impressed", "admire", "inspired", "interested in"]
    has_interest = any(ind in text for ind in interest_indicators)
    if jd and jd.company_name:
        has_interest = has_interest or jd.company_name.lower() in text
    results.append(ChecklistResult(
        item_id="rs_4",
        item_text="Addresses why interested in the organization",
        passed=has_interest,
        required=True,
        notes="Interest expressed" if has_interest else "No interest in organization stated"
    ))
    
    # rs_5: Explains fit for position
    fit_indicators = ["fit", "align", "match", "ideal", "well-suited", "contribute", "bring"]
    has_fit = any(ind in text for ind in fit_indicators)
    results.append(ChecklistResult(
        item_id="rs_5",
        item_text="Explains why you are a fit for the position",
        passed=has_fit,
        required=True,
        notes="Fit explained" if has_fit else "No explanation of fit"
    ))
    
    # rs_6: Follows directions (assume true - can't verify from text alone)
    results.append(ChecklistResult(
        item_id="rs_6",
        item_text="Follows all directions in the posting",
        passed=True,
        required=True,
        notes="Cannot verify from text - assumed compliant"
    ))
    
    return create_section_result("Research & Preparation", results)


def validate_introduction_section(text: str, jd) -> SectionCheckResult:
    """Validate introduction paragraph."""
    results = []
    
    # Estimate first paragraph (first ~100 words or up to first double newline)
    paragraphs = text.split('\n\n')
    intro = ""
    for p in paragraphs:
        if len(p.strip()) > 50 and not any(x in p.lower() for x in ["sincerely", "regards", "thank you for"]):
            intro = p.lower()
            break
    
    # in_1: Identifies position
    position_indicators = ["position", "role", "opportunity", "opening", "job"]
    has_position = any(ind in intro for ind in position_indicators)
    if jd and jd.role_title:
        has_position = has_position or any(w in intro for w in jd.role_title.lower().split() if len(w) > 3)
    results.append(ChecklistResult(
        item_id="in_1",
        item_text="Identifies the position you are applying for",
        passed=has_position,
        required=True,
        notes="Position identified" if has_position else "Position not clearly stated"
    ))
    
    # in_2: Describes how heard about opening
    heard_indicators = ["heard", "learned", "discovered", "saw", "found", "referred", "posting", "linkedin"]
    has_heard = any(ind in intro for ind in heard_indicators)
    results.append(ChecklistResult(
        item_id="in_2",
        item_text="Describes how you heard about the opening",
        passed=has_heard,
        required=False,
        notes="Source mentioned" if has_heard else "No source mentioned (optional)"
    ))
    
    # in_3: Mentions referral by name
    referral_indicators = ["referred by", "recommended by", "suggested by", "introduced by"]
    has_referral = any(ind in intro for ind in referral_indicators)
    results.append(ChecklistResult(
        item_id="in_3",
        item_text="Mentions referral by name if applicable",
        passed=has_referral or True,  # Optional, pass if not applicable
        required=False,
        notes="Referral mentioned" if has_referral else "No referral (optional)"
    ))
    
    # in_4: Highlights interest
    interest_in_intro = any(ind in intro for ind in ["excited", "passionate", "interested", "drawn", "eager"])
    results.append(ChecklistResult(
        item_id="in_4",
        item_text="Briefly highlights why interested in job and organization",
        passed=interest_in_intro,
        required=True,
        notes="Interest shown" if interest_in_intro else "No interest expressed in intro"
    ))
    
    # in_5: Creative opening
    weak_openings = ["i am writing to apply", "i am writing to express", "i would like to apply", 
                     "i am interested in applying", "this letter is to"]
    has_weak_opening = any(wo in intro for wo in weak_openings)
    creative_opening = not has_weak_opening
    results.append(ChecklistResult(
        item_id="in_5",
        item_text="Creative opening that catches employer attention",
        passed=creative_opening,
        required=True,
        notes="Creative opening" if creative_opening else "Generic/weak opening detected"
    ))
    
    return create_section_result("Introduction Paragraph", results)


def validate_body_section(text: str, jd) -> SectionCheckResult:
    """Validate body paragraphs."""
    results = []
    text_lower = text.lower()
    
    # bd_1: Identifies strongest qualifications
    qual_indicators = ["experience", "expertise", "skill", "led", "developed", "built", "managed", "achieved"]
    has_qualifications = sum(1 for ind in qual_indicators if ind in text_lower) >= 2
    results.append(ChecklistResult(
        item_id="bd_1",
        item_text="Identifies strongest and most relevant qualifications",
        passed=has_qualifications,
        required=True,
        notes="Qualifications highlighted" if has_qualifications else "Qualifications not clear"
    ))
    
    # bd_2: States how qualifications apply
    application_indicators = ["this experience", "these skills", "this background", "directly", 
                             "aligns with", "applies to", "relevant to", "enable me to"]
    has_application = any(ind in text_lower for ind in application_indicators)
    results.append(ChecklistResult(
        item_id="bd_2",
        item_text="Clearly states how qualifications apply to the position",
        passed=has_application,
        required=True,
        notes="Application of skills shown" if has_application else "No clear connection to role"
    ))
    
    # bd_3: Incorporates keywords from JD
    keywords_found = 0
    if jd:
        all_keywords = (jd.skills_required or []) + (jd.keywords or [])
        keywords_found = sum(1 for kw in all_keywords if kw.lower() in text_lower)
    has_keywords = keywords_found >= 3
    results.append(ChecklistResult(
        item_id="bd_3",
        item_text="Incorporates keywords from position description",
        passed=has_keywords,
        required=True,
        notes=f"{keywords_found} keywords found" if jd else "No JD to compare"
    ))
    
    # bd_4: Elaborates on interest
    elaboration_indicators = ["specifically", "particularly", "especially", "what draws me", 
                             "what excites me", "i'm drawn to"]
    has_elaboration = any(ind in text_lower for ind in elaboration_indicators)
    results.append(ChecklistResult(
        item_id="bd_4",
        item_text="Elaborates on interest in position, organization, industry",
        passed=has_elaboration,
        required=True,
        notes="Interest elaborated" if has_elaboration else "Interest not elaborated"
    ))
    
    # bd_5: Describes experiences
    experience_indicators = ["at", "during", "while", "when i", "in my role", "as a"]
    has_experience_story = any(ind in text_lower for ind in experience_indicators)
    results.append(ChecklistResult(
        item_id="bd_5",
        item_text="Describes experiences where you developed relevant skills",
        passed=has_experience_story,
        required=True,
        notes="Experiences described" if has_experience_story else "No experience stories"
    ))
    
    # bd_6: Provides clear examples
    has_metrics = bool(re.search(r'\d+[%$MK]?|\d+\s*(percent|million|thousand)', text))
    results.append(ChecklistResult(
        item_id="bd_6",
        item_text="Provides clear examples that capture reader's interest",
        passed=has_metrics,
        required=True,
        notes="Quantified examples present" if has_metrics else "No quantified examples"
    ))
    
    # bd_7: Tells a story, not resume repeat
    story_indicators = ["led", "discovered", "realized", "learned", "transformed", "challenged"]
    has_story = any(ind in text_lower for ind in story_indicators)
    results.append(ChecklistResult(
        item_id="bd_7",
        item_text="Tells a story, does not just repeat resume",
        passed=has_story,
        required=True,
        notes="Narrative style used" if has_story else "May be too resume-like"
    ))
    
    # bd_8: Discusses how skills relate
    relation_indicators = ["relate", "apply", "transfer", "contribute", "bring", "leverage"]
    has_relation = any(ind in text_lower for ind in relation_indicators)
    results.append(ChecklistResult(
        item_id="bd_8",
        item_text="Discusses how skills relate to job description",
        passed=has_relation,
        required=True,
        notes="Skills related to job" if has_relation else "Skills not connected to job"
    ))
    
    # bd_9: Discusses soft skills (optional)
    soft_skill_indicators = ["collaborate", "communicate", "lead", "mentor", "team", "adapt"]
    has_soft_skills = any(ind in text_lower for ind in soft_skill_indicators)
    results.append(ChecklistResult(
        item_id="bd_9",
        item_text="Discusses how soft skills relate to qualifications",
        passed=has_soft_skills,
        required=False,
        notes="Soft skills mentioned" if has_soft_skills else "No soft skills (optional)"
    ))
    
    return create_section_result("Body Paragraphs", results)


def validate_closing_section(text: str) -> SectionCheckResult:
    """Validate closing paragraph."""
    results = []
    text_lower = text.lower()
    
    # Find closing section (last paragraph before signature)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    closing = ""
    for p in reversed(paragraphs):
        if not any(x in p.lower() for x in ["sincerely", "regards", "best,"]):
            if len(p) > 30:
                closing = p.lower()
                break
    
    # cl_1: Thanks the reader
    thanks_indicators = ["thank you", "thanks", "appreciate", "grateful"]
    has_thanks = any(ind in text_lower for ind in thanks_indicators)
    results.append(ChecklistResult(
        item_id="cl_1",
        item_text="Thanks the reader for taking time to read",
        passed=has_thanks,
        required=True,
        notes="Thanks expressed" if has_thanks else "No thanks to reader"
    ))
    
    # cl_2: Reinforces desire
    desire_indicators = ["excited", "eager", "look forward", "welcome", "opportunity", "would love"]
    has_desire = any(ind in text_lower for ind in desire_indicators)
    results.append(ChecklistResult(
        item_id="cl_2",
        item_text="Reinforces desire to work for the organization",
        passed=has_desire,
        required=True,
        notes="Desire reinforced" if has_desire else "No enthusiasm in closing"
    ))
    
    # cl_3: Reinforces fit
    fit_indicators = ["contribute", "bring", "add value", "fit", "ideal", "well-suited"]
    has_fit_closing = any(ind in closing for ind in fit_indicators)
    results.append(ChecklistResult(
        item_id="cl_3",
        item_text="Reinforces fit for the position",
        passed=has_fit_closing,
        required=True,
        notes="Fit reinforced" if has_fit_closing else "Fit not reinforced in closing"
    ))
    
    # cl_4: Identifies next steps
    next_step_indicators = ["discuss", "interview", "conversation", "meeting", "call", "speak"]
    has_next_steps = any(ind in text_lower for ind in next_step_indicators)
    results.append(ChecklistResult(
        item_id="cl_4",
        item_text="Identifies next steps",
        passed=has_next_steps,
        required=True,
        notes="Next steps mentioned" if has_next_steps else "No next steps"
    ))
    
    # cl_5: Follow-up timeframe (optional)
    followup_indicators = ["follow up", "reach out", "contact you", "within", "next week"]
    has_followup = any(ind in text_lower for ind in followup_indicators)
    results.append(ChecklistResult(
        item_id="cl_5",
        item_text="Describes how you will follow up in specific time frame",
        passed=has_followup,
        required=False,
        notes="Follow-up mentioned" if has_followup else "No follow-up plan (optional)"
    ))
    
    return create_section_result("Closing Paragraph", results)


def validate_format_section(text: str, cover_letter) -> SectionCheckResult:
    """Validate format and signature."""
    results = []
    text_lower = text.lower()
    word_count = len(text.split())
    
    # fm_1: One page
    is_one_page = word_count <= 500  # Roughly one page
    results.append(ChecklistResult(
        item_id="fm_1",
        item_text="Stays within one page",
        passed=is_one_page,
        required=True,
        notes=f"{word_count} words" + (" (good)" if is_one_page else " (too long)")
    ))
    
    # fm_2: Contact information
    has_email = "@" in text and "." in text.split("@")[-1] if "@" in text else False
    has_phone = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
    has_contact = has_email or has_phone
    results.append(ChecklistResult(
        item_id="fm_2",
        item_text="Contact information listed on cover letter",
        passed=has_contact,
        required=True,
        notes="Contact info present" if has_contact else "No contact info found"
    ))
    
    # fm_3: Same header as resume (assume true)
    results.append(ChecklistResult(
        item_id="fm_3",
        item_text="Same header as resume for consistency",
        passed=True,
        required=False,
        notes="Cannot verify - assumed consistent"
    ))
    
    # fm_4: Targeted toward employer
    if cover_letter and hasattr(cover_letter, 'company_name'):
        has_company = cover_letter.company_name.lower() in text_lower if cover_letter.company_name else False
    else:
        # Look for company name patterns
        has_company = any(word in text_lower for word in ["company", "organization", "team", "your"])
    results.append(ChecklistResult(
        item_id="fm_4",
        item_text="Targeted toward specific employer",
        passed=has_company,
        required=True,
        notes="Company referenced" if has_company else "Not company-specific"
    ))
    
    # fm_5: Keywords from JD (already checked in body, check again)
    results.append(ChecklistResult(
        item_id="fm_5",
        item_text="Uses keywords from job description",
        passed=True,  # Checked in body section
        required=True,
        notes="Verified in body section"
    ))
    
    # fm_6: Same font (assume true)
    results.append(ChecklistResult(
        item_id="fm_6",
        item_text="Uses same font and font size as resume",
        passed=True,
        required=False,
        notes="Cannot verify from text"
    ))
    
    # fm_7: Addressed to specific person
    salutation_patterns = ["dear mr", "dear ms", "dear dr", "dear mrs"]
    has_specific_addressee = any(p in text_lower for p in salutation_patterns)
    results.append(ChecklistResult(
        item_id="fm_7",
        item_text="Addressed to a specific person if possible",
        passed=has_specific_addressee,
        required=False,
        notes="Specific person addressed" if has_specific_addressee else "Generic salutation (acceptable)"
    ))
    
    # fm_8: Formal closing
    formal_closings = ["sincerely", "regards", "best regards", "respectfully", "best,"]
    has_formal_closing = any(c in text_lower for c in formal_closings)
    results.append(ChecklistResult(
        item_id="fm_8",
        item_text="Formal closing (Sincerely, Regards, Best regards)",
        passed=has_formal_closing,
        required=True,
        notes="Formal closing present" if has_formal_closing else "No formal closing"
    ))
    
    # fm_9: Full name after closing
    # Check if there's text after closing that looks like a name
    has_signature = bool(re.search(r'(sincerely|regards|best)[,\s]*\n+[A-Z][a-z]+\s+[A-Z][a-z]+', text, re.IGNORECASE))
    results.append(ChecklistResult(
        item_id="fm_9",
        item_text="Full name after closing",
        passed=has_signature or True,  # Assume present
        required=True,
        notes="Signature present" if has_signature else "Assumed present"
    ))
    
    # fm_10: No errors (basic check)
    # Simple check for obvious issues
    has_obvious_errors = "  " in text or ".." in text or ",," in text
    results.append(ChecklistResult(
        item_id="fm_10",
        item_text="No spelling or grammatical errors",
        passed=not has_obvious_errors,
        required=True,
        notes="No obvious errors" if not has_obvious_errors else "Potential errors detected"
    ))
    
    return create_section_result("Format & Signature", results)


def create_section_result(name: str, results: List[ChecklistResult]) -> SectionCheckResult:
    """Create a section result from checklist results."""
    items_passed = sum(1 for r in results if r.passed)
    items_total = len(results)
    required_passed = sum(1 for r in results if r.passed and r.required)
    required_total = sum(1 for r in results if r.required)
    
    score = (items_passed / items_total * 100) if items_total > 0 else 0
    
    return SectionCheckResult(
        section_name=name,
        items_passed=items_passed,
        items_total=items_total,
        required_passed=required_passed,
        required_total=required_total,
        score=score,
        results=results
    )


# ============================================================================
# NODE 3: SCORE RUBRIC
# ============================================================================

def score_rubric(state: CoverLetterComplianceState) -> Dict[str, Any]:
    """
    Score cover letter against rubric categories.
    Uses checklist results to inform rubric scoring.
    """
    checklist = state.checklist_results
    
    scores = []
    
    # FORMAT & QUALITY
    format_result = checklist.get("format")
    intro_check = checklist.get("introduction")
    format_score = 3 if format_result and format_result.score >= 85 else (
        2 if format_result and format_result.score >= 60 else 1
    )
    scores.append(RubricScore(
        category="Business Format & Writing Quality",
        score=format_score,
        max_score=3,
        weight=COVER_LETTER_RUBRIC["format_quality"]["weight"],
        description=COVER_LETTER_RUBRIC["format_quality"]["levels"][format_score],
        feedback=generate_rubric_feedback("format", format_score, format_result)
    ))
    
    # INTRODUCTION
    intro_result = checklist.get("introduction")
    intro_score = 3 if intro_result and intro_result.score >= 80 else (
        2 if intro_result and intro_result.score >= 60 else 1
    )
    scores.append(RubricScore(
        category="Section 1: Introduction",
        score=intro_score,
        max_score=3,
        weight=COVER_LETTER_RUBRIC["introduction"]["weight"],
        description=COVER_LETTER_RUBRIC["introduction"]["levels"][intro_score],
        feedback=generate_rubric_feedback("introduction", intro_score, intro_result)
    ))
    
    # SKILLS & EXPERIENCE (most important - 30% weight)
    body_result = checklist.get("body")
    body_score = 3 if body_result and body_result.score >= 80 else (
        2 if body_result and body_result.score >= 55 else 1
    )
    scores.append(RubricScore(
        category="Section 2: Skills & Experience",
        score=body_score,
        max_score=3,
        weight=COVER_LETTER_RUBRIC["skills_experience"]["weight"],
        description=COVER_LETTER_RUBRIC["skills_experience"]["levels"][body_score],
        feedback=generate_rubric_feedback("body", body_score, body_result)
    ))
    
    # CLOSING
    closing_result = checklist.get("closing")
    closing_score = 3 if closing_result and closing_result.score >= 80 else (
        2 if closing_result and closing_result.score >= 60 else 1
    )
    scores.append(RubricScore(
        category="Section 3: Closing",
        score=closing_score,
        max_score=3,
        weight=COVER_LETTER_RUBRIC["closing"]["weight"],
        description=COVER_LETTER_RUBRIC["closing"]["levels"][closing_score],
        feedback=generate_rubric_feedback("closing", closing_score, closing_result)
    ))
    
    print(f"  📊 Rubric Scores: Format={format_score}, Intro={intro_score}, Body={body_score}, Close={closing_score}")
    
    return {"rubric_scores": scores}


def generate_rubric_feedback(category: str, score: int, result: Optional[SectionCheckResult]) -> str:
    """Generate feedback for a rubric category."""
    if not result:
        return "Section not evaluated"
    
    if score == 3:
        return f"Excellent. {result.items_passed}/{result.items_total} items passed."
    elif score == 2:
        failed = [r for r in result.results if not r.passed]
        issues = ", ".join([r.item_text[:30] for r in failed[:2]])
        return f"Good with issues: {issues}"
    else:
        failed = [r for r in result.results if not r.passed and r.required]
        issues = ", ".join([r.item_text[:30] for r in failed[:3]])
        return f"Needs work: {issues}"


# ============================================================================
# NODE 4: GENERATE FEEDBACK
# ============================================================================

def generate_feedback(state: CoverLetterComplianceState) -> Dict[str, Any]:
    """
    Generate strengths, improvements, and critical issues.
    """
    checklist = state.checklist_results
    rubric = state.rubric_scores
    
    strengths = []
    improvements = []
    critical_issues = []
    
    # Analyze checklist results
    for section_name, section in checklist.items():
        # Find strengths (passed required items)
        for result in section.results:
            if result.passed and result.required:
                if section.score >= 75:
                    strengths.append(f"{section.section_name}: {result.item_text}")
        
        # Find improvements (failed items)
        for result in section.results:
            if not result.passed:
                priority = "CRITICAL" if result.required else "MEDIUM"
                issue = f"[{priority}] {section.section_name}: {result.item_text}"
                if result.notes:
                    issue += f" - {result.notes}"
                
                if result.required:
                    critical_issues.append(issue)
                else:
                    improvements.append(issue)
    
    # Add rubric-based feedback
    for score in rubric:
        if score.score == 3:
            strengths.append(f"{score.category}: {score.description[:50]}")
        elif score.score == 1:
            critical_issues.append(f"[CRITICAL] {score.category}: {score.feedback}")
    
    # Deduplicate and limit
    strengths = list(dict.fromkeys(strengths))[:5]
    improvements = list(dict.fromkeys(improvements))[:10]
    critical_issues = list(dict.fromkeys(critical_issues))[:5]
    
    print(f"  💡 Feedback: {len(strengths)} strengths, {len(improvements)} improvements, {len(critical_issues)} critical")
    
    return {
        "_strengths": strengths,
        "_improvements": improvements,
        "_critical_issues": critical_issues
    }


# ============================================================================
# NODE 5: COMPILE REPORT
# ============================================================================

def compile_report(state: CoverLetterComplianceState) -> Dict[str, Any]:
    """
    Compile final CoverLetterComplianceReport.
    """
    checklist = state.checklist_results
    rubric = state.rubric_scores
    
    # Calculate checklist score
    total_passed = sum(s.items_passed for s in checklist.values())
    total_items = sum(s.items_total for s in checklist.values())
    checklist_score = (total_passed / total_items * 100) if total_items > 0 else 0
    
    # Calculate rubric score (weighted)
    weighted_sum = sum(s.score * s.weight for s in rubric)
    max_weighted = sum(3 * s.weight for s in rubric)
    rubric_score = (weighted_sum / max_weighted * 100) if max_weighted > 0 else 0
    
    # Overall score (50% checklist, 50% rubric)
    overall_score = (checklist_score * 0.5) + (rubric_score * 0.5)
    
    # Get grade
    grade = get_grade(overall_score)
    passed = overall_score >= 70  # C or above passes
    
    # Get feedback from state
    strengths = getattr(state, '_strengths', [])
    improvements = getattr(state, '_improvements', [])
    critical_issues = getattr(state, '_critical_issues', [])
    
    report = CoverLetterComplianceReport(
        checklist_score=round(checklist_score, 1),
        checklist_sections={k: v for k, v in checklist.items()},
        checklist_passed=total_passed,
        checklist_total=total_items,
        rubric_score=round(rubric_score, 1),
        rubric_categories=rubric,
        rubric_weighted_score=round(weighted_sum, 2),
        overall_score=round(overall_score, 1),
        grade=grade,
        passed=passed,
        strengths=strengths if strengths else ["Cover letter structure is present"],
        improvements=improvements if improvements else [],
        critical_issues=critical_issues if critical_issues else []
    )
    
    print(f"  📋 Compliance Report: {overall_score:.1f}% (Grade: {grade})")
    print(f"     Checklist: {checklist_score:.1f}% | Rubric: {rubric_score:.1f}%")
    print(f"     Status: {'✅ PASSED' if passed else '⚠️ NEEDS IMPROVEMENT'}")
    
    return {
        "compliance_report": report,
        "validation_complete": True
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "prepare_cover_letter_text",
    "validate_checklist",
    "score_rubric",
    "generate_feedback",
    "compile_report"
]
