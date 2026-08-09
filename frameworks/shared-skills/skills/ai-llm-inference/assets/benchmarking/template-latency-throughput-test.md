# Latency And Throughput Benchmark Template

Use this for reproducible inference testing under realistic concurrency.

## 1. Test Matrix

```yaml
model: "<model_id>"
runtime: "<vllm|sglang|tensorrt-llm|llama.cpp>"
precision: "<bf16|fp8|int4|gguf-q4_k_m>"
traffic_buckets:
  - name: short
    prompt_tokens: 64
    output_tokens: 64
  - name: medium
    prompt_tokens: 512
    output_tokens: 256
  - name: long
    prompt_tokens: 8192
    output_tokens: 512
concurrency_levels: [1, 4, 8, 16, 32]
streaming: [false, true]
structured_outputs: [false, true]
```

## 2. Metrics To Collect

- TTFT p50, p95, p99
- ITL p50, p95, p99
- end-to-end latency p50, p95, p99
- requests per second
- output tokens per second
- queue delay
- GPU utilization and memory headroom
- cache hit or reuse rate
- structured-output valid rate

## 3. Test Hygiene

- [ ] warmup requests excluded
- [ ] fixed prompt buckets used
- [ ] steady-state window defined
- [ ] same tokenizer and chat template used across variants
- [ ] overload behavior captured, not silently dropped
- [ ] streaming measured separately from non-streaming

## 4. Pass Criteria Template

- p95 TTFT <= <target_ms>
- p95 ITL <= <target_ms>
- p95 end-to-end latency <= <target_ms>
- structured-output valid rate >= <target_rate>
- no OOM or crash under target concurrency
- throughput >= current baseline

## 5. Report Format

```text
variant:
  runtime=<runtime>
  precision=<precision>
  routing=<policy>
  topology=<colocated|pd|epd>
results:
  ttft_p95_ms=<value>
  itl_p95_ms=<value>
  e2e_p95_ms=<value>
  output_toks_per_sec=<value>
  structured_output_valid_rate=<value>
decision:
  keep|reject|needs_followup
```
