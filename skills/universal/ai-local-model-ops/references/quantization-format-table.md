# Quantization Format Table

Reference for the most common quantization formats used in local and self-hosted LLM workflows.

## Table of Contents

- [GGUF Formats (llama.cpp / Ollama)](#gguf-formats-llamacpp--ollama)
- [AWQ (Activation-aware Weight Quantization)](#awq-activation-aware-weight-quantization)
- [GPTQ (Generalized Post-Training Quantization)](#gptq-generalized-post-training-quantization)
- [FP8 (8-bit Floating Point)](#fp8-8-bit-floating-point)
- [EXL2 (ExLlamaV2)](#exl2-exllamav2)
- [Quick Decision Tree](#quick-decision-tree)
- [Anti-patterns](#anti-patterns)

---

## GGUF Formats (llama.cpp / Ollama)

GGUF is the dominant format for CPU + Apple Silicon inference via llama.cpp and Ollama. Quantization level is encoded in the filename suffix.

| Format | Bits/weight | Size vs FP16 | Quality loss | Best for |
|--------|-------------|--------------|--------------|----------|
| Q2_K | ~2.6 | ~6.2x smaller | High | Extreme memory constraint; expect noticeable degradation |
| Q3_K_M | ~3.4 | ~4.7x smaller | Moderate–high | Very tight VRAM, acceptable for simple tasks |
| Q4_0 | ~4.5 | ~3.6x smaller | Moderate | Older format; prefer Q4_K_M |
| Q4_K_M | ~4.8 | ~3.3x smaller | Low–moderate | **Default recommendation** — best quality/size for most use cases |
| Q4_K_S | ~4.6 | ~3.5x smaller | Moderate | Slightly smaller than Q4_K_M; slightly lower quality |
| Q5_K_M | ~5.7 | ~2.8x smaller | Very low | When VRAM allows; noticeably better on long-context tasks |
| Q5_K_S | ~5.5 | ~2.9x smaller | Low | |
| Q6_K | ~6.6 | ~2.4x smaller | Minimal | Near-lossless for most benchmarks; requires more VRAM |
| Q8_0 | ~8.5 | ~1.9x smaller | Near-zero | Best quality before full precision; use when VRAM permits |
| F16 | 16 | 1x (baseline) | Zero | Full half-precision; maximum quality, maximum memory |
| F32 | 32 | 2x larger | Zero quantization loss | Full-precision baseline when a workflow requires it |

Size vs FP16 = 16 / bits-per-weight. The bpw and size columns are illustrative, and the quality labels are selection heuristics, not measured results for a particular model. Effective file-level bpw is model-dependent because K-quant recipes can mix tensor types. Derive the real figure from the file you will run: `bpw = file_bytes × 8 / params`. Check the current [llama.cpp quantization guide](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md) before choosing a format.

**K-quant explanation:**
- `_K` identifies a superblock quantization type. A recipe such as `Q4_K_M` may assign different types to different tensors; inspect the resulting file rather than treating its name as a uniform bit width.
- `_M` and `_S` distinguish quantization recipes, not block sizes. Compare the actual size and task quality of candidate files.
- Prefer a K-quant candidate over legacy Q4_0/Q5_0 for the first evaluation, then keep the format that passes the workload's quality and memory gates.

**Recommended defaults:**
- Day-to-day local use: `Q4_K_M`
- Quality-sensitive tasks: `Q5_K_M` or `Q6_K`
- VRAM-constrained: `Q3_K_M` (last resort before quality becomes unusable)

---

## AWQ (Activation-aware Weight Quantization)

AWQ is a 4-bit method that preserves important weights by analyzing activation magnitudes before quantizing. Requires a one-time calibration step.

| Property | Value |
|----------|-------|
| Target bits | 4-bit (W4A16: 4-bit weights, 16-bit activations) |
| Calibration | Use representative task data; time depends on model and hardware |
| Quality vs GPTQ | Compare on the target model and task |
| Runtime support | vLLM, TGI, LMDeploy, transformers |
| File format | `.safetensors` with AWQ metadata |
| GGUF compatibility | No — separate format from GGUF |

**Producing AWQ/GPTQ checkpoints:** the original AutoAWQ and AutoGPTQ repositories are archived. Use a quantization toolkit that is still maintained (check recent releases and open-issue activity before adopting it), or download a pre-quantized checkpoint from a maintained source.

**When to use AWQ:**
- GPU-based serving (vLLM, TGI) where GGUF is not the right format.
- When you need 4-bit GPU inference with production-grade throughput.
- Not recommended for Apple Silicon (use GGUF instead).

---

## GPTQ (Generalized Post-Training Quantization)

GPTQ is a 4-bit method using second-order weight correction. Slightly older than AWQ; still widely available for most models.

| Property | Value |
|----------|-------|
| Target bits | 2-bit, 3-bit, 4-bit (4-bit most common) |
| Calibration | Use representative task data |
| Quality vs AWQ | Compare on the target model and task |
| Runtime support | ExLlamaV2, vLLM, TGI |
| File format | `.safetensors` with GPTQ config |
| Group size | 32 or 128 (lower = higher quality, larger file) |

**When to use GPTQ:**
- When a pre-quantized AWQ model isn't available but GPTQ is.
- ExLlamaV2 backend provides excellent GPTQ throughput on GPU.

---

## FP8 (8-bit Floating Point)

FP8 support depends on the accelerator and serving kernel. Check the current runtime hardware matrix and measure quality and throughput on the target workload.

| Property | Value |
|----------|-------|
| Bits | 8-bit float (E4M3 or E5M2) |
| Quality loss | Evaluate against the BF16 baseline on the target task |
| Throughput gain | Measure against BF16 on the target hardware and batch shape |
| Runtime support | Check current TensorRT-LLM, vLLM, or SGLang documentation |
| Hardware required | Confirm native FP8 kernel support in the runtime's hardware matrix |

---

## EXL2 (ExLlamaV2)

Variable per-layer bit allocation; allows precise control of bits per weight.

| Property | Value |
|----------|-------|
| Target bits | 2–8 bit (fractional, e.g. 3.5-bit) |
| Quality | Compare with GPTQ on the target model and task |
| Runtime | ExLlamaV2 only |
| Calibration | Required |

---

---

## KV-Cache Quantization

KV-cache is often the dominant memory consumer at long contexts. Quantizing the KV cache lets you fit longer sequences or run more concurrent requests without changing the model weights.

| KV quant level | Memory saving vs FP16 KV | Quality impact | Support |
|----------------|--------------------------|----------------|---------|
| INT8 KV | ~2× | Minimal | llama.cpp (`--cache-type-k q8_0 --cache-type-v q8_0`), vLLM (`--kv-cache-dtype fp8_e5m2`) |
| INT4 KV | ~4× | Moderate | llama.cpp (`--cache-type-k q4_0`); vLLM experimental |
| FP8 KV | ~2× | Near-zero | vLLM on H100, TensorRT-LLM |

**When to use KV-cache quantization:**
- Contexts where measured KV-cache use would otherwise exhaust available memory.
- Increasing concurrent request capacity on a fixed GPU budget.
- Not beneficial for short single-turn conversations where KV overhead is small.

**Tradeoffs:**
- INT4 KV on long documents can produce noticeable quality loss; always evaluate on real prompts before shipping.
- Only use KV cache types your llama.cpp build lists under `--cache-type-k` / `--cache-type-v` in `llama-server --help`; community forks may advertise types mainline does not have.
- Flag names and available quant type strings differ between llama.cpp versions — check `llama-server --help` or current docs before scripting.
- Benchmark quantized KV with the attention implementation your runtime actually uses; memory savings can come with a throughput or quality cost.

---

## Speculative Decoding

Speculative decoding uses a small draft model to propose candidate tokens, then verifies them with the target model in a batch. Drafting and verification both cost compute; measure whether the accepted-token rate pays for them. See the [llama.cpp speculative-decoding guide](https://github.com/ggml-org/llama.cpp/blob/master/docs/speculative.md).

**When it helps:**
- Generation dominates latency rather than prompt processing.
- A compatible, faster draft model exists; check the runtime's draft/target compatibility rules.
- Batch size 1 or very small batches — benefit collapses at high concurrency.

Compare end-to-end latency and accepted-token rate with speculative decoding enabled and disabled at the intended concurrency.

**Runtime support (flags change between releases; verify at primary sources):**
- llama.cpp: `--model-draft <path>` flag (check current docs at https://github.com/ggml-org/llama.cpp)
- vLLM: configured through its speculative-decoding config — check the current vLLM speculative-decoding docs (https://docs.vllm.ai) for the flag and schema before scripting
- Ollama: speculative decoding support and env var names change between minor versions — check `ollama help serve` and current release notes before relying on any specific flag

**Draft model selection rule:** Start with a smaller compatible model, then measure its proposal speed and acceptance rate; reject an incompatible pair before serving requests.

---

## NPU / Accelerator Tier

A growing class of devices includes a dedicated Neural Processing Unit (NPU) or AI accelerator alongside the CPU and GPU. NPU tooling is fast-moving — treat specific capability claims as verify-before-use.

| Accelerator | Device | Maturity | Notes |
|-------------|--------|----------|-------|
| Apple Neural Engine (ANE) | M1/M2/M3/M4 Macs, iPhones, iPads | Production (via Core ML / MLX) | MLX targets Metal (GPU) by default; ANE is accessible via Core ML conversion. MLX LoRA fine-tune runs on Metal. |
| Qualcomm Hexagon NPU | Snapdragon X Elite, Windows on ARM | Early production | llama.cpp and Qualcomm's AI Hub SDK have Hexagon backends; verify current model support |
| Intel NPU (Neural Compute Stick successors) | Intel Core Ultra laptops ("Meteor Lake" and later) | Early production | OpenVINO is the primary inference path; support varies by model family |

**Key tradeoffs:**
- NPU inference is often power-efficient but has strict memory and operator support limits — not every model or quantization format will run.
- Fallback to CPU/GPU happens silently in some runtimes if the NPU kernel is unsupported — profile to confirm the accelerator is actually being used.
- Apple Silicon: MLX targets Metal (GPU); Core ML targets ANE. For most local LLM work, Metal via MLX or Ollama gives better throughput than ANE. ANE is more relevant for mobile (iOS/iPadOS) deployment.

**Verify current support before committing:** NPU model coverage, driver requirements, and performance characteristics are updated frequently.

---

## Quick Decision Tree

```
Local inference needed?
├── Apple Silicon (Mac)
│   ├── Framework-level (fine-tune, custom pipeline) → MLX
│   └── Daemon / app use → GGUF via Ollama or LM Studio
│       └── Long context → add KV-cache quantization (llama.cpp --cache-type-k q8_0)
├── Linux GPU workstation
│   ├── Ollama / llama.cpp → GGUF
│   └── vLLM / TGI → AWQ (preferred) or GPTQ
│       └── Large model + speculative decoding → enable it per the current vLLM speculative-decoding docs
└── Production H100 serving
    ├── Latency-critical → FP8 or AWQ
    ├── Max quality → BF16 (no quantization)
    └── Long context / high concurrency → FP8 KV cache
```

---

## Anti-patterns

- Using Q2_K for any user-facing workflow without explicit quality evaluation.
- Mixing GGUF and AWQ/GPTQ formats in the same serving stack without knowing the difference.
- Choosing quantization format before deciding on the runtime — runtime constraints the format choice.
- Assuming Q4_K_M and Q4_0 are equivalent without checking file size and task quality.
- Calibrating GPTQ/AWQ on a dataset unrelated to your actual task distribution.
- Assuming speculative decoding helps at high batch size — benefit is batch-size-1 focused.
- Trusting NPU inference is being used without profiling to confirm — fallback to CPU/GPU is silent in some runtimes.
