"""
Resume Page - Job Application Assistant

Display and copy generated resume content.
"""

import streamlit as st
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

st.set_page_config(
    page_title="Resume - Job Application Assistant",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Generated Resume")
st.markdown("View and copy your tailored resume content")

# Check if we have results
if "final_state" not in st.session_state or not st.session_state.final_state:
    st.warning("⚠️ No pipeline results found. Please run the pipeline first.")
    if st.button("🚀 Go to Run Pipeline"):
        st.switch_page("pages/2_🚀_Run_Pipeline.py")
    st.stop()

state = st.session_state.final_state

# Extract resume data
resume_json = state.get("resume_json")
structured_jd = state.get("structured_jd")

if not resume_json:
    st.warning("⚠️ No resume was generated. There may have been an error in the pipeline.")
    st.stop()

# Display scores
st.markdown("### 📊 Scores")
col1, col2, col3 = st.columns(3)
with col1:
    ats_score = state.get("ats_score", 0)
    st.metric("ATS Score", f"{ats_score:.0f}%", 
              delta="✅ Passed" if ats_score >= 95 else "⚠️ Below target")
with col2:
    compliance_score = state.get("compliance_score", 0)
    st.metric("Compliance Score", f"{compliance_score:.0f}%",
              delta="✅ Passed" if compliance_score >= 85 else "⚠️ Below target")
with col3:
    if structured_jd:
        company = getattr(structured_jd, 'company_name', 'Unknown') if hasattr(structured_jd, 'company_name') else structured_jd.get('company_name', 'Unknown')
        role = getattr(structured_jd, 'role_title', 'Unknown') if hasattr(structured_jd, 'role_title') else structured_jd.get('role_title', 'Unknown')
        st.metric("Tailored For", f"{company}")
        st.caption(role)

st.markdown("---")

# Resume content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Full Resume", "👤 Header & Summary", "💼 Experience", "🔧 Skills & Projects"])

# Helper function to safely get attributes
def safe_get(obj, key, default=""):
    if hasattr(obj, key):
        return getattr(obj, key)
    elif isinstance(obj, dict):
        return obj.get(key, default)
    return default

with tab1:
    st.markdown("### 📋 Complete Resume (Copy-Ready)")
    
    # Build full resume text
    resume_text = ""
    
    # Header
    header = safe_get(resume_json, 'header', {})
    if header:
        name = header.get('name', '') if isinstance(header, dict) else safe_get(header, 'name', '')
        resume_text += f"# {name}\n"
        
        contact_parts = []
        for field in ['email', 'phone', 'linkedin', 'github', 'location']:
            val = header.get(field, '') if isinstance(header, dict) else safe_get(header, field, '')
            if val:
                contact_parts.append(val)
        if contact_parts:
            resume_text += " | ".join(contact_parts) + "\n"
        resume_text += "\n"
    
    # Summary
    summary = safe_get(resume_json, 'summary', '')
    if summary:
        resume_text += "## PROFESSIONAL SUMMARY\n"
        resume_text += f"{summary}\n\n"
    
    # Experience
    experiences = safe_get(resume_json, 'experience', [])
    if experiences:
        resume_text += "## EXPERIENCE\n"
        for exp in experiences:
            role = exp.get('role', '') if isinstance(exp, dict) else safe_get(exp, 'role', '')
            company = exp.get('company', '') if isinstance(exp, dict) else safe_get(exp, 'company', '')
            dates = exp.get('dates', '') if isinstance(exp, dict) else safe_get(exp, 'dates', '')
            location = exp.get('location', '') if isinstance(exp, dict) else safe_get(exp, 'location', '')
            
            resume_text += f"### {role}\n"
            resume_text += f"**{company}** | {dates}"
            if location:
                resume_text += f" | {location}"
            resume_text += "\n"
            
            bullets = exp.get('bullets', []) if isinstance(exp, dict) else safe_get(exp, 'bullets', [])
            for bullet in bullets:
                resume_text += f"• {bullet}\n"
            resume_text += "\n"
    
    # Projects
    projects = safe_get(resume_json, 'projects', [])
    if projects:
        resume_text += "## PROJECTS\n"
        for proj in projects:
            name = proj.get('name', '') if isinstance(proj, dict) else safe_get(proj, 'name', '')
            url = proj.get('url', '') or proj.get('github_url', '') if isinstance(proj, dict) else safe_get(proj, 'url', '')
            
            resume_text += f"### {name}"
            if url:
                resume_text += f" | {url}"
            resume_text += "\n"
            
            bullets = proj.get('bullets', []) if isinstance(proj, dict) else safe_get(proj, 'bullets', [])
            for bullet in bullets:
                resume_text += f"• {bullet}\n"
            resume_text += "\n"
    
    # Skills
    skills = safe_get(resume_json, 'skills', {})
    if skills:
        resume_text += "## SKILLS\n"
        if isinstance(skills, dict):
            for category, skill_list in skills.items():
                resume_text += f"**{category}:** {skill_list}\n"
        resume_text += "\n"
    
    # Education
    education = safe_get(resume_json, 'education', [])
    if education:
        resume_text += "## EDUCATION\n"
        for edu in education:
            degree = edu.get('degree', '') if isinstance(edu, dict) else safe_get(edu, 'degree', '')
            institution = edu.get('institution', '') if isinstance(edu, dict) else safe_get(edu, 'institution', '')
            date = edu.get('date', '') if isinstance(edu, dict) else safe_get(edu, 'date', '')
            
            resume_text += f"**{degree}** - {institution} ({date})\n"
    
    # Display with copy button
    st.text_area(
        "Resume Content (Markdown)",
        value=resume_text,
        height=500,
        key="full_resume"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Download as TXT",
            data=resume_text,
            file_name="resume.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        st.download_button(
            "⬇️ Download as MD",
            data=resume_text,
            file_name="resume.md",
            mime="text/markdown",
            use_container_width=True
        )

with tab2:
    st.markdown("### 👤 Header")
    header = safe_get(resume_json, 'header', {})
    if header:
        col1, col2 = st.columns(2)
        with col1:
            if isinstance(header, dict):
                for key, val in header.items():
                    if val:
                        st.text_input(key.title(), value=val, key=f"header_{key}")
            else:
                st.json(header)
    
    st.markdown("### 📝 Professional Summary")
    summary = safe_get(resume_json, 'summary', '')
    st.text_area("Summary", value=summary, height=150, key="summary_edit")
    
    if summary:
        word_count = len(summary.split())
        st.caption(f"Word count: {word_count}")

with tab3:
    st.markdown("### 💼 Work Experience")
    
    experiences = safe_get(resume_json, 'experience', [])
    if experiences:
        for i, exp in enumerate(experiences):
            with st.expander(f"**{safe_get(exp, 'role', 'Role')}** at {safe_get(exp, 'company', 'Company')}", expanded=i==0):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Dates:** {safe_get(exp, 'dates', '')}")
                with col2:
                    st.write(f"**Location:** {safe_get(exp, 'location', '')}")
                
                st.markdown("**Bullets:**")
                bullets = safe_get(exp, 'bullets', [])
                bullets_text = "\n".join([f"• {b}" for b in bullets])
                st.text_area(f"Experience {i+1} Bullets", value=bullets_text, height=150, key=f"exp_{i}")
    else:
        st.info("No experiences found")

with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Skills")
        skills = safe_get(resume_json, 'skills', {})
        if skills and isinstance(skills, dict):
            for category, skill_list in skills.items():
                st.text_input(f"**{category}**", value=skill_list, key=f"skill_{category}")
        else:
            st.json(skills)
    
    with col2:
        st.markdown("### 🚀 Projects")
        projects = safe_get(resume_json, 'projects', [])
        if projects:
            for i, proj in enumerate(projects):
                with st.expander(safe_get(proj, 'name', f'Project {i+1}')):
                    st.write(f"**URL:** {safe_get(proj, 'url', '') or safe_get(proj, 'github_url', '')}")
                    bullets = safe_get(proj, 'bullets', [])
                    for b in bullets:
                        st.write(f"• {b}")
        else:
            st.info("No projects found")

# JSON view
st.markdown("---")
with st.expander("🔍 View Raw JSON"):
    # Convert to dict if needed
    if hasattr(resume_json, 'dict'):
        resume_dict = resume_json.dict()
    elif hasattr(resume_json, 'model_dump'):
        resume_dict = resume_json.model_dump()
    elif isinstance(resume_json, dict):
        resume_dict = resume_json
    else:
        resume_dict = {"error": "Could not serialize resume"}
    
    st.json(resume_dict)
    
    st.download_button(
        "⬇️ Download JSON",
        data=json.dumps(resume_dict, indent=2, default=str),
        file_name="resume.json",
        mime="application/json",
        use_container_width=True
    )
