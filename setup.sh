#!/bin/bash
# Bazel MCP Server - Ubuntu Setup Script

set -e  # Exit on error

echo "========================================="
echo "  Bazel MCP Server - Setup"
echo "========================================="
echo ""

# Check Python version
echo "🔍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3.10 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ Error: Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or later is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf .venv
fi

python3 -m venv .venv
echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install -U pip -q
echo "✅ pip upgraded"
echo ""

# Install package
echo "📥 Installing bazel-mcp package..."
pip install -e . -q
echo "✅ Package installed"
echo ""

# Verify installation
echo "✅ Verifying installation..."
if ! python -c "import bazel_mcp" 2>/dev/null; then
    echo "❌ Error: Package import failed"
    exit 1
fi

if ! bazel-mcp --help > /dev/null 2>&1; then
    echo "❌ Error: bazel-mcp command not working"
    exit 1
fi

echo "✅ Installation verified"
echo ""

# Check for Bazel
echo "🔍 Checking for Bazel installation..."
if command -v bazel &> /dev/null; then
    BAZEL_VERSION=$(bazel version 2>/dev/null | grep "Build label" || echo "unknown")
    echo "✅ Bazel found: $BAZEL_VERSION"
else
    echo "⚠️  Warning: Bazel not found in PATH"
    echo ""
    echo "To install Bazelisk (recommended):"
    echo "  wget -O bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64"
    echo "  chmod +x bazel && sudo mv bazel /usr/local/bin/bazel"
fi
echo ""

# Summary
echo "========================================="
echo "  ✅ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Test the server:"
echo "   bazel-mcp --repo /path/to/your/bazel/repo"
echo ""
echo "3. Configure in VS Code/Cursor:"
echo "   See README.md for configuration examples"
echo ""
echo "For Warp users, add this to your MCP config:"
echo "{"
echo "  \"bazel-mcp\": {"
echo "    \"command\": \"python3\","
echo "    \"args\": [\"-m\", \"bazel_mcp.server\", \"--repo\", \"/path/to/repo\"],"
echo "    \"working_directory\": \"$(pwd)\","
echo "    \"env\": {"
echo "      \"PYTHONPATH\": \"$(pwd)/src\""
echo "    }"
echo "  }"
echo "}"
echo ""
echo "========================================="