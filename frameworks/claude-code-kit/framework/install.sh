#!/bin/bash
# Claude Code Kit - One-Command Install Script
# Copies production-ready agents, skills, commands, hooks, and settings to your project
#
# Usage:
#   cd your-project/
#   /path/to/install.sh
#
# Or with curl:
#   curl -fsSL https://raw.githubusercontent.com/your-repo/framework/install.sh | bash

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Claude Code Kit - Installation${NC}"
echo "=================================="

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_SKILLS_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)/shared-skills/skills"

# Target is current directory
TARGET_DIR="$(pwd)"

# Check if .claude already exists
if [ -d "$TARGET_DIR/.claude" ]; then
    echo -e "${YELLOW}Warning: .claude/ directory already exists${NC}"
    read -p "Overwrite existing files? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Create directory structure
echo -e "\n${GREEN}Creating .claude/ directory structure...${NC}"
mkdir -p "$TARGET_DIR/.claude/agents"
mkdir -p "$TARGET_DIR/.claude/commands"
mkdir -p "$TARGET_DIR/.claude/hooks"
mkdir -p "$TARGET_DIR/.claude/skills"
mkdir -p "$TARGET_DIR/.claude/logs"

# Copy agents
echo -e "${GREEN}Copying agents (21 files)...${NC}"
cp "$SCRIPT_DIR/agents/"*.md "$TARGET_DIR/.claude/agents/" 2>/dev/null || true
AGENT_COUNT=$(ls "$TARGET_DIR/.claude/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')
echo "  Copied $AGENT_COUNT agents"

# Copy commands
echo -e "${GREEN}Copying commands (28 files)...${NC}"
cp "$SCRIPT_DIR/commands/"*.md "$TARGET_DIR/.claude/commands/" 2>/dev/null || true
COMMAND_COUNT=$(ls "$TARGET_DIR/.claude/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')
echo "  Copied $COMMAND_COUNT commands"

# Copy hooks
echo -e "${GREEN}Copying hooks (7 scripts + docs)...${NC}"
cp "$SCRIPT_DIR/hooks/"*.sh "$TARGET_DIR/.claude/hooks/" 2>/dev/null || true
cp "$SCRIPT_DIR/hooks/.env.example" "$TARGET_DIR/.claude/hooks/" 2>/dev/null || true
chmod +x "$TARGET_DIR/.claude/hooks/"*.sh
HOOK_COUNT=$(ls "$TARGET_DIR/.claude/hooks/"*.sh 2>/dev/null | wc -l | tr -d ' ')
echo "  Copied $HOOK_COUNT hook scripts (made executable)"

# Copy skills from shared-skills
echo -e "${GREEN}Copying skills from shared-skills (76 directories)...${NC}"
if [ -d "$SHARED_SKILLS_DIR" ]; then
    cp -r "$SHARED_SKILLS_DIR/"* "$TARGET_DIR/.claude/skills/" 2>/dev/null || true
    SKILL_COUNT=$(ls -d "$TARGET_DIR/.claude/skills/"*/ 2>/dev/null | wc -l | tr -d ' ')
    echo "  Copied $SKILL_COUNT skills"
else
    echo -e "  ${YELLOW}Warning: shared-skills not found at $SHARED_SKILLS_DIR${NC}"
    echo -e "  ${YELLOW}Copy skills manually: cp -r frameworks/shared-skills/skills/* .claude/skills/${NC}"
    SKILL_COUNT=0
fi

# Copy settings
echo -e "${GREEN}Copying settings...${NC}"
if [ -f "$SCRIPT_DIR/settings/settings.json" ]; then
    cp "$SCRIPT_DIR/settings/settings.json" "$TARGET_DIR/.claude/settings.json"
    echo "  Copied settings.json"
else
    echo -e "  ${YELLOW}Warning: settings.json not found, using template${NC}"
    cp "$SCRIPT_DIR/settings/settings-template.json" "$TARGET_DIR/.claude/settings.json"
fi

# Summary
echo -e "\n${GREEN}Installation Complete!${NC}"
echo "=================================="
echo "Installed to: $TARGET_DIR/.claude/"
echo ""
echo "Components:"
echo "  - $AGENT_COUNT agents"
echo "  - $COMMAND_COUNT commands"
echo "  - $HOOK_COUNT hooks"
echo "  - $SKILL_COUNT skills"
echo "  - settings.json"
echo ""
echo -e "${GREEN}Quick Start:${NC}"
echo "  1. Review .claude/settings.json"
echo "  2. Test hooks: ls -la .claude/hooks/*.sh"
echo "  3. Use commands: /review, /pm-strategy, /test-plan"
echo ""
echo -e "${YELLOW}Optional:${NC}"
echo "  - Edit .claude/hooks/.env.example for notifications"
echo "  - Create .claude/CLAUDE.md for project context"
echo ""
echo -e "${GREEN}Done!${NC}"
