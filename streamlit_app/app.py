"""
Streamlit App - Job Application Assistant

Main entry point for the Streamlit GUI.
Run with: streamlit run streamlit_app/app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

# Page config
st.set_page_config(
    page_title="Job Application Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 20px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main page - Home / Dashboard"""
    
    # Header
    st.markdown('<p class="main-header">📄 Job Application Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered resume tailoring, cover letters, and application tracking</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/resume.png", width=80)
        st.markdown("### Navigation")
        st.markdown("""
        - 🏠 **Home** - Dashboard
        - ⚙️ **Configure** - Settings
        - 🚀 **Run Pipeline** - Process JD
        - 📄 **Resume** - View Results
        - ✉️ **Cover Letter & Email** - View Documents
        - 👤 **Candidate Profile** - Edit Your Info
        """)
        
        st.markdown("---")
        st.markdown("### Quick Stats")
        
        # Check if we have session state data
        if "pipeline_result" in st.session_state and st.session_state.pipeline_result:
            result = st.session_state.pipeline_result
            st.metric("ATS Score", f"{result.get('ats_score', 0):.0f}%")
            st.metric("Compliance", f"{result.get('compliance_score', 0):.0f}%")
            if result.get("success"):
                st.success("✅ Pipeline Complete")
        else:
            st.info("No pipeline run yet")
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 How It Works")
        st.markdown("""
        1. **Configure** - Set your preferences (experiences, projects, thresholds)
        2. **Paste JD** - Enter job description URL or text
        3. **Run Pipeline** - AI processes and generates tailored documents
        4. **Get Results** - Copy resume, cover letter, and email
        """)
        
        st.markdown("### 📊 Pipeline Stages")
        stages = [
            ("1. JD Extraction", "Parse job description"),
            ("2. Skill Matching", "Match your skills to JD"),
            ("3. Content Selection", "Select experiences & projects"),
            ("4. Rewriting", "Optimize bullets with keywords"),
            ("5. Resume Building", "Assemble tailored resume"),
            ("6. ATS Optimization", "Achieve 95%+ ATS score"),
            ("7. Compliance Check", "Validate against checklists"),
            ("8. Cover Letter", "Generate personalized letter"),
            ("9. Email Generation", "Create outreach emails"),
        ]
        
        for stage, desc in stages:
            st.markdown(f"- **{stage}**: {desc}")
    
    with col2:
        st.markdown("### 🚀 Quick Start")
        
        if st.button("⚙️ Go to Configuration", use_container_width=True):
            st.switch_page("pages/1_⚙️_Configure.py")
        
        if st.button("🚀 Run Pipeline", use_container_width=True):
            st.switch_page("pages/2_🚀_Run_Pipeline.py")
        
        if st.button("📄 View Resume", use_container_width=True):
            st.switch_page("pages/3_📄_Resume.py")
        
        if st.button("✉️ View Cover Letter & Email", use_container_width=True):
            st.switch_page("pages/4_✉️_Cover_Letter_Email.py")
        
        if st.button("👤 Edit Candidate Profile", use_container_width=True):
            st.switch_page("pages/5_👤_Candidate_Profile.py")
        
        st.markdown("---")
        
        st.markdown("### ⚡ Current Configuration")
        try:
            from pipeline.config import RESUME_CONFIG, ATS_CONFIG, PIPELINE_CONFIG
            
            config_col1, config_col2 = st.columns(2)
            with config_col1:
                st.markdown(f"**Max Experiences:** {RESUME_CONFIG['max_experiences']}")
                st.markdown(f"**Max Projects:** {RESUME_CONFIG['max_projects']}")
            with config_col2:
                st.markdown(f"**ATS Target:** {ATS_CONFIG['target_score']}%")
                st.markdown(f"**Compliance:** {PIPELINE_CONFIG['compliance_pass_threshold']}%")
        except Exception as e:
            st.warning(f"Could not load config: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888;">
        Built with LangGraph, OpenAI, and Streamlit | 
        <a href="https://github.com/your-repo" target="_blank">GitHub</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
