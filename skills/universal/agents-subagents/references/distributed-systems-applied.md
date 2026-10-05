---
description: Distributed-systems decision rules for multi-agent orchestration: checkpoint before fan-out, idempotency keys, fencing at the mutation receiver, logical ordering, and bounded panel votes that never prove truth.
last_verified: 2026-09-24
status: stable
---

# Distributed Systems Applied to Multi-Agent Orchestration

> **Gate before invoking:** Check [`foundations-distributed-systems` § When to Apply](../../foundations-distributed-systems/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

Distributed protocols only earn their cost when agents run concurrently and pass messages to each other. A single-process sequential workflow doesn't need them. Raft, Paxos, FLP, CAP, CRDTs, vector clocks and broadcast are covered in the foundation. This file keeps the agent-specific rules.

## Decision rules

1. **Checkpoint the plan before fan-out.** Persist the plan ID and version, the disjoint ownership map, dependencies and acceptance criteria before dispatching. Reading the checkpoint back confirms it is visible. It does not prove durability, and it is never consensus. Use Raft or Paxos only for a real replicated state machine.
2. **Every side-effecting call carries an idempotency key:** `stable_hash(tenant, logical_operation_id)`, which stays the same across retries and reassignment. The receiver claims the key atomically and stores a payload hash and a state. A second request with the same key but a different payload is a conflict, not a replay. If a tool cannot accept a key, **don't retry it automatically**: return `PARTIAL_FAILURE` to the orchestrator. A timeout is an unknown outcome, so reconcile before re-sending.
3. **Enforce fencing tokens at the receiver that applies the mutation.** It atomically rejects any holder or epoch older than the current one, before the effect happens, and advances the epoch before the replacement worker gets its grant. An in-context lock registry is only cooperative ownership. Without receiver enforcement, use disjoint ownership or serialize writes through one narrow tool.
4. **Order by logical dependencies, never by wall clock.** Tag each output with `(writer, seq)` and the identities it depended on. Before merging, the synthesizer checks that every declared dependency is present, not merely that some version exists. If one is missing, the result is incomplete and gets escalated.
5. **A panel vote is advisory evidence, not proof of truth or a storage quorum.** Three of five LLM judges agreeing proves neither that the answer is true nor that the state is linearizable. Their errors are correlated, and there is no replicated log. Before dispatch, state the panel size N, the agreement threshold W, the evidence checks, the deadline and who owns escalation. A vote never authorizes execution.
6. **Put a deadline on each debate round; never require unanimity.** Set the round timeout from measured p99 agent latency. Count non-responders as missing evidence, but keep N as the original authorized panel size. This is a workflow rule. It proves nothing about consensus (FLP concerns formal asynchronous agreement).

## Worked recipe — bounded panel verdict

```python
N = len(authorized_judges)            # never shrink on timeout
W = N // 2 + 1                        # illustrative threshold; justify per task
responses = collect(authorized_judges, timeout=3 * p99_latency)
counts = count_verdicts(responses, one_vote_per_authorized_judge=True)
winners = [v for v, c in counts.items() if c >= W]
if len(winners) == 1:
    record(verdict=winners[0], N=N, W=W, counts=counts,
           missing=missing(authorized_judges, responses), dissent=dissents(responses))
else:
    escalate("DEBATE_STALLED", counts=counts, partial=responses)  # tie, split or too few
```

Merging contributions: give each record the identity `(task, writer, seq)` and treat its payload as immutable. An identical replay is ignored. A record with the same identity but a different payload fails closed. For a cumulative snapshot, take the writer's highest seq; for append-only findings, take the union. The executable checks are in `scripts/test_contribution_contracts.py` (approve/approve/reject panels, duplicate votes, reordered snapshots, payload collisions, missing dependencies).

## Related

- [control-theory-applied.md](control-theory-applied.md): risk-class retry policy.
- Primary sources: Fischer, Lynch & Paterson (1985); Lamport (1978); Kleppmann (2017), ch. 11; Gray & Cheriton (1989), all cited in the foundation.
