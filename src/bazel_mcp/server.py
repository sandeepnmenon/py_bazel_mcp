"""Main MCP server implementation for Bazel repositories."""
from __future__ import annotations
import argparse
import asyncio
import json
import os
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
)

from .bazel import run_query, run_build, run_binary, run_test
from .targets import discover_targets, TargetList
from .util import validate_bazel_workspace


def tool(name: str, description: str, schema: Dict[str, Any]) -> Tool:
    """Helper to create a Tool definition."""
    return Tool(name=name, description=description, inputSchema=schema)


def build_server(repo_root: str) -> Server:
    """
    Build and configure the MCP server for a Bazel repository.
    
    Args:
        repo_root: Path to the Bazel workspace root
        
    Returns:
        Configured MCP Server instance
    """
    srv = Server("bazel-mcp")
    cached: TargetList | None = None

    async def ensure_targets():
        """Ensure targets are discovered and cached."""
        nonlocal cached
        if cached is None:
            cached = await discover_targets(repo_root)
        return cached

    # ========== RESOURCES ==========
    
    @srv.list_resources()
    async def list_resources() -> list[Resource]:
        """List available MCP resources."""
        await ensure_targets()
        return [Resource(
            uri="bazel://targets",
            name="Bazel Targets",
            description=f"Discovered targets for {repo_root}",
            mimeType="application/json",
        )]

    @srv.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a resource by URI."""
        if uri != "bazel://targets":
            raise ValueError(f"Unknown resource: {uri}")
        await ensure_targets()
        return json.dumps({
            "timestamp": cached.timestamp,
            "repoRoot": cached.repoRoot,
            "kinds": cached.kinds,
            "all": cached.all,
        }, indent=2)

    # ========== TOOLS ==========
    
    @srv.list_tools()
    async def list_tools() -> list[Tool]:
        """List available MCP tools."""
        return [
            tool(
                name="bazel_list_targets",
                description="List discovered Bazel targets grouped by kind (cc_library, cc_binary, py_library, etc.)",
                schema={
                    "type": "object",
                    "properties": {
                        "refresh": {
                            "type": "boolean",
                            "description": "Force refresh of target cache"
                        }
                    }
                }
            ),
            tool(
                name="bazel_query",
                description="Run a Bazel query expression and return matching targets",
                schema={
                    "type": "object",
                    "required": ["expr"],
                    "properties": {
                        "expr": {
                            "type": "string",
                            "description": "Bazel query expression (e.g., 'deps(//main:app)')"
                        },
                        "flags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Additional Bazel flags"
                        }
                    }
                }
            ),
            tool(
                name="bazel_build",
                description="Build one or more Bazel targets (streams logs)",
                schema={
                    "type": "object",
                    "required": ["targets"],
                    "properties": {
                        "targets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Bazel target labels to build"
                        },
                        "flags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Additional Bazel build flags"
                        }
                    }
                }
            ),
            tool(
                name="bazel_run",
                description="Run a single Bazel binary target with arguments (streams logs)",
                schema={
                    "type": "object",
                    "required": ["target"],
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "Bazel binary target label"
                        },
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Runtime arguments to pass to the binary"
                        },
                        "flags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Bazel run flags (before --)"
                        }
                    }
                }
            ),
            tool(
                name="bazel_test",
                description="Run Bazel tests (supports --test_filter via flags; streams logs)",
                schema={
                    "type": "object",
                    "properties": {
                        "targets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Test target labels (default: //...)"
                        },
                        "flags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Bazel test flags (e.g., --test_filter=MyTest.*)"
                        }
                    }
                }
            ),
            tool(
                name="repo_setup",
                description="Run project setup scripts if present (./tools/setup_cache.sh, ./install/install_all.sh)",
                schema={
                    "type": "object",
                    "properties": {
                        "skipInstall": {
                            "type": "boolean",
                            "description": "Skip running install scripts"
                        }
                    }
                }
            ),
        ]

    # ========== TOOL HANDLERS ==========
    
    async def stream_process(proc, tool_name: str) -> int:
        """
        Stream stdout/stderr from a process.
        
        Args:
            proc: Process handle
            tool_name: Name of the tool (for logging)
            
        Returns:
            Process exit code
        """
        async def forward_stream(stream, prefix: str):
            """Forward stream lines with prefix."""
            while True:
                line = await stream.readline()
                if not line:
                    break
                # Decode bytes to string
                line_str = line.decode('utf-8') if isinstance(line, bytes) else line
                print(f"{prefix}: {line_str.rstrip()}", flush=True)
        
        await asyncio.gather(
            forward_stream(proc.stdout, "OUT"),
            forward_stream(proc.stderr, "ERR"),
        )
        await proc.wait()
        return proc.returncode

    @srv.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool invocations."""
        nonlocal cached
        
        if name == "bazel_list_targets":
            refresh = arguments.get("refresh", False)
            if refresh:
                cached = None
            data = await ensure_targets()
            return [TextContent(
                type="text",
                text=json.dumps({
                    "timestamp": data.timestamp,
                    "repoRoot": data.repoRoot,
                    "kinds": data.kinds,
                    "all": data.all,
                }, indent=2)
            )]
        
        elif name == "bazel_query":
            expr = arguments["expr"]
            flags = arguments.get("flags", [])
            results = await run_query(expr, cwd=repo_root, flags=flags)
            return [TextContent(
                type="text",
                text="\n".join(results) if results else "(no matches)"
            )]
        
        elif name == "bazel_build":
            targets = arguments["targets"]
            flags = arguments.get("flags", ["--color=no", "--curses=no"])
            proc = await run_build(targets, cwd=repo_root, flags=flags)
            code = await stream_process(proc, "bazel_build")
            return [TextContent(
                type="text",
                text=f"Build completed with exit code: {code}"
            )]
        
        elif name == "bazel_run":
            target = arguments["target"]
            run_args = arguments.get("args", [])
            flags = arguments.get("flags", ["--color=no", "--curses=no"])
            proc = await run_binary(target, runtime_args=run_args, cwd=repo_root, flags=flags)
            code = await stream_process(proc, "bazel_run")
            return [TextContent(
                type="text",
                text=f"Run completed with exit code: {code}"
            )]
        
        elif name == "bazel_test":
            targets = arguments.get("targets", ["//..."])
            flags = arguments.get("flags", ["--color=no", "--curses=no"])
            proc = await run_test(targets, cwd=repo_root, flags=flags)
            code = await stream_process(proc, "bazel_test")
            return [TextContent(
                type="text",
                text=f"Tests completed with exit code: {code}"
            )]
        
        elif name == "repo_setup":
            skip_install = arguments.get("skipInstall", False)
            scripts = ["./tools/setup_cache.sh"]
            if not skip_install:
                scripts.append("./install/install_all.sh")
            
            for script in scripts:
                script_path = os.path.join(repo_root, script)
                if not os.path.exists(script_path):
                    print(f"Skipping {script} (not found)")
                    continue
                
                print(f"Running {script}...")
                proc = await asyncio.create_subprocess_exec(
                    "bash", "-lc", script,
                    cwd=repo_root,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await stream_process(proc, "repo_setup")
            
            # Refresh cache after setup
            cached = None
            return [TextContent(
                type="text",
                text="Setup completed successfully"
            )]
        
        else:
            raise ValueError(f"Unknown tool: {name}")

    return srv


async def run_server(repo_root: str):
    """Run the MCP server with stdio transport."""
    srv = build_server(repo_root)
    async with stdio_server() as (read_stream, write_stream):
        await srv.run(
            read_stream,
            write_stream,
            srv.create_initialization_options()
        )


def main():
    """Main entry point for the Bazel MCP server."""
    parser = argparse.ArgumentParser(
        description="Bazel MCP Server - Expose Bazel commands as MCP tools"
    )
    parser.add_argument(
        "--repo",
        default=os.getcwd(),
        help="Path to Bazel workspace root (default: current directory)"
    )
    args = parser.parse_args()

    # Validate repo path
    repo_root = os.path.abspath(args.repo)
    if not os.path.isdir(repo_root):
        print(f"Error: {repo_root} is not a valid directory", flush=True)
        return 1
    
    # Check for WORKSPACE or MODULE.bazel file
    if not validate_bazel_workspace(repo_root):
        print(f"Error: Not a valid Bazel repository.", flush=True)
        print(f"No WORKSPACE or MODULE.bazel file found in {repo_root}", flush=True)
        print("\nPlease run this server from a Bazel workspace root directory.", flush=True)
        print("Expected files: WORKSPACE, WORKSPACE.bazel, or MODULE.bazel", flush=True)
        return 1
    
    print(f"Starting Bazel MCP server for: {repo_root}", flush=True)
    
    asyncio.run(run_server(repo_root))


if __name__ == "__main__":
    exit(main() or 0)