# Quantization Format Table

Reference for the most common quantization formats used in local and self-hosted LLM workflows.

Last updated: 2026-07.

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
| Q2_K | ~2.6 | ~5.6x smaller | High | Extreme memory constraint; expect noticeable degradation |
| Q3_K_M | ~3.4 | ~4.3x smaller | Moderate–high | Very tight VRAM, acceptable for simple tasks |
| Q4_0 | ~4.5 | ~3.2x smaller | Moderate | Older format; prefer Q4_K_M |
| Q4_K_M | ~4.8 | ~2.9x smaller | Low–moderate | **Default recommendation** — best quality/size for most use cases |
| Q4_K_S | ~4.6 | ~3.1x smaller | Moderate | Slightly smaller than Q4_K_M; slightly lower quality |
| Q5_K_M | ~5.7 | ~2.4x smaller | Very low | When VRAM allows; noticeably better on long-context tasks |
| Q5_K_S | ~5.5 | ~2.5x smaller | Low | |
| Q6_K | ~6.6 | ~2.0x smaller | Minimal | Near-lossless for most benchmarks; requires more VRAM |
| Q8_0 | ~8.5 | ~1.7x smaller | Near-zero | Best quality before full precision; use when VRAM permits |
| F16 | 16 | 1x (baseline) | Zero | Full half-precision; maximum quality, maximum memory |
| F32 | 32 | 2x larger | Zero | Training and exact reproducibility; not needed for inference |

**K-quant explanation:**
- `_K` suffix = "k-quant" method: mixed precision that quantizes attention and feed-forward layers at different bit depths.
- `_M` = medium mixed block size; `_S` = small (slightly more aggressive); `_L` = large (slightly more conservative).
- K-quants are strictly better than plain Q4_0/Q5_0 at same size — always prefer K-quants when available.

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
| Calibration | Required (128–512 samples; ~10 min on GPU) |
| Quality vs GPTQ | Generally equal or slightly better at same bit-width |
| Runtime support | vLLM, TGI, LMDeploy, AutoAWQ, transformers |
| File format | `.safetensors` with AWQ metadata |
| GGUF compatibility | No — separate format from GGUF |

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
| Calibration | Required (C4 or Wikitext-2 standard datasets) |
| Quality vs AWQ | Roughly equivalent; slight quality edge to AWQ at 4-bit |
| Runtime support | AutoGPTQ, ExLlamaV2, vLLM, TGI |
| File format | `.safetensors` with GPTQ config |
| Group size | 32 or 128 (lower = higher quality, larger file) |

**When to use GPTQ:**
- When a pre-quantized AWQ model isn't available but GPTQ is.
- ExLlamaV2 backend provides excellent GPTQ throughput on GPU.

---

## FP8 (8-bit Floating Point)

Available on H100 and newer GPUs (Ada Lovelace, Hopper). Near-lossless with significant throughput gains.

| Property | Value |
|----------|-------|
| Bits | 8-bit float (E4M3 or E5M2) |
| Quality loss | Near-zero on most benchmarks |
| Throughput gain | 1.5–2x vs BF16 on H100 |
| Runtime support | TensorRT-LLM, vLLM V1 (V0 deprecated), SGLang |
| Hardware required | H100, RTX 4090 (limited), A100 (software emu) |

---

## EXL2 (ExLlamaV2)

Variable per-layer bit allocation; allows precise control of bits per weight.

| Property | Value |
|----------|-------|
| Target bits | 2–8 bit (fractional, e.g. 3.5-bit) |
| Quality | Best quality-per-bit for GPU inference; often beats GPTQ |
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
| Extreme (llama.cpp "turbo" quant types) | up to ~8×+ | Task-dependent, can be noticeable | llama.cpp (e.g. `--cache-type-k turbo3 --cache-type-v turbo3` for ~3-bit KV) — newer and moves fast; verify current type names via `llama-server --help` before scripting |

**When to use KV-cache quantization:**
- Long-context workloads (>8k tokens) where KV cache would otherwise exhaust VRAM.
- Increasing concurrent request capacity on a fixed GPU budget.
- Not beneficial for short single-turn conversations where KV overhead is small.

**Tradeoffs:**
- INT4 KV (and more so the extreme sub-4-bit "turbo" tiers) on long documents can produce noticeable quality loss; always evaluate on real prompts before shipping.
- Flag names and available quant type strings differ between llama.cpp versions — check `llama-server --help` or current docs before scripting.
- Without Flash Attention enabled, quantized KV cache must be dequantized on every attention step, which can make generation *slower* than unquantized KV — always pair KV-cache quantization with Flash Attention.

---

## Speculative Decoding

Speculative decoding uses a small "draft" model to generate candidate tokens cheaply, then verifies them in parallel with the large target model. Accepted tokens are free; rejected tokens cost one forward pass.

**When it helps:**
- Target model is large (≥30B) and generation-bound (not prefill-bound).
- A compatible small draft model exists (same tokenizer / vocabulary as target).
- Batch size 1 or very small batches — benefit collapses at high concurrency.

**Typical speedup:** 1.5–2.5× on matched draft/target pairs at batch size 1. Highly task-dependent — code generation benefits more than generic chat.

**Runtime support (as of early 2026; verify at primary sources):**
- llama.cpp: `--model-draft <path>` flag (check current docs at https://github.com/ggml-org/llama.cpp)
- vLLM: `--speculative-model` (V1 engine; V0 fully deprecated — see https://docs.vllm.ai/en/stable/usage/v1_guide/)
- Ollama: speculative decoding support and env var names change between minor versions — check `ollama help serve` and current release notes before relying on any specific flag

**Draft model selection rule:** Use a model from the same family, 4–10× smaller than the target. Mismatched tokenizers silently produce wrong output — always verify the draft and target use the same vocabulary.

---

## NPU / Accelerator Tier

A growing class of devices includes a dedicated Neural Processing Unit (NPU) or AI accelerator alongside the CPU and GPU. As of mid-2026, NPU tooling is fast-moving — treat specific capability claims as verify-before-use.

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
│       └── Large model + speculative decoding → add --speculative-model
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
- Assuming Q4_K_M and Q4_0 are equivalent — K-quants are strictly better at the same size.
- Calibrating GPTQ/AWQ on a dataset unrelated to your actual task distribution.
- Assuming speculative decoding helps at high batch size — benefit is batch-size-1 focused.
- Trusting NPU inference is being used without profiling to confirm — fallback to CPU/GPU is silent in some runtimes.
