# Architecture Limitations and Workarounds (Build-Time)

The failure-mode companion to [transformer-from-scratch.md](transformer-from-scratch.md) (core
mechanics) and [modern-architecture-deltas.md](modern-architecture-deltas.md) (the modern
component swaps). This file is organized as a **limitation -> workaround -> tradeoff** catalogue
for each part of the transformer: what breaks, the fix, and what the fix costs. Scope is
*build-time* (training the weights). Serving-time variants (PagedAttention, speculative
decoding, quantized inference) belong to
[ai-llm-inference](../../ai-llm-inference/SKILL.md); MoE *parallelism* at scale belongs to
[ai-distributed-training](../../ai-distributed-training/SKILL.md) — MoE build-time mechanics
(routing, load balancing, granularity, failure modes) are §5 here.

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
You cache the latent + the small rotary part. (MLA originated in DeepSeek-V2/V3 and has since
been ported into other transformer stacks.)

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
fixed FLOPs. MoE is the frontier default *at frontier scale with an expert-parallel serving stack*;
below roughly ~10B total params, or on single-GPU/edge serving, a dense model usually wins on
wall-clock and simplicity (a heuristic — verify against your own serving numbers). It also
imports a cluster of build-time failure modes:

**The mechanism behind most of them is one feedback loop.** An expert that receives more tokens
gets more gradient, so it improves faster, so the router assigns it more probability mass — a
rich-get-richer spiral that ends with a few live experts and a long dead tail. Every balancing
fix below exists to break that loop, either by penalising imbalance (aux loss) or by biasing
selection away from overloaded experts.

| MoE failure mode | Workaround | Diagnostic (what to measure) |
|---|---|---|
| **Router collapse** (all tokens to a few experts) | Auxiliary **load-balancing loss**; or aux-loss-free bias-based balancing (DeepSeek-V3) | Per-expert token share and **normalised routing entropy** over a step window — collapse shows as entropy falling toward 0 while max share climbs. Metric block: [routing-health-metrics](../../ai-llm-inference/references/moe-expert-parallelism.md#routing-health-metrics) |
| **Dead experts** (never selected) | Load-balancing + noise in routing; expert-dropout | Count experts with zero dispatched tokens over a window; watch the count trend, not one step |
| **No real specialisation** — experts are permutation-interchangeable | Finer granularity, shared expert, or accept it: you have an ensemble with a router, not modularity | **Falsifier:** permute two experts' assignments and re-measure loss. If loss barely moves, the experts are interchangeable and there is no modularity to exploit |
| **Saves FLOPs, not VRAM** — all experts must be resident | Budget memory for the *full* parameter count; expert/tensor parallelism | Compare active vs resident expert params. DeepSeek-V3 at 256 routed experts / top-8 computes 8 but holds 256 resident — a **32× gap** |
| **Training instability / token dropping at capacity** | Capacity factor tuning; z-loss on the router | Dropped-token rate per layer at the chosen capacity factor |
| **Shared-expert vs not** (DeepSeek yes / Qwen3 no) | A design choice — a shared always-on expert captures common patterns; verify per target | Ablate: shared-expert share of residual-stream write vs the routed pool |

**Low-batch caveat.** At small batch each active expert's weights are read from HBM to serve very
few tokens, so MoE decode is bandwidth-bound *per active expert*; the FLOP saving only becomes a
latency saving above the batch size that amortises those weight reads.

**Router and load-balance loss, concretely.** The Switch/GShard auxiliary loss is

`L_aux = α · N · Σ_i f_i · P_i`

where `N` is the expert count, `f_i` the fraction of dispatched tokens going to expert i, and
`P_i` the mean router probability assigned to expert i over the batch. Both vectors sum to 1, so a
perfectly balanced router (`f_i = P_i = 1/N`) gives `L_aux = α·N·N·(1/N²) = α` — the loss floor,
which is the sanity check to assert in a unit test. `α` is small (Switch Transformer,
[arXiv 2101.03961](https://arxiv.org/abs/2101.03961); the abstract does not state a value — tune it,
and check the paper body before quoting one). Runnable sketch (executed on torch 2.13; prints
`aux 0.010026` for a near-uniform random router and exactly `α` for the balanced case):

```python
import torch, torch.nn as nn, torch.nn.functional as F

class TopKRouter(nn.Module):
    """Top-k router + Switch/GShard auxiliary load-balance loss."""
    def __init__(self, d_model, n_experts, k, alpha=1e-2):
        super().__init__()
        self.gate = nn.Linear(d_model, n_experts, bias=False)
        self.n, self.k, self.alpha = n_experts, k, alpha

    def forward(self, x):                                 # x: (T, d_model)
        probs = F.softmax(self.gate(x), dim=-1)           # (T, N) router probabilities
        topv, topi = probs.topk(self.k, dim=-1)           # (T, k) selected experts
        w = topv / topv.sum(-1, keepdim=True)             # renormalise over the k chosen
        mask = F.one_hot(topi, self.n).sum(1).float()     # (T, N) dispatch mask
        f = mask.mean(0) / self.k                         # f_i: fraction of dispatch slots
        P = probs.mean(0)                                 # P_i: mean router probability
        return topi, w, self.alpha * self.n * (f * P).sum()
```

**The alternative: bias-based balancing with (almost) no aux loss.** *"Auxiliary-Loss-Free Load Balancing Strategy for
Mixture-of-Experts"* ([arXiv 2408.15664](https://arxiv.org/abs/2408.15664), the method DeepSeek-V3
adopts — [arXiv 2412.19437](https://arxiv.org/abs/2412.19437)) applies "an expert-wise bias to the
routing scores of each expert" for *selection only*, adjusted up or down by each expert's recent
load; the gating weights themselves are untouched. Motivation, verbatim from the abstract: "a large
auxiliary loss will introduce non-negligible interference gradients into training and thus impair
the model performance." DeepSeek-V3 does not drop balancing losses entirely: it keeps a
complementary **sequence-wise** balance loss with a very small weight (α = 0.0001) to stop extreme
imbalance within a single sequence, and it computes affinities with a sigmoid rather than a softmax.

**The five-axis MoE design space.** The survey *"The Evolution of Mixture-of-Experts
Architectures in Large Language Models: Routing, Topology, Load Balancing, and Expert Parallelism"*
(Li, [arXiv 2608.08650](https://arxiv.org/abs/2608.08650)) organizes modern MoE systems along **five
coupled dimensions**. Useful as a checklist: a from-scratch MoE decision is really five decisions, and
they interact.

| Axis | The question it settles | Design example |
|---|---|---|
| **Expert granularity** | Few wide experts or many narrow ones at fixed active-FLOPs? | Fine-grained: DeepSeek-V3 uses 256 routed experts, top-8 per token (verified from its `config.json`: `n_routed_experts: 256`, `num_experts_per_tok: 8`) |
| **Expert topology** | How experts are arranged/shared — always-on shared experts, per-layer independence, tying across layers | DeepSeek-V3 and Kimi-K2 both carry `n_shared_experts: 1` alongside the routed pool; Qwen3-MoE's config declares no shared-expert field |
| **Routing freedom** | How unconstrained the router is — plain top-k, device/node-limited routing, expert-choice | Top-k gating with node-limited routing constrains the all-to-all fan-out |
| **Scope of load balancing** | Per-batch, per-sequence, or aggregate/global balance — and enforced by aux loss or by bias | Aux-loss-free bias-based balancing (DeepSeek-V3) vs a classic auxiliary load-balancing loss |
| **Execution structure** | How the routed compute is actually laid out and parallelized across devices | Expert parallelism + all-to-all; see [ai-llm-inference moe-expert-parallelism.md](../../ai-llm-inference/references/moe-expert-parallelism.md) |

The survey frames these as *coupled*: granularity is not free, because finer experts raise routing and
all-to-all traffic. Serve-side, that coupling is the dominant cost term — treat expert count as a joint
build/serve decision, not a build-time-only one.

**Fine-grained + shared-expert is a common pattern in recent open MoE releases** — many small routed experts, low top-k,
plus (usually) one always-on shared expert to absorb common patterns. Verified expert counts, each read
from the model's own published `config.json` (re-read the config before reusing a count):

| Model | Routed experts | Shared | Active per token |
|---|---|---|---|
| **DeepSeek-V3** | 256 | 1 | top-8 routed |
| **Qwen3-MoE** (235B-A22B) | 128 | none declared in config | top-8 routed |
| **Kimi-K2** | 384 | 1 | top-8 routed |

Note the direction: expert *count* has grown (128 → 256 → 384) while top-k stayed at 8 — that is the
granularity axis being pushed, with active FLOPs roughly held.

**Tied expert layers** — *"Tying the Loop: Tied Expert Layers in Mixture-of-Experts Language Models"*
([arXiv 2606.16825](https://arxiv.org/abs/2606.16825)) shares expert parameters across *consecutive*
transformer layers while keeping independent per-layer routing and attention, cutting MoE memory
footprint roughly 2× (authors' claim). This sits on the topology axis and is adjacent to the
depth/weight-sharing family covered in
[adaptive-depth-and-conditional-compute.md](adaptive-depth-and-conditional-compute.md).

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
| **fp8** (production on Hopper+) | Tensor-core accumulation has limited precision; naive per-tensor fp8 destabilizes | DeepSeek-V3 ([arXiv 2412.19437](https://arxiv.org/abs/2412.19437)): **blockwise/group-128 scaling + high-precision accumulation**; its 16B and 230B ablations found relative loss close to bf16 before the full 671B-MoE run. fp8 tensors use fewer bytes than bf16 — total training memory does **not** halve, since master weights and optimizer state stay at higher precision. Check the current `torchao.float8` and TransformerEngine APIs before implementation. |
| **fp4 (MXFP4 / NVFP4)** (Blackwell) | **Activation & gradient outliers** dominate the 4-bit range and destabilize training | Micro-block scaling, outlier control/clipping, oscillation suppression. In [arXiv 2509.25149](https://arxiv.org/abs/2509.25149), an NVFP4 12B model trained on 10T tokens tracked an FP8 baseline. In a separate 8B, 1T-token comparison, MXFP4 needed 36% more tokens to match NVFP4 loss. These results depend on the tested recipes and models. |

**Rule:** train in **bf16** by default; keep reductions in fp32. fp8 is production-proven on
Hopper+ with a validated recipe, but still demands a bf16 loss-parity check on your own
workload — the hard part is validation, not implementation. fp4 has a genuine 10T-token
result; treat the recipe, not the format, as the open risk. Multi-GPU specifics and the
per-tensor recipe details stay with [ai-distributed-training](../../ai-distributed-training/SKILL.md).

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
