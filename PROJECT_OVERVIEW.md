# Bazel MCP Server - Project Overview

## What is this?

A **Python-based Model Context Protocol (MCP) server** that exposes Bazel build operations as standardized tools for AI agents in VS Code, Cursor, and Warp. This allows AI assistants to discover, build, test, and run targets in your Bazel-managed C++/Python repositories.

## Project Structure

```
py_bazel_mcp/
├── src/bazel_mcp/          # Main package
│   ├── __init__.py         # Package initialization
│   ├── server.py           # MCP server implementation
│   ├── bazel.py            # Bazel command wrappers (query, build, run, test)
│   ├── targets.py          # Target discovery and caching
│   └── util.py             # Helper utilities
├── .vscode/                # VS Code configuration
│   └── mcp.json            # Example MCP configuration
├── pyproject.toml          # Python package metadata
├── setup.sh                # Automated installation script
├── generate_mcp_config.sh  # Configuration generator
├── README.md               # Full documentation
├── QUICKSTART.md           # Quick start guide
├── LICENSE                 # MIT License
└── .gitignore              # Git ignore rules
```

## Key Components

### 1. `server.py` - MCP Server Core
- Implements MCP protocol using `mcp` Python library
- Exposes 6 MCP tools and 1 resource
- Handles async Bazel command execution
- Streams build/test logs to agents
- Validates Bazel workspace on startup

### 2. `bazel.py` - Bazel Operations
- `run_query()` - Execute Bazel query expressions
- `run_build()` - Build targets
- `run_test()` - Run tests
- `run_binary()` - Execute binary targets
- All operations are async and support custom flags

### 3. `targets.py` - Target Discovery
- Auto-discovers targets by kind (cc_*, py_*)
- Caches results to avoid repeated queries
- Returns structured JSON with target metadata
- Supports refresh on demand

### 4. `util.py` - Configuration
- `which_bazel()` - Detects Bazel/Bazelisk executable
- `DEFAULT_KINDS` - Configurable target kinds to discover

## MCP Tools Exposed

| Tool | Purpose | Required Args | Optional Args |
|------|---------|--------------|---------------|
| `bazel_list_targets` | List all targets by kind | - | `refresh` |
| `bazel_query` | Run Bazel query | `expr` | `flags` |
| `bazel_build` | Build targets | `targets` | `flags` |
| `bazel_run` | Run binary | `target` | `args`, `flags` |
| `bazel_test` | Run tests | - | `targets`, `flags` |
| `repo_setup` | Run setup scripts | - | `skipInstall` |

## MCP Resources

- **`bazel://targets`** - JSON snapshot of discovered targets with metadata

## Installation Methods

### Method 1: Automated (Recommended)
```bash
./setup.sh
source .venv/bin/activate
```

### Method 2: Manual
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

## Configuration for Different Editors

### Warp
```bash
./generate_mcp_config.sh /path/to/bazel/repo
# Copy output to Warp → Warp Drive → MCP Servers
```

### VS Code
Place `.vscode/mcp.json` in your Bazel repository with appropriate paths.

### Cursor
Use Settings → MCP Servers → Add Custom Server with generated config.

## How It Works

1. **Startup**: Server validates Bazel workspace (WORKSPACE or MODULE.bazel)
2. **Discovery**: On first `bazel_list_targets` call, queries all target kinds
3. **Caching**: Results cached in memory; refresh with `refresh: true`
4. **Execution**: Bazel commands run via `asyncio.create_subprocess_exec`
5. **Streaming**: stdout/stderr forwarded in real-time to agent
6. **Transport**: Uses MCP stdio protocol for local editor integration

## Environment Variables

- **`BAZEL_PATH`** - Override Bazel executable (default: `bazel`)
- **`BAZELISK`** - Use Bazelisk launcher
- **`PYTHONPATH`** - Must include `src/` for module resolution

## Supported Target Kinds

Default (configurable in `util.py`):
- `cc_library`
- `cc_binary`
- `cc_test`
- `py_library`
- `py_binary`
- `py_test`

To add more kinds (e.g., `go_binary`, `java_library`), edit `DEFAULT_KINDS` in `util.py`.

## Security Considerations

- Server executes arbitrary Bazel commands in specified workspace
- Only use with trusted repositories
- Uses stdio transport (local only, not exposed to network)
- Scripts in `repo_setup` tool can run arbitrary bash commands

## Performance

- **Target discovery**: ~5-30s depending on repo size (cached after first run)
- **Build/test**: Same as native Bazel (no overhead)
- **Query**: Near-instant for cached targets, ~1-5s for complex queries

## Extending the Server

### Add New Tools
1. Define tool schema in `list_tools()`
2. Add handler in `call_tool()`
3. Implement Bazel operation in `bazel.py`

### Add New Resources
1. Define resource in `list_resources()`
2. Implement read handler in `read_resource()`

### Support Additional Target Kinds
Edit `DEFAULT_KINDS` in `util.py`.

## Debugging

### Check Server Logs
- **Warp**: View via MCP Servers page → View Logs
- **VS Code/Cursor**: Check MCP extension logs

### Manual Test
```bash
source .venv/bin/activate
bazel-mcp --repo /path/to/bazel/repo
# Server starts and waits for MCP protocol messages on stdin
```

### Test Target Discovery
```python
source .venv/bin/activate
python3 -c "
import asyncio
from bazel_mcp.targets import discover_targets
print(asyncio.run(discover_targets('/path/to/repo')))
"
```

## Common Issues

### "No module named 'mcp'"
- Solution: `source .venv/bin/activate && pip install -e .`

### "bazel query failed"
- Ensure WORKSPACE/MODULE.bazel exists
- Check Bazel is in PATH: `bazel version`
- Set `BAZEL_PATH` environment variable

### Slow target discovery
- Normal for large repos (10k+ targets)
- Results are cached after first discovery
- Consider filtering to specific packages in query

### Agent can't call tools
- Verify `working_directory` and `PYTHONPATH` in MCP config
- Check MCP server is running (editor logs)
- Restart editor after configuration changes

## Dependencies

- **Python**: 3.10+
- **mcp**: >=1.2.0 (Model Context Protocol library)
- **Bazel**: Any version (Bazelisk recommended)

## License

MIT License - Free for commercial and personal use.

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests if applicable
4. Submit pull request

## Roadmap

- [ ] File watching to auto-refresh targets
- [ ] `bazel cquery` support
- [ ] Coverage and profiling tools
- [ ] Build event protocol (BEP) streaming
- [ ] Remote execution support
- [ ] Multi-workspace support
- [ ] Web UI for monitoring

## Related Resources

- [Model Context Protocol Docs](https://modelcontextprotocol.io/)
- [Bazel Query Reference](https://bazel.build/query/language)
- [Warp MCP Guide](https://www.warp.dev/university/mcp)

---

**Questions?** Open an issue on GitHub or check the documentation.
