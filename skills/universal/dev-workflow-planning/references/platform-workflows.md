# Platform Workflows

Native workflow mapping for Claude Code, Codex, and generic assistants. Use this file when a user asks for planning help and the answer should match the platform's current documented surfaces rather than invented commands.

---
## Table of Contents

- [Core Rule](#core-rule)
- [Claude Code](#claude-code)
- [Best Fit](#best-fit)
- [Native Surfaces](#native-surfaces)
- [Recommended Flow](#recommended-flow)
- [Avoid](#avoid)
- [Codex](#codex)
- [Best Fit](#best-fit)
- [Native Surfaces](#native-surfaces)
- [Recommended Flow](#recommended-flow)
- [Avoid](#avoid)
- [Generic Assistant Fallback](#generic-assistant-fallback)
- [Choosing an Execution Model](#choosing-an-execution-model)
- [Durable Artifact Rules](#durable-artifact-rules)
- [Review and Closure](#review-and-closure)


## Core Rule

Treat `brainstorm`, `plan`, `execute`, and `review` as conceptual phases.

Do not invent slash commands such as `/brainstorm` or `/execute-plan` unless the platform really provides them.

---

## Claude Code

### Best Fit

- local repo work
- human + agent collaboration in the same checkout
- bounded delegation to subagents
- worktree-based isolation when multiple actors work concurrently

### Native Surfaces

| Need | Native surface |
|------|----------------|
| Review a plan before edits | Plan mode: check the [current commands](https://code.claude.com/docs/en/commands) and [permission behavior](https://code.claude.com/docs/en/permissions) before giving entry-point instructions |
| Repo rules and memory | `CLAUDE.md`, repo docs, project memory |
| Delegation | subagents |
| Concurrent local work | worktrees |
| Long-running sessions | checkpoints in a durable plan doc or task tracker |

### Recommended Flow

1. Use plan mode when an ambiguous or risky change benefits from review before edits. Check the [command reference](https://code.claude.com/docs/en/commands) before invoking a named command.
2. Produce a decision-complete plan with success criteria and verification.
3. If the work can be split cleanly, spawn bounded subagents with file ownership.
4. Use worktrees when the human and one or more agents will edit the repo in parallel.
5. Merge or hand off only after acceptance criteria and repo quality gates pass.

### Avoid

- spawning parallel writers before contracts are stable
- treating chat history as the source of truth instead of durable repo artifacts
- assuming a worktree is required for every single-task session

---

## Codex

### Best Fit

- long-horizon implementation work with durable repo instructions
- cloud execution with isolated sandboxes
- structured plans that may span sessions or multiple agents
- review and handoff through Codex app surfaces

### Native Surfaces

| Need | Native surface |
|------|----------------|
| Repo-wide instructions | `AGENTS.md` |
| Durable execution plan | `PLANS.md` or existing repo plan doc |
| Domain guidance | Skills |
| Read-only planning | Plan mode (`/plan`) |
| Parallel work | multi-agent workflows for bounded, independent tasks |
| Review | app review pane |
| Handoff worktree | app worktrees when comparing or landing changes locally |

### Recommended Flow

1. Put general repo behavior in `AGENTS.md`.
2. Store durable execution steps in `PLANS.md` if the work spans sessions or multiple agents.
3. Use skills for specialized patterns instead of duplicating long instructions in the task prompt.
4. Keep multi-agent use bounded: split only by stable interfaces and non-overlapping files.
5. Use app review and worktrees for reconciliation and landing, not as the primary isolation mechanism for cloud execution.

### Avoid

- parallel tasks that share mutable files or still-changing interfaces
- relying on chat-only plans for long-running work
- assuming local git worktrees are required for Codex cloud isolation

---

## Generic Assistant Fallback

When no platform-native surface exists:

1. Write the plan in Markdown inside the conversation or an existing repo doc.
2. Use explicit headings: goal, scope, steps, verification, risks, next action.
3. Run sequentially unless the user explicitly asks for parallel execution and the tasks are clearly independent.
4. Preserve continuity in an existing issue, PR description, ADR, or plan file.

---

## Choosing an Execution Model

```text
Can the task be done safely by one worker?
├── YES -> stay sequential
└── NO
    ├── Are interfaces already stable?
    │   ├── NO -> finish planning first
    │   └── YES
    ├── Do tasks own different files?
    │   ├── NO -> stay sequential
    │   └── YES -> run wave-based parallel execution
```

Use speculative "all at once" parallelism only for prototypes, throwaway scaffolding, or explicit time-critical demos.

---

## Durable Artifact Rules

- Prefer existing repo artifacts over new scratch files.
- For Codex, default to `AGENTS.md` for instructions and `PLANS.md` for execution state.
- For Claude Code, prefer the repo's existing memory and planning documents.
- For both, checkpoints belong in a durable artifact, not only in chat history.

---

## Review and Closure

Every workflow should end with:

- changed scope
- evidence collected
- checks run
- remaining risk
- exact next bounded step

If the platform offers a review surface, use it before final handoff.
