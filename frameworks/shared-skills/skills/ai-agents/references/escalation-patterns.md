# Escalation Patterns for Agent Failures

> Operational reference for designing structured escalation hierarchies in agent systems — when to retry, re-plan, escalate to a parent agent, or hand off to a human. Covers failure classification, escalation budgets, and integration with hooks and orchestration.

---

## Table of Contents

- [Core Principle: Escalation Over Retry](#core-principle-escalation-over-retry)
- [3-Level Escalation Hierarchy](#3-level-escalation-hierarchy)
- [Failure Classification](#failure-classification)
- [Escalation Decision Tree](#escalation-decision-tree)
- [Escalation Budgets](#escalation-budgets)
- [Integration with Hooks](#integration-with-hooks)
- [Graceful Degradation Modes](#graceful-degradation-modes)
- [Anti-Patterns](#anti-patterns)
- [Related Resources](#related-resources)

---

## Core Principle: Escalation Over Retry

The default instinct when an agent task fails is to retry. The better default is to **classify the failure first**, then decide.

**Transient failures** (network timeouts, rate limits, tool unavailability) → retry once with backoff.

**Structural failures** (wrong tool, ambiguous requirements, missing permissions, logic errors) → do not retry the same approach. Re-plan or escalate.

**Safety failures** (policy violation, unauthorized action, data exfiltration attempt) → never retry. Abort and escalate to human immediately.

Retrying a structural failure wastes context and can leave the agent in a loop. Retrying a safety failure is a security risk.

---

## 3-Level Escalation Hierarchy

```
Level 1: Self-resolution
  Agent detects failure → re-plans with different approach → attempts once more
  Budget: 1 re-plan, 1 retry
  Escalate when: same failure recurs or re-plan produces no new approach

Level 2: Parent agent / lead agent escalation
  Worker signals failure with diagnosis → lead decides: reassign, re-scope, unblock, or absorb
  Budget: lead gets 1 attempt to unblock
  Escalate when: lead cannot unblock without human judgment or authority

Level 3: Human escalation
  System pauses, emits structured escalation record → human reviews and resolves
  Triggers: safety constraint, irreversible operation, ambiguous authority, compliance gate
  Never retry after Level 3 until human resolution is confirmed
```

In single-agent systems without a parent agent, Level 2 becomes a local re-plan with a broadened strategy before escalating to human.

---

## Failure Classification

| Failure Type | Example | Escalation Level |
|---|---|---|
| Transient network / rate limit | Timeout, 429 | Level 1 (retry once) |
| Tool unavailable | MCP server down | Level 1 (retry with backoff) |
| Tool argument error | Schema mismatch, missing field | Level 1 (re-plan tool call) |
| Ambiguous requirements | Spec has two conflicting interpretations | Level 2 (lead resolves) |
| Missing permissions | File write denied, API key missing | Level 2 (lead unblocks) |
| Structural logic error | Same approach fails twice | Level 2 (reassign or re-scope) |
| Policy violation | Agent attempts unauthorized action | Level 3 (human review) |
| Irreversible operation | Destructive write, send email, deploy | Level 3 (human approval before proceed) |
| Safety constraint | Prompt injection, secret exfiltration | Level 3 (abort and audit) |
| Compliance gate | Regulated action requiring audit trail | Level 3 (human sign-off) |

---

## Escalation Decision Tree

```text
Task execution failed?
  → Classify failure type
    → Transient?
        → Retry once with backoff
        → Still failing? → treat as structural
    → Structural?
        → Re-plan with different approach
        → Retry once
        → Still failing? → Escalate to Level 2
    → Safety / compliance?
        → Abort immediately → Escalate to Level 3 → Do not retry
  → At Level 2?
    → Lead diagnoses: can unblock?
        → Yes → unblock and resume
        → No → Escalate to Level 3
  → At Level 3?
    → Emit escalation record with: failure type, context, last attempted approach, required resolution
    → Pause execution
    → Resume only after human confirmation
```

---

## Escalation Budgets

Define budgets explicitly in the task contract before dispatch. Agents that exceed budget must escalate rather than continue.

```yaml
escalation_budget:
  max_retries_per_tool_call: 1          # transient failures
  max_replans_before_level2: 1          # structural failures
  max_level2_attempts: 1                # lead unblocking
  max_context_tokens_before_stop: 80000 # abort if context exhausted
  safety_violations_before_abort: 1     # zero tolerance
```

Budget exhaustion is itself an escalation trigger. An agent that has used its entire retry budget without success must escalate, not continue silently.

---

## Integration with Hooks

Use Claude Code hooks to enforce escalation at the runtime level:

**`PostToolUseFailure`** — inspect the failure type and emit a structured escalation record if the failure is non-transient:
```json
{
  "failure_type": "permission_denied",
  "tool": "Write",
  "resource": "/etc/hosts",
  "escalation_level": 3,
  "message": "Write to protected path. Human approval required."
}
```

**`PermissionRequest`** — use to gate Level 3 escalations. Block the operation and route the `PermissionRequest` event to the human approval channel before proceeding.

**`Stop`** — validate that the agent did not stop due to a budget exhaustion without emitting an escalation record. Require a final escalation summary in the stop payload if any failures occurred.

See [../../agents-hooks/SKILL.md](../../agents-hooks/SKILL.md) for hook configuration patterns.

---

## Graceful Degradation Modes

When full escalation is not possible (no parent agent, async human review), fall back gracefully rather than silently:

| Mode | When to Use | Behavior |
|---|---|---|
| **Partial result** | Structural failure on optional step | Return completed steps; clearly mark incomplete sections |
| **Cached result** | Tool unavailable, transient outage | Return last valid result with staleness timestamp |
| **Degraded mode** | Missing capability | Acknowledge limitation; offer reduced-scope alternative |
| **Hard abort** | Safety / policy failure | Return structured error; do not return partial unsafe output |

Never return a result that silently omits a failure. The caller must be able to detect that escalation or degradation occurred.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Retry loop on structural failure | Wastes context, loops indefinitely | Classify before retrying; escalate structural failures |
| Silent degradation | Caller assumes success | Always flag degraded or incomplete results explicitly |
| Escalating transient failures immediately | Unnecessary interruption | Retry transient failures once before escalating |
| Undefined escalation path | Agent has no one to escalate to | Define escalation chain in task contract before dispatch |
| Escalating without diagnosis | Human receives unhelpful ticket | Always include: failure type, last attempted approach, and what resolution is needed |
| Resuming after Level 3 without confirmation | Safety risk | Require explicit human confirmation before resuming after any Level 3 event |

---

## Related Resources

- [../../agents-hooks/SKILL.md](../../agents-hooks/SKILL.md) — PostToolUseFailure, PermissionRequest, Stop hooks
- [../../agents-swarm-orchestration/SKILL.md](../../agents-swarm-orchestration/SKILL.md) — Lead agent escalation responsibilities and escalation-over-retry pattern
- [guardrails-implementation.md](guardrails-implementation.md) — HITL escalation triggers and confidence thresholds
- [agent-operations-best-practices.md](agent-operations-best-practices.md) — Error handling and loop continuation decision trees
- [deployment-ci-cd-and-safety.md](deployment-ci-cd-and-safety.md) — Rollback and control gates
