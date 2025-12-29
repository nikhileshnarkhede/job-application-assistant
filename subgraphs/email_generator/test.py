"""
Test script for Email Generator Subgraph

Generates professional outreach emails for job search.

Run: python -m subgraphs.email_generator.test
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


def save_email(email, filename_prefix="email"):
    """Save generated email to file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save email text
    text_filename = f"{filename_prefix}_{timestamp}.txt"
    text_filepath = os.path.join(OUTPUT_DIR, text_filename)
    
    with open(text_filepath, 'w', encoding='utf-8') as f:
        f.write(f"SUBJECT: {email.subject}\n")
        f.write("=" * 50 + "\n\n")
        f.write(email.full_text)
    
    print(f"\n💾 Saved email to: {text_filepath}")
    return text_filepath


def test_cold_outreach():
    """Test cold outreach email generation."""
    from subgraphs.jd_extractor import extract_jd_from_url, extract_jd_from_text
    from subgraphs.skill_matcher import match_skills_to_jd
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume
    from subgraphs.email_generator import (
        generate_cold_outreach,
        get_email_summary,
        EmailRecipient
    )
    
    print("=" * 70)
    print("Test 1: Cold Outreach Email")
    print("=" * 70)
    
    # Quick setup
    print("\n📄 Setting up context...")
    jd_result = extract_jd_from_url(STANDARD_JD_URL)
    if jd_result["error"]:
        jd_result = extract_jd_from_text(STANDARD_JD_TEXT)
    
    structured_jd = jd_result["structured_jd"]
    print(f"✅ JD: {structured_jd.company_name} - {structured_jd.role_title}")
    
    # Build resume
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
    
    # Generate cold outreach
    print("\n✉️ Generating cold outreach email...")
    result = generate_cold_outreach(
        structured_jd=structured_jd,
        resume_json=resume_json,
        recruiter_name="Sarah Chen",
        recruiter_title="Technical Recruiter",
        how_found="LinkedIn"
    )
    
    if result["error"]:
        print(f"❌ Error: {result['error']}")
        return None
    
    email = result["generated_email"]
    
    # Save and display
    save_email(email, "cold_outreach")
    
    print("\n" + "─" * 50)
    print("📧 COLD OUTREACH EMAIL")
    print("─" * 50)
    print(f"\n📌 Subject: {email.subject}")
    print(f"\n{email.full_text}")
    print("\n" + "─" * 50)
    
    print(get_email_summary(email))
    
    return result


def test_followup_email():
    """Test application follow-up email generation."""
    from subgraphs.jd_extractor import extract_jd_from_text
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume
    from subgraphs.email_generator import generate_followup_email, get_email_summary
    
    print("\n" + "=" * 70)
    print("Test 2: Application Follow-Up Email")
    print("=" * 70)
    
    # Quick setup
    jd_result = extract_jd_from_text(STANDARD_JD_TEXT)
    structured_jd = jd_result["structured_jd"]
    
    exp_result = select_experiences_for_jd(structured_jd, max_experiences=2)
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
    
    # Generate follow-up
    print("\n✉️ Generating follow-up email...")
    result = generate_followup_email(
        structured_jd=structured_jd,
        resume_json=resume_result["resume_json"],
        application_date="January 15, 2024",
        recruiter_name="Recruiting Team"
    )
    
    if result["error"]:
        print(f"❌ Error: {result['error']}")
        return None
    
    email = result["generated_email"]
    save_email(email, "followup")
    
    print("\n" + "─" * 50)
    print("📧 FOLLOW-UP EMAIL")
    print("─" * 50)
    print(f"\n📌 Subject: {email.subject}")
    print(f"\n{email.full_text}")
    print("\n" + "─" * 50)
    
    print(get_email_summary(email))
    
    return result


def test_thank_you_email():
    """Test thank you email generation."""
    from subgraphs.jd_extractor import extract_jd_from_text
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume
    from subgraphs.email_generator import generate_thank_you_email, get_email_summary
    
    print("\n" + "=" * 70)
    print("Test 3: Thank You Email")
    print("=" * 70)
    
    # Quick setup
    jd_result = extract_jd_from_text(STANDARD_JD_TEXT)
    structured_jd = jd_result["structured_jd"]
    
    exp_result = select_experiences_for_jd(structured_jd, max_experiences=2)
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
    
    # Generate thank you
    print("\n✉️ Generating thank you email...")
    result = generate_thank_you_email(
        structured_jd=structured_jd,
        resume_json=resume_result["resume_json"],
        interviewer_name="Dr. Jennifer Martinez",
        interview_date="today",
        custom_context="We discussed the challenges of building real-time ML systems and your team's work on recommendation algorithms."
    )
    
    if result["error"]:
        print(f"❌ Error: {result['error']}")
        return None
    
    email = result["generated_email"]
    save_email(email, "thank_you")
    
    print("\n" + "─" * 50)
    print("📧 THANK YOU EMAIL")
    print("─" * 50)
    print(f"\n📌 Subject: {email.subject}")
    print(f"\n{email.full_text}")
    print("\n" + "─" * 50)
    
    print(get_email_summary(email))
    
    return result


def test_all_email_types():
    """Test all email types with full context."""
    from subgraphs.jd_extractor import extract_jd_from_text
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume
    from subgraphs.email_generator import (
        generate_outreach_email,
        EmailType,
        EmailTone,
        EmailRecipient
    )
    
    print("\n" + "=" * 70)
    print("Test 4: All Email Types")
    print("=" * 70)
    
    # Setup
    jd_result = extract_jd_from_text(STANDARD_JD_TEXT)
    structured_jd = jd_result["structured_jd"]
    
    exp_result = select_experiences_for_jd(structured_jd, max_experiences=2)
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
    resume_json = resume_result["resume_json"]
    
    # Test each email type
    email_types = [
        (EmailType.COLD_OUTREACH, "Cold Outreach"),
        (EmailType.APPLICATION_FOLLOWUP, "Follow-Up"),
        (EmailType.REFERRAL_REQUEST, "Referral Request"),
        (EmailType.NETWORKING, "Networking"),
    ]
    
    for email_type, name in email_types:
        print(f"\n📧 Generating {name}...")
        
        recipient = EmailRecipient(
            name="Alex Johnson",
            title="Engineering Manager",
            company=structured_jd.company_name,
            how_found="LinkedIn"
        )
        
        result = generate_outreach_email(
            structured_jd=structured_jd,
            resume_json=resume_json,
            recipient=recipient,
            email_type=email_type,
            tone=EmailTone.PROFESSIONAL,
            application_date="January 15, 2024" if email_type == EmailType.APPLICATION_FOLLOWUP else None
        )
        
        if result["error"]:
            print(f"   ❌ Error: {result['error']}")
        else:
            email = result["generated_email"]
            print(f"   ✅ {name}: {email.word_count} words, {email.personalization_score:.0f}% personalized")
            print(f"      Subject: {email.subject[:50]}...")


def test_graph_visualization():
    """Show graph structure."""
    print("\n" + "=" * 70)
    print("Graph Structure")
    print("=" * 70)
    
    print("""
    ┌──────────────────────────────────────────────────────────────────────┐
    │                     EMAIL GENERATOR SUBGRAPH                         │
    ├──────────────────────────────────────────────────────────────────────┤
    │                                                                      │
    │   START                                                              │
    │     │                                                                │
    │     ▼                                                                │
    │   ┌─────────────────────────┐                                       │
    │   │    prepare_context      │  ← Gather candidate, job, recipient   │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │    select_template      │  ← Choose email type guidelines       │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │    generate_email       │  ← LLM with 15-shot examples          │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │     format_output       │  ← Validate and format                │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │              END                                                     │
    │                                                                      │
    └──────────────────────────────────────────────────────────────────────┘
    
    Email Types Supported:
    ┌────────────────────────┬────────────┬─────────────────────────────────┐
    │ Type                   │ Words      │ Use Case                        │
    ├────────────────────────┼────────────┼─────────────────────────────────┤
    │ cold_outreach          │ 100-150    │ Initial contact with recruiter  │
    │ application_followup   │ 80-120     │ After submitting application    │
    │ referral_request       │ 120-180    │ Asking for internal referral    │
    │ thank_you              │ 100-150    │ After interview                 │
    │ networking             │ 100-150    │ General networking              │
    │ information_request    │ 100-150    │ Asking about role/company       │
    └────────────────────────┴────────────┴─────────────────────────────────┘
    
    Tone Options:
    ┌─────────────────┬───────────────────────────────────────────────────────┐
    │ Tone            │ Description                                           │
    ├─────────────────┼───────────────────────────────────────────────────────┤
    │ professional    │ Respectful, direct, confident (default)               │
    │ friendly        │ Warmer, uses contractions                             │
    │ enthusiastic    │ Shows genuine excitement                              │
    │ formal          │ Traditional language, no contractions                 │
    └─────────────────┴───────────────────────────────────────────────────────┘
    
    Quality Metrics:
    ┌───────────────────────────┬────────────────────────────────────────────┐
    │ Metric                    │ What It Measures                           │
    ├───────────────────────────┼────────────────────────────────────────────┤
    │ Word Count                │ Email length (type-specific ideal range)   │
    │ Personalization Score     │ Specific details included (0-100%)         │
    │ Has Clear Ask             │ Specific, actionable request present       │
    │ Has Value Proposition     │ Leads with what you offer                  │
    └───────────────────────────┴────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    print("\n🧪 Email Generator Subgraph Tests\n")
    print(f"📌 Standard Test JD: Amazon Applied Scientist")
    print(f"   {STANDARD_JD_URL}\n")
    
    # Test 1: Cold outreach
    test_cold_outreach()
    
    # Test 2: Follow-up
    test_followup_email()
    
    # Test 3: Thank you
    test_thank_you_email()
    
    # Test 4: All types (quick)
    # test_all_email_types()
    
    # Show graph structure
    test_graph_visualization()
    
    print("\n" + "=" * 70)
    print("Tests Complete!")
    print("=" * 70)
