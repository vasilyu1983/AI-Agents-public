# Architecture Limitations and Workarounds (Build-Time)

The failure-mode companion to [transformer-from-scratch.md](transformer-from-scratch.md) (core
mechanics) and [modern-architecture-deltas.md](modern-architecture-deltas.md) (the modern
component swaps). This file is organized as a **limitation -> workaround -> tradeoff** catalogue
for each part of the transformer: what breaks, the fix, and what the fix costs. Scope is
*build-time* (training the weights). Serving-time variants (PagedAttention, speculative
decoding, quantized inference) belong to
[ai-llm-inference](../../ai-llm-inference/SKILL.md); MoE/parallelism at scale belong to
[ai-distributed-training](../../ai-distributed-training/SKILL.md).

Many specifics below (which lab uses what, exact ratios) are volatile — flagged "verify";
the *limitation->workaround structure* is stable.

## Table of Contents

- [How to Read This](#how-to-read-this)
- [1. Attention Core: the O(n^2) Wall](#1-attention-core-the-on2-wall)
- [2. Softmax Attention Pathologies](#2-softmax-attention-pathologies)
- [3. Attention Head Schemes: MHA -> MQA -> GQA -> MLA](#3-attention-head-schemes-mha---mqa---gqa---mla)
- [4. Positional Encoding Design Space](#4-positional-encoding-design-space)
- [5. MLP / FFN and Mixture-of-Experts](#5-mlp--ffn-and-mixture-of-experts)
- [6. Normalization, Residual Stream, and Depth Stability](#6-normalization-residual-stream-and-depth-stability)
- [7. Numerical Precision](#7-numerical-precision)
- [8. Long-Context at Build Time](#8-long-context-at-build-time)
- [9. Encoder vs Decoder vs Encoder-Decoder](#9-encoder-vs-decoder-vs-encoder-decoder)
- [Routing to Depth](#routing-to-depth)

## How to Read This

Each section states the **limitation** (what fails and why), one or more **workarounds**
(ordered cheapest/most-standard first), and the **tradeoff** the workaround introduces. The
recurring meta-lesson: nearly every modern transformer component is itself a workaround for a
limitation of the naive 2017 design, and each carries its own new limitation. There is no free
lunch — only a better-positioned tradeoff.

## 1. Attention Core: the O(n^2) Wall

**Limitation.** Self-attention computes an n×n score matrix: compute and *materialized* memory
are both O(n²) in sequence length. Naive attention also writes the full score matrix to HBM,
so it is memory-bandwidth-bound long before it is compute-bound.

| Workaround | What it does | Tradeoff |
|---|---|---|
| **FlashAttention** (default; use it) | IO-aware *exact* attention: tiles Q/K/V in SRAM, never materializes the n×n matrix; O(n) memory, far fewer HBM reads | Does **not** reduce the O(n²) *compute*; needs a supported kernel/GPU. This is the baseline, not an optimization to defer |
| **Sliding-window / local attention** | Each token attends to a fixed window w: O(n·w) | Loses direct long-range edges; needs global tokens or layer interleaving to recover them |
| **Native Sparse Attention (NSA) / block-sparse** | Learned or structured sparsity over blocks; compressed + selected + local branches | Quality depends on the sparsity pattern; kernel complexity; verify maturity before training on it |
| **Linear / kernel attention, SSM hybrids** | Replace softmax with a kernel or recurrence: O(n) | Pure-linear/pure-SSM underperform on in-context recall; only **hybrids** (a few full-attention layers) stay competitive — see §9 of [modern-architecture-deltas.md](modern-architecture-deltas.md) |

**Rule:** FlashAttention is the floor for any from-scratch run at non-trivial context. Reach
for sparse/sliding/linear only when O(n²) *compute* (not memory) is the proven bottleneck.

## 2. Softmax Attention Pathologies

**Limitation.** Standard softmax must distribute probability mass that sums to 1 even when a
head wants to attend to *nothing*. The model learns to dump that mass on a few tokens
(usually the first token / BOS) — **attention sinks** — and couples them with **massive
activations** (large-norm features in specific channels). At scale this produces exploding
attention logits, **attention-entropy collapse**, loss spikes, and quantization-hostile
activation distributions. (Verified current: attention sinks also induce *gradient* sinks, and
the coupled outlier features are what make W8A8 quantization hard — see
[ai-llm-inference](../../ai-llm-inference/references/architecture-and-attention-serving.md).)

| Workaround | What it does | Tradeoff |
|---|---|---|
| **QK-Norm** (standard at scale) | RMS/L2-normalize queries and keys before the dot product, bounding logit growth | Prevents logit explosion and enables higher learning rates; tiny extra compute; changes attention scaling semantics |
| **Logit soft-capping** | `logits <- c · tanh(logits / c)` before softmax (Gemma-style) | Bounds logits without a norm; the cap `c` is a hyperparameter; can interact poorly with FlashAttention kernels that don't support it |
| **Off-by-one / "quiet" softmax, gated attention, Softpick** | Let attention sum to <1 (a denominator +1, or a learned gate) so a head can attend to nothing | Removes the *need* for a sink and the coupled outliers; newer (2025–26), verify kernel/runtime support before relying on it |
| **z-loss** | Auxiliary loss penalizing the softmax normalizer's log-Z magnitude | Stabilizes the output softmax (and logits); one more loss term to weight |

**Rule:** for any serious-scale from-scratch run, include **QK-Norm** (and/or logit
soft-capping) from the start — retrofitting stability after divergence wastes a run.

## 3. Attention Head Schemes: MHA -> MQA -> GQA -> MLA

**Limitation.** Multi-Head Attention (MHA) stores a full Key and Value per head. The KV-cache —
`2 · layers · heads · head_dim · seq · dtype` — is the binding memory constraint at long
context and large batch, and it dominates decode bandwidth.

| Scheme | KV footprint | Quality / stability | When to choose (build-time) |
|---|---|---|---|
| **MHA** | Full (heads KV pairs) | Best per-head expressivity | Small models, short context, max quality, simplest |
| **MQA** | 1 KV head shared by all query heads | Largest cut, but measurable quality drop and **training instability** | Rarely first choice now |
| **GQA** | G groups share KV (e.g. 8 query : 1 KV) | The compromise; near-MHA quality at a fraction of cache | **Universal default** for new decoders |
| **MLA** (latent) | Low-rank latent KV; cache compact latents, reconstruct per-head at use | Strong quality + the deepest cache cut | Worth it for long-context/serving-cost-bound models; more complex |

**MLA's own limitation and its fix.** A naive low-rank KV latent is *incompatible with RoPE*:
RoPE rotates keys position-dependently, which doesn't commute with the shared low-rank
projection. DeepSeek's fix is **decoupled RoPE** — split each head into a compressed
NoPE-carrying component (the low-rank latent, position-free) plus a small extra
position-carrying component (shared key + per-head query vectors) that *only* carries RoPE.
You cache the latent + the small rotary part. (Verified June 2026; MLA originated in
DeepSeek-V2/V3 and has since been ported into other transformer stacks.)

**Rule:** default **GQA**; choose **MLA** when KV-cache/long-context economics dominate and you
can afford the decoupled-RoPE complexity. Avoid bare MQA unless you've measured GQA too costly.

## 4. Positional Encoding Design Space

**Limitation.** Attention is permutation-invariant; position must be injected. The scheme
chosen at build time bounds how far the model can later be served beyond its trained length.

| Scheme | Mechanism | Limitation | Extrapolation |
|---|---|---|---|
| **Learned absolute** (GPT-2) | A trained position-embedding table | Hard ceiling at `block_size`; zero extrapolation | None |
| **Sinusoidal** (2017) | Fixed sin/cos of position | Weak extrapolation in practice | Poor |
| **RoPE** (modern default) | Rotate Q/K by a position-dependent angle; encodes *relative* position in the dot product | Degrades beyond trained length without scaling | Limited (extendable) |
| **ALiBi** | Linear distance penalty added to logits | Strong length extrapolation, but weaker long-range *retrieval* (in-context recall) than RoPE | Strong |
| **NoPE** | No explicit positional signal; causal mask alone | Surprisingly works in some decoder settings; less controllable | Mixed |

**Extending RoPE beyond trained context** (the standard long-context recipe):

- **Linear position interpolation (PI):** divide positions by a factor s to squeeze longer
  contexts into the trained range. Simple; blurs high-frequency (local) detail.
- **NTK-aware scaling:** scale the RoPE base instead of positions, preserving high-frequency
  resolution; better than linear PI for moderate extension.
- **YaRN:** frequency-band-wise interpolation (interpolate low frequencies, keep high) plus an
  attention-temperature term; the strongest of the three, usually with a short fine-tune.

**Rule:** use **RoPE** by default. If long context is a goal, *plan the extension method at
build time* — train short and extend with YaRN/NTK rather than training natively long (cheaper,
and you avoid the O(n²) cost over the whole run). The serve-time mirror (RoPE-scaling
mismatch traps) is in
[ai-llm-inference](../../ai-llm-inference/references/architecture-and-attention-serving.md).

## 5. MLP / FFN and Mixture-of-Experts

**What the FFN is.** The position-wise FFN holds the majority of parameters and acts as the
model's **key-value memory** (Geva et al.): the up-projection keys detect input patterns, the
down-projection values write associated content into the residual stream. "Knowledge capacity"
is largely FFN capacity.

**Activation evolution (limitation -> fix):** ReLU's dead-neuron / non-smooth gradient ->
**GELU** (smooth) -> **gated GLU variants (GEGLU/SwiGLU)**: a gate branch multiplies the
activation, improving quality per parameter. Tradeoff: gating uses **three** weight matrices
instead of two, so width is scaled to ~⅔ to keep the parameter budget (the "×1.5 / ⅔" rule).

**Dense-FFN cost limitation -> Mixture-of-Experts.** Replace one big FFN with N expert FFNs and
route each token to k of them: compute scales with k, not N, so you get many more parameters at
fixed FLOPs. MoE is the frontier default — but it imports a cluster of build-time failure modes:

| MoE failure mode | Workaround |
|---|---|
| **Router collapse** (all tokens to a few experts) | Auxiliary **load-balancing loss**; or aux-loss-free bias-based balancing (DeepSeek-V3) |
| **Dead experts** (never selected) | Load-balancing + noise in routing; expert-dropout |
| **Saves FLOPs, not VRAM** — all experts must be resident | Budget memory for the *full* parameter count; expert/tensor parallelism |
| **Training instability / token dropping at capacity** | Capacity factor tuning; z-loss on the router; fine- vs coarse-grained expert count |
| **Shared-expert vs not** (DeepSeek yes / Qwen3 no) | A design choice — a shared always-on expert captures common patterns; verify per target |

**Rule:** the FFN is where you spend parameters. Use **SwiGLU**. Move to **MoE** only when
cost-at-scale justifies the routing machinery — and hand the routing/parallelism depth to
[ai-distributed-training](../../ai-distributed-training/SKILL.md).

## 6. Normalization, Residual Stream, and Depth Stability

**Norm type.** **LayerNorm** centers and scales; **RMSNorm** drops mean-centering (cheaper,
no bias) and is the modern default. Caveat: RMSNorm's reductions must run in **fp32** under
bf16 training or precision loss creeps in.

**Norm placement — the core stability tradeoff:**

| Placement | Property | Tradeoff |
|---|---|---|
| **Post-norm** (original) | Norm after the residual add | Better final quality, but unstable to train deep — gradients blow up; needs careful warmup |
| **Pre-norm** (modern default) | Norm before the sublayer | Stable training, clean gradient path | Can let the residual stream grow / representations drift; usually add a final norm before the head |
| **DeepNorm** | Scale residuals + down-scale init so very deep post-norm trains | Recovers post-norm quality at depth; extra init bookkeeping |
| **Sandwich / peri-norm** | Norm on both sides of the sublayer | More stability knobs; more compute |

**Residual stream limitation.** The residual stream is a **finite-bandwidth communication
channel**: every layer reads and writes the same d-dimensional vector, storing features in
superposition. Too-deep/too-narrow models contend for this bandwidth (representation collapse).
Mitigations: scale residual-branch init by `1/sqrt(2·n_layer)` (GPT-2), DeepNorm scaling,
and adequate width for depth.

**Depth failure modes:** beyond gradient vanishing/exploding, deep attention suffers
**attention-entropy / rank collapse** (heads converge to uniform or rank-1). Fixes: **QK-Norm**
(§2), warmup, better init (**T-Fixup** removes the need for warmup via init scaling), and z-loss.

**Rule:** **pre-norm + RMSNorm + scaled residual init + QK-Norm** is the stable modern baseline.
Reach for DeepNorm/T-Fixup only when training unusually deep.

## 7. Numerical Precision

**Limitation.** Lower precision saves memory and bandwidth but narrows dynamic range; overflow
and underflow show up as loss spikes and NaNs.

| Format | Limitation | Workaround |
|---|---|---|
| **fp16** | Small exponent range -> activation/gradient **overflow**, loss spikes on older stacks | **Loss/gradient scaling** (GradScaler); keep a master fp32 copy |
| **bf16** (default) | Wider exponent, lower mantissa precision | Standard for training; run norm/softmax **reductions in fp32** |
| **fp8** (frontier) | Tensor-core accumulation is low-bit; naive fp8 destabilizes | DeepSeek-V3: **blockwise/group-128 scaling + fp32 accumulation every few WGMMA**; first validated 671B-MoE fp8 run (Hopper). ~2× memory vs bf16. Verify hardware/kernel support |
| **fp4 (MXFP4 / NVFP4)** (emerging 2026) | **Activation & gradient outliers** dominate the 4-bit range and destabilize training | Micro-block scaling, outlier control/clipping, oscillation suppression; near-fp8 accuracy reported at 12B. Treat as research-grade — verify before betting a run |

**Rule:** train in **bf16** by default; keep reductions in fp32. fp8 is a deliberate,
infra-heavy decision (custom scaled kernels), not a flag; fp4 is bleeding-edge.

## 8. Long-Context at Build Time

**Limitations.** (a) O(n²) cost over the whole run if you train natively long (§1). (b)
**Length generalization failure** — models don't reliably work past their trained length (§4).
(c) **Lost-in-the-middle** — even within the window, retrieval accuracy sags for content in the
*middle* of the context. (d) Position schemes that don't extrapolate cap you hard.

| Workaround | What it does | Tradeoff |
|---|---|---|
| **Train short, extend with YaRN/NTK** | Most of training at modest length; a short long-context fine-tune extends it | Cheapest path to long context; extension quality must be eval'd |
| **Document masking / intra-doc attention** | Block attention from crossing packed-document boundaries | Cleaner long-context signal; small masking complexity |
| **Sliding-window + attention sinks (StreamingLLM as architecture)** | Keep a few sink tokens + a recent window | Fixed-memory effectively-infinite streams, but loses middle-context fidelity |
| **Needle-in-a-haystack + position-stratified evals** | Don't trust the trained length — measure retrieval across positions | Catches lost-in-the-middle before users do |

**Rule:** decide the long-context strategy (native vs extend) and the positional scheme
*together*, up front; measure with position-stratified retrieval, not just perplexity.

## 9. Encoder vs Decoder vs Encoder-Decoder

This skill builds **decoder-only** by design, but choosing it should be a decision, not a
default-by-omission. The three families and their limitations:

| Family | Strength | Limitation | Workaround / when to switch |
|---|---|---|---|
| **Encoder-only** (BERT-class) | Bidirectional context; best for classification & **dense embeddings** | **Cannot generate**; MLM trains on only ~15% of tokens (masked) -> sample-*inefficient* | **ELECTRA** replaced-token-detection trains on *all* tokens (far more efficient); for generation, switch families |
| **Decoder-only** (GPT-class) | Causal generation, in-context learning, simplest to scale — **why it won** | Causal mask wastes bidirectional context for prompt tokens; no native fixed-length embedding | **Prefix-LM** lets prompt tokens attend bidirectionally while completion stays causal; for embeddings, mean/last-token **pooling** or a contrastive head |
| **Encoder-decoder** (T5-class) | Cross-attention; excels at **seq2seq** (translation, summarization) | ~2× params; weaker few-shot in-context learning; needs paired data | Use when the task is a clean input->output transform with paired data; otherwise decoder-only generalizes better few-shot |

**Rule:** decoder-only is the right default for a general generative model; pick encoder-only
for embeddings/classification and encoder-decoder for paired seq2seq. The decision-layer view
(with routing) lives in
[ai-architecture-advisor](../../ai-architecture-advisor/SKILL.md).

## Routing to Depth

- Core mechanics (attention math, blocks, init) -> [transformer-from-scratch.md](transformer-from-scratch.md)
- Modern component swaps (RoPE/RMSNorm/SwiGLU/GQA/FlashAttention) -> [modern-architecture-deltas.md](modern-architecture-deltas.md)
- Serving-time limitations (KV at serve, SmoothQuant, roofline, StreamingLLM, RoPE-scaling traps, SSM serving) -> [ai-llm-inference architecture-and-attention-serving.md](../../ai-llm-inference/references/architecture-and-attention-serving.md)
- MoE routing + parallelism at scale -> [ai-distributed-training](../../ai-distributed-training/SKILL.md)
- Which family/architecture to pick (decision layer) -> [ai-architecture-advisor](../../ai-architecture-advisor/SKILL.md)
