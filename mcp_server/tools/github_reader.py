"""
GitHub Reader Tool for MCP Server.

Reads GitHub repositories for project ranking:
- README files
- Code files (for keyword extraction)
- Project descriptions
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


def get_github_local_path() -> str:
    """Get the local path for GitHub repos."""
    return os.getenv("GITHUB_LOCAL_PATH", "./github_repos")


def read_readme_files(repo_path: str) -> Dict[str, str]:
    """
    Read all README files from a repository.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary mapping file paths to content
    """
    readme_files = {}
    repo = Path(repo_path)
    
    if not repo.exists():
        return readme_files
    
    # Common README patterns
    patterns = ["README.md", "README.txt", "README", "readme.md", "Readme.md"]
    
    for pattern in patterns:
        # Check root level
        root_readme = repo / pattern
        if root_readme.exists():
            with open(root_readme, "r", encoding="utf-8", errors="ignore") as f:
                readme_files[str(root_readme)] = f.read()
    
    # Also check subdirectories for additional READMEs
    for readme_path in repo.rglob("README.md"):
        if str(readme_path) not in readme_files:
            with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                readme_files[str(readme_path)] = f.read()
    
    return readme_files


def read_code_files(
    repo_path: str,
    extensions: Optional[List[str]] = None,
    max_files: int = 50,
    max_file_size: int = 100000
) -> Dict[str, str]:
    """
    Read code files from a repository.
    
    Args:
        repo_path: Path to the repository
        extensions: List of file extensions to read (default: Python, notebooks)
        max_files: Maximum number of files to read
        max_file_size: Maximum file size in bytes
        
    Returns:
        Dictionary mapping file paths to content
    """
    if extensions is None:
        extensions = [".py", ".ipynb", ".md", ".txt"]
    
    code_files = {}
    repo = Path(repo_path)
    
    if not repo.exists():
        return code_files
    
    # Skip directories
    skip_dirs = {"__pycache__", ".git", "node_modules", "venv", ".venv", "env"}
    
    file_count = 0
    for ext in extensions:
        for file_path in repo.rglob(f"*{ext}"):
            # Skip if in excluded directory
            if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
                continue
            
            # Check file size
            if file_path.stat().st_size > max_file_size:
                continue
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code_files[str(file_path)] = f.read()
                    file_count += 1
                    
                if file_count >= max_files:
                    break
            except Exception:
                continue
        
        if file_count >= max_files:
            break
    
    return code_files


def extract_imports_from_python(code: str) -> List[str]:
    """
    Extract import statements from Python code.
    
    Args:
        code: Python source code
        
    Returns:
        List of imported module names
    """
    imports = []
    
    # Match "import X" and "from X import Y"
    import_pattern = r'^(?:from\s+(\S+)\s+import|import\s+(\S+))'
    
    for line in code.split("\n"):
        line = line.strip()
        match = re.match(import_pattern, line)
        if match:
            module = match.group(1) or match.group(2)
            # Get top-level module
            module = module.split(".")[0]
            if module and module not in imports:
                imports.append(module)
    
    return imports


def extract_keywords_from_code(code: str) -> List[str]:
    """
    Extract relevant keywords from code.
    
    Args:
        code: Source code
        
    Returns:
        List of keywords
    """
    keywords = []
    
    # ML/AI related terms to look for
    ml_terms = [
        "tensorflow", "pytorch", "keras", "sklearn", "scikit-learn",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn",
        "transformers", "huggingface", "bert", "gpt", "lstm", "cnn", "rnn",
        "neural", "deep learning", "machine learning", "nlp", "cv",
        "classification", "regression", "clustering", "embedding",
        "model", "train", "predict", "evaluate", "accuracy", "loss",
        "optimizer", "gradient", "backprop", "epoch", "batch",
        "api", "flask", "fastapi", "docker", "aws", "gcp", "azure",
    ]
    
    code_lower = code.lower()
    
    for term in ml_terms:
        if term in code_lower:
            keywords.append(term)
    
    return list(set(keywords))


def read_github_repo(repo_path: str) -> Dict[str, Any]:
    """
    Read and analyze a GitHub repository.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary with repository analysis
    """
    result = {
        "path": repo_path,
        "readme_content": "",
        "readme_files": {},
        "code_files_count": 0,
        "imports": [],
        "keywords": [],
        "technologies": [],
    }
    
    # Read READMEs
    readmes = read_readme_files(repo_path)
    result["readme_files"] = readmes
    
    # Get main README content
    if readmes:
        # Prefer root README.md
        for path, content in readmes.items():
            if path.endswith("README.md") and "README.md" in path:
                result["readme_content"] = content
                break
        
        # Fallback to first README
        if not result["readme_content"] and readmes:
            result["readme_content"] = list(readmes.values())[0]
    
    # Read code files
    code_files = read_code_files(repo_path)
    result["code_files_count"] = len(code_files)
    
    # Extract imports and keywords
    all_imports = []
    all_keywords = []
    
    for content in code_files.values():
        if content:
            all_imports.extend(extract_imports_from_python(content))
            all_keywords.extend(extract_keywords_from_code(content))
    
    result["imports"] = list(set(all_imports))
    result["keywords"] = list(set(all_keywords))
    
    # Determine technologies
    tech_mapping = {
        "tensorflow": "TensorFlow",
        "torch": "PyTorch",
        "keras": "Keras",
        "sklearn": "Scikit-learn",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "transformers": "Transformers/HuggingFace",
        "flask": "Flask",
        "fastapi": "FastAPI",
        "docker": "Docker",
    }
    
    for imp in result["imports"]:
        if imp in tech_mapping:
            result["technologies"].append(tech_mapping[imp])
    
    for kw in result["keywords"]:
        if kw in tech_mapping and tech_mapping[kw] not in result["technologies"]:
            result["technologies"].append(tech_mapping[kw])
    
    return result


def get_project_summary(repo_analysis: Dict[str, Any]) -> str:
    """
    Generate a summary of a project from analysis.
    
    Args:
        repo_analysis: Repository analysis dictionary
        
    Returns:
        Summary string
    """
    parts = []
    
    # Add technologies
    if repo_analysis.get("technologies"):
        parts.append(f"Technologies: {', '.join(repo_analysis['technologies'])}")
    
    # Add imports
    if repo_analysis.get("imports"):
        key_imports = repo_analysis["imports"][:10]
        parts.append(f"Key imports: {', '.join(key_imports)}")
    
    # Add keywords
    if repo_analysis.get("keywords"):
        parts.append(f"Keywords: {', '.join(repo_analysis['keywords'][:15])}")
    
    # Add README excerpt
    readme = repo_analysis.get("readme_content", "")
    if readme:
        # Get first meaningful paragraph
        paragraphs = [p.strip() for p in readme.split("\n\n") if p.strip()]
        for p in paragraphs:
            if len(p) > 50 and not p.startswith("#"):
                parts.append(f"Description: {p[:300]}...")
                break
    
    return "\n".join(parts)


if __name__ == "__main__":
    # Test GitHub reader
    print("Testing GitHub Reader...")
    
    # Test with current directory as mock repo
    test_path = "."
    
    # Read READMEs
    readmes = read_readme_files(test_path)
    print(f"Found {len(readmes)} README files")
    
    # Read code files
    code_files = read_code_files(test_path)
    print(f"Found {len(code_files)} code files")
    
    # Full analysis
    analysis = read_github_repo(test_path)
    print(f"Imports found: {len(analysis['imports'])}")
    print(f"Keywords found: {len(analysis['keywords'])}")
    print(f"Technologies: {analysis['technologies']}")
    
    print("GitHub Reader tests complete!")
