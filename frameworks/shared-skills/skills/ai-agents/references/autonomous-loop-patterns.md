# Autonomous Loop Patterns

Use this reference when designing **Shape C — Autonomous Loop**: a long-running process that repeatedly invokes an agent against a fixed goal until acceptance criteria are met, the budget is exhausted, or a circuit breaker fires.

Canonical example: Ralph Loop (37h / 250 tasks from a 2000-line PRD). Closely related: Devin-style background agents, BMAD-v6 replayable runs, agent-driven migrations, overnight refactors, continuous research crawls.

This is the deployment shape with the **highest blast radius** and the **least supervision**. Treat every guardrail here as load-bearing, not optional.

## Table of Contents

- [When to Use This Shape](#when-to-use-this-shape)
- [Anatomy of an Autonomous Loop](#anatomy-of-an-autonomous-loop)
- [The PRD (Loop Specification)](#the-prd-loop-specification)
- [Loop Driver — Three Implementations](#loop-driver--three-implementations)
- [Termination Criteria](#termination-criteria)
- [Budget and Iteration Caps](#budget-and-iteration-caps)
- [Checkpointing and Restart](#checkpointing-and-restart)
- [Drift Detection Mid-Loop](#drift-detection-mid-loop)
- [Circuit Breakers](#circuit-breakers)
- [Fail-Loud Wiring](#fail-loud-wiring)
- [Observability](#observability)
- [Operational Checklist](#operational-checklist)
- [Common Failure Modes](#common-failure-modes)
- [Cross-References](#cross-references)

## When to Use This Shape

Use an autonomous loop when **all** of the following hold:

- The work is decomposable into steps the agent can finish without human input.
- Acceptance criteria are concrete enough to be machine-checked (tests pass, all rows migrated, all docs indexed, all PRs merged with green CI).
- The cost of one wasted iteration is small enough that a few wasted iterations are tolerable.
- A budget cap and circuit breaker can stop the loop before it burns runaway cost.

Do **not** use this shape when:

- "Done" is a judgment call only a human can make.
- Each step is irreversible (sending money, posting to social, deleting production data) — those belong in [Shape A](../../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md) with explicit approval gates.
- The work touches multi-stakeholder coordination.
- You cannot articulate the termination criterion in one sentence.

## Anatomy of an Autonomous Loop

```text
              ┌─────────────────────────┐
              │  PRD / loop spec (file) │
              └────────────┬────────────┘
                           │ read each iter
                           ▼
┌──────────────────────────────────────────────────────┐
│                  Loop Driver                         │
│                                                      │
│   for iter in 1..max_iters:                          │
│      1. read PRD + checkpoint                        │
│      2. invoke agent with fresh context              │
│      3. capture output + token/cost/duration         │
│      4. run acceptance check                         │
│      5. run drift check                              │
│      6. write checkpoint                             │
│      7. evaluate stop conditions                     │
│                                                      │
└──────────┬─────────────────────────┬─────────────────┘
           │                         │
           ▼                         ▼
   ┌───────────────┐         ┌──────────────────┐
   │  Checkpoint   │         │  Circuit Breaker │
   │  Store (disk) │         │  (budget, drift, │
   │               │         │   error rate)    │
   └───────────────┘         └──────────────────┘
           │                         │
           ▼                         ▼
   ┌──────────────────────────────────────────┐
   │  Observability: events, traces, metrics  │
   │  Alerts: budget breach, repeated failure │
   └──────────────────────────────────────────┘
```

Five components, all required: PRD, driver, checkpoint store, circuit breaker, observability.

## The PRD (Loop Specification)

The PRD is the **only** durable instruction the loop reads. Every iteration starts with a fresh agent context that re-reads it. Treat it like a contract.

Minimum fields:

```yaml
---
goal: "Migrate all 312 legacy invoices to the v2 schema with zero data loss."
acceptance_criteria:
  - "SELECT COUNT(*) FROM invoices_v2 = SELECT COUNT(*) FROM invoices_legacy"
  - "All rows in invoices_v2 pass schema_check_v2.sql with 0 violations"
  - "Reconciliation report shows 0 drift after 24h soak"
budget:
  max_iterations: 50
  max_tokens_total: 8_000_000
  max_cost_usd: 200
  max_wall_clock_hours: 12
out_of_scope:
  - "Do not touch invoices_legacy table — read only."
  - "Do not modify the v2 schema definition."
escalation:
  on_repeated_failure: "Stop after 3 consecutive iterations with no progress."
  human_contact: "ops-oncall@example.com"
---

## Context
[longer prose context, links, examples]

## Definition of Progress
[what counts as "made progress this iteration" — used for the drift check]
```

Two non-obvious rules:

1. **The PRD must be re-readable from scratch every iteration.** No "see previous run". A fresh agent must understand the goal cold.
2. **Acceptance criteria must be machine-checkable.** If you cannot write a script that returns true/false, you do not have acceptance criteria — you have a wish.

## Loop Driver — Three Implementations

Pick one based on your operational substrate.

### Driver A — Plain Python (`while` loop)

Lowest-ceremony, no infrastructure dependency. Good for: single-machine runs, prototyping, work that completes in < 24h.

```python
import json, time, sys
from pathlib import Path
from anthropic import Anthropic

PRD = Path("loop.prd.md").read_text()
CHECKPOINT = Path("checkpoint.json")
client = Anthropic()

def load_checkpoint() -> dict:
    if CHECKPOINT.exists():
        return json.loads(CHECKPOINT.read_text())
    return {"iter": 0, "tokens": 0, "cost_usd": 0.0, "history": []}

def save_checkpoint(state: dict) -> None:
    CHECKPOINT.write_text(json.dumps(state, indent=2))

def acceptance_check() -> tuple[bool, str]:
    # Run your concrete check here. Return (passed, message).
    # Example: subprocess.run(["./check_acceptance.sh"]) returncode == 0
    raise NotImplementedError("Define your acceptance check")

def run_iteration(state: dict) -> dict:
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        system=PRD,
        messages=[{"role": "user", "content": f"Iteration {state['iter']+1}. Make progress toward the goal. Report what you changed."}],
    )
    text = response.content[0].text
    state["iter"] += 1
    state["tokens"] += response.usage.input_tokens + response.usage.output_tokens
    state["history"].append({"iter": state["iter"], "summary": text[:500]})
    return state

def main():
    state = load_checkpoint()
    config = parse_prd_frontmatter(PRD)  # implement
    no_progress_streak = 0

    while True:
        if state["iter"] >= config["max_iterations"]:
            return halt("iteration cap")
        if state["tokens"] >= config["max_tokens_total"]:
            return halt("token cap")
        if state["cost_usd"] >= config["max_cost_usd"]:
            return halt("cost cap")

        state = run_iteration(state)
        save_checkpoint(state)

        passed, msg = acceptance_check()
        if passed:
            return halt(f"acceptance met: {msg}")

        if not made_progress(state):  # implement against "Definition of Progress"
            no_progress_streak += 1
            if no_progress_streak >= 3:
                return halt("no progress for 3 iterations")
        else:
            no_progress_streak = 0

def halt(reason: str):
    print(f"HALT: {reason}", file=sys.stderr)
    # Send to observability + alert if reason is not "acceptance met"
    sys.exit(0 if reason.startswith("acceptance") else 1)

if __name__ == "__main__":
    main()
```

Run under `systemd`, `tmux`, or a container with restart policy `on-failure`. Crash-safe by design: checkpoint is read on every restart.

### Driver B — Temporal workflow

Use when: you need exactly-once activity semantics, durable retries, multi-day runs, or you already operate Temporal.

```python
# workflow.py
from datetime import timedelta
from temporalio import workflow

@workflow.defn
class AutonomousAgentLoop:
    @workflow.run
    async def run(self, prd_path: str) -> str:
        config = await workflow.execute_activity(load_prd, prd_path, start_to_close_timeout=timedelta(minutes=1))
        state = await workflow.execute_activity(load_checkpoint, prd_path, start_to_close_timeout=timedelta(minutes=1))
        no_progress = 0

        while state["iter"] < config["max_iterations"]:
            if state["cost_usd"] >= config["max_cost_usd"]:
                return "halt:cost_cap"

            iter_result = await workflow.execute_activity(
                run_agent_iteration, args=[prd_path, state],
                start_to_close_timeout=timedelta(minutes=30),
                retry_policy=workflow.RetryPolicy(maximum_attempts=2),
            )
            state = iter_result["state"]
            await workflow.execute_activity(save_checkpoint, args=[prd_path, state], start_to_close_timeout=timedelta(minutes=1))

            acceptance = await workflow.execute_activity(check_acceptance, prd_path, start_to_close_timeout=timedelta(minutes=5))
            if acceptance["passed"]:
                return f"halt:acceptance:{acceptance['msg']}"

            if iter_result["made_progress"]:
                no_progress = 0
            else:
                no_progress += 1
                if no_progress >= 3:
                    return "halt:no_progress"

        return "halt:iter_cap"
```

Key Temporal benefits: workflow history replays on worker restart (no checkpoint file needed), activity timeouts catch hung agent calls, retry policies isolate transient failures.

### Driver C — LangGraph cyclic graph

Use when: the loop has branching decisions per iteration, you already use LangGraph for bots, or you want built-in checkpoint integration.

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver

class LoopState(TypedDict):
    iter: int
    tokens: int
    cost_usd: float
    history: list
    last_output: str
    no_progress_streak: int

def run_iteration_node(state: LoopState) -> LoopState:
    # call agent, update state
    ...

def check_acceptance_node(state: LoopState) -> LoopState:
    ...

def decide_next(state: LoopState) -> str:
    if state["cost_usd"] >= MAX_COST or state["iter"] >= MAX_ITERS:
        return "halt"
    if state.get("acceptance_passed"):
        return "halt"
    if state["no_progress_streak"] >= 3:
        return "halt"
    return "iterate"

graph = StateGraph(LoopState)
graph.add_node("iterate", run_iteration_node)
graph.add_node("check", check_acceptance_node)
graph.add_node("halt", lambda s: s)
graph.set_entry_point("iterate")
graph.add_edge("iterate", "check")
graph.add_conditional_edges("check", decide_next, {"iterate": "iterate", "halt": END})

checkpointer = PostgresSaver.from_conn_string(DATABASE_URL)
app = graph.compile(checkpointer=checkpointer)
```

LangGraph's PostgresSaver gives you checkpointing for free, plus integrates with the bot patterns in [`../../ai-bot-builder/references/graph-design-patterns.md`](../../ai-bot-builder/references/graph-design-patterns.md).

## Termination Criteria

A loop must have at least one of each:

| Type | Example | Purpose |
|---|---|---|
| **Goal-met** | acceptance script returns 0 | The happy path |
| **Bound** | `iter >= max_iterations` | Prevent infinite loop |
| **Cost** | `cost_usd >= max_cost_usd` | Prevent runaway spend |
| **Stagnation** | 3 iterations with no progress | Prevent thrashing |
| **Drift** | acceptance metric regressed by >X% | Prevent corruption |
| **External** | sigterm / kill-switch file present | Allow human halt |

Missing any one of these is a known failure mode. The Ralph Loop original lacked explicit stagnation detection — users reported runs that "kept going" without making progress.

## Budget and Iteration Caps

Budgets are non-negotiable. The Coding Behavior Rule 6 ("token budgets are not advisory") was written for this shape.

Recommended defaults (tune to your work):

| Scope | Default | Notes |
|---|---|---|
| Per-iteration tokens | 50k–200k | Cap input + output |
| Per-iteration wall clock | 30 min | Use as activity timeout |
| Total iterations | 50 | Multiply if loop is known-long |
| Total tokens | 8M | Hard cap on the whole run |
| Total cost USD | $200 | Cross-check against token cost |
| Wall clock | 12h | Forces operator review at next day |

**Budget breach must be loud.** Wire it to PagerDuty / Slack / email, not just stderr. See [`budget-and-loop-hooks.md`](../../agents-hooks/references/budget-and-loop-hooks.md).

## Checkpointing and Restart

Every iteration writes a checkpoint **before** running the next one. The checkpoint is the only durable state — assume the process can die at any line.

What to checkpoint:

- iteration number
- cumulative tokens / cost
- history of iteration summaries (truncated)
- last agent output (full)
- acceptance check result and timestamp
- no-progress streak counter

Where:

- Driver A (plain Python): file on disk, atomic rename (`os.replace`)
- Driver B (Temporal): workflow history (automatic)
- Driver C (LangGraph): `PostgresSaver` or `SqliteSaver`

Restart contract: a restart from checkpoint must produce identical behavior to the iteration that would have run had the process not crashed. Test this explicitly with a kill-9 during iteration 5 and verify the loop resumes correctly.

## Drift Detection Mid-Loop

The loop can technically progress while making the underlying state worse. Detect this with a metric that should monotonically improve.

Examples:

- migration loop: rows-remaining should never increase
- test-fixing loop: failing tests should never increase
- doc-indexing loop: unindexed-doc count should never increase

```python
def check_drift(state: LoopState) -> bool:
    history = state["history"][-5:]
    if len(history) < 5:
        return False
    metrics = [h["primary_metric"] for h in history]
    # If the last 5 iterations show the metric getting worse, drift detected
    return metrics[-1] > metrics[0] * 1.1  # 10% regression tolerance
```

On drift detection: halt, alert, and require human approval before resuming.

## Circuit Breakers

A circuit breaker is a hard stop independent of the loop's normal stop conditions. Implement at least two:

1. **Error-rate breaker.** If 5 of the last 10 iterations errored, halt.
2. **Provider-error breaker.** If the LLM provider returns 5xx for 3 consecutive iterations, halt and back off.
3. **External kill-switch.** Check for a file like `LOOP_KILL` or a Redis key at the start of every iteration. If present, halt immediately and persist the reason.

```python
def kill_switch_active() -> bool:
    return Path("/var/run/agent-loop/KILL").exists()

# Inside loop:
if kill_switch_active():
    halt("external kill switch")
```

A kill-switch the operator can flip from their phone is mandatory for any loop that runs over 1 hour unsupervised.

## Fail-Loud Wiring

Coding Behavior Rule 12: silent success is the most expensive failure mode.

Every halt reason must produce a structured event:

```json
{
  "event": "loop_halt",
  "loop_id": "invoice-migration-2026-05-20",
  "reason": "no_progress",
  "iter": 17,
  "tokens_used": 3_400_000,
  "cost_usd": 84.50,
  "acceptance_passed": false,
  "last_summary": "Could not resolve schema mismatch on row 4521..."
}
```

Send to: stdout (for `tail -f`), observability backend, alert channel.

**Never** halt silently. Never halt with `exit(0)` if acceptance was not met.

## Observability

Minimum signals to emit per iteration:

| Signal | Type | Purpose |
|---|---|---|
| `iter_started` | event | timeline reconstruction |
| `iter_completed` | event | with duration, tokens, cost |
| `acceptance_check` | event | passed/failed + message |
| `progress_metric` | metric | for drift detection |
| `cumulative_cost_usd` | metric | for budget dashboards |
| `iter_count` | metric | for SLO tracking |

Send to Langfuse / Phoenix / OpenLLMetry. See [`evaluation-and-observability.md`](evaluation-and-observability.md) for the May 2026 platform comparison.

Dashboard must show: iterations vs time, cumulative cost vs budget, progress metric trend, halt reasons over recent runs.

## Operational Checklist

Before running an autonomous loop in production:

- [ ] PRD has machine-checkable acceptance criteria
- [ ] Budgets set (iterations, tokens, cost, wall clock)
- [ ] Checkpoint store tested with kill-9 restart
- [ ] Stagnation detector configured (default: 3 iterations)
- [ ] Drift detector configured (or explicit decision to skip with rationale)
- [ ] Kill-switch path documented and tested
- [ ] Alerts routed to a human who is on-call now
- [ ] Halt events flow to observability
- [ ] Dry-run completed against a non-production target
- [ ] Rollback plan exists for partial-progress state
- [ ] Out-of-scope list explicit in PRD
- [ ] Runbook entry written: how to inspect, halt, resume, post-mortem

## Common Failure Modes

| Failure | Symptom | Mitigation |
|---|---|---|
| **Runaway cost** | Bill arrives, loop still running | Cost cap + budget hook |
| **Silent stagnation** | Iterations complete but no progress | Stagnation detector |
| **Drift** | Acceptance metric regresses | Drift detector + monotonic-metric check |
| **Restart loop** | Process crashes, restarts, repeats same work | Atomic checkpoint write + restart smoke test |
| **Provider outage** | Hangs forever on LLM call | Per-iteration timeout |
| **Half-applied state** | Crashes mid-iteration, world is inconsistent | Idempotent agent actions or transaction-scoped iterations |
| **Goal drift** | Agent reinterprets PRD across iterations | PRD pinned in `system`, not in user-turn history |
| **Halt with `exit(0)`** | Pipeline thinks it succeeded | Exit non-zero on any non-acceptance halt |

## Cross-References

- [`agent-delivery-methods.md`](agent-delivery-methods.md) — Ralph Loop row + BMAD/GSD comparison
- [`agent-operations-best-practices.md`](agent-operations-best-practices.md) — general production guidance
- [`evaluation-and-observability.md`](evaluation-and-observability.md) — telemetry platforms
- [`guardrails-implementation.md`](guardrails-implementation.md) — input/output guardrails
- [`deployment-ci-cd-and-safety.md`](deployment-ci-cd-and-safety.md) — release patterns
- [`24-7-operating-model.md`](24-7-operating-model.md) — SLOs and oncall for the loop in production
- [`../../agents-hooks/references/budget-and-loop-hooks.md`](../../agents-hooks/references/budget-and-loop-hooks.md) — hook-based budget enforcement
- [`../../agents-memory/SKILL.md`](../../agents-memory/SKILL.md) — durable state between runs
- [`../../software-workflow-automation/references/durable-execution.md`](../../software-workflow-automation/references/durable-execution.md) — Temporal/Inngest substrate
- [`../../qa-agent-testing/SKILL.md`](../../qa-agent-testing/SKILL.md) — acceptance check construction
