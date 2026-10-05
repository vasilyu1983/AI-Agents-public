---
description: Queueing-theory decision rules for agent orchestration: fan-out wave sizing by the slowest worker, concurrency caps from a wait target, and when to stop adding agents.
last_verified: 2026-09-24
status: stable
---

# Queueing Theory Applied to Agent Orchestration

> **Gate before invoking:** Check [`foundations-queueing-theory` § When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

The formulas (Little's Law, Erlang-C, Kingman, fork-join, USL, priority queues) live in the foundation's templates. This file keeps only the rules that change an orchestrator's fan-out and concurrency choices.

## Decision rules

1. **Size a wave by its slowest worker, not the mean.** A wave of K parallel subagents finishes at `max(S₁…S_K)`. Only for i.i.d. exponential durations is `E[max] = E[S]·H_K` (H₄ ≈ 2.08, H₈ ≈ 2.72). For other distributions, estimate `E[max]` by resampling K durations from prior runs. If the SLO is on a tail, work backwards: a wave p90 needs each worker at its `0.9^(1/K)` quantile (≈ p97.4 for K=4, ≈ p98.7 for K=8). Do not multiply by `(1 + CV²/2)`. That factor is the Pollaczek–Khinchine M/G/1 *waiting-time* correction and says nothing about the maximum of K service times. See [fork-join](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md).
2. **Cap concurrency at the tightest of three limits:** the context the parent can absorb (`usable_context / summary_tokens`, keeping a synthesis reserve), what the runtime or provider allows (look it up in current runtime docs; don't hard-code it), and a queue-wait target. For the wait target, use Erlang-C wait probability and mean wait. A utilisation target alone is not enough: at small c, ρ ≈ 0.67 still means about 44% of spawns wait.
3. **Separate classes that differ by an order of magnitude in duration.** A mixed batch finishes when its slowest class finishes. Run fast readers first and feed their output to the slow analysts.
4. **Give a high-priority class (e.g. writes) a utilisation cap** so it cannot starve the low-priority class: non-preemptive low-priority wait diverges as ρ₁ → 1. Estimate retry cost with the Kingman heavy-traffic approximation `Wq ≈ ρ/(1−ρ)·(CV²ₐ+CV²ₛ)/2·E[S]`. If one retry's wait exceeds the retry budget, open the circuit breaker rather than retrying.
5. **Stop adding agents when measured throughput stops rising.** Fit USL `X(N)=N/(1+σ(N−1)+κN(N−1))` to at least three measured team sizes and check the fit reproduces the measurements before trusting `N_max = √((1−σ)/κ)`.

## Worked recipe — concurrency cap and wave size

Inputs: spawn rate λ = 2/min, mean subagent duration 1 min (μ = 1/min, offered load a = 2), wait target ≤ 10 s. Prior-run durations: mean 45 s, CV² ≈ 2. Wave SLO 180 s at the mean.

```text
Erlang-C, a = 2:   c=3  P(wait)=0.444  Wq=26.7 s   → fails 10 s target
                   c=4  P(wait)=0.174  Wq= 5.2 s   → passes
                   c=5  P(wait)=0.060  Wq= 1.2 s
c_max = min(c_context, c_runtime, 4)

Wave (lognormal fit to the prior runs, 40k resamples):
                   K=3  E[max]≈ 88 s   K=4 ≈ 102 s   K=8 ≈ 144 s   → all ≤ 180 s
Exponential assumption (45·H_K) would give 82.5 / 93.8 / 122.3 s.
K = min(K_SLO, c_max) = 4; run the remaining items as a second wave.
```

USL check on measured throughput 1.0 / 1.8 / 2.6 / 2.3 tasks·min⁻¹ at N = 1/2/4/8: least squares gives σ ≈ 0.01, κ ≈ 0.043, `N_max ≈ 4.8`, and reproduces all four points. Cap the team at 4. A fit that gives `N_max` near 10 on the same data is wrong; check it by predicting X(8).

Recompute `c_context` before each wave, because the parent's context drains.

## Related

- [control-theory-applied.md](control-theory-applied.md): semaphore admission, backoff and circuit breakers that enforce these caps.
- [theory-of-constraints-applied.md](theory-of-constraints-applied.md): the dispatch policy that sits on top of these capacity numbers.
- [mast-failure-taxonomy.md](mast-failure-taxonomy.md): the failure categories. MAST does not classify sizing errors.
- Primary sources: Little (1961); Erlang (1917); Kingman (1961); Nelson & Tantawi (1988); Gunther (2007), all cited in the foundation.
