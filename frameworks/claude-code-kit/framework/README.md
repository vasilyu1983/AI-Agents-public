# Claude Code Kit - Initial Setup

**Copy-paste ready files for instant Claude Code productivity**

60 specialized skills + 17 production agents + 22 workflow commands + 7 automation hooks

---

## Quick Install (30 seconds)

### Option 1: One-Command Install (Recommended)

```bash
cd your-project/
/path/to/frameworks/claude-code-kit/framework/install.sh
```

The install script:

- Creates `.claude/` directory structure
- Copies all agents, skills, commands, hooks
- Makes hooks executable
- Copies `settings.json` ready to use

### Option 2: Manual Copy

```bash
cd your-project/

# Create .claude directories
mkdir -p .claude/{agents,skills,commands,hooks,logs}

# Copy all files
cp frameworks/claude-code-kit/framework/agents/*.md .claude/agents/
cp -r frameworks/claude-code-kit/framework/skills/* .claude/skills/
cp frameworks/claude-code-kit/framework/commands/*.md .claude/commands/
cp frameworks/claude-code-kit/framework/hooks/*.sh .claude/hooks/
chmod +x .claude/hooks/*.sh

# Copy settings (use clean version, not template)
cp frameworks/claude-code-kit/framework/settings/settings.json .claude/settings.json
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
ls .claude/agents/ | wc -l      # Should show 17
ls .claude/skills/ | wc -l      # Should show 60
ls .claude/commands/ | wc -l    # Should show 22
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

**Before (in framework/)**:
```markdown
See [Skills Guide](../docs/skills.md) for details.
Reference: frameworks/claude-code-kit/framework/skills/software-backend/
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
echo "Agents: $(ls .claude/agents/*.md 2>/dev/null | wc -l) (expected: 17)"
echo "Skills: $(ls .claude/skills/*/SKILL.md 2>/dev/null | wc -l) (expected: 60)"
echo "Commands: $(ls .claude/commands/*.md 2>/dev/null | wc -l) (expected: 22)"
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

| Component | Count | Purpose |
|-----------|-------|---------|
| **Agents** | 17 | Specialized roles (backend, frontend, mobile, LLM, DevOps, PM, crypto, security, etc.) |
| **Skills** | 60 | Domain knowledge bases with templates and resources |
| **Commands** | 22 | Quick workflow access (code review, testing, architecture, product management) |
| **Hooks** | 7 | Automated guardrails (formatting, security, testing, logging, notifications, cost tracking) |

**Total**: 106 production-ready files

---

## Complete Documentation

This directory contains **copy-paste files only**. For complete usage guides and references:

### Core References
- **[../reference/agents.md](../reference/agents.md)** - Complete agent catalog and capabilities
- **[../reference/skills.md](../reference/skills.md)** - Skill structure, patterns, and examples
- **[../reference/commands.md](../reference/commands.md)** - Command usage and workflows
- **[../reference/hooks.md](../reference/hooks.md)** - Hook configuration and customization

### Workflow Guide
- **[../reference/workflows.md](../reference/workflows.md)** - Real-world examples showing how all components work together

### Other Resources
- **[../reference/claudemd.md](../reference/claudemd.md)** - CLAUDE.md best practices
- **[../reference/mcp.md](../reference/mcp.md)** - Model Context Protocol integration

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
framework/
├── README.md                    # This file
├── ARCHITECTURE-DIAGRAM.md      # Complete system architecture with Mermaid diagrams
│
├── agents/                      # 17 agent definitions
│   ├── ai-agents-builder.md
│   ├── backend-engineer.md
│   ├── code-reviewer.md
│   ├── crypto-engineer.md
│   ├── data-scientist.md
│   ├── devops-engineer.md
│   ├── frontend-engineer.md
│   ├── llm-engineer.md
│   ├── mobile-engineer.md
│   ├── prd-architect.md
│   ├── product-manager.md
│   ├── prompt-engineer.md
│   ├── security-specialist.md
│   ├── smm-strategist.md
│   ├── sql-engineer.md
│   ├── system-architect.md
│   └── test-architect.md
│
├── skills/                      # 60 skill knowledge bases
│   ├── [skill-name]/
│   │   ├── SKILL.md            # Main skill file
│   │   ├── data/sources.json   # Web resources
│   │   ├── resources/          # Deep-dive guides
│   │   └── templates/          # Code templates
│
├── commands/                    # 22 workflow commands
│   ├── agent-arch.md
│   ├── agent-eval.md
│   ├── agent-plan.md
│   ├── architecture-review.md
│   ├── commit-msg.md
│   ├── coverage-check.md
│   ├── design-system.md
│   ├── ds-deploy.md
│   ├── fullstack-dev.md
│   ├── leadgen.md
│   ├── pm-discovery.md
│   ├── pm-okrs.md
│   ├── pm-positioning.md
│   ├── pm-roadmap.md
│   ├── pm-strategy.md
│   ├── prd-validate.md
│   ├── prompt-validate.md
│   ├── review.md
│   ├── security-scan.md
│   ├── smm-plan.md
│   ├── tech-spec.md
│   └── test-plan.md
│
└── hooks/                       # 7 automation hooks + docs
    ├── pre-tool-validate.sh     # Security validation
    ├── post-tool-format.sh      # Auto-formatting
    ├── post-tool-audit.sh       # Audit logging
    ├── post-tool-notify.sh      # Notifications (optional)
    ├── post-tool-cost-tracker.sh # AI cost tracking (optional)
    ├── stop-run-tests.sh        # Test automation
    ├── session-start-init.sh    # Context loading
    ├── commit-msg.md            # Commit message guidance
    ├── pre-commit.md            # Pre-commit guidance
    ├── HOOKS-GUIDE.md           # Complete hook setup guide
    ├── README.md                # Hook documentation
    └── QUICK-START.md           # Hook quick start
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

- **[Agents](https://docs.claude.com/en/docs/claude-code/sub-agents)** - Creating subagents
- **[Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)** - Knowledge bases
- **[Commands](https://docs.claude.com/en/docs/claude-code/commands)** - Slash commands
- **[Hooks](https://docs.claude.com/en/docs/claude-code/hooks)** - Event automation

---

---

## Recent Updates

**(2025-12-09)**: Startup Validation Machine - Complete Suite

- **NEW: `startup-mega-router`** - Master orchestration for routing through 60+ skills
- **NEW: `startup-idea-validation`** - 9-dimension scoring with Go/No-Go decisions
- **NEW: `startup-competitive-analysis`** - Deep competitive intelligence, market mapping, positioning
- **NEW: `startup-business-models`** - Revenue model design, unit economics, pricing strategy
- **NEW: `startup-fundraising`** - Fundraising strategy, pitch prep, investor targeting, term sheets
- **NEW: `startup-go-to-market`** - GTM strategy, PLG/sales-led motion, channel selection, growth loops
- **NEW: `startup-review-mining`** - Pain extraction from ALL review sources (G2, Capterra, App Store, Reddit, HN)
- **NEW: `startup-trend-prediction`** - 2-3yr lookback → 1-2yr forward trend analysis
- **NEW: `agent-fleet-operations`** - Managing 50+ AI agents as revenue services: orchestration, monitoring, scaling
- **NEW: `qa-agent-testing`** - LLM agent/persona testing: 10-task suites, refusal edge cases, 6-dimension scoring
- Updated skill-dependencies.json with startup domain and cross-links
- Total skills: 54 → 60

**(2025-12-08)**: UX Skills December Updates

- **software-ui-ux-design**: WCAG 3.0 preview, React Aria, AI design tools, shadcn/ui 2025 components
- **software-ux-research**: 3 arXiv papers on LLM-assisted UX evaluation, 2025 benchmarks
- Updated component-library-comparison.md and frontend-aesthetics-2025.md

---

**Ready to build production software with Claude Code!**

For complete usage examples and workflows, see **[../reference/workflows.md](../reference/workflows.md)**
