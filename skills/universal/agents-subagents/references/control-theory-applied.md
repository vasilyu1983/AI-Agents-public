---
description: Control-theory decision rules for multi-agent loops: capped backoff, semaphore fan-out admission, per-tool circuit breakers, stall-based termination with capability escalation, and risk-class concurrency.
last_verified: 2026-09-24
status: stable
---

# Control Theory Applied to Multi-Agent Loops

> **Gate before invoking:** Check [`foundations-control-theory` § When to Apply](../../foundations-control-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

PID, Lyapunov, observability, gain scheduling, anti-windup and the token bucket are explained in the foundation's templates. This file keeps only the rules that change how an orchestrator retries, admits, stops and escalates.

## Decision rules

1. **Cap the whole delay, jitter included:** `delay = min(cap, base·2^k + jitter)`. Jitter added after the cap can push the delay past it. Example: base 2 s, k = 6, cap 60 s, jitter 9 s gives 60 s. Bound total attempts and elapsed retry time too, and follow any server retry guidance.
2. **Completion-released slots are a semaphore, not a token bucket.** Acquire a slot before spawning. Release it exactly once, on completion, cancellation or a failed launch. Use a separate time-refilled token bucket only to limit launch or retry *rate*. Take the cap from measured downstream capacity, file-ownership conflicts and the parent's context reserve, never from the number of items.
3. **Put one circuit breaker on each tool.** While it is open, fail fast into a per-tool fallback (cache, skip, or yield to the parent), and don't count those steps as lack of progress, because an outage is a disturbance, not a stall. Starting thresholds, to tune against the tool's real failure pattern: 3 failures or 40% in a 60 s window, 20 s open, then 1 probe.
4. **Termination = acceptance check + stall counter + absolute budget.** A failing-test count is a heuristic, not a Lyapunov function, and zero failing tests does not mean the acceptance contract is met. Stop with `CONVERGENCE_STALLED` after M non-improving steps (start at M = 3; raise it for long steps). A stall is an escalation, never a success.
5. **In a review-fix loop, escalate capability at the cap instead of trying again.** Rounds 1–3 use the same implementer. Rounds 4–5 use a fresh, more capable implementer. At the cap, the controller puts every open finding into exactly one bucket: reviewer-wrong, real-but-not-load-bearing, or real-and-load-bearing (stop and escalate to a human). Each finding gets a ledger entry, and nothing is silently dropped. (Pattern: obra/superpowers `44c9b2d`, `skills/subagent-driven-development/SKILL.md`, MIT.)
6. **Set concurrency and retries by tool risk class.** Read-only work gets high concurrency and retries. Writes to disjoint owned files get moderate concurrency. Writes to shared state get serial or worktree-isolated execution and **no automatic retry**: yield to the parent, because the write may have partly applied. Drain in-flight readers before the first writer starts.

## Worked recipe — per-tool retry wrapper

```python
def call_with_policy(tool, args, cls, base=1.0, cap=60.0, jitter_max=1.0, max_attempts=5):
    breaker = breakers[tool.name]                     # rule 3
    if cls == WRITE_SHARED:                           # rule 6: no auto-retry
        r = breaker.call(tool, *args)
        return r if r.ok else yield_to_parent("non-idempotent write failed", r)
    for k in range(max_attempts):
        r = breaker.call(tool, *args)
        if r.ok:
            return r
        if r.status == TOOL_UNAVAILABLE:              # breaker open: fall back now
            return FALLBACKS[tool.name](args)
        sleep(min(cap, base * 2**k + uniform(0, jitter_max)))   # rule 1
    return FALLBACKS[tool.name](args)
```

The parent needs specific state from each subagent's return. Implementers report files changed, tests run with pass/fail, and errors. Researchers report sources, open questions and confidence. Reviewers report findings with file:line and severity. Tool callers report the breaker state. Check these fields after each wave before dispatching the next, or the loop is running open-loop.

## Related

- [queueing-theory-applied.md](queueing-theory-applied.md): how large the caps above should be.
- [distributed-systems-applied.md](distributed-systems-applied.md): idempotency keys and fencing for writes that must be retried.
- Primary sources: Åström & Murray, *Feedback Systems* (2020); Nygard, *Release It!* (2018); Hellerstein et al. (2004), all cited in the foundation.
