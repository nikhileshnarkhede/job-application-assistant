"""
Test script for Cover Letter Compliance Subgraph

Validates cover letter against checklists and rubrics.

Run: python -m subgraphs.cover_letter_compliance.test
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
load_dotenv()

from subgraphs.test_constants import STANDARD_JD_URL, STANDARD_JD_TEXT

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def save_report_json(report, filename_prefix="cl_compliance_report"):
    """Save compliance report to JSON file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Convert to dict
    if hasattr(report, 'model_dump'):
        report_dict = report.model_dump()
    elif hasattr(report, 'dict'):
        report_dict = report.dict()
    else:
        report_dict = dict(report)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Saved report to: {filepath}")
    return filepath


def test_full_pipeline():
    """
    Test Cover Letter Compliance using full pipeline:
    1. JD Extractor → structured_jd
    2. Resume Builder → resume_json
    3. Cover Letter Generator → cover_letter
    4. Cover Letter Compliance → compliance report
    """
    from subgraphs.jd_extractor import extract_jd_from_url, extract_jd_from_text
    from subgraphs.skill_matcher import match_skills_to_jd
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.github_ranker import rank_github_projects
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume
    from subgraphs.cover_letter_generator import generate_cover_letter_for_job
    from subgraphs.cover_letter_compliance import (
        validate_cover_letter_compliance,
        get_cover_letter_compliance_summary
    )
    
    print("=" * 70)
    print("Test: Full Pipeline - Cover Letter Compliance")
    print("=" * 70)
    print(f"\n🔗 JD URL: {STANDARD_JD_URL}")
    
    # ===== STEP 1: Extract JD =====
    print("\n" + "─" * 50)
    print("📄 Step 1: Extracting JD...")
    print("─" * 50)
    
    jd_result = extract_jd_from_url(STANDARD_JD_URL)
    if jd_result["error"]:
        print(f"  ⚠️ URL failed, using fallback...")
        jd_result = extract_jd_from_text(STANDARD_JD_TEXT)
    
    if jd_result["error"]:
        print(f"❌ JD Error: {jd_result['error']}")
        return None
    
    structured_jd = jd_result["structured_jd"]
    print(f"✅ JD: {structured_jd.company_name} - {structured_jd.role_title}")
    
    # ===== STEP 2: Build Resume =====
    print("\n" + "─" * 50)
    print("📋 Step 2: Building Resume...")
    print("─" * 50)
    
    skill_result = match_skills_to_jd(structured_jd)
    exp_result = select_experiences_for_jd(structured_jd, max_experiences=3)
    proj_result = rank_github_projects(structured_jd, max_projects=2)
    
    rewrite_result = rewrite_for_jd(
        structured_jd=structured_jd,
        selected_experiences=exp_result["selected_experiences"],
        selected_projects=proj_result.get("selected_projects", [])
    )
    
    resume_result = build_resume(
        structured_jd=structured_jd,
        rewritten_experiences=rewrite_result["rewritten_experiences"],
        rewritten_projects=rewrite_result["rewritten_projects"],
        skill_match_result=skill_result.get("skill_match_result")
    )
    
    resume_json = resume_result["resume_json"]
    print(f"✅ Resume: {len(resume_json.experience)} experiences")
    
    # ===== STEP 3: Generate Cover Letter =====
    print("\n" + "─" * 50)
    print("✉️ Step 3: Generating Cover Letter...")
    print("─" * 50)
    
    cl_result = generate_cover_letter_for_job(
        structured_jd=structured_jd,
        resume_json=resume_json,
        tone="professional"
    )
    
    if cl_result["error"]:
        print(f"❌ Cover Letter Error: {cl_result['error']}")
        return None
    
    cover_letter = cl_result["cover_letter"]
    print(f"✅ Cover Letter: {cover_letter.word_count} words")
    
    # ===== STEP 4: Validate Compliance =====
    print("\n" + "─" * 50)
    print("✅ Step 4: Cover Letter Compliance Validation...")
    print("─" * 50)
    
    result = validate_cover_letter_compliance(
        cover_letter=cover_letter,
        structured_jd=structured_jd
    )
    
    if result["error"]:
        print(f"❌ Compliance Error: {result['error']}")
        return None
    
    report = result["compliance_report"]
    
    # Save report
    save_report_json(report)
    
    # ===== DISPLAY RESULTS =====
    print("\n" + "=" * 70)
    print("📊 COVER LETTER COMPLIANCE RESULTS")
    print("=" * 70)
    
    print(f"\n🎯 Overall Score: {report.overall_score}/100")
    print(f"   Grade: {report.grade}")
    print(f"   Status: {'✅ PASSED' if report.passed else '⚠️ NEEDS IMPROVEMENT'}")
    
    print(f"\n📋 Checklist Score: {report.checklist_score}%")
    print(f"   Items Passed: {report.checklist_passed}/{report.checklist_total}")
    
    print(f"\n📊 Rubric Score: {report.rubric_score}%")
    
    # Rubric details
    print("\n📈 Rubric Categories (1-3 scale):")
    for score in report.rubric_categories:
        stars = "★" * score.score + "☆" * (3 - score.score)
        weight_pct = int(score.weight * 100)
        print(f"   {score.category[:30]:30} [{stars}] {score.score}/3 ({weight_pct}%)")
        if score.feedback:
            print(f"      {score.feedback[:55]}")
    
    # Checklist by section
    print("\n📋 Checklist by Section:")
    for section_name, section in report.checklist_sections.items():
        icon = "✅" if section.score >= 80 else "⚠️" if section.score >= 60 else "❌"
        print(f"   {icon} {section.section_name}: {section.items_passed}/{section.items_total} ({section.score:.0f}%)")
        
        # Show failed items
        failed = [r for r in section.results if not r.passed]
        for f in failed[:2]:
            req = "[REQ]" if f.required else "[OPT]"
            print(f"      ✗ {req} {f.item_text[:40]}")
    
    # Strengths
    if report.strengths:
        print("\n💪 Strengths:")
        for s in report.strengths[:4]:
            print(f"   ✓ {s[:60]}")
    
    # Critical Issues
    if report.critical_issues:
        print("\n🚨 Critical Issues:")
        for issue in report.critical_issues[:4]:
            print(f"   ✗ {issue[:60]}")
    
    # Improvements
    if report.improvements:
        print("\n💡 Improvements:")
        for imp in report.improvements[:4]:
            print(f"   • {imp[:60]}")
    
    # Print full summary
    print("\n" + "─" * 70)
    print("FULL COMPLIANCE SUMMARY")
    print("─" * 70)
    summary = get_cover_letter_compliance_summary(report)
    print(summary)
    
    return result


def test_quick_compliance():
    """Test quick compliance check with sample cover letter text."""
    from subgraphs.cover_letter_compliance import quick_cover_letter_compliance_check
    
    print("\n" + "=" * 70)
    print("Test: Quick Cover Letter Compliance Check")
    print("=" * 70)
    
    # Sample cover letter text
    sample_text = """
John Smith
john.smith@email.com | (555) 123-4567
San Francisco, CA

January 15, 2024

Amazon
Seattle, WA

Dear Hiring Manager,

Amazon's leadership in cloud computing and customer obsession makes this Applied Scientist role particularly exciting. I am drawn to your mission of being Earth's most customer-centric company and believe my background in machine learning aligns perfectly with your team's goals.

At my current role at TechCorp, I developed a recommendation system that increased user engagement by 35% and drove $5M in additional revenue. This experience building production ML systems at scale directly relates to the challenges Amazon faces in delivering personalized customer experiences.

What specifically attracts me to Amazon is your commitment to innovation and the opportunity to work on problems that impact millions of customers daily. Your recent advances in Alexa AI and AWS machine learning services demonstrate the kind of cutting-edge work I want to contribute to.

Thank you for considering my application. I would welcome the opportunity to discuss how my experience in ML systems can contribute to Amazon's continued innovation. I am available for an interview at your convenience.

Sincerely,

John Smith
    """
    
    result = quick_cover_letter_compliance_check(sample_text)
    
    print(f"\n📊 Quick Compliance Results:")
    print(f"   Overall Score: {result['overall_score']}/100")
    print(f"   Checklist: {result['checklist_score']}%")
    print(f"   Rubric: {result['rubric_score']}%")
    print(f"   Grade: {result['grade']}")
    print(f"   Passed: {'✅ Yes' if result['passed'] else '❌ No'}")
    print(f"   Critical Issues: {result['critical_issues_count']}")
    
    return result


def test_graph_visualization():
    """Show graph structure."""
    print("\n" + "=" * 70)
    print("Graph Structure")
    print("=" * 70)
    
    print("""
    ┌──────────────────────────────────────────────────────────────────────┐
    │                 COVER LETTER COMPLIANCE SUBGRAPH                     │
    ├──────────────────────────────────────────────────────────────────────┤
    │                                                                      │
    │   START                                                              │
    │     │                                                                │
    │     ▼                                                                │
    │   ┌─────────────────────────┐                                       │
    │   │prepare_cover_letter_text│  ← Extract text from CoverLetter      │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │  validate_checklist     │  ← Check each item PASS/FAIL          │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │     score_rubric        │  ← Score 1-3 per section              │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │   generate_feedback     │  ← Strengths & improvements           │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │    compile_report       │  ← Create ComplianceReport            │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │              END                                                     │
    │                                                                      │
    └──────────────────────────────────────────────────────────────────────┘
    
    Checklist Sections:
    ┌────────────────────┬───────────────────────────────────────────────────┐
    │ Section            │ Key Checks                                        │
    ├────────────────────┼───────────────────────────────────────────────────┤
    │ Research           │ Position review, company research, fit statement  │
    │ Introduction       │ Position ID, creative hook, interest expressed    │
    │ Body               │ Qualifications, keywords, examples, storytelling  │
    │ Closing            │ Thanks, enthusiasm, next steps, follow-up         │
    │ Format             │ One page, contact info, formal closing, signature │
    └────────────────────┴───────────────────────────────────────────────────┘
    
    Rubric Scoring (1-3):
    ┌────────────────────────────┬────────┬─────────────────────────────────┐
    │ Category                   │ Weight │ Description                     │
    ├────────────────────────────┼────────┼─────────────────────────────────┤
    │ Business Format & Quality  │  25%   │ Format, grammar, spelling       │
    │ Section 1: Introduction    │  25%   │ Hook, position, interest        │
    │ Section 2: Skills & Exp    │  30%   │ Qualifications, relevance       │
    │ Section 3: Closing         │  20%   │ Thanks, follow-up, enthusiasm   │
    └────────────────────────────┴────────┴─────────────────────────────────┘
    
    Grading Scale:
    ┌───────┬──────────┬─────────────────────────────────────────────────────┐
    │ Grade │ Score    │ Meaning                                             │
    ├───────┼──────────┼─────────────────────────────────────────────────────┤
    │ A     │ 90-100   │ Excellent - Should get the interview                │
    │ B     │ 80-89    │ Good - Could land an interview                      │
    │ C     │ 70-79    │ Fair - Average, borderline case (Pass threshold)    │
    │ D     │ 60-69    │ Below Average - Needs significant improvement       │
    │ F     │ <60      │ Would be discarded during screening                 │
    └───────┴──────────┴─────────────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    print("\n🧪 Cover Letter Compliance Subgraph Tests\n")
    print(f"📌 Standard Test JD: Amazon Applied Scientist")
    print(f"   {STANDARD_JD_URL}\n")
    
    # Test 1: Quick compliance check first
    test_quick_compliance()
    
    # Test 2: Full pipeline
    result = test_full_pipeline()
    
    # Show graph structure
    test_graph_visualization()
    
    print("\n" + "=" * 70)
    print("Tests Complete!")
    print("=" * 70)
