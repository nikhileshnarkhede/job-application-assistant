"""
LaTeX Resume Generator Tool

Generates PDF resumes from candidate data using LaTeX templates.

Usage:
    from mcp_server.tools.latex_generator import generate_resume_pdf

    # Generate from candidate data
    pdf_path = generate_resume_pdf(output_dir="./applications/company_123")

    # Generate from custom data
    pdf_path = generate_resume_pdf(data=custom_data, output_dir="./output")
"""

import json
import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, BaseLoader


# ============================================================================
# PATHS
# ============================================================================

def get_template_path() -> Path:
    """Get path to LaTeX template."""
    # Try multiple locations
    possible_paths = [
        Path(__file__).parent.parent.parent / "files" / "resume_template.tex",
        Path("./files/resume_template.tex"),
        Path(__file__).parent / "resume_template.tex",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    raise FileNotFoundError("LaTeX resume template not found")


def get_candidate_data_path() -> Path:
    """Get path to candidate data JSON."""
    data_path = os.getenv("DATA_PATH", "./data")
    return Path(data_path) / "candidate_experience.json"


# ============================================================================
# LATEX ESCAPING
# ============================================================================

def escape_latex(text: str) -> str:
    """
    Escape special LaTeX characters in text.
    
    Args:
        text: Raw text string
    
    Returns:
        LaTeX-safe string
    """
    if not isinstance(text, str):
        return str(text)
    
    # Characters that need escaping in LaTeX
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    
    # Don't escape if already escaped or is a LaTeX command
    for char, replacement in replacements.items():
        # Skip if already escaped
        text = text.replace('\\' + char, '<<ESCAPED_' + char + '>>')
        text = text.replace(char, replacement)
        text = text.replace('<<ESCAPED_' + char + '>>', '\\' + char)
    
    return text


def escape_latex_in_data(data: Any) -> Any:
    """
    Recursively escape LaTeX characters in data structure.
    
    Args:
        data: Dict, list, or string
    
    Returns:
        Data with escaped strings
    """
    if isinstance(data, str):
        return escape_latex(data)
    elif isinstance(data, dict):
        return {k: escape_latex_in_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [escape_latex_in_data(item) for item in data]
    else:
        return data


# ============================================================================
# TEMPLATE RENDERING
# ============================================================================

def load_template(template_path: Optional[Path] = None) -> str:
    """Load LaTeX template content."""
    path = template_path or get_template_path()
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def load_candidate_data() -> Dict[str, Any]:
    """Load candidate data from JSON file."""
    path = get_candidate_data_path()
    
    if not path.exists():
        raise FileNotFoundError(f"Candidate data file not found: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def render_latex(template_str: str, data: Dict[str, Any]) -> str:
    """
    Render LaTeX template with data using Jinja2.
    
    Uses custom delimiters to avoid LaTeX conflicts:
    - [[ variable ]] for variables
    - [% block %] for control structures
    
    Args:
        template_str: LaTeX template with Jinja2 placeholders
        data: Resume data dictionary
    
    Returns:
        Rendered LaTeX string
    """
    env = Environment(
        loader=BaseLoader(),
        block_start_string='[%',
        block_end_string='%]',
        variable_start_string='[[',
        variable_end_string=']]',
        comment_start_string='[#',
        comment_end_string='#]',
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    template = env.from_string(template_str)
    return template.render(**data)


# ============================================================================
# PDF GENERATION
# ============================================================================

def compile_latex_to_pdf(tex_path: Path, output_dir: Path) -> Optional[Path]:
    """
    Compile LaTeX file to PDF using pdflatex.
    
    Args:
        tex_path: Path to .tex file
        output_dir: Directory for output files
    
    Returns:
        Path to generated PDF, or None if compilation failed
    """
    # Check if pdflatex is available
    if not shutil.which('pdflatex'):
        print("  ⚠️ pdflatex not found. Install TeX Live or MiKTeX to generate PDFs.")
        return None
    
    try:
        # Run pdflatex twice for proper reference resolution
        for i in range(2):
            result = subprocess.run(
                [
                    'pdflatex',
                    '-interaction=nonstopmode',
                    '-output-directory', str(output_dir),
                    str(tex_path)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0 and i == 1:
                print(f"  ⚠️ LaTeX compilation warning (may still have generated PDF)")
                # Don't fail - sometimes warnings don't prevent PDF generation
        
        # Check if PDF was generated
        pdf_path = output_dir / (tex_path.stem + '.pdf')
        if pdf_path.exists():
            # Clean up auxiliary files
            for ext in ['.aux', '.log', '.out']:
                aux_file = output_dir / (tex_path.stem + ext)
                if aux_file.exists():
                    aux_file.unlink()
            
            return pdf_path
        else:
            print(f"  ❌ PDF not generated. Check LaTeX errors.")
            return None
            
    except subprocess.TimeoutExpired:
        print("  ❌ LaTeX compilation timed out")
        return None
    except Exception as e:
        print(f"  ❌ LaTeX compilation error: {e}")
        return None


# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def generate_resume_tex(
    data: Optional[Dict[str, Any]] = None,
    template_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    escape_special_chars: bool = False
) -> Path:
    """
    Generate LaTeX resume file from data.
    
    Args:
        data: Resume data (loads from candidate_experience.json if None)
        template_path: Path to template (uses default if None)
        output_path: Output .tex file path
        escape_special_chars: Whether to escape LaTeX special characters
    
    Returns:
        Path to generated .tex file
    """
    # Load data if not provided
    if data is None:
        data = load_candidate_data()
    
    # Escape special characters if requested
    if escape_special_chars:
        data = escape_latex_in_data(data)
    
    # Load template
    template_str = load_template(template_path)
    
    # Render
    rendered = render_latex(template_str, data)
    
    # Determine output path
    if output_path is None:
        output_path = Path("./output_resume.tex")
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered)
    
    print(f"  ✅ LaTeX resume saved: {output_path}")
    return output_path


def generate_resume_pdf(
    data: Optional[Dict[str, Any]] = None,
    template_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    filename: str = "resume"
) -> Optional[Path]:
    """
    Generate PDF resume from data.
    
    Args:
        data: Resume data (loads from candidate_experience.json if None)
        template_path: Path to template (uses default if None)
        output_dir: Output directory for files
        filename: Base filename (without extension)
    
    Returns:
        Path to generated PDF, or None if generation failed
    """
    # Set output directory
    if output_dir is None:
        output_dir = Path("./output")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate .tex file
    tex_path = output_dir / f"{filename}.tex"
    generate_resume_tex(
        data=data,
        template_path=template_path,
        output_path=tex_path,
        escape_special_chars=False  # Template already handles escaping
    )
    
    # Compile to PDF
    pdf_path = compile_latex_to_pdf(tex_path, output_dir)
    
    if pdf_path:
        print(f"  ✅ PDF resume generated: {pdf_path}")
    
    return pdf_path


def generate_resume_from_pipeline_state(
    state: Any,
    output_dir: Path,
    filename: str = "resume"
) -> Optional[Path]:
    """
    Generate PDF resume from pipeline state.
    
    Converts ResumeJSON format to LaTeX template format.
    
    Args:
        state: Pipeline state with resume_json
        output_dir: Output directory
        filename: Base filename
    
    Returns:
        Path to generated PDF
    """
    resume_json = state.resume_json if hasattr(state, 'resume_json') else state.get('resume_json')
    
    if not resume_json:
        print("  ⚠️ No resume_json in state, using candidate data")
        return generate_resume_pdf(output_dir=output_dir, filename=filename)
    
    # Convert ResumeJSON to template format
    data = convert_resume_json_to_template(resume_json)
    
    return generate_resume_pdf(data=data, output_dir=output_dir, filename=filename)


def convert_resume_json_to_template(resume_json: Any) -> Dict[str, Any]:
    """
    Convert ResumeJSON (pipeline format) to LaTeX template format.
    
    Args:
        resume_json: ResumeJSON object or dict
    
    Returns:
        Dict matching template structure
    """
    # Handle both Pydantic model and dict
    if hasattr(resume_json, 'model_dump'):
        rj = resume_json.model_dump()
    elif hasattr(resume_json, 'dict'):
        rj = resume_json.dict()
    else:
        rj = dict(resume_json)
    
    # Build header
    header = rj.get('header', {})
    template_header = {
        "name": header.get('name', ''),
        "location": header.get('location', ''),
        "email": header.get('email', ''),
        "linkedin_url": header.get('linkedin', header.get('linkedin_url', '')),
        "linkedin_text": "LinkedIn",
        "github_url": header.get('github', header.get('github_url', '')),
        "github_text": "GitHub",
        "portfolio_url": header.get('portfolio', header.get('portfolio_url', '')),
        "portfolio_text": "Portfolio"
    }
    
    # Build education
    template_education = []
    for edu in rj.get('education', []):
        template_education.append({
            "institution": edu.get('institution', ''),
            "graduation_date": edu.get('graduation', edu.get('graduation_date', '')),
            "degree": edu.get('degree', ''),
            "location": edu.get('location', '')
        })
    
    # Build experience
    template_experience = []
    for exp in rj.get('experience', []):
        template_experience.append({
            "company": exp.get('company', ''),
            "date_range": exp.get('dates', exp.get('date_range', '')),
            "job_title": exp.get('role', exp.get('job_title', '')),
            "location": exp.get('location', ''),
            "bullets": exp.get('bullets', [])
        })
    
    # Build projects
    template_projects = []
    for proj in rj.get('projects', []):
        template_projects.append({
            "name": proj.get('name', ''),
            "technologies": proj.get('technologies', ''),
            "github_url": proj.get('url', proj.get('github_url', '')),
            "github_text": "GitHub",
            "bullets": proj.get('bullets', [])
        })
    
    # Build skills
    skills = rj.get('skills', {})
    template_skills = {
        "ai_ml": skills.get('AI/ML', skills.get('ai_ml', '')),
        "ai_applications": skills.get('AI Applications', skills.get('ai_applications', '')),
        "mlops": skills.get('MLOps & Tools', skills.get('mlops', '')),
        "frameworks": skills.get('Frameworks', skills.get('frameworks', ''))
    }
    
    # Build research (from publications)
    publications = rj.get('publications', [])
    template_research = {
        "title": publications[0] if publications else "",
        "doi_url": "",
        "doi_text": ""
    }
    
    return {
        "header": template_header,
        "education": template_education,
        "experience": template_experience,
        "projects": template_projects,
        "skills": template_skills,
        "research": template_research
    }


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate LaTeX/PDF resume')
    parser.add_argument('--data', '-d', help='Path to JSON data file')
    parser.add_argument('--template', '-t', help='Path to LaTeX template')
    parser.add_argument('--output', '-o', default='./output', help='Output directory')
    parser.add_argument('--name', '-n', default='resume', help='Output filename (without extension)')
    parser.add_argument('--tex-only', action='store_true', help='Generate .tex only, skip PDF')
    
    args = parser.parse_args()
    
    # Load custom data if provided
    data = None
    if args.data:
        with open(args.data, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    template_path = Path(args.template) if args.template else None
    output_dir = Path(args.output)
    
    if args.tex_only:
        tex_path = generate_resume_tex(
            data=data,
            template_path=template_path,
            output_path=output_dir / f"{args.name}.tex"
        )
        print(f"\n✅ Generated: {tex_path}")
        print(f"   Compile with: pdflatex {tex_path}")
    else:
        pdf_path = generate_resume_pdf(
            data=data,
            template_path=template_path,
            output_dir=output_dir,
            filename=args.name
        )
        if pdf_path:
            print(f"\n✅ Generated: {pdf_path}")
        else:
            print(f"\n⚠️ PDF generation failed. .tex file may still be available.")
