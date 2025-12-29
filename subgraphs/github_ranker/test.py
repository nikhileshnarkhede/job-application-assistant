"""
Test script for GitHub Ranker Subgraph

Uses REAL data:
1. structured_jd from JD Extractor (Amazon Applied Scientist)
2. GitHub projects from cache/API

Run: python -m subgraphs.github_ranker.test
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


def test_end_to_end_with_real_jd():
    """
    Test GitHub ranking using:
    - structured_jd from JD Extractor (REAL Amazon JD)
    - GitHub projects from cache/API
    """
    from subgraphs.jd_extractor import extract_jd_from_url, extract_jd_from_text
    from subgraphs.github_ranker import rank_github_projects
    
    print("=" * 60)
    print("Test: End-to-End GitHub Ranking with Real JD")
    print("=" * 60)
    print(f"\n🔗 JD URL: {STANDARD_JD_URL}")
    
    # ===== STEP 1: Extract JD =====
    print("\n📄 Step 1: Extracting JD...")
    
    jd_result = extract_jd_from_url(STANDARD_JD_URL)
    
    if jd_result["error"]:
        print(f"  ⚠️ URL failed, using fallback text...")
        jd_result = extract_jd_from_text(STANDARD_JD_TEXT)
    
    if jd_result["error"]:
        print(f"❌ JD Extraction Error: {jd_result['error']}")
        return None
    
    structured_jd = jd_result["structured_jd"]
    print(f"✅ JD: {structured_jd.company_name} - {structured_jd.role_title}")
    print(f"   Role Type: {structured_jd.role_type}")
    print(f"   Skills: {len(structured_jd.skills_required)} required, {len(structured_jd.skills_preferred)} preferred")
    
    # ===== STEP 2: Rank GitHub Projects =====
    print("\n🔍 Step 2: Ranking GitHub Projects...")
    
    result = rank_github_projects(
        structured_jd=structured_jd,
        max_projects=3
    )
    
    if result["error"]:
        print(f"❌ Ranking Error: {result['error']}")
        return None
    
    # ===== STEP 3: Display Results =====
    print(f"\n✅ Ranking complete!")
    print(f"   Source: {result['projects_source']}")
    print(f"   Total projects evaluated: {result['all_projects_count']}")
    
    print(f"\n" + "=" * 60)
    print("📊 SELECTED PROJECTS")
    print("=" * 60)
    
    for idx, project in enumerate(result["selected_projects"], 1):
        print(f"\n{'─' * 50}")
        print(f"#{idx} {project.name}")
        print(f"{'─' * 50}")
        print(f"📈 Relevance Score: {project.relevance_score:.1f}/100")
        print(f"🔗 URL: {project.github_url}")
        print(f"📝 Description: {project.description[:100]}...")
        
        # Tech stack
        tech_list = []
        for ts in project.tech_stack.values():
            if isinstance(ts, list):
                tech_list.extend(ts[:3])
        if tech_list:
            print(f"🔧 Tech: {', '.join(tech_list[:6])}")
        
        # Matching skills
        if project.matching_skills:
            print(f"✅ Matching Skills: {', '.join(project.matching_skills[:5])}")
        
        # Bullets
        if project.bullets:
            print(f"\n📋 Resume Bullets:")
            for bullet in project.bullets:
                print(f"   • {bullet}")
    
    return result


def test_quick_ranking():
    """Test quick ranking without full JD extraction."""
    from subgraphs.github_ranker import get_top_projects_for_jd
    
    print("\n" + "=" * 60)
    print("Test: Quick Ranking (Direct Skills)")
    print("=" * 60)
    
    result = get_top_projects_for_jd(
        jd_skills=["Python", "PyTorch", "TensorFlow", "Machine Learning", "NLP"],
        jd_keywords=["deep learning", "neural networks", "transformers", "llm"],
        role_type="ml_ai",
        max_projects=2
    )
    
    if result["error"]:
        print(f"❌ Error: {result['error']}")
        return None
    
    print(f"\n✅ Found {len(result['selected_projects'])} projects")
    
    for project in result["selected_projects"]:
        print(f"\n  📁 {project.name}")
        print(f"     Score: {project.relevance_score:.1f}")
        if project.bullets:
            print(f"     Bullet: {project.bullets[0][:60]}...")
    
    return result


def test_graph_visualization():
    """Show graph structure."""
    print("\n" + "=" * 60)
    print("Graph Structure")
    print("=" * 60)
    
    print("""
    ┌──────────────────────────────────────────────────────────┐
    │                 GITHUB RANKER SUBGRAPH                   │
    ├──────────────────────────────────────────────────────────┤
    │                                                          │
    │   START                                                  │
    │     │                                                    │
    │     ▼                                                    │
    │   ┌─────────────────────────┐                           │
    │   │     load_projects       │  ← From cache/JSON/API    │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │   ┌─────────────────────────┐                           │
    │   │ extract_jd_requirements │  ← Skills & keywords      │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │   ┌─────────────────────────┐                           │
    │   │     score_projects      │  ← Weighted scoring       │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │   ┌─────────────────────────┐                           │
    │   │   select_top_projects   │  ← Pick top N             │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │   ┌─────────────────────────┐                           │
    │   │    generate_bullets     │  ← LLM bullet generation  │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │              END                                         │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
    
    Scoring Weights:
    ┌─────────────────────┬────────┐
    │ Tech Stack Overlap  │  35%   │
    │ Keyword Match       │  25%   │
    │ Role Type Relevance │  20%   │
    │ Quality/Metrics     │  20%   │
    └─────────────────────┴────────┘
    
    Data Flow:
    ┌─────────────┐     ┌─────────────────┐     ┌───────────────┐
    │ JD Extractor│ ──► │  GitHub Ranker  │ ──► │ Selected      │
    │ (structured │     │                 │     │ Projects      │
    │   _jd)      │     │                 │     │               │
    └─────────────┘     │                 │     │ - name        │
                        │                 │     │ - score       │
    ┌─────────────┐     │                 │     │ - bullets     │
    │ GitHub      │ ──► │                 │     │ - tech_stack  │
    │ Projects    │     │                 │     └───────────────┘
    │ (cache/API) │     └─────────────────┘
    └─────────────┘
    """)


if __name__ == "__main__":
    print("\n🧪 GitHub Ranker Subgraph Tests\n")
    print(f"📌 Standard Test JD: Amazon Applied Scientist")
    print(f"   {STANDARD_JD_URL}\n")
    
    # Test 1: Full end-to-end with real JD
    result = test_end_to_end_with_real_jd()
    
    # Test 2: Quick ranking
    test_quick_ranking()
    
    # Show graph structure
    test_graph_visualization()
    
    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)
