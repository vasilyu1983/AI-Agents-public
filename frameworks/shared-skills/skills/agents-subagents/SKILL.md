---
name: agents-subagents
description: Create and maintain AI coding agent subagents (.claude/agents/*.md, .codex/agents/*.md) with YAML frontmatter (name/description/tools/model/permissionMode/skills/hooks), least-privilege tool selection, delegation patterns (Task), context budgeting, and safety best practices.
---

# Claude Code Agents

Create and maintain Claude Code agents/subagents with predictable behavior, least-privilege tools, and explicit delegation contracts.

## Quick Start

1. Create an agent file at `.claude/agents/<agent-name>.md` (kebab-case filename).
2. Add YAML frontmatter (required: `name`, `description`; optional: `tools`, `model`, `permissionMode`, `skills`, `hooks`).
3. Write the agent prompt: responsibilities, workflow, and an output contract.
4. Minimize tools: start read-only, then add only what the agent truly needs.
5. Test on a real task and iterate.

Minimal template:

```markdown
---
name: sql-optimizer
description: Optimize SQL queries, explain tradeoffs, and propose safe indexes
tools: Read, Grep, Glob
model: sonnet
---

# SQL Optimizer

## Responsibilities
- Diagnose bottlenecks using query shape and plans when available
- Propose optimizations with risks and expected impact

## Workflow
1. Identify the slow path and data volume assumptions
2. Propose changes (query rewrite, indexes, stats) with rationale
3. Provide a verification plan

## Output Contract
- Summary (1–3 bullets)
- Recommendations (ordered)
- Verification (commands/tests to run)
```

## Workflow (2026)

1. Define the agent’s scope and success criteria.
2. Choose a model based on risk, latency, and cost (default to `sonnet` for most work).
3. Choose tools via least privilege; avoid granting `Edit`/`Write` unless required.
4. If delegating with `Task`, define a handoff contract (inputs, constraints, output format).
5. Add safety rails for destructive actions and secrets.
6. Add a verification step (checklist, tests, or a dedicated verifier agent).

## Frontmatter Fields (Summary)

- `name` (REQUIRED): kebab-case; match filename (without `.md`).
- `description` (REQUIRED): state when to invoke + what it does; include keywords users will say.
- `tools` (OPTIONAL): explicit allow-list; prefer small, purpose-built sets.
- `model` (OPTIONAL): `haiku` for fast checks, `sonnet` for most tasks, `opus` for high-stakes reasoning, `inherit` to match parent.
- `permissionMode` (OPTIONAL): prefer defaults; change only with a clear reason and understand the tradeoffs.
- `skills` (OPTIONAL): preload skill packs for domain expertise; keep the list minimal.
- `hooks` (OPTIONAL): automate guardrails; prefer using the hooks skill for patterns and safety.

For full tool semantics and permission patterns, use `references/agent-tools.md`. For orchestration and anti-patterns, use `references/agent-patterns.md`.

## 2026 Best Practices (Domain Expertise)

- Use small, specialized agents; avoid “god agents”.
- Keep agent prompts short; put repo conventions in `CLAUDE.md`/project memory and domain knowledge in skills.
- Budget context: pass file paths, minimal snippets, and constraints; avoid dumping long logs/code.
- Use explicit handoffs for subagents: “Goal / Constraints / Inputs / Output Contract”.
- Add a verifier step for risky changes (security, migrations, infra, auth).
- Treat CLI fields/features as moving; verify against official docs in `data/sources.json`.

## Validation Checklist

- Frontmatter: `name` matches filename; `description` is single-line and trigger-oriented; tools are minimal; model fits risk.
- Prompt: responsibilities are concrete; workflow is actionable; output contract is explicit.
- Delegation: subagent briefs are specific and bounded; orchestrator verifies integration.
- Safety: confirm destructive ops; avoid secrets/PII; follow repository policies.

## Navigation

- `frameworks/shared-skills/skills/agents-subagents/references/agent-patterns.md`
- `frameworks/shared-skills/skills/agents-subagents/references/agent-tools.md`
- `frameworks/shared-skills/skills/agents-subagents/data/sources.json`
- `frameworks/shared-skills/skills/agents-skills/SKILL.md`
- `frameworks/shared-skills/skills/agents-hooks/SKILL.md`

## Operational Guardrails: Subagent Orchestration

Use these defaults unless the user explicitly asks for wider fan-out.

### Hard Limits

- Keep active subagents <= 3.
- Keep each subagent scope to one responsibility and a bounded file set.
- Do not let multiple subagents edit the same file in parallel.

### Handoff Template (Required)

```text
Goal:
Constraints:
Owned files:
Do-not-touch files:
Output format:
Definition of done:
```

### Merge Discipline

1. Wait for subagent outputs.
2. Review for overlap/conflicts.
3. Integrate one subagent result at a time.
4. Run verification gates before final synthesis.

### Stop Conditions

Stop and re-plan when:
- two subagents propose conflicting edits to same module,
- repeated retries happen without new evidence,
- context window starts dropping prior decisions.

