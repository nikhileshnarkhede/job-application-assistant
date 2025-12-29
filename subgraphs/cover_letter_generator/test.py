"""
Test script for Cover Letter Generator Subgraph

Generates personalized cover letters with company research.

Run: python -m subgraphs.cover_letter_generator.test
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


def save_cover_letter(cover_letter, research, filename_prefix="cover_letter"):
    """Save cover letter and research to files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save cover letter text
    text_filename = f"{filename_prefix}_{timestamp}.txt"
    text_filepath = os.path.join(OUTPUT_DIR, text_filename)
    
    with open(text_filepath, 'w', encoding='utf-8') as f:
        f.write(cover_letter.full_text)
    
    print(f"\n💾 Saved cover letter to: {text_filepath}")
    
    # Save metadata as JSON
    json_filename = f"{filename_prefix}_{timestamp}_meta.json"
    json_filepath = os.path.join(OUTPUT_DIR, json_filename)
    
    metadata = {
        "candidate_name": cover_letter.candidate_name,
        "company_name": cover_letter.company_name,
        "date": cover_letter.date,
        "word_count": cover_letter.word_count,
        "paragraph_count": cover_letter.paragraph_count,
        "company_mentions": cover_letter.company_mentions,
        "keywords_used": cover_letter.keywords_used,
        "personalization_score": cover_letter.personalization_score,
        "research": {
            "industry": research.industry if research else "",
            "core_values": research.core_values if research else [],
            "recent_news": research.recent_news if research else [],
            "mission": research.mission_statement if research else ""
        }
    }
    
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    return text_filepath


def test_full_pipeline():
    """
    Test Cover Letter Generator using full pipeline:
    1. JD Extractor → structured_jd
    2. Resume Builder → resume_json
    3. Cover Letter Generator → cover letter with company research
    """
    from subgraphs.jd_extractor import extract_jd_from_url, extract_jd_from_text
    from subgraphs.skill_matcher import match_skills_to_jd
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.github_ranker import rank_github_projects
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume
    from subgraphs.cover_letter_generator import (
        generate_cover_letter_for_job,
        get_cover_letter_summary,
        get_search_tool
    )
    
    print("=" * 70)
    print("Test: Full Pipeline - Cover Letter Generator")
    print("=" * 70)
    print(f"\n🔗 JD URL: {STANDARD_JD_URL}")
    
    # Check if DuckDuckGo is available
    search_tool = get_search_tool()
    if search_tool:
        print("✅ DuckDuckGo search: AVAILABLE")
    else:
        print("⚠️ DuckDuckGo search: NOT AVAILABLE (install duckduckgo-search)")
    
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
    
    result = generate_cover_letter_for_job(
        structured_jd=structured_jd,
        resume_json=resume_json,
        tone="professional",
        focus_areas=["technical skills", "innovation"],
        referral_name=None,  # Set to a name if you have a referral
        custom_hook=None
    )
    
    if result["error"]:
        print(f"❌ Generation Error: {result['error']}")
        return None
    
    cover_letter = result["cover_letter"]
    research = result["company_research"]
    
    # Save output
    save_cover_letter(cover_letter, research)
    
    # ===== DISPLAY RESULTS =====
    print("\n" + "=" * 70)
    print("📊 COVER LETTER GENERATION RESULTS")
    print("=" * 70)
    
    # Company Research
    if research:
        print("\n🔍 COMPANY RESEARCH:")
        print(f"   Company: {research.company_name}")
        print(f"   Industry: {research.industry}")
        if research.mission_statement:
            print(f"   Mission: {research.mission_statement[:100]}...")
        if research.core_values:
            print(f"   Values: {', '.join(research.core_values[:5])}")
        if research.recent_news:
            print(f"   Recent News: {len(research.recent_news)} items found")
            for news in research.recent_news[:2]:
                print(f"      • {news[:80]}...")
    
    # Cover Letter Stats
    print(f"\n📊 COVER LETTER STATS:")
    print(f"   Word Count: {cover_letter.word_count}")
    print(f"   Paragraphs: {cover_letter.paragraph_count}")
    print(f"   Company Mentions: {cover_letter.company_mentions}")
    print(f"   Keywords Used: {len(cover_letter.keywords_used)}")
    print(f"   Personalization Score: {cover_letter.personalization_score:.0f}%")
    
    if cover_letter.keywords_used:
        print(f"\n🔑 KEYWORDS INCORPORATED:")
        print(f"   {', '.join(cover_letter.keywords_used[:10])}")
    
    # Full Cover Letter
    print("\n" + "─" * 70)
    print("📝 GENERATED COVER LETTER")
    print("─" * 70)
    print(cover_letter.full_text)
    print("─" * 70)
    
    # Summary
    print("\n" + get_cover_letter_summary(cover_letter, research))
    
    return result


def test_quick_generation():
    """Test quick cover letter generation without full pipeline."""
    from subgraphs.jd_extractor import extract_jd_from_text
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume
    from subgraphs.cover_letter_generator import quick_cover_letter
    
    print("\n" + "=" * 70)
    print("Test: Quick Cover Letter Generation")
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
    
    # Quick generation
    cover_letter_text = quick_cover_letter(structured_jd, resume_result["resume_json"])
    
    print("\n📝 Quick Cover Letter:")
    print("─" * 50)
    print(cover_letter_text[:1000])
    print("..." if len(cover_letter_text) > 1000 else "")
    
    return cover_letter_text


def test_graph_visualization():
    """Show graph structure."""
    print("\n" + "=" * 70)
    print("Graph Structure")
    print("=" * 70)
    
    print("""
    ┌──────────────────────────────────────────────────────────────────────┐
    │                  COVER LETTER GENERATOR SUBGRAPH                     │
    ├──────────────────────────────────────────────────────────────────────┤
    │                                                                      │
    │   START                                                              │
    │     │                                                                │
    │     ▼                                                                │
    │   ┌─────────────────────────┐                                       │
    │   │   research_company      │  ← DuckDuckGo search (no API key)     │
    │   │   - Mission & values    │                                       │
    │   │   - Recent news         │                                       │
    │   │   - Company culture     │                                       │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │ extract_candidate_      │  ← Key achievements from resume       │
    │   │     highlights          │                                       │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │ generate_cover_letter   │  ← LLM with 10-shot examples          │
    │   │   - Introduction hook   │                                       │
    │   │   - Skills paragraph    │                                       │
    │   │   - Company fit         │                                       │
    │   │   - Closing CTA         │                                       │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │    format_output        │  ← Clean formatting                   │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │              END                                                     │
    │                                                                      │
    └──────────────────────────────────────────────────────────────────────┘
    
    Company Research (via DuckDuckGo):
    ┌────────────────────┬───────────────────────────────────────────────────┐
    │ Search Query       │ Purpose                                           │
    ├────────────────────┼───────────────────────────────────────────────────┤
    │ {company} mission  │ Find mission statement and core values            │
    │ {company} news     │ Recent announcements, launches, achievements      │
    │ {company} culture  │ Work environment, employee reviews                │
    │ {company} tech     │ Technology stack, engineering practices           │
    └────────────────────┴───────────────────────────────────────────────────┘
    
    Cover Letter Structure:
    ┌────────────────────┬────────┬─────────────────────────────────────────┐
    │ Section            │ Words  │ Purpose                                 │
    ├────────────────────┼────────┼─────────────────────────────────────────┤
    │ Introduction       │ 40-60  │ Hook, position, interest                │
    │ Body 1 (Skills)    │ 60-80  │ Quantified achievements, JD match       │
    │ Body 2 (Fit)       │ 60-80  │ Company research, why this company      │
    │ Closing            │ 30-50  │ Thank you, call to action               │
    └────────────────────┴────────┴─────────────────────────────────────────┘
    
    Personalization Score:
    ┌───────────────────────────┬────────┬──────────────────────────────────┐
    │ Factor                    │ Points │ Criteria                         │
    ├───────────────────────────┼────────┼──────────────────────────────────┤
    │ Company mentions          │ +30    │ Company name appears 2+ times    │
    │ Keywords incorporated     │ +30    │ 3+ JD keywords used naturally    │
    │ Research reference        │ +20    │ Mentions recent news/values      │
    │ Optimal length            │ +20    │ 250-400 words                    │
    └───────────────────────────┴────────┴──────────────────────────────────┘
    """)


if __name__ == "__main__":
    print("\n🧪 Cover Letter Generator Subgraph Tests\n")
    print(f"📌 Standard Test JD: Amazon Applied Scientist")
    print(f"   {STANDARD_JD_URL}\n")
    
    # Check for DuckDuckGo dependency
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        print("✅ DuckDuckGo search available")
    except ImportError:
        print("⚠️ DuckDuckGo not installed. Run: pip install duckduckgo-search")
        print("   Cover letter will be generated without company research.\n")
    
    # Test 1: Full pipeline
    result = test_full_pipeline()
    
    # Show graph structure
    test_graph_visualization()
    
    print("\n" + "=" * 70)
    print("Tests Complete!")
    print("=" * 70)
