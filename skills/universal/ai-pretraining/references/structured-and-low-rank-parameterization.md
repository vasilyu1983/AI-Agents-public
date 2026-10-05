# Structured and Low-Rank Parameterization

Every `nn.Linear` you wrote in the from-scratch GPT holds a dense `(out, in)` matrix. Dense is the default only because it is the *unconstrained* choice — it makes no assumption about the weight's structure, and it costs `O(d_in · d_out)` parameters and the same order of multiply-accumulates per token. In a transformer block, the four attention projections plus the two (or three, with SwiGLU) FFN projections are essentially all of the parameters and nearly all of the FLOPs. Attention's `QK^T` gets the attention (pun intended) because it is quadratic in sequence length, but at the sequence lengths most models train at, the dense projections dominate the FLOP budget.

Structured parameterization asks: what if `W` is not free? If `W` is constrained to a family that is cheaper to store and to multiply by — low-rank, block-diagonal, a product of butterflies — you buy parameter and FLOP savings at the cost of expressivity. This reference covers that family both as a *training-time* choice (build the structure in from initialization) and as a *post-hoc* compression of an already-trained dense model. Those are genuinely different problems with different failure modes, and conflating them is the most common mistake in this area.

## Table of Contents

- [Canonical Sources](#canonical-sources)
- [Why Dense W Is the Cost Center](#why-dense-w-is-the-cost-center)
- [The Family Tree](#the-family-tree)
- [Comparison Table](#comparison-table)
- [Training From Scratch With Structure](#training-from-scratch-with-structure)
- [Low-Rank as Post-Hoc Compression](#low-rank-as-post-hoc-compression)
- [Low-Rank Inside the Architecture: MLA](#low-rank-inside-the-architecture-mla)
- [LoRA and Friends: the Fine-Tuning Cousin](#lora-and-friends-the-fine-tuning-cousin)
- [Code: a Block Low-Rank Drop-In for nn.Linear](#code-a-block-low-rank-drop-in-for-nnlinear)
- [Code: a Monarch Sketch](#code-a-monarch-sketch)
- [Decision Guidance: Structure vs Pruning vs Quantization](#decision-guidance-structure-vs-pruning-vs-quantization)
- [Common Mistakes](#common-mistakes)

## Canonical Sources

- Monarch: Expressive Structured Matrices for Efficient and Accurate Training — Dao, Chen, Sohoni, Desai, Poli, Grogan, Liu, Rao, Rudra, Ré — https://arxiv.org/abs/2204.00595
- BLAST: Block-Level Adaptive Structured Matrices for Efficient Deep Neural Network Inference (NeurIPS 2024) — Lee, Kwon, Qu, Kim — https://arxiv.org/abs/2410.21262
- Building on Efficient Foundations: Effectively Training LLMs with Structured Feedforward Layers — Wei, Moalla, Pascanu, Gulcehre — https://arxiv.org/abs/2406.16450
- SVD-LLM: Truncation-aware Singular Value Decomposition for Large Language Model Compression — Wang, Zheng, Wan, Zhang — https://arxiv.org/abs/2403.07378
- ASVD: Activation-aware Singular Value Decomposition for Compressing Large Language Models — Yuan, Shang, Song, Yang, Wu, Yan, Sun — https://arxiv.org/abs/2312.05821
- Memory-Efficient Acceleration of Block Low-Rank Foundation Models on Resource Constrained GPUs — Abillama, Lee, Dong, Blaauw, Sylvester, Kim — https://arxiv.org/abs/2512.20861
- DeepSeek-V2 (Multi-head Latent Attention: low-rank KV compression) — DeepSeek-AI — https://arxiv.org/abs/2405.04434

## Why Dense W Is the Cost Center

Count it out for one block of your GPT, hidden size `d`, FFN expansion `4d`:

- Attention projections `W_q, W_k, W_v, W_o`: `4d²` parameters.
- FFN `W_in, W_out`: `8d²` parameters.

So `12d²` per block, and the forward matmul cost is `2 · 12d²` FLOPs per token. Everything else — norms, activations, residual adds, softmax — is `O(d)` or `O(T)` per token and vanishes in the accounting. Attention scores are `O(T²d)` per block, which only overtakes the projections once `T` is on the order of `d` — and modern serving keeps `T` well under that for most requests, which is why the projection matrices, not the attention map, are what structured parameterization targets.

Two separate resources are at stake and they do not always move together:

- **Parameters** — what you store, what the optimizer states multiply (AdamW carries 2 extra copies), what you must move from HBM to SRAM.
- **FLOPs** — what the tensor cores actually do.

A structure can cut one without cutting the other in *wall-clock* terms. That gap is where most disappointment lives: a matrix with 4× fewer FLOPs on paper can be slower than dense, because the dense path runs at near-peak on a tensor core and the structured path runs a memory-bound, poorly-tiled kernel. Abillama et al. make exactly this point for block low-rank inference — their roofline analysis finds that although BLR methods achieve theoretical savings and practical speedups for single-token inference, *multi-token inference often becomes memory-bound in practice, increasing latency despite compiler-level optimizations in PyTorch*. Their fix is custom Triton kernels with partial fusion and memory-layout optimization, not a different matrix family.

## The Family Tree

All of these replace a dense `W ∈ R^{n×n}` with a parameterized subfamily.

**Low-rank: `W ≈ AB`**, with `A ∈ R^{n×r}`, `B ∈ R^{r×n}`, `r ≪ n`. Parameters `2nr` instead of `n²`. The classic and the weakest: it can only represent matrices whose singular value spectrum decays fast. Trained transformer weights are often *not* low-rank in this sense — their spectra are flatter than people expect — which is why naive truncation of a trained model degrades sharply, and why the post-hoc methods below all add a correction term. The likely mechanism is **superposition**: Elhage et al. show in [Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html) (2022) that a layer can represent more features than it has dimensions by storing them in overlapping, non-orthogonal directions. Read as interpretation rather than proof, that predicts exactly the flat spectrum you measure — if the useful directions are packed at near-full dimensionality, there is no small subspace to throw away, and truncating `W` deletes whole features rather than noise. This is the pivot that separates compression from adaptation, and it is picked up again in [LoRA and Friends](#lora-and-friends-the-fine-tuning-cousin) below.

**Block-diagonal.** Partition input and output into `b` blocks and allow no cross-block mixing: parameters and FLOPs both drop by `b×`. Extremely hardware-friendly (it is just `b` independent small GEMMs, or one batched GEMM) but it destroys global mixing on its own — a stack of block-diagonal layers with fixed blocks can never move information between blocks.

**Butterfly.** A product of `O(log n)` sparse factors with the connectivity pattern of an FFT. It recovers global mixing in `O(n log n)` and can express nearly all the transforms people care about (DFT, Hadamard, convolutions, permutations). Its problem is practical, not theoretical: `log n` sequential sparse factors with irregular access patterns are hostile to GPUs.

**Monarch (Dao et al. 2022).** The engineering fix for butterfly. A Monarch matrix is *parameterized as products of block-diagonal matrices* interleaved with permutations — so the whole thing reduces to batched dense GEMMs plus reshapes, which is exactly what a GPU wants. Monarch retains much of butterfly's expressivity (it is a subclass rich enough to contain many structured transforms) while running as ordinary tensor-core work. Its other distinguishing property is that projecting a dense matrix onto the Monarch class has an **analytical optimal solution** despite the problem being nonconvex — meaning you can convert a pretrained dense `W` into a Monarch approximation without gradient descent, which is what makes dense-to-structured fine-tuning workflows possible. Dao et al. report speeding up ViT and GPT-2 training on ImageNet classification and Wikitext-103 language modeling by 2x with comparable model quality, and 23% faster BERT pretraining.

**Kronecker: `W = A ⊗ B`.** With `A ∈ R^{n₁×n₁}`, `B ∈ R^{n₂×n₂}`, `n = n₁n₂`, you store `n₁² + n₂²` parameters. Astonishingly compact (roughly `2n` in the balanced case) and the matvec factorizes into two small GEMMs over a reshaped tensor. The catch is severity of constraint: `A ⊗ B` forces a rigid multiplicative coupling between row and column structure that real weights rarely have, so a single Kronecker factor is usually too restrictive; sums of Kronecker products are the practical form.

**BLAST (Lee et al., NeurIPS 2024).** Rather than committing to one structure a priori, BLAST partitions the matrix into blocks and gives each block a *shared* set of low-rank factors with per-block diagonal coefficients — a block-level adaptive structure. The stated design goal is exactly that flexibility: it "can represent various types of structures that are either learned from data or computed from pre-existing weight matrices," i.e. it subsumes low-rank, block-diagonal, and Monarch-like patterns as special cases and *learns* which one fits. That is why it appears both as a training parameterization and as a compression target. Lee et al. report that for medium-sized models such as ViT and GPT-2, training with BLAST weights boosts performance while reducing complexity by 70% and 40% respectively; and that for large foundation models such as Llama-7B and DiT-XL, the BLAST matrix achieves a 2x compression while exhibiting the lowest performance degradation among all tested structured matrices.

**Structured FFN layers for LLM training (Wei et al. 2024).** The most directly relevant study for a from-scratch builder, because it targets the FFN — the biggest parameter block — *from a training-from-scratch perspective*, at up to 1.3B parameters, in transformer LLMs rather than convnets. Its two findings that matter to you: structured parameterizations exhibit poor training dynamics when used from initialization, which the authors address with a proposed **self-guided training** regime; and the scaling behavior is favorable — they report "steeper curves in scaling training FLOPs, along with a favorable scaling trend in the overtraining regime," concluding that *wide and structured networks can utilize training FLOPs more efficiently, with fewer parameters and lower loss than dense models at their optimal trade-off*.

## Comparison Table

For an `n × n` layer. "Expressivity" is qualitative and relative to dense. "HW friendly" means: does it map onto batched dense GEMMs on a tensor core?

| Structure | Parameters | Matmul cost | Expressivity | HW friendly |
|---|---|---|---|---|
| Dense | `n²` | `O(n²)` | full | yes (baseline, near-peak) |
| Low-rank `AB`, rank `r` | `2nr` | `O(nr)` | only fast-decaying spectra | yes (two thin GEMMs) |
| Block-diagonal, `b` blocks | `n²/b` | `O(n²/b)` | no cross-block mixing | yes (batched GEMM) |
| Butterfly | `O(n log n)` | `O(n log n)` | very high (FFT-class transforms) | poor (sequential sparse factors) |
| Monarch | `O(n^1.5)` typical | sub-quadratic | high; analytic dense projection | yes (block-diag GEMMs + permutes) |
| Kronecker `A ⊗ B` | `n₁² + n₂²` | `O(n(n₁+n₂))` | low alone; rigid coupling | yes (two reshaped GEMMs) |
| BLAST | tunable (block rank) | tunable | adaptive; subsumes the above | yes (batched low-rank GEMMs) |

Read the middle two columns as *theoretical* cost. Wall-clock follows only with a kernel that keeps the arithmetic intensity high — see the memory-bound result in the previous section.

## Training From Scratch With Structure

If you are training with structure from step zero, three things bite.

**Initialization.** A dense layer initialized with std `1/√d` has a known forward/backward variance profile. A product `AB` does not inherit it — naive per-factor init makes the product's variance the product of variances, and the signal either vanishes or explodes through depth. Initialize so the *product* matches the dense variance you would have used, or initialize `A` normally and `B` at zero-plus-noise and let it grow.

**Optimization dynamics.** Factorized parameterizations have a rescaling symmetry (`A → cA`, `B → B/c` leaves the product unchanged) which interacts badly with weight decay and with adaptive optimizers, and the effective learning rate on the product is no longer the learning rate you set. This is the concrete mechanism behind the "poor training dynamics from initialization" that Wei et al. propose self-guided training to address.

**Where to apply it.** The FFN is the right first target: it is the largest parameter block, it has no cross-token coupling to complicate things, and structure there does not interfere with attention's positional machinery. Structuring `W_q`/`W_k` interacts with RoPE and with head layout; structuring `W_o` is comparatively safe. Start with FFN-only, measure, then expand.

## Low-Rank as Post-Hoc Compression

Different problem: `W` is already trained and you want a smaller model without retraining. The obvious move is SVD, keep the top `r` singular values, done. It does not work well, for two reasons the two main papers each name.

**Reason 1 — singular value magnitude is not compression loss.** Truncating the smallest singular values of `W` minimizes `‖W − Ŵ‖_F`, but you do not care about the weight error; you care about the *output* error `‖(W − Ŵ)x‖` over the real activation distribution. Those differ whenever the input distribution is anisotropic, which it always is. SVD-LLM's answer is a truncation-aware **data whitening** step: transform so there is a direct mapping between singular values and compression loss, then truncate. Its second component is a parameter update with sequential low-rank approximation to compensate for the accuracy degradation left after truncation — i.e. the correction term that naive SVD lacks.

**Reason 2 — activation outliers.** LLM activations have heavy-tailed channels; a few input dimensions carry enormous magnitude. A weight column multiplying a huge-activation channel matters far more than its singular value suggests. ASVD's answer is to transform the weight matrix based on the activation distribution so that activation outliers are absorbed into the transformed weights, plus an iterative calibration to set a per-layer decomposition budget rather than a uniform rank — layers differ substantially in how much rank they can lose. ASVD is training-free, and the authors also apply it to the KV cache.

**Practical rule.** Plain rank truncation is defensible only when (a) the layer's spectrum genuinely decays fast — check it, do not assume — and (b) the compression ratio is mild. Once you push past mild ratios, activation-aware weighting stops being an optimization and becomes a requirement; the gap between naive SVD and activation-aware SVD widens with the compression ratio, which is precisely the regime both papers emphasize. And prefer a *block* low-rank target (Monarch, BLAST) over a global one: Abillama et al. summarize the reason plainly — traditional low-rank methods often incur sharp accuracy drops, while BLR approaches such as Monarch and BLAST better capture the underlying structure.

Calibration data matters. Whitening and activation statistics are estimated from a calibration set; if that set does not resemble deployment traffic, you have optimized the wrong error. Treat calibration-set choice as a hyperparameter and evaluate on held-out domains.

## Low-Rank Inside the Architecture: MLA

DeepSeek-V2's Multi-head Latent Attention is the same factorization idea applied to the KV path rather than to a weight matrix. Instead of caching full per-head `K` and `V`, MLA projects them down to a shared latent vector and caches only that, reprojecting up inside attention — "MLA guarantees efficient inference through significantly compressing the Key-Value (KV) cache into a latent vector." The low-rank bottleneck is trained in from the start, so there is no post-hoc truncation error to correct: the model learns weights that are good *given* the bottleneck. That is the general lesson of this whole reference in one architecture — structure designed in beats structure imposed afterward. The MLA-vs-GQA tradeoff (cache size, arithmetic intensity, RoPE handling) is covered in [`modern-architecture-deltas.md`](modern-architecture-deltas.md); this section exists only to place MLA in the low-rank family tree.

## LoRA and Friends: the Fine-Tuning Cousin

LoRA, QLoRA, and DoRA are the *adaptation* application of the identical factorization: freeze dense `W`, learn a low-rank update `ΔW = BA`, and merge it at inference. The structural math is the same `W ≈ AB` above, but the objective is different — you are not compressing `W`, you are constraining the *update* to a low-dimensional subspace to make fine-tuning cheap in memory and to keep many task adapters swappable against one base model. That is why LoRA works where SVD truncation fails, and it is the superposition argument from [The Family Tree](#the-family-tree) cashed out: `W` itself is near-full-rank because its features are packed in superposition, but Hu et al. ([LoRA](https://arxiv.org/abs/2106.09685), 2021) motivate the method on the premise that the *change* `ΔW` induced by adapting to one downstream task has low intrinsic rank — their abstract reports "an empirical investigation into rank-deficiency in language model adaptation, which sheds light on the efficacy of LoRA." Low-rank the update, not the weight. Do not reach for LoRA when the goal is a smaller deployed model: a merged LoRA is exactly the same size as the dense base. Full treatment lives in [`../../ai-post-training/SKILL.md`](../../ai-post-training/SKILL.md) and [`../../ai-llm/SKILL.md`](../../ai-llm/SKILL.md).

## Code: a Block Low-Rank Drop-In for nn.Linear

```python
class BlockLowRankLinear(nn.Module):
    """Drop-in for nn.Linear(d_in, d_out). Partitions into a bh x bw grid of
    blocks; each block is its own rank-r factorization. Setting bh=bw=1 gives
    plain low-rank; large r approaches a dense matrix built from bh x bw
    low-rank blocks -- NOT block-diagonal, because the second einsum contracts
    w, so every output block sees every input block. Block-diagonal needs
    bh == bw and a diagonal-only (h == w) contraction."""
    def __init__(self, d_in, d_out, bh=4, bw=4, rank=32, bias=True):
        super().__init__()
        assert d_in % bw == 0 and d_out % bh == 0
        self.bh, self.bw, self.r = bh, bw, rank
        self.din_b, self.dout_b = d_in // bw, d_out // bh
        # U: (bh, bw, dout_b, r)   V: (bh, bw, r, din_b)
        self.V = nn.Parameter(torch.randn(bh, bw, rank, self.din_b) / self.din_b**0.5)
        # std=(r*bw)^-0.5, not r^-0.5: the forward sums over bw blocks, so the
        # naive r^-0.5 overshoots dense output std by sqrt(bw).
        self.U = nn.Parameter(torch.randn(bh, bw, self.dout_b, rank) * (rank * bw)**-0.5)
        self.bias = nn.Parameter(torch.zeros(d_out)) if bias else None

    def forward(self, x):                                  # x: (..., d_in)
        lead = x.shape[:-1]
        xb = x.reshape(-1, self.bw, self.din_b)            # split input into bw column blocks
        # Contract down to rank r FIRST -- this is where the FLOPs are saved.
        # Dense: d_in*d_out MACs. Here: bh*bw*r*(din_b + dout_b) MACs, i.e. a
        # factor of (din_b*dout_b) / (r*(din_b + dout_b)) cheaper. Break-even is
        # r = din_b*dout_b / (din_b + dout_b) -- HALF the harmonic mean. At
        # din_b = dout_b = 256 that is r = 128 (harmonic mean would say 256).
        z = torch.einsum('nwi,hwri->nhwr', xb, self.V)     # (N, bh, bw, r)
        yb = torch.einsum('nhwr,hwor->nho', z, self.U)     # (N, bh, dout_b) -- sums over bw blocks
        y = yb.reshape(*lead, -1)
        return y if self.bias is None else y + self.bias
```

The saving is entirely in the `einsum` order: never materialize the `(d_out, d_in)` product. Each block does `din_b → r → dout_b` instead of `din_b → dout_b`. Both einsums are batched dense GEMMs, which is the Monarch/BLAST design principle — stay on the tensor cores. **Benchmark before believing it**: at small `r` these kernels are memory-bound and can lose to `nn.Linear` in wall-clock even while winning on FLOPs, which is the failure Abillama et al. address with custom Triton kernels.

## Code: a Monarch Sketch

Monarch is the other shape worth writing out, because it is where the block-diagonal ceiling gets broken: two block-diagonal factors with a fixed permutation ("perfect shuffle") between them, so information crosses block boundaries without ever leaving batched dense GEMM territory.

```python
class MonarchLinear(nn.Module):
    """Monarch (Dao et al. 2022) for a square d x d layer: block-diagonal ->
    perfect shuffle -> block-diagonal. d must be divisible by nblocks."""
    def __init__(self, d, nblocks=8):
        super().__init__()
        assert d % nblocks == 0
        self.n, self.b = nblocks, d // nblocks
        self.L = nn.Parameter(torch.randn(nblocks, self.b, self.b) * self.b**-0.5)
        self.R = nn.Parameter(torch.randn(nblocks, self.b, self.b) * self.b**-0.5)

    def forward(self, x):                                # x: (..., d)
        lead, n, b = x.shape[:-1], self.n, self.b
        z = x.reshape(-1, n, b).transpose(0, 1)          # (n, N, b): n blocks
        z = torch.bmm(z, self.L)                         # block-diagonal factor 1
        z = z.permute(1, 2, 0).reshape(-1, n, b)         # perfect shuffle
        z = torch.bmm(z.transpose(0, 1), self.R)         # block-diagonal factor 2
        return z.transpose(0, 1).reshape(*lead, -1)
# d=64, nblocks=8: params = 2*d*(d/nblocks) = 1024 vs dense d^2 = 4096 (4x fewer);
# MACs identical to the param count here, 1024 vs 4096. Verified against the
# materialised dense equivalent (push an identity through, then compare x @ W):
#   out shape (5, 64); allclose(y, x @ W, atol=1e-5) passes.
# The permutation is load-bearing: W's nonzero fraction is 1.0 -- fully mixing.
# Drop the shuffle and you get two stacked block-diagonals, which never mix.
```

The permutation costs no FLOPs and no parameters; it is a reshape. That is the entire trick — it is why Monarch buys global mixing at block-diagonal cost, and why the sub-quadratic row in the [comparison table](#comparison-table) is reachable in wall-clock rather than only on paper.

## Decision Guidance: Structure vs Pruning vs Quantization

Pruning and quantization are covered in [`../../ai-llm-inference/references/pruning-and-sparsity.md`](../../ai-llm-inference/references/pruning-and-sparsity.md) and [`../../ai-llm-inference/references/quantization-patterns.md`](../../ai-llm-inference/references/quantization-patterns.md). Choose between them on what you actually control:

- **You are training the model.** Structured parameterization is the strongest option, and the only one of the three that reduces *training* cost — quantization-aware training and pruning-during-training mostly pay off at inference. Wei et al.'s from-scratch FLOP-efficiency result is the argument here.
- **You have a trained model and need it smaller, fast, with no retraining.** Quantization first is an ecosystem heuristic, not a law: weight-only INT4/FP8 has mature kernels and tooling, and the accuracy cost per bit saved is better characterised than the accuracy cost per rank removed. The ordering is a statement about kernel support, and it moves as support moves.
- **You have already quantized and need more.** Now structured low-rank compression (SVD-LLM / ASVD / BLAST) earns its place, because it removes a different axis of redundancy than bit-width does.

**The local rule that is not negotiable.** *When you factorize at all, factorize before you quantize the factors.* Decompose on full-precision weights using activation-aware statistics, then quantize the factors, then calibrate end to end. Reversing it means you are decomposing quantization noise — the spectrum you are trying to truncate has already been destroyed by rounding.

The full ordering across all four levers (prune, quantize, factorize, distill), and the quality-vs-bytes-vs-latency frame for choosing among them, lives in one shared matrix: [`../../ai-llm-inference/references/pruning-and-sparsity.md#composability-prune-quantize-factorize-distill`](../../ai-llm-inference/references/pruning-and-sparsity.md#composability-prune-quantize-factorize-distill). Use that, not a restatement here.

## Common Mistakes

- **Assuming trained weights are low-rank.** Plot the singular value spectrum per layer before committing. Many transformer weights have a flat tail that carries real signal; the low-rank prior is an assumption, not a fact.
- **Reporting FLOP savings as speedups.** A structured layer with 4× fewer FLOPs can be slower in wall-clock than dense. Report measured latency on the target device, or say you did not measure it.
- **Uniform rank across all layers.** Layer sensitivity to rank truncation varies substantially — ASVD's iterative calibration exists precisely to allocate rank per layer. A uniform budget wastes rank on tolerant layers and destroys sensitive ones.
- **Naive SVD at aggressive compression ratios.** Without whitening (SVD-LLM) or activation-aware weighting (ASVD), the truncation minimizes the wrong error. The gap grows with the ratio.
- **Calibrating on the wrong distribution.** Activation-aware methods are only as good as the calibration set. Evaluate on held-out domains, not on the calibration data.
- **Confusing LoRA with compression.** A merged LoRA model is the same size as the base. LoRA constrains the *update*, not the weight.
- **Structuring attention projections first.** `W_q`/`W_k` interact with RoPE and head layout. The FFN is the larger, safer, higher-return target — start there.
- **Training a structured net with dense-style initialization and hyperparameters.** Factorized layers have rescaling symmetries and a different variance profile; expect to re-tune LR and weight decay, and expect the first attempt to underperform dense for reasons that are optimization-side, not capacity-side.

*Paper claims in this reference are quoted from the cited abstracts; figures are reproduced verbatim and are not re-derived here. Re-read the paper before reusing a figure.*
