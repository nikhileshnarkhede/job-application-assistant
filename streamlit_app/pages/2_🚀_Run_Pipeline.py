"""
Run Pipeline Page - Job Application Assistant

Main page for inputting JD and running the pipeline.
"""

import streamlit as st
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

st.set_page_config(
    page_title="Run Pipeline - Job Application Assistant",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Run Pipeline")
st.markdown("Paste job description URL or text to generate tailored application materials")

# Initialize session state
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None
if "pipeline_running" not in st.session_state:
    st.session_state.pipeline_running = False
if "pipeline_log" not in st.session_state:
    st.session_state.pipeline_log = []

# Input section
st.markdown("### 📝 Job Description Input")

input_method = st.radio(
    "Input Method",
    options=["URL", "Text"],
    horizontal=True,
    help="Choose how to provide the job description"
)

jd_url = None
jd_text = None

if input_method == "URL":
    jd_url = st.text_input(
        "Job Posting URL",
        placeholder="https://www.linkedin.com/jobs/view/... or https://amazon.jobs/...",
        help="Paste the full URL to the job posting"
    )
    
    # Quick test URL
    if st.button("📋 Use Test URL (Amazon Applied Scientist)"):
        jd_url = "https://www.amazon.jobs/en/jobs/2721089/applied-scientist-aws-applications"
        st.session_state.test_url = jd_url
        st.rerun()
    
    if "test_url" in st.session_state:
        jd_url = st.session_state.test_url
        st.info(f"Using: {jd_url}")
else:
    jd_text = st.text_area(
        "Job Description Text",
        height=300,
        placeholder="""Paste the complete job description here...

Example:
We are looking for a Machine Learning Engineer to join our team...

Requirements:
- 3+ years of experience in ML/AI
- Proficiency in Python, TensorFlow/PyTorch
- Experience with cloud platforms (AWS/GCP)
...""",
        help="Paste the complete job description text"
    )
    
    # Quick test text
    if st.button("📋 Use Test JD (ML Engineer)"):
        jd_text = """Machine Learning Engineer - Amazon Web Services

About the Role:
We are looking for a passionate Machine Learning Engineer to join our AWS AI team. 
You will design and implement scalable ML solutions that power next-generation cloud services.

Responsibilities:
- Design and implement machine learning models for production systems
- Collaborate with cross-functional teams to define ML requirements
- Optimize model performance and reduce inference latency
- Build data pipelines for model training and evaluation

Requirements:
- 3+ years of experience in Machine Learning or related field
- Strong programming skills in Python
- Experience with deep learning frameworks (TensorFlow, PyTorch)
- Familiarity with cloud platforms (AWS preferred)
- Experience with ML deployment and MLOps

Preferred Qualifications:
- PhD or Master's in Computer Science, ML, or related field
- Experience with NLP or Computer Vision
- Publications in top ML conferences
- Experience with distributed computing (Spark, Ray)

Location: Seattle, WA
Employment Type: Full-time
"""
        st.rerun()

st.markdown("---")

# Configuration summary
with st.expander("⚙️ Current Configuration", expanded=False):
    if "config" in st.session_state:
        config = st.session_state.config
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Resume**")
            st.write(f"Max Experiences: {config['resume']['max_experiences']}")
            st.write(f"Max Projects: {config['resume']['max_projects']}")
        
        with col2:
            st.markdown("**ATS**")
            st.write(f"Target Score: {config['ats']['target_score']}%")
            st.write(f"Max Iterations: {config['ats']['max_iterations']}")
        
        with col3:
            st.markdown("**Pipeline**")
            st.write(f"Email Gen: {'✅' if config['pipeline']['enable_email_generation'] else '❌'}")
            st.write(f"Excel Save: {'✅' if config['pipeline']['save_to_excel'] else '❌'}")
    else:
        st.info("Using default configuration. Go to Configure page to customize.")

# Run button
st.markdown("### 🚀 Execute Pipeline")

col1, col2 = st.columns([2, 1])

with col1:
    run_button = st.button(
        "🚀 Run Full Pipeline",
        use_container_width=True,
        type="primary",
        disabled=st.session_state.pipeline_running or (not jd_url and not jd_text)
    )

with col2:
    enable_checkpoints = st.checkbox("Enable Checkpoints", value=True)

# Progress display
if run_button and (jd_url or jd_text):
    st.session_state.pipeline_running = True
    st.session_state.pipeline_log = []
    
    # Create progress containers
    progress_bar = st.progress(0, text="Initializing pipeline...")
    status_container = st.empty()
    log_container = st.empty()
    
    try:
        from pipeline import run_pipeline
        
        stages = [
            ("Extracting JD...", 8),
            ("Matching skills...", 16),
            ("Selecting experiences...", 24),
            ("Ranking projects...", 32),
            ("Rewriting content...", 40),
            ("Building resume...", 50),
            ("Optimizing for ATS...", 65),
            ("Checking compliance...", 75),
            ("Generating cover letter...", 85),
            ("Generating email...", 92),
            ("Saving outputs...", 98),
        ]
        
        # Simulate progress (actual pipeline runs in background)
        for stage_text, progress in stages[:3]:
            progress_bar.progress(progress, text=stage_text)
            st.session_state.pipeline_log.append(f"✅ {stage_text}")
            time.sleep(0.3)
        
        # Run actual pipeline
        status_container.info("🔄 Pipeline running... This may take 1-3 minutes.")
        
        result = run_pipeline(
            jd_url=jd_url,
            jd_text=jd_text,
            enable_checkpoints=enable_checkpoints
        )
        
        # Complete progress
        progress_bar.progress(100, text="Complete!")
        
        if result.get("success"):
            st.session_state.pipeline_result = result
            st.session_state.final_state = result.get("state", {})
            
            status_container.success("🎉 Pipeline completed successfully!")
            
            # Show results summary
            st.markdown("### 📊 Results Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("ATS Score", f"{result.get('ats_score', 0):.0f}%")
            with col2:
                st.metric("Compliance", f"{result.get('compliance_score', 0):.0f}%")
            with col3:
                st.metric("Duration", f"{result.get('duration', 0):.1f}s")
            with col4:
                st.metric("Thread ID", result.get('thread_id', 'N/A'))
            
            if result.get('output_folder'):
                st.info(f"📁 Outputs saved to: `{result['output_folder']}`")
            
            # Navigation buttons
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 View Resume", use_container_width=True):
                    st.switch_page("pages/3_📄_Resume.py")
            with col2:
                if st.button("✉️ View Cover Letter & Email", use_container_width=True):
                    st.switch_page("pages/4_✉️_Cover_Letter_Email.py")
        else:
            status_container.error(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        status_container.error(f"❌ Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
    
    finally:
        st.session_state.pipeline_running = False

# Show previous results if available
elif st.session_state.pipeline_result and not st.session_state.pipeline_running:
    st.markdown("### 📊 Previous Run Results")
    
    result = st.session_state.pipeline_result
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("ATS Score", f"{result.get('ats_score', 0):.0f}%")
    with col2:
        st.metric("Compliance", f"{result.get('compliance_score', 0):.0f}%")
    with col3:
        st.metric("Duration", f"{result.get('duration', 0):.1f}s")
    with col4:
        st.metric("Thread ID", result.get('thread_id', 'N/A'))
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 View Resume", use_container_width=True):
            st.switch_page("pages/3_📄_Resume.py")
    with col2:
        if st.button("✉️ View Cover Letter & Email", use_container_width=True):
            st.switch_page("pages/4_✉️_Cover_Letter_Email.py")

# Help section
with st.expander("❓ Help & Tips"):
    st.markdown("""
    ### Tips for Best Results
    
    1. **Use complete job descriptions** - More detail = better tailoring
    2. **LinkedIn URLs work best** - They're structured and easy to parse
    3. **Check your GitHub credentials** - Required for project ranking
    4. **Review Configuration** - Adjust settings before running
    
    ### What the pipeline does:
    
    1. **Extracts JD** - Parses company, role, skills, keywords
    2. **Matches Skills** - Compares your skills to requirements
    3. **Selects Content** - Picks most relevant experiences & projects
    4. **Rewrites Bullets** - Incorporates JD keywords with action verbs
    5. **Builds Resume** - Generates tailored JSON resume
    6. **Optimizes ATS** - Iterates until 95%+ score
    7. **Checks Compliance** - Validates against checklists
    8. **Generates Cover Letter** - Personalized with company research
    9. **Creates Email** - Outreach email for recruiters
    """)
