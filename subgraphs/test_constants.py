"""
Shared Test Constants for All Subgraph Tests

This file contains standard test data used across all subgraph tests.
Using consistent test data ensures reproducible results and easier debugging.
"""

# ============================================================================
# STANDARD TEST JD URL
# ============================================================================
# Amazon Applied Scientist - AI/ML, Decision Intelligence Team
# Use this URL for all subgraph tests that need a real JD

STANDARD_JD_URL = "https://www.amazon.jobs/en/jobs/3148920/applied-scientist-ai-ml-decision-intelligence-team"

# ============================================================================
# FALLBACK SAMPLE JD (if URL fails)
# ============================================================================
# Based on the Amazon Applied Scientist role

STANDARD_JD_TEXT = """
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

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_standard_jd_url() -> str:
    """Get the standard test JD URL."""
    return STANDARD_JD_URL


def get_standard_jd_text() -> str:
    """Get the standard test JD text (fallback)."""
    return STANDARD_JD_TEXT


def get_structured_jd_for_testing():
    """
    Get a structured JD for testing.
    Tries URL first, falls back to text.
    
    Returns:
        Tuple of (structured_jd, source) where source is "url" or "text"
    """
    from subgraphs.jd_extractor import extract_jd_from_url, extract_jd_from_text
    
    # Try URL first
    result = extract_jd_from_url(STANDARD_JD_URL)
    if not result["error"] and result["structured_jd"]:
        return result["structured_jd"], "url"
    
    # Fallback to text
    result = extract_jd_from_text(STANDARD_JD_TEXT)
    if not result["error"] and result["structured_jd"]:
        return result["structured_jd"], "text"
    
    raise RuntimeError("Could not extract JD from URL or text")


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "STANDARD_JD_URL",
    "STANDARD_JD_TEXT",
    "get_standard_jd_url",
    "get_standard_jd_text",
    "get_structured_jd_for_testing"
]
