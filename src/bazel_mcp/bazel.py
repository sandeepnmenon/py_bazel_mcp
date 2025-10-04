"""Bazel command execution wrappers."""
from __future__ import annotations
import asyncio
from typing import Sequence
from .util import which_bazel
from .validation import (
    validate_query_expression,
    validate_bazel_targets,
    validate_bazel_flags,
    validate_runtime_args,
)


async def run_query(expr: str, cwd: str, flags: Sequence[str] | None = None) -> list[str]:
    """
    Execute a Bazel query and return matching targets.
    
    Args:
        expr: Bazel query expression (e.g., "kind('cc_library', //...)")
        cwd: Working directory (Bazel workspace root)
        flags: Optional additional Bazel flags
        
    Returns:
        List of matching target labels
        
    Raises:
        RuntimeError: If query fails
        ValidationError: If inputs are invalid or potentially malicious
    """
    # Validate inputs
    expr = validate_query_expression(expr)
    validated_flags = validate_bazel_flags(flags)
    
    bazel = which_bazel()
    args = [bazel, "query", expr]
    if validated_flags:
        args.extend(validated_flags)
    
    proc = await asyncio.create_subprocess_exec(
        *args,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    
    # Decode bytes to strings
    out_str = out.decode('utf-8') if out else ''
    err_str = err.decode('utf-8') if err else ''
    
    if proc.returncode != 0:
        raise RuntimeError(f"bazel query failed (code {proc.returncode})\n{err_str}")
    
    return [line.strip() for line in out_str.splitlines() if line.strip()]


async def spawn_stream(cmd: str, args: Sequence[str], cwd: str):
    """
    Spawn a subprocess for streaming output.
    
    Args:
        cmd: Command to execute
        args: Command arguments
        cwd: Working directory
        
    Returns:
        Process handle with stdout/stderr pipes
    """
    proc = await asyncio.create_subprocess_exec(
        cmd, *args, 
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    return proc


async def run_build(targets: Sequence[str], cwd: str, flags: Sequence[str] | None = None):
    """
    Execute bazel build for one or more targets.
    
    Args:
        targets: List of Bazel target labels to build
        cwd: Working directory (Bazel workspace root)
        flags: Optional Bazel build flags
        
    Returns:
        Process handle for streaming
        
    Raises:
        ValidationError: If inputs are invalid or potentially malicious
    """
    # Validate inputs
    validated_targets = validate_bazel_targets(targets)
    validated_flags = validate_bazel_flags(flags)
    
    bazel = which_bazel()
    args = ["build", *validated_targets]
    if validated_flags:
        args.extend(validated_flags)
    return await spawn_stream(bazel, args, cwd)


async def run_test(targets: Sequence[str], cwd: str, flags: Sequence[str] | None = None):
    """
    Execute bazel test for one or more targets.
    
    Args:
        targets: List of Bazel test target labels
        cwd: Working directory (Bazel workspace root)
        flags: Optional Bazel test flags (e.g., --test_filter)
        
    Returns:
        Process handle for streaming
        
    Raises:
        ValidationError: If inputs are invalid or potentially malicious
    """
    # Validate inputs
    validated_targets = validate_bazel_targets(targets)
    validated_flags = validate_bazel_flags(flags)
    
    bazel = which_bazel()
    args = ["test", *validated_targets]
    if validated_flags:
        args.extend(validated_flags)
    return await spawn_stream(bazel, args, cwd)


async def run_binary(target: str, runtime_args: Sequence[str], cwd: str, flags: Sequence[str] | None = None):
    """
    Execute bazel run for a single binary target.
    
    Args:
        target: Bazel binary target label
        runtime_args: Arguments to pass to the binary (after --)
        cwd: Working directory (Bazel workspace root)
        flags: Optional Bazel run flags (must come before --)
        
    Returns:
        Process handle for streaming
        
    Raises:
        ValidationError: If inputs are invalid or potentially malicious
    """
    # Validate inputs
    from .validation import validate_bazel_target
    validated_target = validate_bazel_target(target)
    validated_flags = validate_bazel_flags(flags)
    validated_runtime_args = validate_runtime_args(runtime_args)
    
    bazel = which_bazel()
    if validated_flags:
        # Bazel flags must appear before --
        args = ["run", validated_target, *validated_flags, "--", *validated_runtime_args]
    else:
        args = ["run", validated_target, "--", *validated_runtime_args]
    return await spawn_stream(bazel, args, cwd)
