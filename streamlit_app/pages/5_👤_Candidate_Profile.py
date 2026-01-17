"""
Candidate Profile Page - Job Application Assistant

Allows users to edit their candidate information.
Supports the simplified JSON template structure.
"""

import streamlit as st
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

st.set_page_config(
    page_title="Candidate Profile - Job Application Assistant",
    page_icon="👤",
    layout="wide"
)

# File path
CANDIDATE_FILE = project_root / "data" / "candidate_experience.json"


def load_candidate_data():
    """Load candidate data from JSON file."""
    try:
        with open(CANDIDATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return get_empty_template()
    except json.JSONDecodeError:
        st.error("Error reading candidate file. Using empty template.")
        return get_empty_template()


def save_candidate_data(data):
    """Save candidate data to JSON file."""
    # Ensure directory exists
    CANDIDATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CANDIDATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return True


def get_empty_template():
    """Return empty candidate template matching new structure."""
    return {
        "header": {
            "name": "",
            "location": "",
            "email": "",
            "phone": "",
            "linkedin_url": "",
            "linkedin_text": "LinkedIn",
            "github_url": "",
            "github_text": "GitHub",
            "portfolio_url": "",
            "portfolio_text": "Portfolio"
        },
        "professional_summary": "",
        "education": [],
        "experience": [],
        "research": {
            "title": "",
            "doi_url": "",
            "doi_text": ""
        },
        "projects": [],
        "skills": {
            "ai_ml": "",
            "ai_applications": "",
            "mlops": "",
            "frameworks": ""
        },
        "certifications": []
    }


# Initialize session state
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = load_candidate_data()

data = st.session_state.candidate_data

# Page header
st.title("👤 Candidate Profile")
st.markdown("Edit your personal information, experiences, skills, and projects")

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 Basic Info", 
    "💼 Experience", 
    "🎓 Education", 
    "🔧 Skills",
    "🚀 Projects",
    "📚 Research & Certs"
])

# ============================================================================
# TAB 1: BASIC INFO
# ============================================================================
with tab1:
    st.markdown("### Personal Information")
    
    # Ensure header exists
    if "header" not in data:
        data["header"] = get_empty_template()["header"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        data["header"]["name"] = st.text_input(
            "Full Name *",
            value=data.get("header", {}).get("name", ""),
            key="name"
        )
        
        data["header"]["email"] = st.text_input(
            "Email *",
            value=data.get("header", {}).get("email", ""),
            key="email"
        )
        
        data["header"]["phone"] = st.text_input(
            "Phone",
            value=data.get("header", {}).get("phone", ""),
            key="phone"
        )
        
        data["header"]["location"] = st.text_input(
            "Location",
            value=data.get("header", {}).get("location", ""),
            placeholder="City, State",
            key="location"
        )
    
    with col2:
        data["header"]["linkedin_url"] = st.text_input(
            "LinkedIn URL",
            value=data.get("header", {}).get("linkedin_url", ""),
            placeholder="https://www.linkedin.com/in/yourprofile",
            key="linkedin"
        )
        
        data["header"]["github_url"] = st.text_input(
            "GitHub URL",
            value=data.get("header", {}).get("github_url", ""),
            placeholder="https://github.com/yourusername",
            key="github"
        )
        
        data["header"]["portfolio_url"] = st.text_input(
            "Portfolio URL",
            value=data.get("header", {}).get("portfolio_url", ""),
            placeholder="https://yourportfolio.com",
            key="portfolio"
        )
    
    st.markdown("---")
    st.markdown("### Professional Summary")
    
    data["professional_summary"] = st.text_area(
        "Summary *",
        value=data.get("professional_summary", ""),
        height=150,
        key="summary",
        help="A brief professional summary highlighting your key skills and experience"
    )
    
    if data.get("professional_summary"):
        word_count = len(data["professional_summary"].split())
        st.caption(f"Word count: {word_count}")

# ============================================================================
# TAB 2: EXPERIENCE
# ============================================================================
with tab2:
    st.markdown("### Work Experience")
    st.caption("Add your work experiences. Most recent first.")
    
    # Ensure experience list exists
    if "experience" not in data:
        data["experience"] = []
    
    experiences = data.get("experience", [])
    
    # Add new experience button
    if st.button("➕ Add New Experience", key="add_exp"):
        new_exp = {
            "company": "",
            "job_title": "",
            "date_range": "",
            "location": "",
            "bullets": []
        }
        experiences.insert(0, new_exp)
        data["experience"] = experiences
        st.rerun()
    
    # Display existing experiences
    for i, exp in enumerate(experiences):
        with st.expander(
            f"**{exp.get('job_title', 'New Role')}** at {exp.get('company', 'Company')} "
            f"({exp.get('date_range', '')})",
            expanded=(i == 0)
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                exp["job_title"] = st.text_input(
                    "Job Title *",
                    value=exp.get("job_title", ""),
                    key=f"exp_title_{i}",
                    placeholder="e.g., Machine Learning Engineer"
                )
                
                exp["company"] = st.text_input(
                    "Company *",
                    value=exp.get("company", ""),
                    key=f"exp_company_{i}"
                )
            
            with col2:
                exp["date_range"] = st.text_input(
                    "Date Range",
                    value=exp.get("date_range", ""),
                    placeholder="e.g., Jan 2023 -- Present",
                    key=f"exp_dates_{i}"
                )
                
                exp["location"] = st.text_input(
                    "Location",
                    value=exp.get("location", ""),
                    placeholder="e.g., Boston, MA or Remote",
                    key=f"exp_location_{i}"
                )
            
            # Bullets
            st.markdown("**Bullet Points** (one per line)")
            bullets_text = "\n".join(exp.get("bullets", []))
            new_bullets = st.text_area(
                "Bullets",
                value=bullets_text,
                height=150,
                key=f"exp_bullets_{i}",
                label_visibility="collapsed",
                help="Include a 'Skills:' line at the end to highlight key skills used"
            )
            exp["bullets"] = [b.strip() for b in new_bullets.split("\n") if b.strip()]
            
            # Delete button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col3:
                if st.button("🗑️ Delete Experience", key=f"del_exp_{i}"):
                    experiences.pop(i)
                    data["experience"] = experiences
                    st.rerun()

# ============================================================================
# TAB 3: EDUCATION
# ============================================================================
with tab3:
    st.markdown("### Education")
    
    # Ensure education list exists
    if "education" not in data:
        data["education"] = []
    
    education = data.get("education", [])
    
    if st.button("➕ Add Education", key="add_edu"):
        new_edu = {
            "institution": "",
            "degree": "",
            "graduation_date": "",
            "location": ""
        }
        education.insert(0, new_edu)
        data["education"] = education
        st.rerun()
    
    for i, edu in enumerate(education):
        with st.expander(
            f"**{edu.get('institution', 'Institution')}** - {edu.get('degree', 'Degree')[:50]}",
            expanded=(i == 0)
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                edu["institution"] = st.text_input(
                    "Institution *",
                    value=edu.get("institution", ""),
                    key=f"edu_inst_{i}"
                )
                
                edu["graduation_date"] = st.text_input(
                    "Graduation Date",
                    value=edu.get("graduation_date", ""),
                    placeholder="e.g., May 2024",
                    key=f"edu_grad_{i}"
                )
            
            with col2:
                edu["location"] = st.text_input(
                    "Location",
                    value=edu.get("location", ""),
                    key=f"edu_loc_{i}"
                )
            
            edu["degree"] = st.text_input(
                "Degree (include GPA and Coursework) *",
                value=edu.get("degree", ""),
                placeholder="e.g., M.S. in Data Science, GPA: 4.0; Coursework: ML, NLP, Statistics",
                key=f"edu_degree_{i}",
                help="Format: Degree, GPA: X.X; Coursework: Subject1, Subject2"
            )
            
            # Delete
            if st.button("🗑️ Delete Education", key=f"del_edu_{i}"):
                education.pop(i)
                data["education"] = education
                st.rerun()

# ============================================================================
# TAB 4: SKILLS
# ============================================================================
with tab4:
    st.markdown("### Skills")
    st.caption("Enter skills as comma-separated values for each category")
    
    # Ensure skills dict exists
    if "skills" not in data:
        data["skills"] = get_empty_template()["skills"]
    
    skills = data.get("skills", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        skills["ai_ml"] = st.text_area(
            "AI/ML Skills *",
            value=skills.get("ai_ml", ""),
            height=100,
            key="skill_ai_ml",
            placeholder="Python, Machine Learning, Deep Learning, NLP, LLMs, Generative AI"
        )
        
        skills["ai_applications"] = st.text_area(
            "AI Applications",
            value=skills.get("ai_applications", ""),
            height=100,
            key="skill_ai_apps",
            placeholder="API Integration, Prompt Engineering, RAG, Vector Databases, LangChain"
        )
    
    with col2:
        skills["mlops"] = st.text_area(
            "MLOps & Tools",
            value=skills.get("mlops", ""),
            height=100,
            key="skill_mlops",
            placeholder="Git, Docker, CI/CD, Model Deployment, Logging, Versioning"
        )
        
        skills["frameworks"] = st.text_area(
            "Frameworks",
            value=skills.get("frameworks", ""),
            height=100,
            key="skill_frameworks",
            placeholder="Scikit-learn, TensorFlow, PyTorch, Keras"
        )
    
    data["skills"] = skills
    
    # Show all skills count
    st.markdown("---")
    all_skills = []
    for skill_str in skills.values():
        if skill_str:
            all_skills.extend([s.strip() for s in skill_str.split(",") if s.strip()])
    st.info(f"📊 Total unique skills: {len(set(all_skills))}")

# ============================================================================
# TAB 5: PROJECTS
# ============================================================================
with tab5:
    st.markdown("### Projects")
    st.caption("Add your key projects (GitHub, personal, etc.)")
    
    # Ensure projects list exists
    if "projects" not in data:
        data["projects"] = []
    
    projects = data.get("projects", [])
    
    if st.button("➕ Add Project", key="add_proj"):
        new_proj = {
            "name": "",
            "subtitle": "",
            "technologies": "",
            "github_url": "",
            "github_text": "GitHub",
            "bullets": []
        }
        projects.insert(0, new_proj)
        data["projects"] = projects
        st.rerun()
    
    for i, proj in enumerate(projects):
        with st.expander(
            f"**{proj.get('name', 'New Project')}** ({proj.get('technologies', '')})",
            expanded=(i == 0)
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                proj["name"] = st.text_input(
                    "Project Name *",
                    value=proj.get("name", ""),
                    key=f"proj_name_{i}"
                )
                
                proj["technologies"] = st.text_input(
                    "Technologies",
                    value=proj.get("technologies", ""),
                    placeholder="e.g., LLMs, NLP, RAG",
                    key=f"proj_tech_{i}"
                )
            
            with col2:
                proj["github_url"] = st.text_input(
                    "GitHub URL",
                    value=proj.get("github_url", ""),
                    placeholder="https://github.com/user/project",
                    key=f"proj_github_{i}"
                )
                
                proj["subtitle"] = st.text_input(
                    "Subtitle (optional)",
                    value=proj.get("subtitle", ""),
                    placeholder="e.g., AI Application",
                    key=f"proj_subtitle_{i}"
                )
            
            # Bullets
            st.markdown("**Description Bullets** (one per line)")
            bullets_text = "\n".join(proj.get("bullets", []))
            new_bullets = st.text_area(
                "Bullets",
                value=bullets_text,
                height=100,
                key=f"proj_bullets_{i}",
                label_visibility="collapsed"
            )
            proj["bullets"] = [b.strip() for b in new_bullets.split("\n") if b.strip()]
            
            # Delete
            if st.button("🗑️ Delete Project", key=f"del_proj_{i}"):
                projects.pop(i)
                data["projects"] = projects
                st.rerun()

# ============================================================================
# TAB 6: RESEARCH & CERTIFICATIONS
# ============================================================================
with tab6:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Research / Publication")
        
        # Ensure research dict exists
        if "research" not in data:
            data["research"] = get_empty_template()["research"]
        
        research = data.get("research", {})
        
        research["title"] = st.text_input(
            "Publication Title",
            value=research.get("title", ""),
            key="research_title",
            placeholder="Your paper or research title"
        )
        
        research["doi_url"] = st.text_input(
            "DOI URL",
            value=research.get("doi_url", ""),
            key="research_doi_url",
            placeholder="https://doi.org/10.xxxx/xxxxx"
        )
        
        research["doi_text"] = st.text_input(
            "DOI Text (display)",
            value=research.get("doi_text", ""),
            key="research_doi_text",
            placeholder="DOI: 10.xxxx/xxxxx"
        )
        
        data["research"] = research
    
    with col2:
        st.markdown("### Certifications")
        
        # Ensure certifications list exists
        if "certifications" not in data:
            data["certifications"] = []
        
        certifications = data.get("certifications", [])
        
        if st.button("➕ Add Certification", key="add_cert"):
            certifications.append({
                "name": "",
                "issuer": "",
                "year": ""
            })
            data["certifications"] = certifications
            st.rerun()
        
        for i, cert in enumerate(certifications):
            with st.expander(cert.get("name", "New Certification") or "New Certification"):
                cert["name"] = st.text_input(
                    "Certification Name *",
                    value=cert.get("name", ""),
                    key=f"cert_name_{i}"
                )
                cert["issuer"] = st.text_input(
                    "Issuer",
                    value=cert.get("issuer", ""),
                    key=f"cert_issuer_{i}"
                )
                cert["year"] = st.text_input(
                    "Year",
                    value=str(cert.get("year", "") or ""),
                    key=f"cert_year_{i}"
                )
                
                if st.button("🗑️ Delete", key=f"del_cert_{i}"):
                    certifications.pop(i)
                    data["certifications"] = certifications
                    st.rerun()

# ============================================================================
# SAVE & ACTIONS
# ============================================================================
st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("💾 Save Profile", type="primary", use_container_width=True):
        try:
            save_candidate_data(data)
            st.session_state.candidate_data = data
            st.success("✅ Profile saved successfully!")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Error saving: {e}")

with col2:
    if st.button("🔄 Reload from File", use_container_width=True):
        st.session_state.candidate_data = load_candidate_data()
        st.rerun()

with col3:
    st.download_button(
        label="📥 Download JSON",
        data=json.dumps(data, indent=2, ensure_ascii=False),
        file_name="candidate_experience.json",
        mime="application/json",
        use_container_width=True
    )

# Preview section
with st.expander("📋 Preview JSON Data"):
    st.json(data)

# Import section
st.markdown("---")
st.markdown("### 📤 Import Existing Profile")

uploaded_file = st.file_uploader(
    "Upload a candidate_experience.json file",
    type=["json"],
    help="Upload an existing profile to replace current data"
)

if uploaded_file:
    try:
        imported_data = json.load(uploaded_file)
        if st.button("📥 Import Uploaded Profile"):
            st.session_state.candidate_data = imported_data
            save_candidate_data(imported_data)
            st.success("✅ Profile imported successfully!")
            st.rerun()
    except json.JSONDecodeError:
        st.error("Invalid JSON file")

# Template info
st.markdown("---")
with st.expander("ℹ️ Template Structure"):
    st.markdown("""
    ### JSON Template Structure
    
    ```json
    {
      "header": {
        "name": "Your Name",
        "location": "City, State",
        "email": "email@example.com",
        "phone": "+1 xxx-xxx-xxxx",
        "linkedin_url": "https://linkedin.com/in/...",
        "github_url": "https://github.com/...",
        "portfolio_url": "https://..."
      },
      "professional_summary": "Your summary...",
      "education": [
        {
          "institution": "University Name",
          "degree": "M.S. in Data Science, GPA: 4.0; Coursework: ML, NLP",
          "graduation_date": "May 2024",
          "location": "City, State"
        }
      ],
      "experience": [
        {
          "company": "Company Name",
          "job_title": "Job Title",
          "date_range": "Jan 2023 -- Present",
          "location": "City, State",
          "bullets": ["Bullet 1", "Bullet 2", "Skills: Python, ML"]
        }
      ],
      "projects": [
        {
          "name": "Project Name",
          "technologies": "Tech1, Tech2",
          "github_url": "https://github.com/...",
          "bullets": ["Description bullet 1", "Description bullet 2"]
        }
      ],
      "skills": {
        "ai_ml": "Python, ML, Deep Learning",
        "ai_applications": "RAG, LangChain",
        "mlops": "Git, Docker",
        "frameworks": "TensorFlow, PyTorch"
      },
      "research": {
        "title": "Paper Title",
        "doi_url": "https://doi.org/...",
        "doi_text": "DOI: 10.xxx"
      },
      "certifications": [
        {"name": "Cert Name", "issuer": "Issuer", "year": "2024"}
      ]
    }
    ```
    """)
