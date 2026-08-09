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

- Train BPE/unigram on domain corpus
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

**Post-Training Quantization (PTQ)**:
- int8: 2x smaller, minimal accuracy loss
- int4: 4x smaller, slight accuracy loss
- GPTQ, AWQ for weight-only quantization

**Quantization-Aware Training (QAT)**:
- Simulate quantization during training
- Better accuracy preservation
- Requires full training access

### Pruning

- Remove low-magnitude weights
- Structured pruning (entire neurons/layers)
- Iterative magnitude pruning
- Test after each pruning step

### Distillation

- Train smaller "student" model from larger "teacher"
- Match logits or intermediate activations
- Combine with quantization for maximum compression
- Validate on diverse test set

### Knowledge Distillation Workflow

1. Train large teacher model (or use existing)
2. Generate soft labels from teacher
3. Train smaller student model on soft + hard labels
4. Validate student performance
5. Iterate on student architecture if needed

### Checklist: Compression ready

- [ ] Quantization strategy selected
- [ ] Accuracy validated post-compression
- [ ] Inference latency measured
- [ ] Model size reduction achieved (target: 2-4x)
- [ ] Production deployment tested

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
