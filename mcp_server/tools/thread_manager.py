"""
Thread Manager Tool for MCP Server.

Manages per-application thread folders and persistence.
Each job application gets its own isolated folder with:
- JD artifacts
- Resume versions
- ATS iterations
- Cover letters
- Emails
- Logs
- Metadata
"""

import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


def get_applications_path() -> str:
    """Get the base path for applications."""
    return os.getenv("APPLICATIONS_PATH", "./applications")


def generate_thread_id() -> str:
    """
    Generate a unique thread ID.
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())[:8]


def sanitize_company_name(company: str) -> str:
    """
    Sanitize company name for folder naming.
    
    Args:
        company: Raw company name
        
    Returns:
        Sanitized name safe for filesystem
    """
    # Remove or replace unsafe characters
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ']
    name = company.lower()
    for char in unsafe_chars:
        name = name.replace(char, '_')
    
    # Remove multiple underscores
    while '__' in name:
        name = name.replace('__', '_')
    
    # Trim underscores from ends
    return name.strip('_')[:50]


def create_thread_folder(
    company: str,
    thread_id: Optional[str] = None
) -> Dict[str, str]:
    """
    Create a new thread folder for an application.
    
    Args:
        company: Company name
        thread_id: Optional thread ID (generated if not provided)
        
    Returns:
        Dictionary with thread_id and folder paths
    """
    if thread_id is None:
        thread_id = generate_thread_id()
    
    company_safe = sanitize_company_name(company)
    folder_name = f"{thread_id}_{company_safe}"
    
    base_path = get_applications_path()
    thread_path = os.path.join(base_path, folder_name)
    
    # Create main folder and subfolders
    subfolders = [
        "jd",
        "resume",
        "ats",
        "ats/iterations",
        "compliance",
        "compliance/iterations",
        "cover_letter",
        "cover_letter/versions",
        "recruiter_emails",
        "recruiter_emails/logs",
        "logs",
        "logs/nodes",
    ]
    
    for subfolder in subfolders:
        os.makedirs(os.path.join(thread_path, subfolder), exist_ok=True)
    
    # Create initial metadata
    metadata = {
        "thread_id": thread_id,
        "company": company,
        "created_at": datetime.now().isoformat(),
        "status": "initialized",
        "folder_path": thread_path,
    }
    
    save_thread_metadata(thread_id, metadata)
    
    return {
        "thread_id": thread_id,
        "folder_name": folder_name,
        "folder_path": thread_path,
        "subfolders": {
            "jd": os.path.join(thread_path, "jd"),
            "resume": os.path.join(thread_path, "resume"),
            "ats": os.path.join(thread_path, "ats"),
            "compliance": os.path.join(thread_path, "compliance"),
            "cover_letter": os.path.join(thread_path, "cover_letter"),
            "recruiter_emails": os.path.join(thread_path, "recruiter_emails"),
            "logs": os.path.join(thread_path, "logs"),
        }
    }


def get_thread_path(thread_id: str) -> Optional[str]:
    """
    Get the folder path for a thread by ID.
    
    Args:
        thread_id: The thread ID to look up
        
    Returns:
        Path to the thread folder, or None if not found
    """
    base_path = get_applications_path()
    
    if not os.path.exists(base_path):
        return None
    
    # Look for folder starting with thread_id
    for folder in os.listdir(base_path):
        if folder.startswith(thread_id):
            return os.path.join(base_path, folder)
    
    return None


def save_thread_metadata(thread_id: str, metadata: Dict[str, Any]) -> str:
    """
    Save or update thread metadata.
    
    Args:
        thread_id: Thread ID
        metadata: Metadata dictionary
        
    Returns:
        Path to metadata file
    """
    thread_path = get_thread_path(thread_id)
    
    if thread_path is None:
        raise ValueError(f"Thread folder not found for ID: {thread_id}")
    
    metadata_path = os.path.join(thread_path, "metadata.json")
    
    # Update timestamp
    metadata["updated_at"] = datetime.now().isoformat()
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return metadata_path


def load_thread_metadata(thread_id: str) -> Optional[Dict[str, Any]]:
    """
    Load thread metadata.
    
    Args:
        thread_id: Thread ID
        
    Returns:
        Metadata dictionary, or None if not found
    """
    thread_path = get_thread_path(thread_id)
    
    if thread_path is None:
        return None
    
    metadata_path = os.path.join(thread_path, "metadata.json")
    
    if not os.path.exists(metadata_path):
        return None
    
    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


def update_thread_status(thread_id: str, status: str) -> Dict[str, Any]:
    """
    Update the status of a thread.
    
    Args:
        thread_id: Thread ID
        status: New status
        
    Returns:
        Updated metadata
    """
    metadata = load_thread_metadata(thread_id) or {}
    metadata["status"] = status
    metadata["status_updated_at"] = datetime.now().isoformat()
    
    save_thread_metadata(thread_id, metadata)
    return metadata


def log_to_thread(
    thread_id: str,
    log_type: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Write a log entry to the thread's log folder.
    
    Args:
        thread_id: Thread ID
        log_type: Type of log (e.g., "pipeline", "node", "error")
        message: Log message
        data: Optional additional data
        
    Returns:
        Path to log file
    """
    thread_path = get_thread_path(thread_id)
    
    if thread_path is None:
        raise ValueError(f"Thread folder not found for ID: {thread_id}")
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": log_type,
        "message": message,
    }
    
    if data:
        log_entry["data"] = data
    
    # Append to log file
    log_file = os.path.join(thread_path, "logs", f"{log_type}_log.jsonl")
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return log_file


def save_thread_artifact(
    thread_id: str,
    artifact_type: str,
    filename: str,
    content: str
) -> str:
    """
    Save an artifact to the thread folder.
    
    Args:
        thread_id: Thread ID
        artifact_type: Type of artifact (jd, resume, ats, etc.)
        filename: Name of the file
        content: Content to save
        
    Returns:
        Path to saved file
    """
    thread_path = get_thread_path(thread_id)
    
    if thread_path is None:
        raise ValueError(f"Thread folder not found for ID: {thread_id}")
    
    artifact_path = os.path.join(thread_path, artifact_type, filename)
    
    # Create parent directory if needed
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return artifact_path


def list_all_threads() -> List[Dict[str, Any]]:
    """
    List all application threads.
    
    Returns:
        List of thread info dictionaries
    """
    base_path = get_applications_path()
    
    if not os.path.exists(base_path):
        return []
    
    threads = []
    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if os.path.isdir(folder_path) and "_" in folder:
            thread_id = folder.split("_")[0]
            metadata = load_thread_metadata(thread_id)
            threads.append({
                "thread_id": thread_id,
                "folder": folder,
                "path": folder_path,
                "metadata": metadata,
            })
    
    return threads


if __name__ == "__main__":
    # Test thread manager
    print("Testing Thread Manager...")
    
    # Create test thread
    result = create_thread_folder("Test Company Inc")
    print(f"Created thread: {result['thread_id']}")
    print(f"Folder: {result['folder_path']}")
    
    # Test metadata
    thread_id = result["thread_id"]
    metadata = load_thread_metadata(thread_id)
    print(f"Metadata loaded: {metadata is not None}")
    
    # Test status update
    update_thread_status(thread_id, "in_progress")
    metadata = load_thread_metadata(thread_id)
    print(f"Status updated: {metadata.get('status')}")
    
    # Test logging
    log_path = log_to_thread(thread_id, "test", "Test log message", {"key": "value"})
    print(f"Log written: {os.path.exists(log_path)}")
    
    # Test artifact saving
    artifact_path = save_thread_artifact(thread_id, "jd", "test.txt", "Test content")
    print(f"Artifact saved: {os.path.exists(artifact_path)}")
    
    # List threads
    threads = list_all_threads()
    print(f"Total threads: {len(threads)}")
    
    print("Thread Manager tests complete!")
