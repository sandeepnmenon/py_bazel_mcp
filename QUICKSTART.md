# Quick Start Guide

Get your Bazel MCP server running in under 5 minutes!

## 1. Install (30 seconds)

```bash
cd /home/s.menon/github/py_bazel_mcp
./setup.sh
```

## 2. Activate Virtual Environment

```bash
source .venv/bin/activate
```

## 3. Test the Server

```bash
# Test with help
bazel-mcp --help

# Test with a Bazel repository (replace with your actual repo path)
bazel-mcp --repo /path/to/your/bazel/repo
```

## 4. Configure in Warp (Recommended)

### For Warp Terminal Users:

1. Open **Warp** → **Warp Drive** → **MCP Servers** → Click **`+ Add`**

2. Paste this configuration (update the paths):

```json
{
  "bazel-mcp": {
    "command": "python3",
    "args": ["-m", "bazel_mcp.server", "--repo", "/path/to/your/bazel/repo"],
    "working_directory": "/home/s.menon/github/py_bazel_mcp",
    "env": {
      "PYTHONPATH": "/home/s.menon/github/py_bazel_mcp/src"
    }
  }
}
```

3. Click **Save** and **Start** the server

4. Test it by asking Warp AI: *"List all py_binary targets in my Bazel repo"*

## 5. Configure in VS Code

### For VS Code with MCP Extensions:

1. In your Bazel repository, create `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "bazel-mcp": {
      "command": "python3",
      "args": ["-m", "bazel_mcp.server", "--repo", "${workspaceFolder}"],
      "working_directory": "/home/s.menon/github/py_bazel_mcp",
      "env": {
        "PYTHONPATH": "/home/s.menon/github/py_bazel_mcp/src"
      }
    }
  }
}
```

2. Restart VS Code

3. Test with your AI assistant: *"Build the target //main:app"*

## 6. Configure in Cursor

### For Cursor IDE:

1. Open **Settings** → **MCP Servers** → **Add Custom Server**

2. Fill in:
   - **Name:** `bazel-mcp`
   - **Command:** `python3`
   - **Args:** `-m bazel_mcp.server --repo /path/to/your/bazel/repo`
   - **Working Directory:** `/home/s.menon/github/py_bazel_mcp`
   - **Environment Variables:**
     - Key: `PYTHONPATH`
     - Value: `/home/s.menon/github/py_bazel_mcp/src`

3. Save and restart Cursor

4. Test with Cursor AI: *"Run all tests in //lib/math"*

---

## Example Agent Prompts

Once configured, try these prompts with your AI assistant:

### Discovery
- *"List all cc_binary targets"*
- *"Show me all Python test files"*
- *"What are the dependencies of //main:app?"*

### Building
- *"Build //apps:server with debug flags"*
- *"Build all targets under //lib"*

### Testing
- *"Run all unit tests"*
- *"Run tests matching the pattern 'Vector.*'"*
- *"Test //services:api_test with verbose output"*

### Running
- *"Run //tools:cli with arguments --help"*
- *"Execute //apps:server with --port=8080"*

---

## Troubleshooting

### "Command not found: bazel-mcp"
```bash
source .venv/bin/activate
```

### "No module named 'mcp'"
```bash
source .venv/bin/activate
pip install -e .
```

### "Not a valid Bazel repository"
The server requires a valid Bazel workspace. Ensure your `--repo` path contains one of:
- `WORKSPACE`
- `WORKSPACE.bazel`
- `MODULE.bazel`

### "Bazel not found"
Install Bazelisk:
```bash
wget -O bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64
chmod +x bazel
sudo mv bazel /usr/local/bin/bazel
```

### Server not responding in Warp/VS Code/Cursor
1. Check the MCP server logs in your editor
2. Verify `working_directory` and `PYTHONPATH` are set correctly
3. Ensure the `--repo` path points to a valid Bazel workspace (contains WORKSPACE or MODULE.bazel)
4. Restart your editor

---

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Customize target kinds in `src/bazel_mcp/util.py`
- Add custom setup scripts to your repo (`./tools/setup_cache.sh`)
- Check out [MCP documentation](https://modelcontextprotocol.io/)

---

## Need Help?

- **GitHub Issues:** Report bugs or request features
- **MCP Docs:** https://modelcontextprotocol.io/
- **Bazel Docs:** https://bazel.build/
- **Warp MCP Guide:** https://www.warp.dev/university/mcp