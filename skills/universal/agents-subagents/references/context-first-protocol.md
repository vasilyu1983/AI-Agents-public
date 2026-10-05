---
description: Canonical context rule for every member, team, and debate participant — fresh-context principle, preferred artifact inputs, handoff order, and the authoritative discovery rule.
last_verified: 2026-09-16
status: stable
---

# Context-First Protocol

## Table of Contents

- [Fresh Context Principle](#fresh-context-principle)
- [The Rule](#the-rule)
- [Preferred Context Inputs](#preferred-context-inputs)
- [When Artifacts Are Missing or Stale](#when-artifacts-are-missing-or-stale)
- [When the Brief Itself Is Unclear: Ask Before Assuming](#when-the-brief-itself-is-unclear-ask-before-assuming)
- [Discovery Rule (Authoritative)](#discovery-rule-authoritative)
- [Member Workflow Template](#member-workflow-template)
- [Team Recipe Template](#team-recipe-template)
- [Debate Orchestrator Handoff](#debate-orchestrator-handoff)
- [Anti-Patterns](#anti-patterns)
- [Verification](#verification)
- [Related Skills](#related-skills)

The default operating rule for every canonical member, every shared team, and every debate participant: **use prepared context artifacts before reading raw source files**.

This file is the single source of truth for the rule. Member definitions in `agents/claude/` and `agents/codex/` should reference this file rather than duplicating it, and `shared-context-pattern.md` is a pointer stub back to here.

## Fresh Context Principle

Every subagent receives a **self-contained brief**. This is an orchestration input contract, not a claim about what the runtime also loads.

- The brief contains the task, relevant plan section, file ownership, and required interface contracts; avoid adding a lead-transcript dump. A runtime-selected fresh, forked, or memory-augmented start may add other context.
- A smaller task packet preserves more usable capacity and can reduce irrelevant history, but available context and quality effects must be observed on the selected runtime.
- Orchestration state (task graph, progress, decisions, dependency outputs) lives in durable files, not only in the lead's memory, so any new lead session can resume by reading those files.
- The safest cross-platform abstraction is not "shared live team memory" but a parent/orchestrator that hands each worker a small, durable context packet.
- Shared background: [../../agents-swarm-orchestration/SKILL.md](../../agents-swarm-orchestration/SKILL.md) and [../../ai-agents/references/context-rotation-and-state.md](../../ai-agents/references/context-rotation-and-state.md).

## The Rule

Engineering work on existing repos must follow this order:

1. **Read prepared context first** — `docs/`, profiles, graphs, query outputs, ADRs, runbooks, decision logs
2. **Read specific source files only to confirm or extend the artifacts** — never to rediscover what the artifacts already capture
3. **Fall back to broad repo discovery only when artifacts are missing or stale** — and say so explicitly in the output

This is a load-bearing briefing discipline. It controls what the orchestrator sends; runtime startup and memory behavior remain separate, explicit settings.

## Preferred Context Inputs

Check for these in order. Stop at the first level that has what you need.

### Level 1: Task-Local Context

- Task brief or acceptance criteria from the parent thread or lead
- Decision log from a prior debate (when wired in by the orchestrator)
- Ownership assignment naming the files this worker may touch
- Interface contracts the worker must respect

### Level 2: Repo-Native Context

From `dev-context-engineering`:
- `AGENTS.md` / `CLAUDE.md` at repo root — hot instructions and operating rules
- `docs/` — compiled markdown hub: architecture notes, ADRs, migration plans, runbooks
- Repo-native context model (hot instructions → compiled hub → cold evidence)

### Level 3: Generated Repo Artifacts

From `dev-context-code-graph`:
- `code-profiles/<repo>.json` — file/function inventory, hotspots, ownership
- `graphs/code-graph.json` — caller/callee relationships, blast radius
- `reports/code-graph-validation.json` — graph health
- `reports/query-*.md` — pre-computed answers to common questions ("who calls X?", "what does Y depend on?")

### Level 4: Portfolio-Level Context

From `dev-context-multi-repo`:
- `profiles/*.json` — per-repo profiles (stack, owners, interfaces)
- `catalog/*.md` — human-readable repo summaries
- `graphs/system-edges.json` — cross-repo relationships
- `graphs/knowledge-graph.json` — domain entities and bindings
- `reports/coverage.md` — what's profiled vs not

### Level 5: Source Files

Only after Levels 1-4 are exhausted, read specific source files. Even then:
- Read only the files the artifacts identified as relevant
- Never rediscover the entire codebase
- If you find yourself reading 10+ files just to "understand the layout," stop and report missing context instead

## When Artifacts Are Missing or Stale

Do not silently fall back to full repo discovery. Instead:

1. **Report the gap** in the output: "no `code-profiles/<repo>.json` for this repo, falling back to direct file reads"
2. **Bound the discovery** to what the task requires — never scan the whole repo
3. **Recommend context preparation** for the next run: "suggest running `dev-portfolio-mapper` and `dev-code-graph-builder` before the next session to make this faster"
4. **Trust the lead** if it explicitly says "artifacts are stale, do a fresh read" — then proceed with focused discovery

## When the Brief Itself Is Unclear: Ask Before Assuming

Context-first does not just mean "read prepared files first." It also means "surface questions BEFORE going into independent rounds."

If after reading the provided context any of these are true:

- The scope is ambiguous (could mean two different things)
- A constraint is missing (you'd have to assume something load-bearing)
- The success metric is unclear (multiple metrics point in different directions)
- Your interpretation might differ from another team member's
- A required input is referenced but not provided
- You could approach the task two valid ways and don't know which the user prefers

**Ask the lead in ONE batch BEFORE starting analysis.** Do not silently assume and proceed.

**Your questions are a steering signal, not a failure.** When you say "I don't know exactly what to do," that gives the user a chance to redirect the work before tokens are spent. A user who sees "here are 4 things the team is uncertain about" gets to navigate; a user who sees a finished but misaligned analysis has to react and pay for a redo. Steering is cheaper than reacting.

This connects to the [Round 0 Clarification Pass](../../../../agents/templates/debate-orchestrator.md#round-0-clarification-pass-optional-for-high-stakes-runs) in the orchestrator. The cost of one clarification batch is ~2 turns. The cost of 5 members each interpreting an ambiguous brief differently is a full misaligned debate.

Submit questions in this format:
```
SCOPE: <ambiguity 1>
CONSTRAINT: <missing constraint>
SUCCESS METRIC: <conflicting metrics>
ASSUMPTION CHECK: <load-bearing assumption to confirm>
MISSING INPUT: <referenced but not provided>
```

After the lead answers, restate your understanding in one line before beginning analysis. This makes any remaining gap visible to the lead before tokens are committed to the wrong question.

## Discovery Rule (Authoritative)

> Engineering teams should not reread the whole codebase by default.
> Broad repo discovery is reserved for context-preparation roles such as `dev-portfolio-mapper`, `dev-repo-context-curator`, and `dev-code-graph-builder`, or for workers that are explicitly told the artifacts are missing or stale.

This rule applies to every member in `agents/claude/` and `agents/codex/`, every repository team recipe in `agents/teams/`, and every debate participant invoked through the orchestrator.

## Member Workflow Template

Every canonical member's `## Workflow` section should start with this step:

```markdown
1. Read provided context artifacts in order:
   task brief → docs/ → graphs/profiles → owned files.
   See [agents-subagents/references/context-first-protocol.md](context-first-protocol.md).
   Do not rediscover the repo when prepared context covers the task.
```

The remaining workflow steps focus on the member's specialized lens.

## Team Recipe Template

Every team recipe should include `required_context` and `optional_context` fields:

```yaml
required_context:
  - <minimum input the team cannot run without — task brief, spec, diff, etc.>
optional_context:
  - docs/**/*.md
  - profiles/*.json
  - graphs/code-graph.json
  - reports/query-*.md
  - <other generated artifacts that improve the result if present>
```

The orchestrator passes both lists into each member's task brief. Members read what's available; missing optional context is fine but should be noted.

## Debate Orchestrator Handoff

When the orchestrator spawns perspective agents, the brief MUST include:

```text
PROVIDED CONTEXT:
  - <list of artifact paths actually present>
MISSING CONTEXT:
  - <artifacts that would help but aren't present>

INSTRUCTION: Read the provided context first. Do not perform broad repo discovery
unless the brief explicitly says the artifacts are stale.
```

This prevents perspective agents from each independently rereading the whole repo, which is the most common token-waste failure mode in debate teams.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|--------------|--------------|-----|
| Member starts with `find . -type f -name "*.ts"` | Rereads the entire repo, wastes context | Read `code-profiles/<repo>.json` first |
| 5 perspective agents each read the same files | 5x token cost, no added insight | Lead pre-reads once, passes context to all members |
| Falling back to discovery without reporting the gap | Hides the cost, prevents context preparation next time | Always report missing artifacts in the output |
| Treating "artifacts are stale" as a default assumption | Defeats the whole context-engineering pipeline | Trust artifacts unless explicitly told otherwise |
| Reading every file in `src/` to "understand the structure" | Replaces graph traversal with brute force | Use `graphs/code-graph.json` for structure, source files for confirmation |
| Custom file reads when a `reports/query-*.md` already answers the question | Duplicates pre-computed work | Check `reports/` for relevant queries first |

## Verification

A team or member is following the context-first protocol if:
- ✅ The output cites which context artifacts were used
- ✅ The number of source file reads is bounded (typically <10 for a focused task)
- ✅ Missing artifacts are reported, not silently worked around
- ✅ Broad repo scans only happen in context-preparation roles
- ✅ Multi-member teams share context inputs instead of each rediscovering them

## Related Skills

- [../../dev-context-engineering/SKILL.md](../../dev-context-engineering/SKILL.md) — repo-native context model (the source of `docs/`, `AGENTS.md`)
- [../../dev-context-code-graph/SKILL.md](../../dev-context-code-graph/SKILL.md) — per-repo code graphs and query reports
- [../../dev-context-multi-repo/SKILL.md](../../dev-context-multi-repo/SKILL.md) — portfolio-level profiles and catalogs
- [../../ai-context-layer/SKILL.md](../../ai-context-layer/SKILL.md) — application context layer for retrieval and grounding
