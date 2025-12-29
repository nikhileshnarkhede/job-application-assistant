"""
FastMCP Server Bootstrap.

This module initializes and runs the MCP server with all registered tools.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all tools
from .tools.file_tools import (
    read_file,
    write_file,
    create_directory,
    list_directory,
    file_exists,
)
from .tools.excel_writer import append_excel_row, read_excel_sheet
from .tools.resource_loader import (
    load_action_verbs,
    load_resume_checklist,
    load_resume_guide,
    load_resume_rubric,
    load_cover_letter_checklist,
    load_cover_letter_guide,
    load_cover_letter_rubric,
)
from .tools.prompt_loader import load_main_prompt, load_few_shot_examples
from .tools.thread_manager import (
    create_thread_folder,
    get_thread_path,
    save_thread_metadata,
    load_thread_metadata,
)
from .tools.github_reader import read_github_repo, read_readme_files
from .tools.rag_vectorstore import (
    create_vectorstore,
    query_vectorstore,
    add_documents_to_store,
)
from .tools.rule_engine import (
    validate_resume_rules,
    validate_cover_letter_rules,
    check_action_verb_compliance,
)
from .tools.ats_scoring import calculate_ats_score, get_ats_feedback


def create_mcp_server():
    """
    Create and configure the MCP server with all tools.
    
    Returns:
        dict: Dictionary of all available MCP tools
    """
    tools = {
        # File Tools
        "read_file": read_file,
        "write_file": write_file,
        "create_directory": create_directory,
        "list_directory": list_directory,
        "file_exists": file_exists,
        
        # Excel Tools
        "append_excel_row": append_excel_row,
        "read_excel_sheet": read_excel_sheet,
        
        # Resource Loaders
        "load_action_verbs": load_action_verbs,
        "load_resume_checklist": load_resume_checklist,
        "load_resume_guide": load_resume_guide,
        "load_resume_rubric": load_resume_rubric,
        "load_cover_letter_checklist": load_cover_letter_checklist,
        "load_cover_letter_guide": load_cover_letter_guide,
        "load_cover_letter_rubric": load_cover_letter_rubric,
        
        # Prompt Loaders
        "load_main_prompt": load_main_prompt,
        "load_few_shot_examples": load_few_shot_examples,
        
        # Thread Management
        "create_thread_folder": create_thread_folder,
        "get_thread_path": get_thread_path,
        "save_thread_metadata": save_thread_metadata,
        "load_thread_metadata": load_thread_metadata,
        
        # GitHub Tools
        "read_github_repo": read_github_repo,
        "read_readme_files": read_readme_files,
        
        # RAG Tools
        "create_vectorstore": create_vectorstore,
        "query_vectorstore": query_vectorstore,
        "add_documents_to_store": add_documents_to_store,
        
        # Rule Engine
        "validate_resume_rules": validate_resume_rules,
        "validate_cover_letter_rules": validate_cover_letter_rules,
        "check_action_verb_compliance": check_action_verb_compliance,
        
        # ATS Scoring
        "calculate_ats_score": calculate_ats_score,
        "get_ats_feedback": get_ats_feedback,
    }
    
    return tools


def get_tool(tool_name: str):
    """
    Get a specific tool by name.
    
    Args:
        tool_name: Name of the tool to retrieve
        
    Returns:
        The tool function
    """
    tools = create_mcp_server()
    if tool_name not in tools:
        raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(tools.keys())}")
    return tools[tool_name]


if __name__ == "__main__":
    # Test server initialization
    print("Initializing MCP Server...")
    tools = create_mcp_server()
    print(f"Registered {len(tools)} tools:")
    for name in sorted(tools.keys()):
        print(f"  - {name}")
    print("\nMCP Server ready!")
