# Resilience and HA for LLM Serving

Serving-specific high-availability rules: what changes when the replica is a GPU model server with a large cold start, a KV cache, and token-proportional cost. Generic patterns live with their owners:

| Need | Owner |
|---|---|
| Circuit breakers, retries, timeouts, hedging | [qa-resilience](../../qa-resilience/SKILL.md): `circuit-breaker-patterns.md`, `retry-patterns.md`, `timeout-policies.md`, `deadlines-hedging.md` |
| Liveness / readiness / startup probe design | [qa-resilience](../../qa-resilience/SKILL.md): `health-check-patterns.md` |
| Queue caps, load shedding, priority shedding, backpressure, graceful degradation mechanics | [qa-resilience](../../qa-resilience/SKILL.md): `load-shedding-backpressure.md`, `graceful-degradation.md` |
| Multi-region active-active / active-passive, failover, DR tests | [ai-mlops](../../ai-mlops/SKILL.md) `multi-region-patterns.md`; [qa-resilience](../../qa-resilience/SKILL.md) `disaster-recovery-testing.md` |
| Canary, blue-green, shadow, traffic split, rollback procedure, CI deploy gates | [ai-mlops](../../ai-mlops/SKILL.md) `deployment-lifecycle.md`; SLO specs in qa-resilience `slo-as-code.md` |
| Availability math, error budgets, redundancy, FMEA | [reliability-theory-applied.md](reliability-theory-applied.md) |

## Contents

- [1. Health and Readiness of a Model Server](#1-health-and-readiness-of-a-model-server)
- [2. Cold Start and Warmup](#2-cold-start-and-warmup)
- [3. Autoscaling Signals](#3-autoscaling-signals)
- [4. Token-Aware Overload Protection](#4-token-aware-overload-protection)
- [5. Stateful Asset Coordination](#5-stateful-asset-coordination)
- [6. LLM-Specific Rollout Gates](#6-llm-specific-rollout-gates)
- [Checklist](#checklist)

---

## 1. Health and Readiness of a Model Server

- Weight loading takes minutes on large models. Use a **startup probe** (or a long initial delay) sized from the measured load time, so liveness never kills a pod that is still loading.
- **Readiness** = weights loaded + warmup finished + a recent inference succeeded. Only then take traffic.
- **Liveness** checks that the process answers, not that a generation completes. A slow `generate` under load must not restart the pod: a restart throws away the KV cache and costs a full cold start.

```yaml
startupProbe:            # covers weight load; tune from measured load time
  httpGet: {path: /health, port: 8000}
  periodSeconds: 10
  failureThreshold: 60   # 10 minutes
readinessProbe:          # model loaded + warm + recent success
  httpGet: {path: /ready, port: 8000}
  periodSeconds: 10
livenessProbe:           # process alive only; never runs the model
  httpGet: {path: /health, port: 8000}
  periodSeconds: 30
  failureThreshold: 3
```

## 2. Cold Start and Warmup

- A new replica pays for weight load, CUDA graph capture, and kernel autotuning before it reaches steady-state latency. The first requests after "loaded" are slower.
- Warm with representative requests before marking ready: short and long prompts, including the longest context bucket you serve, plus a streaming request and a structured-output request.
- Size an always-warm floor (min replicas) from autoscaling lag × expected burst growth. Scaling from zero on a burst means the burst is served by nobody for the cold-start window.
- Pre-stage weights on local NVMe or a node cache. Pulling them from object storage on every scale-up is usually the largest part of cold start.

```python
def prewarm(endpoint, model_id, prompt_lengths=(64, 2048, 16000)):
    """Warm kernels and CUDA graphs across length buckets; fail loud."""
    for n in prompt_lengths:
        r = requests.post(f"{endpoint}/v1/completions", timeout=120,
                          json={"model": model_id, "prompt": "x " * n, "max_tokens": 8})
        r.raise_for_status()   # a failed warmup must keep the replica NOT ready
```

## 3. Autoscaling Signals

- Scale on **waiting requests / queue depth**, **KV-cache utilization and preemption count**, and **p95 TTFT**. These move before users feel the overload.
- GPU utilization is a weak signal. It reports the fraction of time a kernel runs, not how saturated the GPU is. Memory-bound decode can read near 100% while more batch still fits.
- Scale up fast, scale down slowly. Scale-down must drain in-flight streams (preStop hook plus a termination grace period longer than your longest generation). Do not cut a stream mid-response.
- Autoscale on per-replica signals only after the router spreads load evenly. With prefix-sticky routing, one hot replica can trip the average while the rest idle (see [routing-and-control-planes.md](routing-and-control-planes.md)).

## 4. Token-Aware Overload Protection

The generic mechanics (bounded queues, 429/503 with Retry-After, priority classes) come from qa-resilience. What is specific to LLMs:

- **Limit in tokens, not requests.** Cost and GPU time are proportional to prompt + output tokens. Admit on an estimate of `prompt_tokens + max_tokens`, then charge the actual usage the server reports. Count with the model's tokenizer or the response `usage` field, never by splitting on whitespace.
- **Cap queue depth by token backlog.** One 100k-token prompt can hold more work than a hundred chat turns. See [queueing-theory-applied.md](queueing-theory-applied.md) for token-budget backpressure.
- **LLM degradation ladder**, cheapest first, each step gated by queue depth or TTFT:
  1. lower `max_tokens` for non-critical traffic;
  2. route low-priority traffic to a smaller model tier;
  3. serve exact-match cached responses where freshness allows;
  4. shed low-priority classes (429/503), keeping critical traffic.

  Every degraded response must be tagged in logs and metrics, so quality dashboards do not mix degraded and normal output.

## 5. Stateful Asset Coordination

- **KV and prefix caches belong to one model version.** New weights, tokenizer, chat template, or LoRA adapter make cached KV invalid. Key any external or shared cache by model version and adapter ID, and drain or flush on rollout.
- **Session reuse:** multi-turn chat benefits from landing on the replica that holds its prefix. Prefer a prefix-aware router over plain ClientIP affinity: affinity breaks behind NAT and pins hot users to one replica.
- **Version the serving unit as one artifact:** model weights, tokenizer, chat template, prompt templates, adapters, and runtime image roll forward and back together. A prompt template from v2 on weights from v1 is an untested combination.
- **Pin a tested runtime image tag.** Never deploy `:latest`, and never a new tag that has not passed the serving benchmark and eval gate. Runtime upgrades change default flags, kernels, and memory headroom.

## 6. LLM-Specific Rollout Gates

Use ai-mlops for rollout mechanics. Add these LLM-specific checks:

- Canary abort metrics must include **TTFT, ITL, schema-valid rate, output-length distribution, and refusal rate**, not only HTTP success rate. Quantization, kernel, and runtime changes often keep 200s flowing while output quality regresses.
- Shadow traffic doubles GPU spend for the mirrored share. Sample it, and compare outputs with an eval, not with string equality (sampling is non-deterministic).
- Blue-green needs double GPU capacity during cutover. Check quota and capacity first, or use a rolling canary.
- Gate every deploy on a benchmark of production-shaped traffic (see the Capacity Promotion Gate in [SKILL.md](../SKILL.md)).

---

## Checklist

- [ ] Startup probe sized from measured weight-load time; liveness never runs the model
- [ ] Readiness requires warmup across length buckets; a failed warmup keeps the replica not ready
- [ ] Warm floor sized from autoscaling lag; weights pre-staged on local storage
- [ ] Autoscaling on queue depth, KV utilization/preemptions, and p95 TTFT, not GPU utilization alone
- [ ] Scale-down drains in-flight streams
- [ ] Rate limits and queue caps denominated in tokens, counted with the real tokenizer or `usage`
- [ ] Degradation ladder defined and degraded responses tagged
- [ ] KV/prefix caches keyed by model version and adapter; flushed or drained on rollout
- [ ] Weights, tokenizer, templates, adapters, and runtime image versioned as one unit; image tag pinned and tested
- [ ] Canary gates include TTFT, ITL, schema-valid rate, and output-length drift

## References

- Kubernetes probes: https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/
- Kubernetes HPA: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- Google SRE Book: https://sre.google/sre-book/table-of-contents/
