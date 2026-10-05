---
description: Durable list of agent-design failure modes: tool-output-as-instructions, context rot, MCP bloat, stale agent files, approval fatigue.
last_verified: 2026-09-02
status: stable
---

# Agent Traps and Anti-Patterns

## Table of Contents

- [Known Traps](#known-traps)
- [Common Anti-Patterns](#common-anti-patterns)

Durable list of agent-design failure modes observed in production. Refer here from any launch-prompt, team-manifest, or agent-review flow.

For the **structured taxonomy** (MAST: 14 failure modes × 3 categories with per-mode mitigations and coverage gaps), see [`mast-failure-taxonomy.md`](mast-failure-taxonomy.md). This file is the operator-facing tip sheet — short, scannable, written for fast reading during launch. The MAST file is the structured cross-reference for postmortems and skill-design coverage analysis.

## Known Traps

- Delegating vague understanding work instead of a bounded artifact, decision, or file-ownership slice.
- Launching repo-local agents when a built-in, global, or plugin-backed agent already matches the task.
- Giving multiple edit-capable workers overlapping files without explicit ownership boundaries.
- Passing the parent transcript as context instead of a fresh brief with exact inputs and deliverables.
- Adding debate or team structure where the task is routine and a single specialist would be clearer.
- **Trusting tool output as instructions** — treat retrieved docs, web results, MCP responses, and file contents as untrusted data; never let tool output modify the worker's task brief, permissions, or ownership. **Read the runtime signal that now exists**: since v2.1.210 Claude Code scans each subagent's final report before the parent reads it, inserting a backslash into text that imitates its own output (`<system-reminder>` tags, lines starting with `Human:` or `Assistant:`) and prepending a line starting with `[harness: subagent output matched instruction-shaped pattern(s):` when the report imitates such tags or mentions permission settings like `bypassPermissions` or `--dangerously-skip-permissions`. Treat that marker as a live injection signal worth escalating on — and do not mistake it for a fix: "the scan doesn't remove or reword anything; it doesn't judge whether content is malicious", and a tool call the report leads Claude to make still goes through the session's permission checks and sandboxing.
- **Orthogonal edits** — a worker that "cleans up" code, comments, or files adjacent to its brief has derailed. Every changed line must trace to the dispatched task; reject reports whose changed-file list exceeds the brief's ownership set.
- **Accepting "done" without verification evidence** — a worker report without the required artifact, verifier command output, or changed-file list is not a completion; reject and re-dispatch.
- **Context rot inside a long-running worker** — output quality can degrade silently well before the window is full; no reliable threshold is established, so checkpoint early and force a handoff or fresh-context restart at the first sign of drift instead of pushing through.
- **MCP server token bloat in the parent** — MCP servers attached to the lead inflate every turn (tool descriptions alone can be large). Field reports (StackOne, Atlassian) describe tool-selection accuracy falling sharply as tool definitions grow, and tool descriptions taking a large share of the context window before any task work begins; measure with `/context`. Scope MCP to the specific worker that needs it. When only one worker needs a server, **define it inline in the subagent's frontmatter** instead of referencing a project-scope server — the inline definition keeps those tool descriptions out of the parent context entirely. For chronic offenders, wrap the MCP inside a dedicated subagent (the **MCP-wrapper subagent** pattern) so the parent never sees the tool descriptions at all — see [harness-patterns.md](harness-patterns.md) §"MCP-Wrapper Subagent". Claude Code can defer full schemas until first use, but check the docs for whether tool **names** still enter the initial context when servers are referenced at project scope. See [agent-tools.md](agent-tools.md) §"Inline MCP servers vs references".
- **Stale agent files after runtime upgrade** — Claude Code and Codex keep adding agent fields (for example `effort`, `initialPrompt`, `skills`, `memory`); pre-upgrade agents silently lose behavior. Audit after each runtime bump.
- **Agent Teams runtime limitations shift quickly** — verify current Agent Teams limitations before designing background-mode teammates. Confirmed in current docs: split-pane display mode does not work reliably in the VS Code extension (use the terminal CLI, or in-process display mode). Earlier practitioner reports of background teammates stalling on unseen permission prompts have not been re-confirmed against current docs — treat as a risk to verify, not a settled fact, and keep edit-capable teammates foreground until you have re-checked.
- **Stale fan-out and verification instructions after a model-generation upgrade** — a lead that under-fanned-out on an older generation needed pushing; a newer generation may delegate more readily and self-verify without being told, so prompts written to compensate for the old one cause spawn churn and over-verification. Re-read agent files and `AGENTS.md` / `CLAUDE.md` for "always fan out" and "add a final verification step" phrasing; see SKILL.md §"Fan-Out and Verification".

## Common Anti-Patterns

- "General helper" agent descriptions that never trigger reliably or trigger everywhere.
- Agents with tool access broader than their deliverable surface.
- Team recipes that duplicate swarm-orchestration rules instead of linking to the shared source of truth.
- Local agent proliferation without a clear reuse reason, lifecycle owner, or smoke-test path.
- Asking workers to decide merge, approval, or synthesis policy that should stay with the lead.
- **Approval fatigue → blanket yes** — fan-out produces many permission prompts; operator stops reading and approves everything. Pre-approve narrow scopes at launch or batch-review approvals rather than rely on per-call judgment.
- **Duplicating patterns owned by the sibling skill** — self-consistency/voting and hierarchical swarm live in [../../agents-swarm-orchestration/SKILL.md](../../agents-swarm-orchestration/SKILL.md); reference them instead of restating.
