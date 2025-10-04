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

def validate_bazel_workspace(repo_root: str) -> bool:
    """
    Validate that a directory is a Bazel workspace.
    
    Checks for the presence of WORKSPACE, WORKSPACE.bazel, or MODULE.bazel files.
    
    Args:
        repo_root: Path to check for Bazel workspace files
        
    Returns:
        bool: True if the directory contains Bazel workspace files, False otherwise
    """
    workspace_files = [
        os.path.join(repo_root, "WORKSPACE"),
        os.path.join(repo_root, "WORKSPACE.bazel"),
        os.path.join(repo_root, "MODULE.bazel"),
    ]
    return any(os.path.exists(f) for f in workspace_files)

# Default target kinds to discover in Bazel repositories
DEFAULT_KINDS = (
    "cc_library", 
    "cc_binary", 
    "cc_test",
    "py_library", 
    "py_binary", 
    "py_test",
)