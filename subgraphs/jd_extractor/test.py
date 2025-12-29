"""
Test script for JD Extractor Subgraph

Uses STANDARD test JD:
- URL: Amazon Applied Scientist role
- Fallback: Sample text

Run: python -m subgraphs.jd_extractor.test
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


def test_url_extraction():
    """Test JD extraction from real Amazon URL."""
    from subgraphs.jd_extractor import extract_jd_from_url
    
    print("=" * 60)
    print("Test 1: JD Extraction from URL")
    print("=" * 60)
    print(f"\n🔗 URL: {STANDARD_JD_URL}")
    
    result = extract_jd_from_url(STANDARD_JD_URL)
    
    if result["error"]:
        print(f"\n⚠️ URL extraction failed: {result['error']}")
        print("   (This may happen if the URL requires authentication)")
        return None
    
    jd = result["structured_jd"]
    
    print(f"\n✅ Extraction successful!")
    print(f"\n📋 Extracted Information:")
    print(f"   Company: {jd.company_name}")
    print(f"   Role: {jd.role_title}")
    print(f"   Role Type: {jd.role_type}")
    print(f"   Location: {jd.location}")
    print(f"   Employment Type: {jd.employment_type}")
    print(f"   Experience: {jd.experience_required}")
    print(f"   Salary: {jd.salary_range}")
    
    print(f"\n🔧 Required Skills ({len(jd.skills_required)}):")
    for skill in jd.skills_required[:8]:
        print(f"   - {skill}")
    if len(jd.skills_required) > 8:
        print(f"   ... and {len(jd.skills_required) - 8} more")
    
    print(f"\n⭐ Preferred Skills ({len(jd.skills_preferred)}):")
    for skill in jd.skills_preferred[:5]:
        print(f"   - {skill}")
    if len(jd.skills_preferred) > 5:
        print(f"   ... and {len(jd.skills_preferred) - 5} more")
    
    print(f"\n🔑 Keywords for ATS ({len(jd.keywords)}):")
    print(f"   {', '.join(jd.keywords[:12])}")
    if len(jd.keywords) > 12:
        print(f"   ... and {len(jd.keywords) - 12} more")
    
    print(f"\n📝 Responsibilities ({len(jd.responsibilities)}):")
    for resp in jd.responsibilities[:3]:
        print(f"   - {resp[:80]}...")
    
    print(f"\n📊 Extraction Confidence: {jd.extraction_confidence:.2%}")
    print(f"   Validation Passed: {result['validation_passed']}")
    
    return result


def test_text_extraction():
    """Test JD extraction from text (fallback)."""
    from subgraphs.jd_extractor import extract_jd_from_text
    
    print("\n" + "=" * 60)
    print("Test 2: JD Extraction from TEXT (Fallback)")
    print("=" * 60)
    
    result = extract_jd_from_text(STANDARD_JD_TEXT)
    
    if result["error"]:
        print(f"\n❌ Error: {result['error']}")
        return None
    
    jd = result["structured_jd"]
    
    print(f"\n✅ Extraction successful!")
    print(f"\n📋 Extracted Information:")
    print(f"   Company: {jd.company_name}")
    print(f"   Role: {jd.role_title}")
    print(f"   Role Type: {jd.role_type}")
    print(f"   Location: {jd.location}")
    
    print(f"\n🔧 Required Skills ({len(jd.skills_required)}):")
    for skill in jd.skills_required[:5]:
        print(f"   - {skill}")
    
    print(f"\n🔑 Keywords ({len(jd.keywords)}):")
    print(f"   {', '.join(jd.keywords[:10])}")
    
    print(f"\n📊 Extraction Confidence: {jd.extraction_confidence:.2%}")
    
    return result


def test_graph_visualization():
    """Test graph visualization."""
    print("\n" + "=" * 60)
    print("Graph Structure")
    print("=" * 60)
    
    print("""
    ┌──────────────────────────────────────────────────────────┐
    │                  JD EXTRACTOR SUBGRAPH                   │
    ├──────────────────────────────────────────────────────────┤
    │                                                          │
    │   START                                                  │
    │     │                                                    │
    │     ▼                                                    │
    │   ┌─────────────────┐                                   │
    │   │  input_router   │  ← Detect text vs URL             │
    │   └────────┬────────┘                                   │
    │            │                                             │
    │     ┌──────┴──────┐                                     │
    │     │             │                                      │
    │     ▼             ▼                                      │
    │  [url]         [text]                                    │
    │     │             │                                      │
    │     ▼             │                                      │
    │   ┌─────────────┐ │                                     │
    │   │ url_fetcher │ │  ← Fetch HTML, parse content        │
    │   └──────┬──────┘ │                                     │
    │          │        │                                      │
    │          ▼        │                                      │
    │   ┌──────┴────────┴───┐                                 │
    │   │    jd_extractor   │◄────────┐  ← LLM extraction     │
    │   └─────────┬─────────┘         │ (retry)               │
    │             │                   │                        │
    │             ▼                   │                        │
    │   ┌───────────────────┐         │                       │
    │   │  validation_node  │─────────┘  ← Validate output    │
    │   └─────────┬─────────┘                                 │
    │             │                                            │
    │     ┌───────┴───────┐                                   │
    │     │               │                                    │
    │     ▼               ▼                                    │
    │   [pass]         [fail]                                  │
    │     │               │                                    │
    │     │               ▼                                    │
    │     │      ┌─────────────────┐                          │
    │     │      │  error_handler  │                          │
    │     │      └────────┬────────┘                          │
    │     │               │                                    │
    │     ▼               ▼                                    │
    │   ┌─────────────────────┐                               │
    │   │         END         │                               │
    │   └─────────────────────┘                               │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
    
    Output: StructuredJD
    ├── company_name, role_title, role_type
    ├── location, employment_type, experience_required
    ├── skills_required[], skills_preferred[]
    ├── responsibilities[], qualifications[]
    ├── keywords[]  ← Critical for ATS
    └── extraction_confidence
    """)


if __name__ == "__main__":
    print("\n🧪 JD Extractor Subgraph Tests\n")
    print(f"📌 Standard Test JD: Amazon Applied Scientist")
    print(f"   {STANDARD_JD_URL}\n")
    
    # Test 1: URL extraction (primary)
    url_result = test_url_extraction()
    
    # Test 2: Text extraction (fallback)
    text_result = test_text_extraction()
    
    # Show graph structure
    test_graph_visualization()
    
    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)
