# Quantization Patterns for Current Inference Stacks

Choose quantization inside the runtime you will deploy. Hardware capability matters, but engine support and model support decide what is actually usable.

## Table of Contents

- [Why Quantization Works And Where It Breaks](#why-quantization-works-and-where-it-breaks)
- [Core Rules](#core-rules)
- [Runtime Support Snapshot](#runtime-support-snapshot)
- [Decision Table](#decision-table)
- [Runtime-Specific Notes](#runtime-specific-notes)
- [NVFP4 / MXFP4 in 2026](#nvfp4--mxfp4-in-2026)
- [KV Cache Quantization](#kv-cache-quantization)
- [Validation Checklist](#validation-checklist)
- [Primary Sources](#primary-sources)

## Why Quantization Works And Where It Breaks

- **What it buys.** Decode at low batch is memory-bandwidth-bound; prefill and high-batch decode are compute-bound. Weight-only quantization shrinks bytes read per token, so it speeds decode and does comparatively little for prefill or high-batch throughput. If your bottleneck is prefill, expect the win to be memory footprint, not latency.
- **Why it breaks: outlier channels.** A few activation channels carry magnitudes far above the rest, so a per-tensor scale sized for them wastes the grid on everything else. Three documented responses: LLM.int8() ([arXiv 2208.07339](https://arxiv.org/abs/2208.07339)) uses a "mixed-precision decomposition scheme, which isolates the outlier feature dimensions into a 16-bit matrix multiplication while still more than 99.9% of values are multiplied in 8-bit"; SmoothQuant ([arXiv 2211.10438](https://arxiv.org/abs/2211.10438)) migrates activation difficulty into the weights; AWQ ([arXiv 2306.00978](https://arxiv.org/abs/2306.00978)) selects salient channels from *activation* statistics and applies "an equivalent transformation to scale the salient weight channels", no backprop or reconstruction.
- **Why smaller groups and rotations help.** Group (block) scaling gives each block its own scale, so one outlier ruins one block instead of the tensor — this is exactly the NVFP4-vs-MXFP4 block-size argument below. Rotations attack the same problem differently: QuaRot ([arXiv 2404.00456](https://arxiv.org/abs/2404.00456)) "rotates LLMs in a way that removes outliers from the hidden state without changing the output, making quantization easier", and SpinQuant ([arXiv 2405.16406](https://arxiv.org/abs/2405.16406)) opens with "Rotating activation or weight matrices helps remove outliers and benefits quantization", learning the rotation rather than fixing it. Both rely on rotations being output-invariant in full precision.

## Core Rules

- Prefer runtime-native precision paths before adding external conversion complexity.
- Separate weight quantization from KV cache quantization in both planning and validation.
- Treat structured outputs, tool calls, and long-context quality as first-class regression targets.
- Verify exact support on the runtime docs you will use in production.
- Storage is not speed: a smaller checkpoint lowers latency or cost only when decode is memory-bandwidth-bound and the runtime ships a kernel for that format. Otherwise you get the same tokens/sec from a smaller file.
- Do not gate on perplexity. Reasoning, schema-valid, and tool-call slices degrade before perplexity visibly moves.
- Quantization-aware training (simulating quantization during training) preserves more accuracy than post-training quantization but needs full training access. Reach for it only when the post-training result fails the quality gate.

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
| concurrency or context is the binding constraint (not weight footprint) | KV cache quantization first — KV cache, not weights, is usually what runs out at real concurrency, and KV quantization is usually the safer quality trade | shorter max context or fewer concurrent sequences |
| on-device NPU (mobile, embedded accelerators) | INT8, or INT4 where the NPU documents it, with **per-tensor** scales and static shapes — many NPU runtimes do not implement group/block scales at all | INT8 per-tensor, or fall back to CPU GGUF; see [../../ai-local-model-ops/SKILL.md](../../ai-local-model-ops/SKILL.md) |

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

## NVFP4 / MXFP4 in 2026

Both are 4-bit microscaling float formats, and they are **not interchangeable**. The difference is the block size and the format of the shared scale.

| Format | Block (group) size | Shared scale format | Extra level |
|---|---|---|---|
| **NVFP4** (NVIDIA) | 16 values | FP8 **E4M3** | plus a per-tensor FP32 scale |
| **MXFP4** (OCP microscaling standard) | 32 values | **E8M0** power-of-two | — |

NVIDIA's own description of NVFP4 is "4 bits (1 sign, 2 exponent, 1 mantissa) plus 1 shared FP8 scale per 16 value block", against MXFP4's "1 shared power-of-two scale per 32 value block"; NVIDIA attributes NVFP4's advantage to the halved block size giving "finer-grained scaling" and "more localized adaptation to the data's dynamic range". Practical read: E8M0 is pure exponent, so MXFP4's scale can only track magnitude in powers of two, while E4M3's mantissa bits let the scale land between them — which is why MXFP4 typically needs extra help to match NVFP4.

**Toy comparison of the two levers** (block size and scale format), run locally on `torch.randn(4096, 4096)` — a 15-level symmetric grid stands in for FP4, so absolute MSE is meaningless and only the ordering is informative:

```python
GRID = torch.linspace(-1, 1, 15)                                # 15-level stand-in for FP4
for block in (16, 32):
    for mode in ("e4m3", "e8m0"):
        xb = x.reshape(-1, block)
        amax = xb.abs().amax(1, keepdim=True)                   # per-block absmax
        s = (amax.to(torch.float8_e4m3fn).float() if mode == "e4m3"   # NVFP4-like scale
             else torch.pow(2.0, torch.ceil(torch.log2(amax))))       # MXFP4-like E8M0 scale
        q = GRID[((xb / s).clamp(-1, 1).unsqueeze(-1) - GRID).abs().argmin(-1)]
        print(f"block={block} {mode} MSE={torch.nn.functional.mse_loss(q * s, xb):.6f}")
```

Printed: `block=16 e4m3 MSE=0.007464`, `block=32 e4m3 MSE=0.009545`, `block=16 e8m0 MSE=0.017638`, `block=32 e8m0 MSE=0.022802`. Both levers move in the expected direction, and on this toy the *scale format* dominates the *block size*. Do not read magnitudes across to real FP4 kernels.

**Closing the MXFP4 gap — MR-GPTQ.** *"Bridging the Gap Between Promise and Performance for Microscaling FP4 Quantization"* ([arXiv 2509.23202](https://arxiv.org/abs/2509.23202), ICLR 2026) introduces **Micro-Rotated-GPTQ (MR-GPTQ)**, a GPTQ variant using "block-wise Hadamard transforms and format-specific optimizations". The authors state MR-GPTQ "matches or outperforms state-of-the-art accuracy, significantly boosting MXFP4, to the point where it can near the accuracy that of NVFP4", reporting "speedups vs. FP16 of up to 3.6x layer-wise, and 2.2x end-to-end on NVIDIA B200, and of 6x layer-wise and 4x end-to-end on RTX5090". Note those speedups are vs FP16 on the authors' setup, not a portable guarantee.

**NVFP4 PTQ scale initialisation.** Where the scale is *initialised* matters materially for 4-bit PTQ, and it is an active 2026 research line:

- **SOAR** ([arXiv 2605.12245](https://arxiv.org/abs/2605.12245)) — "Scale Optimization for Accurate Reconstruction in NVFP4 Quantization": closed-form joint optimization of global and block-wise scales, plus a decoupled discrete search over the dequantization scale. Authors report it "consistently outperforms existing NVFP4 quantization baselines" at equal memory footprint and with no extra hardware.
- **ScaleSweep** ([arXiv 2606.07618](https://arxiv.org/abs/2606.07618)) — "Accurate NVFP4 Post-Training Quantization of LLMs via Block Scale Initialization": sweeps feasible block-scale candidates and picks the one minimizing a target objective; authors report preserving "more than 93% of the full-precision performance" under aggressive quantization of weights, activations, KV cache, and query states.

Both are *PTQ* techniques — they change how you pick scales, not the format. Neither is a runtime feature you can enable; check whether your quantization toolchain implements them before planning around the numbers.

**FP4 for training (not just inference).** *"FP4 All the Way: Fully Quantized Training of LLMs"* ([arXiv 2505.19115](https://arxiv.org/abs/2505.19115)) demonstrates "for the first time, fully quantized training (FQT) of large language models (LLMs) using predominantly 4-bit floating-point (FP4) precision", reporting a "downstream task performance comparable to a standard BF16 baseline" for a 7B model trained on 256 Intel Gaudi2 accelerators. They also identify a practical floor: "when the gradient norm falls below approximately √3 times the quantization noise, quantized training becomes less effective". Relevant here mainly as context for why FP4 checkpoints are increasingly native rather than post-hoc.

**Accuracy recovery scales with model size.** Red Hat's NVFP4 measurements (published 2026-02-04) report recovery of BF16 accuracy improving with model size: "Large models (70B–235B) consistently achieve ~99% recovery", "Mid-size models (~30B) achieve 97–99% recovery", and "For 7B–14B models, NVFP4 recovers ~95–98% of BF16 accuracy across various tasks". They also note MoE models (Llama-4 Scout/Maverick, Qwen3-235B-A22B) "show exceptionally strong robustness", and put weight-storage reduction at "approximately ~3.3× vs BF16" and "roughly 1.5 to 1.8× smaller effective weight storage than FP8". These are one vendor's benchmark suite, and every figure is a *suite average* — the slices that decide production quality (long-context retrieval, code and math, non-English) are exactly the ones an average hides, so re-measure by slice, not by headline number. The direction (larger models recover more) is consistent with other reports as of Aug 2026; re-verify. Note the opposing pressure from pretraining: PTQ degradation grows with training tokens, so a heavily over-trained model can be *more* PTQ-fragile — see [../../ai-scaling-laws/references/post-chinchilla-developments.md](../../ai-scaling-laws/references/post-chinchilla-developments.md).

**Hardware gate:** full W4A4 NVFP4 needs Blackwell-class (SM100+) tensor cores; on older GPUs the same recipe degrades to weight-only, as already noted in the vLLM row above. Verified Aug 2026.

## KV Cache Quantization

Use KV cache quantization when long context or high concurrency makes cache memory the bottleneck.

How much it buys depends on the attention scheme, because it compresses a cache whose size the architecture already set: MHA holds the most KV bytes per token, GQA less, and MLA least of all — so MLA models (DeepSeek-V2/V3/V4) have the least left to win, and the lever may not be worth its quality risk there. See [kv-cache-optimization.md](kv-cache-optimization.md) for the sizing arithmetic.

Questions to answer:

- Does the runtime support the cache dtype on this hardware?
- Does long-context quality stay within tolerance?
- Does the larger batch size actually improve TTFT or throughput after queueing effects?

## Validation Checklist

Every item is a named metric against a **same-seed, same-prompt-set BF16/FP16 baseline**, with a numeric fail threshold and a revert rule. The thresholds below are **rules of thumb**, not measured constants — replace them with your own SLO before they gate anything.

- [ ] **One lever per rollout.** Weight format, KV dtype, and speculative decoding are three separate rollouts. Stacking them makes a regression unattributable; revert the whole stack if you stacked anyway.
- [ ] Baseline captured: BF16 run, fixed seed, frozen prompt set, all metrics below recorded before any quantized run.
- [ ] Runtime and version pinned, and the model verifiably loaded on the intended precision path (not a silent weight-only fallback).
- [ ] **Schema-valid rate** on a held-out structured-output/tool-call set — rule of thumb: revert on any absolute drop >1 point vs baseline. Leading indicator; it moves before generic quality does.
- [ ] **Long-context accuracy** at your real max context (retrieval/needle-style plus one real long-doc task) — rule of thumb: revert on >2 points absolute vs baseline.
- [ ] **p95 end-to-end latency** at production concurrency — rule of thumb: revert if p95 exceeds baseline p95 by more than 10%, even when throughput improved.
- [ ] Slice checks where weight-only formats are known to fail first: code/math and non-English — same >2-point rule of thumb, measured per slice, not on the average.
- [ ] Adapter and cache-heavy workloads re-tested if in scope (locality and reuse shift under quantization).
- [ ] **Revert rule written down before the rollout**, naming who reverts, the BF16 artifact to revert to, and the time budget for the decision.

## Primary Sources

- vLLM quantization docs: https://docs.vllm.ai/en/stable/features/quantization/
- vLLM INT8 W8A8: https://docs.vllm.ai/en/stable/features/quantization/int8.html
- TensorRT-LLM precision reference: https://nvidia.github.io/TensorRT-LLM/reference/precision.html
- SGLang quantization docs: https://docs.sglang.io/docs/advanced_features/quantization
- llama.cpp: https://github.com/ggml-org/llama.cpp
- NVIDIA: Introducing NVFP4 for Efficient and Accurate Low-Precision Inference: https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/
- NVIDIA Transformer Engine NVFP4 reference (block scaling): https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/features/low_precision_training/nvfp4/nvfp4.html
- Red Hat Developer: Accelerating large language models with NVFP4 quantization (2026-02-04): https://developers.redhat.com/articles/2026/02/04/accelerating-large-language-models-nvfp4-quantization
- LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale: https://arxiv.org/abs/2208.07339
- SmoothQuant: Accurate and Efficient Post-Training Quantization for LLMs: https://arxiv.org/abs/2211.10438
- AWQ: Activation-aware Weight Quantization: https://arxiv.org/abs/2306.00978
- QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs: https://arxiv.org/abs/2404.00456
- SpinQuant: LLM Quantization with Learned Rotations: https://arxiv.org/abs/2405.16406
- MR-GPTQ / microscaling FP4 (ICLR 2026): https://arxiv.org/abs/2509.23202
- SOAR: Scale Optimization for Accurate Reconstruction in NVFP4 Quantization: https://arxiv.org/abs/2605.12245
- ScaleSweep: NVFP4 PTQ via Block Scale Initialization: https://arxiv.org/abs/2606.07618
- FP4 All the Way: Fully Quantized Training of LLMs: https://arxiv.org/abs/2505.19115
