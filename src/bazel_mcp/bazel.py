"""Bazel command execution wrappers."""
from __future__ import annotations
import asyncio
from typing import Sequence
from .util import which_bazel


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
    """
    bazel = which_bazel()
    args = [bazel, "query", expr]
    if flags:
        args.extend(flags)
    
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
    """
    bazel = which_bazel()
    args = ["build", *targets]
    if flags:
        args.extend(flags)
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
    """
    bazel = which_bazel()
    args = ["test", *targets]
    if flags:
        args.extend(flags)
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
    """
    bazel = which_bazel()
    if flags:
        # Bazel flags must appear before --
        args = ["run", target, *flags, "--", *runtime_args]
    else:
        args = ["run", target, "--", *runtime_args]
    return await spawn_stream(bazel, args, cwd)