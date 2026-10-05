# Adaptive Depth and Conditional Compute

The GPT you built runs every token through every layer. That is a design choice, not a law: the token `the` and the token that completes a three-hop arithmetic chain get identical FLOPs. **Conditional computation** is the family of architectures that break this uniformity — compute per token becomes a function of the token. Mixture-of-Experts varies compute along the **width** axis (which FFN parameters fire); this reference covers the **depth** axis (how many blocks a token passes through) and its close relative, **weight sharing across depth** (the same block applied repeatedly).

The two axes are separable and composable, and the depth axis has the more interesting failure modes: skipping a layer for one token breaks the KV cache that later tokens expect, and routing depends on tokens that have not been generated yet. This reference works through Mixture-of-Depths, early-exit inference, looped/recursive transformers, and expert tying, then gives a decision table for picking a lever. For MoE itself see [architecture-limitations-and-workarounds.md](architecture-limitations-and-workarounds.md#5-mlp--ffn-and-mixture-of-experts) — it is not re-explained here.

## Table of Contents

- [Canonical Sources](#canonical-sources)
- [Conditional Computation: the Width/Depth Split](#conditional-computation-the-widthdepth-split)
- [Mixture-of-Depths](#mixture-of-depths)
- [Early Exit and Per-Token Depth at Inference](#early-exit-and-per-token-depth-at-inference)
- [Looped Transformers and Cross-Layer Weight Sharing](#looped-transformers-and-cross-layer-weight-sharing)
- [A Looped Block With Per-Token Halting](#a-looped-block-with-per-token-halting)
  - [Mixture-of-Depths, Minimally](#mixture-of-depths-minimally)
- [Serving Looped Models](#serving-looped-models)
- [Does Depth Even Earn Its Keep?](#does-depth-even-earn-its-keep)
- [Weight Sharing Beyond Depth](#weight-sharing-beyond-depth)
- [Modular Networks as the Umbrella](#modular-networks-as-the-umbrella)
- [Why the Depth Axis Is Harder to Train](#why-the-depth-axis-is-harder-to-train)
- [Decision Table](#decision-table)
- [Common Mistakes](#common-mistakes)

## Canonical Sources

- Mixture-of-Depths: Dynamically allocating compute in transformer-based language models — Raposo, Ritter, Richards, Lillicrap, Humphreys, Santoro — https://arxiv.org/abs/2404.02258
- LayerSkip: Enabling Early Exit Inference and Self-Speculative Decoding — Elhoushi, Shrivastava, Liskovich, et al. — https://arxiv.org/abs/2404.16710
- TIDE: Token-Informed Depth Execution for Per-Token Early Exit in LLM Inference — Jaber & Jaber — https://arxiv.org/abs/2603.21365
- Universal Transformers — Dehghani, Gouws, Vinyals, Uszkoreit, Kaiser — https://arxiv.org/abs/1807.03819
- ALBERT: A Lite BERT for Self-supervised Learning of Language Representations — Lan, Chen, Goodman, Gimpel, Sharma, Soricut — https://arxiv.org/abs/1909.11942
- Mixture-of-Recursions: Learning Dynamic Recursive Depths for Adaptive Token-Level Computation (NeurIPS 2025) — Bae, Kim, Bayat, et al. — https://arxiv.org/abs/2507.10524
- AdaPonderLM: Gated Pondering Language Models with Token-Wise Adaptive Depth — Song, Li, Wang, et al. — https://arxiv.org/abs/2603.01914
- Depth-adaptive Inference of Looped Language Models via Continuous Depth Batching — Schwethelm, Rueckert, Kaissis — https://arxiv.org/abs/2608.09444
- Do Language Models Use Their Depth Efficiently? (NeurIPS 2025) — Csordás, Manning, Potts — https://arxiv.org/abs/2505.13898
- Tying the Loop — Tied Expert Layers in Mixture-of-Experts Language Models — https://arxiv.org/abs/2606.16825
- Modular Deep Learning (survey) — Pfeiffer, Ruder, Vulić, Ponti — https://arxiv.org/abs/2302.11529

## Conditional Computation: the Width/Depth Split

A dense transformer's FLOPs per token are fixed by `n_layer × (attention + FFN)`. Conditional computation makes some part of that expression token-dependent. Two orthogonal ways to do it:

| Axis | What varies | Canonical method | Parameter count |
|---|---|---|---|
| **Width** | Which subset of FFN parameters activates | MoE top-k expert routing | Grows (many experts stored) |
| **Depth** | How many blocks the token traverses | MoD, early exit, looped-with-halting | Flat or shrinks (blocks reused) |

The width axis buys *capacity at fixed FLOPs* — more parameters, same compute per token. The depth axis buys *FLOPs savings at fixed capacity*, or with weight sharing, *capacity at fixed parameters*. They target different constraints, which is why "MoE or MoD?" is usually the wrong question; see the [decision table](#decision-table).

One structural asymmetry matters throughout. Width routing is **local**: skipping an expert changes only that layer's output. Depth routing is **global**: skipping a block means no key/value vectors were written for that token at that layer, so every later token that attends back to it finds a hole. Nearly every complication below descends from this.

## Mixture-of-Depths

MoD (Raposo et al., 2024) puts a router before each block. The router scores every token in the sequence, and the **top-k** tokens by score enter the block's attention and MLP; the rest bypass it via the residual stream. Two design choices make this practical:

- **Static compute graph.** `k` is fixed a priori as a fraction of sequence length (a *capacity*), so tensor shapes are known at compile time. The paper stresses this contrasts with conditional-computation methods that produce dynamic shapes: compute is "entirely predictable in sum total, but dynamic and context-sensitive at the token-level."
- **Top-k, not threshold.** Ranking tokens against each other guarantees the budget is met exactly, instead of hoping a threshold produces roughly the right count.

The paper reports these models "match baseline performance for equivalent FLOPS and wall-clock times to train, but require a fraction of the FLOPs per forward pass, and can be upwards of 50% faster to step during post-training sampling."

**The causal-routing problem.** Top-k over the sequence is a non-causal operation — deciding whether token *i* is in the top-k requires seeing tokens that come after it. That is fine during training on a full sequence, but at autoregressive inference the future does not exist yet. The paper's fix is an **auxiliary predictor**: a small classifier trained to predict, from the token's own representation alone, whether it would have been in the top-k, so the routing decision becomes causal. This is a real training-inference asymmetry, not a footnote.

**Why MoD is not a default.** No single disqualifying result — an accumulation of friction:

- The auxiliary predictor adds a train/serve mismatch and its own accuracy failure modes.
- Skipped blocks write no KV entries at that layer, complicating cache layout and any KV-sharing scheme.
- The wins land mostly as FLOPs reduction, and FLOPs are frequently not the binding constraint at inference — memory bandwidth is. A method that halves FLOPs while leaving weight traffic untouched can leave decode latency roughly unchanged.
- MoE was absorbing the same engineering attention on the width axis, where the KV-hole problem does not exist.

MoD is best read as the clearest statement of the depth-routing idea, and the source of the vocabulary (capacity, top-k routing per block) that later work reuses.

## Early Exit and Per-Token Depth at Inference

Early exit asks the inverse question: rather than skipping blocks in the middle, stop early and decode from an intermediate layer when the representation has already settled.

**The missing-KV problem.** If token *i* exits at layer 8 of 32, layers 9–32 hold no K/V for it. Token *i+1*, running to layer 20, will attend at layer 15 to a cache with a gap. Three families of answers exist: **compute-and-discard** (run all layers anyway for the cache — no savings), **copy-forward** (propagate the exit layer's hidden state up, filling the missing K/V approximately), and **defer** (batch up the missing layers and fill them later). Any early-exit paper that does not say which one it uses has not addressed the hard part.

**LayerSkip** (Elhoushi et al., 2024) treats early exit as a *training* problem first. It applies layer dropout with low rates early and higher rates later, plus an early-exit loss where all layers share one exit head. The paper states this "increases the accuracy of early exit at earlier layers, without adding any auxiliary layers or modules." It then adds **self-speculative decoding**: exit early to draft, verify and correct with the remaining layers of the same model. Because draft and verifier are one model, the memory footprint is smaller than two-model speculative decoding and compute/activations are shared. The paper reports task-dependent speedups — up to 2.16× on CNN/DM summarization, 1.82× on coding, 2.0× on TOPv2 semantic parsing — measured on Llama models of several sizes; treat these as the reported ceiling on those tasks, not a general expectation.

Self-speculative decoding is the important structural idea: it converts early exit from an *approximation* (accept whatever the shallow exit said) into an *exact* method (the full stack verifies), so quality loss goes to zero and only the speedup is at risk.

**TIDE** (Jaber & Jaber, 2026) is the post-training end of the spectrum: tiny learned routers at periodic checkpoint layers pick, per token, the earliest layer whose hidden state has converged. No retraining of the base model; calibration is cheap and the router checkpoint is small. The abstract reports single-batch prefill-latency and throughput improvements in the single-digit-percent range on one A100 / DeepSeek-R1-Distill-8B configuration, with 98–99% of tokens exiting early during decoding while retaining correctness on multi-step math. Read those as one hardware/model datapoint, not a portable figure — the gap between "98–99% of tokens exit early" and single-digit latency gains is itself the lesson: **exiting early is not the same as saving wall-clock time**, because the cache still has to be maintained and decode is bandwidth-bound.

## Looped Transformers and Cross-Layer Weight Sharing

Instead of *N* distinct blocks, keep *one* block (or a small stack) and apply it *N* times. Depth becomes a runtime knob rather than a parameter-count commitment.

**Universal Transformer** (Dehghani et al., 2018) is the ancestor: a recurrent-in-depth transformer with a dynamic halting mechanism (Adaptive Computation Time), which the paper notes can be Turing-complete under certain assumptions. **ALBERT** (Lan et al., 2019) applied cross-layer parameter sharing to BERT as one of two parameter-reduction techniques (the other being factorized embedding parameterization), reporting models that scale better than BERT with fewer parameters. ALBERT is the cleanest demonstration that sharing weights across depth costs less quality than the parameter reduction would suggest.

**Mixture-of-Recursions** (Bae et al., NeurIPS 2025) is the modern synthesis and the paper to read if you read one. MoR unifies the two efficiency axes that prior work treated separately: a shared stack of layers reused across recursion steps gives *parameter* efficiency, while lightweight routers assign *different recursion depths to individual tokens* for adaptive compute. Crucially it confronts the KV problem head-on — attention at a given recursion depth runs only among tokens still active there, and only their KV pairs are cached, so the depth adaptivity buys memory-access savings rather than costing them. A KV-sharing variant reuses the first recursion's KV to cut memory further. Across 135M–1.7B parameters the paper reports a new Pareto frontier: at equal training FLOPs and smaller model sizes, lower validation perplexity, better few-shot accuracy, and higher throughput than vanilla and prior recursive baselines. Magnitudes are not restated here — check the paper's tables for your scale.

**AdaPonderLM** (Song et al., 2026) is the halting-mechanism refinement. Its target is that most pretrained recurrent LMs run a *fixed* iteration count, wasting compute on easy tokens. It learns token-wise early exiting during pretraining with iteration-specific MLP gates under a **monotonic halting mask** (once halted, a token stays halted — this is what makes the mask consistent), plus KV reuse for halted tokens so train and test agree. The paper reports reducing inference compute "at about 10%" while maintaining comparable perplexity, on Pythia backbones 70M–410M pretrained and up to 2.8B continued-pretrained. Its most useful finding is diagnostic rather than performance: the learned gates allocate more computation to high-NLL (hard) tokens, and under iso-FLOPs the learned halting policy beats fixed pruning — i.e. adaptive depth wins by putting compute in the *right* places, not merely by lowering average depth.

## A Looped Block With Per-Token Halting

Minimal sketch in the from-scratch style: one shared block, up to `max_loops` iterations, a per-token halting gate with a monotonic mask. Two details carry most of the correctness: **a token takes the remainder on the step it halts**, not only on the last step (otherwise mass is lost); and **the block runs only on live tokens** via gather/scatter, which is where the compute saving actually comes from.

```python
class LoopedBlock(nn.Module):
    def __init__(self, block, n_embd, max_loops=8, threshold=0.99, eps=1e-4):
        super().__init__()
        self.block = block                      # ONE Block, reused every iteration
        self.halt = nn.Linear(n_embd, 1)        # per-token halting gate
        self.max_loops, self.threshold, self.eps = max_loops, threshold, eps

    def forward(self, x):                       # x: (B, T, n_embd)
        B, T, D = x.shape
        cum   = torch.zeros(B, T, device=x.device)   # accumulated halt prob
        out   = torch.zeros_like(x)
        still = torch.ones(B, T, device=x.device)    # 1.0 while not halted
        ponder = torch.zeros(B, T, device=x.device)  # depth actually used
        for step in range(self.max_loops):
            active = still > self.eps
            if not active.any():
                break                                     # every token has halted
            idx = active.nonzero(as_tuple=False)          # gather: live tokens only
            xa = x[idx[:, 0], idx[:, 1]]                  # (N, D), N <= B*T
            ya = self.block(xa)                           # shared weights, N tokens
            x = x.clone(); x[idx[:, 0], idx[:, 1]] = ya   # scatter back
            p = torch.zeros(B, T, device=x.device)
            p[idx[:, 0], idx[:, 1]] = torch.sigmoid(self.halt(ya)).squeeze(-1)
            last = (step == self.max_loops - 1)
            # a token takes the REMAINDER on the step it crosses the threshold
            halting_now = ((cum + still * p) >= self.threshold) | last
            w = torch.where(halting_now, still, still * p) * active.float()
            out = out + w.unsqueeze(-1) * x                # weighted mixture of depths
            ponder = ponder + active.float()
            cum = cum + w
            # monotonic: never revives; halted tokens are zeroed, not decayed
            still = torch.where(halting_now, torch.zeros_like(still), still * (1 - p))
        return out, ponder                                 # add ponder.mean() to the loss
```

```text
# B=4, T=16, D=32, max_loops=8, halt bias +0.5
active tokens per step: [64, 64, 64, 64, 64, 11]
weight-sum min/max: 0.9999999403953552 1.0000001192092896   # sums to 1.0, atol 1e-6
ponder mean: 5.172 of max 8
```

Four things to notice. The halting mask is **monotonic** — `still` only ever shrinks, matching AdaPonderLM's construction. The threshold branch and the remainder are the **same** branch, so output weights sum to exactly one; zeroing `still` on a threshold crossing *without* paying the remainder there silently drops ~1% of the mixture mass (measured 0.990–0.996 on the same seed with that bug). The **gather/scatter** is what makes halting a compute saving rather than a compute-and-discard — the run above invokes the block on 11 tokens on the final step instead of 64. And `ponder` must be penalized in the loss (a small coefficient times `ponder.mean()`), or the model halts nowhere and you have simply built a fixed-depth model with extra steps.

This is still the **training-time** form: the mixture over depths, over a full sequence, with no KV cache. Inference adds the cache maintenance for halted tokens (AdaPonderLM's KV reuse, MoR's active-token-only caching) that this sketch does not model, and the `break` becomes exactly the batching problem below.

### Mixture-of-Depths, Minimally

MoD is the other end of the routing spectrum: no accumulation, no halting state — one router, one top-k, one block, per layer.

```python
class MoDBlock(nn.Module):
    def __init__(self, block, n_embd, capacity=0.5):
        super().__init__()
        self.block, self.capacity = block, capacity
        self.router = nn.Linear(n_embd, 1)

    def forward(self, x):                                  # x: (B, T, D)
        B, T, D = x.shape
        k = max(1, int(self.capacity * T))                 # static: shape known at compile
        scores = self.router(x).squeeze(-1)                # (B, T) raw logits
        idx = scores.topk(k, dim=1).indices                # (B, k) selected tokens
        gather = idx.unsqueeze(-1).expand(-1, -1, D)
        xs = x.gather(1, gather)                           # (B, k, D)
        ys = self.block(xs)                                # block runs on k of T tokens
        w = scores.gather(1, idx).unsqueeze(-1)            # RAW score (not sigmoid):
        return x.scatter_add(1, gather, w * ys)            # keeps router on the grad path
```

```text
# B=2, T=16, D=32, capacity=0.5 -> k=8
in (2, 16, 32)  block saw (2, 8, 32)  out (2, 16, 32)
router.weight.grad is not None after backward: True
```

The score multiplies the block output deliberately — that is the whole mechanism by which a discrete top-k selection yields a gradient for the router (see [Why the Depth Axis Is Harder to Train](#why-the-depth-axis-is-harder-to-train)). Raw logit is used here; a sigmoid works too and bounds the scale, at the cost of a flatter gradient near saturation. Bypassed tokens pass through untouched via the residual, and the `topk` over `dim=1` is the non-causal operation that needs an auxiliary predictor at inference.

## Serving Looped Models

Depth adaptivity breaks standard batching: tokens in one batch need different loop counts, so there is no unified forward pass. **Continuous depth batching** (Schwethelm et al., 2026) is the first end-to-end implementation of loop-level scheduling. The paper notes that frameworks like vLLM schedule at token level and cannot express this, because tokens must be removed from the batch *within* a forward pass; and that the real difficulty is the non-looped boundary stages (embedding, LM head) needing a different scheduling frequency than the loop body. CDB uses separate priority queues for boundary stages and loop steps, makes exit decisions one step ahead, and overlaps scheduling with GPU compute. On Ouro 1.4B and Huginn 3.5B the paper reports realizing up to 99% of the theoretical maximum adaptive-depth speedup, translating to 1.5–1.9× higher offline throughput and 45–90% lower normalized latency under dynamic serving load.

The takeaway for anyone training a looped model: **the serving stack is part of the architecture decision**. An adaptive-depth model served on a token-level scheduler realizes little of its advantage — which is a large part of why these architectures looked disappointing before loop-level scheduling existed.

## Does Depth Even Earn Its Keep?

Csordás, Manning & Potts (NeurIPS 2025) analyze the residual stream of Llama 3.1, Qwen 3, and OLMo 2 and reach a blunt conclusion: layers in the second half contribute much less than those in the first, with a clear phase transition between halves; skipping second-half layers has much smaller effects on later computation and predictions; on multihop tasks they find no evidence that models use extra depth to compose subresults; and linear maps trained between a shallow model's residual stream and a deeper one's align best at the same *relative* depth. Their reading: deeper models are not learning new kinds of computation, only making finer-grained residual adjustments — which may help explain diminishing returns from stacking layers.

This is the strongest available argument that the depth axis has slack to reclaim, and it also predicts *where*: the second half. It cuts both ways. It supports depth-adaptive methods (that compute is skippable) and undercuts the more ambitious claim that looping lets a model "think longer" into qualitatively new computation — at least for the standard stacked-transformer pretraining these models received.

**A layer-skip diagnostic you can run in an afternoon.** Before adopting any lever in the table below, measure whether depth is under-used *in your model*:

1. For each layer `l`, run the eval set with layer `l` bypassed (`x_out = x_in`; equivalently, zero that block's residual contribution).
2. Record Δloss and Δtask-metric per layer, against the unmodified baseline.
3. Sort layers by Δloss and plot against depth index.
4. If the second half's per-layer Δloss is both **small** and **flat**, depth is under-used and a depth lever can pay.
5. Then re-run steps 1–2 on the hardest decile of inputs only, and compare.

As a rule of thumb — *not* a threshold from any paper — treat per-layer Δloss below roughly 1% of baseline loss as "small". Calibrate against your own first and last layers, whose Δloss is usually large, rather than trusting the absolute number.

**Caveat on the diagnostic.** Csordás et al. is one methodology reporting aggregate metrics; "small contribution on average" is not "removable on hard inputs". A layer that barely moves mean loss can still carry the multi-hop or long-tail cases, and averaging hides exactly that — hence step 5. For the pruning end of the same measurement (Block Influence, depth-only layer deletion, and what actually survives retraining) see [`../../ai-llm-inference/references/pruning-and-sparsity.md`](../../ai-llm-inference/references/pruning-and-sparsity.md).

## Weight Sharing Beyond Depth

**Embedding / LM-head tying** is the weight sharing you already have: `wte.weight` and `lm_head.weight` are the same tensor — see [transformer-from-scratch.md](transformer-from-scratch.md). At small vocab-dominated scales this is a large fraction of parameters; it is the cheapest sharing in the model and essentially free in quality.

**Tied expert layers** apply the idea to the width axis. "Tying the Loop" (arXiv 2606.16825, 2026) introduces **Expert Tying**: sharing expert parameters across consecutive transformer layers while keeping routing and attention independent per layer. Evaluated on OLMoE-, Qwen3-, and DeepSeek-style MoEs, the paper reports the approach "can reduce memory footprint by almost 2x at virtually no degradation in perplexity or downstream quality." Note what is *not* shared — the routers stay layer-specific, so each layer can still send a token to a different expert; only the expert weights are reused. This is the same insight as ALBERT's, transplanted to the FFN-expert bank, and it directly attacks MoE's real cost (parameter memory) rather than its FLOPs.

## Modular Networks as the Umbrella

MoE, MoD, looped blocks, and adapters are instances of one pattern: **autonomous modules plus a routing function that decides which modules see which inputs.** Pfeiffer, Ruder, Vulić & Ponti's *Modular Deep Learning* survey (arXiv 2302.11529, 2023) is the reference framing, organizing the space along how modules are computed, how they are aggregated, and how routing selects them — and covering applications from parameter-efficient fine-tuning to cross-lingual transfer.

Reading the depth-axis literature through that lens makes the design space legible: MoE routes *across* parallel modules, MoD routes *past* a module, looped models route *back into* the same module, and adapters route *through* an inserted module. Choosing among them is choosing a routing topology, and the recurring hard problems — load balancing, router training signal, train/serve routing consistency — are properties of routing itself, not of any one architecture. Expect a fix for one to have an analogue in the others.

Three claims the framing invites and does not settle. Each is worth stating as an experiment, because each is routinely assumed:

- **Composability.** Can a module be added without regressing the others? *Falsifier:* held-out tasks covered by existing modules lose accuracy after the new module is trained in.
- **Localisation.** Does ablating a module localise the loss to that module's intended tasks? *Falsifier:* ablation degrades unrelated tasks by a comparable margin — the module was not doing what its name says.
- **Router transfer.** Does the router carry over to a changed module set without retraining? *Falsifier:* swapping or adding one module requires re-training the router to recover baseline routing accuracy.

## Why the Depth Axis Is Harder to Train

Width and depth routing look symmetric on paper and are not, for three reasons worth internalizing before you implement either.

**The router gets no gradient from the path not taken.** A discrete skip/keep decision is not differentiable. MoD sidesteps this by making the router's score multiply the block output, so the score sits on a live gradient path for tokens that *were* selected; ACT-style halting sidesteps it by producing a weighted mixture over depths (the sketch above) rather than a hard choice. Neither gives a clean signal about tokens that were skipped — a router that starts out skipping a token class will not easily learn to stop.

**Depth decisions compound; width decisions do not.** A bad expert choice at layer 12 costs one layer's quality. A bad early-exit decision truncates every subsequent computation for that token. Errors are sequential, so a router that is 95% accurate per decision is much worse across 32 layers than the number suggests.

**The train/serve routing gap is structural.** MoD's non-causal top-k, AdaPonderLM's KV reuse for halted tokens, MoR's active-token-only caching — each is machinery that exists solely to make the inference-time routing match what training assumed. When a depth-adaptive model underperforms its paper, this mismatch is the first place to look, ahead of the architecture itself.

## Decision Table

Pick the row whose **binding resource** matches yours. A lever that relieves a resource you are not short of buys nothing — the single most common way these architectures disappoint.

| Symptom / constraint | Binding resource | Lever | Tradeoff / condition |
|---|---|---|---|
| Quality plateaued; FLOPs budget fixed; VRAM available | Training FLOPs (capacity-limited) | MoE (width) — see [architecture-limitations-and-workarounds.md](architecture-limitations-and-workarounds.md#5-mlp--ffn-and-mixture-of-experts) | Parameter memory balloons; load-balancing losses; expert-parallel sharding complexity |
| Training FLOPs are the binding constraint; want predictable budget | Training FLOPs | MoD | Non-causal top-k needs an auxiliary predictor at inference; KV holes at skipped layers |
| Decode latency dominated by easy tokens; cannot retrain | HBM bandwidth (usually), FLOPs (rarely) | Post-training early-exit routers (TIDE style) | Gains may be small if decode is bandwidth-bound; missing-KV handling determines whether savings are real |
| Want early-exit speed with *zero* quality risk | HBM bandwidth | LayerSkip self-speculative decoding | Needs the layer-dropout + early-exit-loss training recipe; speedup is task-dependent |
| Parameter memory is the constraint (edge, single GPU) | Parameter memory | Looped / recursive with cross-layer sharing (ALBERT, MoR) | Compute is not reduced by sharing alone; sequential loop steps limit depth parallelism |
| **Batch-1 on-device (edge CPU/NPU); model does not fit** | **Parameter memory** | Weight sharing / looped depth — it is the *only* row that shrinks the resident model | At batch 1 the accelerator is weight-load-bound, so MoD and early exit cut FLOPs you were not short of; expect near-zero latency gain from them alone |
| Want parameter *and* compute adaptivity together | Parameter memory + FLOPs | MoR | Routers add training complexity; needs loop-aware serving. Public evidence is ≤3B (MoR: 135M–1.7B) — persistence >10B is untested either way |
| Have a looped model, throughput is poor in production | Scheduler (neither FLOPs nor bandwidth) | Continuous depth batching | Requires a loop-level scheduler; standard token-level frameworks cannot express it |
| MoE model too large to serve; quality must hold | Parameter memory | Expert tying | Cuts parameters, not FLOPs; sharing pattern is a new hyperparameter |
| Unsure depth is being used at all | — | [Layer-skip diagnostic](#does-depth-even-earn-its-keep) (Csordás et al. method) | Diagnostic, not a fix; aggregate Δloss hides hard-input reliance — check the tail |

**The open question under half this table.** Every depth-recursion result cited here is reported at ≤3B parameters. Whether the parameter-efficiency advantage of depth recursion persists above ~10B — where dense models have more residual slack to begin with, per Csordás et al. — had no public evidence in either direction in the papers reviewed here; look for newer scale results before assuming either way. Treat scale extrapolation as an assumption to test, not a property to inherit.

## Common Mistakes

- **Assuming FLOPs saved equals latency saved.** Decode is usually memory-bandwidth-bound. Skipping layers cuts FLOPs but may not cut weight traffic or cache maintenance. Measure wall-clock, not a FLOPs count.
- **Ignoring the KV hole.** Any per-token depth scheme must state what happens to K/V at skipped layers. If your implementation runs all layers anyway "to keep the cache correct," you have saved nothing.
- **Training top-k routing and serving it causally without an auxiliary predictor.** Top-k over a sequence is non-causal. This silently degrades quality at inference while training metrics look fine.
- **Omitting the ponder penalty in an ACT-style loop.** With no cost on depth, halting gates learn never to halt. The model becomes fixed-max-depth with extra parameters.
- **A non-monotonic halting mask.** If a halted token can resume, KV reuse for halted tokens becomes invalid and train/test diverge.
- **Confusing weight sharing with compute sharing.** ALBERT-style cross-layer sharing reduces parameters; every loop iteration still costs a full block of FLOPs. Only halting reduces compute.
- **Serving an adaptive-depth model on a token-level scheduler.** Batching collapses to the max depth in the batch, erasing the adaptivity you trained for.
- **Treating a reported speedup as portable.** The figures above are tied to specific models, tasks, batch sizes, and GPUs (in the papers cited here, most depth-adaptive results are reported at ≤3B parameters — see the scale note under the [decision table](#decision-table)). Re-measure on your configuration before planning around them.
- **Reaching for MoD/looping when the real problem is width.** If quality is capacity-limited, no depth trick recovers it. Diagnose which axis binds before choosing a lever.
- **Applying a FLOPs lever to a memory-bound deployment.** At batch 1 on edge hardware the accelerator is weight-load-bound; MoD and early exit cut the resource you had to spare. Only weight sharing shrinks the resident model.
