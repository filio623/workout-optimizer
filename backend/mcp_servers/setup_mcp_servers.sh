#!/bin/bash
# Setup script for MCP servers
# Run this after cloning the repo to install MCP server dependencies

set -e  # Exit on error

echo "🔧 Setting up MCP servers..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "   Please install Node.js v20 or higher from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js $(node --version) detected"

# Install hevy-mcp dependencies
echo ""
echo "📦 Installing hevy-mcp dependencies..."
cd "$(dirname "$0")/hevy-mcp"

if [ -f "package.json" ]; then
    npm install
    echo "✅ hevy-mcp dependencies installed"
else
    echo "❌ Error: package.json not found in hevy-mcp directory"
    exit 1
fi

echo ""
echo "🎉 MCP servers setup complete!"
echo ""
echo "You can now run: python -m backend.test_mcp_connection"
