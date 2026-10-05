---
description: Reviewer, implementer, researcher, and verifier patterns plus anti-patterns for custom subagents.
last_verified: 2026-09-16
status: stable
---

# Claude Code Subagent Patterns

Use these patterns for custom subagents in `.claude/agents/`. Keep them focused, predictable, and easy for Claude to delegate to automatically.

## Table of Contents

- [Core Rules](#core-rules)
- [Pattern 1: Reviewer](#pattern-1-reviewer)
- [Pattern 2: Bounded Implementer](#pattern-2-bounded-implementer)
- [Pattern 3: Researcher](#pattern-3-researcher)
- [Pattern 4: Browser Verifier](#pattern-4-browser-verifier)
- [Pattern 5: Domain Role Agent](#pattern-5-domain-role-agent)
  - [Reuse as Agent Team Teammates](#reuse-as-agent-team-teammates)
- [Description Patterns](#description-patterns)
- [Handoff Pattern](#handoff-pattern)
- [When To Escalate To Agent Teams](#when-to-escalate-to-agent-teams)
- [Codex TOML Examples](#codex-toml-examples)
  - [PR Review Team](#pr-review-team)
  - [Frontend Debugging Team](#frontend-debugging-team)
- [Pattern 6: Debate Team (Collaborative Debate)](#pattern-6-debate-team-collaborative-debate)
  - [Claude Code Setup](#claude-code-setup)
  - [Debate Protocol](#debate-protocol)
  - [Codex Setup](#codex-setup)
  - [Claude Code Agent Teams (Experimental)](#claude-code-agent-teams-experimental)
  - [Cost Awareness](#cost-awareness)
  - [Alternative: MCP Debate Server](#alternative-mcp-debate-server)
- [Pattern 7: Member + Team Deployment](#pattern-7-member--team-deployment)
  - [Structure](#structure)
  - [Inline Brief Convention](#inline-brief-convention)
  - [How Members Differ From Templates](#how-members-differ-from-templates)
  - [Workflow Contracts](#workflow-contracts)
- [Anti-Patterns](#anti-patterns)
  - [Name Collision (Codex)](#name-collision-codex)
  - [God Agent](#god-agent)
  - [Vague Trigger](#vague-trigger)
  - [Swarm Logic In A Subagent Skill](#swarm-logic-in-a-subagent-skill)
  - [Memory Without A Reason](#memory-without-a-reason)
- [Related](#related)

Each pattern section carries a complete agent-file template; the `Workflow` and
`Output Contract` headings inside those templates are template content, not
document sections, so they are not linkable.

## Core Rules

- One subagent, one primary responsibility
- One clear output contract
- One bounded capability profile
- One explicit reason to exist beyond a built-in agent

The patterns below are **teaching shapes** — minimal frontmatter and a workflow skeleton to illustrate the role. For deployment-ready, fully-wired versions, copy a canonical member from [`agents/claude/`](../../../../agents/claude/) or [`agents/codex/`](../../../../agents/codex/) (e.g. `dev-feature-reviewer`, `dev-feature-implementer`, `software-security-reviewer`). Members carry `skills:` wiring and family-prefix naming that the inline patterns below intentionally omit.

## Pattern 1: Reviewer

Best for:

- code review
- migration review
- regression scanning
- "check this before I commit"

Template:

```markdown
---
name: code-reviewer
description: Review diffs for correctness, regression risk, and missing tests. Use proactively after code changes or before commits.
tools: Read, Grep, Glob, Bash
maxTurns: 8
model: sonnet
---

# Code Reviewer

Review changes for bugs, regressions, and missing verification.

## Workflow
1. Inspect the changed files and nearby code paths
2. Identify correctness risks and missing tests
3. Return findings ordered by severity

## Output Contract
- Findings
- Open questions
- Verification gap
```

Why it works:

- the trigger is concrete
- the output is findings-first
- the tool set is still narrow

## Pattern 2: Bounded Implementer

Best for:

- a defined feature slice
- a contained bug fix
- owned-file changes with a verification command

Template:

```markdown
---
name: implementation-worker
description: Implement a bounded change in owned files and report verification results. Use when the task has clear file ownership and acceptance criteria.
tools: Read, Grep, Glob, Edit, Write, Bash
permissionMode: acceptEdits
maxTurns: 12
isolation: worktree
model: sonnet
---

# Implementation Worker

Implement only the requested change within the owned files.

## Workflow
1. Read the owned files and acceptance criteria
2. Make the smallest correct change
3. Run the required verification
4. Report what changed and what was verified

## Output Contract
- Summary
- Files changed
- Verification results
- Risks or blockers
```

Why it works:

- file ownership is explicit
- verification is mandatory
- worktree isolation reduces parallel-edit contention

## Pattern 3: Researcher

Best for:

- current framework behavior
- library migration notes
- source-backed comparisons

Template:

```markdown
---
name: docs-researcher
description: Research current framework or platform behavior and return a cited recommendation. Use proactively when an answer depends on current external docs.
tools: Read, Grep, Glob, WebFetch, WebSearch
maxTurns: 10
model: sonnet
---

# Docs Researcher

Gather current facts from primary sources and recommend the best path.

## Workflow
1. Search current official documentation
2. Read the most relevant pages
3. Compare options against the local codebase need
4. Return a recommendation with sources

## Output Contract
- Summary
- Findings with sources
- Recommendation
- Known uncertainty
```

Why it works:

- it turns "go look things up" into a bounded artifact
- it separates current-facts work from implementation

## Pattern 4: Browser Verifier

Best for:

- reproducing UI bugs
- verifying checkout or onboarding flows
- capturing screenshots and console/network evidence

Template:

```markdown
---
name: browser-verifier
description: Reproduce and verify web flows in a real browser with screenshots and logs. Use when debugging or validating browser behavior.
tools: Read, Grep, Glob
mcpServers:
  - playwright
background: true
maxTurns: 10
model: sonnet
---

# Browser Verifier

Use the browser to reproduce the issue or verify the target flow.

## Workflow
1. Follow the provided reproduction or verification steps
2. Capture screenshots and any console/network evidence
3. Report pass/fail and the exact failing step

## Output Contract
- Result
- Reproduction steps followed
- Evidence captured
- Recommended next action
```

Why it works:

- MCP scope is specific
- write access is not granted
- background mode fits longer verification passes

## Pattern 5: Domain Role Agent

Best for:

- non-developer specialists (marketing, product, business, design)
- cross-functional team compositions
- reusable persona definitions that work both as subagents and agent team teammates

Template:

```markdown
---
name: marketing-strategist
description: Analyze positioning, messaging, and go-to-market strategy. Use when evaluating campaigns, landing pages, competitive positioning, or launch plans.
tools: Read, Grep, Glob, WebFetch, WebSearch
maxTurns: 12
model: sonnet
skills:
  - marketing-content-strategy
  - marketing-seo
---

# Marketing Strategist

Evaluate marketing assets and strategy from a growth marketing perspective.

## Workflow
1. Read the asset or plan under review
2. Assess positioning, messaging clarity, and audience fit
3. Check competitive differentiation and channel alignment
4. Return actionable recommendations with priority

## Output Contract
- Assessment summary
- Strengths and weaknesses
- Prioritized recommendations
- Competitive gaps identified
```

Why it works:

- domain skills are preloaded so the agent starts with expert knowledge
- the description is trigger-rich for non-code tasks
- it can be reused as an agent team teammate via its definition name

Other domain role examples:

| Role | Skills to Preload | Key Tools | Use Case |
|------|-------------------|-----------|----------|
| Business Analyst | `product-management`, `startup-business-models` | Read, Grep, WebSearch | Requirements analysis, competitive research, business case review |
| Product Manager | `product-management`, `marketing-product-analytics` | Read, Grep, Glob, WebSearch | Feature prioritization, spec review, user story refinement |
| UX Designer | `software-ui-ux-design`, `software-ux-research` | Read, Grep, Glob | Design review, flow critique, accessibility audit |
| Security Auditor | `software-security-appsec`, `qa-security-testing` | Read, Grep, Glob, Bash | Threat modeling, vulnerability triage, compliance checks |

### Reuse as Agent Team Teammates

Any subagent definition works as an agent team teammate. When spawning a teammate, reference the subagent by name:

```text
Spawn a teammate using the marketing-strategist agent type to review the landing page copy.
```

The teammate inherits the definition's `tools` and `model`, and the body is appended to its system prompt (for a split-pane teammate the body *replaces* the default system prompt). `skills` from the definition are never applied to a teammate — it loads skills from your project and user settings instead. `mcpServers` are applied only to a split-pane teammate; an in-process teammate ignores the field and loads MCP servers from project and user settings ([agent-teams docs](https://code.claude.com/docs/en/agent-teams#use-subagent-definitions-for-teammates)).

To ensure teammates have domain knowledge, either:

- include the critical context directly in the subagent body (always works)
- ensure the relevant skills are in the project or user skill locations the runtime loads automatically (`.claude/skills/` and `~/.claude/skills/` on Claude Code; the Codex equivalent under `~/.agents/skills/`)

## Description Patterns

Strong description:

```text
Review diffs for correctness, regression risk, and missing tests. Use proactively after code changes or before commits.
```

Weak description:

```text
Helps with engineering work.
```

Rules:

- include the artifact or trigger
- include the outcome
- avoid generic helper wording

## Handoff Pattern

Use this structure when delegating to a subagent:

```text
Goal:
Constraints:
Owned files:
Read-only context:
Do-not-touch:
Deliverable:
Verification:
```

If the task cannot name owned files or a deliverable, the task is probably not ready for a subagent yet.

## When To Escalate To Agent Teams

Prefer agent teams instead of a single subagent when:

- specialists need to talk to each other directly
- the work benefits from persistent background collaboration
- the parent thread should supervise multiple workers at once
- you need a leader-worker structure instead of one-shot delegation

Important:

- agent teams are still an optional Claude Code capability; if they are not enabled in the current environment, keep the coordination logic in the parent thread instead

## Codex TOML Examples

### PR Review Team

Three read-only agents working in parallel on a pull request.

**`.codex/agents/pr-explorer.toml`**:
```toml
name = "pr_explorer"
description = "Read-only codebase explorer for gathering evidence before changes are proposed."
model = "<mechanical-tier-model>"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Stay in exploration mode.
Trace the real execution path, cite files and symbols, and avoid proposing fixes unless the parent agent asks for them.
Prefer fast search and targeted file reads over broad scans.
"""
```

**`.codex/agents/reviewer.toml`**:
```toml
name = "reviewer"
description = "PR reviewer focused on correctness, security, and missing tests."
model = "<critical-tier-model>"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Review code like an owner.
Prioritize correctness, security, behavior regressions, and missing test coverage.
Lead with concrete findings, include reproduction steps when possible, and avoid style-only comments unless they hide a real bug.
"""
```

**`.codex/agents/docs-researcher.toml`** (MCP-connected):
```toml
name = "docs_researcher"
description = "Documentation specialist that uses the docs MCP server to verify APIs and framework behavior."
model = "<mechanical-tier-model>"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Use the docs MCP server to confirm APIs, options, and version-specific behavior.
Return concise answers with links or exact references when available.
Do not make code changes.
"""

[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
```

### Frontend Debugging Team

Three agents for reproducing and fixing UI issues.

**`.codex/agents/code-mapper.toml`**:
```toml
name = "code_mapper"
description = "Read-only codebase explorer for locating the relevant frontend and backend code paths."
model = "<mechanical-tier-model>"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Map the code that owns the failing UI flow.
Identify entry points, state transitions, and likely files before the worker starts editing.
"""
```

**`.codex/agents/browser-qa-debugger.toml`** (MCP + workspace-write):
```toml
name = "browser_debugger"
description = "UI qa-debugger that uses browser tooling to reproduce issues and capture evidence."
model = "<critical-tier-model>"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"
developer_instructions = """
Reproduce the issue in the browser, capture exact steps, and report what the UI actually does.
Use browser tooling for screenshots, console output, and network evidence.
Do not edit application code.
"""

[mcp_servers.chrome_devtools]
url = "http://localhost:3000/mcp"
startup_timeout_sec = 20
```

**`.codex/agents/ui-fixer.toml`** (implementation-focused, with optional runtime-specific skill wiring):
```toml
name = "ui_fixer"
description = "Implementation-focused agent for small, targeted fixes after the issue is understood."
model = "<mechanical-tier-model>"
model_reasoning_effort = "medium"
developer_instructions = """
Own the fix once the issue is reproduced.
Make the smallest defensible change, keep unrelated files untouched, and validate only the behavior you changed.
"""

## Optional runtime-specific skill wiring example
#
# This illustrates a possible Codex skill preload shape. The `agents-subagents`
# canonical members in this repo currently rely on inline briefs plus artifact-backed
# handoff because the repo does not yet ship a validated cross-environment skills
# preload example.
[[skills.config]]
path = "/Users/me/.agents/skills/docs-editor/SKILL.md"
enabled = false
```

## Pattern 6: Debate Team (Collaborative Debate)

Best for:

- architecture decisions with competing valid approaches
- feature design tradeoffs (security vs UX, speed vs correctness)
- strategy choices where different stakeholder lenses matter
- pre-implementation alignment to prevent rework during fan-out

This pattern runs a structured multi-persona debate before dispatching implementation workers. Inspired by BMAD Party Mode and the SWE-Debate protocol (Li et al., *SWE-Debate: Competitive Multi-Agent Debate for Software Issue Resolution*, [arXiv:2507.23348](https://arxiv.org/abs/2507.23348), ICSE 2026 Research Track). See the [agents-swarm-orchestration Pre-Dispatch section](../../agents-swarm-orchestration/SKILL.md) for orchestration context.

### Claude Code Setup

Three agent files in `.claude/agents/`:

- `debate-orchestrator.md` — spawns perspective agents, runs rounds, produces decision log
- `perspective-agent.md` — reusable persona template (architect, marketer, user, etc.)
- `debate-synthesizer.md` — judges positions and produces a structured recommendation

Templates in `agents/templates/debate-orchestrator.md`, `agents/templates/perspective-agent.md`, and `agents/templates/debate-synthesizer.md`. For step-by-step setup instructions, see [debate-quickstart.md](debate-quickstart.md).

### Debate Protocol

1. **Round 1 (parallel):** Orchestrator spawns 2-4 perspective agents simultaneously. Each receives the decision prompt, context, and their persona assignment. Each returns an independent structured position (stance + arguments + risks + modifications).
2. **Round 2 (optional, parallel):** For high-stakes decisions, feed Round 1 positions back to each agent for rebuttal. Agents address counterarguments and may update their stance.
3. **Round 3 (single):** Synthesizer agent receives all positions and rebuttals, produces a decision log with recommendation, tradeoff, dissent, conditions, and action items.

Skip Round 2 when positions converge in Round 1 or the decision is medium-stakes.

### Codex Setup

Three TOML files in `.codex/agents/`:

**`.codex/agents/perspective-architect.toml`**:
```toml
name = "perspective_architect"
description = "Evaluates decisions from a system architecture lens: complexity, scalability, coupling, tech debt."
model = "<critical-tier-model>"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
You are a senior software architect evaluating a decision.
Be genuinely opinionated. Hedging weakens the debate.
Return: stance (support/oppose/conditional), max 3 arguments with evidence, risks with severity, suggested modifications.
Name your known bias: you tend to over-engineer and resist pragmatic shortcuts.
"""
```

**`.codex/agents/perspective-marketer.toml`**:
```toml
name = "perspective_marketer"
description = "Evaluates decisions from a growth and user-acquisition lens: positioning, conversion, differentiation."
model = "<critical-tier-model>"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
You are an experienced growth marketer evaluating a decision.
Be genuinely opinionated. Hedging weakens the debate.
Return: stance (support/oppose/conditional), max 3 arguments with evidence, risks with severity, suggested modifications.
Name your known bias: you tend to over-weight optics and demo-ability over substance.
"""
```

**`.codex/agents/debate-synthesizer.toml`**:
```toml
name = "debate_synthesizer"
description = "Synthesizes multi-perspective debate positions into a decision log with clear recommendation."
model = "<critical-tier-model>"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
You are a judge, not a diplomat. Pick a direction — do not split the difference.
Name what is being traded away. Weight arguments by evidence quality, not by how many agents agree.
If perspectives disagree, report the disagreement and explain your reasoning.
Never fabricate consensus.
Return: recommendation, rationale, key tradeoff, dissent (steelmanned), conditions, action items.
"""
```

Trigger in Codex: "Spawn architect, marketer, and user perspective agents to debate [decision]. Then spawn the synthesizer to produce a decision log."

### Claude Code Agent Teams (Experimental)

If agent teams are enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), teammates can debate directly without the orchestrator routing messages:

```
Spawn 3 agent teammates as architect, marketer, and end-user perspectives.
Have them debate [decision prompt] and challenge each other's positions.
After 2 rounds, produce a decision log with consensus, dissent, and action items.
```

Agent teams provide native inter-agent messaging and a shared task list. This is the highest-fidelity debate but is experimental and token-expensive (each teammate is a separate Claude instance).

### Cost Awareness

A 3-persona, 2-round debate costs roughly 6x a single-agent analysis. Use this for decisions where the cost of a wrong choice exceeds the cost of the debate. For routine decisions, a single-agent analysis with explicit tradeoff prompting is sufficient.

### Alternative: MCP Debate Server

For teams that want a formal protocol, the [multi-agent-debate-mcp](https://github.com/albinjal/multi-agent-debate-mcp) server provides structured `register → argue → rebut → judge` actions on a single `multiagentdebate` MCP tool; check its repository for the current action set before depending on it. Add it to `mcpServers` in the orchestrator agent for protocol-enforced debate with transcript tracking.

## Pattern 7: Member + Team Deployment

Best for:

- deploying a ready-made team of agents for a common scenario
- ensuring dual-platform coverage (Claude Code + Codex) from the same source
- reducing setup friction for recurring team compositions

The canonical model is **canonical members** (deduplicated native agent definitions in [`agents/`](../../../../agents/)) composed by repository **team recipes** ([`agents/teams/*/team.yaml`](../../../../agents/teams/)). The YAML is launcher metadata, not runtime configuration. Each member ships Claude (`.md`) and Codex (`.toml`) variants from the same role contract.

### Structure

```text
assets/
  members/
    claude/     # canonical .md agent definitions
    codex/      # canonical .toml agent definitions
  teams/
    {team}/
      team.yaml # references member ids; no duplicate agent files
```

Deploy with `scripts/deploy-preset.sh`:

```bash
bash scripts/deploy-preset.sh --list                # available teams
bash scripts/deploy-preset.sh --list-members        # available canonical members
bash scripts/deploy-preset.sh software-code-review-board --platform claude --project
bash scripts/deploy-preset.sh software-security-reviewer --member --platform codex --user
```

### Inline Brief Convention

Each canonical member includes an inline role brief (20-40 lines of distilled domain knowledge) in the body. This serves two purposes:

1. **As a subagent**: the `skills:` field loads full skill content. The inline brief provides additional structure.
2. **As a teammate**: the `skills:` field is NOT applied. The inline brief is the agent's only domain knowledge. It must be self-sufficient.

The brief should capture the 20% of a skill that drives 80% of the value: key frameworks, checklists, and decision criteria.

### How Members Differ From Templates

| Aspect | Template | Canonical Member |
|--------|----------|------------------|
| Purpose | Starting point to customize | Ready to deploy |
| Customization | Expected | Optional |
| Dual-platform | Single-platform (role-only shapes) | Always both `.md` and `.toml` |
| Skills | None | Mapped to specific domain skills via `skills:` (Claude) and derived `[[skills.config]]` (Codex) |
| Inline brief | Minimal | Full role brief for teammate mode |
| Naming | Generic role labels | Family-prefix canonical ids (e.g. `software-security-reviewer`) |

### Workflow Contracts

Use [workflow-contracts.md](workflow-contracts.md) for the canonical ownership, evidence, sequencing, output, and cleanup requirements that apply across saved workflows, interactive Claude Agent Teams, and explicit Codex subagents. See [team-lifecycle.md](team-lifecycle.md) for the full setup → run → cleanup sequence.

## Anti-Patterns

### Name Collision (Codex)

```toml
name = "explorer"
```

Problem: a custom agent with the same name as a built-in agent (default, worker, explorer) overrides the built-in. This silently replaces Codex's standard behavior. Use distinct names for custom agents.

### God Agent

```yaml
name: do-everything
description: Handle all development tasks
tools: Read, Grep, Glob, Edit, Write, Bash, WebFetch, WebSearch
```

Problem: poor delegation quality, context bloat, and unclear safety boundaries.

### Vague Trigger

```yaml
description: Help with code stuff
```

Problem: Claude cannot tell when to delegate.

### Swarm Logic In A Subagent Skill

Problem: dependency waves, conflict resolution, and multi-worker retry policy belong in [../../agents-swarm-orchestration/SKILL.md](../../agents-swarm-orchestration/SKILL.md), not in an ordinary subagent definition.

### Memory Without A Reason

Problem: persistent memory becomes noise if the source of truth already lives in project memory or repo docs.

## Related

- [agent-tools.md](agent-tools.md) - Tools, permission, MCP, and isolation guidance
- [subagent-interruption-recovery.md](subagent-interruption-recovery.md) - Recovery steps for interrupted workers
- [../SKILL.md](../SKILL.md) - Main subagent guide
- [../../agents-swarm-orchestration/SKILL.md](../../agents-swarm-orchestration/SKILL.md) - Multi-worker orchestration
