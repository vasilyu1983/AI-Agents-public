# Fast-Track Guide

Getting productive with context-driven development quickly. Three tracks based on repo size, plus batch onboarding for organizations with many repos.

## Table of Contents

- [Key Research Insight (March 2026)](#key-research-insight-march-2026)
- [Quick Wins (Under 5 Minutes Each)](#quick-wins-under-5-minutes-each)
- [30-Minute Fast-Track (Medium Repos, 10K-100K LOC)](#30-minute-fast-track-medium-repos-10k-100k-loc)
- [Minute 0-5: Orientation](#minute-0-5-orientation)
- [Understand the codebase](#understand-the-codebase)
- [Minute 5-15: Create AGENTS.md](#minute-5-15-create-agentsmd)
- [[Project Name]](#project-name)
- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Commands](#commands)
- [Key Patterns](#key-patterns)
- [Known Constraints](#known-constraints)
- [Conventions](#conventions)
- [Minute 15-25: Add 2-3 Rules](#minute-15-25-add-2-3-rules)
- [Minute 25-30: First Plan File](#minute-25-30-first-plan-file)
- [Use Claude Code to generate: "Create a plan for [your next task]"](#use-claude-code-to-generate-create-a-plan-for-your-next-task)
- [2-Hour Fast-Track (Large Repos, 100K-1M LOC)](#2-hour-fast-track-large-repos-100k-1m-loc)
- [Hour 1: Hierarchical Context](#hour-1-hierarchical-context)
- [[Project Name]](#project-name)
- [Overview](#overview)
- [Architecture](#architecture)
- [Commands](#commands)
- [Scoped Areas](#scoped-areas)
- [Key Decisions](#key-decisions)
- [Cross-Cutting Concerns](#cross-cutting-concerns)
- [For each major subdirectory](#for-each-major-subdirectory)
- [Rules (5-10 min each)](#rules-5-10-min-each)
- [Create 3-5 focused rule files covering major concerns](#create-3-5-focused-rule-files-covering-major-concerns)
- [See agents-memory for templates](#see-agents-memory-for-templates)
- [Agents (10-15 min each)](#agents-10-15-min-each)
- [Create 1-2 specialized subagents for common tasks](#create-1-2-specialized-subagents-for-common-tasks)
- [See agents-subagents for templates](#see-agents-subagents-for-templates)
- [Hour 2: Automation](#hour-2-automation)
- [Test the setup with a real task](#test-the-setup-with-a-real-task)
- [Use Claude Code to work on something and observe:](#use-claude-code-to-work-on-something-and-observe)
- [- Does the agent follow your conventions?](#does-the-agent-follow-your-conventions)
- [- Are the rules being applied?](#are-the-rules-being-applied)
- [- Is any context missing?](#is-any-context-missing)
- [Common gap: agents don't know about your test patterns](#common-gap-agents-dont-know-about-your-test-patterns)
- [Fix: add a testing rule or test-writer subagent](#fix-add-a-testing-rule-or-test-writer-subagent)
- [Batch Onboarding (100 Repos)](#batch-onboarding-100-repos)
- [Phase 1: Foundation (Week 1)](#phase-1-foundation-week-1)
- [Phase 2: Pilot (Week 2-3)](#phase-2-pilot-week-2-3)
- [Phase 3: Scale (Week 4-8)](#phase-3-scale-week-4-8)
- [Phase 4: Sustain (Ongoing)](#phase-4-sustain-ongoing)
- [Batch Priority Matrix](#batch-priority-matrix)
- [Cross-References](#cross-references)

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
| 1 | Create `AGENTS.md` with only non-inferable details | 2 min | Portable baseline for agent instructions |
| 2 | Add Claude compatibility only if needed | 2 min | `CLAUDE.md` wrapper/import or symlink for Claude Code |
| 3 | Add build/test/lint commands to `AGENTS.md` | 2 min | Agents can verify their own work |
| 4 | Add `.claude/rules/` with one coding standard | 3 min | Consistent code style from agents |
| 5 | Add 2-3 repo-specific constraints or failure modes | 3 min | Higher signal than directory summaries |
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

## Key Patterns
- [Pattern 1: e.g., "All API routes use middleware chain in src/middleware/"]
- [Pattern 2: e.g., "Database queries go through repository pattern in src/repos/"]

## Known Constraints
- [Constraint 1: e.g., "Use pnpm only; npm lockfiles are rejected in CI"]
- [Constraint 2: e.g., "Playwright tests require local auth seed before running"]

## Conventions
- Commits: conventional commits (feat:, fix:, chore:)
- Branches: feature/*, fix/*, chore/*
- PRs: require 1 approval minimum
```

If your team uses Claude Code, add `CLAUDE.md` as either:

```markdown
@AGENTS.md
```

or a symlink if that is your team convention.

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

## Scoped Areas
- `src/auth/` — Authentication rules live in `src/auth/AGENTS.md`
- `src/payments/` — Payment rules live in `src/payments/AGENTS.md`
- `src/api/` — API layer with shared request/response patterns
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
# See agents-memory for templates

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

## Performance Budgets for the Hot Layer

<!-- Source: github.com/MemPalace/mempalace@6614b9b4e71e67da2236493b036b7bf42ba2d55f (MIT), extracted 2026-04-13 -->

Qualitative guidance like "keep it fast" doesn't survive a sprint. Pin numeric thresholds so CI can enforce them and so tradeoffs become visible at review time:

| Operation | Budget | Why |
|-----------|--------|-----|
| Session startup injection (loading L0+L1) | **< 100ms** | Anything slower is felt as lag on the first token |
| Pre-session hook (e.g. context assembly, environment checks) | **< 500ms** | Longer hooks push the user past the "it's ready" threshold and erode trust in automation |
| Post-response hook (background save, index write, cron trigger) | **< 500ms** | Must run out-of-band; user should never wait for it |
| Bookkeeping chat tokens (status messages, "saving…", "indexing…") | **Zero** | Background work should be invisible; every visible bookkeeping message is a tax on the real work |

**Enforcement**:
- Put a stopwatch in your hooks. Fail CI or log a warning when a hook exceeds its budget.
- Audit the always-on context monthly. If L0+L1 together cross ~1,000 tokens, the budget is being breached silently on every request.
- When something is slow, move it to the background (async, scheduled, post-response) rather than optimizing the hot path. "Background everything" is cheaper than "make the hot path twice as fast."

**Why zero bookkeeping tokens**: every "saving context now…" message costs tokens *and* user attention. Move the save to a PreCompact/Stop hook that runs after the response completes. The user sees the reply; the save runs invisibly. This pattern alone can cut per-session cost meaningfully when bookkeeping previously happened in the chat window.

## Cross-References

- **agents-memory** — Detailed AGENTS.md writing patterns
- **agents-memory/references/large-codebase-strategy.md** — 100K-1M LOC specific strategies
- **docs-ai-prd/references/architecture-extraction.md** — Extracting architecture from existing code
- **docs-ai-prd/references/convention-mining.md** — Mining conventions from codebases
- **maturity-model.md** — Self-assessment before and after onboarding
- **multi-repo-strategy.md** — Coordination patterns for batch onboarding
