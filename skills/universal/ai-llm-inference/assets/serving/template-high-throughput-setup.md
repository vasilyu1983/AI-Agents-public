# High-Throughput Serving Setup

Use this template for replica-based or routed serving where throughput and p95 matter more than minimal setup time.

## 1. Topology

```yaml
topology:
  engine: "<vllm|sglang|tensorrt-llm>"
  replicas: <count>
  router: "<none|vllm-router|llm-d|sglang-gateway>"
  disaggregation: "<none|pd|epd>"
  adapter_mode: "<none|multi-lora>"
```

## 2. Runtime Policy

```yaml
runtime:
  batching: "continuous"
  max_num_seqs: <value>
  max_num_batched_tokens: <value>
  kv_cache_dtype: "auto"
  enable_prefix_reuse: true
  structured_outputs: true
```

## 3. Placement Policy

```yaml
routing:
  sticky_prefix: true
  sticky_adapter: true
  load_signal: "queue_depth"
  overload_action: "shed"
```

## 4. Observability

Dashboards should include:

- TTFT percentiles
- ITL percentiles
- end-to-end latency
- tokens per second
- queue depth
- cache hit or reuse rate
- adapter cold-load latency
- structured-output valid rate

## 5. Readiness Checklist

- [ ] colocated baseline exists
- [ ] overload behavior tested
- [ ] router decisions are observable
- [ ] prefix and adapter locality are measured
- [ ] rollback to simpler routing is possible
