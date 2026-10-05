---
name: ai-coding-agents
description: "Creates coding-agent definitions (review, test, refactor, team) for Claude Code, Codex, and Agent SDK. Use when writing a code-review or test subagent, not a runtime."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-09-29
---

# AI Coding Agents — Creation Hub

Use this skill to go from a coding agent idea to a working agent definition, whether a single-purpose agent or a coordinated multi-agent coding team.

This skill owns the coding-domain-specific creation workflow, templates, and patterns. For agent architecture decisions and build-vs-not gates, start with [`../ai-agents/SKILL.md`](../ai-agents/SKILL.md).

## Two Different Tracks

This skill (and its siblings prefixed `ai-coding-agents-*`) split into two tracks with different audiences. Pick the right one before going deeper.

**Track A — Create an agent on an existing platform (this skill).**
Use this umbrella when the platform exists (Claude Code, Codex, or Agent SDK) and you need to define an agent on top of it: frontmatter, tools, archetype, multi-agent coordination. This is the common case.

**Track B: build a coding-agent runtime from scratch (the `ai-coding-agents-*` sibling skills).**
Use the dedicated curriculum when you are building the runtime itself: the thing that loads agents, sandboxes execution, routes tool calls, manages sessions. Each skill captures traps, patterns and anti-patterns for one subsystem. Build order and subsystem owners: [references/runtime-build-spine.md](references/runtime-build-spine.md).

| Concern | Skills |
|---------|--------|
| Tools and commands | [`ai-coding-agents-runtime-core`](../ai-coding-agents-runtime-core/SKILL.md) (registries, tool search, dispatch, slash commands) |
| Providers | [`ai-coding-agents-provider-runtime`](../ai-coding-agents-provider-runtime/SKILL.md) (abstraction, streaming, fallback routing) |
| Safety | [`ai-coding-agents-safety-envelope`](../ai-coding-agents-safety-envelope/SKILL.md) (approvals and local sandbox), `ai-coding-agents-cloud-sandboxes`, [`ai-coding-agents-settings-policy`](../ai-coding-agents-settings-policy/SKILL.md) (precedence, managed policy, fleet updates) |
| State | [`ai-coding-agents-state`](../ai-coding-agents-state/SKILL.md) (sessions, resume, checkpoints, tasks, triggers) |
| Surfaces | [`ai-coding-agents-surfaces`](../ai-coding-agents-surfaces/SKILL.md) (remote runtime, bridges, terminal UI) |
| Extensibility and delivery | [`ai-coding-agents-plugins`](../ai-coding-agents-plugins/SKILL.md) (also plugin and cache compatibility across upgrades), [`ai-coding-agents-observability-evals`](../ai-coding-agents-observability-evals/SKILL.md) |

If the request is "how do I add a slash command to my runtime?" or "how should I design approval prompts?", route to Track B. If it's "how do I define a code-review agent on Claude Code?", stay here.

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How do I create a coding agent end-to-end? | [references/creation-workflow.md](references/creation-workflow.md) | Step-by-step from idea to running agent |
| Which platform should I target? | [references/platform-patterns.md](references/platform-patterns.md) | Decision tree: `.md` vs `.toml` vs SDK |
| What single-agent archetypes exist? | [references/agent-archetypes.md](references/agent-archetypes.md) | Six patterns with frontmatter and tools |
| When should I use a multi-agent team? | [references/multi-agent-coding-patterns.md](references/multi-agent-coding-patterns.md) | Three architectures: coordinator, fork, swarm |
| How do I manage context for code-heavy work? | [references/context-management.md](references/context-management.md) | Token budgets, file selection, progressive disclosure |
| How do I wrap dev tools for agents? | [references/tool-integration.md](references/tool-integration.md) | Linter, formatter, test runner, type checker patterns |
| My agent is broken | [references/debugging-guide.md](references/debugging-guide.md) | Failure taxonomy and fixes |
| What do production coding agents look like? | [references/production-patterns.md](references/production-patterns.md) | Patterns from shipped coding-agent runtimes |
| Which prompt recipes steer a Claude Code session to a specific outcome? | [references/claude-code-prompt-recipes.md](references/claude-code-prompt-recipes.md) | 35 named recipes covering setup, planning, execution, review, debug/recovery, and session economics |

## When To Use

- Create a new coding agent from scratch on any supported platform
- Choose the right archetype for a coding task (review, test generation, refactoring, migration, docs, security)
- Design a multi-agent team for complex coding tasks (parallel reviews, bug investigation, migration fleets)
- Design context loading strategy for agents working with large codebases
- Wrap existing dev tools (linters, formatters, test runners, type checkers) for agent use
- Debug a coding agent producing poor results, hallucinated files, or scope creep
- Port a coding agent between platforms (Claude Code ↔ Codex ↔ Agent SDK)

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Agent architecture decisions, build-vs-not | [`../ai-agents/SKILL.md`](../ai-agents/SKILL.md) |
| Subagent frontmatter, delegation contracts | [`../agents-subagents/SKILL.md`](../agents-subagents/SKILL.md); read current field names, allowed values and tool-scoping syntax in its [`references/runtime-surfaces.md`](../agents-subagents/references/runtime-surfaces.md) instead of copying a field list; permission-mode restrictions live in [`../ai-coding-agents-safety-envelope/SKILL.md`](../ai-coding-agents-safety-envelope/SKILL.md) |
| MCP server setup and integration | [`../agents-mcp/SKILL.md`](../agents-mcp/SKILL.md) |
| Hook guardrails and lifecycle events | [`../agents-hooks/SKILL.md`](../agents-hooks/SKILL.md) |
| Skill packaging and SKILL.md conventions | [`../agents-skills/SKILL.md`](../agents-skills/SKILL.md) |
| Generic multi-agent orchestration, wave dispatch | [`../agents-swarm-orchestration/SKILL.md`](../agents-swarm-orchestration/SKILL.md) |
| AGENTS.md and CLAUDE.md configuration | [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md) |
| Any runtime subsystem (Track B table above) | The `ai-coding-agents-*` skill named there |
| Testing coding agents (evals, regression) | [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md) |
| Context loading strategies (generic) | [`../dev-context-engineering/SKILL.md`](../dev-context-engineering/SKILL.md) |
| Measuring coding agent ROI | [`../dev-ai-coding-metrics/SKILL.md`](../dev-ai-coding-metrics/SKILL.md) |
| Claude API and Agent SDK reference | claude-api skill |

## Default Workflow

The goal is a bounded agent whose scope, tools, and verification you can state in one sentence before it runs. Classify the task first — what code it touches, what tools it needs, what it emits — and decide single agent (one bounded task) or team (interdependent tasks, parallel reviews, complex investigation). Pick the closest [archetype](#single-agent-archetype-index) or [multi-agent pattern](#multi-agent-pattern-index), then the platform: Claude Code `.md` for repo-level agents, Codex `.toml` for Codex workflows, Agent SDK for programmatic integration. Start from the matching template in [assets/templates/](assets/templates/).

Scope tools to the minimum: read-only agents get Read, Grep, Glob; edit agents add Edit, Write, Bash. "Read-only" is enforced by the permission layer or the sandbox, never by the prompt: an agent granted Bash can write files, so a reviewer or scanner that needs Bash runs under deny rules for writing commands or inside a read-only sandbox. Design the context strategy alongside it — which files the agent needs, how it discovers them, what token budget it has — and decide how the agent checks its own work.

Rule: `rules/repo/agent-defs.md` loads this invariant when Claude edits an agent definition in this library.

Before copying a platform template, build a small capability record from the target runtime: available tools, writable roots, approval path, context-start behavior, background/cancellation support, and installed model. Treat configured, advertised, and successfully exercised capabilities as separate states; template parity does not prove runtime parity. A template counts as proven on a runtime only after a canary task has exercised its capability record there, including at least one action the record says must be denied.

Two verification checks before deploying:

- **Smoke test on 3+ representative tasks.** For teams, the verifier must be a separate agent, not the one that made the change.
- **Extension robustness for edit, refactor, and migration agents:** run at least one evolving-spec sequence with 3+ checkpoints, each started in a fresh conversation/context, carrying forward the same agent-created workspace and retaining all prior regression tests.

Then iterate on observed behavior: tighten scope, improve prompts.

Before the first session on a machine, run [`scripts/smoke_test.sh`](scripts/smoke_test.sh) (`--help` for details) against the project root: CLI installed, tool registry present, and sandbox enabled by parsed settings. The CLI check is an install check; it probes model access only when run with an API key and `SMOKE_TEST_MODEL`. A `[FAIL] Sandbox engaged` line means Bash in that project runs unsandboxed, so read-only archetypes are not enforced there.

Choose the model per task, not per agent fleet: route routine edits to a cheaper workhorse model and reserve the frontier model for the hard minority (planning, cross-module debugging, review of risky diffs). Savings figures for this split are practitioner self-reports, not measurements; before choosing the split, read the provider's current pricing page (and the runtime's model-config docs for which aliases resolve to which models), since tier names and per-token prices change between releases.

## Known Traps

- giving a coding agent repo-wide edit authority before the owned files and verification surface are clear
- asking the same agent to implement, review, and approve its own high-risk changes
- inheriting parent context blindly across phases instead of re-briefing from current repo truth
- building a multi-agent coding team before the task graph, file ownership, and merge plan exist
- assuming Claude Code, Codex, and SDK workers expose equivalent tools, hooks, and approval semantics
- treating one-shot green tests, a plan-first prompt, or an anti-slop prompt as evidence that edit-capable agents remain extensible over repeated changes

## Common Anti-Patterns

- "full-stack fixer" agents with no bounded artifact, path, or runtime scope
- tool wrappers that hide destructive commands behind vague natural-language instructions
- edit-capable workers launched in parallel on the same branch with no ownership contract
- context strategies that preload too much code instead of progressive disclosure and file selection
- smoke tests skipped because the prompt "looks right"

## OpenAI Internal Practice (Codex)

Validated-by-use patterns from OpenAI's internal Codex report: optional two-stage Ask to Code flow, environment-as-prompt, prompt-as-GitHub-issue, task queue as lightweight backlog, and Best-of-N as a generation primitive. Detail, sources and anti-patterns: [references/openai-internal-practice-codex.md](references/openai-internal-practice-codex.md). The task-sizing heuristic lives in [`../ai-coding-agents-state/SKILL.md`](../ai-coding-agents-state/SKILL.md).

## Platform Decision Tree

| Scenario | Platform | Why |
|----------|----------|-----|
| Repo-team agent, auto-delegated by description | Claude Code `.md` | Description-driven routing, shared via `.claude/agents/` |
| Codex thread workers | Codex `.toml` | Explicit spawning, sandbox-mode scoped |
| Non-interactive code review in CI | `codex review` subcommand | Headless, no terminal UI; structured output for pipelines |
| Programmatic, CI, or API integration | Agent SDK | Full control, custom tools, hook callbacks |
| Quick prototype | Claude Code `.md` | Fastest path to working agent |
| Multi-agent coordinator team | Claude Code `.md` | Subagents and agent teams; the coordinator is a pattern on the lead agent, not a documented runtime mode |
| Custom orchestration logic | Agent SDK | Programmatic control over spawning, routing, results |
| Local-first OSS coding agent, editor-integrated via ACP (Zed, JetBrains, IntelliJ) | Goose (Rust) + recipe YAML | ACP server mode; MCP extensions; custom distros; Apache-2.0 |
| Enterprise white-label coding agent with pinned providers and extensions | Goose Custom Distribution | Distro manifest baked into the binary; supply-chain gates (`deny.toml`); AAIF/LF governance |
| GitHub-centric repo, lightweight PR-aware agent, no multi-agent need | GitHub Copilot CLI custom agent (`.agent.md`) | Pre-wired GitHub MCP server, PR-scoped agent versioning; see Copilot CLI section below for its ceiling |

See [references/platform-patterns.md](references/platform-patterns.md) for side-by-side comparison and porting guide.

Goose (OSS, MCP and ACP, recipe YAML, custom distros) and GitHub Copilot CLI (`.agent.md` custom agents, no native multi-agent or sandbox-mode ladder) are covered in [references/additional-platforms-goose-and-copilot-cli.md](references/additional-platforms-goose-and-copilot-cli.md). Prefer Claude Code or Codex when the task needs a coordinator or team pattern, worktree isolation, or a documented permission-mode ladder.

## Single Agent Archetype Index

| Archetype | Core Tools | maxTurns | Key Constraint | Template |
|-----------|-----------|----------|----------------|----------|
| Code Reviewer | Read, Grep, Glob, Bash | 8 | Read-only enforced by deny rules or sandbox (Bash can write); findings-first output | [code-reviewer.md](assets/templates/code-reviewer.md) |
| Test Generator | Read, Write, Edit, Bash, Grep | 15 | Must run generated tests | [test-generator.md](assets/templates/test-generator.md) |
| Refactoring Agent | Read, Edit, Bash, Grep, Glob | 20 | Preserve behavior, run existing tests | [refactoring-agent.md](assets/templates/refactoring-agent.md) |
| Migration Agent | Read, Write, Edit, Bash, Grep, Glob | 25 | Pattern-at-a-time, checkpoint between batches | [migration-agent.md](assets/templates/migration-agent.md) |
| Documentation Agent | Read, Write, Grep, Glob | 12 | Source-anchored, no invented APIs | Universal template |
| Security Scanner | Read, Grep, Glob, Bash | 10 | Read-only enforced by deny rules or sandbox (Bash can write); severity-ordered output | [security-scanner.md](assets/templates/security-scanner.md) |

Each archetype is detailed in [references/agent-archetypes.md](references/agent-archetypes.md) with full frontmatter, system prompt structure, and failure modes.

## Multi-Agent Pattern Index

| Pattern | Communication | Isolation | Best For | Template |
|---------|--------------|-----------|----------|----------|
| Coordinator-Led Team | `<task-notification>` XML | Workers in background | Research → implement → verify loops | [coordinator-coding-team.md](assets/templates/coordinator-coding-team.md) |
| Fork Subagents | Implicit (context inherited) | Shared prompt cache | Parallel background exploration | See fork guidance below |
| Agent Teams (Peer Swarm) | Mailbox messaging (SendMessage) | Shared checkout; exclusive owned files per teammate | Self-coordinating specialists | [swarm-investigation.md](assets/templates/swarm-investigation.md) |
| Background Agents | Supervisor-managed sessions started and monitored from the runtime's agent view | Isolated git worktree per session | Long-running parallel tasks, tasks dispatched and monitored without keeping a terminal open | See background agent guidance below |
| ACP-Delegated Subagent | ACP stdio (line-delimited JSON) | Separate process; approvals round-trip through orchestrator | Cross-platform delegation (Goose → Claude Code, Goose → Codex, etc.) | See ACP delegation note below |

Pattern selection, coordinator, fork, peer-swarm, background-agent and ACP-delegation detail, and the shared multi-agent principles (never delegate understanding, freeze interfaces, exclusive owned files, separate verifiers, fresh workers at phase boundaries, files for state, escalation, notification-driven planning, nesting depth as a ceiling) are in [references/multi-agent-coding-patterns.md](references/multi-agent-coding-patterns.md).

## Context Management Essentials

Code is large and interdependent, so split the window into instructions, code and output budgets, read by progressive disclosure (directory structure, key files, then targeted sections), and separate read-only exploration from editing. Split into subagents with clear file ownership when a task spans more than 5-10 unrelated files. Detail: [references/context-management.md](references/context-management.md); skill-subagent isolation: [`../agents-subagents/SKILL.md`](../agents-subagents/SKILL.md).

## Templates and Entry Points

- Single agent: [claude-code-agent.md](assets/templates/claude-code-agent.md), [code-reviewer.md](assets/templates/code-reviewer.md), [test-generator.md](assets/templates/test-generator.md), [refactoring-agent.md](assets/templates/refactoring-agent.md), [migration-agent.md](assets/templates/migration-agent.md), [security-scanner.md](assets/templates/security-scanner.md)
- Multi-agent: [coordinator-coding-team.md](assets/templates/coordinator-coding-team.md), [swarm-investigation.md](assets/templates/swarm-investigation.md), [parallel-review-team.md](assets/templates/parallel-review-team.md)
- Cross-platform: [codex-agent.toml](assets/templates/codex-agent.toml), [sdk-agent-py.py](assets/templates/sdk-agent-py.py), [sdk-agent-ts.ts](assets/templates/sdk-agent-ts.ts)
- Checklists: [agent-design-checklist.md](assets/checklists/agent-design-checklist.md), [multi-agent-checklist.md](assets/checklists/multi-agent-checklist.md), [production-readiness.md](assets/checklists/production-readiness.md)

## Navigation

### References
- [references/creation-workflow.md](references/creation-workflow.md) — End-to-end creation guide
- [references/platform-patterns.md](references/platform-patterns.md) — Claude Code vs Codex vs Agent SDK
- [references/agent-archetypes.md](references/agent-archetypes.md) — Six single-agent coding patterns
- [references/multi-agent-coding-patterns.md](references/multi-agent-coding-patterns.md) — Three multi-agent architectures
- [references/context-management.md](references/context-management.md) — Token budgets and file strategies
- [references/tool-integration.md](references/tool-integration.md) — Dev tool wrapping patterns
- [references/debugging-guide.md](references/debugging-guide.md) — Failure taxonomy and fixes
- [references/production-patterns.md](references/production-patterns.md) — Patterns from shipped coding-agent runtimes
- [references/claude-code-prompt-recipes.md](references/claude-code-prompt-recipes.md) — Named prompt recipes for setup, planning, execution, review, and debug/recovery
- [references/openai-internal-practice-codex.md](references/openai-internal-practice-codex.md) — OpenAI internal Codex practice patterns
- [references/additional-platforms-goose-and-copilot-cli.md](references/additional-platforms-goose-and-copilot-cli.md) — Goose and GitHub Copilot CLI as target platforms
- [references/runtime-build-spine.md](references/runtime-build-spine.md) — Runtime build order with subsystem owners, invariants, false shortcuts

### Assets
- [assets/templates/](assets/templates/) — Agent definition and team templates
- [assets/checklists/](assets/checklists/) — Design, dispatch, and deployment checklists

### Data
- [`data/sources.json`](data/sources.json) — Primary documentation and research references

## Platform and Source Notes

- Agent definition field names and allowed values come from the runtime's current docs; read them in [`../agents-subagents/references/runtime-surfaces.md`](../agents-subagents/references/runtime-surfaces.md) and verify against current runtime behavior before depending on one.
- Platform-specific capabilities (Codex sandbox modes and current model names, SDK hook patterns, GitHub Copilot CLI's custom-agent and plugin surface) should be verified against current platform documentation — the Copilot CLI surface in particular moves faster than the rest of this platform list.
- Star counts, model names, and other numeric/product-name claims cited for Goose, career-ops, and similar community projects drift continuously; treat any figure here as a snapshot, not a live value.
## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

