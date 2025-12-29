"""
Prompt Loader Tool for MCP Server.

Loads prompts from external text files for each module.
Supports main prompts and few-shot examples.
"""

import os
from pathlib import Path
from typing import Optional


def get_modules_path() -> str:
    """Get the base path for modules."""
    return os.getenv("MODULES_PATH", "./modules")


def load_main_prompt(module_name: str) -> str:
    """
    Load the main prompt for a module.
    
    Args:
        module_name: Name of the module (e.g., "jd_extractor")
        
    Returns:
        Content of the main prompt file
        
    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    prompt_path = os.path.join(
        get_modules_path(),
        module_name,
        "prompts",
        "main_prompt.txt"
    )
    
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(
            f"Main prompt not found for module '{module_name}' at {prompt_path}"
        )
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def load_few_shot_examples(module_name: str) -> str:
    """
    Load few-shot examples for a module.
    
    Args:
        module_name: Name of the module (e.g., "jd_extractor")
        
    Returns:
        Content of the few-shot examples file
        
    Raises:
        FileNotFoundError: If examples file doesn't exist
    """
    examples_path = os.path.join(
        get_modules_path(),
        module_name,
        "prompts",
        "few_shot_examples.txt"
    )
    
    if not os.path.exists(examples_path):
        raise FileNotFoundError(
            f"Few-shot examples not found for module '{module_name}' at {examples_path}"
        )
    
    with open(examples_path, "r", encoding="utf-8") as f:
        return f.read()


def load_prompt_with_examples(
    module_name: str,
    variables: Optional[dict] = None
) -> str:
    """
    Load main prompt and few-shot examples, combining them.
    
    Args:
        module_name: Name of the module
        variables: Optional variables to format into the prompt
        
    Returns:
        Combined prompt with examples
    """
    main_prompt = load_main_prompt(module_name)
    few_shot = load_few_shot_examples(module_name)
    
    # Combine prompts
    combined = f"{main_prompt}\n\n{few_shot}"
    
    # Format with variables if provided
    if variables:
        try:
            combined = combined.format(**variables)
        except KeyError as e:
            # If a variable is missing, leave it as-is
            pass
    
    return combined


def save_prompt(
    module_name: str,
    prompt_type: str,
    content: str
) -> str:
    """
    Save a prompt to file.
    
    Args:
        module_name: Name of the module
        prompt_type: Either "main_prompt" or "few_shot_examples"
        content: Prompt content to save
        
    Returns:
        Path to the saved file
    """
    if prompt_type not in ["main_prompt", "few_shot_examples"]:
        raise ValueError(f"Invalid prompt type: {prompt_type}")
    
    prompt_dir = os.path.join(get_modules_path(), module_name, "prompts")
    os.makedirs(prompt_dir, exist_ok=True)
    
    file_path = os.path.join(prompt_dir, f"{prompt_type}.txt")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return file_path


def list_module_prompts(module_name: str) -> dict:
    """
    List all prompts available for a module.
    
    Args:
        module_name: Name of the module
        
    Returns:
        Dictionary with prompt availability
    """
    prompt_dir = os.path.join(get_modules_path(), module_name, "prompts")
    
    main_exists = os.path.exists(os.path.join(prompt_dir, "main_prompt.txt"))
    examples_exists = os.path.exists(os.path.join(prompt_dir, "few_shot_examples.txt"))
    
    return {
        "module": module_name,
        "main_prompt": main_exists,
        "few_shot_examples": examples_exists,
        "prompt_directory": prompt_dir,
    }


def list_all_modules_prompts() -> list:
    """
    List prompt status for all modules.
    
    Returns:
        List of prompt status dictionaries for each module
    """
    modules_path = get_modules_path()
    
    if not os.path.exists(modules_path):
        return []
    
    modules = [
        d for d in os.listdir(modules_path)
        if os.path.isdir(os.path.join(modules_path, d))
        and not d.startswith("_")
    ]
    
    return [list_module_prompts(module) for module in modules]


if __name__ == "__main__":
    # Test prompt loader
    print("Testing Prompt Loader...")
    
    # List all modules
    modules = list_all_modules_prompts()
    print(f"Found {len(modules)} modules")
    
    for module in modules:
        status = "✓" if module["main_prompt"] and module["few_shot_examples"] else "✗"
        print(f"  {status} {module['module']}")
    
    print("Prompt Loader tests complete!")
