# Latency & Throughput Benchmark Template

Defines a reproducible load-testing process for LLM inference.

---

## 1. Test Parameters

model: "<model_id>"
concurrency_levels: [1, 4, 8, 16, 32]
request_rate: "<req/s>"
prompt_length: <tokens>
max_output_tokens: <tokens>

---

## 2. Test Scenarios

- Short prompts (≤50 tokens)  
- Medium prompts (100–500 tokens)  
- Long-context prompts (2k–10k tokens)  
- RAG prompts with large context blocks  

---

## 3. Metrics to Collect

### Latency

- Mean  
- P50, P95, P99  

### Throughput

- req/s  
- tokens/s  

### GPU Metrics

- GPU utilization  
- Memory usage  
- Kernel time  

---

## 4. Pass Criteria

- P95 latency < <threshold>  
- No OOM  
- Throughput ≥ baseline  
- No format regressions (JSON tasks)

---

## 5. Checklist

- [ ] Warmup period excluded  
- [ ] Stable iteration count  
- [ ] Metrics logged  
