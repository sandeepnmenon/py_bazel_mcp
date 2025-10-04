"""Tests for utility functions."""
import os
import tempfile
import pytest
from bazel_mcp.util import validate_bazel_workspace


def test_validate_bazel_workspace_with_workspace():
    """Test validation with WORKSPACE file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = os.path.join(tmpdir, "WORKSPACE")
        with open(workspace, "w") as f:
            f.write("# Bazel workspace")
        
        assert validate_bazel_workspace(tmpdir) is True


def test_validate_bazel_workspace_with_workspace_bazel():
    """Test validation with WORKSPACE.bazel file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = os.path.join(tmpdir, "WORKSPACE.bazel")
        with open(workspace, "w") as f:
            f.write("# Bazel workspace")
        
        assert validate_bazel_workspace(tmpdir) is True


def test_validate_bazel_workspace_with_module_bazel():
    """Test validation with MODULE.bazel file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        module = os.path.join(tmpdir, "MODULE.bazel")
        with open(module, "w") as f:
            f.write("# Bazel module")
        
        assert validate_bazel_workspace(tmpdir) is True


def test_validate_bazel_workspace_without_files():
    """Test validation fails without any Bazel workspace files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        assert validate_bazel_workspace(tmpdir) is False


def test_validate_bazel_workspace_nonexistent_directory():
    """Test validation with non-existent directory."""
    assert validate_bazel_workspace("/path/that/does/not/exist") is False
