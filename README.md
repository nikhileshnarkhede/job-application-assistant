# Job Application Assistant


https://github.com/user-attachments/assets/f48ee384-1c78-4594-89c7-b363b2de36f7


An AI-powered job application automation system built with **LangGraph**, **LLM**, and **GitHub API** integration.

## 🎯 Features

- **JD Extraction**: Parse job descriptions from URLs or text using LLM
- **Skill Matching**: Automated skill gap analysis against JD requirements
- **GitHub Project Ranking**: Dynamically fetch and rank GitHub projects by JD relevance
- **Experience Selection**: Select most relevant work experiences
- **Content Rewriting**: ATS-optimized bullet points with action verbs and metrics
- **Resume Generation**: Structured JSON output with JD-tailored summary
- **ATS Optimization**: Iterative loop until score ≥ 95%
- **Resource Compliance**: Validate against checklists and rubrics
- **Cover Letter Generation**: Personalized cover letters with company research
- **Email Generation**: Recruiter outreach emails (cold, follow-up, thank-you)
- **Excel Tracking**: Automatic job application tracking spreadsheet
- **Checkpointing**: Resume from any stage with SQLite persistence
- **Streamlit GUI**: User-friendly web interface for easy interaction

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PARENT GRAPH PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   START                                                                  │
│     │                                                                    │
│     ▼                                                                    │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐    │
│   │ 1. Extract   │────►│ 2. Match     │────►│ 3a. Select           │    │
│   │    JD        │     │    Skills    │     │     Experiences      │    │
│   └──────────────┘     └──────────────┘     └──────────┬───────────┘    │
│         │                                              │                 │
│         │ [fail]                                       ▼                 │
│         │                               ┌──────────────────────┐         │
│         │                               │ 3b. Rank Projects    │         │
│         │                               │     (GitHub API)     │         │
│         │                               └──────────┬───────────┘         │
│         │                                          │                     │
│         │                                          ▼                     │
│         │                               ┌──────────────────────┐         │
│         │                               │ 4. Rewrite Content   │         │
│         │                               └──────────┬───────────┘         │
│         │                                          │                     │
│         │                                          ▼                     │
│         │                               ┌──────────────────────┐         │
│         │                               │ 5. Build Resume      │         │
│         │                               └──────────┬───────────┘         │
│         │                                          │                     │
│         │                                          ▼                     │
│         │                               ┌──────────────────────┐         │
│         │                               │ 6. ATS Optimize ◄────┼─┐       │
│         │                               │    (retry loop)      │ │       │
│         │                               └──────────┬───────────┘ │       │
│         │                                          │             │       │
│         │                                    [score < 95%]───────┘       │
│         │                                          │                     │
│         │                                          ▼                     │
│         │                               ┌──────────────────────┐         │
│         │                               │ 7. Compliance Check  │         │
│         │                               └──────────┬───────────┘         │
│         │                                          │                     │
│         │                                          ▼                     │
│         │                               ┌──────────────────────┐         │
│         │                               │ 8. Cover Letter      │         │
│         │                               └──────────┬───────────┘         │
│         │                                          │                     │
│         │                                          ▼                     │
│         │                               ┌──────────────────────┐         │
│         │                               │ 9. CL Compliance     │         │
│         │                               └──────────┬───────────┘         │
│         │                                          │                     │
│         │                                          ▼                     │
│         │                               ┌──────────────────────┐         │
│         │                               │ 10. Generate Email   │         │
│         │                               └──────────┬───────────┘         │
│         │                                          │                     │
│         │                                          ▼                     │
│         │                               ┌──────────────────────┐         │
│         │                               │ 11. Excel Tracker    │         │
│         │                               └──────────┬───────────┘         │
│         │                                          │                     │
│         └──────────────────────────────────────────┼─────────────────────┤
│                                                    ▼                     │
│                                         ┌──────────────────────┐         │
│                                         │ 12. Save Outputs     │         │
│                                         └──────────┬───────────┘         │
│                                                    │                     │
│                                                    ▼                     │
│                                                   END                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
job-application-assistant/
│
├── main.py                       # CLI entry point
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (API keys)
│
├── pipeline/                     # Parent graph implementation
│   ├── __init__.py               # Package exports
│   ├── config.py                 # All configuration parameters
│   ├── state.py                  # ParentGraphState definition
│   ├── nodes.py                  # 12 node functions
│   ├── graph.py                  # Graph builder with conditional edges
│   └── runner.py                 # Execution & checkpointing
│
├── subgraphs/                    # 12 LangGraph subgraphs
│   ├── __init__.py               # Central exports for all subgraphs
│   ├── test_constants.py         # Standard test JD URL/text
│   ├── jd_extractor/             # Extract structured JD
│   ├── skill_matcher/            # Match skills to JD
│   ├── github_ranker/            # Rank GitHub projects
│   ├── experience_selector/      # Select relevant experiences
│   ├── experience_rewriter/      # Rewrite bullets with keywords
│   ├── resume_builder/           # Assemble ResumeJSON
│   ├── ats_optimizer/            # Optimize for ATS score
│   ├── resource_compliance/      # Validate against checklists
│   ├── cover_letter_generator/   # Generate cover letter
│   ├── cover_letter_compliance/  # Validate cover letter
│   ├── email_generator/          # Generate outreach emails
│   └── excel_writer/             # Save to tracking spreadsheet
│
├── state/                        # Shared state models
│   └── state_models.py           # StructuredJD, ResumeJSON, etc.
│
├── mcp_server/                   # MCP server & tools
│   └── tools/
│       ├── candidate_loader.py   # Load candidate data
│       ├── github_project_loader.py  # GitHub API integration
│       └── resource_loader.py    # Load resource files
│
├── resources/                    # Reference materials (READ-ONLY)
│   ├── action_verbs.json
│   ├── resume_checklist.md
│   ├── resume_rubric.md
│   ├── resume_writing_guide.md
│   ├── cover_letter_checklist.md
│   ├── cover_letter_rubric.md
│   └── cover_letter_writing_guide.md
│
├── data/                         # Data files
│   ├── candidate_experience.json # Candidate profile
│   ├── github_projects.json      # Manual project overrides
│   └── checkpoints/              # SQLite checkpoint DB
│
├── applications/                 # Generated outputs per application
│   └── {company}_{timestamp}/
│       ├── resume.json
│       ├── cover_letter.txt
│       ├── email.txt
│       └── metadata.json
│
└── docs/                         # Documentation
    ├── PROJECT_STRUCTURE.md
    ├── STATE_ARCHITECTURE.md
    ├── PIPELINE.md
    └── SUBGRAPHS.md
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/job-application-assistant.git
cd job-application-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys:
# - OPENAI_API_KEY (required)
# - GITHUB_TOKEN (required for project ranking)
# - GITHUB_USERNAME (required for project ranking)
```

### 3. Run

```bash
# Run with test JD (Amazon Applied Scientist)
python main.py --test

# Run with specific URL
python main.py --jd-url "https://example.com/job-posting"

# Run with pasted JD text
python main.py --jd-text "We are looking for a Machine Learning Engineer..."

# Show configuration
python main.py --config

# List checkpoints
python main.py --list-checkpoints

# Resume from checkpoint
python main.py --resume <thread_id>
```

## 🖥️ Streamlit GUI

For a user-friendly web interface:

```bash
# Run Streamlit app
streamlit run streamlit_app/app.py
```

Open `http://localhost:8501` in your browser.

### GUI Pages

| Page | Description |
|------|-------------|
| 🏠 **Home** | Dashboard with overview |
| ⚙️ **Configure** | Adjust pipeline settings |
| 🚀 **Run Pipeline** | Input JD and execute |
| 📄 **Resume** | View and copy resume |
| ✉️ **Cover Letter & Email** | View generated documents |

## 📊 CLI Options

| Option | Description |
|--------|-------------|
| `--test` | Run with standard test JD URL |
| `--jd-url URL` | Process job posting from URL |
| `--jd-text TEXT` | Process raw JD text |
| `--config` | Show current configuration |
| `--list-checkpoints` | List available checkpoints |
| `--resume THREAD_ID` | Resume from checkpoint |
| `--no-checkpoints` | Disable checkpointing |

## ⚙️ Configuration

Edit `pipeline/config.py` to customize:

```python
RESUME_CONFIG = {
    "max_experiences": 4,
    "max_projects": 3,
    "summary_max_words": 60,
}

ATS_CONFIG = {
    "target_score": 95,
    "max_iterations": 3,
}

PIPELINE_CONFIG = {
    "compliance_pass_threshold": 85,
    "enable_email_generation": True,
    "save_to_excel": True,
}
```

## 🧪 Testing Individual Subgraphs

Each subgraph can be tested independently:

```python
from subgraphs import extract_jd_from_url, match_skills_to_jd

# Test JD extraction
result = extract_jd_from_url("https://example.com/job")
print(result["structured_jd"])

# Test skill matching
result = match_skills_to_jd(structured_jd=jd)
print(result["skill_match_result"])
```

## 📦 Output Structure

Each job application creates a dedicated folder:

```
applications/{company}_{timestamp}/
├── resume.json           # Structured resume data
├── cover_letter.txt      # Generated cover letter
├── email.txt             # Outreach email
└── metadata.json         # Scores and metrics
```

## 🔧 Customization

### Prompt Engineering

All prompts are in external files:

```
subgraphs/{subgraph}/prompts/
├── system_prompt.txt       # LLM role/persona
├── main_prompt.txt         # Task instructions
└── few_shot_examples.txt   # N-shot examples
```

### Adding Resources

Place files in `resources/` folder:
- `action_verbs.json` - Strong action verbs by category
- `resume_checklist.md` - Resume validation checklist
- `resume_rubric.md` - Resume scoring rubric

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please read the documentation in `docs/` before submitting PRs.
