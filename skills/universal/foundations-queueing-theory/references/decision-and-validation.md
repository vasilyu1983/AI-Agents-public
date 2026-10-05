# Capacity and scheduling decision worksheet

## Intake and output

Record arrival population/rate and temporal dependence, paired service traces, server heterogeneity, queue discipline, buffer limits, abandonments/retries, batching, held resources and latency SLO. Report exact vs approximate baseline, assumption violations, workload-specific headroom, validation window, alternatives and omitted mechanisms. Mean utilization does not establish queue or tail safety.

## Select a model

- M/M/c: Poisson input, iid exponential service, homogeneous servers and waiting.
- Erlang-B: loss on busy; do not borrow it for waiting or abandonment.
- M/G/1: Poisson arrivals, finite service moments. Kingman: renewal arrivals and approximate single-server waiting; autocorrelation needs trace validation.
- Finite buffers and abandonment: identify loss/timeout population before computing throughput, waits and Little's Law. Measure admitted/completed/lost work separately; do not silently use infinite-buffer Erlang-C.
- Batch arrivals M[X]/M/1 differ from bulk service; record batch formation and state-dependent capacity explicitly.

## Checkable examples

Little's Law: 100/s with mean .2s gives mean inflight20; median .05s cannot replace the mean.

Ideal preemptive-resume M/G/1, high λ=.2,E[S]=1,E[S²]=2 and low λ=.2,E[S]=2,E[S²]=8: high Wq=.25s. Nonpreemptive high Wq=1.25s. A batch job with 3s remaining followed by two queued high 1s jobs makes the second high wait4s; priority is not a hard wait bound.

Two iid unit-mean exponential branches have expected maximum1.5; two deterministic unit branches have maximum1. Loaded worker queues and correlations need joint response-time modeling.

## Replay boundary

Use the existing FCFS runner only for its documented fixed-server, unbounded-buffer, initially-empty finite trace. Preserve observed arrival/service pairing and temporal dependence. Measurement-window integrals and all-job drained summaries have different populations. The runner cannot assess finite-buffer drops, abandonment, priorities or changing capacity. Choose a validated richer model before such mechanisms drive capacity commitments; general simulation skill expansion is deferred.

Primary scheduling reference: [Harchol-Balter's author book page](https://www.cs.cmu.edu/~harchol/PerformanceModeling/book.html). See the bundled trace-driven-simulation reference for executable usage and interpretation.
