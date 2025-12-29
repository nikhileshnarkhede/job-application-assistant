"""
Test script for Excel Writer Subgraph

Saves job application data to Excel tracking spreadsheet.

Run: python -m subgraphs.excel_writer.test
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
load_dotenv()

from subgraphs.test_constants import STANDARD_JD_URL, STANDARD_JD_TEXT

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def test_full_pipeline():
    """
    Test Excel Writer with full pipeline data.
    """
    from subgraphs.jd_extractor import extract_jd_from_url, extract_jd_from_text
    from subgraphs.skill_matcher import match_skills_to_jd
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume
    from subgraphs.resource_compliance import validate_resume_compliance
    from subgraphs.excel_writer import (
        save_application_to_excel,
        get_applications_summary,
        ApplicationStatus,
        ApplicationSource
    )
    
    print("=" * 70)
    print("Test 1: Full Pipeline - Excel Writer")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    excel_path = os.path.join(OUTPUT_DIR, "job_applications_test.xlsx")
    
    # ===== STEP 1: Extract JD =====
    print("\n📄 Step 1: Extracting JD...")
    jd_result = extract_jd_from_url(STANDARD_JD_URL)
    if jd_result["error"]:
        jd_result = extract_jd_from_text(STANDARD_JD_TEXT)
    
    structured_jd = jd_result["structured_jd"]
    print(f"✅ JD: {structured_jd.company_name} - {structured_jd.role_title}")
    
    # ===== STEP 2: Build Resume =====
    print("\n📋 Step 2: Building Resume...")
    skill_result = match_skills_to_jd(structured_jd)
    exp_result = select_experiences_for_jd(structured_jd, max_experiences=2)
    rewrite_result = rewrite_for_jd(
        structured_jd=structured_jd,
        selected_experiences=exp_result["selected_experiences"],
        selected_projects=[]
    )
    resume_result = build_resume(
        structured_jd=structured_jd,
        rewritten_experiences=rewrite_result["rewritten_experiences"],
        rewritten_projects=[],
        skill_match_result=skill_result.get("skill_match_result")
    )
    resume_json = resume_result["resume_json"]
    print(f"✅ Resume built")
    
    # ===== STEP 3: Get Compliance Score =====
    print("\n✅ Step 3: Getting Compliance Score...")
    compliance_result = validate_resume_compliance(resume_json)
    resume_score = 0.0
    if compliance_result.get("compliance_report"):
        resume_score = compliance_result["compliance_report"].overall_score
    print(f"✅ Resume Score: {resume_score:.1f}%")
    
    # ===== STEP 4: Save to Excel =====
    print("\n💾 Step 4: Saving to Excel...")
    result = save_application_to_excel(
        structured_jd=structured_jd,
        resume_json=resume_json,
        resume_score=resume_score,
        cover_letter_score=82.5,  # Example score
        file_path=excel_path,
        status=ApplicationStatus.APPLIED,
        source=ApplicationSource.LINKEDIN,
        notes="Applied via LinkedIn Easy Apply",
        why_interested="Great team, interesting ML challenges"
    )
    
    if result["error"]:
        print(f"❌ Error: {result['error']}")
        return None
    
    print(f"✅ Saved to: {result['file_path']}")
    print(f"   Row number: {result['row_number']}")
    
    # Print summary
    print("\n" + get_applications_summary(excel_path))
    
    return result


def test_quick_save():
    """Test quick save functionality."""
    from subgraphs.excel_writer import (
        quick_save_application,
        ApplicationStatus,
        ApplicationSource
    )
    
    print("\n" + "=" * 70)
    print("Test 2: Quick Save Applications")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    excel_path = os.path.join(OUTPUT_DIR, "job_applications_test.xlsx")
    
    # Save multiple applications quickly
    applications = [
        {
            "company": "Google",
            "role": "Senior ML Engineer",
            "job_url": "https://careers.google.com/123",
            "status": ApplicationStatus.APPLIED,
            "source": ApplicationSource.COMPANY_WEBSITE,
            "notes": "Referred by John"
        },
        {
            "company": "Meta",
            "role": "Research Scientist",
            "job_url": "https://metacareers.com/456",
            "status": ApplicationStatus.PHONE_SCREEN,
            "source": ApplicationSource.REFERRAL,
            "notes": "Phone screen scheduled for next week"
        },
        {
            "company": "OpenAI",
            "role": "ML Engineer",
            "job_url": "https://openai.com/careers/789",
            "status": ApplicationStatus.NOT_APPLIED,
            "source": ApplicationSource.LINKEDIN,
            "notes": "Need to tailor resume"
        }
    ]
    
    for app in applications:
        print(f"\n📝 Saving: {app['company']} - {app['role']}")
        result = quick_save_application(
            company=app["company"],
            role=app["role"],
            job_url=app["job_url"],
            status=app["status"],
            source=app["source"],
            file_path=excel_path,
            notes=app["notes"]
        )
        
        if result["error"]:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Row: {result['row_number']}")
    
    return excel_path


def test_update_status():
    """Test status update functionality."""
    from subgraphs.excel_writer import (
        update_application_status,
        get_application_stats,
        ApplicationStatus
    )
    
    print("\n" + "=" * 70)
    print("Test 3: Update Application Status")
    print("=" * 70)
    
    excel_path = os.path.join(OUTPUT_DIR, "job_applications_test.xlsx")
    
    if not os.path.exists(excel_path):
        print("⚠️ No Excel file found. Run test_quick_save first.")
        return
    
    # Get stats first
    stats = get_application_stats(excel_path)
    print(f"\n📊 Current Stats:")
    print(f"   Total: {stats.get('total', 0)}")
    print(f"   By Status: {stats.get('by_status', {})}")
    
    # Note: To test update, you'd need a known application_id
    # This would come from a previous save operation
    print("\n💡 To test update, use:")
    print('   update_application_status("path.xlsx", "APP-xxx", ApplicationStatus.OFFER)')


def test_statistics():
    """Test statistics functionality."""
    from subgraphs.excel_writer import (
        get_application_stats,
        get_applications_summary
    )
    
    print("\n" + "=" * 70)
    print("Test 4: Application Statistics")
    print("=" * 70)
    
    excel_path = os.path.join(OUTPUT_DIR, "job_applications_test.xlsx")
    
    if not os.path.exists(excel_path):
        print("⚠️ No Excel file found. Run other tests first.")
        return
    
    # Get detailed stats
    stats = get_application_stats(excel_path)
    print(f"\n📊 Detailed Statistics:")
    print(f"   Total Applications: {stats.get('total', 0)}")
    print(f"   Unique Companies: {stats.get('unique_companies', 0)}")
    print(f"   By Status: {stats.get('by_status', {})}")
    print(f"   By Source: {stats.get('by_source', {})}")
    
    # Get formatted summary
    print("\n" + get_applications_summary(excel_path))


def test_graph_visualization():
    """Show graph structure."""
    print("\n" + "=" * 70)
    print("Graph Structure")
    print("=" * 70)
    
    print("""
    ┌──────────────────────────────────────────────────────────────────────┐
    │                      EXCEL WRITER SUBGRAPH                           │
    ├──────────────────────────────────────────────────────────────────────┤
    │                                                                      │
    │   START                                                              │
    │     │                                                                │
    │     ▼                                                                │
    │   ┌─────────────────────────┐                                       │
    │   │    prepare_record       │  ← Create ApplicationRecord           │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │load_or_create_workbook  │  ← Load existing or create new        │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │     write_record        │  ← Write row to spreadsheet           │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │   format_spreadsheet    │  ← Apply styling & formatting         │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │     save_workbook       │  ← Save and close file                │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │              END                                                     │
    │                                                                      │
    └──────────────────────────────────────────────────────────────────────┘
    
    Spreadsheet Columns (28 total):
    ┌────────────────────┬────────────────────┬────────────────────────────┐
    │ Basic Info         │ Tracking           │ Outcomes                   │
    ├────────────────────┼────────────────────┼────────────────────────────┤
    │ Application ID     │ Date Found         │ Resume Score               │
    │ Company            │ Date Applied       │ Cover Letter Score         │
    │ Role               │ Last Updated       │ Offer Amount               │
    │ Location           │ Status             │ Response Time              │
    │ Job URL            │ Source             │ Notes                      │
    │ Salary Range       │ Next Follow-Up     │ Key Requirements           │
    │ Work Type          │ Last Contact       │ Why Interested             │
    └────────────────────┴────────────────────┴────────────────────────────┘
    
    Application Status Options:
    ┌────────────────────┬───────────────────────────────────────────────────┐
    │ Status             │ Description                                       │
    ├────────────────────┼───────────────────────────────────────────────────┤
    │ Not Applied        │ Saved but not yet applied                         │
    │ Applied            │ Application submitted                             │
    │ Referred           │ Applied with internal referral                    │
    │ Phone Screen       │ Initial phone/video screening                     │
    │ Technical Interview│ Technical or coding interview                     │
    │ Onsite             │ Onsite or virtual onsite round                    │
    │ Final Round        │ Final interviews                                  │
    │ Offer              │ Received offer                                    │
    │ Accepted           │ Accepted offer                                    │
    │ Rejected           │ Application rejected                              │
    │ Withdrawn          │ Withdrew application                              │
    │ No Response        │ No response after reasonable time                 │
    └────────────────────┴───────────────────────────────────────────────────┘
    
    Application Sources:
    ┌────────────────────┬───────────────────────────────────────────────────┐
    │ Company Website    │ LinkedIn           │ Referral                    │
    │ Indeed             │ Glassdoor          │ Recruiter                   │
    │ Career Fair        │ Networking         │ Other                       │
    └────────────────────┴───────────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    print("\n🧪 Excel Writer Subgraph Tests\n")
    
    # Check for openpyxl
    try:
        import openpyxl
        print("✅ openpyxl installed")
    except ImportError:
        print("❌ openpyxl not installed. Run: pip install openpyxl")
        print("   Exiting tests.")
        sys.exit(1)
    
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    
    # Test 1: Full pipeline
    test_full_pipeline()
    
    # Test 2: Quick save multiple
    test_quick_save()
    
    # Test 3: Update status (info only)
    test_update_status()
    
    # Test 4: Statistics
    test_statistics()
    
    # Show graph structure
    test_graph_visualization()
    
    print("\n" + "=" * 70)
    print("Tests Complete!")
    print(f"📁 Check output at: {OUTPUT_DIR}")
    print("=" * 70)
