"""
Test script for Resume Builder Subgraph

Uses REAL data from previous subgraphs:
1. structured_jd from JD Extractor
2. skill_match_result from Skill Matcher
3. rewritten_experiences from Experience Rewriter
4. rewritten_projects from Experience Rewriter

Run: python -m subgraphs.resume_builder.test
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables
load_dotenv()

# Import standard test constants
from subgraphs.test_constants import STANDARD_JD_URL, STANDARD_JD_TEXT


def test_full_pipeline():
    """
    Test resume building using full pipeline:
    1. JD Extractor → structured_jd
    2. Skill Matcher → skill_match_result
    3. Experience Selector → selected_experiences
    4. GitHub Ranker → selected_projects
    5. Experience Rewriter → rewritten_experiences, rewritten_projects
    6. Resume Builder → ResumeJSON
    """
    from subgraphs.jd_extractor import extract_jd_from_url, extract_jd_from_text
    from subgraphs.skill_matcher import match_skills_to_jd
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.github_ranker import rank_github_projects
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume, resume_to_dict
    
    print("=" * 70)
    print("Test: Full Pipeline - Resume Builder")
    print("=" * 70)
    print(f"\n🔗 JD URL: {STANDARD_JD_URL}")
    
    # ===== STEP 1: Extract JD =====
    print("\n" + "─" * 50)
    print("📄 Step 1: Extracting JD...")
    print("─" * 50)
    
    jd_result = extract_jd_from_url(STANDARD_JD_URL)
    
    if jd_result["error"]:
        print(f"  ⚠️ URL failed, using fallback text...")
        jd_result = extract_jd_from_text(STANDARD_JD_TEXT)
    
    if jd_result["error"]:
        print(f"❌ JD Extraction Error: {jd_result['error']}")
        return None
    
    structured_jd = jd_result["structured_jd"]
    print(f"✅ JD: {structured_jd.company_name} - {structured_jd.role_title}")
    
    # ===== STEP 2: Match Skills =====
    print("\n" + "─" * 50)
    print("🎯 Step 2: Matching Skills...")
    print("─" * 50)
    
    skill_result = match_skills_to_jd(structured_jd)
    skill_match_result = skill_result.get("skill_match_result")
    
    if skill_match_result:
        print(f"✅ Match: {skill_match_result.match_percentage:.1f}%")
        print(f"   Matched: {len(skill_match_result.matched_skills)}")
    
    # ===== STEP 3: Select Experiences =====
    print("\n" + "─" * 50)
    print("👔 Step 3: Selecting Experiences...")
    print("─" * 50)
    
    exp_result = select_experiences_for_jd(structured_jd, max_experiences=4)
    selected_experiences = exp_result["selected_experiences"]
    print(f"✅ Selected {len(selected_experiences)} experiences")
    
    # ===== STEP 4: Rank Projects =====
    print("\n" + "─" * 50)
    print("📁 Step 4: Ranking Projects...")
    print("─" * 50)
    
    proj_result = rank_github_projects(structured_jd, max_projects=3)
    selected_projects = proj_result.get("selected_projects", [])
    print(f"✅ Selected {len(selected_projects)} projects")
    
    # ===== STEP 5: Rewrite Bullets =====
    print("\n" + "─" * 50)
    print("✍️ Step 5: Rewriting Bullets...")
    print("─" * 50)
    
    rewrite_result = rewrite_for_jd(
        structured_jd=structured_jd,
        selected_experiences=selected_experiences,
        selected_projects=selected_projects
    )
    
    rewritten_experiences = rewrite_result["rewritten_experiences"]
    rewritten_projects = rewrite_result["rewritten_projects"]
    print(f"✅ Rewritten {len(rewritten_experiences)} experiences, {len(rewritten_projects)} projects")
    print(f"   Keyword incorporation: {rewrite_result['incorporation_rate']:.1f}%")
    
    # ===== STEP 6: Build Resume =====
    print("\n" + "─" * 50)
    print("📋 Step 6: Building Resume...")
    print("─" * 50)
    
    result = build_resume(
        structured_jd=structured_jd,
        rewritten_experiences=rewritten_experiences,
        rewritten_projects=rewritten_projects,
        skill_match_result=skill_match_result
    )
    
    if result["error"]:
        print(f"❌ Build Error: {result['error']}")
        return None
    
    resume = result["resume_json"]
    
    # ===== DISPLAY RESULTS =====
    print(f"\n" + "=" * 70)
    print("📊 RESUME BUILD RESULTS")
    print("=" * 70)
    
    print(f"\n📌 Tailored For: {resume.tailored_for}")
    print(f"📅 Generated: {resume.last_modified}")
    
    # Header
    print(f"\n" + "─" * 50)
    print("👤 HEADER")
    print("─" * 50)
    for key, value in resume.header.items():
        if value:
            print(f"   {key}: {value}")
    
    # Summary
    print(f"\n" + "─" * 50)
    print("📝 PROFESSIONAL SUMMARY")
    print("─" * 50)
    print(f"   {resume.summary}")
    
    # Skills
    print(f"\n" + "─" * 50)
    print("🔧 SKILLS (Optimized Order)")
    print("─" * 50)
    for category, skills in resume.skills.items():
        print(f"   {category}:")
        print(f"      {skills}")
    
    # Experience
    print(f"\n" + "─" * 50)
    print("💼 EXPERIENCE")
    print("─" * 50)
    for exp in resume.experience:
        print(f"\n   {exp['role']} @ {exp['company']}")
        print(f"   {exp['dates']} | {exp['location']}")
        for bullet in exp['bullets'][:3]:
            print(f"   • {bullet[:80]}{'...' if len(bullet) > 80 else ''}")
        if len(exp['bullets']) > 3:
            print(f"   ... +{len(exp['bullets']) - 3} more bullets")
    
    # Projects
    if resume.projects:
        print(f"\n" + "─" * 50)
        print("📁 PROJECTS")
        print("─" * 50)
        for proj in resume.projects:
            print(f"\n   {proj['name']}")
            print(f"   Tech: {proj['technologies']}")
            for bullet in proj['bullets'][:2]:
                print(f"   • {bullet[:80]}{'...' if len(bullet) > 80 else ''}")
    
    # Education
    print(f"\n" + "─" * 50)
    print("🎓 EDUCATION")
    print("─" * 50)
    for edu in resume.education:
        print(f"   {edu['degree']} - {edu['institution']}")
        print(f"   {edu['graduation']} | {edu['location']}")
    
    # Certifications
    if resume.certifications:
        print(f"\n" + "─" * 50)
        print("📜 CERTIFICATIONS")
        print("─" * 50)
        for cert in resume.certifications[:3]:
            print(f"   • {cert}")
    
    # Convert to dict and show structure
    print(f"\n" + "─" * 50)
    print("📦 RESUME STRUCTURE")
    print("─" * 50)
    resume_dict = resume_to_dict(resume)
    print(f"   Sections: {list(resume_dict.keys())}")
    print(f"   Experience entries: {len(resume_dict['experience'])}")
    print(f"   Project entries: {len(resume_dict['projects'])}")
    print(f"   Skill categories: {len(resume_dict['skills'])}")
    
    return result


def test_save_resume_json():
    """Test saving resume to JSON file."""
    from subgraphs.jd_extractor import extract_jd_from_text
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume, resume_to_dict
    
    print("\n" + "=" * 70)
    print("Test: Save Resume to JSON")
    print("=" * 70)
    
    # Quick pipeline
    jd_result = extract_jd_from_text(STANDARD_JD_TEXT)
    structured_jd = jd_result["structured_jd"]
    
    exp_result = select_experiences_for_jd(structured_jd, max_experiences=3)
    
    rewrite_result = rewrite_for_jd(
        structured_jd=structured_jd,
        selected_experiences=exp_result["selected_experiences"],
        selected_projects=[]
    )
    
    result = build_resume(
        structured_jd=structured_jd,
        rewritten_experiences=rewrite_result["rewritten_experiences"],
        rewritten_projects=[]
    )
    
    # Save to file
    resume_dict = resume_to_dict(result["resume_json"])
    output_path = "output/test_resume.json"
    
    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resume_dict, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved resume to: {output_path}")
    
    return result


def test_graph_visualization():
    """Show graph structure."""
    print("\n" + "=" * 70)
    print("Graph Structure")
    print("=" * 70)
    
    print("""
    ┌──────────────────────────────────────────────────────────────────────┐
    │                      RESUME BUILDER SUBGRAPH                         │
    ├──────────────────────────────────────────────────────────────────────┤
    │                                                                      │
    │   START                                                              │
    │     │                                                                │
    │     ▼                                                                │
    │   ┌─────────────────────────┐                                       │
    │   │   load_candidate_data   │  ← Header, education, certs, pubs     │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │     tailor_summary      │  ← LLM: JD-tailored with metrics      │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │    optimize_skills      │  ← Reorder by JD relevance            │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │   format_experiences    │  ← Apply bullet limits                │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │    format_projects      │  ← Structure for resume               │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │    assemble_resume      │  ← Combine into ResumeJSON            │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │              END                                                     │
    │                                                                      │
    └──────────────────────────────────────────────────────────────────────┘
    
    Bullet Limits:
    ┌───────────────────────┬──────────┐
    │ Most Recent (1st)     │ 5 max    │
    │ Second Experience     │ 4 max    │
    │ Third Experience      │ 3 max    │
    │ Fourth+ Experience    │ 2 max    │
    │ Projects              │ 3 max    │
    └───────────────────────┴──────────┘
    
    Data Flow:
    ┌─────────────────┐
    │  JD Extractor   │──────────────────────────────────┐
    └─────────────────┘                                  │
                                                         │
    ┌─────────────────┐                                  │
    │  Skill Matcher  │──────────────────────────────────┤
    └─────────────────┘                                  │
                                                         ▼
    ┌─────────────────┐     ┌─────────────────┐    ┌───────────────┐
    │ Exp Selector    │────►│ Exp Rewriter    │───►│ Resume        │
    └─────────────────┘     └─────────────────┘    │ Builder       │
                                                   │               │
    ┌─────────────────┐     ┌─────────────────┐    │               │
    │ GitHub Ranker   │────►│ (Proj Rewrite)  │───►│               │
    └─────────────────┘     └─────────────────┘    └───────┬───────┘
                                                           │
    ┌─────────────────┐                                    │
    │ Candidate Data  │────────────────────────────────────┘
    │ (Header, Edu,   │
    │  Certs, Skills) │
    └─────────────────┘
                                                           │
                                                           ▼
                                                   ┌───────────────┐
                                                   │  ResumeJSON   │
                                                   │  (Complete)   │
                                                   └───────────────┘
    """)


if __name__ == "__main__":
    print("\n🧪 Resume Builder Subgraph Tests\n")
    print(f"📌 Standard Test JD: Amazon Applied Scientist")
    print(f"   {STANDARD_JD_URL}\n")
    
    # Test 1: Full pipeline
    result = test_full_pipeline()
    
    # Test 2: Save to JSON (optional - uncomment if needed)
    test_save_resume_json()
    
    # Show graph structure
    test_graph_visualization()
    
    print("\n" + "=" * 70)
    print("Tests Complete!")
    print("=" * 70)
