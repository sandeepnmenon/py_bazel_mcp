#!/bin/bash
# Generate MCP configuration for different editors

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BAZEL_REPO="${1:-/path/to/your/bazel/repo}"

echo "========================================="
echo "  MCP Configuration Generator"
echo "========================================="
echo ""
echo "Bazel MCP Server Directory: $SCRIPT_DIR"
echo "Target Bazel Repository: $BAZEL_REPO"
echo ""

# Warp Configuration
echo "📋 WARP CONFIGURATION"
echo "-------------------------------------"
echo "Paste this into Warp → Warp Drive → MCP Servers → + Add:"
echo ""
cat <<EOF
{
  "bazel-mcp": {
    "command": "python3",
    "args": ["-m", "bazel_mcp.server", "--repo", "$BAZEL_REPO"],
    "working_directory": "$SCRIPT_DIR",
    "env": {
      "PYTHONPATH": "$SCRIPT_DIR/src"
    }
  }
}
EOF
echo ""
echo ""

# VS Code Configuration
echo "📋 VS CODE CONFIGURATION"
echo "-------------------------------------"
echo "Create .vscode/mcp.json in your Bazel repository:"
echo ""
cat <<EOF
{
  "mcpServers": {
    "bazel-mcp": {
      "command": "python3",
      "args": ["-m", "bazel_mcp.server", "--repo", "\${workspaceFolder}"],
      "working_directory": "$SCRIPT_DIR",
      "env": {
        "PYTHONPATH": "$SCRIPT_DIR/src"
      }
    }
  }
}
EOF
echo ""
echo ""

# Cursor Configuration
echo "📋 CURSOR CONFIGURATION"
echo "-------------------------------------"
echo "Settings → MCP Servers → Add Custom Server:"
echo ""
echo "Name: bazel-mcp"
echo "Command: python3"
echo "Args: -m bazel_mcp.server --repo $BAZEL_REPO"
echo "Working Directory: $SCRIPT_DIR"
echo "Environment Variables:"
echo "  PYTHONPATH=$SCRIPT_DIR/src"
echo ""
echo ""

echo "========================================="
echo "Usage: $0 [bazel-repo-path]"
echo ""
echo "Example: $0 /home/user/my-bazel-project"
echo "========================================="