# Pruning and Sparsity for LLM Serving

Guidance for removing weights, structures, or activations from an LLM to make serving cheaper — one-shot post-training pruning, N:M semi-structured sparsity, structured pruning with distillation retraining, and contextual (activation) sparsity. The organising question is not "how much can we prune" but "which of these does the hardware and the runtime actually execute faster."

**Hedge note**: Runtime sparsity support is the least stable part of this reference and moved *backwards* during 2026 (see [Runtime Support](#runtime-support)). Paper-reported speedups are measured on the authors' kernels, models, and batch sizes — treat them as direction, not as a forecast for your deployment. Re-verify every runtime row against current docs before planning around it.

## Table of Contents

- [When to Use This Reference](#when-to-use-this-reference)
- [Intake Question](#intake-question)
- [Taxonomy: What Each Kind of Sparsity Actually Buys](#taxonomy-what-each-kind-of-sparsity-actually-buys)
- [One-Shot Post-Training Pruning](#one-shot-post-training-pruning)
- [Eval Gates Before Shipping a Pruned Model](#eval-gates-before-shipping-a-pruned-model)
- [N:M Semi-Structured Sparsity](#nm-semi-structured-sparsity)
- [Structured Pruning Plus Distillation Retraining](#structured-pruning-plus-distillation-retraining)
- [Activation (Contextual) Sparsity](#activation-contextual-sparsity)
- [Decision: Prune, Distill, or Train Small From Scratch](#decision-prune-distill-or-train-small-from-scratch)
- [Composability: Prune, Quantize, Factorize, Distill](#composability-prune-quantize-factorize-distill)
- [Runtime Support](#runtime-support)
- [Common Mistakes](#common-mistakes)
- [Primary Sources](#primary-sources)

---

## When to Use This Reference

Use this reference when:

- Quantization is already applied and further memory or compute reduction is needed
- You are evaluating a vendor or community "sparse" checkpoint and need to know whether it will be faster
- You need a smaller model in a family and are choosing between pruning a parent and training from scratch
- Decode is memory-bound at low batch size and you are considering activation sparsity

Do **not** start here. Exhaust the cheaper levers first, in this order: **roofline diagnosis** (memory- vs compute-bound — every lever below helps only one) -> **batching / admission control** (free throughput, no quality risk) -> **KV-cache quantization** (the resource that binds first at long context) -> **speculative decoding** (`speculative-decoding-guide.md`; lossless only with rejection-sampling verification — Medusa-style relaxed acceptance is not, gate those) -> **weight quantization** (`quantization-patterns.md`; higher-yield and better-supported) -> **pruning / distillation**, this reference, last.

---

## Intake Question

**Will anything in the serving path execute the sparsity you create?**

Answer before pruning a single weight:

- Which sparsity pattern — unstructured, N:M, structured, activation?
- Which GPU architecture, and does it have Sparse Tensor Cores?
- Does the runtime have a sparse kernel for that pattern *and* that dtype?
- If any answer is "no", the pruning buys a smaller checkpoint file and nothing else.

---

## Taxonomy: What Each Kind of Sparsity Actually Buys

| Kind | Pattern | Memory | Wall-clock on GPU | Notes |
|---|---|---|---|---|
| **Unstructured** | any weight may be zero | only with a sparse storage format | **nothing**, absent a sparse kernel | dense GEMM multiplies zeros at full cost; the classic trap |
| **Semi-structured (N:M)** | fixed count of zeros per block, e.g. 2 of every 4 | ~2x on the sparse tensors | real, on Sparse Tensor Cores with a supporting kernel | hardware-native but rigid; see the 50% problem below |
| **Structured** | whole heads, channels, FFN dims, or layers removed | yes, unconditionally | yes, unconditionally | output is a smaller *dense* model — no special kernel needed |
| **Activation / contextual** | input-dependent zeros in activations, weights untouched | reduces weight *movement* per token | only when memory-bound | a different axis: dynamic, not baked into the checkpoint |

The practical ranking for most teams is the reverse of the research ranking. Structured pruning needs no kernel support and no runtime cooperation, so it is the one that reliably ships. Unstructured pruning is the easiest to do and the least likely to help.

---

## One-Shot Post-Training Pruning

Both leading methods prune without retraining, using a small calibration set.

**SparseGPT** (Frantar & Alistarh, arXiv 2301.00774) solves a layer-wise reconstruction problem. The paper claims GPT-family models "can be pruned to at least 50% sparsity in one-shot, without any retraining, at minimal loss of accuracy", running on OPT-175B and BLOOM-176B "in under 4.5 hours", and reaching "60% unstructured sparsity with negligible increase in perplexity". It "generalizes to semi-structured (2:4 and 4:8) patterns, and is compatible with weight quantization approaches" — that last clause is why it is the algorithm behind most 2:4 checkpoints.

**Wanda** (Sun, Liu, Bair & Kolter, arXiv 2306.11695) is the cheap alternative and the more useful mental model. Its metric is stated in the paper as pruning "weights with the smallest magnitudes multiplied by the corresponding input activations, on a per-output basis" — weight magnitude alone is the wrong importance signal because of "emergent large magnitude features in LLMs". A small weight sitting on a large-activation input channel matters; a large weight on a dead channel does not. Wanda "requires no retraining or weight update", and the paper reports it "significantly outperforms the established baseline of magnitude pruning and performs competitively against" reconstruction-based methods.

The score is `S_ij = |W_ij| · ||X_j||_2` — weight magnitude times the L2 norm of that input feature's activations over the calibration batch. Ranking is **per output row** `i`, and the lowest-scored fraction is pruned within each row; a single global threshold would concentrate the damage in a few rows.

```python
W = torch.randn(64, 64)                   # [out, in]
X = torch.randn(128, 64)                  # calibration activations [tokens, in]
S = W.abs() * X.norm(p=2, dim=0)          # ||X_j||_2 broadcasts across input features
k = int(0.5 * W.shape[1])                 # per-row, not global
idx = S.argsort(dim=1)[:, :k]
mask = torch.ones_like(W, dtype=torch.bool).scatter_(1, idx, False)
Wp = W * mask
```

The 2:4 mask is a different operation — keep the two largest of every four contiguous weights, so a count, not a threshold, is fixed:

```python
g = W.reshape(-1, 4)
keep = g.abs().topk(2, dim=1).indices
m24 = torch.zeros_like(g, dtype=torch.bool).scatter_(1, keep, True).reshape(W.shape)
W24 = W * m24
```

Run on a random 64x64 weight (2026-08-29; both results are exact by construction of the code, not empirical): Wanda per-row sparsity was exactly 0.5 for every row (min and max both 0.5), and every group of four in the 2:4 mask had exactly 2 nonzeros.

**Tolerable sparsity.** The papers' own headline is 50%, with SparseGPT claiming 60% unstructured at negligible perplexity increase on 175B-class models. Two cautions the papers do not cover for you: these results are perplexity-centric on large models, and reasoning benchmarks degrade far earlier than perplexity does — SlideSparse (below) reports Qwen3 accuracy falling from 54% to 15% under 50% pruning — a single unreplicated result from the method's own paper, so treat it as an existence proof that the cliff is real, not as a general rule. Smaller models have less redundancy to give up. Treat 50% as an upper bound to *test*, not a default, and gate on the slices below.

---

## Eval Gates Before Shipping a Pruned Model

**Baseline first.** Score the *dense* model on every slice below with the same seed, decoding parameters, and harness you will use for the pruned artifact — run-to-run variance alone can exceed the regression you are hunting. Perplexity is not on the list; it is the least sensitive detector of pruning damage.

| Slice | Why it catches pruning damage |
|---|---|
| Task evals, split by domain | An aggregate score hides a single collapsed domain |
| Structured-output / schema-valid rate | Format adherence breaks before content quality does |
| Tool-call validity | Argument-name and type errors appear early |
| Long-context retrieval (needle, multi-needle) | Depth and head pruning damage retrieval before generation |
| Reasoning (math, code) | The earliest and steepest degradation — see the Qwen3 note above |

**Fail rule (heuristic, not measured).** Reject if any single slice drops more than **2 points absolute** (1 point for schema-valid rate) against the dense baseline — the same numbers the quantization, MoE, and distillation gates use, even when the aggregate looks fine. Treat that band as a starting default to tune against your own run-to-run variance, not a threshold with evidence behind it: set it above your measured noise floor, or you will reject on noise.

Evaluate the **served artifact** — post-quantization, post-recovery, in the target runtime. Each stage's separate delta does not predict the composed one.

---

## N:M Semi-Structured Sparsity

NVIDIA introduced fine-grained structured sparsity with Ampere. Per NVIDIA's developer blog: "The NVIDIA A100 GPU adds support for fine-grained structured sparsity to its Tensor Cores. Sparse Tensor Cores accelerate a 2:4 sparsity pattern", where "in each contiguous block of four values, two values must be zero. This naturally leads to a sparsity of 50%." The hardware ceiling on the sparse matmul is 2x throughput; end-to-end gains are much smaller because attention, norms, and memory movement do not shrink.

**The 50% problem.** 2:4 is not a tuning knob — the hardware requires exactly half the weights be zero. For many LLMs, and reasoning-heavy workloads especially, that is past the quality cliff. Milder patterns like 6:8 (25% pruning) preserve accuracy but, as SlideSparse (Shao et al., arXiv 2603.05232) puts it, "receive no hardware support, falling back to dense execution without any benefit from sparsity."

**SlideSparse** closes that gap for the (2N−2):2N family. Its Sliding Window Decomposition "reconstructs any (2N-2):2N weight block into N-1 overlapping 2:4-compliant windows without any accuracy loss", so milder patterns run on existing Sparse Tensor Cores. Integrated into vLLM and evaluated across A100/H100/B200/RTX 4090/RTX 5080/DGX-spark and FP4/INT8/FP8/BF16/FP16, the paper reports that "on compute-bound workloads, the measured speedup ratio (1.33x) approaches the theoretical upper-bound N/(N-1)=4/3 at 6:8 weight sparsity in Qwen2.5-7B." Note the scoping: *compute-bound* workloads. Decode at low batch size is memory-bound and will not see this. (Verified 2026-08-29; check whether this has landed in an upstream vLLM release before planning around it.)

---

## Structured Pruning Plus Distillation Retraining

This is the path that produces a smaller dense model — no kernel dependency, works in every runtime — at the cost of a retraining budget.

**Start with depth-only pruning.** ShortGPT (Men et al., arXiv 2403.03853) is a one-afternoon experiment that often beats the elaborate schemes. Its Block Influence metric is the cosine similarity between a block's input and output hidden states, averaged over calibration tokens, subtracted from one:

```text
BI_l = 1 - E_tokens[ cos( x_l , x_{l+1} ) ]
```

where `x_l` is the block's input and `x_{l+1}` its output, so a block that barely rotates the residual stream scores near zero — "the more a transformer block changes the hidden states, the more influential this layer is." The procedure: "sort layers in ascending order according to the BI, and delete the layers with the smaller importance" — **lowest BI goes first**. The paper reports layer removal "significantly outperforms previous state-of-the-art (SOTA) methods in model pruning" and is "orthogonal to quantization-like methods".

**Why low-BI blocks exist.** ShortGPT frames it as "a high degree of redundancy in the model architecture", which names the symptom rather than the mechanism. Csordás et al. (arXiv 2505.13898) supply the mechanism: "layers in the second half contribute much less than those in the first half, with a clear phase transition between the two halves", because "deeper models are not using their depth to learn new kinds of computation, but only using the greater depth to perform more fine-grained adjustments to the residual." Low BI is that small residual contribution, measured. See [`../../ai-pretraining/references/adaptive-depth-and-conditional-compute.md#does-depth-even-earn-its-keep`](../../ai-pretraining/references/adaptive-depth-and-conditional-compute.md#does-depth-even-earn-its-keep).

**When BI is not enough**, the width-and-distillation methods:

| Method | What it prunes | Recovery | When to reach for it |
|---|---|---|---|
| **Minitron** (Muralidharan et al., arXiv 2407.14679, NeurIPS 2024) | "depth, width, attention and MLP pruning" jointly | knowledge distillation on "a fraction (<3%) of the original training data" | Deriving a whole family from one parent. 8B and 4B from a 15B needs "up to 40x fewer training tokens per model compared to training from scratch", "compute cost savings of 1.8x for training the full model family (15B, 8B, and 4B)", "up to a 16% improvement in MMLU scores compared to training from scratch" |
| **Minitron in practice** (Sreenivas et al., arXiv 2408.11796) | compares "(1) depth pruning and (2) joint hidden/attention/MLP (width) pruning" on Llama 3.1 8B and Mistral NeMo 12B | same | Choosing depth vs width. Rule of thumb, not from the abstract: depth cuts latency roughly linearly by removing sequential layers; width preserves quality better at equal parameter count but yields less latency per parameter. Benchmark both — the abstracts do not settle it |
| **NVIDIA Model Optimizer** | "uses the activation magnitudes to prune the embedding hidden size; mlp ffn hidden size; transformer attention heads; ... MoE number of experts ... and number of layers" | "1x training epochs (or 1x downstream task fine-tuning), same or smaller (0.5x-1x) learning rate" | The supported production implementation of the above |
| **Sheared LLaMA** (Xia, Gao, Zeng & Chen, arXiv 2310.06694) | targeted structured pruning + dynamic batch loading; LLaMA2-7B to 1.3B and 2.7B | continued pretraining, "only 3% of compute compared to training" from scratch | Large ratio cuts where the data mixture during recovery matters |
| **DarwinLM** (Tang, Sieberling, Kurtic, Shen & Alistarh, arXiv 2502.07780) | per-layer ratios found by "an evolutionary search process, generating multiple offspring models in each generation through mutation" | budget grows across selection stages; "5x less training data during post-compression training" than Sheared LLaMA | You have search compute and want to stop hand-tuning per-layer ratios |

**Minitron's savings are BUILD cost, not serving cost.** "40x fewer training tokens" and "1.8x compute" are one-off training-budget figures. They say nothing about what the resulting model costs to serve. Make the serving case separately, in tokens per dollar at your target concurrency and latency SLO — a pruned model that misses the SLO or falls off a batch-size cliff can cost more per token than the parent it came from.

---

## Activation (Contextual) Sparsity

A different axis entirely: weights stay dense on disk, but for each token only a subset is used.

**Exact zeros versus thresholded approximations.** ReLU emits *exact* zeros, so skipping those rows is arithmetically lossless — the skipped terms contribute nothing. SwiGLU and GELU are smooth and almost never output exactly zero, so TEAL and CATS instead threshold small-magnitude activations to zero. That is an approximation whose error grows with the sparsity target, since every discarded activation was genuinely nonzero — which is why SwiGLU-family results are always quoted as "at X% sparsity with Y degradation" and ReLU results are not. For ReLU the sparsity is free; the only question is whether the pretraining change was affordable.

**Deja Vu** (Liu et al., arXiv 2310.17157) named the phenomenon — "small, input-dependent sets of attention heads and MLP parameters that yield approximately the same output as the dense model for a given input" — and reports over 2x latency reduction versus FasterTransformer and over 6x versus a HuggingFace implementation, without compromising quality or in-context learning. The abstract does not state batch-size conditions; the gains come from skipping weight loads, so they are a low-batch, memory-bound-decode phenomenon by construction.

**ReLU strikes back** (Mirzadeh et al., arXiv 2310.04564) argues that swapping GELU/SiLU for ReLU "has a negligible impact on convergence and performance" while creating the sparsity that makes this exploitable, claiming strategies that "substantially reduce LLM inference computation up to three times". Relevant mostly if you control pretraining or can afford continued pretraining — most 2026 production models do not use ReLU.

**TEAL** (Liu et al., "Training-Free Activation Sparsity in Large Language Models", arXiv 2408.14690) removes that prerequisite: a "training-free method that applies magnitude-based activation sparsity to hidden states throughout the entire model", achieving "40-50% model-wide sparsity with minimal performance degradation across Llama-2, Llama-3, and Mistral families, with sizes varying from 7B to 70B", and demonstrating "wall-clock decoding speed-ups of up to 1.53× and 1.8× at 40% and 50% model-wide sparsity". It is "compatible with weight quantization".

**CATS** (Lee et al., arXiv 2404.08763) thresholds activations contextually, reporting 50% activation sparsity with downstream performance within a small margin of base models, and a custom GPU kernel giving "a ~15% improvement in wall-clock inference latency of token generation on both Llama-7B and Mistral-7B."

**When this pays.** Activation sparsity reduces bytes moved per token, so it helps exactly where decode is memory-bandwidth-bound: batch size 1, single-stream, latency-sensitive, local/edge. As batch size rises, weight loads amortise across the batch and the arithmetic intensity climbs — the same weights serve every sequence, so skipping them per-token stops being a win and the gather overhead can make it a loss. Note the gap between the 40–50% sparsity figures and the 1.53–1.8x speedups: sparsity fraction is not speedup. Do not plan capacity for a high-QPS batched server on these numbers.

---

## Decision: Prune, Distill, or Train Small From Scratch

Anchor on "Small LLMs: Pruning vs. Training from Scratch" (Xu, Lu, Li, Zhu, Sun & Liu, arXiv 2606.14150). Its conclusion, in the authors' framing: "with a large pretrained model in hand and a limited training token budget, pruning is better than training from scratch; when the training budget is not limited, training from scratch can be competitive for coarser pruning" — though "pruning at finer granularities still retain[s] an advantage", and pruned initialization consistently beat random initialization at matched token budgets. So a large pretrained parent "is not always necessary" when compute is abundant.

```text
Need a smaller model in this family?
  |
  |- Token budget is tight, strong parent available
  |     -> prune (structured) + distillation-retrain. Minitron / Sheared LLaMA / DarwinLM.
  |        Finer granularity retains more of the advantage than coarse.
  |
  |- Token budget is generous
  |     -> training from scratch is competitive against coarse pruning; the parent
  |        stops being a prerequisite. Compare against a distillation baseline before
  |        committing — see the distillation scaling law for when a teacher pays off:
  |        ../../ai-scaling-laws/references/post-chinchilla-developments.md#9-distillation-scaling-laws-2025
  |
  |- No training budget at all
  |     -> one-shot pruning (Wanda / SparseGPT) or depth pruning (ShortGPT).
  |        Expect a quality cost. Verify a sparse kernel exists first.
  |
  `- Just need it cheaper to serve, no new model
        -> work the lever ladder above; quantization before pruning.
```

The genuinely cheapest option is often none of the above: a smaller model already exists in the family, already trained, already supported by your runtime. Check that before building a compression pipeline.

---

## Composability: Prune, Quantize, Factorize, Distill

This is the shared matrix for all four compression levers; other references link here rather than restating it.

**Choosing ONE lever: quantization first.** Not a law — an ecosystem heuristic, not a fixed rule. Quantization wins because the kernel support is mature in every major runtime, while sparse and factorized kernels are patchy (see [Runtime Support](#runtime-support)); check current runtime support before relying on this ranking, since it changes as kernel support matures.

**Pipeline order when STACKING.** Each arrow is a gate: run the [eval gate set](#eval-gates-before-shipping-a-pruned-model) after every stage, and stop at the first slice that fails rather than compounding damage into the next one.

```text
structured prune -> distillation recovery -> factorize (optional; before quantizing the factors)
   -> quantize -> calibrate -> evaluate the SERVED artifact
```

Why: recovery training repairs structural damage most cheaply right after pruning; distillation wants a clean, un-quantized teacher signal; the quantizer must calibrate on the factors you actually ship; and quantization goes last because it is the cheapest stage to redo. Factorization is optional and often skipped — see [`../../ai-pretraining/references/structured-and-low-rank-parameterization.md`](../../ai-pretraining/references/structured-and-low-rank-parameterization.md).

| Lever | What it reduces | Binding resource it helps | Typical quality cost |
|---|---|---|---|
| **Quantization** | bytes per weight (and per KV entry) | memory capacity and bandwidth; weight-load-bound decode | lowest per byte saved at 8- and 4-bit; rises sharply below 4-bit |
| **Structured pruning** | parameter count and layer count | capacity, bandwidth, *and* FLOPs — depth pruning also cuts sequential latency | high without distillation recovery; moderate with it |
| **Factorization** | parameter count, at the cost of extra matmuls | capacity; can *hurt* latency by adding kernel launches | varies widely by rank; needs recovery training like pruning |
| **Distillation** | nothing on its own — it is the recovery step, or trains a smaller student outright | none directly; enables the others | recovers quality rather than costing it; costs training compute |

Composed error is not additive in a predictable way. SparseGPT is "compatible with weight quantization approaches", TEAL is "compatible with weight quantization", ShortGPT is "orthogonal to quantization-like methods" — all true, and none of them licenses inferring the combined delta from the separate ones. Evaluate the artifact you will serve.

**MoE handoff.** MoE has its own pruning axis: whole experts. "Not All Experts are Equal" (Lu et al., arXiv 2402.14800) proposes "post-training approaches for task-agnostic and task-specific expert pruning and skipping of MoE LLMs", reporting reduced model size and increased inference speed with maintained performance — expert-level sparsification that, unlike weight pruning, does not "rely on specifically designed hardware." After pruning experts, the router is distributing the same tokens over fewer destinations, so re-check routing health before anything else: [`moe-expert-parallelism.md#routing-health-metrics`](moe-expert-parallelism.md#routing-health-metrics). Expect MaxVio to rise; tokens start being dropped or rerouted once `1 + MaxVio` exceeds the capacity factor (MaxVio is a fractional excess over mean load, so compare on one scale — definition in [Routing Health Metrics](moe-expert-parallelism.md#routing-health-metrics)).

---

## Runtime Support

Check each runtime's current release notes before relying on this table — sparsity support has historically been thinner than quantization support and can contract as well as grow.

| Runtime | 2:4 / semi-structured | Activation sparsity | Notes |
|---|---|---|---|
| **vLLM** | kernels present (CUTLASS sparse GEMM), but the *production path narrowed* | no documented support | vLLM's quantization docs index does not list sparsity at all. Critically, LLM Compressor — the tool that produced 2:4 checkpoints for vLLM — now states: "Sparse compression (including 2of4 sparsity) is no longer supported by LLM Compressor due lack of hardware support and user interest" (ref vLLM PR #36799). SparseGPT/Wanda/magnitude *modifiers* still exist for producing pruned weights. Verify end-to-end before planning around 2:4 on vLLM. |
| **TensorRT-LLM** | via NVIDIA Model Optimizer; strongest vendor path | no documented support | ModelOpt is the supported producer; TRT-LLM the consumer. Verify version compatibility. |
| **SGLang** | no supported path documented (re-checked 2026-08-29) | no supported path documented (re-checked 2026-08-29) | A 2:4 feature request exists (sgl-project/sglang issue #2200) and sparse GEMM modules have been referenced, but no stable docs page confirms a supported 2:4 serving path. Do not assume. |
| **llama.cpp / GGUF** | no | no | CPU and Apple Silicon backends have no Sparse Tensor Core equivalent; 2:4 buys nothing here. Sparse GGUF checkpoints exist but run as dense. Use quantization instead. |
| **NVIDIA Model Optimizer** | yes — producer, not server | n/a | Supports the NVIDIA 2:4 pattern with ASP and SparseGPT sparsification, plus Minitron/Puzzletron/FastNAS structured pruning. Minitron prunes embedding hidden size, FFN hidden size, attention heads, GQA query groups, MoE experts, and layer count. |

**The honest summary**: structured pruning is universally supported because its output is just a smaller dense model. 2:4 has hardware support on Ampere+ but the software supply chain around it weakened in 2026. Activation sparsity has research kernels and essentially no first-class runtime support — treat it as a research technique unless you are willing to maintain kernels.

---

## Common Mistakes

- **Pruning unstructured and expecting a speedup.** A dense GEMM multiplies zeros at full cost. Without a sparse kernel, 50% unstructured sparsity is 0% faster. This is the single most common failure.
- **Confusing sparsity fraction with speedup.** 50% sparsity does not mean 2x. TEAL reports up to 1.8x at 50% model-wide activation sparsity; the 2:4 hardware ceiling is 2x on the matmul alone, and end-to-end is well under that.
- **Treating 2:4 as tunable.** It is exactly 50% by hardware definition. If 50% is too aggressive for your model, 2:4 is not the answer — look at (2N−2):2N, structured pruning, or quantization.

---

## Primary Sources

- SparseGPT — Frantar & Alistarh: https://arxiv.org/abs/2301.00774
- Wanda — Sun, Liu, Bair & Kolter: https://arxiv.org/abs/2306.11695
- SlideSparse, (2N−2):2N structured sparsity — Shao et al.: https://arxiv.org/abs/2603.05232
- Minitron / Compact Language Models via Pruning and Knowledge Distillation — Muralidharan et al. (NeurIPS 2024): https://arxiv.org/abs/2407.14679
- LLM Pruning and Distillation in Practice: The Minitron Approach — Sreenivas et al.: https://arxiv.org/abs/2408.11796
- Sheared LLaMA — Xia, Gao, Zeng & Chen: https://arxiv.org/abs/2310.06694
- DarwinLM — Tang, Sieberling, Kurtic, Shen & Alistarh: https://arxiv.org/abs/2502.07780
- ShortGPT — Men et al.: https://arxiv.org/abs/2403.03853
- Do Language Models Use Their Depth Efficiently? — Csordás et al.: https://arxiv.org/abs/2505.13898
- Deja Vu — Liu et al.: https://arxiv.org/abs/2310.17157
- ReLU Strikes Back — Mirzadeh et al.: https://arxiv.org/abs/2310.04564
- TEAL / Training-Free Activation Sparsity — Liu et al.: https://arxiv.org/abs/2408.14690
- CATS — Lee et al.: https://arxiv.org/abs/2404.08763
- Small LLMs: Pruning vs. Training from Scratch — Xu et al.: https://arxiv.org/abs/2606.14150
- Not All Experts are Equal (MoE expert pruning) — Lu et al.: https://arxiv.org/abs/2402.14800
- NVIDIA, Accelerating Inference with Sparsity Using Ampere and TensorRT: https://developer.nvidia.com/blog/accelerating-inference-with-sparsity-using-ampere-and-tensorrt/
- NVIDIA Model Optimizer pruning guide: https://nvidia.github.io/Model-Optimizer/guides/3_pruning.html
- LLM Compressor compression schemes (2of4 deprecation notice): https://docs.vllm.ai/projects/llm-compressor/en/latest/guides/compression_schemes/
- vLLM quantization docs: https://docs.vllm.ai/en/stable/features/quantization/
