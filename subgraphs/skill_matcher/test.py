"""
Test script for Skill Matcher Subgraph

Uses REAL data:
1. structured_jd from JD Extractor (using real Amazon JD URL)
2. candidate_skills_flat from candidate_loader

Run: python -m subgraphs.skill_matcher.test
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables
load_dotenv()

# ============================================================================
# STANDARD TEST JD - Use this for all subgraph tests
# ============================================================================
AMAZON_JD_URL = "https://www.amazon.jobs/en/jobs/3148920/applied-scientist-ai-ml-decision-intelligence-team"


def test_end_to_end_with_real_jd():
    """
    Test skill matching using:
    - structured_jd from JD Extractor (REAL Amazon JD)
    - candidate_skills_flat from candidate_loader
    """
    from subgraphs.jd_extractor import extract_jd_from_url
    from subgraphs.skill_matcher import match_skills_to_jd
    from mcp_server.tools.candidate_loader import (
        get_all_candidate_skills,
        get_all_candidate_keywords
    )
    
    print("=" * 60)
    print("Test: End-to-End with REAL Amazon JD")
    print("=" * 60)
    print(f"\n🔗 URL: {AMAZON_JD_URL}")
    
    # ===== STEP 1: Extract JD using JD Extractor =====
    print("\n📄 Step 1: Extracting JD from URL...")
    
    jd_result = extract_jd_from_url(AMAZON_JD_URL)
    
    if jd_result["error"]:
        print(f"❌ JD Extraction Error: {jd_result['error']}")
        print("\n⚠️ Falling back to cached/sample JD...")
        return test_with_sample_jd()
    
    structured_jd = jd_result["structured_jd"]
    print(f"✅ JD Extracted: {structured_jd.company_name} - {structured_jd.role_title}")
    print(f"   Role Type: {structured_jd.role_type}")
    print(f"   Location: {structured_jd.location}")
    print(f"   Required Skills: {len(structured_jd.skills_required)}")
    print(f"   Preferred Skills: {len(structured_jd.skills_preferred)}")
    print(f"   Keywords: {len(structured_jd.keywords)}")
    
    # Show extracted skills
    print(f"\n   📋 Required Skills:")
    for skill in structured_jd.skills_required[:10]:
        print(f"      - {skill}")
    if len(structured_jd.skills_required) > 10:
        print(f"      ... and {len(structured_jd.skills_required) - 10} more")
    
    # ===== STEP 2: Load Candidate Skills =====
    print("\n👤 Step 2: Loading Candidate Skills...")
    
    candidate_skills = get_all_candidate_skills()
    candidate_keywords = get_all_candidate_keywords()
    
    print(f"✅ Loaded {len(candidate_skills)} skills and {len(candidate_keywords)} keywords")
    print(f"   Sample skills: {candidate_skills[:5]}...")
    
    # ===== STEP 3: Run Skill Matcher =====
    print("\n🔍 Step 3: Running Skill Matcher...")
    
    result = match_skills_to_jd(
        structured_jd=structured_jd,
        candidate_skills=candidate_skills,
        candidate_keywords=candidate_keywords
    )
    
    if result["error"]:
        print(f"❌ Matching Error: {result['error']}")
        return None
    
    # ===== STEP 4: Display Results =====
    match = result["skill_match_result"]
    
    print(f"\n" + "=" * 60)
    print("📊 SKILL MATCH RESULTS")
    print("=" * 60)
    
    print(f"\n🎯 Match Percentage: {match.match_percentage:.1f}%")
    
    print(f"\n✅ Matched Skills ({len(match.matched_skills)}):")
    for skill in match.matched_skills:
        print(f"   ✓ {skill}")
    
    print(f"\n❌ Missing Skills ({len(match.missing_skills)}):")
    for skill in match.missing_skills:
        print(f"   ✗ {skill}")
    
    if match.critical_missing:
        print(f"\n🚨 Critical Missing Skills:")
        for skill in match.critical_missing:
            print(f"   ⚠️ {skill}")
    
    if match.partial_matches:
        print(f"\n🔄 Partial Matches ({len(match.partial_matches)}):")
        for pm in match.partial_matches:
            print(f"   ≈ {pm}")
    
    print(f"\n➕ Additional Candidate Skills ({len(match.additional_skills)}):")
    for skill in match.additional_skills[:8]:
        print(f"   + {skill}")
    if len(match.additional_skills) > 8:
        print(f"   ... and {len(match.additional_skills) - 8} more")
    
    if match.skill_gap_analysis:
        print(f"\n📝 Gap Analysis:")
        print(f"   {match.skill_gap_analysis}")
    
    return result


def test_with_sample_jd():
    """
    Fallback test using sample JD text (in case URL fails).
    Based on Amazon Applied Scientist role.
    """
    from subgraphs.jd_extractor import extract_jd_from_text
    from subgraphs.skill_matcher import match_skills_to_jd
    from mcp_server.tools.candidate_loader import (
        get_all_candidate_skills,
        get_all_candidate_keywords
    )
    
    print("\n" + "=" * 60)
    print("Test: Fallback with Sample JD (Amazon-style)")
    print("=" * 60)
    
    # Sample JD based on Amazon Applied Scientist role
    sample_jd = """
    Applied Scientist - AI/ML, Decision Intelligence Team
    Amazon - Seattle, WA (On-site)
    
    About Amazon:
    Amazon is guided by four principles: customer obsession, passion for invention, 
    commitment to operational excellence, and long-term thinking.
    
    About the Role:
    We are looking for an Applied Scientist to join our Decision Intelligence team. 
    You will work on building ML models that power critical business decisions across Amazon.
    
    Responsibilities:
    - Design and implement machine learning models for decision optimization
    - Develop scalable ML pipelines for training and inference
    - Collaborate with engineers to deploy models to production
    - Conduct A/B experiments to measure model impact
    - Write technical documents and present findings to stakeholders
    - Mentor junior scientists and engineers
    
    Basic Qualifications:
    - PhD or Master's degree in Computer Science, Machine Learning, Statistics, or related field
    - 3+ years of experience in applied machine learning
    - Strong programming skills in Python
    - Experience with deep learning frameworks (PyTorch, TensorFlow)
    - Experience with large-scale data processing (Spark, SQL)
    - Track record of delivering ML models to production
    
    Preferred Qualifications:
    - Experience with reinforcement learning or optimization
    - Experience with NLP or computer vision
    - Publications in top ML conferences (NeurIPS, ICML, ICLR)
    - Experience with AWS services (SageMaker, EMR)
    - Experience with causal inference
    
    Benefits:
    - Competitive salary
    - Stock options (RSUs)
    - Health, dental, vision insurance
    - 401(k) matching
    """
    
    print("\n📄 Extracting sample JD...")
    jd_result = extract_jd_from_text(sample_jd)
    
    if jd_result["error"]:
        print(f"❌ JD Extraction Error: {jd_result['error']}")
        return None
    
    structured_jd = jd_result["structured_jd"]
    print(f"✅ JD: {structured_jd.company_name} - {structured_jd.role_title}")
    print(f"   Role Type: {structured_jd.role_type}")
    
    # Load candidate skills
    candidate_skills = get_all_candidate_skills()
    candidate_keywords = get_all_candidate_keywords()
    
    # Match
    print("\n🔍 Running Skill Matcher...")
    result = match_skills_to_jd(
        structured_jd=structured_jd,
        candidate_skills=candidate_skills,
        candidate_keywords=candidate_keywords
    )
    
    if result["error"]:
        print(f"❌ Matching Error: {result['error']}")
        return None
    
    match = result["skill_match_result"]
    
    print(f"\n🎯 Match Percentage: {match.match_percentage:.1f}%")
    
    print(f"\n✅ Matched Skills ({len(match.matched_skills)}):")
    for skill in match.matched_skills:
        print(f"   ✓ {skill}")
    
    print(f"\n❌ Missing Skills ({len(match.missing_skills)}):")
    for skill in match.missing_skills:
        print(f"   ✗ {skill}")
    
    if match.skill_gap_analysis:
        print(f"\n📝 Gap Analysis:")
        print(f"   {match.skill_gap_analysis}")
    
    return result


def test_graph_visualization():
    """Show graph structure."""
    print("\n" + "=" * 60)
    print("Graph Structure")
    print("=" * 60)
    
    print("""
    ┌──────────────────────────────────────────────────────────┐
    │                 SKILL MATCHER SUBGRAPH                   │
    ├──────────────────────────────────────────────────────────┤
    │                                                          │
    │   START                                                  │
    │     │                                                    │
    │     ▼                                                    │
    │   ┌─────────────────────────┐                           │
    │   │  load_candidate_skills  │  ← From candidate_loader  │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │   ┌─────────────────────────┐                           │
    │   │    extract_jd_skills    │  ← From structured_jd     │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │   ┌─────────────────────────┐                           │
    │   │      match_skills       │  ← Matching algorithm     │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │   ┌─────────────────────────┐                           │
    │   │      analyze_gaps       │  ← LLM gap analysis       │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │   ┌─────────────────────────┐                           │
    │   │      build_result       │  ← SkillMatchResult       │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │              END                                         │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
    
    Data Flow:
    ┌─────────────┐     ┌─────────────────┐     ┌───────────────┐
    │ JD Extractor│ ──► │  Skill Matcher  │ ──► │ SkillMatch    │
    │ (Amazon URL)│     │                 │     │ Result        │
    └─────────────┘     │                 │     │               │
                        │                 │     │ - matched     │
    ┌─────────────┐     │                 │     │ - missing     │
    │ Candidate   │ ──► │                 │     │ - percentage  │
    │ Loader      │     │                 │     │ - gap_analysis│
    │ (skills)    │     └─────────────────┘     └───────────────┘
    └─────────────┘
    """)


if __name__ == "__main__":
    print("\n🧪 Skill Matcher Subgraph Tests\n")
    print(f"📌 Standard Test JD: Amazon Applied Scientist")
    print(f"   {AMAZON_JD_URL}\n")
    
    # Test with real Amazon JD URL
    result = test_end_to_end_with_real_jd()
    
    # Show graph structure
    test_graph_visualization()
    
    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)
