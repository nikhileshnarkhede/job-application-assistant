"""
Test script for Experience Selector Subgraph

Uses REAL data:
1. structured_jd from JD Extractor (Amazon Applied Scientist)
2. Candidate experiences from candidate_loader

Run: python -m subgraphs.experience_selector.test
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
    Test experience selection using:
    - structured_jd from JD Extractor (REAL Amazon JD)
    - Candidate experiences from candidate_loader
    """
    from subgraphs.jd_extractor import extract_jd_from_url, extract_jd_from_text
    from subgraphs.experience_selector import select_experiences_for_jd
    
    print("=" * 60)
    print("Test: End-to-End Experience Selection with Real JD")
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
    print(f"   Responsibilities: {len(structured_jd.responsibilities)}")
    
    # ===== STEP 2: Select Experiences =====
    print("\n🔍 Step 2: Selecting Experiences...")
    
    result = select_experiences_for_jd(
        structured_jd=structured_jd,
        max_experiences=4
    )
    
    if result["error"]:
        print(f"❌ Selection Error: {result['error']}")
        return None
    
    # ===== STEP 3: Display Results =====
    print(f"\n✅ Selection complete!")
    print(f"   Total experiences evaluated: {result['all_experiences_count']}")
    
    print(f"\n" + "=" * 60)
    print("📊 SELECTED EXPERIENCES")
    print("=" * 60)
    
    for idx, exp in enumerate(result["selected_experiences"], 1):
        print(f"\n{'─' * 50}")
        print(f"#{idx} {exp.role}")
        print(f"{'─' * 50}")
        print(f"🏢 Company: {exp.company}")
        print(f"📈 Relevance Score: {exp.relevance_score:.1f}/100")
        
        if exp.dates:
            dates_str = f"{exp.dates.get('start', '')} - {exp.dates.get('end', '')}"
            if exp.dates.get('duration'):
                dates_str += f" ({exp.dates['duration']})"
            print(f"📅 Dates: {dates_str}")
        
        if exp.matching_keywords:
            print(f"✅ Matching Keywords: {', '.join(exp.matching_keywords[:8])}")
        
        # Show top bullets
        print(f"\n📋 Top Bullets (sorted by relevance):")
        for bullet in exp.original_bullets[:4]:
            # Truncate long bullets
            if len(bullet) > 100:
                bullet = bullet[:97] + "..."
            print(f"   • {bullet}")
        
        if len(exp.original_bullets) > 4:
            print(f"   ... and {len(exp.original_bullets) - 4} more bullets")
    
    return result


def test_quick_selection():
    """Test quick selection without full JD extraction."""
    from subgraphs.experience_selector import quick_experience_selection
    
    print("\n" + "=" * 60)
    print("Test: Quick Selection (Direct Skills)")
    print("=" * 60)
    
    result = quick_experience_selection(
        jd_skills=["Python", "PyTorch", "TensorFlow", "Machine Learning", "Deep Learning"],
        jd_keywords=["neural networks", "model training", "data pipelines", "research"],
        role_type="ml_ai",
        max_experiences=3
    )
    
    if result["error"]:
        print(f"❌ Error: {result['error']}")
        return None
    
    print(f"\n✅ Selected {len(result['selected_experiences'])} experiences")
    
    for exp in result["selected_experiences"]:
        print(f"\n  💼 {exp.role} @ {exp.company}")
        print(f"     Score: {exp.relevance_score:.1f}")
        print(f"     Matching: {', '.join(exp.matching_keywords[:5])}")
    
    return result


def test_graph_visualization():
    """Show graph structure."""
    print("\n" + "=" * 60)
    print("Graph Structure")
    print("=" * 60)
    
    print("""
    ┌──────────────────────────────────────────────────────────┐
    │              EXPERIENCE SELECTOR SUBGRAPH                │
    ├──────────────────────────────────────────────────────────┤
    │                                                          │
    │   START                                                  │
    │     │                                                    │
    │     ▼                                                    │
    │   ┌─────────────────────────┐                           │
    │   │    load_experiences     │  ← From candidate_loader  │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │   ┌─────────────────────────┐                           │
    │   │ extract_jd_requirements │  ← Skills & keywords      │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │   ┌─────────────────────────┐                           │
    │   │   score_experiences     │  ← Weighted scoring       │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │   ┌─────────────────────────┐                           │
    │   │ select_top_experiences  │  ← Pick top N             │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │   ┌─────────────────────────┐                           │
    │   │  prepare_for_rewriting  │  ← Sort bullets, finalize │
    │   └────────────┬────────────┘                           │
    │                │                                         │
    │                ▼                                         │
    │              END                                         │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
    
    Scoring Weights:
    ┌───────────────────────┬────────┐
    │ Skill Match           │  30%   │
    │ Keyword Match         │  25%   │
    │ Responsibility Match  │  20%   │
    │ Relevance Tier        │  15%   │
    │ Recency Bonus         │  10%   │
    └───────────────────────┴────────┘
    
    Data Flow:
    ┌─────────────┐     ┌───────────────────┐     ┌─────────────────┐
    │ JD Extractor│ ──► │ Experience        │ ──► │ Selected        │
    │ (structured │     │ Selector          │     │ Experiences     │
    │   _jd)      │     │                   │     │                 │
    └─────────────┘     │                   │     │ - role          │
                        │                   │     │ - company       │
    ┌─────────────┐     │                   │     │ - score         │
    │ Candidate   │ ──► │                   │     │ - bullets       │
    │ Loader      │     │                   │     │ - keywords      │
    │ (experiences)     └───────────────────┘     └─────────────────┘
    └─────────────┘
    """)


if __name__ == "__main__":
    print("\n🧪 Experience Selector Subgraph Tests\n")
    print(f"📌 Standard Test JD: Amazon Applied Scientist")
    print(f"   {STANDARD_JD_URL}\n")
    
    # Test 1: Full end-to-end with real JD
    result = test_end_to_end_with_real_jd()
    
    # Test 2: Quick selection
    test_quick_selection()
    
    # Show graph structure
    test_graph_visualization()
    
    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)
