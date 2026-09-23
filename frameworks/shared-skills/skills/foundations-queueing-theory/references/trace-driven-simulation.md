---
description: Input, output, and interpretation contract for the finite-trace FCFS queue simulator.
last_verified: 2026-09-08
status: stable
---

# Trace-Driven FCFS Simulation

Use the simulator when empirical burstiness, service-time variation, or a finite backlog makes the closed-form models too restrictive. Use the formulas for a quick baseline when their arrival, service, and steady-state assumptions are adequate.

## Model and input

The runner models an initially empty, unbounded, nonpreemptive FCFS queue with a fixed number of identical servers. The UTF-8 CSV requires `arrival_time` and `service_time`; `job_id` is optional. Times must be finite and nonnegative, arrivals must be in nondecreasing order, and service time may be zero. Derived completion times and reported aggregates must also remain finite; rescale the time unit or shorten the horizon if floating-point arithmetic would overflow. Simultaneous arrivals retain CSV row order. Each row stays intact, so an observed arrival and its service time are never independently reshuffled.

A server completing at time `t` is available to an arrival at `t`. When several servers are free, the earliest release wins, then the lowest zero-based server ID. These rules make ties reproducible.

## Command and worked example

From the skill directory:

```bash
python3 scripts/queue_trace_simulator.py \
  --input data/example-fcfs-trace.csv \
  --servers 1
```

The example starts jobs at times 0, 3, and 5. Waiting times are 0, 2, and 3; response times are 3, 4, and 4. The default measurement interval is the first arrival through the last completion, `[0, 6]`. Busy time is 6, capacity time is `1 server * 6 time units`, utilization is 1, the queue-time integral is 5, and the maximum waiting backlog is 2.

Use `--measurement-start` and `--measurement-end` when utilization must use an externally defined observation window. Busy time and queue time are clipped to that window. Utilization is `clipped busy time / (servers * window duration)`. A zero-duration window has `null` utilization because its denominator is zero. End-state backlog uses post-event, half-open interval semantics: a completion at the window end is finished, while a job starting there is in service only when its service time is positive.

## Output interpretation

The JSON reports the model and tie policy, measurement interval and integrals, waiting/in-service/unfinished counts at the interval end, empirical waiting/response summaries, the maximum waiting queue over the full trace, and per-job assignments. Waiting and response summaries cover every trace job after the queue drains, even when a custom utilization window ends earlier. Quantiles use type-7 linear interpolation. `--summary-only` omits job rows; `--output PATH` writes the JSON to a file.

This is a finite-horizon replay of one trace from an empty initial state. It has no warm-up deletion, stochastic replications, or confidence interval. Do not label its quantiles or utilization as steady-state estimates. For population uncertainty, collect representative traces or define and validate a stochastic input model, seeds, warm-up, run length, independent replications, and diagnostics before drawing confidence intervals. NIST's [modeling and simulation guidance](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=910389) is the primary verification and validation reference used for that escalation boundary.

The runner does not model finite buffers, abandonment, retries, priorities, changing capacity, heterogeneous servers, preemption, or shared-resource coupling. Extend and test the event model when those mechanisms can change the decision; otherwise report them as omitted assumptions.
