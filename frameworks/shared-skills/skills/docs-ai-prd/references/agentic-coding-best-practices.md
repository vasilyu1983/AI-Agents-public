# Agentic Coding Best Practices

Purpose: operational patterns for coding-agent workflows that need to survive tool changes and documentation churn.

Last verified: 2026-03-13

## Table of Contents

- [Durable Principles](#durable-principles)
- [Context Surfaces By Tool](#context-surfaces-by-tool)
- [Recommended Workflow](#recommended-workflow)
- [1. Plan](#1-plan)
- [2. Recon](#2-recon)
- [3. Implement In Increments](#3-implement-in-increments)
- [4. Validate](#4-validate)
- [5. Handoff](#5-handoff)
- [Patterns That Age Well](#patterns-that-age-well)
- [Decision-First Docs](#decision-first-docs)
- [Progressive Disclosure](#progressive-disclosure)
- [Approval Boundaries](#approval-boundaries)
- [Eval-Driven Iteration](#eval-driven-iteration)
- [Common Mistakes](#common-mistakes)
- [Quick Review Checklist](#quick-review-checklist)

## Durable Principles

1. Project memory is a routing layer, not a dumping ground.
2. Canonical docs beat duplicated summaries.
3. Small, validated increments beat large autonomous runs.
4. Approval boundaries must be explicit before the agent acts.
5. Evals and acceptance criteria must be defined before broad rollout.

## Context Surfaces By Tool

Use the official vendor docs in `data/sources.json` to verify details before final answers.

| Tool | Shared context | Tool-specific context |
|------|----------------|-----------------------|
| Claude Code | `CLAUDE.md` or linked docs | `.claude/agents/`, `.claude/skills/`, `.claude/hooks/` |
| GitHub Copilot | `AGENTS.md` where supported | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.github/agents/`, `.github/skills/` |
| Cursor | `AGENTS.md` | `.cursor/rules/`, optional root `CLAUDE.md`, CLI approvals |

Rule:
- Keep shared repo facts in one place.
- Use tool-specific files only for behavior that is not portable.

## Recommended Workflow

### 1. Plan

Use a planning step when:
- the change spans multiple files
- requirements are ambiguous
- rollout, migration, or security decisions matter
- the task will likely cross multiple sessions

Output:
- objective
- non-goals
- acceptance criteria
- risks
- validation plan

### 2. Recon

Before editing:
- inspect the current implementation
- map the affected code, tests, and docs
- identify dependencies and approvals
- confirm which context files are canonical

### 3. Implement In Increments

Work in small batches:
- one logical subsystem at a time
- verify after each batch
- update the plan or handoff notes when reality changes

### 4. Validate

Validation should include:
- automated checks
- acceptance criteria review
- security review for risky areas
- behavior-focused self-review

### 5. Handoff

Record:
- changed behavior
- validation performed
- residual risks
- follow-up tasks or open questions

## Patterns That Age Well

### Decision-First Docs

For PRDs, specs, and project memory:
- separate final decisions from open questions
- label transition states explicitly
- attach owners and end conditions to temporary exceptions

### Progressive Disclosure

In context files and skills:
- keep the top layer short
- link to deeper docs for details
- load only the parts needed for the task

### Approval Boundaries

Document which actions require human approval:
- destructive commands
- production writes
- migrations
- external side effects
- tool calls that can spend money or alter customer data

### Eval-Driven Iteration

For AI features:
- define the eval objective before tuning prompts or routing
- track offline, human, and online evaluation separately
- use rollback triggers, not just success targets

## Common Mistakes

Avoid:
- assuming `AGENTS.md` is universal across tools
- duplicating the same context in three files
- publishing vendor-specific claims without a verification date
- asking reasoning models to expose chain-of-thought as a default pattern
- treating generated code as correct because tests passed once

Prefer:
- one canonical source per fact
- tool-specific overlays
- source-backed, date-stamped external claims
- concise rationale instead of hidden reasoning dumps
- repeated validation during rollout

## Quick Review Checklist

- [ ] Shared context is canonical and small
- [ ] Tool-specific files only carry tool-specific behavior
- [ ] Acceptance criteria are explicit
- [ ] Approval boundaries are documented
- [ ] External claims are source-backed and current
- [ ] Handoff notes describe behavior, validation, and risks
