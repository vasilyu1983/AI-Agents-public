# Skill vs. Agent vs. Both — Decision Matrix

Use this reference when you are unsure whether to write a skill, a subagent, or both.

---

## Table of Contents

- [One-Sentence Definitions](#one-sentence-definitions)
- [Decision Matrix](#decision-matrix)
- [Canonical Patterns](#canonical-patterns)
- [Anti-Patterns](#anti-patterns)
- [Skill vs. AGENTS.md / CLAUDE.md](#skill-vs-agentsmd--claudemd)
- [Boundary Rules (Repo-Specific)](#boundary-rules-repo-specific)
- [Quick Checklist Before Writing Anything](#quick-checklist-before-writing-anything)
- [References](#references)

---

## One-Sentence Definitions

- **Skill** — a reusable prompt fragment + reference files loaded into an agent's context to give it domain knowledge or a repeatable procedure. No runtime process; no tool calls of its own.
- **Subagent** — a separate agent process dispatched by an orchestrating parent, operating with its own context, tool access, and execution scope.
- **Both** — a skill provides the domain knowledge; a subagent executes the work using that skill as context.

---

## Decision Matrix

| Question | If YES → | If NO → |
|----------|---------|---------|
| Does the capability need to run autonomously in parallel with other work? | Subagent | Skill |
| Does it require tool calls (bash, write, read, browser)? | Subagent | Skill |
| Is the knowledge reusable across many agents and sessions? | Skill | Consider a one-off prompt |
| Does it need to return a structured result to an orchestrator? | Subagent | Skill |
| Is it purely instructional — patterns, anti-patterns, decision guides? | Skill | Consider whether runtime action is needed |
| Does it involve long-running or expensive operations (scans, builds, evals)? | Subagent | Skill |
| Will multiple agents with different roles need the same domain knowledge? | Skill (shared) | Subagent-only |
| Is there a repeatable, multi-step procedure that should be teachable? | Skill + Subagent | Depends on isolation needs |
| Does the work modify files or state that must be isolated from the parent? | Subagent | Skill |
| Is it a decision framework (flowchart, matrix, rules)? | Skill | Subagent |

---

## Canonical Patterns

### Write a Skill when:

- You are encoding domain knowledge — "how to do X" — that many agents need
- You want to teach an agent a procedure it runs step by step in its own context
- The capability is read-only guidance with no tool calls
- You need a prompt to be loadable on demand without spinning up a new process
- Example: a security checklist, an API design guide, a coding behavior ruleset

### Write a Subagent when:

- The task needs tool access (file reads, writes, bash, browser)
- You want isolation — the work should not pollute the parent's context
- You are fanning out parallelizable work (3+ independent paths)
- The result is a structured artifact the parent must receive and act on
- The task is long-running or has a hard wall-clock budget
- Example: a research agent that reads 20 files and returns a summary

### Write Both when:

- A subagent needs domain knowledge to do its job well
- The skill encodes the "what and why"; the subagent does the "how" with tools
- You want the same domain knowledge reusable across many subagent types
- Example: a `dev-api-design` skill loaded into a `dev-api-designer` subagent

---

## Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|-------------|---------|-----------------|
| Writing a subagent when a skill would do | Adds runtime cost and process overhead for no isolation benefit | Write a skill; load it into the calling agent |
| Writing a skill when tool calls are needed | Skill cannot execute — the agent must still manually follow every step | Write a subagent with the skill loaded as context |
| Putting tool-call logic in a skill | Skills are loaded as prompt text; tool calls in them are never executed | Move tool-call logic into a subagent definition or script |
| One monolithic skill for an entire domain | Skills become too large to load selectively | Split into focused skill files; link from an index |
| Writing a skill per agent instead of per domain | Knowledge gets duplicated across many files | Write one skill per domain; load it into multiple agents |
| Subagent for every tiny task | Context and latency overhead exceed the benefit | Use a skill or inline prompt for tasks under 5 tool calls |

---

## Skill vs. AGENTS.md / CLAUDE.md

A skill is invoked on demand. `AGENTS.md` (or `CLAUDE.md`) is loaded into every turn. That difference matters more than it looks.

Vercel's published evals found:

- Skills were **never invoked** in 56% of relevant cases despite being available — implicit triggering is brittle.
- Skills with explicit prompt instructions reached 79% accuracy on their target tasks.
- The same content placed in `AGENTS.md` reached 100% accuracy.
- Skills even underperformed the no-skill baseline on some metrics because trigger ambiguity introduced new failure modes.

This does not mean skills are wrong — it means they are wrong for some content. Use this matrix:

| Question | If YES → | If NO → |
|----------|---------|---------|
| Should this guidance apply to **every** turn, regardless of task? | `AGENTS.md` / `CLAUDE.md` | Skill |
| Is the content general conventions, style, or repo-wide rules? | `AGENTS.md` | Skill |
| Is the content >5K tokens of mostly-irrelevant detail per request? | Skill (cost wins) | `AGENTS.md` |
| Does the content only apply to a narrow trigger (deploys, PDFs, migrations)? | Skill | `AGENTS.md` |
| Is correctness so critical that a 50% miss rate is unacceptable? | `AGENTS.md` | Skill |
| Does the content have side effects you want manually triggered? | Skill with `disable-model-invocation: true` | `AGENTS.md` |
| Will it grow into a procedure with steps, validation, and scripts? | Skill | `AGENTS.md` |

Rule of thumb: **convention → AGENTS.md, capability → skill**. Style guides, naming rules, and "always do X" go in `AGENTS.md`. Multi-step workflows, domain-specific procedures, and on-demand reference go in skills. When in doubt, measure: if a skill triggers under 80% on its own evals, the content probably belongs in `AGENTS.md`.

Source: [Vercel — AGENTS.md outperforms skills in our agent evals](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals).

---

## Boundary Rules (Repo-Specific)

These rules apply to this repo's `frameworks/shared-skills/skills/` structure:

- `project-*` skills are self-contained. Do not cross-link them to domain or router skills.
- Subagent team definitions live in `agents-subagents/assets/` — not inside individual project or domain skills.
- A skill encodes the knowledge; the subagent manifest (`assets/members/`) wires the knowledge to an agent identity.
- `router-main` is the universal entry point. It routes by scenario; it does not contain domain knowledge itself.

---

## Quick Checklist Before Writing Anything

1. Search `frameworks/shared-skills/graph/graph.json` (or the per-router Mermaid files) — does a relevant skill already exist?
2. Check `agents-subagents/assets/members/` — does a relevant subagent already exist?
3. If both exist: load the skill into the subagent rather than duplicating content.
4. If neither exists: decide using the matrix above, then create the skill first, then the subagent if needed.

---

## References

- Skill structure guide: `frontmatter-reference.md`
- Skill validation: `skill-validation.md`
- Skill patterns: `skill-patterns.md`
- Subagent patterns: `../../agents-subagents/references/skill-subagent-patterns.md`
- Anthropic skills guide: `anthropic-skills-guide.md`
