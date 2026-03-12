# Fast-Track Guide

Getting productive with context-driven development quickly. Three tracks based on repo size, plus batch onboarding for organizations with many repos.

## Key Research Insight (March 2026)

Before you start: **quality matters more than quantity**. ETH Zurich research (arxiv 2602.11988) found that LLM-generated AGENTS.md files actually degrade agent performance by 3% while increasing costs 20%+. Human-written files help only when limited to **non-inferable details** — things the agent cannot discover by reading your code and docs:

- Custom build/test commands not in package.json or Makefile
- Domain-specific conventions not evident from code patterns
- Known failure modes and workarounds
- Specific CI/CD quirks

**Do NOT include**: project structure descriptions, dependency lists, or README-level documentation the agent can find itself.

## Quick Wins (Under 5 Minutes Each)

Do these first regardless of repo size:

| # | Action | Time | Impact |
|---|--------|------|--------|
| 1 | Create AGENTS.md with project name + tech stack | 2 min | Agents know what this repo is |
| 2 | Symlink: `ln -s AGENTS.md CLAUDE.md` | 10 sec | Both Claude Code and Codex get context |
| 3 | Add build/test/lint commands to AGENTS.md | 2 min | Agents can verify their own work |
| 4 | Add `.claude/rules/` with one coding standard | 3 min | Consistent code style from agents |
| 5 | Add directory structure overview to AGENTS.md | 3 min | Agents navigate the codebase faster |
| 6 | Create `docs/` directory | 30 sec | Home for specs and plans |
| 7 | Add `.gitignore` entries for agent temp files | 1 min | Clean repo state |
| 8 | Set up signed commits: `git config commit.gpgsign true` | 1 min | Audit trail (required for regulated) |
| 9 | Add PR template with AI disclosure section | 3 min | Transparency in PRs |
| 10 | Run orientation: `wc -l **/*.{ts,py,go} \| tail -1` | 30 sec | Know your codebase size |

## 30-Minute Fast-Track (Medium Repos, 10K-100K LOC)

For repos where a single developer can understand the whole codebase.

### Minute 0-5: Orientation

```bash
# Understand the codebase
find . -name '*.ts' -o -name '*.py' -o -name '*.go' | head -20
wc -l $(find . -name '*.ts' -o -name '*.py' -o -name '*.go') | tail -1
cat package.json 2>/dev/null || cat pyproject.toml 2>/dev/null || cat go.mod 2>/dev/null
ls -la
```

### Minute 5-15: Create AGENTS.md

```markdown
# [Project Name]

## Overview
[1-2 sentence description from README]

## Tech Stack
- Language: [e.g., TypeScript 5.x]
- Framework: [e.g., Next.js 15]
- Database: [e.g., PostgreSQL via Prisma]
- Testing: [e.g., Vitest + Playwright]

## Commands
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`
- Dev: `npm run dev`

## Directory Structure
- `src/` — Application source code
- `src/api/` — API routes
- `src/components/` — React components
- `tests/` — Test files
- `prisma/` — Database schema and migrations

## Key Patterns
- [Pattern 1: e.g., "All API routes use middleware chain in src/middleware/"]
- [Pattern 2: e.g., "Database queries go through repository pattern in src/repos/"]

## Conventions
- Commits: conventional commits (feat:, fix:, chore:)
- Branches: feature/*, fix/*, chore/*
- PRs: require 1 approval minimum
```

Then: `ln -s AGENTS.md CLAUDE.md`

### Minute 15-25: Add 2-3 Rules

```bash
mkdir -p .claude/rules
```

Create focused rule files (one concern per file):

**`.claude/rules/code-style.md`** — Key patterns, naming conventions, import ordering

**`.claude/rules/testing.md`** — Test file location, naming, coverage expectations

**`.claude/rules/architecture.md`** — Layer boundaries, dependency direction, prohibited patterns

### Minute 25-30: First Plan File

Create `docs/plans/` and write a small plan for your next task using dev-workflow-planning. This validates the entire setup.

```bash
mkdir -p docs/plans
# Use Claude Code to generate: "Create a plan for [your next task]"
```

**Result**: L1-L2 maturity in 30 minutes. Agents now produce consistent, context-aware output.

## 2-Hour Fast-Track (Large Repos, 100K-1M LOC)

For repos too large for a single developer to hold in memory.

### Hour 1: Hierarchical Context

**Step 1 (15 min): Root AGENTS.md**

Keep the root file as an orientation guide. Don't try to document everything:

```markdown
# [Project Name]

## Overview
[Brief description]

## Architecture
[High-level architecture: services, layers, data flow]

## Commands
[Build, test, lint, deploy — the essentials]

## Directory Map
- `src/auth/` — Authentication (has own AGENTS.md)
- `src/payments/` — Payment processing (has own AGENTS.md)
- `src/api/` — API layer
- `src/shared/` — Shared utilities
- `packages/` — Internal packages

## Key Decisions
- [Decision 1: e.g., "Event-driven architecture using RabbitMQ"]
- [Decision 2: e.g., "Domain-Driven Design with bounded contexts"]

## Cross-Cutting Concerns
- Error handling: [pattern]
- Logging: [pattern]
- Authentication: [pattern]
```

**Step 2 (15 min): Subdirectory AGENTS.md files**

For complex subdirectories, create focused context:

```bash
# For each major subdirectory
echo "# Auth Module\n\n## Purpose\n...\n## Patterns\n...\n## Testing\n..." > src/auth/AGENTS.md
echo "# Payments Module\n\n## Purpose\n...\n## Patterns\n...\n## Testing\n..." > src/payments/AGENTS.md
```

**Step 3 (30 min): Rules and agents**

```bash
mkdir -p .claude/rules .claude/agents

# Rules (5-10 min each)
# Create 3-5 focused rule files covering major concerns
# See agents-project-memory for templates

# Agents (10-15 min each)
# Create 1-2 specialized subagents for common tasks
# See agents-subagents for templates
```

### Hour 2: Automation

**Step 4 (20 min): Hooks**

Set up hooks for the most common pain points. See agents-hooks for patterns:
- Pre-commit: lint check, test runner
- Notification: context reminders

**Step 5 (20 min): CI/CD gates**

Add compliance gates if regulated. See `assets/fca-compliance-gate.yml`.

**Step 6 (20 min): Validate and iterate**

```bash
# Test the setup with a real task
# Use Claude Code to work on something and observe:
# - Does the agent follow your conventions?
# - Are the rules being applied?
# - Is any context missing?

# Common gap: agents don't know about your test patterns
# Fix: add a testing rule or test-writer subagent
```

**Result**: L2-L3 maturity in 2 hours. Agents work within guardrails with automated enforcement.

## Batch Onboarding (100 Repos)

Rolling out context-driven development across an organization.

### Phase 1: Foundation (Week 1)

1. **Create coordination repo** (see multi-repo-strategy.md)
2. **Create template AGENTS.md** with org-wide sections
3. **Create mandatory rules** (compliance, data handling, AI governance)
4. **Write sync scripts** for rule distribution

### Phase 2: Pilot (Week 2-3)

1. **Select 10 pilot repos** — pick diverse sizes and tech stacks
2. **Priority ordering**: Start with most-active repos (highest commit frequency)
3. **Apply 30-minute or 2-hour fast-track** to each pilot repo
4. **Collect feedback**: What worked? What context was missing?

### Phase 3: Scale (Week 4-8)

1. **Batch apply** to remaining repos in groups of 10-20
2. **Use automation**: Template sync or CI/CD sync for mandatory rules
3. **Allow local customization**: Repo teams own their AGENTS.md content
4. **Track maturity**: Use audit script from maturity-model.md

### Phase 4: Sustain (Ongoing)

1. **Monthly context retrospective** per team
2. **Quarterly org-wide context audit**
3. **Context curation guild** reviews shared rules
4. **Retire stale context** aggressively

### Batch Priority Matrix

| Priority | Criteria | Action |
|----------|----------|--------|
| **P1 (now)** | Active development + customer-facing + regulated | Full fast-track + compliance gates |
| **P2 (week 2-3)** | Active development + internal | Standard fast-track |
| **P3 (week 4-6)** | Moderate activity | Basic AGENTS.md + mandatory rules |
| **P4 (later)** | Dormant/archived | Minimal AGENTS.md only |

## Cross-References

- **agents-project-memory** — Detailed AGENTS.md writing patterns
- **agents-project-memory/references/large-codebase-strategy.md** — 100K-1M LOC specific strategies
- **docs-ai-prd/references/architecture-extraction.md** — Extracting architecture from existing code
- **docs-ai-prd/references/convention-mining.md** — Mining conventions from codebases
- **maturity-model.md** — Self-assessment before and after onboarding
- **multi-repo-strategy.md** — Coordination patterns for batch onboarding
