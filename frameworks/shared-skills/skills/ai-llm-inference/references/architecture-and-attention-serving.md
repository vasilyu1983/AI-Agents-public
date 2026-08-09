# Architecture and Attention Serving

Serving-time limitation → workaround reference for transformer architecture variants, attention mechanisms, and inference bottlenecks not covered by the KV-cache, quantization, speculative-decoding, batching, queueing, disaggregation, or routing depth files. Cross-links to those files are provided in each section and in the Routing to Depth index at the end.

---

## Table of Contents

- [1. Attention Variants and KV Cache Footprint](#1-attention-variants-and-kv-cache-footprint)
- [2. SSM and Hybrid Model Serving](#2-ssm-and-hybrid-model-serving)
- [3. Roofline and Arithmetic Intensity](#3-roofline-and-arithmetic-intensity)
- [4. Long-Context Serving Workarounds](#4-long-context-serving-workarounds)
- [5. RoPE Scaling at Serve Time](#5-rope-scaling-at-serve-time)
- [6. Activation Outliers and W8A8 Quantization](#6-activation-outliers-and-w8a8-quantization)
- [7. Draft-Model-Free Speculative Decoding](#7-draft-model-free-speculative-decoding)
- [8. FlashAttention Decode vs Prefill Profile](#8-flashattention-decode-vs-prefill-profile)
- [Routing to Depth](#routing-to-depth)

---

## 1. Attention Variants and KV Cache Footprint

### Limitation

KV cache memory scales with the number of KV heads: `2 × num_layers × num_kv_heads × head_dim × seq_len × dtype_bytes`. Multi-Head Attention (MHA) stores one K and V tensor per query head; at large model scale this dominates GPU memory and limits batch size. See [kv-cache-optimization.md](kv-cache-optimization.md) for the full size formula and memory breakdown.

### Variant Overview

| Attention type | KV heads | Relative KV bytes/token | Quality trade-off | Runtime support |
|---|---|---|---|---|
| **MHA** (standard) | = num_query_heads | 1× (baseline) | Highest quality | Universal |
| **MQA** (multi-query) | 1 | ~1/num_heads (8-32×) | Noticeable quality / stability cost on some tasks | Most modern runtimes; verify per-model |
| **GQA** (grouped-query) | 4–8 (configurable) | ~4–8× reduction vs MHA | Near-MHA quality at 4–8 groups; the dominant default | Universal; default in Llama 3/Mistral/Gemma 2+ |
| **MLA** (multi-head latent) | Latent-compressed | ~2.7–4.7× vs comparable GQA models (DeepSeek-V3 ≈ 70 KB/token) | Competitive with MHA in reported evals; some instability on edge cases — verify current | Requires runtime support for latent-space KV and decoupled RoPE; mainstream in vLLM now — confirm your runtime version |

**MQA**: Proposed by Shazeer (2019). Maximum cache compression but measurably degrades quality and generation stability compared to MHA; rarely used in new flagship models. Favoured in early-generation fast-inference models (e.g., Falcon-7B).

**GQA**: Introduced by Ainslie et al. (2023). Groups query heads to share a smaller set of KV heads. Llama 3 (8/70B), Mistral 7B v0.3+, Gemma 2, Qwen 2.5 all default to GQA with 8 KV groups. The 4–8× cache reduction compared to MHA (at the same num_layers and head_dim) is the primary reason these models are memory-efficient to serve.

**MLA** (DeepSeek-V2/V3/R1): Projects K and V into a shared low-rank latent vector before storage, then reconstructs at decode time. The latent is small — DeepSeek-V3 stores **576 dims/token** (512 KV-latent + 64 for the decoupled RoPE key), caching **~70 KB/token vs ~192–328 KB/token for comparable GQA models** (LLaMA-3.1 405B ≈ 516 KB, Qwen-2.5 72B ≈ 327 KB) — roughly a **2.7–4.7× reduction**. The catch: decoupled RoPE (position encoding applied after the latent projection, not before) requires runtime-level support. Standard vLLM MLA support landed in 2024–2025 and is now mainstream; still confirm your runtime version's MLA path before deploying. (Per-token bytes are architecture-specific — check the current DeepSeek technical report for exact per-model numbers.)

### Decision Table

| Deployment goal | Attention type to target | Notes |
|---|---|---|
| Maximize KV cache capacity for batching | GQA (8 groups) or MLA | GQA is the safe default; MLA needs runtime confirmation |
| Use a pre-trained model as-is | Whatever the checkpoint was trained with | Changing attention type requires architectural changes + retraining |
| Memory-constrained single-GPU serving | GQA + FP8 KV cache | Stacking: see [kv-cache-optimization.md](kv-cache-optimization.md) §KV Cache Quantization |
| Million-token+ contexts | MLA or GQA + offload + disaggregation | See §4 below and [disaggregated-inference.md](disaggregated-inference.md) |

**Cross-link**: [kv-cache-optimization.md](kv-cache-optimization.md) for the sizing formula, PagedAttention block management, and FP8 KV cache configuration.

---

## 2. SSM and Hybrid Model Serving

### Limitation

Pure Transformer decoders maintain an O(n) KV cache that grows with sequence length. At long context this is both memory-expensive and bandwidth-expensive to load per decode step.

### Workaround: SSMs and Hybrids

State space models (SSMs) — Mamba-1/2/3 and derivatives — replace attention layers with a recurrent operator that carries a **fixed-size state** regardless of sequence length. The per-layer memory footprint is O(1) in context length rather than O(n).

**Serving implications**:

| Property | Pure Transformer | SSM layer | Hybrid (e.g., Jamba, Granite 4, Nemotron-H, Mamba-Attention hybrids) |
|---|---|---|---|
| Memory per token (decode) | Grows with context | Fixed state size | Mixed: attention layers grow, SSM layers fixed |
| Prefill cost | O(n²) attention | O(n) recurrent scan | Mixed: attention blocks still O(n²) for their layers |
| KV cache admission control | Must size for max context × batch | SSM layers need no KV allocation | Must size KV budget only for attention layer count |
| Quantization of state | Standard KV quant | State quantization (different distribution) | Apply separately per layer type |

**Key limitation — pure SSM in-context recall**: Pure SSMs have weaker in-context recall than Transformers on tasks requiring exact retrieval of earlier tokens (e.g., retrieval-augmented generation with long documents, multi-hop reasoning). This is a structural trade-off of fixed-state compression. Only hybrid models (SSM + attention layers interleaved) are competitive with pure Transformers on benchmarks that test long-range recall. Verify current benchmark comparisons before selecting a pure SSM for recall-heavy workloads.

**Workaround for long-context cost**: Use hybrids (Jamba, Granite 4, Nemotron-H, or similar) where most layers are SSM (cheap) and a smaller fraction are full attention (expensive, cached). This delivers near-linear memory scaling while preserving recall quality for the attention layers. The trade-off: smaller KV budget still required for the attention layers; prefill for those layers still scales quadratically.

**Admission control**: Because SSM layers don't consume KV slots, standard KV-capacity-based admission control (common in vLLM) may need tuning when serving hybrids. The maximum batch size is bounded by attention-layer KV budget, not total layer count.

**Runtime support**: Verify SSM and hybrid model support in your chosen runtime before planning. vLLM added Mamba-2 support; SGLang hybrid support status varies — check current release notes. (Verify current — SSM kernel availability and correctness is an active development area as of mid-2026.)

---

## 3. Roofline and Arithmetic Intensity

### Mental Model

GPU performance is bounded by two ceilings: compute (FLOPs/s) and memory bandwidth (bytes/s). Which one limits you depends on **arithmetic intensity**: FLOPs per byte of data moved.

```
Arithmetic intensity = FLOPs / bytes accessed

If intensity < ridge point → memory-bandwidth-bound (roofline left slope)
If intensity > ridge point → compute-bound (roofline plateau)

H100 SXM5 ridge point: ~295 FLOPs/byte (HBM β≈3.35 TB/s, FP16 π≈990 TFLOP/s)
```

### The Decode Problem

During autoregressive decode at small batch size, each step loads all model weights once to produce a single token. Weight loading is ~2 FLOPs per byte (one multiply-add per weight element). This is far below the H100 ridge point.

```
Decode at batch=1:   ~2 FLOPs/byte → deeply memory-bandwidth-bound
Decode at batch=16:  ~32 FLOPs/byte → still memory-bandwidth-bound
Decode at batch=128: ~256 FLOPs/byte → approaching compute-bound
Decode at batch=150+: crosses ridge point → compute-bound on H100-class hardware
(exact crossover depends on model size, TP degree, and precision — treat as order-of-magnitude)
```

**Prefill** processes a full prompt in parallel. With long prompts and large batch, arithmetic intensity is high (each attention computation reuses weights across many tokens) → prefill is often compute-bound.

### Practical Decisions This Drives

| Observation | Decision |
|---|---|
| Decode latency not improving when adding compute (e.g., bigger GPU tier) | You are memory-bandwidth-bound. More FLOPs don't help; more bandwidth does. |
| TP (tensor parallelism) reduces decode latency | TP splits weight matrices across GPUs → each GPU loads a smaller slice → lower per-step bandwidth cost. This is the main per-token latency benefit of TP, not compute parallelism. |
| Throughput increases with batch size but latency stays constant (then rises) | Expected. Batching amortizes bandwidth cost → higher tokens/s without changing the per-step load time until the batch crosses the compute-bound ridge. |
| Small batch, memory-bandwidth-limited → KV cache quantization or model quantization help | Lower dtype → fewer bytes to load per step → lower memory-bandwidth cost per token. |
| Can't reach the ridge point regardless of batch | The weight matrix is too large for the available bandwidth. Consider model compression, TP, or a smaller model. |

**When you are guaranteed memory-bound**: Any single-user, low-QPS, interactive serving workload. No caching optimization or batching trick can make a batch-1 decode compute-bound on a standard Transformer.

**Cross-link**: [queueing-theory-applied.md](queueing-theory-applied.md) for continuous batching mechanics, queue sizing, and why batching improves throughput even when it can't reduce per-token latency at small concurrency.

---

## 4. Long-Context Serving Workarounds

Serving contexts beyond model training length or beyond GPU memory capacity requires explicit architectural intervention. Each technique below trades memory for fidelity or hardware.

### 4a. StreamingLLM / Attention Sinks

**Limitation**: Standard KV caches for contexts of hundreds of thousands of tokens exceed a single GPU's HBM. Without eviction, decode stalls or OOMs.

**Workaround**: Keep a small window of "sink" tokens at the start of the sequence (the first 4–16 tokens, which the model attends to regardless of content) plus a sliding window of recent tokens. Evict everything in the middle.

| Property | Value |
|---|---|
| Memory footprint | Fixed (sink size + window size), regardless of total stream length |
| Effective context | Theoretically infinite streams |
| Fidelity cost | **Loses access to middle context.** The model cannot retrieve facts or instructions placed in the middle of a very long stream. Suitable for live-transcription, streaming agents, open-ended conversation — not for RAG or document summarization that requires mid-document recall. |
| Runtime support | Verify in your runtime. Not universally supported natively; may require custom attention kernel. |

**When to use**: Low-memory deployments streaming indefinitely (live support agents, long-running tool-use loops) where mid-context recall is not required.

### 4b. Sliding-Window Attention Serving

**Limitation**: Full causal attention over very long contexts is quadratic in compute and linear in KV memory per layer.

**Workaround**: Restrict each token's attention to the most recent W tokens (window size). Each layer's KV cache is bounded at W rather than n.

| Property | Value |
|---|---|
| Memory per layer | O(W) not O(n) |
| Fidelity cost | Tokens outside the window are invisible to local attention. Models trained with SWA (e.g., Mistral v0.1 SWA variant) learn to propagate long-range information through layers; zero-shot application of a window to a standard MHA model degrades quality significantly. |
| Serving requirement | The model must have been trained or fine-tuned with sliding-window attention. Do not apply SWA post-hoc to a standard MHA checkpoint. |

**When to use**: Models explicitly trained with SWA (Mistral 7B v0.1 SWA layer, Gemma SWA variants). Check model cards before assuming this is applicable.

### 4c. Ring Attention (Sequence Parallelism for >1M Context)

**Limitation**: Even with GQA and FP8 KV cache, 1M+ token contexts exceed a single node's HBM for most large models.

**Workaround**: Ring Attention (Liu et al., 2023) partitions the sequence across GPUs. Each GPU holds a contiguous chunk of the sequence and its corresponding KV entries. GPUs pass KV blocks around a logical ring while computing attention over local Q chunks. Net effect: attention computation and KV memory scale with number of GPUs, not per-GPU memory.

| Property | Value |
|---|---|
| Memory scaling | O(n / num_gpus) per GPU KV cache |
| Compute overhead | All-reduce-equivalent ring communication cost per layer; scales with interconnect bandwidth (NVLink-scale required for practical use) |
| Fidelity | Exact attention; no approximation |
| Serving requirement | Sequence-parallel framework support; not available in standard vLLM as of mid-2026 — verify current. More common in training frameworks (Megatron-LM, DeepSpeed Ulysses); production inference support is emerging. |

**When to use**: Research-scale or specialized deployments requiring exact attention at >512k–1M tokens where ring-communication overhead is acceptable. For most production multi-GPU serving, prefer TP + GQA + FP8 KV + offload tiers first (see [kv-cache-optimization.md](kv-cache-optimization.md)).

**Cross-link**: [kv-cache-optimization.md](kv-cache-optimization.md) §KV Cache Offloading and §Sequence Parallelism for the 3-tier offload model and Megatron-LM TP patterns.

---

## 5. RoPE Scaling at Serve Time

### Limitation

Rotary Position Embeddings (RoPE) encode absolute position. Models trained up to context length C exhibit perplexity blowup when served at lengths > C because the rotation frequencies are outside the trained distribution. This is a common production trap: the model loads, generates, and returns output — but quality degrades silently or catastrophically for positions beyond the trained context.

### Workarounds

Three main scaling methods exist. The method used at **fine-tuning** must match what is applied at **serve time**; mismatching is the most common misconfiguration.

| Method | What it does | When to use | Misconfiguration risk |
|---|---|---|---|
| **Linear PI (Position Interpolation)** | Scales all frequencies by a factor `s = C_target / C_train`, compressing positions into the trained range | When the fine-tune used linear PI | Applying to a model fine-tuned with YaRN frequencies degrades quality |
| **NTK-aware scaling** | Scales frequencies non-linearly, preserving high-frequency components while stretching low-frequency ones | When the fine-tune used NTK-aware scaling; better out-of-distribution generalization than linear PI for some models | Same mismatch risk |
| **YaRN** (Yet Another RoPE extensioN) | Combines NTK-aware interpolation with attention temperature scaling; often the highest quality option for long-context fine-tuned models | When the fine-tune used YaRN; Llama 3.1+ long-context variants typically use YaRN | Forgetting to set the YaRN scale factor in serving config; some runtimes require explicit flags |

### Validation Step

After enabling any RoPE extension at serve time:

1. Generate at the target extended context length.
2. Compare perplexity or task accuracy on a fixed long-context benchmark against the model's reported performance at that context length.
3. If perplexity is higher than expected or outputs degrade near the context boundary, the scaling method or scale factor is likely wrong.
4. Check your runtime's configuration flag for RoPE scaling explicitly — not all runtimes auto-detect the correct method from the model config. (Verify current: vLLM and SGLang both have `rope_scaling` config parameters — confirm the expected format for your runtime version before deploying.)

**Common production trap**: Deploying a fine-tuned 128k-context model without setting the runtime's `rope_scaling` config. The model generates without error for short prompts and silently degrades on long ones.

---

## 6. Activation Outliers and W8A8 Quantization

### Limitation

Weight-only quantization (AWQ, GPTQ — see [quantization-patterns.md](quantization-patterns.md)) keeps activation tensors in FP16/BF16, which avoids the activation outlier problem but limits kernel efficiency: weights and activations must be cast for every operation. W8A8 (INT8 weights and INT8 activations) enables native INT8 GEMM, which is faster on hardware with INT8 tensor cores, but transformer activations contain a small fraction of extremely large-magnitude values in specific hidden-state channels ("outliers").

**The outlier problem**: If you naively quantize activations to INT8, these large-magnitude channels clip, causing large quantization error and significant quality degradation. This is particularly severe for certain model families (LLaMA-1, OPT) and less severe for models trained with explicit quantization awareness.

### Workaround: SmoothQuant

SmoothQuant (Xiao et al., 2022) migrates the quantization difficulty from activations to weights via per-channel scaling.

```
For each channel c:
  scale_c = (max |activation_c|) ^ α / (max |weight_c|) ^ (1 - α)
  activation_c' = activation_c / scale_c      ← smoothed activation (easier to quantize)
  weight_c'     = weight_c × scale_c          ← compensated weight (absorbs the scaling)
```

The activations become smoother (lower dynamic range), and the weights absorb the scaling. Both can then be quantized to INT8 within acceptable error. The `α` hyperparameter (typically 0.5) controls how much difficulty to migrate to weights.

**Key requirement**: SmoothQuant calibration uses a small set of representative inputs to determine per-channel scales. The calibration set must match the deployment distribution. Calibrating on a mismatched dataset (e.g., generic text for a code-serving model) degrades results.

| W8A8 step | What can go wrong | Mitigation |
|---|---|---|
| Collecting calibration data | Distribution mismatch → bad per-channel scales | Use production-representative samples |
| Running SmoothQuant | `α` too high → weights too large to quantize | Tune α; start at 0.5 |
| Runtime integration | INT8 GEMM kernel not enabled → no speedup | Verify runtime supports W8A8 INT8 natively (TensorRT-LLM SmoothQuant, vLLM W8A8 path — see [quantization-patterns.md](quantization-patterns.md)) |
| Post-quantization validation | Outlier channels in this specific model | Run long-context and edge-case evals; compare against FP8 or weight-only INT8 |

**When SmoothQuant fails**: Some models have activation distributions that cannot be migrated cleanly even with tuned α. If post-calibration quality is still insufficient, prefer FP8 (which avoids the W8A8 outlier problem entirely on supported hardware) or weight-only INT8 as a fallback.

**Cross-link**: [quantization-patterns.md](quantization-patterns.md) for the full runtime-scoped quantization decision table, KV cache quantization, and the validation checklist.

---

## 7. Draft-Model-Free Speculative Decoding

### Limitation

Standard draft-model speculative decoding (EAGLE, separate small model — see [speculative-decoding-guide.md](speculative-decoding-guide.md)) requires a draft model that fits alongside the target model in memory. This doubles VRAM pressure and introduces a dependency on a compatible draft checkpoint being available.

### Workaround: N-gram / Lookahead Decoding

Instead of a learned draft model, propose candidate tokens by matching n-gram patterns from the **current context itself** (a trie or sliding n-gram index built from the context window and any retrieved documents).

| Property | Value |
|---|---|
| Extra memory | Minimal — only the n-gram index (proportional to context length) |
| Extra model loading | None |
| Acceptance rate — repeated text (code, RAG, boilerplate) | High: often 60–80%+ in favorable conditions |
| Acceptance rate — novel or creative text | Near zero: n-gram proposals are not useful when the continuation does not repeat prior context |
| Speedup ceiling | Lower than draft-model methods on diverse text; competitive on repetitive text |
| Runtime support | n-gram/lookahead is in vLLM; SGLang uses tree attention for speculation. Note the broader spec-decode landscape has matured: **EAGLE-3 is now production-standard across vLLM, SGLang, and TensorRT-LLM** (2–3×), and **P-EAGLE** (parallel draft) landed in vLLM (2026). Confirm your runtime version's flags. |

### Position vs Draft-Model Families

| Method | Memory overhead | Best workload | Worst workload |
|---|---|---|---|
| N-gram / lookahead | ~0 | RAG, code generation, templated outputs, long documents with repetition | Creative generation, diverse chat |
| EAGLE / Medusa / draft model | 10–40% extra for draft model/heads | General text, chat, coding with diverse outputs | Memory-constrained deployments |
| MTP (native heads) | Minimal (heads trained into model) | Models with native MTP (DeepSeek-V3) | Models without native MTP support |

**Cross-link**: [speculative-decoding-guide.md](speculative-decoding-guide.md) for the full EAGLE, MTP, draft-model, and Medusa coverage, deployment checklist, and failure mode analysis.

---

## 8. FlashAttention Decode vs Prefill Profile

### Limitation

FlashAttention is widely described as the standard attention kernel — but its benefit profile differs substantially between the prefill and decode phases. Over-attributing decode latency to attention compute leads to misdiagnosis and wasted optimization effort.

### FA's Benefit: Predominantly Prefill

During **prefill**, the input sequence (potentially thousands of tokens) produces a large attention matrix. This computation is:
- IO-intensive: the attention matrix can exceed L2 cache → HBM reads dominate without fusion
- Compute-intensive at long sequence: O(n²) FLOPs for full causal attention

FlashAttention's tiled, IO-aware kernel avoids materializing the full n×n attention matrix in HBM, reducing memory bandwidth cost and enabling kernel fusion. The speedup is largest here.

### Decode: A Different Bottleneck

During single-query **decode** (batch=1 to batch~16), each step produces attention over the full KV cache but for only one or a few query tokens. This means:
- Attention FLOPs are small (1 query × n KV)
- The bottleneck is **weight loading bandwidth**, not attention compute (see §3 above)
- FlashAttention's tiling benefit is smaller — attention is already fast relative to weight loads

```
At small batch decode:
  Weight load cost >> Attention compute cost
  → FlashAttention speedup in decode is marginal

At large batch decode (batch >> 64):
  Weight load is amortized, attention grows
  → FlashAttention benefit increases proportionally
```

### FlashInfer Decode Kernels

FlashInfer (MLSys 2025) was developed specifically to address the decode profile: its kernels are optimized for the KV-cache read pattern of decode — where the access is across a paged, fragmented cache — rather than the contiguous-matrix pattern of prefill. Decode with FlashInfer has shown measurably lower inter-token latency compared to generic FA-2/FA-3 kernels on decode workloads (verify current benchmarks for your hardware/runtime combination).

**Practical guidance**:

| Phase | Primary bottleneck | What helps |
|---|---|---|
| Prefill (long prompt, any batch) | Attention IO + compute | FlashAttention-3, fused kernels, TP to split work |
| Decode (small batch < ~32) | Weight loading bandwidth | TP to reduce per-GPU weight size, quantization to reduce bytes/weight, batching to amortize |
| Decode (large batch > ~128) | Attention + weight both matter | FlashInfer decode kernels, FA-3, batching, TP |

**What not to do**: Profile latency on a combined prefill+decode benchmark, see high numbers, and tune the attention kernel — only to find decode latency unchanged because the bottleneck was weight bandwidth.

**Cross-link**: [kv-cache-optimization.md](kv-cache-optimization.md) §FlashAttention-3 and FlashInfer for FA evolution history, GPU utilization figures, and FlashInfer integration notes with vLLM and SGLang.

---

## Routing to Depth

This file covers architecture-level serving trade-offs. For deeper production detail on each adjacent topic:

| Topic | Primary reference |
|---|---|
| KV cache sizing, PagedAttention, prefix caching, FP8 KV, offload tiers, FlashAttention | [kv-cache-optimization.md](kv-cache-optimization.md) |
| Quantization: FP8, AWQ, GPTQ, W8A8, KV quant, runtime decision table | [quantization-patterns.md](quantization-patterns.md) |
| Speculative decoding: EAGLE, MTP, draft model, Medusa, deployment checklist | [speculative-decoding-guide.md](speculative-decoding-guide.md) |
| Batching strategies, continuous batching, chunked prefill | [batching-and-scheduling.md](batching-and-scheduling.md) |
| Queue sizing, Little's Law, Kingman, admission control, backpressure | [queueing-theory-applied.md](queueing-theory-applied.md) |
| Prefill/decode disaggregation, encoder disaggregation, when to split | [disaggregated-inference.md](disaggregated-inference.md) |
| Multi-model routing, cascade routing, cache-aware placement | [multi-model-routing.md](multi-model-routing.md) |
