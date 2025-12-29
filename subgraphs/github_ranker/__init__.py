"""
GitHub Ranker Subgraph

Ranks GitHub projects by relevance to job description and generates resume bullets.

Usage:
    from subgraphs.github_ranker import rank_github_projects
    
    # With structured JD (from JD Extractor):
    result = rank_github_projects(structured_jd, max_projects=3)
    
    for project in result["selected_projects"]:
        print(f"{project.name} - Score: {project.relevance_score}")
        for bullet in project.bullets:
            print(f"  • {bullet}")
"""

from subgraphs.github_ranker.graph import (
    build_github_ranker_graph,
    create_github_ranker_subgraph,
    rank_github_projects,
    get_top_projects_for_jd
)

from subgraphs.github_ranker.state import (
    GitHubRankerState,
    SCORING_WEIGHTS,
    ROLE_TYPE_TAGS
)

from subgraphs.github_ranker.nodes import (
    load_projects,
    extract_jd_requirements,
    score_projects,
    select_top_projects,
    generate_bullets
)

__all__ = [
    # Main functions
    "rank_github_projects",
    "get_top_projects_for_jd",
    
    # Graph builders
    "build_github_ranker_graph",
    "create_github_ranker_subgraph",
    
    # State
    "GitHubRankerState",
    "SCORING_WEIGHTS",
    "ROLE_TYPE_TAGS",
    
    # Nodes (for custom graph building)
    "load_projects",
    "extract_jd_requirements",
    "score_projects",
    "select_top_projects",
    "generate_bullets"
]
