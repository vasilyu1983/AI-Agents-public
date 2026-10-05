# Research Recipes: Transfer, Schedules, Spikes, Mid-Training

Decision rules for the research-level parts of a pretraining run: µP hyperparameter transfer, learning-rate schedules and cooldown, loss-spike diagnosis, and mid-training or continued-pretraining data mixes. Each section says when to use the technique, what to measure, and what failure looks like. The loop-level mechanics (the WSD code, the base annealing probe, the loss-spike protocol) live in [Pretraining Loop](pretraining-loop.md). This file goes one level deeper and does not restate them.

Paper figures below are the ones reported in the cited paper for its own setup. Treat them as a starting point to re-measure, never as constants to copy.

## Table of Contents

- [Hyperparameter Transfer (muP)](#hyperparameter-transfer-mup)
- [LR Schedules, Cooldown and Annealing](#lr-schedules-cooldown-and-annealing)
- [Loss-Spike Diagnosis and Mitigation](#loss-spike-diagnosis-and-mitigation)
- [Mid-Training and Continued Pretraining Mixes](#mid-training-and-continued-pretraining-mixes)
- [Sources](#sources)

## Hyperparameter Transfer (muP)

**Use it when** you will train more than one width, or when the target is too expensive to sweep. Tune on a narrow proxy, then reuse the tuned values at the target width. **Skip it** for a single-scale reproduction, where one LR sweep at that scale is cheaper than a correct µP port. The fallback is fitting η_opt(C) and B_opt(C) on small budgets ([ai-scaling-laws](../../ai-scaling-laws/SKILL.md), workflow step 6).

**What transfers, and along which axis.** Yang et al. (arXiv 2203.03466) transfer the optimization hyperparameters: learning rate, schedule, initialization scale, and the per-layer output and attention multipliers. The paper reports that regularization hyperparameters, such as dropout and weight decay, do not transfer the same way. Width is the axis the theory covers. Transfer across depth, batch size, training length and sequence length is shown empirically for Transformers in that paper, not proven. Later depth-µP work (arXiv 2310.02244) reports fundamental limits for blocks with more than one layer, which includes the standard transformer block. Rule: transfer across width freely. Treat any other axis as a hypothesis, and re-check it with a short sweep at two depths or batch sizes.

**Evidence of the payoff.** The µTransfer paper tuned a 40M-parameter proxy and transferred the result to GPT-3 6.7B, at a tuning cost of about 7% of the target's pretraining cost. It also transferred from a 13M proxy to BERT-large.

**Implementation signatures.** Getting any one of these wrong silently breaks transfer:

- Attention logits are scaled by 1/d_head, not 1/√d_head.
- The output (readout) layer and the query projection are zero-initialized.
- Initialization and LR multipliers depend on tensor type (input, hidden or output). Take them from the paper's tables or the authors' reference implementation. Do not re-derive them by hand.

**Verify before trusting it: the coordinate check.** Train a few steps at 3+ widths and plot a per-layer activation size, such as the mean |x| of each layer's output, against width. Under a correct µP these curves stay flat as width grows. A curve that grows with width marks the tensor whose parameterization is wrong.

**Failure signatures.**

| Symptom | Likely cause |
|---|---|
| The optimal LR from the proxy sweep drifts with width | Parameterization bug. Run the coordinate check before blaming the method. |
| The transferred LR diverges at the target | A second axis changed as well (depth, batch, sequence length), or the embedding or readout multipliers are wrong |
| Proxy and target optima agree, but the target is worse than a standard-parameterization baseline | A regularization value was transferred as if it were an optimization value. Re-tune weight decay and dropout at scale. |

**What to measure.** Loss against LR at 2–3 proxy widths: the minima should line up. Report the width range you checked, and do not extrapolate far past it without one confirmation run.

## LR Schedules, Cooldown and Annealing

**Choose the schedule by what you know about the budget:**

| Situation | Schedule |
|---|---|
| Token budget fixed and known up front | Cosine to a small floor. It is the reproduction default. |
| Budget may grow, or you need usable checkpoints along the way | WSD: warmup, a constant plateau, then a cooldown at the end. MiniCPM (arXiv 2404.06395) introduced it for continuous training. |
| Data or mixture ablations branched off one run | WSD. Branch from a plateau checkpoint and give each arm the same cooldown. |
| Training continues on new data without a planned end | An "infinite" schedule (a constant phase with a cooldown per release). See the next section. |

**What Hägele et al. (arXiv 2405.18392) report for constant LR plus cooldown:**

- It matches cosine's scaling behaviour, so scaling-law fits can reuse one plateau run across many token budgets instead of one cosine run per budget.
- A (1−sqrt) cooldown shape beat a linear one.
- The gain from lengthening the cooldown flattened out at about 20% of the run. For long runs a smaller fraction was enough, provided the cooldown was long in absolute steps.
- Stochastic weight averaging narrowed the gap to a cooldown but did not close it.
- Decaying to a lower final LR improved loss, but annealing all the way to zero could hurt downstream metrics. Pick the floor using the evals you care about, not loss alone.

**Decision rules.**

- Compare a WSD run with a cosine run only after both have decayed. Plateau loss sits well above post-cooldown loss, so a mid-plateau comparison favours cosine for the wrong reason.
- Hold the cooldown length and shape fixed across ablation arms. The cooldown is where loss falls fastest, so its length is a confounder.
- Set warmup in tokens or steps, never as a fraction of the run ([reference card](pretraining-loop.md#gpt-2-124m-reference-card)).

**Failure signatures.**

- The cooldown barely lowers loss: the plateau LR was too low to leave anything for the cooldown to recover, or the cooldown was too short in absolute steps.
- Loss improves in the cooldown but downstream evals regress: check the LR floor and what data the cooldown saw (next section) before blaming the schedule.

## Loss-Spike Diagnosis and Mitigation

Start from the working protocol in [Pretraining Loop](pretraining-loop.md#loss-spike-protocol). The additions below help decide which kind of spike you have.

**Classify first. The classes have different fixes:**

| Class | Precursor to look for | First-line fix |
|---|---|---|
| Attention-logit growth | Max pre-softmax attention logit per layer rising for many steps | QK-layernorm (or logit capping) |
| Output-logit divergence | log Z of the output softmax drifting away from 0 | z-loss on the output softmax |
| Vanishing Adam updates | Per-tensor gradient RMS approaching AdamW's ε, so updates collapse | Lower ε. Re-check at the target scale. |
| Batch × state interaction | A sudden spike with no slow precursor | Roll back and skip the batch window |

**What Wortsman et al. (arXiv 2309.14322) found.** Attention-logit growth and output-logit divergence both reproduce in *small* models trained at a high LR. Instability can therefore be studied cheaply on a proxy rather than discovered at scale. qk-layernorm and a z-loss (coefficient 1e-4) mitigated them. Loss deteriorated once the max attention logit reached roughly 1e3–1e4 in their setup. When gradient RMS fell toward AdamW's default ε, updates shrank. Lowering ε to 1e-15 helped at 4.8B parameters, while raising it to 1e-6 caused an instability. Their *LR sensitivity* metric is the loss spread across a range of LRs, and it is a cheap way to score a stability intervention: a better intervention flattens the curve.

**What PaLM (arXiv 2204.02311) found at 540B.** It saw about 20 loss spikes even with gradient clipping on. The mitigation was to restart from a checkpoint about 100 steps before the spike and skip roughly 200–500 data batches. Replaying those same batches from a different checkpoint did not spike. The authors attribute the spikes to the combination of particular batches with a particular parameter state, not to bad data as such. So a skip that works is not evidence that the data was corrupt. Do not drop the shard from the corpus on that basis alone. PaLM also used an auxiliary z-loss of 1e-4·log²Z.

**Decision tree.**

1. Is there a slow precursor (attention logit, log Z, or grad RMS near ε)? → Apply the matching structural fix, then re-run from before the precursor began.
2. Is there no precursor, and does the spike recover within a few steps? → Log it and continue.
3. Is there no precursor, and the spike does not recover? → Roll back about 100 steps and skip the batch window. If the same data replayed from an earlier checkpoint is fine, treat it as batch × state, not a data defect.
4. Do spikes repeat after the fixes? → Measure LR sensitivity on a proxy and lower the peak LR.

**What to log every step:** max attention logit per layer, output log Z, per-tensor gradient RMS next to ε, the update-to-weight ratio, and the global grad norm. Loss alone tells you a spike happened, not which class it was.

## Mid-Training and Continued Pretraining Mixes

Two related moves:

- **Mid-training:** a final annealing phase on a higher-quality or task-shaped mix, added to your own run.
- **Continued pretraining:** more tokens, or a new domain or language, on an existing checkpoint.

The mechanics of a same-length base-mix control are in [Pretraining Loop](pretraining-loop.md#annealing-data-probe-and-mid-training-stage).

**Continued pretraining: rewarm, re-decay, replay.** Ibrahim et al. (arXiv 2403.08763) found that re-warming and re-decaying the LR, combined with replaying some old data, matched re-training from scratch on the union of datasets in their setting.

- Replay scales with distribution shift: 5% was enough for English→English, while English→German needed 25%. Even 1% replay reduced forgetting.
- A lower re-warmed max LR forgets less. A higher one adapts more. Choose on the axis you care about.
- They propose "infinite" LR schedules so that future continuation does not require re-warming.

Gupta et al. (arXiv 2308.04014) report that re-warming first *raises* loss on the old data but helps over a longer continuation. Do not abort a re-warm because of the initial bump.

**Mid-training recipes as reported.**

- **Llama 3 (arXiv 2407.21783):**
  - Used annealing as a data-quality probe: take an 8B model at 50% of training, decay the LR linearly to 0 over 40B tokens with 30% candidate data and 70% default mix, then score the result.
  - Annealed the final 40M tokens of the main run with high-quality sources upsampled, then averaged checkpoints.
  - Extended context in 6 stages from 8K to 128K over about 800B tokens. Each stage advanced only when short-context evals had fully recovered and the needle-in-a-haystack test was solved.
- **OLMo 2 (arXiv 2501.00656):**
  - Spent 5–10% of training FLOPs on mid-training, decaying the LR linearly to zero on a specialized mix.
  - Used "micro-annealing" runs to score candidate data sources cheaply.
  - Averaged ("souped") several anneals that differed only in data order.
  - Reported that the gap from a higher pretraining LR was recovered by mid-training. Judge pretraining-LR choices after the anneal, not before.

**Decision rules.**

- Rank candidate datasets with short anneals of equal length from the same checkpoint. The difference is a relative signal for ranking, not a forecast of full-run gains.
- Size replay by the size of the shift: small for same-language domain shifts, large for a new language. Never zero.
- Decontaminate the anneal slice harder than the rest of the corpus. Benchmark leakage there inflates scores the most.
- For context extension, set the gate before the next stage: short-context evals recovered, and a retrieval-at-length probe passed.

**What to measure.**

- Loss on held-out *old* data, which measures forgetting.
- Loss on held-out *new* data, which measures adaptation.
- Downstream evals after the anneal, compared with a base-mix anneal of equal length.
- For long context: short-context regression and a retrieval-at-length probe.

**Failure signatures.**

| Symptom | Likely cause |
|---|---|
| General benchmarks drop after a domain continuation | Too little replay, or the re-warm LR was too high |
| Benchmarks jump suspiciously after the anneal | Contamination in the anneal slice |
| Long-context probe passes but short-context evals regress | A stage advanced too early. Add short-context data back into the mix. |

## Sources

- Yang et al. 2022, µTransfer / µP — arXiv 2203.03466
- Yang et al. 2023, depth-wise µP (Tensor Programs VI) — arXiv 2310.02244
- Hu et al. 2024, MiniCPM (WSD) — arXiv 2404.06395
- Hägele et al. 2024, scaling laws and compute-optimal training beyond fixed durations — arXiv 2405.18392
- Chowdhery et al. 2022, PaLM — arXiv 2204.02311
- Wortsman et al. 2023, small-scale proxies for large-scale Transformer training instabilities — arXiv 2309.14322
- Ibrahim et al. 2024, simple and scalable strategies to continually pre-train LLMs — arXiv 2403.08763
- Gupta et al. 2023, continual pre-training of LLMs: how to (re)warm your model — arXiv 2308.04014
- Llama Team 2024, The Llama 3 Herd of Models — arXiv 2407.21783
- OLMo Team 2025, 2 OLMo 2 Furious — arXiv 2501.00656
