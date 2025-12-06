# Gemini Kit — Claude Code Skills Router

**Status**: PRODUCTION-READY
**Version**: 1.1
**Last Updated**: 2025-11-25

## Overview

The Gemini Kit enables **Gemini CLI users to leverage Claude Code skills and agents in the same repository** through a routing command. Instead of duplicating agent definitions, Gemini reads your root `GEMINI.md` plus a router command in `.gemini/commands/` that knows how to map tasks to the existing `.claude/` skills and agents.

**Same-Repo Cross-Platform Usage**:
- User sets up `.claude/` with skills and agents (from Claude Code Kit)
- User copies router files from `frameworks/gemini-kit/framework/` into `.gemini/`
- Gemini CLI loads `GEMINI.md` (project memory) and the `/claude-router` command
- Router command chooses the best Claude agent and skill for each request
- Result: Gemini users get Claude Code capabilities without switching tools

## Contents

```
frameworks/gemini-kit/
├── README.md                         # This file
└── framework/                        # Copy these files to your repo's .gemini/ folder
    ├── README.md                     # 1-minute setup guide
    ├── gemini-router.toml            # /claude-router command definition
    ├── gemini-router.md              # Structured routing reference
    ├── gemini-router.yaml            # Configuration metadata
    └── router-tests.md               # Validation test cases
```

## Quick Start (3 Steps)

### Prerequisites
- `.claude/` folder already set up in your repository (from Claude Code Kit)
- Root-level `GEMINI.md` present (project memory and global rules)
- Gemini CLI installed and configured

### Step 1: Copy Router Files to `.gemini/`

```bash
# From your repository root
mkdir -p .gemini/commands

# Copy router command and docs
cp frameworks/gemini-kit/framework/gemini-router.toml .gemini/commands/claude-router.toml
cp frameworks/gemini-kit/framework/gemini-router.md .gemini/
cp frameworks/gemini-kit/framework/gemini-router.yaml .gemini/
cp frameworks/gemini-kit/framework/router-tests.md .gemini/
```

### Step 2: Ensure Claude Code Kit Is Installed

Your repository should already include the Claude Code Kit agents and skills:

```bash
mkdir -p .claude/{agents,skills,commands}

cp frameworks/claude-code-kit/framework/agents/*.md .claude/agents/
cp -r frameworks/claude-code-kit/framework/skills/* .claude/skills/
cp frameworks/claude-code-kit/framework/commands/*.md .claude/commands/
```

Gemini will not read `.claude/` automatically, but the router command is written to assume that these files exist and can be passed as context when needed.

### Step 3: Use Claude Skills from Gemini

Run Gemini from your repository root and call the router command:

```bash
# Example: SQL optimization
gemini run /claude-router "Optimize this PostgreSQL query for performance" \
  src/db/slow-query.sql \
  .claude/skills/data-sql-optimization/SKILL.md

# Example: RAG pipeline design
gemini run /claude-router "Design a RAG pipeline for legal document retrieval"

# Example: Frontend security review
gemini run /claude-router "Review this React component for XSS issues" \
  src/components/UserProfile.tsx
```

On each call, the router:
- Reads the task description (and any attached files)
- Chooses an agent and skill from `.claude/agents/` and `.claude/skills/`
- Prints a routing line like `Route: Agent: llm-engineer | Skill: ai-rag | Priority: 2`
- Then provides the answer from that agent’s perspective using the chosen skill

## Routing System Features

**17 Agents Available** (from Claude Code Kit):

- ai-agents-builder, backend-engineer, code-reviewer, crypto-engineer, data-scientist
- devops-engineer, frontend-engineer, llm-engineer, mobile-engineer, prd-architect
- product-manager, prompt-engineer, security-specialist, smm-strategist, sql-engineer
- system-architect, test-architect

**50 Skills Available**:

- ai-agents, ai-llm, ai-llm-inference, ai-ml-data-science, ai-ml-timeseries, ai-mlops, ai-prompt-engineering, ai-rag
- claude-code-agents, claude-code-commands, claude-code-hooks, claude-code-mcp, claude-code-project-memory, claude-code-skills
- data-lake-platform, data-sql-optimization, dev-api-design, dev-dependency-management, dev-workflow-planning
- docs-ai-prd, docs-codebase, document-docx, document-pdf, document-pptx, document-xlsx
- git-commit-message, git-workflow, marketing-ai-search-optimization, marketing-leads-generation, marketing-seo-technical, marketing-social-media
- ops-devops-platform, product-management, qa-debugging, qa-docs-coverage, qa-observability, qa-refactoring, qa-resilience
- qa-testing-ios, qa-testing-playwright, qa-testing-strategy
- software-architecture-design, software-backend, software-code-review, software-crypto-web3, software-frontend, software-mobile, software-security-appsec, software-ui-ux-design, software-ux-research

**28 Routing Rules**:
- 4-tier priority system (explicit override → task-specific → domain-specific → fallback)
- Conflict resolution for ambiguous or cross-domain tasks
- Automatic skill selection based on task type and tech stack

**Test Coverage**:
- 15 standard test cases covering all agent types
- 8 edge cases (overrides, conflicts, missing components)
- 100% coverage: all agents, skills, and priority rules

## Related Documentation

**Claude Code Kit**: `frameworks/claude-code-kit/`
- Source of all skills, agents, and commands
- Copy from `framework/` to `.claude/` in your repository

**Gemini Project Memory**: `GEMINI.md`  
- Repository overview and global rules for Gemini  
- Works together with `.gemini/commands/*.toml` and `.gemini/skills/*.md`

**Codex Kit (Optional)**: `frameworks/codex-kit/`  
- If you also use Codex CLI, you can install the Codex router to reuse the same `.claude/` skills there.

## Support and Maintenance

- Use `.gemini/router-tests.md` to validate routing behavior after installation
- When Claude Code Kit adds new skills or agents, update `.claude/` first and then refresh the router command if you need new routing rules
- If routing seems incorrect, compare behavior against `router-tests.md` and `gemini-router.md`

## Version History

**v1.1 (2025-11-22)**:

- Updated to 17 agents, 50 skills (full parity with Claude Code Kit v3.0)
- Added agents: crypto-engineer, security-specialist
- Added 10 new skills across quality, foundation, and operations categories
- Router files updated with complete catalog aligned to Claude Code skills (data-lake-platform, data-sql-optimization)
- Full alignment with Codex Kit v1.2 routing

**v1.0 (2025-11-19)**:

- Initial release with Gemini CLI router command
- 15 agents, 24 skills, 28 routing rules
- 4-tier priority system with conflict resolution
- Integration with Claude Code Kit via router command
