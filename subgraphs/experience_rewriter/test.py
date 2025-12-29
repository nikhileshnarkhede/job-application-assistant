"""
Test script for Experience Rewriter Subgraph

Uses REAL data from previous subgraphs:
1. structured_jd from JD Extractor
2. selected_experiences from Experience Selector
3. selected_projects from GitHub Ranker

Run: python -m subgraphs.experience_rewriter.test
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables
load_dotenv()

# Import standard test constants
from subgraphs.test_constants import STANDARD_JD_URL, STANDARD_JD_TEXT


def test_full_pipeline():
    """
    Test experience rewriting using full pipeline:
    1. JD Extractor → structured_jd
    2. Experience Selector → selected_experiences
    3. GitHub Ranker → selected_projects
    4. Experience Rewriter → rewritten bullets with metrics
    """
    from subgraphs.jd_extractor import extract_jd_from_url, extract_jd_from_text
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.github_ranker import rank_github_projects
    from subgraphs.experience_rewriter import rewrite_for_jd
    
    print("=" * 70)
    print("Test: Full Pipeline - Experience Rewriter")
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
    print(f"   Skills: {len(structured_jd.skills_required)} required, {len(structured_jd.skills_preferred)} preferred")
    print(f"   Keywords: {len(structured_jd.keywords)}")
    
    # ===== STEP 2: Select Experiences =====
    print("\n" + "─" * 50)
    print("👔 Step 2: Selecting Experiences...")
    print("─" * 50)
    
    exp_result = select_experiences_for_jd(structured_jd, max_experiences=3)
    
    if exp_result["error"]:
        print(f"❌ Experience Selection Error: {exp_result['error']}")
        return None
    
    selected_experiences = exp_result["selected_experiences"]
    print(f"✅ Selected {len(selected_experiences)} experiences")
    for exp in selected_experiences:
        print(f"   • {exp.role} @ {exp.company} (score: {exp.relevance_score:.1f})")
    
    # ===== STEP 3: Rank Projects =====
    print("\n" + "─" * 50)
    print("📁 Step 3: Ranking GitHub Projects...")
    print("─" * 50)
    
    proj_result = rank_github_projects(structured_jd, max_projects=2)
    
    if proj_result["error"]:
        print(f"⚠️ Project Ranking Error: {proj_result['error']}")
        selected_projects = []
    else:
        selected_projects = proj_result["selected_projects"]
        print(f"✅ Selected {len(selected_projects)} projects")
        for proj in selected_projects:
            print(f"   • {proj.name} (score: {proj.relevance_score:.1f})")
    
    # ===== STEP 4: Rewrite Experiences =====
    print("\n" + "─" * 50)
    print("✍️ Step 4: Rewriting with Metrics & Keywords...")
    print("─" * 50)
    
    result = rewrite_for_jd(
        structured_jd=structured_jd,
        selected_experiences=selected_experiences,
        selected_projects=selected_projects
    )
    
    if result["error"]:
        print(f"❌ Rewriting Error: {result['error']}")
        return None
    
    # ===== DISPLAY RESULTS =====
    print(f"\n" + "=" * 70)
    print("📊 REWRITING RESULTS")
    print("=" * 70)
    
    print(f"\n🎯 Target Keywords (top 15):")
    print(f"   {', '.join(result['target_keywords'][:15])}")
    
    print(f"\n📈 Keyword Incorporation Rate: {result['incorporation_rate']:.1f}%")
    print(f"   Keywords Used: {', '.join(result['keywords_incorporated'][:10])}")
    
    # Show rewritten experiences
    print(f"\n" + "─" * 70)
    print("📋 REWRITTEN EXPERIENCE BULLETS")
    print("─" * 70)
    
    for exp in result["rewritten_experiences"]:
        print(f"\n🏢 {exp.role} @ {exp.company}")
        print(f"   Keywords incorporated: {', '.join(exp.keywords_incorporated[:5])}")
        
        print(f"\n   ORIGINAL → REWRITTEN:")
        for i, (orig, new) in enumerate(zip(exp.original_bullets[:4], exp.rewritten_bullets[:4])):
            print(f"\n   [{i+1}] Original:")
            print(f"       {orig[:80]}{'...' if len(orig) > 80 else ''}")
            print(f"   [{i+1}] Rewritten:")
            print(f"       {new}")
    
    # Show rewritten projects
    if result["rewritten_projects"]:
        print(f"\n" + "─" * 70)
        print("📁 REWRITTEN PROJECT BULLETS")
        print("─" * 70)
        
        for proj in result["rewritten_projects"]:
            print(f"\n🔧 {proj.name}")
            print(f"   Keywords: {', '.join(proj.keywords_incorporated[:5])}")
            
            print(f"\n   Rewritten Bullets:")
            for bullet in proj.rewritten_bullets[:3]:
                print(f"   • {bullet}")
    
    return result


def test_metrics_presence():
    """Verify that rewritten bullets contain metrics."""
    import re
    from subgraphs.jd_extractor import extract_jd_from_text
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.experience_rewriter import rewrite_for_jd
    
    print("\n" + "=" * 70)
    print("Test: Verify Metrics in Rewritten Bullets")
    print("=" * 70)
    
    # Quick extraction
    jd_result = extract_jd_from_text(STANDARD_JD_TEXT)
    structured_jd = jd_result["structured_jd"]
    
    exp_result = select_experiences_for_jd(structured_jd, max_experiences=2)
    selected_experiences = exp_result["selected_experiences"]
    
    result = rewrite_for_jd(
        structured_jd=structured_jd,
        selected_experiences=selected_experiences,
        selected_projects=[]
    )
    
    # Check for metrics
    total_bullets = 0
    bullets_with_metrics = 0
    metric_pattern = r'\d+[%xX]|\d+\.\d+|\$\d+|\d+K|\d+M|\d+\+'
    
    for exp in result["rewritten_experiences"]:
        for bullet in exp.rewritten_bullets:
            total_bullets += 1
            if re.search(metric_pattern, bullet):
                bullets_with_metrics += 1
                print(f"✅ Metric found: {bullet[:70]}...")
            else:
                print(f"⚠️ No metric: {bullet[:70]}...")
    
    metric_rate = bullets_with_metrics / total_bullets * 100 if total_bullets > 0 else 0
    
    print(f"\n📊 Metrics presence: {bullets_with_metrics}/{total_bullets} ({metric_rate:.1f}%)")
    
    if metric_rate >= 80:
        print("✅ PASS: Most bullets contain metrics")
    else:
        print("⚠️ WARNING: Some bullets missing metrics")
    
    return result


def test_graph_visualization():
    """Show graph structure."""
    print("\n" + "=" * 70)
    print("Graph Structure")
    print("=" * 70)
    
    print("""
    ┌──────────────────────────────────────────────────────────────────────┐
    │                    EXPERIENCE REWRITER SUBGRAPH                      │
    ├──────────────────────────────────────────────────────────────────────┤
    │                                                                      │
    │   START                                                              │
    │     │                                                                │
    │     ▼                                                                │
    │   ┌─────────────────────────┐                                       │
    │   │    load_resources       │  ← Load action verbs                  │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │   prepare_keywords      │  ← Prioritize JD keywords             │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │  rewrite_experiences    │  ← LLM: Add metrics + keywords        │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │   rewrite_projects      │  ← LLM: Enhance project bullets       │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │   validate_rewrites     │  ← Check metrics & keyword rate       │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │              END                                                     │
    │                                                                      │
    └──────────────────────────────────────────────────────────────────────┘
    
    Bullet Transformation:
    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    │  BEFORE: "Built machine learning models for customer segmentation" │
    │                                                                     │
    │  AFTER:  "Engineered gradient boosting models for customer         │
    │           segmentation achieving 89% accuracy, enabling targeted   │
    │           marketing campaigns that increased conversion by 34%"    │
    │                                                                     │
    │  ✓ Action verb: "Engineered"                                       │
    │  ✓ Metrics: "89% accuracy", "34% increase"                         │
    │  ✓ Keywords: "machine learning", "customer segmentation"           │
    │  ✓ Impact: "increased conversion"                                  │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    print("\n🧪 Experience Rewriter Subgraph Tests\n")
    print(f"📌 Standard Test JD: Amazon Applied Scientist")
    print(f"   {STANDARD_JD_URL}\n")
    
    # Test 1: Full pipeline
    result = test_full_pipeline()
    
    # Test 2: Verify metrics (optional - uncomment if needed)
    # test_metrics_presence()
    
    # Show graph structure
    test_graph_visualization()
    
    print("\n" + "=" * 70)
    print("Tests Complete!")
    print("=" * 70)
