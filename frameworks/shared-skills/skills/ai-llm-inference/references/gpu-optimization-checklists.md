# GPU Optimization Checklists

Use this guide for current GPU fit and production tuning without relying on stale benchmark tables.

## 1. GPU Selection Checklist

Pick the GPU after matching all three dimensions:

- model size and context window
- runtime support and maturity
- workload objective: lowest latency, highest throughput, or lowest cost

Use these heuristics:

- **H100 or H200**: safest mature choice for mainstream production stacks
- **B200 or GB200**: use when the runtime and driver stack are already validated for your workload
- **A100, L40S, L4, A10G**: cost-conscious serving for smaller models or lower concurrency
- **CPU or Apple Silicon**: GGUF or llama.cpp edge flows

## 2. Compatibility Preflight

- [ ] CUDA and driver versions match the chosen runtime
- [ ] interconnect matches the topology plan
- [ ] precision mode is supported by the runtime on this GPU
- [ ] multimodal encoder support is validated if required
- [ ] LoRA or adapter support is validated if required

## 3. Profiling Checklist

- [ ] GPU utilization measured at steady state
- [ ] queueing delay separated from compute time
- [ ] TTFT and ITL measured separately
- [ ] memory bandwidth pressure identified
- [ ] CPU bottlenecks or Python overhead ruled out
- [ ] network or cache transfer cost measured for multi-node serving

## 4. Memory And Cache Checklist

- [ ] max context size is justified by actual workloads
- [ ] KV cache dtype is chosen intentionally
- [ ] prefix caching or KV reuse is enabled where it helps
- [ ] fragmentation and eviction behavior are observable
- [ ] adapter memory pressure is measured if multi-LoRA is used

## 5. Latency Checklist

- [ ] warm replicas before shifting traffic
- [ ] cap queue depth and fail fast on overload
- [ ] use runtime-native structured outputs when validity matters
- [ ] verify p95 and p99 under burst load, not just average load
- [ ] compare colocated versus split topology only after a baseline exists

## 6. Throughput Checklist

- [ ] continuous batching tuned with realistic prompt lengths
- [ ] replica count chosen from real concurrency tests
- [ ] router policy preserves cache or adapter locality
- [ ] disaggregation justified by measured interference
- [ ] autoscaling reacts to queue depth and token throughput, not CPU alone

## 7. Production Alerts

- [ ] GPU OOM
- [ ] sustained low utilization with growing queue
- [ ] cache transfer failures or rising transfer latency
- [ ] schema-valid rate drop after runtime or precision changes
- [ ] cold adapter load spikes
- [ ] multimodal encoder queue growth

## 8. Procurement Rules

- Do not buy for benchmark headlines alone.
- Prefer mature software support over theoretical peak numbers.
- Re-verify support matrices before each major runtime or driver upgrade.
- Treat hardware advice as volatile and always tie it to the target runtime and workload.
