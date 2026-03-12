# Inference Performance Review Checklist

**Purpose**: Verify production readiness, identify optimizations, document baseline performance.

---

## Template Contract

### Goals
- Establish a reproducible performance baseline under realistic load.
- Identify bottlenecks and select safe optimizations with rollback plan.
- Ensure reliability, cost control, and observability are production-ready.

### Inputs
- Model artifact + config (context limits, decoding settings, quantization).
- Traffic shape: prompt length distribution, output length, concurrency, QPS.
- Hardware and deployment topology.
- SLOs/budgets: latency, availability, cost per request.

### Decisions
- Serving configuration (batching, scheduling, caching, parallelism).
- Optimization plan (quantization, kernel changes, speculative decoding).
- Capacity plan (replicas, autoscaling, queue caps) and rollback triggers.

### Risks
- Tail-latency explosions from queueing and long prompts.
- Quality regressions from quantization/optimizations.
- Cascading retries and overload amplification.
- OOM and instability due to unbounded context or concurrency.

### Metrics
- TTFT/ITL and total latency p50/p95/p99 under load.
- Throughput (req/s, tok/s), GPU/CPU utilization, memory headroom.
- Error rate by class and cost per request.

## 1. Configuration

### Model Details
- Model name: _______________
- Model size: ___B parameters
- Original precision: [ ] FP32 [ ] FP16 [ ] BF16 [ ] FP8

### Hardware
- GPU type: _______________
- GPU count: ___
- GPU memory: ___GB each
- Total VRAM: ___GB

### Framework
- Inference engine: _______________ (example: open-source server, managed endpoint)
- Version: _______________

### Quantization
- Current: [ ] None [ ] FP8 [ ] INT8 [ ] INT4 [ ] AWQ [ ] GPTQ [ ] GGUF
- KV cache dtype: [ ] FP16 [ ] FP8 [ ] INT8

---

## 2. Performance Baseline

### Latency (measure with realistic load)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Time to First Token (TTFT) P50 | ___ms | ___ms | [ ] Pass [ ] Fail |
| TTFT P95 | ___ms | ___ms | [ ] Pass [ ] Fail |
| Inter-Token Latency (ITL) | ___ms | ___ms | [ ] Pass [ ] Fail |
| Total Latency P50 | ___ms | ___ms | [ ] Pass [ ] Fail |
| Total Latency P95 | ___ms | ___ms | [ ] Pass [ ] Fail |
| Total Latency P99 | ___ms | ___ms | [ ] Pass [ ] Fail |

### Throughput

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Requests/second | ___ | ___ | [ ] Pass [ ] Fail |
| Output tokens/second | ___ | ___ | [ ] Pass [ ] Fail |
| Concurrent users | ___ | ___ | [ ] Pass [ ] Fail |

### Resource Utilization

| Metric | Value | Healthy Range | Status |
|--------|-------|---------------|--------|
| GPU utilization | ___% | 70-95% | [ ] Pass [ ] Fail |
| GPU memory used | ___GB | <90% VRAM | [ ] Pass [ ] Fail |
| CPU utilization | ___% | <80% | [ ] Pass [ ] Fail |
| System memory | ___GB | <80% | [ ] Pass [ ] Fail |

---

## 3. Optimization Checklist

### Quantization

| Optimization | Applied | Impact | Notes |
|--------------|---------|--------|-------|
| FP8 weights | [ ] Yes [ ] No [ ] N/A | Lower memory / higher throughput (varies) | Validate on eval set |
| FP8 KV cache | [ ] Yes [ ] No [ ] N/A | Lower KV memory (varies) | Validate long-context quality |
| INT4/FP4 (if needed) | [ ] Yes [ ] No [ ] N/A | Large memory reduction (varies) | Higher regression risk |
| Weight-only quantization | [ ] Yes [ ] No [ ] N/A | Lower memory (varies) | Compare candidates |

**Accuracy validation post-quantization**: [ ] Completed [ ] Pending

### Batching

| Setting | Current | Recommended | Status |
|---------|---------|-------------|--------|
| Continuous batching | [ ] On [ ] Off | On | |
| Max batch size | ___ | Tune per GPU | |
| Max tokens in batch | ___ | Tune per use case | |

### Attention Optimization

| Optimization | Applied | Notes |
|--------------|---------|-------|
| Optimized attention kernels | [ ] Yes [ ] No [ ] N/A | Example: FlashAttention-style kernels |
| Kernel-level serving optimizations | [ ] Yes [ ] No [ ] N/A | Example: fused prefill/decode kernels |
| KV-cache paging | [ ] Yes [ ] No [ ] N/A | Example: PagedAttention-style paging |

### Caching

| Cache Type | Enabled | Hit Rate | Notes |
|------------|---------|----------|-------|
| Prefix caching | [ ] Yes [ ] No | ___% | Reuse common prefixes |
| Response caching | [ ] Yes [ ] No | ___% | Semantic or exact |
| Embedding caching | [ ] Yes [ ] No | ___% | For RAG |

### Parallelism

| Strategy | Applied | Configuration |
|----------|---------|---------------|
| Tensor parallelism | [ ] Yes [ ] No | TP=___ |
| Pipeline parallelism | [ ] Yes [ ] No | PP=___ |
| Data parallelism | [ ] Yes [ ] No | Replicas=___ |

### Advanced

| Optimization | Applied | Notes |
|--------------|---------|-------|
| CUDA graphs | [ ] Yes [ ] No | Reduces kernel launch overhead |
| Speculative decoding | [ ] Yes [ ] No | Draft model: ___ |
| Chunked prefill | [ ] Yes [ ] No | For long inputs |

---

## 4. Cost Analysis

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Cost per 1K input tokens | $___ | $___ | |
| Cost per 1K output tokens | $___ | $___ | |
| Cost per request (avg) | $___ | $___ | |
| Monthly projected cost | $___ | $___ | |
| GPU utilization efficiency | ___% | >80% | |

### Cost Optimization Actions
- [ ] _______________
- [ ] _______________
- [ ] _______________

---

## 5. Reliability

| Check | Status | Notes |
|-------|--------|-------|
| Health check endpoint | [ ] Configured | |
| Graceful shutdown | [ ] Tested | |
| Request timeout | ___s | |
| Max retries | ___ | |
| Circuit breaker | [ ] Configured | |
| Load balancing | [ ] Configured | |

---

## 6. Monitoring

| Metric | Exported | Alert Threshold |
|--------|----------|-----------------|
| Request latency | [ ] Yes | P95 > ___ms |
| Throughput | [ ] Yes | < ___ req/s |
| Error rate | [ ] Yes | > ___% |
| GPU utilization | [ ] Yes | < 50% or > 95% |
| Memory usage | [ ] Yes | > 90% |
| Queue depth | [ ] Yes | > ___ |

---

## 7. Anti-Patterns Check

| Anti-Pattern | Risk | Status |
|--------------|------|--------|
| Unbounded context | OOM, latency explosion | [ ] Mitigated |
| No max_tokens limit | Cost explosion | [ ] Mitigated |
| Uncontrolled retries | Cascading failures | [ ] Mitigated |
| Missing timeout | Hung requests | [ ] Mitigated |
| No rate limiting | Resource exhaustion | [ ] Mitigated |
| No caching | Redundant compute | [ ] Mitigated |

---

## 8. Decisions & Actions

### Optimizations to Implement
1. _______________
2. _______________
3. _______________

### Re-benchmark Date
- Next review: _______________
- Owner: _______________

### Sign-Off
- [ ] ML Engineer: _______________ Date: ___
- [ ] Platform Engineer: _______________ Date: ___
