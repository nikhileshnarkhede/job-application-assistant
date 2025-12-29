# 🎯 GitHub Project Selection Strategy

This document explains how the pipeline selects and ranks GitHub projects for your resume.

---

## 📊 Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROJECT SELECTION PIPELINE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │   SOURCE    │     │   PARSE     │     │   INDEX     │                   │
│  │             │     │             │     │             │                   │
│  │ • JSON file │ ──► │ • README    │ ──► │ • Keywords  │                   │
│  │ • Local repos│    │ • Tech stack│     │ • Tech      │                   │
│  │ • GitHub API│     │ • Features  │     │ • Tags      │                   │
│  └─────────────┘     └─────────────┘     └─────────────┘                   │
│                                                 │                           │
│                                                 ▼                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         RANKING ENGINE                               │   │
│  │                                                                      │   │
│  │   JD Skills ──────┐                                                  │   │
│  │                   │     ┌──────────────────────┐                     │   │
│  │   JD Keywords ────┼────►│   SCORING FORMULA    │                     │   │
│  │                   │     │                      │                     │   │
│  │   Role Type ──────┘     │ Tech Match:    40%   │                     │   │
│  │                         │ Keyword Match: 30%   │                     │   │
│  │                         │ Tag Match:     20%   │                     │   │
│  │                         │ Has Metrics:   10%   │                     │   │
│  │                         └──────────────────────┘                     │   │
│  │                                   │                                  │   │
│  └───────────────────────────────────┼──────────────────────────────────┘   │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      TOP 3 PROJECTS SELECTED                        │   │
│  │                                                                      │   │
│  │   Project 1: Score 85 ──► Rewrite bullets with Action Verbs         │   │
│  │   Project 2: Score 72 ──► Rewrite bullets with Action Verbs         │   │
│  │   Project 3: Score 68 ──► Rewrite bullets with Action Verbs         │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Data Sources (Priority Order)

### 1. Manual JSON File (Recommended) ⭐
**File:** `data/github_projects.json`

```json
{
  "projects": [
    {
      "id": 1,
      "name": "ml-pipeline-project",
      "github_url": "https://github.com/user/ml-pipeline",
      "description": "End-to-end ML pipeline for...",
      "tech_stack": {
        "languages": ["Python"],
        "frameworks": ["TensorFlow", "FastAPI"],
        "tools": ["Docker", "MLflow"]
      },
      "metrics": ["Achieved 95% accuracy", "Reduced latency by 40%"],
      "keywords": ["ML", "Pipeline", "Deep Learning"],
      "relevance_tags": ["ml_ai", "data_engineering"]
    }
  ]
}
```

**Why recommended:**
- Most accurate data
- You control the narrative
- Pre-written bullets available
- Metrics included

---

### 2. Local Repository Scan
**Set in `.env`:** `GITHUB_REPOS_PATH=D:\Projects`

The system will:
1. Scan all folders in the path
2. Read README.md for description
3. Parse requirements.txt / package.json for tech stack
4. Detect languages from file extensions
5. Extract keywords from README

**Auto-detected:**
- Languages: Python, JavaScript, Java, C++, etc.
- Frameworks: TensorFlow, PyTorch, React, FastAPI, etc.
- Tools: Docker, GitHub Actions
- Keywords: ML, NLP, API, etc.

---

### 3. GitHub API
**Set in `.env`:** `GITHUB_USERNAME=your_username`

Fetches public repositories via GitHub API.

---

## 🧮 Scoring Formula

Each project is scored out of 100 points:

| Factor | Weight | How It's Calculated |
|--------|--------|---------------------|
| **Tech Stack Match** | 40% | `(overlapping_tech / jd_tech_count) × 40` |
| **Keyword Match** | 30% | `(overlapping_keywords / jd_keyword_count) × 30` |
| **Relevance Tag** | 20% | Exact match = 20, Partial = 10 |
| **Has Metrics** | 10% | If project has quantified results = 10 |

### Example Calculation:

```
JD Requirements:
- Skills: Python, TensorFlow, Docker, AWS, FastAPI
- Keywords: machine learning, deep learning, API, deployment
- Role: ML Engineer

Project: "ML Pipeline"
- Tech: Python, TensorFlow, Docker, FastAPI
- Keywords: machine learning, deep learning, pipeline
- Tags: ml_ai
- Metrics: ["95% accuracy"]

Score Calculation:
- Tech Match: 4/5 × 40 = 32 points
- Keyword Match: 2/4 × 30 = 15 points  
- Tag Match: ml_ai matches "ML Engineer" = 20 points
- Has Metrics: Yes = 10 points

TOTAL: 32 + 15 + 20 + 10 = 77/100
```

---

## 🏷️ Relevance Tags

Projects are tagged for quick role matching:

| Tag | Matches These Roles |
|-----|---------------------|
| `ml_ai` | ML Engineer, AI Engineer, Data Scientist |
| `nlp` | NLP Engineer, LLM Engineer, AI Researcher |
| `computer_vision` | CV Engineer, Perception Engineer |
| `web_dev` | Full Stack, Frontend, Backend |
| `data_engineering` | Data Engineer, Analytics Engineer |
| `devops` | DevOps, MLOps, Platform Engineer |
| `research` | Research Scientist, ML Researcher |

---

## 🔄 Integration with Pipeline

### In `github_ranker` Subgraph:

```python
from mcp_server.tools.github_project_loader import get_projects_for_resume

def rank_github_projects_node(state):
    """Select and rank GitHub projects based on JD."""
    
    # Get JD info from previous nodes
    jd_skills = state.structured_jd.skills_required
    jd_keywords = state.structured_jd.keywords
    role_type = state.structured_jd.role
    
    # Get ranked projects
    selected_projects = get_projects_for_resume(
        jd_skills=jd_skills,
        jd_keywords=jd_keywords,
        role_type=role_type,
        max_projects=3
    )
    
    return {"selected_projects": selected_projects}
```

### In `experience_rewriter` Subgraph:

```python
def rewrite_project_bullets_node(state):
    """Rewrite project bullets with action verbs aligned to JD."""
    
    projects = state.selected_projects
    action_verbs = get_action_verbs_for_role(state.role_type)
    
    for project in projects:
        prompt = f"""
        Rewrite these project bullets using action verbs: {action_verbs[:15]}
        
        Project: {project['name']}
        Tech: {project['tech_stack']}
        Original bullets: {project['bullets']}
        
        JD Keywords to incorporate: {state.jd_keywords}
        
        Rules:
        - Start each bullet with an action verb
        - Include metrics where available
        - Align language with JD requirements
        """
        
        rewritten = llm.invoke(prompt)
        project['rewritten_bullets'] = rewritten
    
    return {"rewritten_projects": projects}
```

---

## 📝 Output Format for Resume

After selection and rewriting, each project looks like:

```json
{
  "name": "ML Pipeline Project",
  "github_url": "https://github.com/user/ml-pipeline",
  "technologies": ["Python", "TensorFlow", "Docker", "FastAPI"],
  "bullets": [
    "Engineered end-to-end ML pipeline using TensorFlow and FastAPI, achieving 95% model accuracy",
    "Implemented automated model retraining with Docker containers, reducing deployment time by 60%",
    "Designed RESTful API serving 10K+ predictions/day with <100ms latency"
  ],
  "relevance_score": 77
}
```

---

## ✅ What You Need to Do

### Option A: Fill Manual JSON (Recommended)

1. Open `data/github_projects.json`
2. Replace placeholder with your actual projects
3. Include:
   - Accurate tech stack
   - Key features
   - **Metrics/results** (very important!)
   - Keywords for matching

### Option B: Local Repo Scan

1. Set `GITHUB_REPOS_PATH` in `.env` to your repos folder
2. System will auto-detect:
   - Languages from file extensions
   - Frameworks from requirements.txt/package.json
   - Keywords from README.md

### Option C: Hybrid (Best)

1. Let system scan repos first
2. Review and enhance the generated JSON
3. Add metrics and better descriptions manually

---

## 🎯 Tips for Better Matching

1. **Add Metrics to Projects**
   - "Achieved 95% accuracy" → +10 points
   - "Reduced latency by 40%" → +10 points

2. **Use Standard Tech Names**
   - "tensorflow" not "tf"
   - "PyTorch" not "torch"

3. **Tag Appropriately**
   - ML projects → `["ml_ai"]`
   - NLP projects → `["ml_ai", "nlp"]`
   - Full stack → `["web_dev", "backend"]`

4. **Keep README Updated**
   - First paragraph becomes project description
   - Include tech stack mentions
   - List key features

---

## 📊 Example: Complete Project Entry

```json
{
  "id": 1,
  "name": "Real-Time Sentiment Analysis API",
  "github_url": "https://github.com/nikhilesh/sentiment-api",
  "status": "completed",
  "description": "Production-ready sentiment analysis API using fine-tuned BERT model with FastAPI backend and Docker deployment.",
  "problem_solved": "Enables real-time sentiment classification for customer feedback at scale.",
  "tech_stack": {
    "languages": ["Python"],
    "frameworks": ["PyTorch", "Transformers", "FastAPI"],
    "tools": ["Docker", "GitHub Actions", "Pytest"],
    "databases": ["Redis"],
    "cloud": ["AWS EC2", "AWS ECR"]
  },
  "key_features": [
    "Fine-tuned BERT model for domain-specific sentiment",
    "Async API with batch processing support",
    "Redis caching for frequent queries",
    "Comprehensive test coverage (95%)"
  ],
  "metrics": [
    "Achieved 92% F1-score on test dataset",
    "Handles 1000+ requests/second",
    "Reduced inference time by 40% with ONNX optimization",
    "99.9% API uptime in production"
  ],
  "keywords": [
    "NLP", "Sentiment Analysis", "BERT", "Transformers",
    "API", "FastAPI", "Docker", "Production ML"
  ],
  "relevance_tags": ["ml_ai", "nlp", "web_dev", "devops"],
  "bullets_for_resume": [
    "Developed production sentiment analysis API using fine-tuned BERT, achieving 92% F1-score",
    "Engineered FastAPI backend handling 1000+ requests/second with Redis caching",
    "Optimized inference pipeline with ONNX, reducing latency by 40%",
    "Deployed containerized solution on AWS with 99.9% uptime"
  ]
}
```

This project would score very high for ML Engineer, NLP Engineer, or Backend roles!
