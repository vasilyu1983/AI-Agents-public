# Codex Kit — Claude Code Skills Router

**Status**: PRODUCTION-READY
**Version**: 1.3
**Last Updated**: 2025-12-09

## Overview

The Codex Kit enables **Codex CLI users to leverage Claude Code skills in the same repository** through a smart routing system. Instead of duplicating agent definitions, Codex reads from your existing `.claude/` folder and routes requests to the appropriate skills and agents.

**Same-Repo Cross-Platform Usage**:
- User sets up `.claude/` with skills/agents (from Claude Code Kit)
- User copies router to `.codex/` (from this kit)
- Codex CLI reads router, references `.claude/` skills/agents
- Result: Codex users get Claude Code capabilities without switching tools

## Contents

```
frameworks/codex-kit/
├── README.md                          # This file
├── tools/
│   └── claude-skill-to-codex/
│       └── prompt.md                  # Router builder prompt (regenerate router from Claude setup)
└── framework/                         # Copy these files to your repo's .codex/ folder
    ├── codex-router.md                # Structured routing reference (8.4KB)
    ├── codex-mega-prompt.txt          # Paste-ready session starter (8.5KB)
    ├── codex-router.yaml              # Configuration metadata (5.7KB)
    └── router-tests.md                # Validation test cases (11KB)
```

## Quick Start (3 Steps)

### Prerequisites
- `.claude/` folder already set up in your repository (from Claude Code Kit)
- Codex CLI installed and configured

### Step 1: Copy Router to `.codex/`
```bash
mkdir -p .codex
cp frameworks/codex-kit/framework/codex-router.md .codex/
cp frameworks/codex-kit/framework/codex-mega-prompt.txt .codex/
cp frameworks/codex-kit/framework/codex-router.yaml .codex/
```

### Step 2: Paste Mega-Prompt into Codex Session
```bash
# Start Codex in your repository
codex

# Paste contents of .codex/codex-mega-prompt.txt
# (This tells Codex how to route requests)
```

### Step 3: Use Claude Skills from Codex
```
User: "Review this React component for security issues"
Codex: Agent: frontend-engineer | Skill: ml-ops-security-privacy
       [provides security review using both]

User: "Optimize this PostgreSQL query"
Codex: Agent: sql-engineer | Skill: sql-optimization
       [provides optimization]

User: "Design a RAG pipeline for document retrieval"
Codex: Agent: llm-engineer | Skill: rag-engineering
       [provides RAG architecture]
```

## Routing System Features

**17 Agents Available**:

- ai-agents-builder, backend-engineer, code-reviewer, crypto-engineer, data-scientist
- devops-engineer, frontend-engineer, llm-engineer, mobile-engineer, prd-architect
- product-manager, prompt-engineer, security-specialist, smm-strategist, sql-engineer
- system-architect, test-architect

**62 Skills Available** (including 4 routers):

- **Routers**: router-main, router-startup, router-engineering, router-operations
- **AI/ML**: ai-agents, ai-llm, ai-llm-inference, ai-ml-data-science, ai-ml-timeseries, ai-mlops, ai-prompt-engineering, ai-rag
- **Claude Code**: claude-code-agents, claude-code-commands, claude-code-hooks, claude-code-mcp, claude-code-project-memory, claude-code-skills
- **Data**: data-lake-platform, data-sql-optimization
- **Dev Tools**: dev-api-design, dev-dependency-management, dev-workflow-planning, git-commit-message, git-workflow
- **Docs**: docs-ai-prd, docs-codebase, document-docx, document-pdf, document-pptx, document-xlsx
- **Marketing**: marketing-ai-search-optimization, marketing-leads-generation, marketing-seo-technical, marketing-social-media
- **Ops**: ops-devops-platform
- **Product**: product-management
- **QA**: qa-agent-testing, qa-debugging, qa-docs-coverage, qa-observability, qa-refactoring, qa-resilience, qa-testing-ios, qa-testing-playwright, qa-testing-strategy
- **Software**: software-architecture-design, software-backend, software-code-review, software-crypto-web3, software-frontend, software-mobile, software-security-appsec, software-ui-ux-design, software-ux-research
- **Startup**: startup-idea-validation, startup-competitive-analysis, startup-business-models, startup-fundraising, startup-go-to-market, startup-review-mining, startup-trend-prediction

**28 Routing Rules**:
- 4-tier priority system (explicit override → task-specific → domain-specific → fallback)
- Conflict resolution for ambiguous requests
- Automatic skill selection based on task type and tech stack

**Test Coverage**:
- 15 standard test cases covering all agent types
- 8 edge cases (overrides, conflicts, missing components)
- 100% coverage: all agents, skills, and priority rules

## File Descriptions

### codex-router.md (Reference Documentation)
Structured catalog of skills, agents, and routing rules. Use this to:
- Look up available skills and agents
- Understand routing logic and priority order
- Debug unexpected routing decisions
- Extend routing rules for new skills

### codex-mega-prompt.txt (Session Starter)
Single paste-ready prompt containing:
- Full skills and agents catalog
- Routing rules with examples
- Output format specification (`Agent: X | Skill: Y`)
- 12 diverse examples covering all domains

**Usage**: Paste into Codex at session start, then ask any question.

### codex-router.yaml (Configuration)
Metadata and deployment info:
- Version, last updated date
- Source directories (`.claude/skills/`, `.claude/agents/`)
- Deployment paths (copy from `frameworks/codex-kit/` to `.codex/`)
- Counts: 17 agents, 62 skills, 28 routing rules

### router-tests.md (Validation)
Test cases to verify routing correctness:
- 15 standard scenarios (agent design, code review, optimization, etc.)
- 8 edge cases (overrides, ambiguity, conflicts, missing components)
- Each test shows expected route, rationale, and priority rule applied

## Regenerating Router (Advanced)

If you update Claude Code Kit skills/agents and need to regenerate the router:

```bash
# Read the router builder prompt
cat frameworks/codex-kit/tools/claude-skill-to-codex/prompt.md

# Follow the 8-step process to regenerate all 4 files:
# 1. Parse Claude setup (skills, agents, commands)
# 2. Normalize catalog (clean IDs, consolidate overlaps)
# 3. Design routing rules (priority order, conflict resolution)
# 4. Generate codex-router.md
# 5. Generate codex-mega-prompt.txt
# 6. Generate codex-router.yaml
# 7. Generate router-tests.md
# 8. Report issues and recommendations
```

## Architecture

**Same-Repo Bridging**:
```
User's Repository
├── .claude/                    # Claude Code Kit (source of truth)
│   ├── skills/                 # 50 operational skills
│   ├── agents/                 # 17 specialized agents
│   └── commands/               # 22 slash commands
└── .codex/                     # Codex Kit (routing layer)
    ├── codex-router.md         # Reference documentation
    ├── codex-mega-prompt.txt   # Session starter
    └── codex-router.yaml       # Configuration

Routing Chain:
Codex CLI → .codex/router → .claude/agents/ → .claude/skills/
```

**Benefits**:
- No duplication: Single source of truth in `.claude/`
- Cross-platform: Use Claude Code skills from Codex CLI
- Maintainable: Update skills in one place, both tools benefit
- Testable: Comprehensive test coverage ensures correct routing

## Related Documentation

**Claude Code Kit**: `frameworks/claude-code-kit/`
- Source of all skills, agents, and commands
- Copy from `framework/` to `.claude/` in your repository

**Shared Foundations**: `frameworks/shared-foundations/`
- MCP (Model Context Protocol) for tool integration
- A2A (Agent-to-Agent Protocol) for multi-agent systems
- Starter templates for security, CI/CD, team workflows

**Repository Standards**: `CLAUDE.md`, `AGENTS.md`, `README.md`
- Three-layer architecture pattern
- File format guidelines
- Git and GitHub integration

## Support

**Issues or Questions**:
- Check `router-tests.md` for expected routing behavior
- Verify `.claude/` folder structure matches Claude Code Kit
- Ensure `codex-mega-prompt.txt` was pasted correctly at session start

**Updating Router**:
- When Claude Code Kit adds new skills: Regenerate router using `claude-skill-to-codex/prompt.md`
- When routing seems incorrect: Check `router-tests.md` and compare actual vs expected
- When skills missing: Verify `.claude/skills/` contains all skill directories

## Version History

**v1.3 (2025-12-09)**:

- Updated to 17 agents, 62 skills (full parity with Claude Code Kit v3.4)
- **NEW**: Four-router architecture (router-main, router-startup, router-engineering, router-operations)
- Added 7 startup validation skills (idea-validation, competitive-analysis, business-models, fundraising, go-to-market, review-mining, trend-prediction)
- Added qa-agent-testing skill for LLM agent testing
- Router skills provide intelligent cross-domain orchestration

**v1.2 (2025-11-22)**:

- Updated to 17 agents, 50 skills (full parity with Claude Code Kit v3.0)
- Added agents: crypto-engineer, security-specialist
- Added 10 new skills across quality, foundation, and operations categories
- Router files updated with complete catalog aligned to Claude Code skills (data-lake-platform, data-sql-optimization)
- Documentation synchronized across all framework READMEs

**v1.1 (2025-11-19)**:

- Updated to 15 agents, 24 skills
- Added: smm-strategist agent, social-media-marketing skill
- Enhanced skill references across all agents
- Added MLOps and search/retrieval skills integration

**v1.0 (2025-11-18)**:

- Initial release with 10 agents, 16 skills, 28 routing rules
- 4-tier priority system with conflict resolution
- Comprehensive test coverage (23 test cases)
- Production-ready router system
