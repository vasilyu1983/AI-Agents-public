# Adaptation Patterns: Task Tuning, Synthetic Data, Distillation, Multi-Task

Adaptation techniques beyond plain SFT/LoRA ([fine-tuning-recipes.md](fine-tuning-recipes.md)). Moved out: RLHF and preference optimization → [ai-post-training](../../ai-post-training/SKILL.md); the pretraining path → [ai-pretraining](../../ai-pretraining/SKILL.md); context engineering → [ai-context-layer](../../ai-context-layer/SKILL.md); production monitoring → [ai-mlops](../../ai-mlops/SKILL.md).

---
## Table of Contents

- [Pattern 3: Task-Specific Tuning (Classify, Embed, Multimodal)](#pattern-3-task-specific-tuning-classify-embed-multimodal)
- [Pattern 6: Synthetic Data Generation](#pattern-6-synthetic-data-generation)
- [Pattern 7: Model Compression & Optimization](#pattern-7-model-compression--optimization)
- [Knowledge Distillation Workflow](#knowledge-distillation-workflow)
- [KD Variants for LLMs](#kd-variants-for-llms)
- [Recipe Table](#recipe-table)
- [Hard vs Soft Distillation](#hard-vs-soft-distillation)
- [Checklist: Compression ready](#checklist-compression-ready)
- [Pattern 8: Multi-Task Learning](#pattern-8-multi-task-learning)

Pattern numbers are kept stable so older links still resolve.

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

## Pattern 6: Synthetic Data Generation

**Use when**: Insufficient real data for fine-tuning or evaluation

### Use Cases

- Bootstrapping datasets for new domains
- Augmenting sparse classes in imbalanced datasets
- Generating edge cases and adversarial examples
- Creating evaluation sets for specific phenomena

### Generation Strategies

**Distillation**:
- Use a stronger teacher model to generate from task prompts — only if the teacher's terms permit training on its outputs (see the licensing gate in Pattern 7)
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

### Quantization and Pruning (serving side lives elsewhere)

Compression changes what you serve, so the format and sparsity choice belongs to the serving skills. Read them before choosing:

- Quantization formats, runtime support, calibration, KV-cache quantization: [ai-llm-inference quantization-patterns](../../ai-llm-inference/references/quantization-patterns.md). On-disk local formats (GGUF, AWQ, GPTQ, MLX): [ai-local-model-ops quantization-format-table](../../ai-local-model-ops/references/quantization-format-table.md).
- Pruning families (unstructured, N:M, structured), one-shot vs prune-then-distill, and the runtime-support matrix: [ai-llm-inference pruning-and-sparsity](../../ai-llm-inference/references/pruning-and-sparsity.md). Low-rank factorization: [ai-pretraining structured-and-low-rank-parameterization](../../ai-pretraining/references/structured-and-low-rank-parameterization.md).

This skill owns the adaptation half: the distillation recovery phase after structured pruning (below) and the compression gate in the checklist.

### Distillation

Train a smaller "student" to reproduce a larger "teacher". For LLMs the interesting question is not *whether* to distill but *which supervision signal you can actually obtain* — logits, generated text, or rationales — because that is what your teacher access determines.

### Knowledge Distillation Workflow

0. **Check you need a distillation run at all.** Is there an existing smaller sibling in the same family — already trained, already supported by your runtime? If the need is many task variants rather than one smaller model, multi-LoRA adapters on a shared base is the cheaper shape. Distill only after both are ruled out.
1. **Teacher licence gate.** Confirm the teacher's terms (API ToS or open-weight licence) permit training a model that may compete with it, and record the licence and the date you read it next to the dataset. If the terms forbid it, stop — no recipe choice fixes that.
2. Decide the KD variant from the recipe table below — teacher access, not preference, is the binding constraint
3. Obtain the teacher signal (logits, generations, or rationales); budget this as one-off spend
4. Train the student against that signal, alone or mixed with ground-truth hard labels
5. Validate the student on a held-out set that exercises the target capability, not just perplexity
6. Iterate on student architecture or signal mix if the gap is unacceptable

#### KD Variants for LLMs

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

Test-time compute (thinking budget, best-of-N, self-consistency, critique loops, PRM search) is an architecture decision, not adaptation: see [ai-architecture-advisor decision-matrices](../../ai-architecture-advisor/references/decision-matrices.md#thinking-budget-how-much-test-time-compute).
