"""
Test script for ATS Optimizer Subgraph

Uses REAL data from previous subgraphs:
1. structured_jd from JD Extractor
2. resume_json from Resume Builder (via full pipeline)

Run: python -m subgraphs.ats_optimizer.test
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables
load_dotenv()

# Import standard test constants
from subgraphs.test_constants import STANDARD_JD_URL, STANDARD_JD_TEXT

# Output directory for JSON files
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def save_resume_json(resume_json, filename_prefix="optimized_resume"):
    """
    Save the optimized resume JSON to a file.
    
    Args:
        resume_json: ResumeJSON object
        filename_prefix: Prefix for the output filename
    
    Returns:
        Path to the saved file
    """
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Convert ResumeJSON to dict
    if hasattr(resume_json, 'model_dump'):
        resume_dict = resume_json.model_dump()
    elif hasattr(resume_json, 'dict'):
        resume_dict = resume_json.dict()
    else:
        resume_dict = dict(resume_json)
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(resume_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved resume JSON to: {filepath}")
    return filepath


def test_full_pipeline():
    """
    Test ATS optimization using full pipeline.
    Saves the optimized resume JSON to output directory.
    """
    from subgraphs.jd_extractor import extract_jd_from_url, extract_jd_from_text
    from subgraphs.skill_matcher import match_skills_to_jd
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.github_ranker import rank_github_projects
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume
    from subgraphs.ats_optimizer import optimize_resume_for_ats, get_ats_report
    
    print("=" * 70)
    print("Test: Full Pipeline - ATS Optimizer")
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
    print(f"   Required skills: {len(structured_jd.skills_required)}")
    print(f"   Preferred skills: {len(structured_jd.skills_preferred)}")
    print(f"   Keywords: {len(structured_jd.keywords)}")
    
    # ===== STEP 2: Match Skills =====
    print("\n" + "─" * 50)
    print("🎯 Step 2: Matching Skills...")
    print("─" * 50)
    
    skill_result = match_skills_to_jd(structured_jd)
    skill_match_result = skill_result.get("skill_match_result")
    
    if skill_match_result:
        print(f"✅ Skill Match: {skill_match_result.match_percentage:.1f}%")
    
    # ===== STEP 3: Select & Rewrite Experiences =====
    print("\n" + "─" * 50)
    print("👔 Step 3: Selecting & Rewriting Experiences...")
    print("─" * 50)
    
    exp_result = select_experiences_for_jd(structured_jd, max_experiences=4)
    proj_result = rank_github_projects(structured_jd, max_projects=2)
    
    rewrite_result = rewrite_for_jd(
        structured_jd=structured_jd,
        selected_experiences=exp_result["selected_experiences"],
        selected_projects=proj_result.get("selected_projects", [])
    )
    
    print(f"✅ Rewritten: {len(rewrite_result['rewritten_experiences'])} experiences")
    print(f"   Keyword incorporation: {rewrite_result['incorporation_rate']:.1f}%")
    
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
    print(f"✅ Resume built: {len(resume_json.experience)} experiences, {len(resume_json.projects)} projects")
    
    # Save BEFORE optimization
    save_resume_json(resume_json, "resume_before_ats")
    
    # ===== STEP 5: ATS Optimization =====
    print("\n" + "─" * 50)
    print("🎯 Step 5: ATS Optimization...")
    print("─" * 50)
    
    result = optimize_resume_for_ats(
        structured_jd=structured_jd,
        resume_json=resume_json,
        target_score=95,
        max_iterations=10
    )
    
    if result["error"]:
        print(f"❌ ATS Error: {result['error']}")
        return None
    
    # ===== SAVE OPTIMIZED RESUME =====
    optimized_resume = result.get("optimized_resume")
    if optimized_resume:
        save_resume_json(optimized_resume, "resume_after_ats")
    
    # ===== DISPLAY RESULTS =====
    print(f"\n" + "=" * 70)
    print("📊 ATS OPTIMIZATION RESULTS")
    print("=" * 70)
    
    ats = result["ats_analysis"]
    
    print(f"\n🎯 ATS Score: {ats.score}/100")
    print(f"   Status: {'✅ PASSED' if ats.passed else '⚠️ Below target (95)'}")
    print(f"   Iterations: {result['iterations']}")
    
    print(f"\n📈 Keyword Analysis:")
    print(f"   Density: {ats.keyword_density*100:.1f}%")
    print(f"   Found: {len(ats.keywords_found)}")
    print(f"   Missing: {len(ats.keywords_missing)}")
    
    print(f"\n✅ Keywords Found ({len(ats.keywords_found)}):")
    found_display = ", ".join(ats.keywords_found[:15])
    print(f"   {found_display}")
    if len(ats.keywords_found) > 15:
        print(f"   ... +{len(ats.keywords_found) - 15} more")
    
    if ats.keywords_missing:
        print(f"\n❌ Keywords Missing ({len(ats.keywords_missing)}):")
        missing_display = ", ".join(ats.keywords_missing[:10])
        print(f"   {missing_display}")
    
    if ats.format_issues:
        print(f"\n⚠️ Format Issues ({len(ats.format_issues)}):")
        for issue in ats.format_issues[:5]:
            print(f"   • {issue[:70]}")
    
    if ats.section_scores:
        print(f"\n📋 Section Scores:")
        for section, score in ats.section_scores.items():
            bar = "█" * (score // 10) + "░" * (10 - score // 10)
            print(f"   {section:15} [{bar}] {score}/100")
    
    # Print formatted report
    print(f"\n" + "─" * 70)
    print("FORMATTED ATS REPORT")
    print("─" * 70)
    print(get_ats_report(ats))
    
    # ===== SHOW OUTPUT LOCATION =====
    print(f"\n" + "=" * 70)
    print("📁 OUTPUT FILES")
    print("=" * 70)
    print(f"\nJSON files saved to: {OUTPUT_DIR}")
    if os.path.exists(OUTPUT_DIR):
        files = sorted(os.listdir(OUTPUT_DIR))
        for f in files[-4:]:  # Show last 4 files
            filepath = os.path.join(OUTPUT_DIR, f)
            size = os.path.getsize(filepath)
            print(f"   📄 {f} ({size:,} bytes)")
    
    return result


def test_quick_ats_check():
    """Test quick ATS check without full optimization."""
    from subgraphs.jd_extractor import extract_jd_from_text
    from subgraphs.experience_selector import select_experiences_for_jd
    from subgraphs.experience_rewriter import rewrite_for_jd
    from subgraphs.resume_builder import build_resume
    from subgraphs.ats_optimizer import quick_ats_check
    
    print("\n" + "=" * 70)
    print("Test: Quick ATS Check")
    print("=" * 70)
    
    # Build a quick resume
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
    result = quick_ats_check(
        resume_json=resume_result["resume_json"],
        jd_skills=["Python", "Machine Learning", "Deep Learning", "AWS", "SQL"],
        jd_keywords=["data pipeline", "model deployment", "A/B testing"]
    )
    
    print(f"\n📊 Quick ATS Score: {result['score']}/100")
    print(f"   Keyword Density: {result['keyword_density']*100:.1f}%")
    print(f"   Found: {len(result['keywords_found'])}")
    print(f"   Missing: {len(result['keywords_missing'])}")
    
    return result


def test_graph_visualization():
    """Show graph structure."""
    print("\n" + "=" * 70)
    print("Graph Structure")
    print("=" * 70)
    
    print("""
    ┌──────────────────────────────────────────────────────────────────────┐
    │                       ATS OPTIMIZER SUBGRAPH                         │
    ├──────────────────────────────────────────────────────────────────────┤
    │                                                                      │
    │   START                                                              │
    │     │                                                                │
    │     ▼                                                                │
    │   ┌─────────────────────────┐                                       │
    │   │   extract_jd_keywords   │  ← Weight: Required=3, Preferred=2    │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │   scan_resume_content   │  ← Extract all text by section        │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │   calculate_ats_score   │  ← Match + fuzzy + aliases            │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │   check_format_issues   │  ← Action verbs, pronouns, length     │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │   ┌─────────────────────────┐                                       │
    │   │  generate_suggestions   │  ← LLM + Direct keyword injection     │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │            ◆ score >= 95?                                           │
    │           ╱            ╲                                             │
    │        YES              NO                                          │
    │          │               │                                          │
    │          │   ┌───────────▼───────────┐                              │
    │          │   │   apply_suggestions   │ ← Add to Skills/Projects     │
    │          │   └───────────┬───────────┘                              │
    │          │               │                                          │
    │          │               └──► Loop back to scan                     │
    │          │                    (max 3 iterations)                    │
    │          │                                                          │
    │          ▼                                                          │
    │   ┌─────────────────────────┐                                       │
    │   │   finalize_analysis     │  ← Create ATSAnalysis object          │
    │   └────────────┬────────────┘                                       │
    │                │                                                     │
    │                ▼                                                     │
    │              END                                                     │
    │                                                                      │
    └──────────────────────────────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    print("\n🧪 ATS Optimizer Subgraph Tests\n")
    print(f"📌 Standard Test JD: Amazon Applied Scientist")
    print(f"   {STANDARD_JD_URL}\n")
    
    # Test 1: Full pipeline
    result = test_full_pipeline()
    
    # Show graph structure
    test_graph_visualization()
    
    print("\n" + "=" * 70)
    print("Tests Complete!")
    print("=" * 70)
