"""
Test script for Resource Compliance Subgraph

Validates resume against checklists and rubrics.

Run: python -m subgraphs.resource_compliance.test
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


def save_report_json(report, filename_prefix="compliance_report"):
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
    Test Resource Compliance using full pipeline:
    1. JD Extractor → structured_jd
    2. Experience Selector → selected_experiences
    3. Experience Rewriter → rewritten content
    4. Resume Builder → resume_json
    5. Resource Compliance → compliance report
    """
    from subgraphs.jd_extractor import extract_jd_from_url, extract_jd_from_text
    from subgraphs.skill_matcher import match_skills_to_jd
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.github_ranker import rank_github_projects
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume
    from subgraphs.resource_compliance import validate_resume_compliance, get_compliance_summary
    
    print("=" * 70)
    print("Test: Full Pipeline - Resource Compliance")
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
    
    # ===== STEP 2: Match Skills =====
    print("\n" + "─" * 50)
    print("🎯 Step 2: Matching Skills...")
    print("─" * 50)
    
    skill_result = match_skills_to_jd(structured_jd)
    skill_match_result = skill_result.get("skill_match_result")
    print(f"✅ Skill Match: {skill_match_result.match_percentage:.1f}%")
    
    # ===== STEP 3: Select & Rewrite Experiences =====
    print("\n" + "─" * 50)
    print("👔 Step 3: Selecting & Rewriting...")
    print("─" * 50)
    
    exp_result = select_experiences_for_jd(structured_jd, max_experiences=4)
    proj_result = rank_github_projects(structured_jd, max_projects=2)
    
    rewrite_result = rewrite_for_jd(
        structured_jd=structured_jd,
        selected_experiences=exp_result["selected_experiences"],
        selected_projects=proj_result.get("selected_projects", [])
    )
    print(f"✅ Rewritten: {len(rewrite_result['rewritten_experiences'])} experiences")
    
    # ===== STEP 4: Build Resume =====
    print("\n" + "─" * 50)
    print("📋 Step 4: Building Resume...")
    print("─" * 50)
    
    resume_result = build_resume(
        structured_jd=structured_jd,
        rewritten_experiences=rewrite_result["rewritten_experiences"],
        rewritten_projects=rewrite_result["rewritten_projects"],
        skill_match_result=skill_match_result
    )
    
    resume_json = resume_result["resume_json"]
    print(f"✅ Resume: {len(resume_json.experience)} experiences, {len(resume_json.projects)} projects")
    
    # ===== STEP 5: Validate Compliance =====
    print("\n" + "─" * 50)
    print("✅ Step 5: Resource Compliance Validation...")
    print("─" * 50)
    
    result = validate_resume_compliance(resume_json)
    
    if result["error"]:
        print(f"❌ Compliance Error: {result['error']}")
        return None
    
    report = result["compliance_report"]
    
    # Save report
    save_report_json(report)
    
    # ===== DISPLAY RESULTS =====
    print("\n" + "=" * 70)
    print("📊 COMPLIANCE VALIDATION RESULTS")
    print("=" * 70)
    
    print(f"\n🎯 Overall Score: {report.overall_score}/100")
    print(f"   Grade: {report.grade}")
    print(f"   Status: {'✅ PASSED' if report.passed else '⚠️ NEEDS IMPROVEMENT'}")
    
    print(f"\n📋 Checklist Score: {report.checklist_score}%")
    print(f"   Items Passed: {report.checklist_passed}/{report.checklist_total}")
    
    print(f"\n📊 Rubric Score: {report.rubric_score}%")
    
    # Rubric details
    print("\n📈 Rubric Categories:")
    for score in report.rubric_categories:
        stars = "★" * score.score + "☆" * (4 - score.score)
        weight_pct = int(score.weight * 100)
        print(f"   {score.category:15} [{stars}] {score.score}/4 (Weight: {weight_pct}%)")
        if score.feedback:
            print(f"      {score.feedback[:60]}")
    
    # Checklist by section
    print("\n📋 Checklist by Section:")
    for section_name, section in report.checklist_sections.items():
        icon = "✅" if section.score >= 80 else "⚠️" if section.score >= 60 else "❌"
        print(f"   {icon} {section.section_name}: {section.items_passed}/{section.items_total} ({section.score:.0f}%)")
        
        # Show failed items
        failed = [r for r in section.results if not r.passed]
        for f in failed[:2]:
            req = "[REQ]" if f.required else "[OPT]"
            print(f"      ✗ {req} {f.item_text[:45]}")
    
    # Strengths
    if report.strengths:
        print("\n💪 Strengths:")
        for s in report.strengths[:5]:
            print(f"   ✓ {s[:65]}")
    
    # Critical Issues
    if report.critical_issues:
        print("\n🚨 Critical Issues:")
        for issue in report.critical_issues[:5]:
            print(f"   ✗ {issue[:65]}")
    
    # Improvements
    if report.improvements:
        print("\n💡 Improvements Needed:")
        for imp in report.improvements[:5]:
            print(f"   • {imp[:65]}")
    
    # Print full summary
    print("\n" + "─" * 70)
    print("FULL COMPLIANCE SUMMARY")
    print("─" * 70)
    summary = get_compliance_summary(report)
    print(summary)
    
    return result


def test_quick_compliance():
    """Test quick compliance check without full pipeline."""
    from subgraphs.jd_extractor import extract_jd_from_text
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume
    from subgraphs.resource_compliance import quick_compliance_check
    
    print("\n" + "=" * 70)
    print("Test: Quick Compliance Check")
    print("=" * 70)
    
    # Quick resume build
    jd_result = extract_jd_from_text(STANDARD_JD_TEXT)
    structured_jd = jd_result["structured_jd"]
    
    exp_result = select_experiences_for_jd(structured_jd, max_experiences=3)
    
    rewrite_result = rewrite_for_jd(
        structured_jd=structured_jd,
        selected_experiences=exp_result["selected_experiences"],
        selected_projects=[]
    )
    
    resume_result = build_resume(
        structured_jd=structured_jd,
        rewritten_experiences=rewrite_result["rewritten_experiences"],
        rewritten_projects=[]
    )
    
    # Quick check
    result = quick_compliance_check(resume_result["resume_json"])
    
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
    │                   RESOURCE COMPLIANCE SUBGRAPH                       │
    ├──────────────────────────────────────────────────────────────────────┤
    │                                                                      │
    │   START                                                              │
    │     │                                                                │
    │     ▼                                                                │
    │   ┌─────────────────────────┐                                       │
    │   │  prepare_resume_text    │  ← Extract text from ResumeJSON       │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │  validate_checklist     │  ← Check each item PASS/FAIL          │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │     score_rubric        │  ← Score 1-4 per category             │
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
    │ Personal Info      │ Name, email, phone, LinkedIn                      │
    │ Education          │ Institution, degree, dates, GPA                   │
    │ Experience         │ Action verbs, metrics, dates, no passive voice    │
    │ Skills             │ Organized, technical, no soft skills              │
    │ Format             │ Length, margins, consistency                      │
    │ Content            │ No pronouns, keywords, varied verbs               │
    └────────────────────┴───────────────────────────────────────────────────┘
    
    Rubric Scoring (1-4):
    ┌────────────────────┬────────┬─────────────────────────────────────────┐
    │ Category           │ Weight │ Description                             │
    ├────────────────────┼────────┼─────────────────────────────────────────┤
    │ Format             │  20%   │ Layout, spacing, appearance             │
    │ Education          │  20%   │ Completeness, organization              │
    │ Experience         │  40%   │ Action verbs, achievements, metrics     │
    │ Activities/Honors  │  20%   │ Skills, certifications, awards          │
    └────────────────────┴────────┴─────────────────────────────────────────┘
    
    Grading Scale:
    ┌───────┬──────────┬─────────────────────────────────────────────────────┐
    │ Grade │ Score    │ Meaning                                             │
    ├───────┼──────────┼─────────────────────────────────────────────────────┤
    │ A     │ 90-100   │ Excellent - Interview Ready                         │
    │ B     │ 80-89    │ Good - Minor Polish Needed                          │
    │ C     │ 70-79    │ Fair - Improvements Required (Pass threshold)       │
    │ D     │ 60-69    │ Below Average - Major Revisions                     │
    │ F     │ <60      │ Needs Complete Overhaul                             │
    └───────┴──────────┴─────────────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    print("\n🧪 Resource Compliance Subgraph Tests\n")
    print(f"📌 Standard Test JD: Amazon Applied Scientist")
    print(f"   {STANDARD_JD_URL}\n")
    
    # Test 1: Full pipeline
    result = test_full_pipeline()
    
    # Test 2: Quick check
    # test_quick_compliance()
    
    # Show graph structure
    test_graph_visualization()
    
    print("\n" + "=" * 70)
    print("Tests Complete!")
    print("=" * 70)
