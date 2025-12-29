# 📁 Project Structure

**Last Updated:** December 29, 2024

## Directory Layout

```
D:\ML_AI\LLM\job-application-assistant\
│
├── .env                          # Environment variables (API keys)
├── .env.example                  # Template for .env
├── .gitignore                    # Git ignore rules
├── main.py                       # CLI entry point
├── pyproject.toml                # Project configuration
├── README.md                     # Main documentation
├── requirements.txt              # Python dependencies
│
├── pipeline/                     # 🔄 Parent Graph Implementation
│   ├── __init__.py               # Package exports
│   ├── config.py                 # All configuration parameters
│   ├── state.py                  # ParentGraphState definition
│   ├── nodes.py                  # 12 node functions
│   ├── graph.py                  # Graph builder with conditional edges
│   └── runner.py                 # Execution & checkpointing
│
├── subgraphs/                    # 📊 12 LangGraph Subgraphs
│   ├── __init__.py               # Central exports
│   ├── test_constants.py         # Standard test JD URL/text
│   │
│   ├── jd_extractor/             # ✅ 1. Extract structured JD
│   ├── skill_matcher/            # ✅ 2. Match skills to JD
│   ├── github_ranker/            # ✅ 3. Rank GitHub projects
│   ├── experience_selector/      # ✅ 4. Select experiences
│   ├── experience_rewriter/      # ✅ 5. Rewrite bullets
│   ├── resume_builder/           # ✅ 6. Build ResumeJSON
│   ├── ats_optimizer/            # ✅ 7. ATS optimization
│   ├── resource_compliance/      # ✅ 8. Resume compliance
│   ├── cover_letter_generator/   # ✅ 9. Cover letter
│   ├── cover_letter_compliance/  # ✅ 10. CL compliance
│   ├── email_generator/          # ✅ 11. Outreach emails
│   └── excel_writer/             # ✅ 12. Excel tracking
│
├── state/                        # 📋 Shared State Models
│   ├── __init__.py
│   └── state_models.py           # StructuredJD, ResumeJSON, etc.
│
├── mcp_server/                   # 🔧 MCP Server & Tools
│   ├── __init__.py
│   └── tools/
│       ├── candidate_loader.py   # Load candidate data
│       ├── github_project_loader.py  # GitHub API integration
│       ├── resource_loader.py    # Load resource files
│       ├── ats_scoring.py        # ATS scoring utilities
│       ├── excel_writer.py       # Excel utilities
│       └── ...
│
├── resources/                    # 📚 Reference Materials (READ-ONLY)
│   ├── action_verbs.json         # Strong action verbs
│   ├── resume_checklist.md       # Resume validation checklist
│   ├── resume_rubric.md          # Resume scoring rubric
│   ├── resume_writing_guide.md   # Best practices
│   ├── cover_letter_checklist.md
│   ├── cover_letter_rubric.md
│   └── cover_letter_writing_guide.md
│
├── data/                         # 💾 Data Files
│   ├── candidate_experience.json # Candidate profile
│   ├── github_projects.json      # Manual project overrides
│   ├── github_projects_fetched.json  # API cache
│   └── checkpoints/              # SQLite checkpoint DB
│       └── pipeline.db
│
├── applications/                 # 📤 Generated Outputs
│   └── {company}_{timestamp}/
│       ├── resume.json
│       ├── cover_letter.txt
│       ├── email.txt
│       └── metadata.json
│
├── docs/                         # 📖 Documentation
│   ├── PROJECT_STRUCTURE.md      # This file
│   ├── STATE_ARCHITECTURE.md     # State design
│   ├── PIPELINE.md               # Pipeline documentation
│   ├── SUBGRAPHS.md              # Subgraph overview
│   └── ...
│
└── output/                       # 🗂️ Misc outputs
```

---

## 🔧 Subgraph Standard Structure

Every subgraph follows this pattern:

```
subgraphs/{subgraph_name}/
├── __init__.py           # Package exports
├── state.py              # Subgraph-specific state
├── nodes.py              # Node function definitions
├── graph.py              # LangGraph builder + convenience functions
├── test.py               # Test script
├── README.md             # Documentation
└── prompts/              # LLM prompts (if applicable)
    ├── system_prompt.txt
    ├── main_prompt.txt
    └── few_shot_examples.txt
```

---

## 📝 Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Folders | `snake_case` | `jd_extractor/` |
| Python files | `snake_case.py` | `nodes.py` |
| Prompt files | `snake_case.txt` | `system_prompt.txt` |
| State classes | `PascalCase` | `JDExtractorState` |
| Node functions | `snake_case` | `extract_jd()` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Config dicts | `UPPER_SNAKE_CASE` | `RESUME_CONFIG` |

---

## ⚠️ Rules

1. **All subgraphs in `subgraphs/`** - Never create `modules/` folder
2. **Shared models in `state/`** - StructuredJD, ResumeJSON, etc.
3. **Resources are READ-ONLY** - Never modify files in `resources/`
4. **Data files in `data/`** - Candidate info, GitHub cache
5. **Tools in `mcp_server/tools/`** - Data loaders, utilities
6. **Config in `pipeline/config.py`** - All parameters in one place
7. **Each subgraph has README.md** - Document usage and API

---

## 📊 Component Status

| Component | Status | Location |
|-----------|--------|----------|
| CLI Entry Point | ✅ Done | `main.py` |
| Parent Graph | ✅ Done | `pipeline/` |
| JD Extractor | ✅ Done | `subgraphs/jd_extractor/` |
| Skill Matcher | ✅ Done | `subgraphs/skill_matcher/` |
| GitHub Ranker | ✅ Done | `subgraphs/github_ranker/` |
| Experience Selector | ✅ Done | `subgraphs/experience_selector/` |
| Experience Rewriter | ✅ Done | `subgraphs/experience_rewriter/` |
| Resume Builder | ✅ Done | `subgraphs/resume_builder/` |
| ATS Optimizer | ✅ Done | `subgraphs/ats_optimizer/` |
| Resource Compliance | ✅ Done | `subgraphs/resource_compliance/` |
| Cover Letter Gen | ✅ Done | `subgraphs/cover_letter_generator/` |
| CL Compliance | ✅ Done | `subgraphs/cover_letter_compliance/` |
| Email Generator | ✅ Done | `subgraphs/email_generator/` |
| Excel Writer | ✅ Done | `subgraphs/excel_writer/` |
