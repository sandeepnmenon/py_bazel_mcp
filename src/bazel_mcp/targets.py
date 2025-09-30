"""Bazel target discovery and caching."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List
from .bazel import run_query
from .util import DEFAULT_KINDS


@dataclass
class TargetList:
    """Container for discovered Bazel targets."""
    timestamp: str
    repoRoot: str
    kinds: Dict[str, List[str]]
    all: List[str]


async def discover_targets(repo_root: str) -> TargetList:
    """
    Discover all Bazel targets in the repository by kind.
    
    Queries the repository for each target kind defined in DEFAULT_KINDS
    and aggregates results.
    
    Args:
        repo_root: Path to Bazel workspace root
        
    Returns:
        TargetList containing discovered targets grouped by kind
    """
    kinds: Dict[str, List[str]] = {}
    
    # Query each target kind
    for k in DEFAULT_KINDS:
        expr = f"kind('{k}', //...)"
        try:
            kinds[k] = await run_query(expr, cwd=repo_root)
        except Exception as e:
            # If query fails for a kind, set empty list and continue
            print(f"Warning: Failed to query {k}: {e}")
            kinds[k] = []
    
    # Deduplicate and sort all targets
    all_targets = sorted({t for arr in kinds.values() for t in arr})
    
    return TargetList(
        timestamp=datetime.now(timezone.utc).isoformat(),
        repoRoot=repo_root,
        kinds=kinds,
        all=all_targets,
    )