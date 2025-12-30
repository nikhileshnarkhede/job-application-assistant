"""
Candidate Profile Page - Job Application Assistant

Allows users to edit their candidate information.
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
    # Update timestamp
    data["candidate_info"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    
    # Ensure directory exists
    CANDIDATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CANDIDATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return True


def get_empty_template():
    """Return empty candidate template."""
    return {
        "candidate_info": {
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "total_experiences": 0,
            "years_of_experience": "0"
        },
        "header": {
            "name": "",
            "title": "",
            "phone": "",
            "email": "",
            "location": "",
            "linkedin": "",
            "github": ""
        },
        "professional_summary": {
            "default": ""
        },
        "education": [],
        "certifications": [],
        "skills": {},
        "experiences": [],
        "publications": []
    }


# Initialize session state
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = load_candidate_data()

data = st.session_state.candidate_data

# Page header
st.title("👤 Candidate Profile")
st.markdown("Edit your personal information, experiences, skills, and education")

# Last updated info
if data.get("candidate_info", {}).get("last_updated"):
    st.caption(f"📅 Last updated: {data['candidate_info']['last_updated']}")

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 Basic Info", 
    "💼 Experience", 
    "🎓 Education", 
    "🔧 Skills",
    "📝 Summary",
    "📚 Publications"
])

# ============================================================================
# TAB 1: BASIC INFO
# ============================================================================
with tab1:
    st.markdown("### Personal Information")
    
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
            placeholder="City, State/Country",
            key="location"
        )
    
    with col2:
        data["header"]["title"] = st.text_input(
            "Professional Title",
            value=data.get("header", {}).get("title", ""),
            placeholder="e.g., Machine Learning Engineer | Data Scientist",
            key="title"
        )
        
        data["header"]["linkedin"] = st.text_input(
            "LinkedIn URL",
            value=data.get("header", {}).get("linkedin", ""),
            placeholder="linkedin.com/in/yourprofile",
            key="linkedin"
        )
        
        data["header"]["github"] = st.text_input(
            "GitHub URL",
            value=data.get("header", {}).get("github", ""),
            placeholder="github.com/yourusername",
            key="github"
        )
        
        # Years of experience
        data["candidate_info"]["years_of_experience"] = st.text_input(
            "Years of Experience",
            value=data.get("candidate_info", {}).get("years_of_experience", ""),
            placeholder="e.g., 3+, 5-7",
            key="years_exp"
        )

# ============================================================================
# TAB 2: EXPERIENCE
# ============================================================================
with tab2:
    st.markdown("### Work Experience")
    st.caption("Add your work experiences. Most recent first.")
    
    experiences = data.get("experiences", [])
    
    # Add new experience button
    if st.button("➕ Add New Experience", key="add_exp"):
        new_exp = {
            "id": len(experiences) + 1,
            "role": "",
            "role_full": "",
            "company": "",
            "employment_type": "Full-time",
            "dates": {"start": "", "end": "", "duration_months": 0},
            "location": {"city": "", "state": "", "country": "", "type": "On-site"},
            "scope": "",
            "bullets_flat": [],
            "skills": [],
            "keywords": [],
            "relevance_tags": []
        }
        experiences.insert(0, new_exp)
        data["experiences"] = experiences
        st.rerun()
    
    # Display existing experiences
    for i, exp in enumerate(experiences):
        with st.expander(
            f"**{exp.get('role', 'New Role')}** at {exp.get('company', 'Company')} "
            f"({exp.get('dates', {}).get('start', '')} - {exp.get('dates', {}).get('end', '')})",
            expanded=(i == 0)
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                exp["role"] = st.text_input(
                    "Role Title *",
                    value=exp.get("role", ""),
                    key=f"exp_role_{i}"
                )
                
                exp["company"] = st.text_input(
                    "Company *",
                    value=exp.get("company", ""),
                    key=f"exp_company_{i}"
                )
                
                exp["employment_type"] = st.selectbox(
                    "Employment Type",
                    options=["Full-time", "Part-time", "Contract", "Internship", "Freelance", "Research Position"],
                    index=["Full-time", "Part-time", "Contract", "Internship", "Freelance", "Research Position"].index(
                        exp.get("employment_type", "Full-time")
                    ) if exp.get("employment_type") in ["Full-time", "Part-time", "Contract", "Internship", "Freelance", "Research Position"] else 0,
                    key=f"exp_type_{i}"
                )
            
            with col2:
                # Dates
                date_col1, date_col2 = st.columns(2)
                with date_col1:
                    if "dates" not in exp:
                        exp["dates"] = {}
                    exp["dates"]["start"] = st.text_input(
                        "Start Date",
                        value=exp.get("dates", {}).get("start", ""),
                        placeholder="e.g., Jan 2023",
                        key=f"exp_start_{i}"
                    )
                with date_col2:
                    exp["dates"]["end"] = st.text_input(
                        "End Date",
                        value=exp.get("dates", {}).get("end", ""),
                        placeholder="e.g., Present",
                        key=f"exp_end_{i}"
                    )
                
                # Location
                if "location" not in exp:
                    exp["location"] = {}
                loc_col1, loc_col2 = st.columns(2)
                with loc_col1:
                    exp["location"]["city"] = st.text_input(
                        "City",
                        value=exp.get("location", {}).get("city", ""),
                        key=f"exp_city_{i}"
                    )
                with loc_col2:
                    exp["location"]["type"] = st.selectbox(
                        "Work Type",
                        options=["On-site", "Remote", "Hybrid"],
                        index=["On-site", "Remote", "Hybrid"].index(
                            exp.get("location", {}).get("type", "On-site")
                        ) if exp.get("location", {}).get("type") in ["On-site", "Remote", "Hybrid"] else 0,
                        key=f"exp_worktype_{i}"
                    )
            
            # Scope/Description
            exp["scope"] = st.text_area(
                "Role Description",
                value=exp.get("scope", ""),
                height=80,
                key=f"exp_scope_{i}"
            )
            
            # Bullets
            st.markdown("**Bullet Points** (one per line)")
            bullets_text = "\n".join(exp.get("bullets_flat", []))
            new_bullets = st.text_area(
                "Bullets",
                value=bullets_text,
                height=150,
                key=f"exp_bullets_{i}",
                label_visibility="collapsed"
            )
            exp["bullets_flat"] = [b.strip() for b in new_bullets.split("\n") if b.strip()]
            
            # Skills used
            skills_text = ", ".join(exp.get("skills", []))
            new_skills = st.text_input(
                "Skills Used (comma-separated)",
                value=skills_text,
                key=f"exp_skills_{i}"
            )
            exp["skills"] = [s.strip() for s in new_skills.split(",") if s.strip()]
            
            # Delete button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col3:
                if st.button("🗑️ Delete Experience", key=f"del_exp_{i}"):
                    experiences.pop(i)
                    data["experiences"] = experiences
                    st.rerun()
    
    # Update experience count
    data["candidate_info"]["total_experiences"] = len(experiences)

# ============================================================================
# TAB 3: EDUCATION
# ============================================================================
with tab3:
    st.markdown("### Education")
    
    education = data.get("education", [])
    
    if st.button("➕ Add Education", key="add_edu"):
        new_edu = {
            "institution": "",
            "location": "",
            "degree": "",
            "field": "",
            "graduation": "",
            "gpa": "",
            "coursework": [],
            "highlights": []
        }
        education.insert(0, new_edu)
        data["education"] = education
        st.rerun()
    
    for i, edu in enumerate(education):
        with st.expander(
            f"**{edu.get('degree', 'Degree')}** - {edu.get('institution', 'Institution')}",
            expanded=(i == 0)
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                edu["institution"] = st.text_input(
                    "Institution *",
                    value=edu.get("institution", ""),
                    key=f"edu_inst_{i}"
                )
                
                edu["degree"] = st.text_input(
                    "Degree *",
                    value=edu.get("degree", ""),
                    placeholder="e.g., Master of Science",
                    key=f"edu_degree_{i}"
                )
                
                edu["field"] = st.text_input(
                    "Field of Study *",
                    value=edu.get("field", ""),
                    placeholder="e.g., Computer Science",
                    key=f"edu_field_{i}"
                )
            
            with col2:
                edu["location"] = st.text_input(
                    "Location",
                    value=edu.get("location", ""),
                    key=f"edu_loc_{i}"
                )
                
                edu["graduation"] = st.text_input(
                    "Graduation Date",
                    value=edu.get("graduation", ""),
                    placeholder="e.g., May 2024",
                    key=f"edu_grad_{i}"
                )
                
                edu["gpa"] = st.text_input(
                    "GPA",
                    value=edu.get("gpa", ""),
                    placeholder="e.g., 3.8/4.0",
                    key=f"edu_gpa_{i}"
                )
            
            # Coursework
            coursework_text = ", ".join(edu.get("coursework", []))
            new_coursework = st.text_input(
                "Relevant Coursework (comma-separated)",
                value=coursework_text,
                key=f"edu_courses_{i}"
            )
            edu["coursework"] = [c.strip() for c in new_coursework.split(",") if c.strip()]
            
            # Highlights
            highlights_text = ", ".join(edu.get("highlights", []))
            new_highlights = st.text_input(
                "Highlights/Achievements (comma-separated)",
                value=highlights_text,
                key=f"edu_highlights_{i}"
            )
            edu["highlights"] = [h.strip() for h in new_highlights.split(",") if h.strip()]
            
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
    st.caption("Organize your skills by category")
    
    skills = data.get("skills", {})
    
    # Add new category
    col1, col2 = st.columns([3, 1])
    with col1:
        new_category = st.text_input(
            "New Category Name",
            placeholder="e.g., Cloud Platforms",
            key="new_skill_cat"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Category") and new_category:
            skills[new_category] = ""
            data["skills"] = skills
            st.rerun()
    
    # Display existing categories
    st.markdown("---")
    
    categories_to_delete = []
    for category, skill_list in skills.items():
        col1, col2 = st.columns([4, 1])
        with col1:
            skills[category] = st.text_input(
                f"**{category}**",
                value=skill_list if isinstance(skill_list, str) else ", ".join(skill_list),
                key=f"skill_{category}",
                help="Enter skills separated by commas"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_skill_{category}"):
                categories_to_delete.append(category)
    
    # Delete marked categories
    for cat in categories_to_delete:
        del skills[cat]
        data["skills"] = skills
        st.rerun()
    
    # Update all_skills_flat
    all_skills = []
    for skill_str in skills.values():
        if isinstance(skill_str, str):
            all_skills.extend([s.strip() for s in skill_str.split(",") if s.strip()])
        elif isinstance(skill_str, list):
            all_skills.extend(skill_str)
    data["all_skills_flat"] = list(set(all_skills))

# ============================================================================
# TAB 5: PROFESSIONAL SUMMARY
# ============================================================================
with tab5:
    st.markdown("### Professional Summary")
    st.caption("Create different versions of your summary for different roles")
    
    summaries = data.get("professional_summary", {"default": ""})
    
    # Default summary
    summaries["default"] = st.text_area(
        "Default Summary *",
        value=summaries.get("default", ""),
        height=150,
        key="summary_default",
        help="This is your main professional summary"
    )
    
    st.markdown("---")
    st.markdown("#### Role-Specific Summaries (Optional)")
    
    # Add new variant
    col1, col2 = st.columns([3, 1])
    with col1:
        new_variant = st.text_input(
            "New Variant Name",
            placeholder="e.g., data_engineer, frontend_developer",
            key="new_summary_variant"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Variant") and new_variant:
            summaries[new_variant] = summaries.get("default", "")
            data["professional_summary"] = summaries
            st.rerun()
    
    # Display variants
    for variant, text in summaries.items():
        if variant != "default":
            col1, col2 = st.columns([5, 1])
            with col1:
                summaries[variant] = st.text_area(
                    f"**{variant}**",
                    value=text,
                    height=100,
                    key=f"summary_{variant}"
                )
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_summary_{variant}"):
                    del summaries[variant]
                    data["professional_summary"] = summaries
                    st.rerun()
    
    data["professional_summary"] = summaries

# ============================================================================
# TAB 6: PUBLICATIONS & CERTIFICATIONS
# ============================================================================
with tab6:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Publications")
        
        publications = data.get("publications", [])
        
        if st.button("➕ Add Publication", key="add_pub"):
            publications.append({
                "title": "",
                "journal": "",
                "year": "",
                "authors": [],
                "type": "Peer-reviewed"
            })
            data["publications"] = publications
            st.rerun()
        
        for i, pub in enumerate(publications):
            with st.expander(pub.get("title", "New Publication") or "New Publication"):
                pub["title"] = st.text_input(
                    "Title *",
                    value=pub.get("title", ""),
                    key=f"pub_title_{i}"
                )
                pub["journal"] = st.text_input(
                    "Journal/Conference",
                    value=pub.get("journal", ""),
                    key=f"pub_journal_{i}"
                )
                pub["year"] = st.text_input(
                    "Year",
                    value=str(pub.get("year", "")),
                    key=f"pub_year_{i}"
                )
                authors_text = ", ".join(pub.get("authors", []))
                new_authors = st.text_input(
                    "Authors (comma-separated)",
                    value=authors_text,
                    key=f"pub_authors_{i}"
                )
                pub["authors"] = [a.strip() for a in new_authors.split(",") if a.strip()]
                
                if st.button("🗑️ Delete", key=f"del_pub_{i}"):
                    publications.pop(i)
                    data["publications"] = publications
                    st.rerun()
    
    with col2:
        st.markdown("### Certifications")
        
        certifications = data.get("certifications", [])
        
        if st.button("➕ Add Certification", key="add_cert"):
            certifications.append({
                "name": "",
                "issuer": "",
                "year": "",
                "credential_id": ""
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
                cert["credential_id"] = st.text_input(
                    "Credential ID",
                    value=cert.get("credential_id", "") or "",
                    key=f"cert_id_{i}"
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
    if st.button("📥 Download JSON", use_container_width=True):
        st.download_button(
            label="⬇️ Download",
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
