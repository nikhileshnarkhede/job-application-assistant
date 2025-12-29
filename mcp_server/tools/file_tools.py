"""
File Tools for MCP Server.

Provides file read/write operations, directory management, and file existence checks.
All operations are thread-aware and support the per-application folder structure.
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read content from a file.
    
    Args:
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def write_file(
    file_path: str,
    content: str,
    encoding: str = "utf-8",
    create_dirs: bool = True
) -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write
        encoding: File encoding (default: utf-8)
        create_dirs: Create parent directories if they don't exist
        
    Returns:
        Absolute path to the written file
    """
    path = Path(file_path)
    
    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding=encoding) as f:
        f.write(content)
    
    return str(path.absolute())


def append_file(
    file_path: str,
    content: str,
    encoding: str = "utf-8",
    create_dirs: bool = True
) -> str:
    """
    Append content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to append
        encoding: File encoding (default: utf-8)
        create_dirs: Create parent directories if they don't exist
        
    Returns:
        Absolute path to the file
    """
    path = Path(file_path)
    
    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "a", encoding=encoding) as f:
        f.write(content)
    
    return str(path.absolute())


def read_json(file_path: str) -> Dict[str, Any]:
    """
    Read and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON content as dictionary
    """
    content = read_file(file_path)
    return json.loads(content)


def write_json(
    file_path: str,
    data: Dict[str, Any],
    indent: int = 2,
    create_dirs: bool = True
) -> str:
    """
    Write data to a JSON file.
    
    Args:
        file_path: Path to the JSON file
        data: Data to write
        indent: JSON indentation (default: 2)
        create_dirs: Create parent directories if they don't exist
        
    Returns:
        Absolute path to the written file
    """
    content = json.dumps(data, indent=indent, ensure_ascii=False)
    return write_file(file_path, content, create_dirs=create_dirs)


def create_directory(dir_path: str, exist_ok: bool = True) -> str:
    """
    Create a directory.
    
    Args:
        dir_path: Path to the directory to create
        exist_ok: If True, don't raise error if directory exists
        
    Returns:
        Absolute path to the created directory
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=exist_ok)
    return str(path.absolute())


def list_directory(
    dir_path: str,
    pattern: str = "*",
    recursive: bool = False
) -> List[str]:
    """
    List files in a directory.
    
    Args:
        dir_path: Path to the directory
        pattern: Glob pattern to filter files (default: "*")
        recursive: If True, search recursively
        
    Returns:
        List of file paths
    """
    path = Path(dir_path)
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    
    if recursive:
        files = list(path.rglob(pattern))
    else:
        files = list(path.glob(pattern))
    
    return [str(f) for f in files]


def file_exists(file_path: str) -> bool:
    """
    Check if a file exists.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if file exists, False otherwise
    """
    return Path(file_path).exists()


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    stat = path.stat()
    return {
        "path": str(path.absolute()),
        "name": path.name,
        "extension": path.suffix,
        "size_bytes": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "is_file": path.is_file(),
        "is_directory": path.is_dir(),
    }


def copy_file(source: str, destination: str, create_dirs: bool = True) -> str:
    """
    Copy a file to a new location.
    
    Args:
        source: Source file path
        destination: Destination file path
        create_dirs: Create parent directories if they don't exist
        
    Returns:
        Absolute path to the destination file
    """
    import shutil
    
    src_path = Path(source)
    dst_path = Path(destination)
    
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    
    if create_dirs:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    shutil.copy2(src_path, dst_path)
    return str(dst_path.absolute())


def delete_file(file_path: str) -> bool:
    """
    Delete a file.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        True if file was deleted, False if it didn't exist
    """
    path = Path(file_path)
    if path.exists():
        path.unlink()
        return True
    return False


if __name__ == "__main__":
    # Test file tools
    print("Testing File Tools...")
    
    # Test write and read
    test_path = "/tmp/test_file_tools.txt"
    write_file(test_path, "Hello, World!")
    content = read_file(test_path)
    print(f"Write/Read test: {'PASS' if content == 'Hello, World!' else 'FAIL'}")
    
    # Test file exists
    print(f"File exists test: {'PASS' if file_exists(test_path) else 'FAIL'}")
    
    # Test delete
    delete_file(test_path)
    print(f"Delete test: {'PASS' if not file_exists(test_path) else 'FAIL'}")
    
    print("File Tools tests complete!")
