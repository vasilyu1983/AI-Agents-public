# Advanced LLM Development Patterns

Advanced techniques for alignment, pretraining, task-specific tuning, test-time compute, and production feedback loops. For the 2026 post-training stack (GRPO, DAPO, GSPO, RLVR, SimPO, KTO), see [Post-Training 2026](post-training.md).

---
## Table of Contents

- [Pattern 1: RLHF / Feedback Alignment Loop (Production-Friendly)](#pattern-1-rlhf-feedback-alignment-loop-production-friendly)
- [Loop (Minimal Viable)](#loop-minimal-viable)
- [Checklist: RLHF pass](#checklist-rlhf-pass)
- [Pattern 2: Pretraining Path (Tokenizer → Corpus → Schedule)](#pattern-2-pretraining-path-tokenizer-→-corpus-→-schedule)
- [Pattern 9: Test-Time Compute Scaling](#pattern-9-test-time-compute-scaling)
- [Tokenizer & Vocab Fit](#tokenizer-&-vocab-fit)
- [Corpus Pipeline](#corpus-pipeline)
- [Training Schedule](#training-schedule)
- [Long-Context Plan](#long-context-plan)
- [Eval During Pretrain](#eval-during-pretrain)
- [Checklist: Pretraining ready](#checklist-pretraining-ready)
- [Pattern 3: Task-Specific Tuning (Classify, Embed, Multimodal)](#pattern-3-task-specific-tuning-classify-embed-multimodal)
- [Classification/Extraction](#classificationextraction)
- [Embedding Models](#embedding-models)
- [Multimodal Adapters](#multimodal-adapters)
- [Latency/Cost Fit](#latencycost-fit)
- [Monitoring](#monitoring)
- [Checklist: Task tuning safe](#checklist-task-tuning-safe)
- [Pattern 4: Context Engineering Best Practices](#pattern-4-context-engineering-best-practices)
- [Progressive Disclosure](#progressive-disclosure)
- [Session Management](#session-management)
- [Memory Provenance](#memory-provenance)
- [Generation Triggers](#generation-triggers)
- [Background vs Blocking](#background-vs-blocking)
- [Retrieval Timing](#retrieval-timing)
- [Multimodal Context](#multimodal-context)
- [Fresh Contexts](#fresh-contexts)
- [Checklist: Context engineering ready](#checklist-context-engineering-ready)
- [Pattern 5: Production Monitoring & Observability](#pattern-5-production-monitoring-&-observability)
- [Key Metrics to Track](#key-metrics-to-track)
- [Instrumentation](#instrumentation)
- [Alerting Rules](#alerting-rules)
- [A/B Testing Framework](#ab-testing-framework)
- [Drift Detection](#drift-detection)
- [Checklist: Monitoring ready](#checklist-monitoring-ready)
- [Pattern 6: Synthetic Data Generation](#pattern-6-synthetic-data-generation)
- [Use Cases](#use-cases)
- [Generation Strategies](#generation-strategies)
- [Quality Control](#quality-control)
- [Contamination Prevention](#contamination-prevention)
- [Checklist: Synthetic data ready](#checklist-synthetic-data-ready)
- [Pattern 7: Model Compression & Optimization](#pattern-7-model-compression-&-optimization)
- [Quantization](#quantization)
- [Pruning](#pruning)
- [Distillation](#distillation)
- [Knowledge Distillation Workflow](#knowledge-distillation-workflow)
- [KD Variants for LLMs (as of Aug 2026)](#kd-variants-for-llms-as-of-aug-2026)
- [Recipe Table](#recipe-table)
- [Hard vs Soft Distillation](#hard-vs-soft-distillation)
- [Resource Basis: A Point-in-Time Single-Setup Comparison](#resource-basis-a-point-in-time-single-setup-comparison)
- [Checklist: Compression ready](#checklist-compression-ready)
- [Pattern 8: Multi-Task Learning](#pattern-8-multi-task-learning)
- [Task Selection](#task-selection)
- [Architecture Patterns](#architecture-patterns)
- [Training Strategies](#training-strategies)
- [Evaluation](#evaluation)
- [Checklist: Multi-task ready](#checklist-multi-task-ready)


## Pattern 1: RLHF / Feedback Alignment Loop (Production-Friendly)

**Use when**: You need tighter alignment than SFT alone (safety, refusals, tone control, reasoning quality)

**2026 context**: Full PPO-based RLHF is expensive and complex. Most production teams now use one of:
- **Preference optimization without rollouts** (DPO, SimPO, KTO, ORPO) — simpler, no reward model needed
- **RL with verifiable rewards** (GRPO, RLVR) — effective for tasks with deterministic correctness signals (math, code, structured output)

See [Post-Training 2026](post-training.md) for the full decision tree across all 2026 post-training algorithms.

### Loop (Minimal Viable)

1. **Collect preference data**
   - Pairwise rankings or scalar scores on model outputs (reward modeling)
   - Include safety/refusal edge cases
   - Gather from production logs or human labelers
   - Ensure diverse coverage of task types

2. **Train reward model (RM)** — skip if using DPO-family or RLVR
   - Small model or head on frozen encoder/decoder
   - Validate on held-out preferences
   - Check for overfitting to labeler biases
   - Measure inter-rater agreement

3. **Policy optimization** — choose algorithm for your constraints:
   - **PPO**: full RLHF; highest ceiling but needs rollout infra and RM; use only when reward signal is complex and cannot be verified programmatically
   - **DPO / ORPO**: no rollout infra, no RM; trains directly on preference pairs; good default when you have pairwise human labels
   - **SimPO**: margin-based DPO variant; better calibration in some regimes; no reference model needed
   - **KTO**: trains on scalar feedback (binary thumbs up/down) rather than pairwise comparisons; useful when pairwise labels are hard to collect
   - **GRPO / RLVR**: RL with programmatic or verifiable reward; best for math, code, and structured output where correctness can be checked without a learned RM
   - Constrain KL divergence to base model (applies to PPO, DPO-family)
   - Stop if degradation on held-out tasks
   - Monitor reward hacking (gaming the RM) when using a learned reward model

4. **Safety & regression eval**
   - Safety red-team set + task eval + format adherence
   - Gate on "no new regressions"
   - Verify refusal behavior intact
   - Check for capability degradation

5. **Package**
   - Ship RM + policy + configs (or policy + configs for RM-free methods)
   - Log KL, reward distribution, eval metrics
   - Document training hyperparameters
   - Maintain rollback capability

### Checklist: RLHF pass

- [ ] Algorithm chosen for your feedback signal type (pairwise → DPO; scalar → KTO; verifiable → GRPO/RLVR; complex reward → PPO)
- [ ] Preference dataset balanced (task + safety)
- [ ] RM validated on held-out set (if using RM)
- [ ] KL/constraint tracked per step
- [ ] Regression + safety eval passed
- [ ] Policy + RM + configs versioned together
- [ ] Reward hacking monitored and mitigated (if using learned RM)
- [ ] Inter-rater agreement measured (if human labels)

---

## Pattern 2: Pretraining Path (Tokenizer → Corpus → Schedule)

**Use when**: Building or heavily adapting a base model (from-scratch or major domain shift)

### Tokenizer & Vocab Fit

- Train BPE/unigram on domain corpus (method selection and tokenizer evaluation: `ai-pretraining` → references/bpe-tokenizer.md, "Tokenizer Landscape")
- Audit splits on code, math, URLs, PII markers
- Lock tokenizer before corpus filtering
- Validate coverage on representative samples
- Test efficiency (tokens per character)

### Corpus Pipeline

- Mix domains (code/docs/web/structured)
- Dedupe (exact + near-dup with MinHash)
- Contamination scan against evals
- Filter low-quality/boilerplate (perplexity filters, heuristics)
- Balance multilingual if needed
- Document corpus composition and lineage

### Training Schedule

- Warmup → cosine decay learning rate
- Gradient clipping (1.0 typical)
- EMA (Exponential Moving Average) optional
- Checkpoint/adapter save cadence
- Loss spikes watchdog (pause if gradient norm spikes)

### Long-Context Plan

- Position encodings (RoPE/YaRN)
- Sliding-window attention where needed
- Budget KV cache size early
- Test on long-context benchmarks

### Eval During Pretrain

- Perplexity slices per domain
- Probe tasks (code/math/narrative)
- Long-context stress set
- Stop if loss flattens while probes regress

### Checklist: Pretraining ready

- [ ] Tokenizer validated on domain sample
- [ ] Corpus deduped, filtered, contamination-checked
- [ ] Learning rate schedule + clip + checkpoints defined
- [ ] Long-context attention + KV budget selected
- [ ] Probe eval + early-stop rules wired
- [ ] Corpus composition documented
- [ ] Contamination scan completed

---

## Pattern 3: Task-Specific Tuning (Classify, Embed, Multimodal)

**Use when**: Going beyond chat to task/format-specific models

### Classification/Extraction

- Use instruction or seq2seq format
- Add calibration (logits/temperature scaling)
- Enforce schema with constrained decoding
- Class-balance the dataset (oversample minority classes)
- Test on class-imbalanced holdout set

### Embedding Models

- Optimize for retrieval/ranking tasks
- Mine hard negatives (similar but incorrect)
- Evaluate on Recall@K / nDCG metrics
- Test multilingual/domain drift
- Use contrastive loss (InfoNCE, triplet loss)

### Multimodal Adapters

- Choose vision encoder + connector (CLIP, SigLIP)
- Align image tokens with text prompts
- Cap resolution to balance quality/compute
- Cache vision tower outputs
- Add safety filters on images (NSFW, harmful content)

### Latency/Cost Fit

- Smaller heads/adapters where possible
- Quantize heads (int8, int4)
- Restrict max output length for classification/extraction
- Batch inference for throughput

### Monitoring

- Per-class metrics (precision, recall, F1)
- Schema violations (malformed outputs)
- Drift on embeddings (centroid/dispersion)
- Multimodal failure modes (misaligned image-text)

### Checklist: Task tuning safe

- [ ] Format/schema fixed and validated in eval
- [ ] Negatives/hard examples included
- [ ] Multimodal connector latency/cost measured (if used)
- [ ] Per-class/embedding drift monitored
- [ ] Safety filters for text + images active
- [ ] Calibration validated on holdout set

---

## Pattern 4: Context Engineering Best Practices

**Use when**: Managing context and memory across LLM interactions

**Key Insight**: Context structure matters more than model selection. Even weaker LLMs perform well with proper context.

### Progressive Disclosure

- Load context on-demand, not upfront
- Route by domain before retrieve
- Prioritize recent and relevant over exhaustive
- Use lazy loading for large knowledge bases

### Session Management

- Treat sessions as conversation containers
- Honor framework differences (LangChain vs LlamaIndex)
- Share session handles safely across agents with scoped replay
- Implement session timeout and cleanup

### Memory Provenance

- Track lineage (source, timestamp, approvals)
- Store only verifiable data
- Tag memory with confidence scores
- Version memory snapshots

### Generation Triggers

- Extract/consolidate memory at phase boundaries
- Trigger after confidence drops below threshold
- Generate when new entities appear
- Periodic snapshots for long conversations

### Background vs Blocking

- Run heavy writes async (embeddings, summarization)
- Keep blocking writes minimal for critical state
- Use queues for non-critical memory updates
- Prioritize read latency over write latency

### Retrieval Timing

- Retrieve before high-impact actions
- Re-retrieve after state changes
- Enforce recency windows (e.g., last 24h for news)
- Cache frequently accessed contexts

### Multimodal Context

- Normalize metadata across modalities
- Store text + embeddings separately
- Tag modalities (text/image/audio/video)
- Align timestamps across modalities

### Fresh Contexts

- Spawn new agents with clean state
- Hydrate from validated memory only
- Avoid context pollution from previous tasks
- Test with and without context carryover

### Checklist: Context engineering ready

- [ ] Progressive disclosure implemented
- [ ] Session management configured
- [ ] Memory provenance tracked
- [ ] Generation triggers defined
- [ ] Background/blocking writes separated
- [ ] Retrieval timing optimized
- [ ] Multimodal metadata normalized
- [ ] Fresh context spawning tested

---

## Pattern 5: Production Monitoring & Observability

**Use when**: Deploying LLMs to production environments

### Key Metrics to Track

**Quality Metrics**:
- Task success rate (did it complete the task?)
- Correctness score (is the output accurate?)
- Format compliance (schema violations)
- Refusal rate (appropriate vs over-cautious)

**Performance Metrics**:
- Latency (p50, p95, p99)
- Throughput (requests/second)
- Token usage (input + output)
- Cost per request

**Safety Metrics**:
- PII detection rate
- Toxicity/harmful content rate
- Jailbreak attempt detection
- Policy violation rate

### Instrumentation

- Log every request/response with trace IDs
- Capture prompt templates and versions
- Store model outputs with timestamps
- Record user feedback (thumbs up/down, edits)

### Alerting Rules

- Latency spike > 2x baseline
- Error rate > 5%
- Cost spike > 1.5x budget
- Safety violations > threshold
- Refusal rate drift > 10%

### A/B Testing Framework

- Shadow new prompts/models before rollout
- Split traffic (5-10% canary)
- Compare metrics side-by-side
- Automated rollback on regression

### Drift Detection

- Monitor output distribution shifts
- Track new entity types appearing
- Detect format changes over time
- Alert on vocabulary drift

### Checklist: Monitoring ready

- [ ] All key metrics instrumented
- [ ] Trace IDs propagated
- [ ] Alerting rules configured
- [ ] A/B testing framework ready
- [ ] Drift detection active
- [ ] Cost tracking enabled

---

## Pattern 6: Synthetic Data Generation

**Use when**: Insufficient real data for fine-tuning or evaluation

### Use Cases

- Bootstrapping datasets for new domains
- Augmenting sparse classes in imbalanced datasets
- Generating edge cases and adversarial examples
- Creating evaluation sets for specific phenomena

### Generation Strategies

**Distillation**:
- Use stronger model (GPT-4, Claude) to generate from weaker model prompts
- Validate outputs manually or with automated checks
- Ensure diversity in generated examples

**Paraphrasing**:
- Rephrase existing examples with semantic preservation
- Use multiple paraphrase models for diversity
- Validate meaning equivalence

**Backtranslation**:
- Translate to intermediate language and back
- Creates natural variations
- Test with multiple language pairs

**Rule-Based Templates**:
- Create templates with variable slots
- Fill slots programmatically
- Validate logical consistency

### Quality Control

- Manual review of random samples (10-20%)
- Automated filters (length, perplexity, toxicity)
- Deduplication against real data
- Diversity metrics (unique n-grams, entity coverage)

### Contamination Prevention

- Keep synthetic data separate from eval sets
- Track lineage (synthetic vs real)
- Hash all synthetic samples
- Periodic audits for leakage

### Checklist: Synthetic data ready

- [ ] Generation strategy selected
- [ ] Quality control implemented
- [ ] Manual review completed
- [ ] Deduplication run
- [ ] Contamination prevention active
- [ ] Lineage tracking configured

---

## Pattern 7: Model Compression & Optimization

**Use when**: Deploying to resource-constrained environments or reducing costs

### Quantization

**Post-Training Quantization (PTQ)** — format families as of Aug 2026, stated as *weight-storage* reduction against BF16:
- **INT8 W8A8** (weights and activations at 8-bit) — ~2x smaller weights.
- **INT4 weight-only with group scales** (AWQ, GPTQ; activations stay at higher precision) — ~4x smaller weights.
- **FP8** (E4M3/E5M2) — ~2x, native on recent datacenter GPUs.
- **NVFP4 / MXFP4** (4-bit float with block-level micro-scales) — ~4x; the current 4-bit direction where hardware supports it.

- **Storage is not speed.** Memory reduction converts to latency or cost only when decode is memory-bandwidth-bound *and* your runtime ships the kernel for that format. Otherwise you get a smaller checkpoint at the same tokens/sec.
- **KV cache is sized separately** and at long context or high concurrency it, not the weights, is what runs out first. Quantizing weights does not shrink it.
- **Quality depends on granularity, outlier handling, and scale format** — not on the bit-width label alone. Reasoning and structured-output/tool-call validity degrade before perplexity visibly moves, so perplexity is the wrong gate.

**Quantization-Aware Training (QAT)**:
- Simulate quantization during training
- Better accuracy preservation
- Requires full training access

> The treatment above is decision-level only; read [`ai-llm-inference/references/quantization-patterns.md`](../../ai-llm-inference/references/quantization-patterns.md) before choosing a format. For calibration procedure, KV-cache and activation quantization, and per-method accuracy behavior see [`ai-llm-inference/references/quantization-patterns.md`](../../ai-llm-inference/references/quantization-patterns.md); for the concrete on-disk format matrix (GGUF/AWQ/GPTQ/MLX and their quant-level names) see [`ai-local-model-ops/references/quantization-format-table.md`](../../ai-local-model-ops/references/quantization-format-table.md). Those are authoritative; this section is a pointer.

### Pruning

Three families, in increasing order of how much real speedup they buy and how much accuracy risk they carry:

- **Unstructured** (drop individual weights) — best accuracy retention at a given sparsity, but yields no wall-clock speedup without sparse kernels; mostly a memory-footprint lever.
- **N:M semi-structured** (e.g. 2:4 — N nonzeros per M-weight block) — a middle path that *can* map onto sparse-tensor-core support, but the sparsity is redeemable only where your serving runtime actually ships the sparse kernel. Verify that first: as of Aug 2026 the vLLM / LLM Compressor 2:4 production path is withdrawn — verify current status in `../../ai-llm-inference/references/pruning-and-sparsity.md#runtime-support` before relying on it; hardware capability alone is not the gate.
- **Structured** (drop whole heads, channels, MLP dims, or layers) — the only family that speeds up dense hardware unconditionally, and the one that costs the most accuracy per unit removed, so it is normally paired with a recovery phase.

Two operating modes. **One-shot post-training pruning** (SparseGPT, Wanda) prunes a trained model using a small calibration set and no gradient retraining — cheap, and the right first attempt. **Prune-then-distill** (Minitron: original arXiv [2407.14679](https://arxiv.org/abs/2407.14679), follow-up arXiv [2408.11796](https://arxiv.org/abs/2408.11796)) structurally prunes and then runs a distillation recovery phase. The original abstract states that retraining a pruned model on "a fraction (<3%) of the original training data" requires "up to 40x fewer training tokens per model compared to training from scratch" for 8B and 4B models derived from a 15B model — their numbers on their family, not a transferable ratio. The follow-up compresses Llama 3.1 8B and Mistral NeMo 12B, comparing depth pruning against joint width pruning of hidden/attention/MLP dimensions. Expect one-shot to degrade faster than prune+distill as the compression ratio grows — but measure on your task, since published ratios do not transfer.

> Read before choosing: [`ai-llm-inference/references/pruning-and-sparsity.md`](../../ai-llm-inference/references/pruning-and-sparsity.md) — it carries the runtime-support matrix this decision hinges on. Low-rank factorization is a *different* parameter-reduction axis (factorize rather than zero out) and is covered in [`ai-pretraining/references/structured-and-low-rank-parameterization.md`](../../ai-pretraining/references/structured-and-low-rank-parameterization.md).

### Distillation

Train a smaller "student" to reproduce a larger "teacher". For LLMs the interesting question is not *whether* to distill but *which supervision signal you can actually obtain* — logits, generated text, or rationales — because that is what your teacher access determines.

### Knowledge Distillation Workflow

0. **Check you need a distillation run at all.** Is there an existing smaller sibling in the same family — already trained, already supported by your runtime? If the need is many task variants rather than one smaller model, multi-LoRA adapters on a shared base is the cheaper shape. Distill only after both are ruled out.
1. Decide the KD variant from the recipe table below — teacher access, not preference, is the binding constraint
2. Obtain the teacher signal (logits, generations, or rationales); budget this as one-off spend
3. Train the student against that signal, alone or mixed with ground-truth hard labels
4. Validate the student on a held-out set that exercises the target capability, not just perplexity
5. Iterate on student architecture or signal mix if the gap is unacceptable

#### KD Variants for LLMs (as of Aug 2026)

**Logit / soft-label KD with temperature.** The classic setup: match the teacher's softened output distribution, minimizing KL against the teacher's per-token distribution. Hinton, Vinyals & Dean, "Distilling the Knowledge in a Neural Network" (arXiv [1503.02531](https://arxiv.org/abs/1503.02531), 2015). The objective:

```text
L_soft = KL( softmax(z_t/T) || softmax(z_s/T) ) · T²
L      = alpha · L_soft + (1 - alpha) · L_hard        # L_hard = CE against ground-truth labels
# both teacher (z_t) and student (z_s) logits divided by the SAME T
```

The T² factor is not cosmetic. §2 of the paper: "Since the magnitudes of the gradients produced by the soft targets scale as 1/T² it is important to multiply them by T² when using both hard and soft targets." Verified numerically — soft-loss grad norm w.r.t. student logits, T=1/2/4: without T² 0.00130 / 0.00026 / 0.00006 (falls even faster than 1/T², because softening also flattens the teacher distribution and shrinks the KL itself), with T² 0.00130 / 0.00105 / 0.00100 (roughly constant — the point). Hinton's 1/T² is the per-logit gradient term, not the end-to-end norm of a batch-mean KL, so do not "fix" that discrepancy.

Use when you have teacher logits *and* a shared tokenizer — in practice, within one model family.

**Sequence-level / hard KD.** Train the student by ordinary supervised fine-tuning on text the teacher generated. Needs only API-visible outputs. This is the default for LLMs; see the hard-vs-soft discussion below for why.

**On-policy / student-generated KD.** Both variants above train the student on sequences the *teacher* produced, so at inference the student meets its own distribution for the first time. GKD ("On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., arXiv [2306.13649](https://arxiv.org/abs/2306.13649)) names this directly: KD for auto-regressive sequence models "suffer[s] from distribution mismatch between output sequences seen during training and those generated by the student during inference", and fixes it by training the student on its own generations scored by teacher feedback. MiniLLM (Gu et al., arXiv [2306.08543](https://arxiv.org/abs/2306.08543), ICLR 2024) attacks the same problem from the divergence side, replacing forward KL with reverse KL as "more suitable for KD on generative language models, to prevent the student model from overestimating the low-probability regions of the teacher distribution" — that is the paper's own stated reason. The mode-covering / mode-seeking framing (small student forced to put mass everywhere the teacher does averages across modes it cannot represent) is *interpretation*, not the paper's claim, and the reverse-KL advantage is not universal — it trades coverage for commitment, which hurts where output diversity matters. Both require the ability to score student samples with the teacher, so both cost more per step than offline hard KD.

**Rationale distillation.** Distilling Step-by-Step (arXiv [2305.02301](https://arxiv.org/abs/2305.02301)) extracts LLM rationales as *additional supervision* alongside labels in a multi-task setup, rather than training only on final answers — worth considering when the teacher's reasoning, not just its verdict, is the thing you want transferred.

**Reasoning-trace distillation.** The DeepSeek-R1 report (arXiv [2501.12948](https://arxiv.org/abs/2501.12948)) states that "the emergent reasoning patterns exhibited by these large-scale models can be systematically harnessed to guide and enhance the reasoning capabilities of smaller models," and that the authors distilled several smaller models and released them. Directionally this is sequence-level KD where the teacher's *reasoning traces*, not just final answers, are the training targets. Treat the specific student sizes and recipe details as things to read out of that paper before copying — do not assume them.

**Prune-then-distill.** When you own the weights, compress first and use distillation as the recovery phase (Minitron, above) rather than training a fresh small model. This is the compression-first path and it changes the question from "what student architecture?" to "what do I remove, and how much recovery does it need?".

#### Recipe Table

| Goal | KD variant | What you need | Main failure mode |
|------|-----------|---------------|-------------------|
| Cheapest transfer from an API teacher | Sequence-level / hard KD | Teacher generations only | Student never sees its own error distribution; provider ToS may forbid it |
| Max signal per token, same model family | Logit / soft-label KD + temperature | Teacher logits **and** matching tokenizer | Missing T² on the soft term (soft gradient collapses as 1/T², so tuning T silently reweights the blend); tokenizer mismatch silently misaligns vocabularies; logit storage cost for long traces |
| Student underperforms at generation despite good training loss | On-policy KD (GKD) | Ability to sample the student **and** score those samples with the teacher | Higher per-step cost; needs a live teacher in the loop |
| Small student over-hedging / mode-averaging | Reverse-KL objective (MiniLLM) | Same as on-policy | Mode-seeking can drop legitimate diversity |
| Transfer reasoning, not just answers | Rationale KD / reasoning-trace KD | Teacher rationales or traces | Traces are long — data and context cost grows fast |
| You own the weights and want a smaller *deployable* model | Prune-then-distill (Minitron) | Full weight access + recovery compute | Structured pruning damage may exceed what recovery restores |

**Distill or just train a small model?** This is now answerable from a scaling law rather than intuition — see [Distillation Scaling Laws](../../ai-scaling-laws/references/post-chinchilla-developments.md#9-distillation-scaling-laws-2025). Short version from that section: distillation wins when a capable teacher already exists or you will amortize it across several students; if only one student is needed *and* the teacher's training compute must be counted too, plain supervised training is generally the better use of the same compute.

**Licensing gate.** Training on another provider's generated outputs may be restricted by that provider's terms of service. See [`ai-data-curation-pretraining/SKILL.md`](../../ai-data-curation-pretraining/SKILL.md) for provider-ToS handling. Settle this before generating the teacher dataset — it is the most common way a distillation plan dies late.

#### Hard vs Soft Distillation

Raschka frames the same choice as a two-way split, and explains why the LLM default is
the *weaker* signal:

- **Hard distillation** — student trained on the teacher's generated text; mechanically just
  SFT on synthetic data. Needs only the teacher's output text.
- **Soft distillation** — student trained to match the teacher's full-vocabulary distribution
  at each step via KL. Richer signal; needs teacher logits or log-probabilities.
- **Combined** — train on the teacher's tokens while also matching its distribution. The classic
  Hinton, Vinyals & Dean setup.

**Why hard distillation dominates for LLMs.** Two independent blockers:

1. **Closed APIs do not expose logits.** Proprietary systems may expose generated text
   but generally not the full vocabulary distribution soft distillation needs. If your
   teacher is behind an API, soft distillation is off the table regardless of preference.
2. **Matching tokenizers required.** Even when logits are available, student and teacher
   usually need the same tokenizer so their vocabulary distributions line up — which in
   practice confines soft distillation to within a single model family. Storing and
   using full token distributions for long reasoning traces is also far more expensive
   than storing plain text.

So: **default to hard distillation** unless you own both models, they share a tokenizer,
and you have measured that the distribution signal is worth the storage and plumbing.
Note that the on-policy methods above are a third option that sidesteps this axis: they
still need a live teacher, but they attack exposure bias rather than signal richness.

#### Resource Basis: A Point-in-Time Single-Setup Comparison

Raschka reports the following from **one setup on a DGX Spark** while distilling a
Qwen3 0.6B student. These are conditions-attached observations from a single hardware
and model configuration, not general scaling claims — do not extrapolate the ratios:

| Method | Reported cost on that setup |
|--------|------------------------------|
| Distillation training run | "about 3 hours on a DGX Spark and use about 15 GB of RAM" |
| A few GRPO rounds (same hardware) | "around 12 hours and 70 GB of RAM on the same hardware" |
| Teacher data generation | "approximately $50 in API usage" — 671B-parameter DeepSeek-R1 via OpenRouter, generating answers for 12,000 MATH training problems |

The directional takeaway that does travel: distillation shifts cost from *training
compute* to *one-off teacher-generation spend*, and the teacher dataset can be generated
ahead of student training rather than in the loop. That structural property is why it is
often cheaper than RLVR at small scale — not the specific hours and gigabytes above.

**Context accuracies from the same chapter**, again verbatim with their conditions —
all on MATH-500, all point-in-time:

- Qwen3 0.6B base model: **15.2%**
- Official Qwen3 0.6B reasoning reference model: **50.8%**
- DeepSeek-R1 teacher (671B parameters): **91.2%**

These frame the headroom a distillation run is working inside on that specific
benchmark and model pair. They are not benchmarks to target and they will not hold for
your task, your dataset, or a different student size. Model names appear here as
experimental conditions, not as recommendations.

Source: Sebastian Raschka, *Build a Reasoning Model (From Scratch)* (Manning, 2026),
Ch. 8.

### Checklist: Compression ready

Gate on a regression suite, not on checkpoint size. Size is an *input*; the output metric is tokens/$ at your target concurrency. Rollback triggers below are heuristic starting thresholds — label them as such and set your own from the baseline spread.

- [ ] **Same-seed pre-compression baseline** captured (same prompts, decode params, seed) — every row below is a delta against it, not an absolute
- [ ] **Task evals by slice**, not aggregate — roll back if any slice regresses beyond its own noise band (heuristic: >2 pts absolute)
- [ ] **Structured-output / schema-valid rate** — heuristic rollback at >1 pt absolute drop; this breaks before perplexity moves
- [ ] **Tool-call validity** (correct name + parseable arguments) — heuristic rollback at >1 pt absolute drop
- [ ] **Long-context retrieval** at your real context length — heuristic rollback at >2 pts absolute drop (same gate as quantization-patterns.md)
- [ ] **Reasoning benchmark** on the task family you actually serve — heuristic rollback at >3 pts absolute drop
- [ ] **Tokens/$ at target concurrency** improved by enough to justify the risk; if not, the compression bought nothing
- [ ] Production deployment tested with the rollback path exercised

---

## Pattern 8: Multi-Task Learning

**Use when**: Training a single model for multiple related tasks

### Task Selection

- Choose related tasks with shared representations
- Ensure sufficient data per task
- Balance task difficulty
- Test negative transfer (tasks hurting each other)

### Architecture Patterns

**Shared Encoder + Task-Specific Heads**:
- Common for classification tasks
- Efficient parameter sharing
- Easy to add new tasks

**Multi-Task Transformer**:
- Task tokens or prompts to indicate task
- Single unified output space
- More flexible but needs more data

### Training Strategies

**Task Sampling**:
- Proportional to dataset size
- Temperature-based (flatten/sharpen distribution)
- Dynamic (based on task performance)

**Loss Weighting**:
- Equal weights baseline
- Uncertainty weighting (learn task weights)
- GradNorm (gradient-based balancing)

### Evaluation

- Per-task metrics
- Average across tasks
- Worst-task performance (important for robustness)
- Test for negative transfer

### Checklist: Multi-task ready

- [ ] Tasks selected and validated
- [ ] Architecture chosen
- [ ] Task sampling strategy defined
- [ ] Loss weighting configured
- [ ] Per-task evaluation implemented
- [ ] Negative transfer monitored

---

## Pattern 9: Test-Time Compute Scaling

**Use when**: You need higher accuracy at inference time without retraining; task has verifiable correctness or strong reasoning requirements.

**Core idea**: Instead of training a larger model, spend more compute at inference by generating and evaluating multiple candidate outputs. This is an inference-time capability lever, not a training technique.

### Approaches

**Best-of-N sampling (BoN)**
- Generate N independent completions; select the best by a reward model, verifier, or heuristic.
- Simple to implement; cost scales linearly with N.
- Effective when a reliable scorer exists (e.g., test-case pass rate for code, exact-match for math).

**Chain-of-thought + self-consistency**
- Generate multiple reasoning chains; aggregate by majority vote on the final answer.
- Works without a trained verifier; especially effective on symbolic and mathematical tasks.
- Use a high-temperature sample for diversity, then majority vote.

**Reasoning model APIs (provider-native)**
- Models like OpenAI o-series, Claude with adaptive thinking, and DeepSeek-R1 allocate internal token budget to extended reasoning before producing a final answer.
- Verify current API parameters against provider docs — test-time compute controls differ by provider and are subject to breaking changes (e.g., Anthropic removed `budget_tokens` in favor of `thinking: {type: "adaptive"}` for Opus 4.7).
- Cost scales with reasoning tokens; set per-request budgets to control spend.

**Sequential refinement / critique loops**
- Generate a draft; use the same or a different model to critique and refine.
- More expensive than BoN per output; better for open-ended tasks without a verifier.
- Cap refinement rounds to control cost.

**Process reward models (PRM)**
- Train a step-level (rather than outcome-level) reward model; use to guide beam search or tree search at inference.
- Highest quality ceiling for multi-step reasoning; highest complexity and infra cost.
- Verify PRM availability in your framework before committing (as of mid-2026, PRM support in open ecosystems is maturing).

### Decision Table

| Situation | Approach | Notes |
|-----------|----------|-------|
| Task has verifiable output (math, code) | Best-of-N + verifier or RLVR-trained model | Highest ROI; verifier is free |
| No verifier, symbolic task | Self-consistency (majority vote) | No additional infra |
| Provider reasoning model available | Native adaptive thinking / reasoning mode | Check API docs for current params |
| Open-ended, no verifier | Sequential critique loop (capped rounds) | Control cost strictly |
| Highest accuracy, budget available | PRM + beam/tree search | Complex; verify framework support |

### Tradeoffs

- Test-time compute improves accuracy but **increases latency and cost per request** — not a substitute for training when throughput matters.
- Best-of-N requires a reliable scorer; without one, majority vote or human review is needed.
- Verify that provider reasoning-mode pricing is within your cost budget before enabling for high-volume workloads.

### Checklist: Test-time compute ready

- [ ] Approach selected for task type (verifiable vs open-ended)
- [ ] N budget and cost ceiling defined
- [ ] Verifier or scorer validated on held-out set (if using BoN)
- [ ] Latency impact measured at target concurrency
- [ ] Provider API parameters verified against current docs
- [ ] Cost tracking enabled per reasoning-token pool

---
