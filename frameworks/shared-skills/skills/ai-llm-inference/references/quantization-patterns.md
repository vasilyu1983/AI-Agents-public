# Quantization Patterns for Current Inference Stacks

Choose quantization inside the runtime you will deploy. Hardware capability matters, but engine support and model support decide what is actually usable.

## Core Rules

- Prefer runtime-native precision paths before adding external conversion complexity.
- Separate weight quantization from KV cache quantization in both planning and validation.
- Treat structured outputs, tool calls, and long-context quality as first-class regression targets.
- Verify exact support on the runtime docs you will use in production.

## Runtime Support Snapshot

| Runtime | Practical Starting Points | Notes |
|---|---|---|
| **vLLM** | FP8, INT4 W4A16, AWQ, GPTQ, runtime-native LoRA and KV cache dtypes; FP4/NVFP4 W4A4 via llm-compressor and the Marlin kernel (GPTQ/AWQ/FP8/FP4 on Turing+, but Marlin MXFP4 specifically is not supported on Turing) | INT8 W8A8 is documented but the current vLLM docs exclude Blackwell (compute capability >= 10.0); use FP8 there instead. Full W4A4 activation quantization requires Blackwell-class (SM100+) hardware — on older GPUs the same NVFP4 recipe falls back to weight-only quantization. Verified 2026-07-11 at docs.vllm.ai. |
| **TensorRT-LLM** | FP8, INT8 SmoothQuant, INT4 or INT8 weight-only, GPTQ or AWQ, NVFP4 on supported Blackwell paths | strongest choice when precision control is a primary requirement |
| **SGLang** | FP4 (NVFP4, ModelOpt FP4), FP8 (blockwise and dynamic), MXFP4/MXFP8, INT4/INT8 (including W8A8), AWQ, GPTQ, compressed-tensors, quark, auto-round, gguf, quantized KV cache, multi-LoRA aware serving | docs.sglang.io/docs/advanced_features/quantization now resolves (the older advanced_features/quantization.html path 404s) — verify exact model and backend compatibility in current docs before deploying. Verified 2026-07-11. |
| **llama.cpp / GGUF** | Q4_K_M, Q5_K_M, Q6_K, Q8_0 | best for CPU, edge, and Apple Silicon flows |

## Decision Table

| Goal | First Choice | Fallback |
|---|---|---|
| keep highest quality on supported GPUs | FP8 in the target runtime | BF16 or weight-only INT8 |
| maximize memory reduction on GPU | INT4 or weight-only path | AWQ or GPTQ |
| long-context batching | KV cache quantization plus context budget tuning | lower max context or more memory |
| multi-tenant edge deployment | GGUF in llama.cpp | smaller base model |
| safety-critical or schema-critical tasks | FP8 or high-quality weight-only | stay at BF16 if evals regress |

## Runtime-Specific Notes

### vLLM

- Prefer FP8 where supported and validated.
- Use vLLM-native low-bit modes and external formats only if the serving path supports them end to end.
- FP4: the Marlin kernel in vLLM supports GPTQ/AWQ/FP8/FP4 on Turing and newer GPUs, except Marlin MXFP4 which excludes Turing (confirmed via current quantization docs). Separately, llm-compressor documents a W4A4 NVFP4 recipe (weights and activations both quantized to 4-bit) — full activation quantization needs Blackwell-class (SM100+) hardware; on pre-Blackwell GPUs the same recipe runs as weight-only. Verify at https://docs.vllm.ai/en/stable/features/quantization/ before using.
- Token-cost claims ("4× reduction") for FP4: hedge — actual savings depend on hardware, batch size, and context length. Measure against your production workload.
- Do not carry over a universal "Blackwell means no INT8" claim; scope it to the vLLM INT8 W8A8 path because that is what the current docs state.

### TensorRT-LLM

- Use TensorRT-LLM when precision and kernel selection are part of the core deployment strategy.
- Consider INT8 SmoothQuant or weight-only modes when FP8 is not the best tradeoff.
- For Blackwell-specific deployments, evaluate NVFP4 and the documented precision paths for that stack.

### SGLang

- Use only the quantizers documented for the server path and model family you are deploying.
- Re-test adapter and cache-heavy workloads after quantization because locality and reuse patterns can shift p95 behavior.

### GGUF And Edge

- Pick quant level by device RAM and acceptable quality loss, not by a generic "smallest is best" rule.
- Tune `n_ctx`, `threads`, and `n_gpu_layers` along with the GGUF level.

## KV Cache Quantization

Use KV cache quantization when long context or high concurrency makes cache memory the bottleneck.

Questions to answer:

- Does the runtime support the cache dtype on this hardware?
- Does long-context quality stay within tolerance?
- Does the larger batch size actually improve TTFT or throughput after queueing effects?

## Validation Checklist

- [ ] baseline BF16 or FP16 metrics recorded
- [ ] target runtime and version confirmed
- [ ] model loads with the intended precision path
- [ ] latency measured at realistic concurrency
- [ ] long-context quality tested
- [ ] schema-valid or structured-output rate tested
- [ ] adapter and cache-heavy workloads tested if relevant
- [ ] rollback path kept available

## Primary Sources

- vLLM quantization docs: https://docs.vllm.ai/en/stable/features/quantization/
- vLLM INT8 W8A8: https://docs.vllm.ai/en/stable/features/quantization/int8.html
- TensorRT-LLM precision reference: https://nvidia.github.io/TensorRT-LLM/reference/precision.html
- SGLang quantization docs: https://docs.sglang.io/docs/advanced_features/quantization
- llama.cpp: https://github.com/ggerganov/llama.cpp
