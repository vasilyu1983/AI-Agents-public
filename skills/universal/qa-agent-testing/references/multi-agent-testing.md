# Multi-Agent Testing

Coordination testing patterns for systems with multiple collaborating agents.

## Contents

- [Why It Differs](#why-it-differs)
- [Core Failure Modes](#core-failure-modes)
- [Recommended Checks](#recommended-checks)
- [Metrics](#metrics)
- [Template](#template)

## Why It Differs

Multi-agent systems add failure modes beyond single-agent quality:

- Handoff loss
- Contradictory sub-goals
- Shared-state drift
- Retry storms
- Approval confusion across agents
- Tool side effects triggered by the wrong agent

Prefer qualitative topology guidance unless you have strong, direct evidence for numeric claims in your own system.

## Core Failure Modes

### 1. Handoff failures

One agent omits or distorts key context before the next agent acts.

### 2. State divergence

Agents operate on stale or inconsistent state.

### 3. Role drift

Agents stop following their intended responsibilities.

### 4. Cascading tool errors

One bad tool call propagates through the workflow.

### 5. Approval-boundary confusion

One agent assumes another agent already obtained approval.

## Recommended Checks

### Pairwise handoff tests

Test each important handoff in isolation before testing the full workflow.

### Fault injection

Inject:

- Delayed messages
- Missing messages
- Corrupted shared state
- Tool failures
- Approval denials

### Semantic-preserving mutation

If a workflow solves the original request, it should usually solve equivalent restatements unless the wording changes intent.

### Trace review

Verify:

- Which agent chose which tool
- Which agent obtained approval
- Which messages were authoritative
- Which side effects were triggered

## Metrics

Use a small, practical set:

| Metric | What It Measures |
|---|---|
| Handoff success rate | Required context arrives intact |
| Shared-state consistency | Agents act on the same facts |
| Role adherence | Agents stay inside their responsibilities |
| Recovery quality | System degrades safely under faults |
| Tool side-effect containment | One agent cannot trigger unsafe side effects silently |

## Template

```markdown
## Multi-Agent Test Suite

### System Under Test
- Agents: [list]
- Topology: [orchestrator / hierarchical / mesh / mixed]
- Shared state: [none / memory / DB / tool outputs]
- Approval model: [centralized / per-agent / hybrid]

### Handoff Checks
| From | To | Scenario | Expected | Pass |
|---|---|---|---|---|
| Planner | Worker | ... | ... | PASS/FAIL |

### Fault Injection
| Fault | Expected Recovery | Pass |
|---|---|---|
| Tool timeout | Retry or safe failure | PASS/FAIL |
| Approval denied | No silent side effect | PASS/FAIL |

### State Consistency
| Scenario | Expected | Pass |
|---|---|---|
| Shared memory update | All agents read same state | PASS/FAIL |

### Summary
| Metric | Result | Pass |
|---|---|---|
| Handoff success rate | ... | PASS/FAIL |
| Recovery quality | ... | PASS/FAIL |
```

## Related

- [SKILL.md](../SKILL.md) - main skill overview
- [tool-sandboxing.md](tool-sandboxing.md) - isolation and approval checks
- [regression-protocol.md](regression-protocol.md) - rerun policy
