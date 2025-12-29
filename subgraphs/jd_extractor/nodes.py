"""
JD Extractor Nodes

This module contains all node definitions for the JD Extractor subgraph:
1. input_router - Routes based on input type (text vs URL)
2. url_fetcher - Fetches JD content from URL
3. jd_extractor - Extracts structured JD using LLM
4. validation_node - Validates extraction output
5. error_handler - Handles extraction errors

Node Flow:
    START → input_router → [url_fetcher] → jd_extractor → validation_node → END
                 │                               ↑
                 └─────────────────────────────→─┘ (if text input)
"""

import os
import re
import json
import requests
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

# State imports
from subgraphs.jd_extractor.state import (
    JDExtractorState,
    validate_structured_jd
)
from state.state_models import StructuredJD


# ============================================================================
# CONFIGURATION
# ============================================================================

def get_llm():
    """Get configured LLM instance."""
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.1,  # Low temperature for consistent extraction
        api_key=os.getenv("OPENAI_API_KEY")
    )


def load_prompt(filename: str) -> str:
    """Load prompt from file."""
    prompt_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(prompt_dir, "prompts", filename)
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


# ============================================================================
# NODE 1: INPUT ROUTER
# ============================================================================

def input_router(state: JDExtractorState) -> Dict[str, Any]:
    """
    Route based on input type.
    
    Determines whether input is text or URL and sets appropriate flags.
    
    Returns:
        Updated state dict with routing decision
    """
    # Check if URL is provided
    if state.jd_url and state.jd_url.strip():
        # Validate URL format
        try:
            result = urlparse(state.jd_url)
            if all([result.scheme, result.netloc]):
                return {
                    "input_type": "url",
                    "jd_url": state.jd_url.strip()
                }
        except Exception:
            pass
    
    # Check if raw text is provided
    if state.raw_jd_text and state.raw_jd_text.strip():
        return {
            "input_type": "text",
            "raw_jd_text": state.raw_jd_text.strip()
        }
    
    # No valid input
    return {
        "extraction_error": "No valid input provided. Please provide either JD text or URL.",
        "extraction_complete": True
    }


# ============================================================================
# NODE 2: URL FETCHER
# ============================================================================

def url_fetcher(state: JDExtractorState) -> Dict[str, Any]:
    """
    Fetch JD content from URL.
    
    Supports various job board formats:
    - LinkedIn
    - Indeed
    - Greenhouse
    - Lever
    - Generic HTML pages
    
    Returns:
        Updated state dict with fetched content or error
    """
    url = state.jd_url
    
    if not url:
        return {
            "fetch_error": "No URL provided",
            "extraction_error": "No URL provided"
        }
    
    try:
        # Set headers to mimic browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        # Fetch page
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        
        # Try to find job description container (common patterns)
        content = None
        
        # LinkedIn pattern
        linkedin_div = soup.find("div", class_=re.compile(r"description|job-details|show-more-less"))
        if linkedin_div:
            content = linkedin_div.get_text(separator="\n", strip=True)
        
        # Greenhouse pattern
        if not content:
            greenhouse_div = soup.find("div", id=re.compile(r"content|job-content"))
            if greenhouse_div:
                content = greenhouse_div.get_text(separator="\n", strip=True)
        
        # Lever pattern
        if not content:
            lever_div = soup.find("div", class_=re.compile(r"posting-|content"))
            if lever_div:
                content = lever_div.get_text(separator="\n", strip=True)
        
        # Generic: look for main content area
        if not content:
            main = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|job|posting"))
            if main:
                content = main.get_text(separator="\n", strip=True)
        
        # Fallback: get body text
        if not content:
            body = soup.find("body")
            if body:
                content = body.get_text(separator="\n", strip=True)
        
        if not content:
            return {
                "fetch_error": "Could not extract content from URL",
                "extraction_error": "Could not extract content from URL"
            }
        
        # Clean up content
        # Remove excessive whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)
        
        # Limit content length (some pages have too much irrelevant content)
        if len(content) > 15000:
            content = content[:15000]
        
        return {
            "fetched_content": content,
            "raw_jd_text": content,
            "fetch_error": None
        }
        
    except requests.exceptions.Timeout:
        return {
            "fetch_error": "URL request timed out",
            "extraction_error": "URL request timed out"
        }
    except requests.exceptions.RequestException as e:
        return {
            "fetch_error": f"Failed to fetch URL: {str(e)}",
            "extraction_error": f"Failed to fetch URL: {str(e)}"
        }
    except Exception as e:
        return {
            "fetch_error": f"Error processing URL: {str(e)}",
            "extraction_error": f"Error processing URL: {str(e)}"
        }


# ============================================================================
# NODE 3: JD EXTRACTOR (LLM)
# ============================================================================

def jd_extractor(state: JDExtractorState) -> Dict[str, Any]:
    """
    Extract structured JD from raw text using LLM.
    
    Uses three prompts:
    1. System prompt - Sets LLM role and guidelines
    2. Main prompt - Task description with schema
    3. Few-shot examples - 10 examples for consistency
    
    Returns:
        Updated state dict with structured_jd or error
    """
    raw_text = state.raw_jd_text
    
    if not raw_text or not raw_text.strip():
        return {
            "extraction_error": "No JD text to extract",
            "extraction_complete": True
        }
    
    try:
        # Load prompts
        system_prompt = load_prompt("system_prompt.txt")
        main_prompt_template = load_prompt("main_prompt.txt")
        few_shot_examples = load_prompt("few_shot_examples.txt")
        
        # Format main prompt with JD text
        main_prompt = main_prompt_template.format(raw_jd_text=raw_text)
        
        # Build messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
Here are examples of how to extract job descriptions:

{few_shot_examples}

---

Now extract the following job description:

{main_prompt}
""")
        ]
        
        # Get LLM
        llm = get_llm()
        
        # Invoke LLM
        response = llm.invoke(messages)
        
        # Parse response
        response_text = response.content.strip()
        
        # Clean JSON (remove markdown code blocks if present)
        if response_text.startswith("```"):
            response_text = re.sub(r'^```(?:json)?\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
        
        # Parse JSON
        try:
            jd_dict = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Try to fix common JSON issues
            response_text = response_text.replace("'", '"')
            response_text = re.sub(r',\s*}', '}', response_text)
            response_text = re.sub(r',\s*]', ']', response_text)
            jd_dict = json.loads(response_text)
        
        # Add raw_text_length if not present
        if "raw_text_length" not in jd_dict:
            jd_dict["raw_text_length"] = len(raw_text)
        
        # Create StructuredJD object
        structured_jd = StructuredJD(**jd_dict)
        
        return {
            "structured_jd": structured_jd,
            "extraction_error": None
        }
        
    except json.JSONDecodeError as e:
        return {
            "extraction_error": f"Failed to parse LLM response as JSON: {str(e)}",
            "retry_count": state.retry_count + 1
        }
    except Exception as e:
        return {
            "extraction_error": f"Extraction failed: {str(e)}",
            "retry_count": state.retry_count + 1
        }


# ============================================================================
# NODE 4: VALIDATION NODE
# ============================================================================

def validation_node(state: JDExtractorState) -> Dict[str, Any]:
    """
    Validate the extracted structured JD.
    
    Checks:
    - Required fields are present
    - Role type is valid
    - Extraction confidence is acceptable
    - Skills and keywords were extracted
    
    Returns:
        Updated state dict with validation results
    """
    if not state.structured_jd:
        return {
            "validation_passed": False,
            "extraction_error": "No structured JD to validate",
            "extraction_complete": True
        }
    
    is_valid, issues = validate_structured_jd(state.structured_jd)
    
    if is_valid:
        return {
            "validation_passed": True,
            "extraction_complete": True,
            "extraction_error": None
        }
    else:
        # Check if we should retry
        if state.retry_count < state.max_retries:
            return {
                "validation_passed": False,
                "extraction_error": f"Validation failed: {', '.join(issues)}",
                "retry_count": state.retry_count + 1
            }
        else:
            # Max retries reached, accept with warnings
            return {
                "validation_passed": True,  # Accept with warnings
                "extraction_complete": True,
                "extraction_error": f"Accepted with warnings: {', '.join(issues)}"
            }


# ============================================================================
# NODE 5: ERROR HANDLER
# ============================================================================

def error_handler(state: JDExtractorState) -> Dict[str, Any]:
    """
    Handle extraction errors.
    
    Decides whether to retry or give up.
    
    Returns:
        Updated state dict
    """
    if state.retry_count >= state.max_retries:
        return {
            "extraction_complete": True,
            "extraction_error": f"Max retries ({state.max_retries}) exceeded. Last error: {state.extraction_error}"
        }
    
    # Allow retry
    return {
        "extraction_complete": False
    }


# ============================================================================
# CONDITIONAL EDGES
# ============================================================================

def route_by_input_type(state: JDExtractorState) -> str:
    """
    Route based on input type.
    
    Returns:
        "fetch_url" if URL input, "extract" if text input, "error" if no input
    """
    if state.extraction_error:
        return "error"
    
    if state.input_type == "url":
        return "fetch_url"
    elif state.input_type == "text":
        return "extract"
    else:
        return "error"


def route_after_validation(state: JDExtractorState) -> str:
    """
    Route after validation.
    
    Returns:
        "end" if complete, "retry" if should retry, "error" if failed
    """
    if state.extraction_complete:
        return "end"
    
    if state.retry_count < state.max_retries:
        return "retry"
    
    return "error"


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Nodes
    "input_router",
    "url_fetcher",
    "jd_extractor",
    "validation_node",
    "error_handler",
    
    # Conditional edges
    "route_by_input_type",
    "route_after_validation",
    
    # Utilities
    "get_llm",
    "load_prompt"
]
