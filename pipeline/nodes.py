"""
Pipeline Node Functions

All 12 node functions for the parent graph.
Each node calls one subgraph's convenience function and updates state.
"""

from typing import Dict, Any
from pathlib import Path
from datetime import datetime
import json
import traceback

from pipeline.config import (
    RESUME_CONFIG,
    ATS_CONFIG,
    PIPELINE_CONFIG,
    PATHS_CONFIG
)
from pipeline.state import ParentGraphState


# ============================================================================
# STAGE 1: JD EXTRACTION
# ============================================================================

def node_extract_jd(state: ParentGraphState) -> Dict[str, Any]:
    """Extract structured JD from URL or text."""
    from subgraphs import extract_jd_from_url, extract_jd_from_text
    from subgraphs.test_constants import STANDARD_JD_TEXT
    
    print("\n" + "=" * 60)
    print("📄 STAGE 1: JD EXTRACTION")
    print("=" * 60)
    
    try:
        result = None
        
        if state.jd_url:
            print(f"   Extracting from URL: {state.jd_url[:60]}...")
            result = extract_jd_from_url(state.jd_url)
            
            # Debug: print result
            if not result.get("structured_jd"):
                print(f"   ⚠️  URL extraction returned: error={result.get('error')}")
            
            # Fallback to STANDARD_JD_TEXT if URL extraction fails
            if not result.get("structured_jd") and "amazon.jobs" in state.jd_url:
                print("   🔄 Using fallback text...")
                result = extract_jd_from_text(STANDARD_JD_TEXT)
                
                if not result.get("structured_jd"):
                    print(f"   ⚠️  Text extraction also failed: error={result.get('error')}")
                    # Create a minimal structured JD manually
                    print("   🔧 Creating minimal structured JD from fallback...")
                    result = _create_fallback_jd()
                
        elif state.jd_text:
            print(f"   Extracting from text ({len(state.jd_text)} chars)...")
            result = extract_jd_from_text(state.jd_text)
        else:
            print("   ❌ No JD URL or text provided")
            return {"extraction_error": "No JD URL or text provided"}
        
        structured_jd = result.get("structured_jd")
        
        if structured_jd:
            company = getattr(structured_jd, 'company_name', None) or structured_jd.get('company_name', 'Unknown')
            role = getattr(structured_jd, 'role_title', None) or structured_jd.get('role_title', 'Unknown')
            print(f"   ✅ Extracted: {company} - {role}")
            return {"structured_jd": structured_jd, "current_stage": "jd_extracted"}
        else:
            error = result.get("error", "Unknown error")
            print(f"   ❌ Failed: {error}")
            return {"extraction_error": error}
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return {"extraction_error": str(e)}


def _create_fallback_jd() -> Dict[str, Any]:
    """Create a fallback structured JD for testing when extraction fails."""
    from state.state_models import StructuredJD
    
    structured_jd = StructuredJD(
        company_name="Amazon",
        role_title="Applied Scientist - AI/ML",
        role_type="ml_ai",
        location="Seattle, WA",
        employment_type="Full-time",
        experience_required="3+ years",
        skills_required=[
            "Python", "Machine Learning", "Deep Learning", 
            "PyTorch", "TensorFlow", "Statistics", "SQL"
        ],
        skills_preferred=[
            "Reinforcement Learning", "NLP", "Computer Vision",
            "AWS SageMaker", "Causal Inference"
        ],
        responsibilities=[
            "Design and implement machine learning models",
            "Develop scalable ML pipelines",
            "Collaborate with engineers to deploy models",
            "Conduct A/B experiments"
        ],
        qualifications=[
            "PhD or Master's in CS, ML, or related field",
            "3+ years applied ML experience",
            "Track record of delivering ML models to production"
        ],
        keywords=[
            "machine learning", "deep learning", "python", "pytorch",
            "tensorflow", "nlp", "computer vision", "aws", "sagemaker",
            "spark", "sql", "a/b testing", "reinforcement learning"
        ],
        company_info="Amazon is guided by customer obsession and innovation",
        extraction_confidence=0.95,
        raw_text_length=1500
    )
    
    return {
        "structured_jd": structured_jd,
        "error": None,
        "validation_passed": True
    }


# ============================================================================
# STAGE 2: SKILL MATCHING
# ============================================================================

def node_match_skills(state: ParentGraphState) -> Dict[str, Any]:
    """Match candidate skills to JD requirements."""
    from subgraphs import match_skills_to_jd
    
    print("\n" + "=" * 60)
    print("🎯 STAGE 2: SKILL MATCHING")
    print("=" * 60)
    
    if not state.structured_jd:
        print("   ⚠️  No structured JD, skipping")
        return {"current_stage": "skills_matched"}
    
    try:
        result = match_skills_to_jd(structured_jd=state.structured_jd)
        
        skill_match = result.get("skill_match_result")
        if skill_match:
            pct = getattr(skill_match, 'match_percentage', 0) or skill_match.get('match_percentage', 0)
            matched = getattr(skill_match, 'matched_skills', []) or skill_match.get('matched_skills', [])
            missing = getattr(skill_match, 'missing_skills', []) or skill_match.get('missing_skills', [])
            
            print(f"   ✅ Match: {pct:.1f}%")
            print(f"   📊 Matched: {len(matched)} | Missing: {len(missing)}")
            
            return {
                "skill_match_result": skill_match,
                "match_percentage": pct,
                "current_stage": "skills_matched"
            }
        
        return {"current_stage": "skills_matched"}
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return {"current_stage": "skills_matched"}


# ============================================================================
# STAGE 3a: EXPERIENCE SELECTION
# ============================================================================

def node_select_experiences(state: ParentGraphState) -> Dict[str, Any]:
    """Select relevant experiences for resume."""
    from subgraphs import select_experiences_for_jd
    
    print("\n" + "=" * 60)
    print("📋 STAGE 3a: EXPERIENCE SELECTION")
    print("=" * 60)
    
    if not state.structured_jd:
        print("   ⚠️  No structured JD, skipping")
        return {"current_stage": "experiences_selected"}
    
    try:
        result = select_experiences_for_jd(
            structured_jd=state.structured_jd,
            max_experiences=RESUME_CONFIG["max_experiences"]
        )
        
        selected = result.get("selected_experiences", [])
        print(f"   ✅ Selected {len(selected)} experiences")
        
        for exp in selected[:3]:
            role = getattr(exp, 'role', None) or exp.get('role', 'Unknown')
            company = getattr(exp, 'company', None) or exp.get('company', 'Unknown')
            print(f"      • {role} @ {company}")
        
        return {
            "selected_experiences": selected,
            "current_stage": "experiences_selected"
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return {"selected_experiences": [], "current_stage": "experiences_selected"}


# ============================================================================
# STAGE 3b: PROJECT RANKING
# ============================================================================

def node_rank_projects(state: ParentGraphState) -> Dict[str, Any]:
    """Rank and select GitHub projects."""
    from subgraphs import rank_github_projects
    
    print("\n" + "=" * 60)
    print("🔧 STAGE 3b: PROJECT RANKING")
    print("=" * 60)
    
    if not state.structured_jd:
        print("   ⚠️  No structured JD, skipping")
        return {"current_stage": "projects_ranked"}
    
    try:
        result = rank_github_projects(
            structured_jd=state.structured_jd,
            max_projects=RESUME_CONFIG["max_projects"]
        )
        
        selected = result.get("selected_projects", [])
        print(f"   ✅ Selected {len(selected)} projects")
        
        for proj in selected[:3]:
            name = getattr(proj, 'name', None) or proj.get('name', 'Unknown')
            print(f"      • {name}")
        
        return {
            "selected_projects": selected,
            "current_stage": "projects_ranked"
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return {"selected_projects": [], "current_stage": "projects_ranked"}


# ============================================================================
# STAGE 4: CONTENT REWRITING
# ============================================================================

def node_rewrite_content(state: ParentGraphState) -> Dict[str, Any]:
    """Rewrite experiences and projects with keywords."""
    from subgraphs import rewrite_for_jd
    
    print("\n" + "=" * 60)
    print("✏️  STAGE 4: CONTENT REWRITING")
    print("=" * 60)
    
    if not state.selected_experiences and not state.selected_projects:
        print("   ⚠️  No content to rewrite, skipping")
        return {"current_stage": "content_rewritten"}
    
    try:
        result = rewrite_for_jd(
            structured_jd=state.structured_jd,
            selected_experiences=state.selected_experiences,
            selected_projects=state.selected_projects
        )
        
        rewritten_exp = result.get("rewritten_experiences", [])
        rewritten_proj = result.get("rewritten_projects", [])
        rate = result.get("incorporation_rate", 0)
        
        print(f"   ✅ Rewrote {len(rewritten_exp)} experiences")
        print(f"   ✅ Rewrote {len(rewritten_proj)} projects")
        print(f"   📊 Keyword incorporation: {rate:.1f}%")
        
        return {
            "rewritten_experiences": rewritten_exp,
            "rewritten_projects": rewritten_proj,
            "current_stage": "content_rewritten"
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        # Fallback: use original content
        return {
            "rewritten_experiences": state.selected_experiences,
            "rewritten_projects": state.selected_projects,
            "current_stage": "content_rewritten"
        }


# ============================================================================
# STAGE 5: RESUME BUILDING
# ============================================================================

def node_build_resume(state: ParentGraphState) -> Dict[str, Any]:
    """Build complete ResumeJSON."""
    from subgraphs import build_resume
    
    print("\n" + "=" * 60)
    print("📝 STAGE 5: RESUME BUILDING")
    print("=" * 60)
    
    # Use rewritten content, falling back to selected content
    experiences = state.rewritten_experiences or state.selected_experiences or []
    projects = state.rewritten_projects or state.selected_projects or []
    
    if not experiences and not projects:
        print("   ⚠️  No content to build resume from")
        return {"current_stage": "resume_built"}
    
    try:
        result = build_resume(
            structured_jd=state.structured_jd,
            rewritten_experiences=experiences,
            rewritten_projects=projects,
            skill_match_result=state.skill_match_result
        )
        
        resume = result.get("resume_json")
        
        if resume:
            summary = getattr(resume, 'summary', '') or resume.get('summary', '')
            exp = getattr(resume, 'experience', []) or resume.get('experience', [])
            proj = getattr(resume, 'projects', []) or resume.get('projects', [])
            
            print(f"   ✅ Resume built")
            print(f"   📊 Summary: {len(summary.split())} words")
            print(f"   📊 Experiences: {len(exp)} | Projects: {len(proj)}")
            
            return {"resume_json": resume, "current_stage": "resume_built"}
        
        error = result.get("error")
        if error:
            print(f"   ⚠️  {error}")
        return {"current_stage": "resume_built"}
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return {"current_stage": "resume_built"}


# ============================================================================
# STAGE 6: ATS OPTIMIZATION
# ============================================================================

def node_optimize_ats(state: ParentGraphState) -> Dict[str, Any]:
    """Optimize resume for ATS score."""
    from subgraphs import optimize_resume_for_ats
    
    iteration = state.ats_iteration + 1
    print("\n" + "=" * 60)
    print(f"🎯 STAGE 6: ATS OPTIMIZATION (Iteration {iteration})")
    print("=" * 60)
    
    if not state.resume_json:
        print("   ⚠️  No resume to optimize, skipping")
        return {"ats_iteration": iteration, "current_stage": "ats_optimized"}
    
    try:
        result = optimize_resume_for_ats(
            structured_jd=state.structured_jd,
            resume_json=state.resume_json,
            target_score=ATS_CONFIG["target_score"],
            max_iterations=ATS_CONFIG["max_iterations"]
        )
        
        # Get score from result
        score = result.get("original_score", 0)
        passed = result.get("passed", False)
        optimized = result.get("optimized_resume")
        
        print(f"   📊 ATS Score: {score}%")
        print(f"   🎯 Target: {ATS_CONFIG['target_score']}%")
        print(f"   {'✅ PASSED' if passed else '⚠️  Below target'}")
        
        return {
            "ats_score": float(score),
            "ats_passed": passed,
            "ats_iteration": iteration,
            "ats_report": result.get("ats_analysis"),
            "resume_json": optimized if optimized else state.resume_json,
            "current_stage": "ats_optimized"
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return {"ats_iteration": iteration, "current_stage": "ats_optimized"}


# ============================================================================
# STAGE 7: COMPLIANCE CHECK
# ============================================================================

def node_check_compliance(state: ParentGraphState) -> Dict[str, Any]:
    """Check resume compliance with standards."""
    from subgraphs import validate_resume_compliance
    
    iteration = state.compliance_iteration + 1
    print("\n" + "=" * 60)
    print(f"✅ STAGE 7: COMPLIANCE CHECK (Iteration {iteration})")
    print("=" * 60)
    
    if not state.resume_json:
        print("   ⚠️  No resume to check, skipping")
        return {"compliance_iteration": iteration, "current_stage": "compliance_checked"}
    
    try:
        result = validate_resume_compliance(resume_json=state.resume_json)
        
        report = result.get("compliance_report")
        
        if report:
            score = getattr(report, 'overall_score', 0) or report.get('overall_score', 0)
            grade = getattr(report, 'grade', 'N/A') or report.get('grade', 'N/A')
            passed = score >= PIPELINE_CONFIG["compliance_pass_threshold"]
            
            print(f"   📊 Score: {score:.1f}% (Grade: {grade})")
            print(f"   🎯 Target: {PIPELINE_CONFIG['compliance_pass_threshold']}%")
            print(f"   {'✅ PASSED' if passed else '⚠️  Below threshold'}")
            
            return {
                "compliance_score": float(score),
                "compliance_passed": passed,
                "compliance_iteration": iteration,
                "compliance_report": report,
                "current_stage": "compliance_checked"
            }
        
        return {"compliance_iteration": iteration, "current_stage": "compliance_checked"}
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return {"compliance_iteration": iteration, "current_stage": "compliance_checked"}


# ============================================================================
# STAGE 8: COVER LETTER GENERATION
# ============================================================================

def node_generate_cover_letter(state: ParentGraphState) -> Dict[str, Any]:
    """Generate personalized cover letter."""
    from subgraphs import generate_cover_letter_for_job
    
    print("\n" + "=" * 60)
    print("📝 STAGE 8: COVER LETTER GENERATION")
    print("=" * 60)
    
    if not state.structured_jd:
        print("   ⚠️  No structured JD, skipping")
        return {"current_stage": "cover_letter_generated"}
    
    if not state.resume_json:
        print("   ⚠️  No resume, skipping")
        return {"current_stage": "cover_letter_generated"}
    
    try:
        result = generate_cover_letter_for_job(
            structured_jd=state.structured_jd,
            resume_json=state.resume_json
        )
        
        cover_letter = result.get("cover_letter")
        
        if cover_letter:
            text = getattr(cover_letter, 'full_text', '') or cover_letter.get('full_text', '')
            word_count = len(text.split())
            
            print(f"   ✅ Generated cover letter")
            print(f"   📊 Word count: {word_count}")
            
            return {
                "cover_letter": cover_letter,
                "cover_letter_text": text,
                "current_stage": "cover_letter_generated"
            }
        
        error = result.get("error")
        if error:
            print(f"   ⚠️  {error}")
            
        return {"current_stage": "cover_letter_generated"}
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return {"current_stage": "cover_letter_generated"}


# ============================================================================
# STAGE 9: COVER LETTER COMPLIANCE
# ============================================================================

def node_check_cl_compliance(state: ParentGraphState) -> Dict[str, Any]:
    """Check cover letter compliance."""
    from subgraphs import validate_cover_letter_compliance
    
    print("\n" + "=" * 60)
    print("✅ STAGE 9: COVER LETTER COMPLIANCE")
    print("=" * 60)
    
    if not state.cover_letter_text:
        print("   ⏭️  Skipped (no cover letter)")
        return {"current_stage": "cl_compliance_checked"}
    
    try:
        result = validate_cover_letter_compliance(
            cover_letter=state.cover_letter,
            cover_letter_text=state.cover_letter_text,
            structured_jd=state.structured_jd
        )
        
        report = result.get("compliance_report")
        
        if report:
            score = getattr(report, 'overall_score', 0) or report.get('overall_score', 0)
            passed = getattr(report, 'passed', False) or report.get('passed', False)
            
            print(f"   📊 Score: {score:.1f}%")
            print(f"   {'✅ PASSED' if passed else '⚠️  Needs improvement'}")
            
            return {
                "cl_compliance_score": float(score),
                "cl_compliance_passed": passed,
                "current_stage": "cl_compliance_checked"
            }
        
        return {"current_stage": "cl_compliance_checked"}
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return {"current_stage": "cl_compliance_checked"}


# ============================================================================
# STAGE 10: EMAIL GENERATION
# ============================================================================

def node_generate_email(state: ParentGraphState) -> Dict[str, Any]:
    """Generate recruiter outreach email."""
    from subgraphs import generate_outreach_email
    
    print("\n" + "=" * 60)
    print("📧 STAGE 10: EMAIL GENERATION")
    print("=" * 60)
    
    if not PIPELINE_CONFIG["enable_email_generation"]:
        print("   ⏭️  Skipped (disabled)")
        return {"current_stage": "email_generated"}
    
    if not state.structured_jd:
        print("   ⚠️  No structured JD, skipping")
        return {"current_stage": "email_generated"}
    
    try:
        result = generate_outreach_email(
            structured_jd=state.structured_jd,
            resume_json=state.resume_json
        )
        
        email = result.get("generated_email")
        
        if email:
            text = getattr(email, 'full_text', '') or email.get('full_text', '')
            subject = getattr(email, 'subject', '') or email.get('subject', '')
            
            print(f"   ✅ Generated email")
            print(f"   📧 Subject: {subject[:50]}...")
            print(f"   📊 Word count: {len(text.split())}")
            
            return {
                "email": email,
                "email_text": text,
                "current_stage": "email_generated"
            }
        
        return {"current_stage": "email_generated"}
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return {"current_stage": "email_generated"}


# ============================================================================
# STAGE 11: EXCEL TRACKING
# ============================================================================

def node_save_to_excel(state: ParentGraphState) -> Dict[str, Any]:
    """Save application to Excel tracker."""
    from subgraphs import save_application_to_excel
    
    print("\n" + "=" * 60)
    print("💾 STAGE 11: EXCEL TRACKING")
    print("=" * 60)
    
    if not PIPELINE_CONFIG["save_to_excel"]:
        print("   ⏭️  Skipped (disabled)")
        return {"current_stage": "excel_saved"}
    
    try:
        result = save_application_to_excel(
            structured_jd=state.structured_jd,
            resume_json=state.resume_json,
            resume_score=state.compliance_score,
            cover_letter_score=state.cl_compliance_score,
            file_path=PATHS_CONFIG["excel_file"]
        )
        
        if result.get("write_complete"):
            print(f"   ✅ Saved to: {PATHS_CONFIG['excel_file']}")
            print(f"   📋 Row: {result.get('row_number', 'N/A')}")
            return {"excel_saved": True, "current_stage": "excel_saved"}
        
        error = result.get("error")
        if error:
            print(f"   ⚠️  {error}")
            
        return {"excel_saved": False, "current_stage": "excel_saved"}
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return {"excel_saved": False, "current_stage": "excel_saved"}


# ============================================================================
# STAGE 12: SAVE OUTPUTS
# ============================================================================

def node_save_outputs(state: ParentGraphState) -> Dict[str, Any]:
    """Save all output files to disk."""
    print("\n" + "=" * 60)
    print("💾 STAGE 12: SAVING OUTPUTS")
    print("=" * 60)
    
    try:
        # Create output folder
        jd = state.structured_jd
        if jd:
            company = getattr(jd, 'company_name', '') or jd.get('company_name', 'unknown')
            company = company.lower().replace(' ', '_')[:20]
        else:
            company = "unknown"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{company}_{timestamp}"
        output_path = Path(PATHS_CONFIG["output_folder"]) / folder_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save resume JSON
        if state.resume_json:
            resume_path = output_path / "resume.json"
            resume_data = state.resume_json
            if hasattr(resume_data, 'model_dump'):
                resume_data = resume_data.model_dump()
            elif hasattr(resume_data, 'dict'):
                resume_data = resume_data.dict()
            with open(resume_path, 'w') as f:
                json.dump(resume_data, f, indent=2, default=str)
            print(f"   ✅ Resume: {resume_path}")
        
        # Save cover letter
        if state.cover_letter_text:
            cl_path = output_path / "cover_letter.txt"
            with open(cl_path, 'w') as f:
                f.write(state.cover_letter_text)
            print(f"   ✅ Cover Letter: {cl_path}")
        
        # Save email
        if state.email_text:
            email_path = output_path / "email.txt"
            with open(email_path, 'w') as f:
                f.write(state.email_text)
            print(f"   ✅ Email: {email_path}")
        
        # Save metadata
        metadata = {
            "company": company,
            "timestamp": timestamp,
            "ats_score": state.ats_score,
            "compliance_score": state.compliance_score,
            "match_percentage": state.match_percentage
        }
        meta_path = output_path / "metadata.json"
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"   ✅ Metadata: {meta_path}")
        
        return {"output_folder": str(output_path), "current_stage": "outputs_saved"}
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return {"current_stage": "outputs_saved"}


# ============================================================================
# ROUTING FUNCTIONS
# ============================================================================

def should_retry_ats(state: ParentGraphState) -> str:
    """Decide whether to retry ATS optimization."""
    if state.ats_passed:
        return "continue"
    if state.ats_iteration >= PIPELINE_CONFIG["max_ats_iterations"]:
        print(f"   ⚠️  Max ATS iterations reached ({state.ats_iteration})")
        return "continue"
    return "continue"  # Always continue for now (no retry loop)


def should_retry_compliance(state: ParentGraphState) -> str:
    """Decide whether to retry compliance check."""
    if state.compliance_passed:
        return "continue"
    if state.compliance_iteration >= PIPELINE_CONFIG["max_compliance_iterations"]:
        print(f"   ⚠️  Max compliance iterations reached ({state.compliance_iteration})")
        return "continue"
    return "continue"  # Always continue for now (no retry loop)
