"""
GitHub Project Loader & Ranker

Loads GitHub projects from:
1. GitHub API (using GITHUB_TOKEN and GITHUB_USERNAME from .env) ⭐ PRIMARY
2. Manual JSON file (for customization)
3. Local repository folder scan

Then ranks projects by relevance to job description.
"""

import os
import json
import re
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import requests


@dataclass
class GitHubProject:
    """Represents a GitHub project."""
    id: int
    name: str
    github_url: str
    local_path: Optional[str]
    status: str
    description: str
    problem_solved: str
    tech_stack: Dict[str, List[str]]
    key_features: List[str]
    metrics: List[str]
    keywords: List[str]
    relevance_tags: List[str]
    bullets_for_resume: List[str]
    readme_content: Optional[str] = None
    relevance_score: float = 0.0
    stars: int = 0
    forks: int = 0
    language: str = ""
    topics: List[str] = field(default_factory=list)
    updated_at: str = ""


def get_data_path() -> str:
    """Get the base path for data files."""
    return os.getenv("DATA_PATH", "./data")


def get_github_token() -> str:
    """Get GitHub token from environment."""
    return os.getenv("GITHUB_TOKEN", "")


def get_github_username() -> str:
    """Get GitHub username from environment."""
    return os.getenv("GITHUB_USERNAME", "")


# ============================================================================
# GITHUB API METHODS
# ============================================================================

def fetch_repos_from_github(username: str = None, include_forks: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch all repositories for a GitHub user using the API.
    
    Args:
        username: GitHub username (defaults to GITHUB_USERNAME from .env)
        include_forks: Whether to include forked repositories
    
    Returns:
        List of repository data from GitHub API
    """
    username = username or get_github_username()
    token = get_github_token()
    
    if not username:
        print("Warning: GITHUB_USERNAME not set in .env")
        return []
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    repos = []
    page = 1
    per_page = 100
    
    while True:
        url = f"https://api.github.com/users/{username}/repos"
        params = {
            "page": page,
            "per_page": per_page,
            "sort": "updated",
            "direction": "desc"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            page_repos = response.json()
            
            if not page_repos:
                break
            
            for repo in page_repos:
                # Skip forks if not requested
                if repo.get("fork") and not include_forks:
                    continue
                
                repos.append(repo)
            
            page += 1
            
            # Safety limit
            if page > 10:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repos: {e}")
            break
    
    return repos


def fetch_repo_readme(owner: str, repo_name: str) -> str:
    """
    Fetch README content for a repository.
    
    Args:
        owner: Repository owner (username)
        repo_name: Repository name
    
    Returns:
        README content as string
    """
    token = get_github_token()
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}/readme"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 404:
            return ""
        
        response.raise_for_status()
        data = response.json()
        
        # README is base64 encoded
        content = data.get("content", "")
        if content:
            return base64.b64decode(content).decode("utf-8", errors="ignore")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching README for {repo_name}: {e}")
    
    return ""


def fetch_repo_languages(owner: str, repo_name: str) -> Dict[str, int]:
    """
    Fetch languages used in a repository.
    
    Returns:
        Dict mapping language name to bytes of code
    """
    token = get_github_token()
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}/languages"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching languages for {repo_name}: {e}")
    
    return {}


def fetch_repo_contents(owner: str, repo_name: str, path: str = "") -> List[Dict[str, Any]]:
    """
    Fetch contents of a repository directory.
    
    Useful for detecting requirements.txt, package.json, etc.
    """
    token = get_github_token()
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        pass
    
    return []


def fetch_file_content(owner: str, repo_name: str, file_path: str) -> str:
    """Fetch content of a specific file from repository."""
    token = get_github_token()
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 404:
            return ""
        
        response.raise_for_status()
        data = response.json()
        
        content = data.get("content", "")
        if content:
            return base64.b64decode(content).decode("utf-8", errors="ignore")
        
    except requests.exceptions.RequestException:
        pass
    
    return ""


def load_projects_from_github_api(
    username: str = None,
    include_forks: bool = False,
    fetch_details: bool = True
) -> List[GitHubProject]:
    """
    Load projects directly from GitHub API.
    
    Args:
        username: GitHub username (defaults to .env)
        include_forks: Include forked repos
        fetch_details: Fetch README and detect tech stack (slower but more accurate)
    
    Returns:
        List of GitHubProject objects
    """
    username = username or get_github_username()
    
    if not username:
        return []
    
    print(f"Fetching repositories for GitHub user: {username}")
    
    repos = fetch_repos_from_github(username, include_forks)
    
    if not repos:
        print("No repositories found")
        return []
    
    print(f"Found {len(repos)} repositories")
    
    projects = []
    
    for idx, repo in enumerate(repos):
        repo_name = repo.get("name", "")
        
        print(f"  Processing {idx + 1}/{len(repos)}: {repo_name}")
        
        # Basic info from API
        description = repo.get("description", "") or ""
        html_url = repo.get("html_url", "")
        language = repo.get("language", "") or ""
        topics = repo.get("topics", [])
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        updated_at = repo.get("updated_at", "")
        
        # Determine status
        archived = repo.get("archived", False)
        status = "archived" if archived else "active"
        
        # Fetch additional details
        readme_content = ""
        tech_stack = {"languages": [], "frameworks": [], "tools": [], "databases": [], "cloud": []}
        
        if fetch_details:
            # Fetch README
            readme_content = fetch_repo_readme(username, repo_name)
            
            # Fetch languages
            languages = fetch_repo_languages(username, repo_name)
            tech_stack["languages"] = list(languages.keys())[:5]
            
            # Detect frameworks from requirements.txt
            requirements = fetch_file_content(username, repo_name, "requirements.txt")
            if requirements:
                tech_stack["frameworks"] = detect_frameworks_from_requirements(requirements)
            
            # Check for Docker
            contents = fetch_repo_contents(username, repo_name)
            file_names = [c.get("name", "").lower() for c in contents if isinstance(c, dict)]
            
            if "dockerfile" in file_names or "docker-compose.yml" in file_names:
                tech_stack["tools"].append("Docker")
            
            if ".github" in file_names:
                # Check for workflows
                workflows = fetch_repo_contents(username, repo_name, ".github/workflows")
                if workflows:
                    tech_stack["tools"].append("GitHub Actions")
        else:
            # Just use primary language
            if language:
                tech_stack["languages"] = [language]
        
        # Extract keywords from README and topics
        keywords = list(topics)
        if readme_content:
            keywords.extend(extract_keywords_from_readme(readme_content))
        keywords = list(set(keywords))[:15]
        
        # Infer relevance tags
        relevance_tags = infer_relevance_tags(tech_stack, keywords)
        
        # Also infer from topics
        for topic in topics:
            topic_lower = topic.lower()
            if any(t in topic_lower for t in ["ml", "machine-learning", "deep-learning", "ai"]):
                relevance_tags.append("ml_ai")
            if any(t in topic_lower for t in ["nlp", "natural-language"]):
                relevance_tags.append("nlp")
            if any(t in topic_lower for t in ["computer-vision", "cv", "image"]):
                relevance_tags.append("computer_vision")
        
        relevance_tags = list(set(relevance_tags))
        
        project = GitHubProject(
            id=idx + 1,
            name=repo_name,
            github_url=html_url,
            local_path=None,
            status=status,
            description=description[:500] if description else f"Project: {repo_name}",
            problem_solved="",
            tech_stack=tech_stack,
            key_features=[],
            metrics=[],
            keywords=keywords,
            relevance_tags=relevance_tags,
            bullets_for_resume=[],
            readme_content=readme_content,
            stars=stars,
            forks=forks,
            language=language,
            topics=topics,
            updated_at=updated_at
        )
        
        projects.append(project)
    
    return projects


def detect_frameworks_from_requirements(requirements_content: str) -> List[str]:
    """Detect frameworks from requirements.txt content."""
    
    if not requirements_content:
        return []
    
    content_lower = requirements_content.lower()
    
    framework_patterns = {
        "tensorflow": "TensorFlow",
        "torch": "PyTorch",
        "keras": "Keras",
        "scikit-learn": "Scikit-learn",
        "sklearn": "Scikit-learn",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django",
        "streamlit": "Streamlit",
        "langchain": "LangChain",
        "transformers": "HuggingFace Transformers",
        "opencv": "OpenCV",
        "matplotlib": "Matplotlib",
        "plotly": "Plotly",
        "sqlalchemy": "SQLAlchemy",
        "celery": "Celery",
        "redis": "Redis",
        "boto3": "AWS SDK",
        "pyspark": "PySpark",
        "gradio": "Gradio",
        "huggingface": "HuggingFace",
        "openai": "OpenAI API",
        "anthropic": "Anthropic API",
        "sentence-transformers": "Sentence Transformers",
        "chromadb": "ChromaDB",
        "pinecone": "Pinecone",
        "faiss": "FAISS"
    }
    
    found = []
    for pattern, framework in framework_patterns.items():
        if pattern in content_lower:
            found.append(framework)
    
    return list(set(found))


# ============================================================================
# MANUAL JSON LOADING (for customization/override)
# ============================================================================

def load_projects_from_json() -> List[GitHubProject]:
    """
    Load projects from manual JSON file.
    
    Use this to override/enhance GitHub API data with custom descriptions,
    metrics, and pre-written bullets.
    """
    path = os.path.join(get_data_path(), "github_projects.json")
    
    if not os.path.exists(path):
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    projects = []
    for proj in data.get("projects", []):
        # Skip placeholder
        if proj.get("name", "").startswith("Project Name"):
            continue
            
        projects.append(GitHubProject(
            id=proj.get("id", 0),
            name=proj.get("name", ""),
            github_url=proj.get("github_url", ""),
            local_path=proj.get("local_path"),
            status=proj.get("status", "completed"),
            description=proj.get("description", ""),
            problem_solved=proj.get("problem_solved", ""),
            tech_stack=proj.get("tech_stack", {}),
            key_features=proj.get("key_features", []),
            metrics=proj.get("metrics", []),
            keywords=proj.get("keywords", []),
            relevance_tags=proj.get("relevance_tags", []),
            bullets_for_resume=proj.get("bullets_for_resume", [])
        ))
    
    return projects


def save_projects_to_json(projects: List[GitHubProject], filename: str = "github_projects.json"):
    """Save projects to JSON file for manual editing."""
    
    path = os.path.join(get_data_path(), filename)
    
    data = {
        "metadata": {
            "source": "github_api",
            "username": get_github_username(),
            "total_projects": len(projects)
        },
        "projects": [project_to_dict(p) for p in projects]
    }
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(projects)} projects to {path}")


# ============================================================================
# LOCAL REPO SCANNING
# ============================================================================

def scan_local_repos(repos_path: str) -> List[GitHubProject]:
    """Scan local repository folder and extract project info."""
    
    if not os.path.exists(repos_path):
        return []
    
    projects = []
    project_id = 1
    
    for item in os.listdir(repos_path):
        repo_path = os.path.join(repos_path, item)
        
        if not os.path.isdir(repo_path):
            continue
        
        if item.startswith(".") or item in ["node_modules", "__pycache__", "venv", ".git"]:
            continue
        
        project = extract_project_from_local_repo(repo_path, project_id)
        if project:
            projects.append(project)
            project_id += 1
    
    return projects


def extract_project_from_local_repo(repo_path: str, project_id: int) -> Optional[GitHubProject]:
    """Extract project information from a local repository."""
    
    repo_name = os.path.basename(repo_path)
    
    # Read README
    readme_content = ""
    description = ""
    for readme_file in ["README.md", "README.txt", "README", "readme.md"]:
        readme_path = os.path.join(repo_path, readme_file)
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                readme_content = f.read()
                lines = readme_content.split("\n")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("!"):
                        description = line[:500]
                        break
            break
    
    # Detect tech stack
    tech_stack = detect_tech_stack_local(repo_path)
    
    # Extract keywords
    keywords = extract_keywords_from_readme(readme_content)
    
    # Infer relevance tags
    relevance_tags = infer_relevance_tags(tech_stack, keywords)
    
    return GitHubProject(
        id=project_id,
        name=repo_name,
        github_url="",
        local_path=repo_path,
        status="completed",
        description=description or f"Project: {repo_name}",
        problem_solved="",
        tech_stack=tech_stack,
        key_features=[],
        metrics=[],
        keywords=keywords,
        relevance_tags=relevance_tags,
        bullets_for_resume=[],
        readme_content=readme_content
    )


def detect_tech_stack_local(repo_path: str) -> Dict[str, List[str]]:
    """Detect technologies used in a local repository."""
    
    tech_stack = {
        "languages": [],
        "frameworks": [],
        "tools": [],
        "databases": [],
        "cloud": []
    }
    
    # Language detection by file extension
    language_extensions = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".cpp": "C++",
        ".c": "C",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby"
    }
    
    detected_languages = set()
    
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in ["node_modules", "__pycache__", "venv", ".git", "dist", "build"]]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in language_extensions:
                detected_languages.add(language_extensions[ext])
    
    tech_stack["languages"] = list(detected_languages)
    
    # Framework detection from requirements.txt
    req_path = os.path.join(repo_path, "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            tech_stack["frameworks"] = detect_frameworks_from_requirements(content)
    
    # Docker detection
    if os.path.exists(os.path.join(repo_path, "Dockerfile")) or \
       os.path.exists(os.path.join(repo_path, "docker-compose.yml")):
        tech_stack["tools"].append("Docker")
    
    if os.path.exists(os.path.join(repo_path, ".github", "workflows")):
        tech_stack["tools"].append("GitHub Actions")
    
    return tech_stack


# ============================================================================
# KEYWORD & TAG EXTRACTION
# ============================================================================

def extract_keywords_from_readme(readme_content: str) -> List[str]:
    """Extract relevant keywords from README content."""
    
    if not readme_content:
        return []
    
    keyword_patterns = [
        r"machine learning", r"deep learning", r"neural network",
        r"nlp", r"natural language", r"computer vision",
        r"classification", r"regression", r"clustering",
        r"transformer", r"bert", r"gpt", r"llm",
        r"cnn", r"rnn", r"lstm", r"attention",
        r"api", r"rest", r"graphql",
        r"docker", r"kubernetes", r"aws", r"gcp", r"azure",
        r"database", r"sql", r"nosql", r"mongodb", r"postgresql",
        r"real-time", r"streaming", r"batch processing",
        r"data pipeline", r"etl", r"data engineering",
        r"web scraping", r"automation", r"bot",
        r"rag", r"retrieval", r"embedding", r"vector"
    ]
    
    readme_lower = readme_content.lower()
    found_keywords = []
    
    for pattern in keyword_patterns:
        if re.search(pattern, readme_lower):
            keyword = pattern.replace(r"\b", "").title()
            found_keywords.append(keyword)
    
    return found_keywords[:15]


def infer_relevance_tags(tech_stack: Dict[str, List[str]], keywords: List[str]) -> List[str]:
    """Infer relevance tags from tech stack and keywords."""
    
    tags = set()
    
    all_tech = " ".join([
        " ".join(tech_stack.get("languages", [])),
        " ".join(tech_stack.get("frameworks", [])),
        " ".join(keywords)
    ]).lower()
    
    if any(t in all_tech for t in ["tensorflow", "pytorch", "keras", "scikit", "machine learning", "deep learning"]):
        tags.add("ml_ai")
    
    if any(t in all_tech for t in ["nlp", "transformers", "bert", "gpt", "langchain", "natural language", "llm"]):
        tags.add("nlp")
    
    if any(t in all_tech for t in ["opencv", "computer vision", "image", "cnn"]):
        tags.add("computer_vision")
    
    if any(t in all_tech for t in ["react", "vue", "angular", "flask", "django", "fastapi", "express"]):
        tags.add("web_dev")
    
    if any(t in all_tech for t in ["spark", "airflow", "etl", "pipeline", "kafka"]):
        tags.add("data_engineering")
    
    if any(t in all_tech for t in ["docker", "kubernetes", "aws", "gcp", "azure"]):
        tags.add("devops")
    
    if any(t in all_tech for t in ["rag", "retrieval", "embedding", "vector", "chromadb", "pinecone"]):
        tags.add("rag_llm")
    
    return list(tags)


# ============================================================================
# RANKING & SELECTION
# ============================================================================

def rank_projects_for_jd(
    projects: List[GitHubProject],
    jd_skills: List[str],
    jd_keywords: List[str],
    role_type: str = "ml_ai"
) -> List[GitHubProject]:
    """
    Rank projects by relevance to job description.
    
    Scoring factors:
    - Tech stack overlap (35%)
    - Keyword match (25%)
    - Relevance tag match (20%)
    - Has metrics (10%)
    - Stars/activity bonus (10%)
    """
    
    jd_skills_lower = {s.lower() for s in jd_skills}
    jd_keywords_lower = {k.lower() for k in jd_keywords}
    
    for project in projects:
        score = 0.0
        
        # Tech stack overlap (35%)
        project_tech = set()
        for tech_list in project.tech_stack.values():
            for tech in tech_list:
                project_tech.add(tech.lower())
        
        tech_overlap = len(project_tech & jd_skills_lower)
        tech_score = min(tech_overlap / max(len(jd_skills_lower), 1) * 35, 35)
        score += tech_score
        
        # Keyword match (25%)
        project_keywords = {k.lower() for k in project.keywords}
        project_keywords.update(t.lower() for t in project.topics)
        keyword_overlap = len(project_keywords & jd_keywords_lower)
        keyword_score = min(keyword_overlap / max(len(jd_keywords_lower), 1) * 25, 25)
        score += keyword_score
        
        # Relevance tag match (20%)
        role_normalized = role_type.lower().replace(" ", "_").replace("-", "_")
        if role_normalized in project.relevance_tags:
            score += 20
        elif any(tag in role_normalized or role_normalized in tag for tag in project.relevance_tags):
            score += 10
        
        # Has metrics bonus (10%)
        if project.metrics and len(project.metrics) > 0:
            score += 10
        
        # Stars/activity bonus (10%)
        if project.stars >= 10:
            score += 5
        if project.stars >= 50:
            score += 5
        
        project.relevance_score = round(score, 2)
    
    # Sort by score descending
    projects.sort(key=lambda p: p.relevance_score, reverse=True)
    
    return projects


def select_top_projects(
    projects: List[GitHubProject],
    jd_skills: List[str],
    jd_keywords: List[str],
    role_type: str = "ml_ai",
    top_n: int = 3
) -> List[GitHubProject]:
    """Select top N projects for resume based on JD relevance."""
    ranked = rank_projects_for_jd(projects, jd_skills, jd_keywords, role_type)
    return ranked[:top_n]


# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def get_projects_for_resume(
    jd_skills: List[str],
    jd_keywords: List[str],
    role_type: str = "ml_ai",
    max_projects: int = 3,
    use_github_api: bool = True,
    fetch_details: bool = True
) -> List[Dict[str, Any]]:
    """
    Main function to get projects ready for resume.
    
    Priority:
    1. GitHub API (if credentials available)
    2. Manual JSON file
    3. Local repo scan
    
    Returns projects with relevance scores and suggested bullets.
    """
    projects = []
    
    # Try GitHub API first
    if use_github_api and get_github_username() and get_github_token():
        projects = load_projects_from_github_api(fetch_details=fetch_details)
    
    # Merge with manual JSON (for custom metrics/bullets)
    manual_projects = load_projects_from_json()
    if manual_projects:
        # Merge: manual overrides API data
        manual_names = {p.name.lower() for p in manual_projects}
        for proj in projects:
            if proj.name.lower() not in manual_names:
                manual_projects.append(proj)
        projects = manual_projects
    
    # Fallback to local scan
    if not projects:
        repos_path = os.getenv("GITHUB_REPOS_PATH", "")
        if repos_path and os.path.exists(repos_path):
            projects = scan_local_repos(repos_path)
    
    if not projects:
        return []
    
    # Select top projects
    selected = select_top_projects(projects, jd_skills, jd_keywords, role_type, max_projects)
    
    # Format for resume
    result = []
    for proj in selected:
        result.append({
            "name": proj.name,
            "github_url": proj.github_url,
            "description": proj.description,
            "tech_stack": proj.tech_stack,
            "key_features": proj.key_features,
            "metrics": proj.metrics,
            "keywords": proj.keywords,
            "topics": proj.topics,
            "relevance_score": proj.relevance_score,
            "stars": proj.stars,
            "bullets": proj.bullets_for_resume if proj.bullets_for_resume else generate_project_bullets(proj),
            "matching_skills": list(set(s.lower() for s in jd_skills) & 
                                   set(t.lower() for ts in proj.tech_stack.values() for t in ts))
        })
    
    return result


def generate_project_bullets(project: GitHubProject) -> List[str]:
    """Generate resume bullet points for a project (template for LLM to rewrite)."""
    bullets = []
    
    tech_list = ", ".join(project.tech_stack.get("frameworks", [])[:3])
    if tech_list:
        bullets.append(f"Developed {project.name} using {tech_list}")
    elif project.tech_stack.get("languages"):
        bullets.append(f"Built {project.name} in {project.tech_stack['languages'][0]}")
    
    if project.description:
        bullets.append(project.description[:100])
    
    if project.metrics:
        bullets.append(project.metrics[0])
    
    return bullets


def project_to_dict(project: GitHubProject) -> Dict[str, Any]:
    """Convert GitHubProject to dictionary."""
    return {
        "id": project.id,
        "name": project.name,
        "github_url": project.github_url,
        "local_path": project.local_path,
        "status": project.status,
        "description": project.description,
        "problem_solved": project.problem_solved,
        "tech_stack": project.tech_stack,
        "key_features": project.key_features,
        "metrics": project.metrics,
        "keywords": project.keywords,
        "relevance_tags": project.relevance_tags,
        "bullets_for_resume": project.bullets_for_resume,
        "relevance_score": project.relevance_score,
        "stars": project.stars,
        "forks": project.forks,
        "language": project.language,
        "topics": project.topics,
        "updated_at": project.updated_at
    }


def refresh_projects_from_github(save_to_json: bool = True) -> List[GitHubProject]:
    """
    Refresh projects from GitHub API and optionally save to JSON.
    
    Call this to update your local cache of projects.
    """
    projects = load_projects_from_github_api(fetch_details=True)
    
    if save_to_json and projects:
        save_projects_to_json(projects, "github_projects_fetched.json")
    
    return projects


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("GitHub Project Loader - Testing")
    print("=" * 60)
    
    username = get_github_username()
    token = get_github_token()
    
    print(f"\nGitHub Username: {username}")
    print(f"GitHub Token: {'✓ Set' if token else '✗ Not set'}")
    
    if username and token:
        print("\n" + "-" * 60)
        print("Fetching projects from GitHub API...")
        print("-" * 60)
        
        projects = load_projects_from_github_api(fetch_details=True)
        
        print(f"\nFound {len(projects)} projects:")
        for proj in projects[:10]:  # Show first 10
            print(f"\n  📁 {proj.name}")
            print(f"     URL: {proj.github_url}")
            print(f"     Language: {proj.language}")
            print(f"     Frameworks: {proj.tech_stack.get('frameworks', [])}")
            print(f"     Topics: {proj.topics}")
            print(f"     Stars: {proj.stars}")
            print(f"     Tags: {proj.relevance_tags}")
        
        # Test ranking
        print("\n" + "-" * 60)
        print("Testing ranking for ML Engineer role...")
        print("-" * 60)
        
        jd_skills = ["Python", "TensorFlow", "PyTorch", "Docker", "AWS", "FastAPI"]
        jd_keywords = ["machine learning", "deep learning", "neural networks", "api"]
        
        ranked = rank_projects_for_jd(projects, jd_skills, jd_keywords, "ml_ai")
        
        print("\nTop 5 projects for ML Engineer:")
        for proj in ranked[:5]:
            print(f"  {proj.relevance_score:.1f} - {proj.name}")
        
        # Save to JSON
        print("\n" + "-" * 60)
        print("Saving projects to JSON...")
        save_projects_to_json(projects, "github_projects_fetched.json")
        
    else:
        print("\n⚠️  Set GITHUB_USERNAME and GITHUB_TOKEN in .env to use API")
        
        # Try manual JSON
        print("\nTrying manual JSON file...")
        projects = load_projects_from_json()
        print(f"Found {len(projects)} projects from JSON")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
