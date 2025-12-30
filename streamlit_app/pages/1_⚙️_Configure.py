"""
Configuration Page - Job Application Assistant

Allows users to configure pipeline parameters.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

st.set_page_config(
    page_title="Configure - Job Application Assistant",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Configuration")
st.markdown("Configure pipeline parameters and preferences")

# Initialize session state for config if not exists
if "config" not in st.session_state:
    try:
        from pipeline.config import RESUME_CONFIG, COVER_LETTER_CONFIG, ATS_CONFIG, PIPELINE_CONFIG
        st.session_state.config = {
            "resume": RESUME_CONFIG.copy(),
            "cover_letter": COVER_LETTER_CONFIG.copy(),
            "ats": ATS_CONFIG.copy(),
            "pipeline": PIPELINE_CONFIG.copy()
        }
    except:
        st.session_state.config = {
            "resume": {
                "max_experiences": 4,
                "bullets_per_experience": 4,
                "max_projects": 3,
                "bullets_per_project": 2,
                "summary_min_words": 40,
                "summary_max_words": 60,
            },
            "cover_letter": {
                "target_words": 300,
                "max_words": 400,
                "tone": "professional"
            },
            "ats": {
                "target_score": 95,
                "max_iterations": 3
            },
            "pipeline": {
                "ats_pass_threshold": 95,
                "compliance_pass_threshold": 85,
                "enable_email_generation": True,
                "save_to_excel": True
            }
        }

# Create tabs for different config sections
tab1, tab2, tab3, tab4 = st.tabs(["📄 Resume", "📝 Cover Letter", "🎯 ATS", "⚙️ Pipeline"])

with tab1:
    st.markdown("### Resume Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Content Limits")
        st.session_state.config["resume"]["max_experiences"] = st.slider(
            "Maximum Experiences",
            min_value=1, max_value=6, 
            value=st.session_state.config["resume"]["max_experiences"],
            help="Number of work experiences to include"
        )
        
        st.session_state.config["resume"]["bullets_per_experience"] = st.slider(
            "Bullets per Experience",
            min_value=2, max_value=6,
            value=st.session_state.config["resume"]["bullets_per_experience"],
            help="Number of bullet points per experience"
        )
        
        st.session_state.config["resume"]["max_projects"] = st.slider(
            "Maximum Projects",
            min_value=1, max_value=5,
            value=st.session_state.config["resume"]["max_projects"],
            help="Number of GitHub projects to include"
        )
    
    with col2:
        st.markdown("#### Word Counts")
        st.session_state.config["resume"]["summary_min_words"] = st.number_input(
            "Summary Min Words",
            min_value=20, max_value=100,
            value=st.session_state.config["resume"]["summary_min_words"]
        )
        
        st.session_state.config["resume"]["summary_max_words"] = st.number_input(
            "Summary Max Words",
            min_value=40, max_value=150,
            value=st.session_state.config["resume"]["summary_max_words"]
        )

with tab2:
    st.markdown("### Cover Letter Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.config["cover_letter"]["target_words"] = st.slider(
            "Target Word Count",
            min_value=200, max_value=500,
            value=st.session_state.config["cover_letter"]["target_words"],
            help="Target length for cover letter"
        )
        
        st.session_state.config["cover_letter"]["max_words"] = st.slider(
            "Maximum Words",
            min_value=300, max_value=600,
            value=st.session_state.config["cover_letter"]["max_words"]
        )
    
    with col2:
        st.session_state.config["cover_letter"]["tone"] = st.selectbox(
            "Tone",
            options=["professional", "enthusiastic", "conversational"],
            index=["professional", "enthusiastic", "conversational"].index(
                st.session_state.config["cover_letter"].get("tone", "professional")
            ),
            help="Writing style for cover letter"
        )

with tab3:
    st.markdown("### ATS Optimization Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.config["ats"]["target_score"] = st.slider(
            "Target ATS Score (%)",
            min_value=80, max_value=100,
            value=st.session_state.config["ats"]["target_score"],
            help="Target score to achieve before proceeding"
        )
    
    with col2:
        st.session_state.config["ats"]["max_iterations"] = st.slider(
            "Max Optimization Iterations",
            min_value=1, max_value=5,
            value=st.session_state.config["ats"]["max_iterations"],
            help="Maximum retry attempts for ATS optimization"
        )

with tab4:
    st.markdown("### Pipeline Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Thresholds")
        st.session_state.config["pipeline"]["ats_pass_threshold"] = st.slider(
            "ATS Pass Threshold (%)",
            min_value=80, max_value=100,
            value=st.session_state.config["pipeline"]["ats_pass_threshold"]
        )
        
        st.session_state.config["pipeline"]["compliance_pass_threshold"] = st.slider(
            "Compliance Pass Threshold (%)",
            min_value=70, max_value=100,
            value=st.session_state.config["pipeline"]["compliance_pass_threshold"]
        )
    
    with col2:
        st.markdown("#### Features")
        st.session_state.config["pipeline"]["enable_email_generation"] = st.checkbox(
            "Enable Email Generation",
            value=st.session_state.config["pipeline"]["enable_email_generation"]
        )
        
        st.session_state.config["pipeline"]["save_to_excel"] = st.checkbox(
            "Save to Excel Tracker",
            value=st.session_state.config["pipeline"]["save_to_excel"]
        )

# Save button
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("💾 Save Configuration", use_container_width=True, type="primary"):
        st.success("✅ Configuration saved to session!")
        st.balloons()

# Display current config as JSON
with st.expander("📋 View Current Configuration (JSON)"):
    st.json(st.session_state.config)

# Environment variables check
st.markdown("---")
st.markdown("### 🔑 Environment Variables Status")

import os
env_vars = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "GITHUB_USERNAME": os.getenv("GITHUB_USERNAME"),
    "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
}

col1, col2, col3 = st.columns(3)
with col1:
    if env_vars["OPENAI_API_KEY"]:
        st.success("✅ OPENAI_API_KEY set")
    else:
        st.error("❌ OPENAI_API_KEY missing")

with col2:
    if env_vars["GITHUB_USERNAME"]:
        st.success(f"✅ GitHub: {env_vars['GITHUB_USERNAME']}")
    else:
        st.warning("⚠️ GITHUB_USERNAME not set")

with col3:
    if env_vars["GITHUB_TOKEN"]:
        st.success("✅ GITHUB_TOKEN set")
    else:
        st.warning("⚠️ GITHUB_TOKEN not set")
