"""
Resume Page - Job Application Assistant

Display and copy generated resume content.
Includes LaTeX/PDF generation.
"""

import streamlit as st
import sys
import json
from pathlib import Path
import tempfile
import os

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
st.markdown("View, copy, and download your tailored resume")

# Helper function to safely get attributes
def safe_get(obj, key, default=""):
    if hasattr(obj, key):
        return getattr(obj, key)
    elif isinstance(obj, dict):
        return obj.get(key, default)
    return default


# ============================================================================
# SIDEBAR - PDF GENERATION
# ============================================================================
with st.sidebar:
    st.markdown("### 📑 PDF Generation")
    
    # Check if pdflatex is available
    import shutil
    pdflatex_available = shutil.which('pdflatex') is not None
    
    if pdflatex_available:
        st.success("✅ pdflatex found")
    else:
        st.warning("⚠️ pdflatex not found")
        st.caption("Install TeX Live or MiKTeX to generate PDFs")
    
    st.markdown("---")
    
    # Generate from candidate data
    st.markdown("#### From Candidate Profile")
    if st.button("📄 Generate PDF from Profile", use_container_width=True, disabled=not pdflatex_available):
        try:
            from mcp_server.tools.latex_generator import generate_resume_pdf
            
            with st.spinner("Generating PDF..."):
                # Create temp directory for output
                output_dir = project_root / "output"
                output_dir.mkdir(exist_ok=True)
                
                pdf_path = generate_resume_pdf(
                    output_dir=output_dir,
                    filename="resume_from_profile"
                )
                
                if pdf_path and pdf_path.exists():
                    st.session_state.generated_pdf = pdf_path
                    st.success("✅ PDF generated!")
                else:
                    st.error("❌ PDF generation failed")
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Download generated PDF
    if "generated_pdf" in st.session_state and st.session_state.generated_pdf:
        pdf_path = st.session_state.generated_pdf
        if Path(pdf_path).exists():
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇️ Download PDF",
                    data=f.read(),
                    file_name="resume.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    st.markdown("---")
    st.markdown("#### Quick Links")
    if st.button("🚀 Run Pipeline", use_container_width=True):
        st.switch_page("pages/2_🚀_Run_Pipeline.py")
    if st.button("✉️ Cover Letter", use_container_width=True):
        st.switch_page("pages/4_✉️_Cover_Letter_Email.py")
    if st.button("👤 Edit Profile", use_container_width=True):
        st.switch_page("pages/5_👤_Candidate_Profile.py")


# ============================================================================
# MAIN CONTENT
# ============================================================================

# Check if we have pipeline results or use candidate data
has_pipeline_results = "final_state" in st.session_state and st.session_state.final_state

if has_pipeline_results:
    state = st.session_state.final_state
    resume_json = state.get("resume_json")
    structured_jd = state.get("structured_jd")
    
    # Display scores
    st.markdown("### 📊 Pipeline Results")
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
else:
    # No pipeline results - show candidate data instead
    st.info("ℹ️ No pipeline results found. Showing candidate profile data.")
    
    try:
        from mcp_server.tools.candidate_loader import get_complete_resume_data
        candidate_data = get_complete_resume_data()
        
        # Convert to resume_json-like format
        resume_json = {
            "header": candidate_data.get("header", {}),
            "summary": candidate_data.get("professional_summary", ""),
            "education": candidate_data.get("education", []),
            "experience": candidate_data.get("experiences", []),
            "projects": candidate_data.get("projects", []),
            "skills": candidate_data.get("skills", {}),
            "publications": candidate_data.get("publications", [])
        }
        structured_jd = None
    except Exception as e:
        st.error(f"Error loading candidate data: {e}")
        resume_json = None

if not resume_json:
    st.warning("⚠️ No resume data available. Please run the pipeline or check your candidate profile.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Run Pipeline"):
            st.switch_page("pages/2_🚀_Run_Pipeline.py")
    with col2:
        if st.button("👤 Edit Profile"):
            st.switch_page("pages/5_👤_Candidate_Profile.py")
    st.stop()


# ============================================================================
# RESUME TABS
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Full Resume", 
    "👤 Header & Summary", 
    "💼 Experience", 
    "🔧 Skills & Projects",
    "📑 PDF Export"
])

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
    if not summary:
        summary = safe_get(resume_json, 'professional_summary', '')
    if summary:
        resume_text += "## PROFESSIONAL SUMMARY\n"
        resume_text += f"{summary}\n\n"
    
    # Experience
    experiences = safe_get(resume_json, 'experience', [])
    if not experiences:
        experiences = safe_get(resume_json, 'experiences', [])
    if experiences:
        resume_text += "## EXPERIENCE\n"
        for exp in experiences:
            role = exp.get('role', '') or exp.get('job_title', '') if isinstance(exp, dict) else safe_get(exp, 'role', '')
            company = exp.get('company', '') if isinstance(exp, dict) else safe_get(exp, 'company', '')
            dates = exp.get('dates', '') or exp.get('date_range', '') if isinstance(exp, dict) else safe_get(exp, 'dates', '')
            location = exp.get('location', '') if isinstance(exp, dict) else safe_get(exp, 'location', '')
            
            resume_text += f"### {role}\n"
            resume_text += f"**{company}** | {dates}"
            if location:
                resume_text += f" | {location}"
            resume_text += "\n"
            
            bullets = exp.get('bullets', []) or exp.get('bullets_flat', []) if isinstance(exp, dict) else safe_get(exp, 'bullets', [])
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
            date = edu.get('graduation', '') or edu.get('graduation_date', '') if isinstance(edu, dict) else safe_get(edu, 'graduation', '')
            
            resume_text += f"**{degree}** - {institution}"
            if date:
                resume_text += f" ({date})"
            resume_text += "\n"
    
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
                for key, val in list(header.items())[:4]:
                    if val:
                        st.text_input(key.replace('_', ' ').title(), value=str(val), key=f"header_{key}", disabled=True)
        with col2:
            if isinstance(header, dict):
                for key, val in list(header.items())[4:]:
                    if val:
                        st.text_input(key.replace('_', ' ').title(), value=str(val), key=f"header_{key}", disabled=True)
    
    st.markdown("### 📝 Professional Summary")
    summary = safe_get(resume_json, 'summary', '') or safe_get(resume_json, 'professional_summary', '')
    st.text_area("Summary", value=summary, height=150, key="summary_edit", disabled=True)
    
    if summary:
        word_count = len(summary.split())
        st.caption(f"Word count: {word_count}")

with tab3:
    st.markdown("### 💼 Work Experience")
    
    experiences = safe_get(resume_json, 'experience', []) or safe_get(resume_json, 'experiences', [])
    if experiences:
        for i, exp in enumerate(experiences):
            role = safe_get(exp, 'role', '') or safe_get(exp, 'job_title', 'Role')
            company = safe_get(exp, 'company', 'Company')
            with st.expander(f"**{role}** at {company}", expanded=i==0):
                col1, col2 = st.columns(2)
                with col1:
                    dates = safe_get(exp, 'dates', '') or safe_get(exp, 'date_range', '')
                    st.write(f"**Dates:** {dates}")
                with col2:
                    st.write(f"**Location:** {safe_get(exp, 'location', '')}")
                
                st.markdown("**Bullets:**")
                bullets = safe_get(exp, 'bullets', []) or safe_get(exp, 'bullets_flat', [])
                bullets_text = "\n".join([f"• {b}" for b in bullets])
                st.text_area(f"Experience {i+1} Bullets", value=bullets_text, height=150, key=f"exp_{i}", disabled=True)
    else:
        st.info("No experiences found")

with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Skills")
        skills = safe_get(resume_json, 'skills', {})
        if skills and isinstance(skills, dict):
            for category, skill_list in skills.items():
                st.text_input(f"**{category}**", value=str(skill_list), key=f"skill_{category}", disabled=True)
        else:
            st.json(skills)
    
    with col2:
        st.markdown("### 🚀 Projects")
        projects = safe_get(resume_json, 'projects', [])
        if projects:
            for i, proj in enumerate(projects):
                with st.expander(safe_get(proj, 'name', f'Project {i+1}')):
                    url = safe_get(proj, 'url', '') or safe_get(proj, 'github_url', '')
                    if url:
                        st.write(f"**URL:** {url}")
                    bullets = safe_get(proj, 'bullets', [])
                    for b in bullets:
                        st.write(f"• {b}")
        else:
            st.info("No projects found")

with tab5:
    st.markdown("### 📑 LaTeX / PDF Export")
    
    # Check pdflatex
    import shutil
    pdflatex_available = shutil.which('pdflatex') is not None
    
    if not pdflatex_available:
        st.warning("""
        ⚠️ **pdflatex not found**
        
        To generate PDFs, install a TeX distribution:
        - **Windows**: [MiKTeX](https://miktex.org/download) or [TeX Live](https://tug.org/texlive/)
        - **Mac**: `brew install --cask mactex`
        - **Linux**: `sudo apt install texlive-full`
        
        After installation, restart Streamlit.
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Generate LaTeX")
        if st.button("📝 Generate .tex File", use_container_width=True):
            try:
                from mcp_server.tools.latex_generator import generate_resume_tex, load_candidate_data
                
                with st.spinner("Generating LaTeX..."):
                    output_dir = project_root / "output"
                    output_dir.mkdir(exist_ok=True)
                    
                    tex_path = generate_resume_tex(
                        output_path=output_dir / "resume.tex"
                    )
                    
                    st.session_state.generated_tex = tex_path
                    st.success(f"✅ Generated: {tex_path.name}")
            except Exception as e:
                st.error(f"Error: {e}")
        
        # Download .tex file
        if "generated_tex" in st.session_state and st.session_state.generated_tex:
            tex_path = Path(st.session_state.generated_tex)
            if tex_path.exists():
                with open(tex_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        "⬇️ Download .tex",
                        data=f.read(),
                        file_name="resume.tex",
                        mime="text/plain",
                        use_container_width=True
                    )
    
    with col2:
        st.markdown("#### Generate PDF")
        if st.button("📄 Generate PDF", use_container_width=True, disabled=not pdflatex_available):
            try:
                from mcp_server.tools.latex_generator import generate_resume_pdf
                
                with st.spinner("Generating PDF (this may take a moment)..."):
                    output_dir = project_root / "output"
                    output_dir.mkdir(exist_ok=True)
                    
                    pdf_path = generate_resume_pdf(
                        output_dir=output_dir,
                        filename="resume"
                    )
                    
                    if pdf_path and pdf_path.exists():
                        st.session_state.generated_pdf = pdf_path
                        st.success(f"✅ Generated: {pdf_path.name}")
                    else:
                        st.error("❌ PDF generation failed. Check LaTeX errors.")
            except Exception as e:
                st.error(f"Error: {e}")
        
        # Download PDF
        if "generated_pdf" in st.session_state and st.session_state.generated_pdf:
            pdf_path = Path(st.session_state.generated_pdf)
            if pdf_path.exists():
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download PDF",
                        data=f.read(),
                        file_name="resume.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
    
    st.markdown("---")
    
    # Manual compilation instructions
    with st.expander("📖 Manual Compilation"):
        st.markdown("""
        If automatic PDF generation doesn't work, you can compile manually:
        
        1. Download the `.tex` file above
        2. Open terminal/command prompt
        3. Navigate to the download folder
        4. Run: `pdflatex resume.tex`
        
        Or use an online LaTeX editor like [Overleaf](https://www.overleaf.com/).
        """)


# ============================================================================
# JSON VIEW
# ============================================================================
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
