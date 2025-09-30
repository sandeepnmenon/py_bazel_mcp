# Bazel MCP Server

A **Model Context Protocol (MCP)** server that exposes your Bazel-managed repository as MCP tools for AI agents in **VS Code** and **Cursor**. Turn your large C++/Python Bazel repo into an AI-friendly interface with minimal setup.

## Features

🎯 **Auto-discovery** — Point at your Bazel repo; targets are automatically discovered  
🔧 **MCP Tools** — Build, run, test, and query via standardized MCP interface  
📦 **Target kinds** — Supports `cc_library`, `cc_binary`, `cc_test`, `py_library`, `py_binary`, `py_test`  
🚀 **Streaming logs** — Real-time build/test output streamed to your agent  
⚙️ **Setup automation** — Optional `repo_setup` tool for custom init scripts  
🐧 **Ubuntu-ready** — Turnkey installation on Ubuntu with Python 3.10+

---

## Quick Start (Ubuntu)

### 1. Install

```bash
# Clone the repository
git clone <your-repo-url> bazel-mcp
cd bazel-mcp

# Run the setup script
./setup.sh
```

This creates a virtual environment, installs dependencies, and sets up the `bazel-mcp` command.

### 2. Verify Installation

```bash
# Activate the virtual environment
source .venv/bin/activate

# Test the server
bazel-mcp --help
```

### 3. Configure in VS Code / Cursor

#### Option A: VS Code with Warp

If you're using [Warp](https://www.warp.dev/), add to Warp's MCP settings:

1. Open Warp → Warp Drive → MCP Servers → `+ Add`
2. Paste this JSON:

```json
{
  "bazel-mcp": {
    "command": "python3",
    "args": ["-m", "bazel_mcp.server", "--repo", "/path/to/your/bazel/repo"],
    "working_directory": "/home/you/github/py_bazel_mcp",
    "env": {
      "PYTHONPATH": "/home/you/github/py_bazel_mcp/src"
    }
  }
}
```

**Important:** Replace `/path/to/your/bazel/repo` with your actual Bazel workspace path.

#### Option B: VS Code (Claude or other MCP-enabled extensions)

Create or update `.vscode/mcp.json` in your Bazel repository:

```json
{
  "mcpServers": {
    "bazel-mcp": {
      "command": "python3",
      "args": ["-m", "bazel_mcp.server", "--repo", "${workspaceFolder}"],
      "working_directory": "/home/you/github/py_bazel_mcp",
      "env": {
        "PYTHONPATH": "/home/you/github/py_bazel_mcp/src"
      }
    }
  }
}
```

#### Option C: Cursor

In Cursor, add a **Custom MCP Server**:

1. Open Settings → MCP Servers → Add Custom Server
2. **Command:** `python3`
3. **Args:** `-m bazel_mcp.server --repo /path/to/your/bazel/repo`
4. **Working Directory:** `/home/you/github/py_bazel_mcp`
5. **Environment Variables:**
   - `PYTHONPATH`: `/home/you/github/py_bazel_mcp/src`

---

## MCP Tools

Once configured, your AI agent can use these tools:

### `bazel_list_targets`

List all discovered targets grouped by kind.

**Parameters:**
- `refresh` (boolean, optional): Force re-discovery of targets

**Example:**
```json
{
  "refresh": true
}
```

**Returns:** JSON with `cc_library`, `cc_binary`, `py_library`, `py_binary`, `cc_test`, `py_test` arrays.

---

### `bazel_query`

Run arbitrary Bazel query expressions.

**Parameters:**
- `expr` (string, required): Bazel query expression
- `flags` (array, optional): Additional Bazel flags

**Examples:**
```json
{
  "expr": "deps(//main:app)"
}
```

```json
{
  "expr": "kind('cc_test', //...)",
  "flags": ["--output=label_kind"]
}
```

---

### `bazel_build`

Build one or more targets.

**Parameters:**
- `targets` (array, required): Target labels to build
- `flags` (array, optional): Bazel build flags

**Example:**
```json
{
  "targets": ["//src:my_library", "//apps:server"],
  "flags": ["--config=debug", "--verbose_failures"]
}
```

---

### `bazel_run`

Run a single binary target with arguments.

**Parameters:**
- `target` (string, required): Binary target label
- `args` (array, optional): Runtime arguments passed to the binary
- `flags` (array, optional): Bazel run flags (before `--`)

**Example:**
```json
{
  "target": "//tools:cli",
  "args": ["--port=8080", "--verbose"],
  "flags": ["--config=local"]
}
```

---

### `bazel_test`

Run tests with optional filters.

**Parameters:**
- `targets` (array, optional): Test targets (default: `//...`)
- `flags` (array, optional): Test flags (e.g., `--test_filter`)

**Examples:**
```json
{
  "targets": ["//tests:unit_tests"]
}
```

```json
{
  "targets": ["//..."],
  "flags": ["--test_filter=MyTestSuite.*", "--test_output=errors"]
}
```

---

### `repo_setup`

Run project setup scripts if present:
- `./tools/setup_cache.sh`
- `./install/install_all.sh`

**Parameters:**
- `skipInstall` (boolean, optional): Skip install scripts

**Example:**
```json
{
  "skipInstall": false
}
```

---

## MCP Resources

### `bazel://targets`

Returns JSON snapshot of discovered targets.

**Schema:**
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "repoRoot": "/path/to/repo",
  "kinds": {
    "cc_library": ["//lib:math", "//lib:utils"],
    "py_binary": ["//tools:cli"]
  },
  "all": ["//lib:math", "//lib:utils", "//tools:cli"]
}
```

---

## Environment Variables

- **`BAZEL_PATH`**: Override Bazel executable path (default: `bazel`)
- **`BAZELISK`**: Use Bazelisk launcher (recommended)
- **`PYTHONPATH`**: Must include `src` directory for module resolution

---

## Manual Installation (without setup.sh)

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install -U pip

# Install package in editable mode
pip install -e .
```

---

## Installing Bazelisk (Recommended)

Bazelisk automatically downloads and manages Bazel versions:

```bash
# Download for Linux
wget -O bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64

# Make executable and move to PATH
chmod +x bazel
sudo mv bazel /usr/local/bin/bazel

# Verify
bazel version
```

---

## Usage Examples (Agent Prompts)

**Example 1: List all Python binaries**
> "List all py_binary targets in the repo"

Agent calls:
```json
{
  "tool": "bazel_list_targets",
  "arguments": {}
}
```

**Example 2: Build a specific target**
> "Build the server binary at //apps:server"

Agent calls:
```json
{
  "tool": "bazel_build",
  "arguments": {
    "targets": ["//apps:server"]
  }
}
```

**Example 3: Run tests matching a pattern**
> "Run all tests in //lib/math that match Vector.*"

Agent calls:
```json
{
  "tool": "bazel_test",
  "arguments": {
    "targets": ["//lib/math:all"],
    "flags": ["--test_filter=Vector.*"]
  }
}
```

**Example 4: Query dependencies**
> "What are the dependencies of //main:app?"

Agent calls:
```json
{
  "tool": "bazel_query",
  "arguments": {
    "expr": "deps(//main:app)"
  }
}
```

---

## Troubleshooting

### "No module named 'mcp'"

Make sure you've activated the virtual environment and installed dependencies:
```bash
source .venv/bin/activate
pip install -e .
```

### "bazel query failed"

- Ensure you're pointing to a valid Bazel workspace (contains `WORKSPACE` or `MODULE.bazel`)
- Check that Bazel is installed: `bazel version`
- Try setting `BAZEL_PATH` or `BAZELISK` environment variables

### VS Code / Cursor not detecting MCP server

- Verify `working_directory` and `PYTHONPATH` are set correctly in your MCP config
- Check MCP server logs (see your editor's MCP documentation)
- Restart your editor after adding the configuration

### Logs not streaming

The server uses `--color=no --curses=no` by default. If you need more verbose output, pass custom flags:
```json
{
  "tool": "bazel_build",
  "arguments": {
    "targets": ["//..."],
    "flags": ["--verbose_failures", "--announce_rc"]
  }
}
```

---

## Architecture

```
bazel-mcp/
├── src/bazel_mcp/
│   ├── server.py      # MCP server implementation
│   ├── bazel.py       # Bazel command wrappers
│   ├── targets.py     # Target discovery & caching
│   └── util.py        # Helper functions
├── pyproject.toml     # Package metadata
└── setup.sh           # Installation script
```

**Key Design Decisions:**

1. **Target caching** — Initial discovery is cached; use `refresh: true` to rescan
2. **Streaming** — Build/run/test logs stream to stdout/stderr in real-time
3. **Async** — All Bazel operations use `asyncio` for non-blocking execution
4. **stdio transport** — Uses MCP stdio protocol for local editor integration

---

## Future Enhancements

- [ ] Watch mode with file system monitoring (auto-refresh targets)
- [ ] `cquery` support for configuration-aware queries
- [ ] Coverage and benchmark tools (`bazel coverage`, `bazel bench`)
- [ ] Build graph visualization resource
- [ ] Multi-repo support (external workspaces)
- [ ] Remote execution support (RBE)

---

## Contributing

Contributions welcome! Please open an issue or PR.

---

## License

MIT License - see LICENSE file for details.

---

## Related Resources

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Bazel Documentation](https://bazel.build/)
- [Warp MCP Guide](https://www.warp.dev/university/mcp)
- [VS Code MCP Extensions](https://marketplace.visualstudio.com/)