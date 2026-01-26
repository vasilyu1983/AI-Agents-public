# Claude Code Kit - Initial Setup

**Copy-paste ready files for instant Claude Code productivity**

21 production agents + 28 workflow commands + 7 automation hooks

**Skills**: Copy separately from `frameworks/shared-skills/` (shared with Codex Kit)

---

## Quick Install (30 seconds)

```bash
cd your-project/

# Create .claude directories
mkdir -p .claude/{agents,skills,commands,hooks}

# Copy framework files
cp frameworks/claude-code-kit/framework/agents/*.md .claude/agents/
cp frameworks/claude-code-kit/framework/commands/*.md .claude/commands/
cp frameworks/claude-code-kit/framework/hooks/*.sh .claude/hooks/
chmod +x .claude/hooks/*.sh
cp frameworks/claude-code-kit/framework/settings/settings.json .claude/settings.json

# Copy skills from shared source
cp -r frameworks/shared-skills/skills/* .claude/skills/
```

### Settings Files

| File | Purpose |
|------|---------|
| `settings.json` | Clean, production-ready. Copy-paste and use immediately. |
| `settings-template.json` | Documented version with comments and optional sections. |

---

## Verify Installation

```bash
# Check counts
ls .claude/agents/ | wc -l      # Should show 21
ls .claude/skills/ | wc -l      # Should show 83
ls .claude/commands/ | wc -l    # Should show 28
ls -l .claude/hooks/*.sh        # Should show 7 executable files

# Verify settings
cat .claude/settings.json | jq '.hooks'
```

---

## Post-Installation Verification

After copying files to `.claude/`, verify that all internal references are correct:

### Check for Broken Links

**Why this matters**: Files in `framework/` may contain relative paths that break when moved to `.claude/`. This step ensures all cross-references work correctly in your project.

```bash
# Search for references to framework paths (should return nothing)
grep -r "frameworks/claude-code-kit/framework/" .claude/agents/
grep -r "frameworks/claude-code-kit/framework/" .claude/commands/
grep -r "frameworks/claude-code-kit/framework/" .claude/skills/

# Search for references to ../reference/ paths (may need updating)
grep -r "\.\./reference/" .claude/agents/
grep -r "\.\./reference/" .claude/commands/
grep -r "\.\./reference/" .claude/skills/

# Check for skill cross-references (verify paths are correct)
grep -r "\.claude/skills/" .claude/agents/
grep -r "skills/" .claude/commands/
```

### Common Path Fixes

If you find broken references, update them:

**Before (in shared-skills/)**:
```markdown
See [Skills Guide](../docs/skills.md) for details.
Reference: frameworks/shared-skills/skills/software-backend/
```

**After (in .claude/)**:
```markdown
See Claude Code Skills documentation for details.
Reference: .claude/skills/software-backend/
```

### Verify Agent References

```bash
# Ensure agents reference skills correctly
grep -h "skill:" .claude/agents/*.md | sort -u

# Check that all referenced skills exist
for agent in .claude/agents/*.md; do
  echo "Checking $agent..."
  grep "skill:" "$agent" | while read -r line; do
    skill=$(echo "$line" | sed 's/.*skill: *\([^ ]*\).*/\1/')
    if [ ! -d ".claude/skills/$skill" ]; then
      echo "  WARNING: Missing skill '$skill'"
    fi
  done
done
```

### Verify Command References

```bash
# Check commands reference valid agents/skills
grep -h "Use.*agent" .claude/commands/*.md

# Verify all agent names in commands exist as files
for cmd in .claude/commands/*.md; do
  echo "Checking $cmd..."
  grep -o "[a-z-]*-agent\|[a-z-]*-engineer\|[a-z-]*-architect" "$cmd" | \
  while read -r agent; do
    if [ ! -f ".claude/agents/$agent.md" ]; then
      echo "  WARNING: Missing agent '$agent'"
    fi
  done
done
```

### Hook Verification

```bash
# Verify hooks have correct permissions
ls -l .claude/hooks/*.sh | awk '{print $1, $9}' | grep -v "^-rwx"

# Check hooks reference valid paths
grep -h "CLAUDE_PROJECT_DIR\|\.claude" .claude/hooks/*.sh

# Test hooks don't have syntax errors (dry run)
for hook in .claude/hooks/*.sh; do
  bash -n "$hook" && echo "$hook: OK" || echo "$hook: SYNTAX ERROR"
done
```

### Complete Verification Script

```bash
#!/bin/bash
# verify-installation.sh - Run all verification checks

echo "=== Checking File Counts ==="
echo "Agents: $(ls .claude/agents/*.md 2>/dev/null | wc -l) (expected: 21)"
echo "Skills: $(ls .claude/skills/*/SKILL.md 2>/dev/null | wc -l) (expected: 83)"
echo "Commands: $(ls .claude/commands/*.md 2>/dev/null | wc -l) (expected: 28)"
echo "Hooks: $(ls .claude/hooks/*.sh 2>/dev/null | wc -l) (expected: 7)"

echo -e "\n=== Checking for Broken Paths ==="
broken=$(grep -r "frameworks/claude-code-kit/framework/" .claude/ 2>/dev/null | wc -l)
echo "References to framework path: $broken (expected: 0)"

echo -e "\n=== Checking Hook Permissions ==="
for hook in .claude/hooks/*.sh; do
  if [ -x "$hook" ]; then
    echo "✓ $hook"
  else
    echo "✗ $hook (not executable - run: chmod +x $hook)"
  fi
done

echo -e "\n=== Checking Hook Syntax ==="
for hook in .claude/hooks/*.sh; do
  if bash -n "$hook" 2>/dev/null; then
    echo "✓ $hook"
  else
    echo "✗ $hook (syntax error)"
  fi
done

echo -e "\n=== Verification Complete ==="
```

Save this as `.claude/verify-installation.sh` and run:
```bash
chmod +x .claude/verify-installation.sh
./.claude/verify-installation.sh
```

---

## What You Get

| Component | Count | Source |
| --------- | ----- | ------ |
| **Agents** | 21 | `framework/agents/` |
| **Commands** | 28 | `framework/commands/` |
| **Hooks** | 7 | `framework/hooks/` |
| **Skills** | 83 | `shared-skills/skills/` (separate) |

---

## Complete Documentation

This directory contains **copy-paste files only**. For complete usage guides and references:

### Core References

- **[../docs/agents.md](../docs/agents.md)** - Complete agent catalog and capabilities
- **[../docs/skills.md](../docs/skills.md)** - Skill structure, patterns, and examples
- **[../docs/commands.md](../docs/commands.md)** - Command usage and workflows
- **[../docs/hooks.md](../docs/hooks.md)** - Hook configuration and customization

### Workflow Guide

- **[../docs/workflows.md](../docs/workflows.md)** - Real-world examples showing how all components work together

### Other Resources

- **[../docs/claudemd.md](../docs/claudemd.md)** - CLAUDE.md best practices
- **[../docs/mcp.md](../docs/mcp.md)** - Model Context Protocol integration

---

## Quick Start

### 1. Use Commands for Common Tasks

```bash
# Code quality
/review src/auth/              # Comprehensive code review
/security-scan src/            # Security vulnerability scan
/test-plan authentication      # Test strategy and plan

# Architecture
/design-system chat-app        # System architecture design
/architecture-review src/      # Architecture analysis

# AI development
/agent-arch support-bot        # Agent architecture design
/agent-eval my-agent          # Evaluation framework

# Product
/prd user-authentication      # Product requirements doc
/tech-spec oauth-integration  # Technical specification
```

### 2. Invoke Agents Directly

```bash
# Development
"Use backend-engineer to build REST API for tasks"
"Use frontend-engineer to create dashboard UI"
"Use mobile-engineer for iOS app"

# Quality & Architecture
"Use code-reviewer to audit security"
"Use test-architect for testing strategy"
"Use system-architect to design scalable system"

# Specialized
"Use llm-engineer to build RAG pipeline"
"Use data-scientist for churn prediction"
"Use devops-engineer for K8s deployment"
```

### 3. Skills Auto-Load

Skills automatically activate when agents are invoked:
- `backend-engineer` → uses `software-backend` skill
- `frontend-engineer` → uses `software-frontend` skill
- `llm-engineer` → intelligently routes between 3 LLM skills
- And so on...

---

## File Structure

```
framework/                       # Copy to .claude/
├── agents/                      # 21 agent definitions
├── commands/                    # 28 workflow commands
├── hooks/                       # 7 automation hooks
└── settings/                    # Configuration files

shared-skills/                   # Copy to .claude/skills/
└── skills/                      # 76 skill knowledge bases
    └── [skill-name]/
        ├── SKILL.md             # Main skill file
        ├── data/sources.json    # Web resources
        ├── references/           # Deep-dive guides
        └── assets/           # Code templates
```

---

## Customization

### Extend Skills

Add your team's patterns to any skill:

```bash
# Edit skill file
vim .claude/skills/software-backend-engineering/SKILL.md

# Add section:
## Company Standards
[Your specific patterns, templates, conventions]
```

### Add Custom Commands

```bash
# Create new command
cat > .claude/commands/my-workflow.md << 'EOF'
# My Workflow

Use the [agent-name] agent to [task description].

Apply [specific patterns or constraints].
EOF
```

### Customize Hooks

```bash
# Edit any hook
vim .claude/hooks/post-tool-format.sh

# Add language support, notifications, validation rules, etc.
```

---

## Troubleshooting

**Command not found:**
```bash
ls .claude/commands/review.md  # Filename must match command name
```

**Agent not loading:**
```bash
head -10 .claude/agents/prd-architect.md  # Check YAML frontmatter
```

**Skill not accessible:**
```bash
ls .claude/skills/*/SKILL.md  # Verify skill files exist
```

**Hooks not running:**
```bash
chmod +x .claude/hooks/*.sh  # Fix permissions
```

---

## Official Documentation

**Agent Skills Open Format**:

- **[Agent Skills Specification](https://agentskills.io/specification)** - Complete format specification
- **[What Are Skills?](https://agentskills.io/what-are-skills)** - Conceptual overview
- **[Anthropic Skills Repository](https://github.com/anthropics/skills)** - Official examples

**Claude Code**:

- **[Agents](https://docs.claude.com/en/docs/claude-code/sub-agents)** - Creating subagents
- **[Commands](https://docs.claude.com/en/docs/claude-code/commands)** - Slash commands
- **[Hooks](https://docs.claude.com/en/docs/claude-code/hooks)** - Event automation

---

## Recent Updates

**(2025-12-20)**: Shared Skills Source

- Skills now maintained in `frameworks/shared-skills/`
- Run `./frameworks/sync-skills.sh` to sync from shared source
- Both Claude Code Kit and Codex Kit use same skills

**(2025-12-19)**: Agent Skills Alignment (v3.6)

- Skills aligned with [agentskills.io](https://agentskills.io) specification
- Progressive disclosure model with <5000 token SKILL.md bodies
- Directory structure: `references/`, `scripts/`, `assets/`

**(2025-12-09)**: Four-Router Architecture

- `router-main` - Universal entry point routing to domain-specific routers
- `router-engineering` - 29 technical skills (AI/ML, software, data)
- `router-operations` - 15 operations skills (QA, testing, DevOps)
- `router-startup` - 17 business skills (startup, marketing, product)

---

**Ready to build production software with Claude Code!**

For complete usage examples and workflows, see **[../docs/workflows.md](../docs/workflows.md)**
