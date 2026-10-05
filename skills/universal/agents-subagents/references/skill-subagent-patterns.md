---
description: Skill-to-subagent delegation: skills: preload (role pattern) and context: fork (task pattern).
last_verified: 2026-09-02
status: stable
---

# Skill ↔ Subagent Delegation Patterns

Skills and subagents can reference each other in two directions. Each direction solves a different problem. Pick the one that matches the actor you care about, not the one that matches the syntax you remember.

## Table of Contents

- [Direction 1: Subagent preloads skills (Role pattern)](#direction-1-subagent-preloads-skills-role-pattern)
- [Direction 2: Skill delegates to subagent (Task pattern)](#direction-2-skill-delegates-to-subagent-task-pattern)
- [Choosing the direction](#choosing-the-direction)
- [Safe defaults](#safe-defaults)
- [Related](#related)

## Direction 1: Subagent preloads skills (Role pattern)

Use when defining a **role** — a specialized agent that needs domain knowledge available from the first turn.

The `skills:` field in agent frontmatter injects skill content directly into the subagent's system prompt before any task runs. The subagent controls the prompt; skills are its reference material. Confirmed behavior: "Skills injected at startup (full content, not just availability)" — see [`../../agents-swarm-orchestration/references/platform-patterns.md`](../../agents-swarm-orchestration/references/platform-patterns.md) §"Subagent configuration".

```yaml
---
name: api-developer
description: Implements API endpoints following team conventions.
model: sonnet
tools: Read, Write, Edit, Bash
skills:
  - api-conventions
  - error-handling-patterns
  - auth-patterns
---

You are a senior backend engineer. Implement endpoints following the preloaded conventions.
```

When to use this pattern:

- A recurring role that always needs the same domain context
- A code reviewer that always loads your style guide
- A migration agent that always loads schema conventions
- A deployment agent that always loads your infra runbook

Important behavior:

- Skills inject as content, not as "available-for-use" metadata. The subagent sees the skill body in its system prompt from turn 1.
- `skills:` is **not** inherited by Agent Team teammates. Teammates load skills from project/user settings, not from the subagent definition. If you need a teammate to have specific skills, configure them at project scope.

## Direction 2: Skill delegates to subagent (Task pattern)

Use when you have a **task** that is too verbose or expensive to run inline and would pollute the main conversation with intermediate context.

The `context: fork` field in skill frontmatter spawns a subagent. The skill content becomes the task prompt, and the `agent:` field picks which subagent type executes it (e.g., `Explore`, `general-purpose`, or a custom agent name; defaults to `general-purpose` if omitted). The subagent runs in isolation and does the work. Current agent-view fork mode runs forked subagents in the background and returns their result through a completion notification.

**To make a forked skill block, set `background: false`.** It is a documented skill-frontmatter field: "Only applies with `context: fork`. Set to `false` to wait for the forked subagent's result in the turn that invoked the skill, instead of running it in the background. Default: `true`. Requires Claude Code v2.1.218 or later." Use it whenever the invoking turn needs the result. Before v2.1.218 forked skills always blocked, so on older runtimes there is no background mode to opt out of; the field exists because newer runtimes run forks in the background by default. Source: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills), verified 2026-09-02.

```yaml
---
name: deep-research
description: Research a topic thoroughly across the codebase.
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:
- Find all relevant files and patterns
- Identify how this is used across the project
- Summarize findings with file references
```

Key constraint: `context: fork` only makes sense for skills with **explicit task instructions**. A skill that contains only guidelines, conventions, or reference material will give the subagent context but no actionable direction, and the subagent will not produce useful output. If your skill body reads like a manual, do not set `context: fork` — write a proper agent file instead.

When to use this pattern:

- You already have a skill and want it to run in isolation without creating a full agent file
- The skill executes a bounded research or transformation task with a clear deliverable
- You want to isolate verbose intermediate steps from the lead context

For the authoritative field reference, see [`../../agents-skills/references/frontmatter-reference.md`](../../agents-skills/references/frontmatter-reference.md).

## Choosing the direction

| Pattern | Actor | Knowledge source | Use when |
|---------|-------|-----------------|----------|
| Subagent with `skills:` | Subagent (long-lived role) | Skills baked into prompt | Defining a role that always needs domain context |
| Skill with `context: fork` | Skill (ephemeral task) | Skill body is the task prompt | Running a verbose task in isolation |

If you are building something new, prefer creating a subagent. `context: fork` is best when a skill already exists and you want to add isolation without a separate agent file.

### The inverse-relationship framing (Anthropic)

Anthropic's current docs frame these two fields as strict inverses of each other:

> _"`skills:` in a subagent and `context: fork` in a skill are inverses. With `skills:`, the subagent owns the prompt and skills are preloaded reference material. With `context: fork`, the skill owns the prompt and the subagent is the executor that runs it."_ — Claude Code subagents + skill frontmatter docs (April 2026)

The operational consequence: never use both directions for the same pair of artifacts. If `skill-X` has `context: fork + agent: reviewer` **and** `reviewer` has `skills: [skill-X]`, you get a two-layer prompt cycle — the skill content appears once as the task prompt and again preloaded into the executor. Pick one direction. The one you pick is determined by **who should own the prompt**:

- Prompt is durable, shared across many tasks, domain-shaped → **subagent with `skills:`** (skill is reference material)
- Prompt is one task's instructions, you want it isolated from the lead context → **skill with `context: fork`** (subagent is the executor)

## Safe defaults

- Prefer `tools` over broad inheritance; use either `tools` or `disallowedTools`, not both.
- Keep `maxTurns` low for reviewer and research agents.
- Treat `memory` as opt-in — it automatically grants file-edit capability for the memory directory.
- When using `context: fork`, set a clear task-shaped skill body (imperatives, acceptance criteria, deliverable format). Guidelines-only skills fail this pattern.
- Verify `context: fork` availability against current Claude Code docs before relying on it operationally — skill frontmatter fields move faster than agent frontmatter fields.
- **Known issue (anthropics/claude-code#47350)**: a skill with `context: fork + agent: <name>` may silently bypass the executor agent's `model:` pin — the child inherits the parent's model instead. Verify with `/cost` or the context-timeline hook before relying on per-agent model pinning in fork mode. See [`subagent-context-forking.md`](subagent-context-forking.md) §"Cache-Prefix Sharing".

## Related

- [../SKILL.md](../SKILL.md) - Main subagent guide
- [agent-tools.md](agent-tools.md) - Tool, permission, MCP, and isolation guidance
- [runtime-surfaces.md](runtime-surfaces.md) - Claude Code + Codex runtime behavior and field mapping
- [../../agents-skills/SKILL.md](../../agents-skills/SKILL.md) - Skill packaging and `SKILL.md` conventions
- [../../agents-skills/references/frontmatter-reference.md](../../agents-skills/references/frontmatter-reference.md) - Full skill frontmatter field reference
- [../../agents-swarm-orchestration/references/platform-patterns.md](../../agents-swarm-orchestration/references/platform-patterns.md) - Current field matrix
