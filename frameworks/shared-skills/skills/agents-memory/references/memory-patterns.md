# Project Memory Patterns (AGENTS.md / CLAUDE.md)

Common patterns for effective project memory configuration.

Use these templates as the content for `AGENTS.md` (Codex). If you support both tools, keep `AGENTS.md` as the single source of truth and symlink `CLAUDE.md` to it.

---
## Table of Contents

- [Pattern 1: Minimal Core Memory](#pattern-1-minimal-core-memory)
- [Pattern 0: Layered Memory Model](#pattern-0-layered-memory-model)
- [Hot memory](#hot-memory)
- [Episodic recall](#episodic-recall)
- [Procedural memory](#procedural-memory)
- [Prompt stability rules](#prompt-stability-rules)
- [Project Name](#project-name)
- [Stack](#stack)
- [Commands](#commands)
- [Code Standards](#code-standards)
- [Pattern 2: Team Standards Memory](#pattern-2-team-standards-memory)
- [Project Name](#project-name)
- [Architecture](#architecture)
- [Git Workflow](#git-workflow)
- [Code Review](#code-review)
- [Testing](#testing)
- [Pattern 3: Claude-Friendly Reference-Heavy Memory](#pattern-3-claude-friendly-reference-heavy-memory)
- [Project Name](#project-name)
- [Quick Reference](#quick-reference)
- [Current Sprint](#current-sprint)
- [Agent Preferences](#agent-preferences)
- [Pattern 4: Monorepo Memory](#pattern-4-monorepo-memory)
- [Monorepo Standards](#monorepo-standards)
- [Shared Rules](#shared-rules)
- [Package Commands](#package-commands)
- [Web Package](#web-package)
- [Stack](#stack)
- [Testing](#testing)
- [Pattern 5: Local Overrides Without Polluting Shared Memory](#pattern-5-local-overrides-without-polluting-shared-memory)
- [Personal Defaults](#personal-defaults)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [Don't: Generic Instructions](#dont-generic-instructions)
- [Bad Example](#bad-example)
- [Don't: Duplicate Code Comments](#dont-duplicate-code-comments)
- [Bad Example](#bad-example)
- [UserService](#userservice)
- [Don't: Outdated Information](#dont-outdated-information)
- [Bad Example](#bad-example)
- [Database](#database)
- [Don't: Sensitive Data](#dont-sensitive-data)
- [Bad Example](#bad-example)
- [Pattern 6: Behavioral Coding Rules](#pattern-6-behavioral-coding-rules)
- [Coding Behavior Rules](#coding-behavior-rules)
- [Before Implementation](#before-implementation)
- [During Implementation](#during-implementation)
- [After Changes](#after-changes)
- [Pattern 7: Cross-Platform Memory (AGENTS.md + CLAUDE.md)](#pattern-7-cross-platform-memory-agentsmd-claudemd)
- [Directory Structure](#directory-structure)
- [Setup Commands](#setup-commands)
- [AGENTS.md primary](#agentsmd-primary)
- [Copy approach (simpler, requires manual sync)](#copy-approach-simpler-requires-manual-sync)
- [Or create sync script in package.json](#or-create-sync-script-in-packagejson)
- ["sync:agents": "cp AGENTS.md CLAUDE.md"](#syncagents-cp-agentsmd-claudemd)
- [Unified Memory File Template](#unified-memory-file-template)
- [Project Name](#project-name)
- [Overview](#overview)
- [Architecture](#architecture)
- [Code Standards](#code-standards)
- [Shared Working Rules](#shared-working-rules)
- [Tool-Specific Notes](#tool-specific-notes)
- [Claude Code](#claude-code)
- [Codex CLI](#codex-cli)
- [Cursor](#cursor)
- [Tool Compatibility Matrix](#tool-compatibility-matrix)
- [Best Practices](#best-practices)
- [Pattern 8: Multi-Agent Safety Rules](#pattern-8-multi-agent-safety-rules)
- [Multi-Agent Safety](#multi-agent-safety)
- [Git State Protection](#git-state-protection)
- [Scoped Commits](#scoped-commits)
- [Unrecognized Files](#unrecognized-files)
- [Lint/Format Churn](#lintformat-churn)
- [Session Isolation](#session-isolation)
- [Pattern 9: Quality Gates & Operational Guardrails](#pattern-9-quality-gates-&-operational-guardrails)
- [Quality Gates & Guardrails](#quality-gates-&-guardrails)
- [PR Evidence Gates (Bug-Fix Validation)](#pr-evidence-gates-bug-fix-validation)
- [Release Guardrails](#release-guardrails)
- [Shorthand Commands](#shorthand-commands)
- [Agent Vocabulary](#agent-vocabulary)
- [Automation Labels](#automation-labels)
- [Pattern 10: Retrospective AGENTS.md Updates](#pattern-10-retrospective-agentsmd-updates)
- [Pattern 11: config.toml + AGENTS.md Separation](#pattern-11-configtoml-agentsmd-separation)
- [Pattern 12: Prompt / Agent Library Repo](#pattern-12-prompt--agent-library-repo)
- [Pattern 13: Progressive Disclosure Architecture](#pattern-13-progressive-disclosure-architecture)
- [Pattern 14: Three-Tier Boundaries](#pattern-14-three-tier-boundaries)
- [Pattern 15: Feedback Loop Instructions](#pattern-15-feedback-loop-instructions)
- [Memory Size Guidelines](#memory-size-guidelines)


## Pattern 0: Layered Memory Model

Before writing more into `AGENTS.md`, decide which memory layer the information belongs to.

### Hot memory

Use always-loaded project memory only for small, durable facts that should shape almost every session:

- repo purpose and key directories
- exact build, test, and lint commands
- weird local setup or deployment quirks the agent will not discover reliably
- hard constraints and prohibitions
- stable architectural boundaries
- repeated workflow corrections

Do not use the hot layer for long meeting notes, daily logs, transient task state, or README-level summaries.

### Episodic recall

Past conversations, decisions, and work history belong in searchable history, not in the always-loaded prompt layer.

Good episodic recall surfaces:

- issue trackers
- searchable notes or logs
- session databases or indexed transcript stores
- decision logs and changelogs

The rule is simple: if it is important sometimes rather than every turn, retrieve it on demand.

### Procedural memory

If the agent needs to remember how to do something repeatedly, turn that into a skill or automation rather than another paragraph in `AGENTS.md`.

Good procedural memory candidates:

- release checklists
- migration playbooks
- investigation flows
- repeatable formatting or packaging workflows

### Prompt stability rules

- Keep the always-loaded layer compact and stable for caching and predictability.
- Treat `AGENTS.md` / `CLAUDE.md` as living exception files, not general knowledge bases.
- If a fact is inferable from source code, manifests, lint config, or the README, keep it out of hot memory by default.
- Prefer frozen or infrequently edited project memory over constant append-only updates.
- Promote repeated methods into skills.
- Route long histories into searchable systems.
- Summarize before re-injecting anything from historical context back into the active task.

## Pattern 1: Minimal Core Memory

Best for small projects. Keep the primary memory file under 50 lines.

```markdown
# Project Name

Brief one-line description.

## Stack
- Frontend: React, TypeScript
- Backend: Node.js, PostgreSQL

## Commands
- `npm run dev` - Start development
- `npm test` - Run tests
- `npm run build` - Production build

## Code Standards
- TypeScript strict mode
- Prettier for formatting
- ESLint for linting
```

**When to use**: Projects with <10 files, solo developers, simple architectures.

---

## Pattern 2: Team Standards Memory

For teams needing consistent conventions across developers.

```markdown
# Project Name

## Architecture
- Monorepo with Turborepo
- Shared packages in /packages
- Apps in /apps

## Git Workflow
- Branch from `main`
- PR required for all changes
- Squash merge only
- Conventional commits: feat:, fix:, chore:

## Code Review
- 1 approval minimum
- CI must pass
- No console.log in production code

## Testing
- Unit tests for utilities
- Integration tests for APIs
- E2E for critical paths
- 80% coverage minimum
```

**When to use**: Teams of 2+, shared codebases, CI/CD pipelines.

---

## Pattern 3: Claude-Friendly Reference-Heavy Memory

Use `@` imports when Claude should pull detailed documentation on demand. For Codex, keep the essential shared rules inline and use nested `AGENTS.md` files for directory-specific context instead.

```markdown
# Project Name

High-level overview only in this file.

## Quick Reference
- @docs/architecture.md - System design
- @docs/api-patterns.md - API conventions
- @docs/testing-guide.md - Test requirements
- @.claude/agents/README.md - Available agents

## Current Sprint
- Feature X in progress
- Bug Y needs fixing

## Agent Preferences
- Use `backend-engineer` for API work
- Use `test-architect` for coverage
```

**When to use**: Large codebases, detailed documentation exists, token optimization needed.

---

## Pattern 4: Monorepo Memory

Hierarchical memory for multi-package repositories.

```text
monorepo/
├── AGENTS.md              # Primary memory file
├── CLAUDE.md              # Symlink → AGENTS.md
├── packages/
│   ├── web/
│   │   ├── AGENTS.md      # Web-specific
│   │   └── CLAUDE.md      # Symlink → AGENTS.md
│   ├── api/
│   │   ├── AGENTS.md      # API-specific
│   │   └── CLAUDE.md      # Symlink → AGENTS.md
│   └── shared/
│       ├── AGENTS.md      # Shared lib
│       └── CLAUDE.md      # Symlink → AGENTS.md
```

**Root memory file (AGENTS.md or CLAUDE.md)**:
```markdown
# Monorepo Standards

## Shared Rules
- All packages use TypeScript
- Shared ESLint config
- Turborepo for builds

## Package Commands
- `turbo run build` - Build all
- `turbo run test` - Test all
- `turbo run dev --filter=web` - Dev specific
```

**Package memory file (AGENTS.md or CLAUDE.md)**:
```markdown
# Web Package

Inherits from root. Additional rules:

## Stack
- Next.js 16 App Router
- Tailwind CSS
- Zustand for state

## Testing
- Vitest for unit
- Playwright for E2E
```

---

## Pattern 5: Local Overrides Without Polluting Shared Memory

Keep machine-local or developer-local preferences out of committed project memory.

- **Claude Code**: use `.claude/settings.local.json` for local settings such as `claudeMdExcludes` and other machine-local controls from the official docs.
- **Claude auto memory**: keep it enabled for personal notes and repeated local reminders, but do not rely on it as the shared project contract.
- **Codex**: use `~/.codex/AGENTS.md` for personal defaults across repositories.
- **Repo-local Codex overrides**: if you need a developer-only layer inside one repo, keep `AGENTS.override.md` git-ignored and make sure the committed `AGENTS.md` still stands on its own.

```json
{
  "claudeMdExcludes": [
    "docs/vendor/CLAUDE.md"
  ]
}
```

```markdown
<!-- ~/.codex/AGENTS.md -->

# Personal Defaults

- Prefer `rg` for search
- Ask before destructive commands
- Keep summaries concise
```

---

## Anti-Patterns to Avoid

### Don't: Philosophy Blocks

Long coding manifestos consume always-loaded context but rarely create reliable behavior change.

Prefer:

- concrete constraints
- exact commands
- recurring failure modes
- specific examples of mistakes to avoid

Not:

- generic "write elegant code"
- abstract design essays
- duplicated style rules already enforced by tools

### Don't: Generic Instructions

```markdown
# Bad Example
- Write clean code
- Follow best practices
- Be efficient
```

### Don't: Duplicate Code Comments

```markdown
# Bad Example
## UserService
The UserService handles user operations...
(already documented in code)
```

### Don't: Outdated Information

```markdown
# Bad Example
## Database
Using MySQL 5.7  # Actually migrated to PostgreSQL
```

### Don't: Sensitive Data

```markdown
# Bad Example
API_KEY=sk-12345...  # Never put secrets here
```

---

## Pattern 6: Behavioral Coding Rules

Explicit cognitive guardrails to prevent common AI failure modes (assumption errors, scope creep, over-engineering).

**Canonical source**: [`references/coding-behavior.md`](coding-behavior.md) inside this skill. The file below is a simplified illustration — the canonical file has been refined with Karpathy-derived patterns (goal transformation, trace test, 200-line heuristic, orphan distinction, tradeoff disclosure, working-if metric). When installing the skill, symlink the canonical file into your repo instead of copying the inline snippet:

```bash
# From your repo root
mkdir -p .claude/rules
ln -sf ~/.claude/skills/agents-memory/references/coding-behavior.md .claude/rules/coding-behavior.md
```

**Active file**: `.claude/rules/coding-behavior.md` (project-local, typically a symlink to the skill's canonical file)

```markdown
# Coding Behavior Rules

## Before Implementation

- **Surface assumptions**: List them explicitly, ask for correction before proceeding
- **Manage confusion**: STOP when encountering ambiguity, name the specific confusion, wait for resolution
- **Inline planning**: For multi-step tasks, emit lightweight plan before executing

## During Implementation

- **Scope discipline**: Touch only what's asked—no unsolicited cleanup, refactoring, or "improvements"
- **Simplicity enforcement**: Prefer boring, obvious solutions; if 100 lines suffice, don't write 1000
- **Push back when warranted**: Point out problems directly; "Of course!" to bad ideas helps no one

## After Changes

- **Change summary**: Report CHANGES MADE / INTENTIONALLY UNTOUCHED / POTENTIAL CONCERNS
- **Dead code hygiene**: Identify unreachable code explicitly, ask before deleting
- **Preserve unknowns**: Don't remove code or comments you don't fully understand
```

**When to use**: Teams experiencing AI over-engineering, scope creep, silent assumption errors, or sycophantic responses.

**Key failure modes this prevents**:
1. Making wrong assumptions without checking
2. Not surfacing inconsistencies or tradeoffs
3. Being sycophantic ("Of course!") to bad ideas
4. Overcomplicating code and APIs
5. Modifying code orthogonal to the task

---

## Pattern 7: Cross-Platform Memory (AGENTS.md + CLAUDE.md)

Share project memory and behavioral rules across multiple AI coding tools.

### Directory Structure

```text
your-project/
├── AGENTS.md                    # Primary (Codex) or mirror
├── CLAUDE.md                    # Primary (Claude Code) or mirror
└── .claude/
    └── rules/
        ├── coding-behavior.md   # Behavioral rules (tool-agnostic)
        ├── security.md          # Security rules
        └── testing.md           # Testing standards
```

### Setup Commands

**macOS/Linux** (symlink):
```bash
# AGENTS.md primary
ln -sf AGENTS.md CLAUDE.md
```

**Windows** (copy or script):
```powershell
# Copy approach (simpler, requires manual sync)
Copy-Item AGENTS.md CLAUDE.md

# Or create sync script in package.json
# "sync:agents": "cp AGENTS.md CLAUDE.md"
```

### Unified Memory File Template

```markdown
# Project Name

Cross-platform instructions for AI coding assistants.

## Overview
Brief project description...

## Architecture

See `docs/architecture.md` for the long-form design.

## Code Standards
- TypeScript strict mode
- Prettier + ESLint
- 80% test coverage

## Shared Working Rules
- Surface assumptions before implementation
- Stop on ambiguity and call out the confusion
- Touch only requested files unless asked to broaden scope
- Run the relevant tests before handoff when behavior changes

## Tool-Specific Notes

### Claude Code
- Split extra detail into `.claude/rules/*.md`
- Use `.claude/settings.local.json` for local excludes and settings
- Skills in `.claude/skills/` are better than long always-loaded memory

### Codex CLI
- Reads AGENTS.md directly
- Use nested `AGENTS.md` files in packages or services for local context
- Keep essential shared rules inline here; do not assume Claude-style imports

### Cursor
- Mirror the shared essentials into Cursor's native config if needed
```

### Tool Compatibility Matrix

| Feature | Claude Code | Codex CLI | Cursor |
|---------|-------------|-----------|--------|
| Primary file | CLAUDE.md | AGENTS.md | .cursorrules |
| Shared inline rules | ✓ | ✓ | ✓ |
| `@imports` in project memory | Documented | Do not assume | Limited |
| `.claude/rules/` | Native | Not a Codex feature | Copy needed |
| Symlink support | ✓ | ✓ | ✓ |

### Best Practices

1. **Single source of truth**: Keep AGENTS.md as primary, symlink CLAUDE.md
2. **Tool-agnostic rules**: Write rules that work for any AI assistant
3. **Inline the essentials**: Shared rules should not require Claude-only features
4. **Git-track symlinks**: Symlinks work in git repos across platforms

**When to use**: Teams using multiple AI coding assistants (Claude Code + Cursor, Claude Code + Codex CLI, etc.) who want consistent behavior across all tools.

---

## Pattern 8: Multi-Agent Safety Rules

Explicit guardrails for projects running 2+ AI agents in parallel on the same repository.

```markdown
# Multi-Agent Safety

## Git State Protection
- Do **not** create/apply/drop `git stash` entries unless explicitly requested.
  Assume other agents may be working; keep unrelated WIP untouched.
- Do **not** create/remove/modify `git worktree` checkouts unless explicitly
  requested.
- Do **not** switch branches or check out a different branch unless explicitly
  requested.

## Scoped Commits
- When the user says "commit", scope to your changes only.
- When the user says "commit all", commit everything in grouped chunks.
- When the user says "push", you may `git pull --rebase` to integrate latest
  changes but never discard other agents' work.

## Unrecognized Files
- When you see unrecognized files (from other agents), keep going.
- Focus on your changes and commit only those.
- End with a brief "other files present" note only if relevant to your task.

## Lint/Format Churn
- If staged+unstaged diffs are formatting-only, auto-resolve without asking.
- If commit/push already requested, auto-stage formatting-only changes in the
  same commit — no extra confirmation needed.
- Only ask when changes are semantic (logic, data, or behavior).

## Session Isolation
- Running multiple agents is OK as long as each agent has its own session.
- Focus reports on your edits; avoid guard-rail disclaimers unless truly blocked.
```

**When to use**: Any project running 2+ AI coding agents in parallel (Claude Code sessions, Codex tasks, Cursor + Claude Code, etc.). Add these rules before the first multi-agent collision, not after.

**Key failure modes this prevents**:
1. Agent A stashes Agent B's uncommitted work
2. One agent switches branches while another is mid-task
3. Agents commit each other's files, creating confused git history
4. Agents interrupt workflow to ask about formatting diffs from other agents
5. Agents add verbose disclaimers about "other files" in every response

---

## Pattern 9: Quality Gates & Operational Guardrails

Explicit evidence bars, release gates, and operational shortcuts that prevent hallucinated fixes, accidental publishes, and ambiguous commands.

```markdown
# Quality Gates & Guardrails

## PR Evidence Gates (Bug-Fix Validation)
- Never merge a bug-fix PR based only on issue text, PR text, or AI rationale.
- Minimum merge gate for bug-fix PRs:
  1. Symptom evidence (repro steps, logs, or failing test)
  2. Verified root cause in code with file and line reference
  3. Fix touches the implicated code path
  4. Regression test (fail before / pass after) when feasible;
     if not feasible, include manual verification proof
- If a claim is unsubstantiated or likely hallucinated: do not merge.

## Release Guardrails
- Do not change version numbers without explicit consent.
- Always ask permission before running any publish or release step.
- Index all version locations so no file is missed during bumps:
  - `package.json`, platform build files, docs with pinned versions

## Shorthand Commands
- Define project-specific command aliases to reduce ambiguity:
  - Example: `sync` = commit dirty changes → git pull --rebase → git push
  - Example: `bump` = update all version locations except auto-generated files

## Agent Vocabulary
- Define domain-specific shorthand that agents should understand:
  - Example: "makeup" = "mac app" (the macOS application)
  - Example: "gate run" = "CI pipeline on the PR branch"

## Automation Labels
- Document workflow automation labels so agents use them instead of
  manual close/comment:
  - `r: support` → auto-close with redirect to community channels
  - `r: spam` → auto-close + lock
  - `invalid` → close as not_planned
```

**When to use**: Projects where agents triage issues, merge PRs, or perform release tasks. Especially important when agents can take irreversible actions (merge, publish, close).

**Key failure modes this prevents**:
1. Hallucinated bug fixes merged without evidence
2. Accidental version bumps or npm publishes
3. Ambiguous shorthand commands leading to wrong actions
4. Agents manually closing issues that should use automation labels
5. Missing version locations during release bumps

---

## Pattern 10: Retrospective AGENTS.md Updates

When Codex repeats the same mistake, ask it to analyze the failure and propose an `AGENTS.md` rule.

**Process**:
1. Observe the repeated failure (e.g., wrong test command, missed lint step)
2. Ask Codex: "Analyze what went wrong and propose an AGENTS.md update"
3. Format the rule as: `[Rule] + [Why this rule exists] + [Example of the mistake]`
4. Add the rule to `AGENTS.md`, not to the prompt
5. Delete rules that no longer apply

**When to use**: Any time Codex (or another agent) repeats a correctable mistake. Reactive rules based on real friction are more useful than preemptive rules based on theory.

---

## Pattern 11: config.toml + AGENTS.md Separation

Keep operational infrastructure in `config.toml` and team workflow guidance in `AGENTS.md`.

**config.toml** (`.codex/config.toml`):
```toml
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"

[agents]
max_threads = 6
max_depth = 1
```

**AGENTS.md**:
```markdown
## Repo Layout
- src/ — application code
- tests/ — test suites

## Commands
- `npm test` — run all tests
- `npm run lint` — check formatting

## Constraints
- Never commit directly to main
```

**Anti-pattern**: putting model selection, sandbox mode, or MCP server config in `AGENTS.md`. These are infrastructure concerns that belong in `config.toml`.

---

## Pattern 12: Prompt / Agent Library Repo

For repositories whose primary purpose is storing and maintaining AI prompt files, Custom GPT configs, agent skills, and frameworks — as opposed to an application that *calls* AI APIs. The unique constraints are platform character caps, YAML/markdown parity, archive hygiene, and skill cross-linking rules.

**File**: `CLAUDE.md`

```markdown
# [Repo Name]

Prompt and agent library — not a product repo.

## Repo Areas
- `custom-gpt/` — Custom GPT instruction files and configs
- `ai-agents/` — Agent SDK implementation assets
- `frameworks/` — Reusable skills and development kits

## Standard Agent File Pattern
1. `01_agent-name.md` — main instruction file
2. `02_sources-agent-name.json` — curated sources
3. `agent-name.yaml` — runtime/config mapping

Optional: `03_supplemental.md`, `0X_data.json`, `sources/` (git-ignored), `.archive/` (git-ignored)

## Platform Constraints
- Custom GPT instruction files: hard limit **8000 characters**
- Target 7500–7900 chars for safe margin
- Validate: `wc -c path/to/01_agent-name.md`
- If over limit: split into numbered files, not prose cuts

## YAML / Markdown Alignment
When editing any `01_*.md` prompt, keep its sibling YAML aligned:
- `## COMMANDS` in markdown matches YAML `commands` names
- YAML `max_chars` matches the markdown OUTPUT CONTRACT cap
- `framework`, `tone`, `answer_shape` consistent across md/yaml

## Archive and Token Discipline
Never read or scan `.archive/` directories unless explicitly requested.
- Search: `rg <pattern> -g '!**/.archive/**'`
- Find: `find . -type f ! -path '*/.archive/*'`

## Skill Cross-Linking Rules
- `project-*` skills are self-contained — never cross-link from domain or router skills
- Skills within the same project family can reference each other
- Keep `router-main` as universal entry point; domain routers own detailed journeys

## Validation

```bash
# Unresolved placeholders
rg "{{[^}]+}}" custom-gpt -g '!**/.archive/**'

# Command parity
rg -n '^## COMMANDS' custom-gpt -g '!**/.archive/**'
rg -n 'name:\s*/[A-Za-z0-9:_-]+' custom-gpt -g '!**/.archive/**'

# Character cap
wc -c custom-gpt/**/01_*.md
```

## Editing Rules
- Preserve safety/precedence/workflow constraints unless task requires changing them
- YAML: two-space indentation, lowercase keys
- Do not rename files/directories unless requested
- Do not create summary/report files by default (SUMMARY.md, CHANGELOG.md, etc.)
```

**When to use**: Any repository that IS a library of AI prompts, Custom GPT configs, agent skills, or frameworks — as distinct from an app that uses AI.

**Key failure modes this prevents**:
1. Instruction files silently truncated at the platform's character cap
2. YAML config out of sync with markdown commands — agent receives wrong affordances
3. Archive files polluting search results and AI context windows
4. Cross-linked `project-*` skills breaking isolation and causing context leakage
5. Missing validation before shipping prompt updates

---

## Pattern 13: Progressive Disclosure Architecture

Keep the root memory file lean by pointing to detailed documentation instead of inlining it. The agent sees the pointers in every session but only loads full documents when working in the relevant area.

```markdown
# Project Name

Brief description.

## Commands
- `npm test` - Run tests
- `npm run build` - Production build
- `npm run lint` - Lint code

## Code Standards
- TypeScript strict mode
- Prettier for formatting

## Documentation (load on demand)

When working in these areas, read the relevant doc first:

- **Architecture**: `docs/architecture.md` — system design and module boundaries
- **API patterns**: `docs/api-patterns.md` — REST conventions, error handling
- **Database**: `docs/database-schema.md` — schema docs (load if working with DB)
- **Testing**: `docs/testing-guide.md` — advanced testing patterns and fixtures

## Constraints
[hard boundaries that apply every session]
```

**When to use**: Any project where the root memory file would exceed ~100 lines if all context were inlined. Works especially well when detailed documentation already exists in `docs/`.

**How it works per tool**:
- **Claude Code**: Can use `@docs/architecture.md` import syntax for explicit loading. Agent also searches for files naturally based on the pointers.
- **Codex**: Prefers nested `AGENTS.md` files in directories. Use plain prose pointers ("see `docs/architecture.md`") rather than Claude-specific `@` syntax.

**Key benefit**: Root file stays under 80 lines. Token cost per session drops because detailed docs are loaded on demand rather than always. Agent still knows where to look.

---

## Pattern 14: Three-Tier Boundaries

Structure agent permissions using an explicit Always / Ask / Never model. This replaces scattered constraints and vague "be careful" instructions with clear decision rules that agents can follow mechanically.

```markdown
## Boundaries

### Always Do
- Run tests after code changes
- Update types when changing function signatures
- Read existing similar code as reference before writing new code
- Preserve existing safety constraints unless task requires changing them

### Ask First
- Installing new dependencies
- Modifying database schema or migrations
- Changing API contracts or public interfaces
- Deleting files or removing exports
- Broadening scope beyond the requested task

### Never Do
- Force-push to main or protected branches
- Commit secrets, credentials, or PII
- Delete test files or remove failing tests
- Modify authentication or authorization systems without review
- Create summary/report files unless explicitly requested
```

**When to use**: Any project. Place this section near the top of `AGENTS.md` so the agent sees it early in the context window.

**Why it works**: Research across 2,500+ repositories shows agents handle explicit permission tiers better than mixed prose. The three-tier model reduces ambiguity — agents know exactly which actions they can take autonomously, which require confirmation, and which are forbidden.

**Adaptation**: Start with the template above, then add project-specific boundaries as real incidents occur (e.g., "Never update the Carbon dependency" after a breakage incident).

---

## Pattern 15: Feedback Loop Instructions

Explicit verification steps are the single highest-impact practice for agent efficiency. Agents perform 2–3x better when they can verify their own work through tight feedback loops rather than handing off unchecked output.

```markdown
## Verification

After code changes, run all applicable:
1. `npm test` — confirm no regressions
2. `npm run lint` — confirm style compliance
3. `npm run typecheck` — confirm type safety

After prompt or config edits:
1. `wc -c <edited-file>` — confirm within platform character cap
2. `rg "{{[^}]+}}" <edited-dir>` — confirm no unresolved placeholders

After database changes:
1. `npm run db:migrate` — apply migration
2. `npm run db:seed` — verify seed data still works

After UI changes (if Playwright MCP available):
1. Open the page in browser
2. Verify the change is visible
3. Check for console errors
```

**When to use**: Every project. This is the single most impactful addition you can make to project memory. Without it, agents implement changes but skip verification, leading to 2–3x more iteration cycles.

**Pattern**: Frame verification as a checklist, not prose. Use exact, copy-pasteable commands. Group by change type so the agent selects the relevant checks.

**How it compounds**: When the agent runs tests → sees failures → fixes them → reruns, the tight loop resolves issues in one session instead of requiring human round-trips.

---

## Pattern 16: Intent Split — Strategic Context vs Per-Task Intent

**Symptom**: Every prompt repeats the same project context ("we're a B2B SaaS that …", "our stack is …", "never touch the billing module without review"), and the agent still occasionally ignores it. Prompts are long; memory is either empty or bloated with process instructions. Introduced for Opus 4.7 (2026-04-16), where literal interpretation and native progress emission changed the payoff of each line.

**Antidote**: Split what belongs in durable memory (strategic context — *what we're building, who it's for, what good looks like, what's off-limits, exact commands*) from what belongs in each prompt turn (per-task intent — *this specific refactor/bugfix/feature*). Memory carries the constants; the prompt carries the variable.

### Example CLAUDE.md / AGENTS.md (strategic only)

```markdown
# Project: Acme Billing

## What we're building
Subscription billing for mid-market SaaS. Stripe-backed. UK-domiciled.

## What good looks like
- Idempotent webhooks (all handlers must be safe to replay)
- Every money value is a `Money{amount_minor, currency}` — never a float
- Read-model projections live under `src/projections/`; command handlers under `src/commands/`

## Off-limits without explicit approval
- `src/projections/ledger.ts` (append-only audit trail)
- Database migrations touching `invoices` or `ledger_entries`

## Commands
- `pnpm test` — full suite
- `pnpm test:webhook` — replay integration tests
- `pnpm typecheck`
```

Per-task intent then stays in the prompt:

> Refactor `getSubscription` in `src/commands/getSubscription.ts` to use the new DI container. Keep behavior identical — the existing test suite must pass unchanged.

### When NOT to apply

- One-shot scripts or throwaway repos where you will open one session and close it.
- Workspaces where the "strategic context" legitimately changes every session (research notebooks, scratch repos).
- When the prompt is already short and memory is already tight — don't invent structure to solve a non-problem.

**Source**: [Anthropic: Best practices for using Claude Opus 4.7 with Claude Code](https://claude.com/blog/best-practices-for-using-claude-opus-4-7-with-claude-code) (2026-04-16); Pawel Huryn migration guide (2026-04-20).

---

## Memory Size Guidelines

| Project Size | Primary File Lines | Strategy |
|--------------|-----------------|----------|
| Small (<10 files) | 20-50 | Single file, minimal |
| Medium (10-100 files) | 50-100 | Core + docs/rules split |
| Large (100+ files) | 50-100 | Nested AGENTS + Claude rules |
| Monorepo | 30-50 per package | Inheritance pattern |

**Rule**: If the primary memory file exceeds 150 lines, move deep detail into docs, skills, or nested per-directory memory files.

**Instruction budget**: Agent compliance drops after approximately 150–200 discrete instructions in always-loaded memory. Every line costs instruction budget, not just tokens. This means:
- A 300-line file with vague rules performs worse than a 100-line file with precise rules.
- Rules enforced by linters or formatters should not also live in project memory.
- Generic advice ("write clean code") wastes budget without creating behavior change.
- Ruthless pruning improves agent behavior more than comprehensive documentation.
