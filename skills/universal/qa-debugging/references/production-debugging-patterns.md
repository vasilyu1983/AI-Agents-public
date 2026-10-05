# Production Debugging Patterns

Hypothesis-driven debugging when the failure lives in production: what to do first, what
destroys evidence, and how to add observation without causing a second incident. Incident
command, severity levels, communications, and postmortems are owned by
`../../ops-incident-response/SKILL.md`. Telemetry setup is owned by
`../../qa-observability/SKILL.md`.

> **No hypothesis and no reproduction?** Use the hypothesis-free core analysis loop in
> [../../qa-observability/references/core-analysis-loop.md](../../qa-observability/references/core-analysis-loop.md)
> to localize the problem, then return here.

## Contents

- [Order of Operations](#order-of-operations)
- [Evidence That a Restart Destroys](#evidence-that-a-restart-destroys)
- [Adding Observation Safely](#adding-observation-safely)
- [Read-Only Data Investigation](#read-only-data-investigation)
- [Verifying a Production Fix](#verifying-a-production-fix)

---

## Order of Operations

1. **Is impact ongoing?** If yes, mitigate first (rollback, flag off, shed load, fail over) and
   investigate in parallel. Do not hold mitigation hostage to a root cause.
2. **Before mitigating, spend a bounded minute capturing evidence** that mitigation will
   destroy (next section). If capture would extend user harm materially, skip it and say so in
   the incident record.
3. **Enumerate every change in the window**: deploys across all services involved, flag flips,
   config pushes, schema migrations, dependency or certificate expiries, autoscaling events,
   traffic mix changes, cron jobs. The newest deploy is the most salient candidate and often not
   the cause (SKILL.md Cognitive Traps; `causal-inference-applied.md` A2/A3).
4. **Pick the rollback target by evidence, not recency.** Rolling back the wrong change costs a
   deploy cycle and removes a variable you might need.
5. Investigate with existing telemetry (traces, logs filtered by ID, metrics, continuous
   profiles) before adding anything new.

## Evidence That a Restart Destroys

A restart, redeploy, or pod eviction resets connection pools, caches, heap, thread state, and
local files. Once done, a stateful bug may not recur for days.

| Symptom | Capture first | How (see `systems-debugging-tools.md`) |
|---------|---------------|-----------------------------------------|
| Hang or stuck requests | All-thread stacks | `py-spy dump`, `jcmd Thread.print`, `gdb -p ... thread apply all bt`, Go pprof goroutine endpoint |
| Memory growth | Heap snapshot or dump (check snapshot memory cost first) | `memory-leak-detection.md` |
| Crash loop | Core dump, last logs of the previous container (`kubectl logs --previous`) | Core-dump workflow |
| Wrong data | The bad records, their audit history, the request IDs that wrote them | Read-only query, export |
| Latency | A profile and a few slow-request traces from the bad state | Continuous profiler, trace search by duration |

Take one replica out of rotation instead of restarting all of them when possible: users get
relief, and you keep a live specimen of the bad state.

## Adding Observation Safely

- Scope extra logging or tracing to the affected tenant, user, or endpoint with a feature flag,
  and give it an expiry. Global debug logging at production volume can itself cause latency,
  cost, and disk-full incidents.
- Redact secrets and PII in anything added; debug-level logs are where tokens and request
  bodies leak.
- Prefer attach-and-detach tools (profilers, BPF, stack dumps) over redeploying with more
  logging: they do not restart the process and do not need a deploy approval cycle.
- Interactive debugging in production (breakpoints, REPL against production, live edits) is a
  last resort: it needs explicit approval and a rollback plan, and a breakpoint on a request
  path stalls real users.
- A canary deploy of a candidate fix is an experiment: define in advance which metric must
  return to baseline on the canary, compared against the non-canary fleet over the same window,
  before widening.

## Read-Only Data Investigation

- Query a read replica by default, but remember **replicas lag**: a record missing on the
  replica may exist on the primary. When the question is about the newest writes, check the
  replica's lag first.
- Heavy analytical queries on a replica can themselves increase replication lag or be
  cancelled by conflicts with replication. Bound them (`LIMIT`, time window, `EXPLAIN` first).
- Export the minimal failing records to reproduce locally, with PII masked, instead of
  debugging logic against live data.
- Data repairs go through a reviewed, idempotent script with a backup and a dry-run count, never
  an ad-hoc `UPDATE` in a console.

## Verifying a Production Fix

- Compare the regressed metric before and after on the same traffic slice and time-of-day
  window; a fix deployed during a traffic trough looks good for the wrong reason.
- Symptom remission after a restart or rollback is consistent with, not proof of, the
  hypothesis. State the mechanism, or label the root cause `probable` (SKILL.md evidence bar).
- Remove temporary flags and debug instrumentation, and record their removal.
