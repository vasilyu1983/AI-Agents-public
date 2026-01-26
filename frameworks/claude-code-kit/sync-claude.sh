#!/bin/bash

# Sync agents, commands, hooks, and skills to .claude folder
# Does NOT overwrite settings.local.json (preserves project-specific config)
#
# Usage: ./sync-claude-codex.sh [target-project-root]
#
# If no target specified, uses current directory

set -euo pipefail

# Source directories (absolute paths to AI-Agents repo)
AI_AGENTS_ROOT="/Users/vasiliyuvarov/Documents/AI-Agents"
FRAMEWORK_DIR="$AI_AGENTS_ROOT/frameworks/claude-code-kit/framework"
SKILLS_SOURCE="$AI_AGENTS_ROOT/frameworks/shared-skills/skills"

# Target directory (argument or current directory)
TARGET_ROOT="${1:-.}"
TARGET_ROOT="$(cd "$TARGET_ROOT" && pwd)"

# Target .claude subdirectories
CLAUDE_DIR="$TARGET_ROOT/.claude"

echo "=========================================="
echo "Claude Code Sync Script (no settings)"
echo "=========================================="
echo "Target: $TARGET_ROOT"
echo ""

# Verify source directories exist
for dir in "$FRAMEWORK_DIR/agents" "$FRAMEWORK_DIR/commands" "$FRAMEWORK_DIR/hooks" "$SKILLS_SOURCE"; do
    if [ ! -d "$dir" ]; then
        echo "Error: Source directory not found: $dir"
        exit 1
    fi
done

# ==========================================
# Sync .claude folder
# ==========================================
echo "Syncing .claude folder..."

# Remove existing subfolders (preserve settings.local.json and other files)
echo "  Removing existing agents, commands, hooks, skills..."
rm -rf "$CLAUDE_DIR/agents"
rm -rf "$CLAUDE_DIR/commands"
rm -rf "$CLAUDE_DIR/hooks"
rm -rf "$CLAUDE_DIR/skills"

# Create .claude directory
mkdir -p "$CLAUDE_DIR"

# Copy agents
echo "  Copying agents..."
cp -r "$FRAMEWORK_DIR/agents" "$CLAUDE_DIR/agents"

# Copy commands
echo "  Copying commands..."
cp -r "$FRAMEWORK_DIR/commands" "$CLAUDE_DIR/commands"

# Copy hooks
echo "  Copying hooks..."
cp -r "$FRAMEWORK_DIR/hooks" "$CLAUDE_DIR/hooks"

# Make hooks executable
chmod +x "$CLAUDE_DIR/hooks/"*.sh 2>/dev/null || true

# Copy skills
echo "  Copying skills..."
cp -r "$SKILLS_SOURCE" "$CLAUDE_DIR/skills"

# Check if settings.local.json exists
if [ -f "$CLAUDE_DIR/settings.local.json" ]; then
    echo "  settings.local.json: preserved (existing)"
else
    echo "  settings.local.json: not found (run setup-claude-codex.sh for initial setup)"
fi

# ==========================================
# Summary
# ==========================================
echo ""
echo "=========================================="
echo "Sync complete!"
echo "=========================================="
echo ""
echo ".claude folder:"
echo "  - agents:   $(ls -1 "$CLAUDE_DIR/agents" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  - commands: $(ls -1 "$CLAUDE_DIR/commands" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  - hooks:    $(ls -1 "$CLAUDE_DIR/hooks" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  - skills:   $(ls -1 "$CLAUDE_DIR/skills" 2>/dev/null | wc -l | tr -d ' ') folders"
if [ -f "$CLAUDE_DIR/settings.local.json" ]; then
    echo "  - settings.local.json: ✓ (preserved)"
else
    echo "  - settings.local.json: ✗ (missing)"
fi
