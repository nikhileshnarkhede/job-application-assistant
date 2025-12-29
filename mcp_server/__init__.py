"""
FastMCP Server for Job Application Assistant.

This module provides all external tools for:
- File operations
- Excel writing
- Resource loading
- Prompt loading
- Thread management
- GitHub reading
- RAG vectorstore operations
- Rule engine
- ATS scoring
"""

from .server import create_mcp_server

__all__ = ["create_mcp_server"]
