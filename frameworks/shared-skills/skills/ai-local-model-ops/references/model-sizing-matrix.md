# Model Sizing Matrix 2026

Hardware tiers and expected throughput for running quantized open-weight models locally or on single-node GPU setups. Numbers are indicative — measure on your actual hardware and quant level.

Last updated: 2026-07. Verify model releases and VRAM specs before quoting to users.

## Table of Contents

- [Hardware Tiers](#hardware-tiers)
- [Llama 4 Family](#llama-4-family)
- [Mixtral Family](#mixtral-family)
- [Qwen 3 Family](#qwen-3-family)
- [DeepSeek Family](#deepseek-family)
- [Mistral Family](#mistral-family)
- [Gemma 4 Family](#gemma-4-family)
- [GPT-OSS (OpenAI open-weight releases)](#gpt-oss-openai-open-weight-releases)
- [Hardware-specific notes](#hardware-specific-notes)
- [Throughput Estimates (tokens/sec, generation)](#throughput-estimates-tokenssec-generation)
- [Selection Heuristic](#selection-heuristic)
- [Local vs API: The Real Tradeoff](#local-vs-api-the-real-tradeoff)

---

## Hardware Tiers

| Tier | RAM / VRAM | Typical use |
|------|-----------|-------------|
| M3 MacBook Pro (36 GB) | 36 GB unified | Solo dev, experiments, up to ~30B quant |
| M4 Max Mac Studio (128 GB) | 128 GB unified | Team workflows, up to 70B Q4 or 405B small variants |
| Single NVIDIA RTX 4090 | 24 GB GDDR6X | Linux workstation; up to 34B Q4_K_M; limited FP8 |
| Single NVIDIA RTX 5090 (Blackwell) | 32 GB GDDR7 | Linux workstation; up to 34B Q4_K_M with headroom; native FP8 |
| Single NVIDIA H100 (SXM/PCIe 80 GB) | 80 GB HBM3 | Production inference, up to 70B full or 405B quant; native FP8 |

---

## Llama 4 Family

| Model | Params | MoE? | Quant | M3 36 GB | M4 128 GB | RTX 4090 | H100 80 GB |
|-------|--------|------|-------|----------|-----------|----------|------------|
| Llama 4 Scout | 17B active / 109B total | Yes (16 experts) | Q4_K_M | Fits (~14 GB active) | Fits easily | Fits (16 GB active) | Fits |
| Llama 4 Scout | 17B active | Q8_0 | Tight (~32 GB) | Fits | Not recommended (≥40 GB) | Fits |
| Llama 4 Maverick | 17B active / 400B total | Yes (128 experts) | Q4_K_M | No (router overhead) | Fits (dense layer ~35 GB) | No | Tight (~72 GB) |
| Llama 4 Maverick | 17B active | Q2_K | Experimental | Fits (~28 GB) | Fits | Experimental | Fits |
| Llama 4 Behemoth | weights not publicly released (paused as of May 2026) | — | — | — | — | — | — |
| Llama 3.3 70B | 70B | No | Q4_K_M | No (>40 GB) | Fits (~40 GB) | No (>24 GB) | Fits (~40 GB) |
| Llama 3.1 8B | 8B | No | Q4_K_M | Fits (~5 GB) | Fits | Fits | Fits |

Notes:
- MoE models load only active parameters per token; router/embedding weights are always resident.
- Q4_K_M = 4-bit K-quant with mixed precision on attention layers — best quality/size tradeoff.
- "Fits" = loads into RAM/VRAM with headroom for KV cache at 2–4k context.
- **Llama 4 Scout 10M-token context:** The stated 10M-token context is theoretical; KV cache at that length far exceeds consumer hardware. Practical ceiling on a 36 GB M3 with Q4_K_M is approximately 32–64k context before KV cache exhausts available memory. Verify via llama.cpp `--ctx-size` flag on your hardware before specifying long contexts.
- **Llama 4 Behemoth:** Meta previewed Behemoth as a ~2T-parameter teacher model in April 2025 but repeatedly delayed it through 2025, then shifted its frontier effort to a closed-weight model (Muse Spark, announced April 2026) instead of shipping Behemoth weights. Treat Behemoth as effectively shelved — do not plan local-inference work around it, and re-verify at https://ai.meta.com/llama before assuming otherwise.

---

## Mixtral Family

| Model | Params | MoE? | Quant | M3 36 GB | M4 128 GB | RTX 4090 | H100 80 GB |
|-------|--------|------|-------|----------|-----------|----------|------------|
| Mixtral 8x7B | 47B total / 13B active | Yes | Q4_K_M | Tight (~26 GB) | Fits | Tight (~25 GB) | Fits |
| Mixtral 8x7B | 47B total | Q5_K_M | No (~32 GB) | Fits | No | Fits |
| Mixtral 8x22B | 141B total / 39B active | Yes | Q4_K_M | No | Fits (~78 GB) | No | Tight (~75 GB) |

---

## Qwen 3 Family

| Model | Params | MoE? | Quant | M3 36 GB | M4 128 GB | RTX 4090 | H100 80 GB |
|-------|--------|------|-------|----------|-----------|----------|------------|
| Qwen3-0.6B | 0.6B | No | Q4_K_M | Fits (<1 GB) | Fits | Fits | Fits |
| Qwen3-4B | 4B | No | Q4_K_M | Fits (~3 GB) | Fits | Fits | Fits |
| Qwen3-8B | 8B | No | Q4_K_M | Fits (~5 GB) | Fits | Fits | Fits |
| Qwen3-14B | 14B | No | Q4_K_M | Fits (~9 GB) | Fits | Fits | Fits |
| Qwen3-32B | 32B | No | Q4_K_M | Tight (~20 GB) | Fits | No (~20 GB)* | Fits |
| Qwen3-30B-A3B | 30B total / 3B active | Yes | Q4_K_M | Fits (~20 GB) | Fits | Fits (~20 GB) | Fits |
| Qwen3-235B-A22B | 235B total / 22B active | Yes | Q4_K_M | No | Fits (~130 GB) | No | Tight (~130 GB) |

*Qwen3-32B Q4_K_M sits at ~20 GB; fits on RTX 4090 with minimal KV cache.

**Newer Qwen releases:** Alibaba shipped Qwen3.5 (Feb 2026, native vision-language, up to 397B-A17B MoE) and Qwen3.6 (April 2026, includes a dense 27B that targets single-consumer-GPU agentic coding). Sizing mechanics are the same as Qwen3 — MoE active-parameter footprint or dense parameter count at your chosen quant — but confirm GGUF/Ollama/LM Studio support has landed for the specific point release before recommending it; community GGUF conversions for a new architecture can lag the official release by weeks. Verify at https://huggingface.co/Qwen and https://ollama.com/library.

---

## DeepSeek Family

DeepSeek is one of the most-run local model families in 2026, largely via two very different paths: the full frontier MoE (V3.x, R1) for teams with serious hardware, and the small R1-distill models for laptop-class use.

| Model | Params | MoE? | Quant | M3 36 GB | M4 128 GB | RTX 4090 | H100 80 GB |
|-------|--------|------|-------|----------|-----------|----------|------------|
| DeepSeek-R1-Distill-Qwen-7B | 7B | No | Q4_K_M | Fits (~5 GB) | Fits | Fits | Fits |
| DeepSeek-R1-Distill-Qwen-32B | 32B | No | Q4_K_M | Tight (~20 GB) | Fits | No (~20 GB, tight) | Fits |
| DeepSeek-R1-Distill-Llama-70B | 70B | No | Q4_K_M | No (>40 GB) | Fits (~40 GB) | No | Fits |
| DeepSeek-V3 / R1 (full) | 671B total / 37B active | Yes | Q4_K_M | No | Tight (~380 GB — multi-node or CPU offload) | No | No (single 80 GB card cannot hold it) |
| DeepSeek-V3.2 | 675B total / 37B active | Yes | Q4_K_M | No | No (needs ~380 GB+) | No | No (needs multi-GPU) |

Notes:
- **Distills are not the same model as R1.** The R1-Distill-* models are Qwen or Llama base models fine-tuned on R1 reasoning traces — they inherit R1's reasoning *style*, not its full capability. Set user expectations accordingly; do not market a 7B distill as "DeepSeek R1 quality."
- **Full V3/R1-class MoE does not fit on any single-GPU consumer or single-H100 setup at usable quant.** Effective total footprint at Q4_K_M is roughly 380–420 GB; realistic local paths are (a) a multi-GPU/multi-node cluster, (b) aggressive CPU+GPU offload via llama.cpp (slow, but functional on a high-RAM workstation, e.g. 512 GB DDR5 host RAM with a single GPU for hot experts), or (c) an even more aggressive sub-2-bit dynamic quant from providers like Unsloth — verify quality on your eval set before trusting these.
- GGUF conversions for DeepSeek's MoE routing lag a few points behind the safetensors original on generation benchmarks; expect a small (~5-10%) quality/throughput gap, not equivalence.
- License: DeepSeek-V3.2 and R1 weights are MIT-licensed — among the most permissive of the frontier-scale open releases, which is part of why they proliferate in local-inference guides. Verify current license terms at the model card before redistributing.
- Verify current releases and GGUF availability at https://huggingface.co/deepseek-ai and community requantizers (e.g. unsloth, bartowski, ubergarm).

---

## Mistral Family

| Model | Params | MoE? | Quant | M3 36 GB | M4 128 GB | RTX 4090 | H100 80 GB |
|-------|--------|------|-------|----------|-----------|----------|------------|
| Ministral 3B / 8B | 3B / 8B | No | Q4_K_M | Fits | Fits | Fits | Fits |
| Mistral 3 14B (dense) | 14B | No | Q4_K_M | Fits (~9 GB) | Fits | Fits | Fits |
| Mistral Large 3 | 675B total / 41B active | Yes | Q4_K_M | No | No (needs ~380 GB+) | No | No (needs multi-GPU) |

Notes:
- Mistral 3 (small dense 3B/8B/14B) and Mistral Large 3 (MoE, Dec 2025) are Apache 2.0. The small dense tier is the locally-relevant one for laptop/workstation use; Large 3 has the same multi-GPU reality as DeepSeek-V3-class MoE above.
- Mistral Large 3 supports long context (256K) and image understanding — useful when a single self-hosted endpoint needs to serve both text and vision workloads without swapping models.
- Verify current releases at https://mistral.ai/news and https://huggingface.co/mistralai before quoting sizes or license terms.

---

## Gemma 4 Family

Released April 2, 2026 (Apache 2.0). Encoder-free multimodal architecture (text, image, audio, video input). Reference: https://ai.google.dev/gemma/docs/releases

| Model | Params | Quant | M3 36 GB | M4 128 GB | RTX 4090 | H100 80 GB | Notes |
|-------|--------|-------|----------|-----------|----------|------------|-------|
| Gemma 4 12B (BF16) | 12B | BF16 | Fits (~16 GB) | Fits | No (>24 GB) | Fits | Minimum 16 GB unified memory for BF16 |
| Gemma 4 12B (QAT) | 12B | QAT (~Jun 2026) | Fits (~4–5 GB est.) | Fits | Fits | Fits | QAT weights cut memory ~72% vs BF16; verify exact size at release page |

Notes:
- QAT = Quantization-Aware Training; Google released QAT weights June 5, 2026 — verify current download at https://ai.google.dev/gemma/docs/releases.
- `ollama pull gemma4` is the standard local path; LM Studio also supports Gemma 4.
- QAT size estimates are indicative (~72% reduction vs BF16 ≈ ~4.5 GB); measure on your hardware.

---

## GPT-OSS (OpenAI open-weight releases, August 2025)

Note: "GPT-OSS" in this section refers specifically to the two MoE models OpenAI released in August 2025 under Apache 2.0, not to GPT-4 or GPT-4o (weights for those remain unreleased). These are distinct from GPT-2 and community forks.

| Model | Params (total / active) | Quant | M3 36 GB | M4 128 GB | RTX 4090 | H100 80 GB | Notes |
|-------|------------------------|-------|----------|-----------|----------|------------|-------|
| gpt-oss-20b | 21B total / 3.6B active | BF16 | Fits | Fits | Fits | Fits | MoE; optimized for low latency and local use |
| gpt-oss-120b | 117B total / 5.1B active | BF16 | No | Fits | No (>24 GB) | Fits (single 80 GB) | MoE; targets single 80 GB GPU for production |
| GPT-2 XL | 1.5B | BF16 | Fits | Fits | Fits | Fits | Legacy; included for completeness |

Notes:
- gpt-oss models use OpenAI's "harmony response format" — verify format compatibility with your inference stack before deploying.
- gpt-oss models support MXFP4 quantization; actual VRAM requirements under MXFP4 will be lower than BF16 above.
- Verify current weights and license terms at https://huggingface.co/openai before deployment.

---

## Hardware-specific notes

### M3 / M4 Apple Silicon (unified memory)

**Inference paths:**
- **Ollama / llama.cpp (GGUF):** Simplest daemon-based path. Uses Metal automatically. Best for most local-use cases.
- **LM Studio:** GUI frontend over llama.cpp/MLX. Supports both GGUF and MLX model formats natively — pick MLX models from HuggingFace for best Metal throughput.
- **MLX (Apple's framework):** Framework-level Python library targeting Apple Silicon Metal. Use MLX when you need: (a) LoRA fine-tuning on-device, (b) custom generation pipelines, (c) model-level control not exposed by daemon runtimes. Quantization and LoRA adapters are supported natively. Verify current release and model support at https://github.com/ml-explore/mlx-lm.

**Unified memory advantage:** RAM and VRAM share the same pool — no PCIe bandwidth bottleneck. Context length is the main constraint; KV cache scales linearly with sequence length.

**M4 Max with 128 GB** can run 70B Q4 comfortably at 2–4k context. With KV-cache quantization (Q8_0 KV), effective context can extend to 16k+ on 70B models.

### RTX 4090 (24 GB GDDR6X)
- Most efficient at 7–13B quant models; 34B models require Q2/Q3 or model sharding.
- Flash Attention 2 gives significant throughput boost for long contexts.
- For models that don't fit, use llama.cpp with CPU offload (slower but functional).
- FP8 support is limited on Ada Lovelace (RTX 4090): partial FP8 emulation available but throughput gain is smaller than on H100 or RTX 50-series Blackwell. Prefer Q4_K_M or Q8_0 quantization paths on this card.

### H100 80 GB
- The reference tier for single-card production inference.
- Supports bfloat16 for 70B models without quantization.
- TensorRT-LLM or vLLM with PagedAttention recommended for production serving.
- Use FP8 quantization on H100 for 70B+ with minimal quality loss.

### RTX 50-series / Blackwell (e.g. RTX 5090, RTX 5080)
- Native FP8 support: Blackwell GPUs natively support FP8, eliminating the emulation overhead seen on Ampere. FP8 throughput improvement vs FP16 is larger on Blackwell than on RTX 4090.
- RTX 5090 VRAM: 32 GB GDDR7 — fits most 30–34B Q4_K_M models and allows modest FP8 experiments on smaller dense models.
- Verify driver and framework support: FP8 paths in vLLM, TensorRT-LLM, and llama.cpp may have Blackwell-specific branches; check current release notes before deploying FP8 on RTX 50-series.

---

## Throughput Estimates (tokens/sec, generation)

Estimates at ~2k context, batch size 1. Highly dependent on implementation.

| Model | Quant | M3 36 GB | RTX 4090 | H100 80 GB |
|-------|-------|----------|----------|------------|
| 7–8B | Q4_K_M | 30–50 | 80–120 | 150–250 |
| 13–14B | Q4_K_M | 15–25 | 45–70 | 100–160 |
| 30–34B | Q4_K_M | 5–10 | 18–30 | 60–100 |
| 70B | Q4_K_M | — | — | 30–55 |
| MoE 17B active | Q4_K_M | 20–35 | 50–90 | 120–200 |

---

## Selection Heuristic

1. Start with the largest model that fits with 20% VRAM headroom for KV cache.
2. Prefer Q4_K_M over Q5_K_M unless you measure a meaningful quality gap on your eval set.
3. Use Q8_0 only if VRAM permits — quality is near-lossless but doubles memory vs Q4.
4. For MoE models, active VRAM matters more than total parameters.
5. If throughput is the bottleneck and you have an H100, use FP8 or BF16 before quantizing.

See `references/quantization-format-table.md` for format details.

---

## Local vs API: The Real Tradeoff

The honest comparison is rarely "quality" in isolation — it's total cost of ownership against the constraint that actually matters.

**Local wins when:**
- Data cannot leave the premises (regulatory, contractual, or trust reasons) — this is the strongest and most common real justification.
- Offline or air-gapped operation is a hard requirement, not a nice-to-have.
- Request volume is high and steady enough that a $2–4k GPU or Apple Silicon workstation amortizes below API cost within months — do the arithmetic on your actual token volume, not a vendor's marketing comparison.
- Latency needs to be sub-100ms and the model fits comfortably in VRAM with headroom (no CPU offload, no cold starts).
- The task is narrow enough that a 7–32B open model, properly evaluated, already matches frontier-API quality on it (classification, extraction, short-form generation, code-adjacent completion).

**API (hosted frontier) wins when:**
- The task needs frontier-tier reasoning, long-context coherence, or tool-use reliability that open-weight models at a size you can actually run locally do not yet match — this gap has narrowed a lot since 2024 but has not closed, especially for multi-step agentic tasks.
- Traffic is spiky or low-volume — a always-on local GPU is dead capital between bursts; pay-per-token is cheaper below a threshold that depends on your GPU cost and utilization.
- You need the frontier model's context window (1M+) rather than what fits in local VRAM.
- Engineering time for local ops (driver issues, quant regressions, model updates, capacity planning) costs more than the API bill would.

**The trap to avoid in both directions:** "Local" is not automatically cheaper (hardware, power, and your own ops time are real costs) and "hosted API" is not automatically higher quality on your specific task (a well-evaluated small local model can beat a poorly-prompted frontier model on a narrow job). Decide with a real eval set and a real cost model, not vibes or vendor benchmarks.
