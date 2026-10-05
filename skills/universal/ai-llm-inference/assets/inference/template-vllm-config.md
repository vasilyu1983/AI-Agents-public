# vLLM Serve Template

Configuration skeleton for modern vLLM deployments. Adjust flags to the version you actually run.

## 1. Engine Settings

```yaml
engine:
  model: "<model_name_or_path>"
  dtype: "bfloat16"
  tensor_parallel_size: <num_gpus>
  max_model_len: <tokens>
  gpu_memory_utilization: 0.90
  max_num_seqs: <concurrent_sequences>
  max_num_batched_tokens: <batched_tokens>
  enable_prefix_caching: true
  kv_cache_dtype: "auto"
  trust_remote_code: false
```

## 2. Structured Outputs

```yaml
structured_outputs:
  enabled: true
  backend: "auto"
  enable_in_reasoning: false
```

## 3. Optional Adapter Settings

```yaml
lora:
  enable: false
  modules: []
  max_loras: <count>
  max_cpu_loras: <count>
  max_lora_rank: <rank>
```

## 4. OpenAI-Compatible Server

```bash
vllm serve <model_name_or_path> \
  --dtype bfloat16 \
  --tensor-parallel-size <num_gpus> \
  --max-model-len <tokens> \
  --gpu-memory-utilization 0.90 \
  --max-num-seqs <concurrent_sequences> \
  --max-num-batched-tokens <batched_tokens> \
  --enable-prefix-caching \
  --kv-cache-dtype auto \
  --structured-outputs-config.backend auto \
  --port 8000
```

## 5. Guardrails

- [ ] request token caps enforced at the API boundary
- [ ] queue depth or overload policy defined outside the engine
- [ ] TTFT, ITL, and schema-valid rate measured under concurrency
- [ ] reasoning plus structured-output behavior tested if applicable
- [ ] disaggregation only enabled after colocated baseline is recorded
