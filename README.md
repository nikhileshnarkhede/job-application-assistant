# Job Application Assistant

An AI-powered job application automation system built with **LangGraph**, **RAG**, and **FastMCP** tools.

## 🎯 Features

- **JD Extraction**: Parse job descriptions from URLs or text
- **Skill Matching**: RAG-powered skill gap analysis
- **GitHub Project Ranking**: Automatically select and rewrite relevant projects
- **Experience Rewriting**: ATS-optimized bullet points aligned with JD
- **Resume Generation**: Structured JSON output with strict schema
- **ATS Optimization**: Auto-loop until score ≥ 95
- **Resource Compliance**: Validate against guides, checklists, and rubrics
- **Cover Letter Generation**: Technical, tailored cover letters
- **Recruiter Email Generation**: Multiple versions (short/medium/long)
- **Excel Tracking**: Automatic job application tracking
- **Thread Isolation**: Each application gets its own folder and persistence

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Master LangGraph Pipeline                      │
├─────────────────────────────────────────────────────────────────┤
│  JD → Skills → GitHub → Rewrite → Resume → ATS → Compliance     │
│                           ↑                  │         │         │
│                           └──────────────────┴─────────┘         │
│                              (loops until passing)                │
├─────────────────────────────────────────────────────────────────┤
│                    → Excel → Cover Letter → Email                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Simple**: Each module does one thing well
2. **Modular**: Subgraphs are self-contained and replaceable
3. **Loosely Coupled**: Integration via LangGraph edges only
4. **Maintainable**: External prompts, clear boundaries
5. **Testable**: Each subgraph has its own test harness

## 📁 Project Structure

```
project_root/
├── main.py                 # Master pipeline
├── mcp_server/             # FastMCP tools
│   └── tools/              # File, Excel, RAG tools
├── modules/                # 10 LangGraph subgraphs
│   ├── jd_extractor/
│   ├── skill_matcher/
│   ├── github_ranker/
│   ├── experience_rewriter/
│   ├── resume_json_builder/
│   ├── ats_optimizer/
│   ├── resource_compliance/
│   ├── cover_letter_generator/
│   ├── recruiter_email_generator/
│   └── excel_writer/
├── resources/              # Guides, checklists, rubrics
├── vectorstores/           # RAG indexes
├── applications/           # Per-application thread folders
└── data/                   # Checkpoints, cache, temp files
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/job-application-assistant.git
cd job-application-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy and edit environment file
cp .env.example .env
# Edit .env with your API keys
```

### 3. Add Your Resources

Place your files in the `resources/` folder:
- `Action_Verbs.xlsx`
- `Resume Checklist.txt`
- `Resume guide.txt`
- `Resume rubric.xlsx`
- `Cover Letter Checklist.txt`
- `Cover letter guide.txt`
- `Cover letter rubric.xlsx`

### 4. Run

```bash
# Run the full pipeline
python main.py --jd "https://example.com/job-posting"

# Or with pasted JD text
python main.py --jd-text "We are looking for a Machine Learning Engineer..."

# Test individual subgraphs
python -m modules.jd_extractor.jd_extractor_subgraph
```

## 🧪 Testing Individual Modules

Each subgraph can be tested independently:

```bash
# Test JD Extractor
python -m modules.jd_extractor.jd_extractor_subgraph

# Test Skill Matcher
python -m modules.skill_matcher.skill_matcher_subgraph

# Test any module
python -m modules.<module_name>.<module_name>_subgraph
```

## 📊 Application Tracking

Each job application creates a dedicated folder:

```
applications/<thread_id>_<company>/
├── jd/                    # JD artifacts
├── resume/                # Resume versions
├── ats/                   # ATS iterations
├── compliance/            # Rubric results
├── cover_letter/          # Cover letters
├── recruiter_emails/      # Email versions
├── logs/                  # Debug logs
└── metadata.json          # Application metadata
```

## 🔧 Customization

### Prompt Engineering

All prompts are in external `.txt` files:

```
modules/<module>/prompts/
├── main_prompt.txt        # Core instruction
└── few_shot_examples.txt  # N-shot examples
```

Edit these files to tune the AI behavior without touching code.

### Thresholds

Adjust in `.env`:
- `ATS_SCORE_THRESHOLD=95`
- `RESUME_RUBRIC_THRESHOLD=85`
- `COVER_LETTER_RUBRIC_THRESHOLD=85`

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.
