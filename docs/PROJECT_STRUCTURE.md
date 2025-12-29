# 📁 Project Structure - Job Application Assistant

**IMPORTANT: Always reference this before creating new files/folders!**

```
D:\ML_AI\LLM\job-application-assistant\
│
├── .env                          # Environment variables (API keys, paths)
├── .gitignore                    # Git ignore rules
├── main.py                       # Main entry point (parent graph)
├── pyproject.toml                # Project config
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
│
├── applications/                 # Generated application outputs
│   └── {company}_{role}_{date}/  # Per-application folder
│       ├── resume.json
│       ├── resume.docx
│       ├── cover_letter.docx
│       └── email.txt
│
├── data/                         # Candidate & project data
│   ├── candidate_experience.json # Complete candidate profile
│   ├── github_projects.json      # Manual project overrides
│   └── github_projects_fetched.json  # API-fetched projects cache
│
├── docs/                         # Documentation
│   ├── GITHUB_PROJECT_SELECTION.md
│   ├── LLM_STRATEGIC_GUIDE.md
│   ├── RESOURCE_USAGE_VERIFICATION.md
│   └── STATE_ARCHITECTURE.md     # State design documentation
│
├── mcp_server/                   # MCP server & tools
│   └── tools/
│       ├── candidate_loader.py   # Load candidate data
│       ├── github_project_loader.py  # GitHub API integration
│       └── resource_loader.py    # Load resource files
│
├── resources/                    # Reference materials (READ-ONLY)
│   ├── action_verbs.json
│   ├── cover_letter_checklist.md
│   ├── cover_letter_rubric.md
│   ├── cover_letter_writing_guide.md
│   ├── resume_checklist.md
│   ├── resume_rubric.md
│   └── resume_writing_guide.md
│
├── state/                        # State definitions
│   ├── __init__.py
│   └── state_models.py           # ParentState + all subgraph states
│
├── subgraphs/                    # LangGraph subgraphs (ALL go here)
│   ├── __init__.py
│   │
│   ├── jd_extractor/             # ✅ DONE
│   │   ├── __init__.py
│   │   ├── state.py              # Subgraph-specific state
│   │   ├── nodes.py              # Node functions
│   │   ├── graph.py              # Graph builder
│   │   ├── test.py               # Test script
│   │   └── prompts/
│   │       ├── system_prompt.txt
│   │       ├── main_prompt.txt
│   │       └── few_shot_examples.txt
│   │
│   ├── skill_matcher/            # TODO
│   ├── github_ranker/            # TODO
│   ├── experience_selector/      # TODO
│   ├── experience_rewriter/      # TODO
│   ├── resume_builder/           # TODO
│   ├── ats_optimizer/            # TODO
│   ├── resource_compliance/      # TODO
│   ├── cover_letter_generator/   # TODO
│   ├── cover_letter_compliance/  # TODO
│   ├── email_generator/          # TODO
│   └── excel_writer/             # TODO
│
└── vectorstores/                 # Vector DB storage (if used)
```

---

## 🚫 DELETED FOLDERS (Do NOT recreate)

- `modules/` - Was duplicate of `subgraphs/`, DELETED

---

## 📝 Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Subgraph folder | `snake_case` | `jd_extractor/` |
| Python files | `snake_case.py` | `nodes.py`, `graph.py` |
| Prompt files | `snake_case.txt` | `system_prompt.txt` |
| State classes | `PascalCase` | `JDExtractorState` |
| Node functions | `snake_case` | `jd_extractor()` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |

---

## 🔧 Subgraph Standard Structure

Every subgraph in `subgraphs/` follows this pattern:

```
subgraphs/{subgraph_name}/
├── __init__.py           # Exports
├── state.py              # Subgraph-specific state (extends parent)
├── nodes.py              # Node function definitions
├── graph.py              # LangGraph builder
├── test.py               # Test script
└── prompts/
    ├── system_prompt.txt     # LLM role/persona
    ├── main_prompt.txt       # Task instructions
    └── few_shot_examples.txt # 10 examples for consistency
```

---

## ⚠️ Rules

1. **NO duplicate folders** - Check structure before creating
2. **All subgraphs go in `subgraphs/`** - Not modules, not elsewhere
3. **State models in `state/`** - Not in subgraph folders
4. **Resources are READ-ONLY** - Never modify files in `resources/`
5. **Data files in `data/`** - Candidate info, GitHub cache
6. **Tools in `mcp_server/tools/`** - Data loaders, utilities

---

## 📊 Current Progress

| Component | Status | Location |
|-----------|--------|----------|
| Parent State | ✅ Done | `state/state_models.py` |
| JD Extractor | ✅ Done | `subgraphs/jd_extractor/` |
| Skill Matcher | 🔲 TODO | `subgraphs/skill_matcher/` |
| GitHub Ranker | 🔲 TODO | `subgraphs/github_ranker/` |
| Experience Selector | 🔲 TODO | `subgraphs/experience_selector/` |
| Experience Rewriter | 🔲 TODO | `subgraphs/experience_rewriter/` |
| Resume Builder | 🔲 TODO | `subgraphs/resume_builder/` |
| ATS Optimizer | 🔲 TODO | `subgraphs/ats_optimizer/` |
| Resource Compliance | 🔲 TODO | `subgraphs/resource_compliance/` |
| Cover Letter Gen | 🔲 TODO | `subgraphs/cover_letter_generator/` |
| CL Compliance | 🔲 TODO | `subgraphs/cover_letter_compliance/` |
| Email Generator | 🔲 TODO | `subgraphs/email_generator/` |
| Excel Writer | 🔲 TODO | `subgraphs/excel_writer/` |
