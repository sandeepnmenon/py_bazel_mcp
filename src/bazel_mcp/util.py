"""Utility functions for Bazel MCP server."""
from __future__ import annotations
import os

def which_bazel() -> str:
    """
    Determine which Bazel executable to use.
    
    Priority:
    1. BAZEL_PATH environment variable
    2. BAZELISK environment variable  
    3. Default to 'bazel'
    
    Returns:
        str: Path or command name for Bazel executable
    """
    return os.environ.get("BAZEL_PATH") or os.environ.get("BAZELISK") or "bazel"

# Default target kinds to discover in Bazel repositories
DEFAULT_KINDS = (
    "cc_library", 
    "cc_binary", 
    "cc_test",
    "py_library", 
    "py_binary", 
    "py_test",
)