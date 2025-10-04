# bazel-mcp

[![Python Version](https://img.shields.io/pypi/pyversions/bazel-mcp)](https://pypi.org/project/bazel-mcp/)
[![PyPI Version](https://img.shields.io/pypi/v/bazel-mcp)](https://pypi.org/project/bazel-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io/)

**Integrate Bazel with AI coding assistants via the Model Context Protocol**

bazel-mcp is a [Model Context Protocol](https://modelcontextprotocol.io/) server that exposes your Bazel workspace to AI assistants like Claude (in VS Code or Cursor). It enables AI assistants to understand and work with Bazel projects by providing direct access to build, test, run, and query capabilities.

## Why bazel-mcp?

- **🤖 AI-Native Development**: Let AI assistants build, test, and run Bazel targets directly
- **📦 Zero Configuration**: Automatically discovers all Bazel targets in your workspace
- **🔄 Real-time Streaming**: See build and test output as it happens
- **🎯 Smart Context**: AI understands your build graph and dependencies
- **⚡ Fast Iteration**: No context switching between AI chat and terminal

## Installation

### From PyPI (Recommended)

```bash
pip install bazel-mcp
```

### From Source

```bash
git clone https://github.com/sandeepnmenon/py_bazel_mcp
cd py_bazel_mcp
pip install -e .
```

## Quick Start

### 1. Configure Your Editor

#### VS Code (Claude Extension)

Create `.vscode/mcp.json` in your workspace:

```json
{
  "mcpServers": {
    "bazel-mcp": {
      "command": "bazel-mcp",
      "args": ["--repo", "${workspaceFolder}"]
    }
  }
}
```

#### Cursor

Add as a custom MCP server:
1. Settings → MCP Servers → Add Custom Server
2. Command: `bazel-mcp`
3. Args: `--repo /path/to/your/bazel/workspace`

### 2. Verify Setup

Ask your AI assistant:
> "Can you list all Bazel targets in this workspace?"

The assistant should use the `bazel_list_targets` tool and show your project's targets.

## Features

### 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `bazel_list_targets` | List all discovered targets grouped by type |
| `bazel_query` | Run arbitrary Bazel query expressions |
| `bazel_build` | Build one or more targets with streaming output |
| `bazel_run` | Run a binary target with arguments |
| `bazel_test` | Run tests with optional filters |
| `repo_setup` | Run project setup scripts |

### 📚 Resources

- **`bazel://targets`**: Returns a JSON snapshot of all discovered targets in your workspace

### 🔒 Security Features

- **Input Validation**: All inputs are validated to prevent command injection attacks
- **Structured Output**: Consistent JSON responses with timing and metrics
- **Resource Limits**: Protects against DoS with reasonable limits on input sizes
- **Workspace Validation**: Only runs in legitimate Bazel workspaces

See [SECURITY.md](SECURITY.md) for comprehensive security documentation.

## Usage Examples

### Building and Testing

> "Build the server binary"

```python
# AI will use:
bazel_build(targets=["//apps:server"])
```

> "Run all tests matching 'Vector' in the math library"

```python
# AI will use:
bazel_test(
    targets=["//lib/math:all"],
    flags=["--test_filter=Vector.*"]
)
```

### Dependency Analysis

> "What depends on the database library?"

```python
# AI will use:
bazel_query(expr="rdeps(//..., //lib:database)")
```

> "Show me the build graph for the main app"

```python
# AI will use:
bazel_query(expr="deps(//main:app)")
```

### Running Binaries

> "Run the CLI tool with port 8080"

```python
# AI will use:
bazel_run(
    target="//tools:cli",
    args=["--port=8080"]
)
```

## API Documentation

### Tool Reference

<details>
<summary><b>bazel_list_targets</b> - List all discovered targets</summary>

**Parameters:**
- `refresh` (bool, optional): Force re-discovery of targets

**Returns:** Structured JSON response:
```json
{
  "success": true,
  "timestamp": "2025-10-04T12:00:00",
  "repoRoot": "/path/to/workspace",
  "kinds": {
    "cc_library": ["//lib:common", "//lib:utils"],
    "cc_binary": ["//src:app"]
  },
  "elapsed_seconds": 0.523
}
```
</details>

<details>
<summary><b>bazel_query</b> - Run Bazel query expressions</summary>

**Parameters:**
- `expr` (str, required): Bazel query expression
- `flags` (list, optional): Additional Bazel flags

**Example:**
```python
bazel_query(expr="deps(//main:app)")
bazel_query(expr="kind('cc_test', //...)", flags=["--output=label_kind"])
```
</details>

<details>
<summary><b>bazel_build</b> - Build targets</summary>

**Parameters:**
- `targets` (list, required): Target labels to build
- `flags` (list, optional): Bazel build flags

**Example:**
```python
bazel_build(targets=["//src:lib", "//apps:server"])
bazel_build(targets=["//..."], flags=["--config=debug"])
```
</details>

<details>
<summary><b>bazel_run</b> - Run a binary target</summary>

**Parameters:**
- `target` (str, required): Binary target label
- `args` (list, optional): Arguments for the binary
- `flags` (list, optional): Bazel run flags

**Example:**
```python
bazel_run(target="//tools:cli", args=["--port=8080"])
```
</details>

<details>
<summary><b>bazel_test</b> - Run tests</summary>

**Parameters:**
- `targets` (list, optional): Test targets (default: `//...`)
- `flags` (list, optional): Test flags

**Example:**
```python
bazel_test(targets=["//tests:unit_tests"])
bazel_test(targets=["//..."], flags=["--test_filter=MyTest.*"])
```
</details>

<details>
<summary><b>repo_setup</b> - Run setup scripts</summary>

**Parameters:**
- `skipInstall` (bool, optional): Skip install scripts

**Runs (if present):**
- `./tools/setup_cache.sh`
- `./install/install_all.sh`
</details>

## Advanced Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `BAZEL_PATH` | Path to Bazel executable | `bazel` |
| `BAZELISK` | Use Bazelisk if available | auto-detect |
| `PYTHONPATH` | Python module search path | Required for source installs |

### Using Bazelisk (Recommended)

Bazelisk automatically manages Bazel versions:

```bash
# Install Bazelisk
wget -O bazelisk https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64
chmod +x bazelisk
sudo mv bazelisk /usr/local/bin/bazel

# bazel-mcp will automatically detect and use it
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No module named 'mcp'" | Install with `pip install bazel-mcp` |
| "Not a valid Bazel repository" | The server must be run from a directory containing `WORKSPACE`, `WORKSPACE.bazel`, or `MODULE.bazel`. Check your `--repo` path. |
| "bazel query failed" | Ensure you're in a Bazel workspace (has `WORKSPACE` or `MODULE.bazel`) |
| Editor not detecting server | Restart editor after configuration |
| Logs not streaming | Add `--verbose_failures` flag to see detailed output |

## Development

### Setting up for Development

```bash
git clone https://github.com/sandeepnmenon/py_bazel_mcp
cd py_bazel_mcp
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
py_bazel_mcp/
├── src/bazel_mcp/
│   ├── __init__.py
│   ├── server.py      # MCP server implementation
│   ├── bazel.py       # Bazel command wrappers
│   ├── targets.py     # Target discovery & caching
│   └── util.py        # Utility functions
├── tests/             # Unit tests
├── pyproject.toml     # Package configuration
└── README.md          # Documentation
```

## Contributing

Contributions are welcome!

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Reporting Issues

Please report issues on our [GitHub Issues](https://github.com/sandeepnmenon/py_bazel_mcp/issues) page. Include:
- Your environment (OS, Python version, Bazel version)
- Steps to reproduce
- Expected vs actual behavior

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol that makes this possible
- [Bazel](https://bazel.build/) - The build system we're integrating with
- The MCP community for inspiration and examples

## Links

- **Documentation**: [GitHub Wiki](https://github.com/sandeepnmenon/py_bazel_mcp/wiki)
- **PyPI Package**: [bazel-mcp](https://pypi.org/project/bazel-mcp/)
- **Issue Tracker**: [GitHub Issues](https://github.com/sandeepnmenon/py_bazel_mcp/issues)


---

*Built for developers using Bazel and AI assistants*
