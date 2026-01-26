#!/bin/bash

# Setup complete .claude folder with agents, commands, hooks, skills, and settings
# Usage: ./setup-claude-codex.sh [target-project-root]
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
echo "Claude Code Setup Script"
echo "=========================================="
echo "Target: $TARGET_ROOT"
echo ""

# Verify source directories exist
for dir in "$FRAMEWORK_DIR/agents" "$FRAMEWORK_DIR/commands" "$FRAMEWORK_DIR/hooks" "$FRAMEWORK_DIR/settings" "$SKILLS_SOURCE"; do
    if [ ! -d "$dir" ]; then
        echo "Error: Source directory not found: $dir"
        exit 1
    fi
done

if [ ! -f "$FRAMEWORK_DIR/settings/settings-template.json" ]; then
    echo "Error: Settings template not found"
    exit 1
fi

# ==========================================
# Setup .claude folder
# ==========================================
echo "Setting up .claude folder..."

# Remove existing subfolders (but preserve .claude if it has other files)
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

# Copy settings template as settings.local.json
echo "  Copying settings.local.json..."
cp "$FRAMEWORK_DIR/settings/settings-template.json" "$CLAUDE_DIR/settings.local.json"

# ==========================================
# Summary
# ==========================================
echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo ".claude folder:"
echo "  - agents:   $(ls -1 "$CLAUDE_DIR/agents" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  - commands: $(ls -1 "$CLAUDE_DIR/commands" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  - hooks:    $(ls -1 "$CLAUDE_DIR/hooks" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  - skills:   $(ls -1 "$CLAUDE_DIR/skills" 2>/dev/null | wc -l | tr -d ' ') folders"
echo "  - settings.local.json: ✓"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code for settings to take effect"
echo "  2. Review .claude/settings.local.json for project-specific tweaks"
echo "  3. Add project-specific excludedCommands if needed (vercel, firebase, etc.)"
