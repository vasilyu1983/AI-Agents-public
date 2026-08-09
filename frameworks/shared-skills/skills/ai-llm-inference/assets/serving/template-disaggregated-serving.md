# Disaggregated Serving Template

Use this only after proving that colocated serving misses the target because different phases want different resources.

## 1. Split Plan

```yaml
split:
  mode: "<pd|epd>"
  router: "<vllm-router|llm-d|sglang-gateway|custom>"
  transfer_backend: "<runtime_specific>"
  rollback_mode: "colocated"
```

## 2. Phase Pools

```yaml
prefill_or_encoder_pool:
  replicas: <count>
  optimization_goal: "compute"

decode_pool:
  replicas: <count>
  optimization_goal: "memory_bandwidth"
```

## 3. Required Metrics

- queue depth by phase
- transfer latency
- TTFT by request class
- ITL by decode pool
- cache reuse rate
- structured-output valid rate if applicable

## 4. Go-Live Gates

- [ ] colocated baseline recorded
- [ ] transfer failures are surfaced
- [ ] router can bypass sticky placement during incidents
- [ ] p95 or p99 improves at target concurrency
- [ ] throughput does not regress
- [ ] rollback path tested
