---
description: Cybernetics and VSM decision rules for multi-agent systems: autonomy within output contracts, coordination on shared targets, calibrated algedonic escalation, variety checks before adding agents, and recursion boundaries.
last_verified: 2026-09-24
status: stable
---

# Cybernetics and VSM Applied to Multi-Agent Systems

> **Gate before invoking:** Check [`foundations-cybernetics-vsm` § When to Apply](../../foundations-cybernetics-vsm/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

S1–S5, Ashby's law, variety engineering and algedonic channels are covered in the foundation. In team terms, the subagents are S1, the file-ownership or debate protocol is S2, the orchestrator is S3, routing is S4, and the repository rules and permissions are S5. This file keeps only the rules that change a team design.

## Decision rules

1. **Give subagents autonomy within a contract; don't approve every call.** Each subagent gets a tool allow-list, file ownership and a required-fields output contract. If the orchestrator approves individual tool calls, it has collapsed into the worker role (S3 into S1): its context fills with approvals and the fan-out gains nothing. Check that summaries are accurate with occasional full-trace audits, not constant supervision.
2. **Put a coordinator on every shared target before running concurrent writers.** That means one write owner per file, or a sequencing rule for a shared synthesis document. The coordinator sequences and flags conflicts. Once it starts commanding members, it has become a second orchestrator.
3. **Design the escalation (algedonic) channel to bypass the summary path, and calibrate it.** Triggers are irreversible actions outside a worker's ownership, writes to a production or security boundary, spend beyond a set multiple of the estimate (start at 3×), and all workers stalled at once. Implement them as `PreToolUse`/`PostToolUse` hooks or an orchestrator check, never inside the worker. Timeouts and 429s belong in the retry path. If the channel fires more than about twice per session, the threshold is too low. If a critical event was absorbed into a summary, it is too high.
4. **Before adding an agent, name the task type nobody on the team currently handles.** If you can't, the team is short on absorption, not variety. Run the [response-coverage audit](../../foundations-cybernetics-vsm/references/response-coverage-audit.md) to check this rather than restating Ashby's bound here. Then shrink what comes back to the orchestrator (tighter output contracts, a summary subagent) instead of adding a specialist. A starting trigger: add a summary layer when expected summaries exceed about 40% of the parent's remaining context.
5. **Respect recursion boundaries.** A parent orchestrator does not choose files for a sub-orchestrator's workers, and a sub-orchestrator does not reopen budgets or team composition that the parent set. Add a nesting level only if it reduces the variety the upper level has to handle.

## Worked recipe — role map and escalation register at launch

```text
System in focus: <team>, serving as one S1 unit of <parent session>
S5 policy        repo rules + agent disallowedTools, wired into each worker's prompt/frontmatter
S4 routing       task classification before dispatch (is any task type unhandled?)
S3 orchestrator  dispatch, synthesis, output-contract field check
S2 coordination  file-ownership matrix; debate round order; judge flags CONFLICT_UNRESOLVED
S1 workers       bounded tasks inside their allow-list

Escalation register:
T1 write outside ownership / unapproved prod endpoint → PreToolUse block + operator notice
T2 spend > 3× estimate in one wave → pause spawns, surface cost breakdown
T3 output blocked by repo policy → PostToolUse block + full trace
T4 ≥80% of workers CONVERGENCE_STALLED together → halt, surface full state
```

Test each hook on a controlled red-flag input before relying on it. After an escalation fires, review the cause, not the agent, and retune the threshold or the output contract.

## Related

- [control-theory-applied.md](control-theory-applied.md): breakers and stall detection that feed T4.
- [agents-hooks](../../agents-hooks/SKILL.md): hook mechanics.
- Primary sources: Beer, *Brain of the Firm* (1972); Ashby, *An Introduction to Cybernetics* (1956), both cited in the foundation.
