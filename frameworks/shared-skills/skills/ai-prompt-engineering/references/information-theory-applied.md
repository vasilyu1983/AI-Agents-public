# Information Theory Applied to Prompt Engineering

> **Gate before invoking:** Check [`foundations-information-theory` § When to Apply](../../foundations-information-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Anchored to the 11 primitives in [foundations-information-theory](../../foundations-information-theory/SKILL.md). Use this reference when quantifying prompt quality, budgeting token budgets, selecting few-shot examples, or detecting prompt drift._

---

## Table of Contents

- [When to Use This Reference](#when-to-use-this-reference)
- [Patterns](#patterns)
  - [P1 Token-Budget Allocation as Rate-Distortion](#p1-token-budget-allocation-as-rate-distortion)
  - [P2 Redundancy Detection via Prompt-Chunk Entropy](#p2-redundancy-detection-via-prompt-chunk-entropy)
  - [P3 Few-Shot Selection by Mutual Information](#p3-few-shot-selection-by-mutual-information)
  - [P4 KL-Based Prompt-Version Drift Detection](#p4-kl-based-prompt-version-drift-detection)
  - [P5 Information-Bottleneck Framing for Prompt Compression](#p5-information-bottleneck-framing-for-prompt-compression)
  - [P6 MDL Principle for Prompt-Template Choice](#p6-mdl-principle-for-prompt-template-choice)
  - [P7 Cross-Tokenizer Perplexity Caveats](#p7-cross-tokenizer-perplexity-caveats)
  - [P8 Output-Entropy as an Underspecification Signal](#p8-output-entropy-as-an-underspecification-signal)
- [Anti-Patterns](#anti-patterns)
  - [A1 KL Asymmetry Misuse](#a1-kl-asymmetry-misuse)
  - [A2 Adding Examples Without Checking Redundancy](#a2-adding-examples-without-checking-redundancy)
  - [A3 Cross-Tokenizer Perplexity Comparison](#a3-cross-tokenizer-perplexity-comparison)
  - [A4 Politeness Padding with Zero MI](#a4-politeness-padding-with-zero-mi)
  - [A5 Small-Eval Cross-Entropy as Unbiased Comparison](#a5-small-eval-cross-entropy-as-unbiased-comparison)
- [Recipes](#recipes)
  - [R1 Redundancy-Aware Prompt Diet](#r1-redundancy-aware-prompt-diet)
  - [R2 Few-Shot Selection by MI](#r2-few-shot-selection-by-mi)
  - [R3 Prompt-Version Drift Gate](#r3-prompt-version-drift-gate)
- [Composition](#composition)
- [Sources](#sources)

---

## When to Use This Reference

Load this file when the task is one of:

- Setting token budgets for multi-section prompts (system prompt, retrieved context, history, user turn)
- Pruning a long prompt to reduce cost without quality regression
- Choosing which few-shot examples to include in a classification or extraction prompt
- Detecting that a prompt revision has shifted the output distribution significantly
- Diagnosing high-variance outputs from an underspecified prompt

Route other prompt questions to [core-patterns.md](core-patterns.md), [rag-patterns.md](rag-patterns.md), or [reasoning-patterns.md](reasoning-patterns.md).

---

## Patterns

### P1 Token-Budget Allocation as Rate-Distortion

**Anchor:** Primitive #6 — [Rate-Distortion](../../foundations-information-theory/assets/templates/information-theory/06-rate-distortion.md)

**Problem.** A context window has a fixed token ceiling (e.g., 8 192 tokens). Multiple sections compete for space: system instructions, retrieved passages, conversation history, and the user turn. Most teams assign budgets by feel or round-number heuristic, leaving high-value sections under-allocated and low-value sections over-represented.

**Framing.** Rate-distortion theory says: the minimum representation length R(D) at acceptable distortion D is a fundamental, task-specific bound. Apply it per section:

- **Distortion measure**: task-relevant quality loss from truncating the section (e.g., 1 − F1 on a held-out eval, or 1 − ROUGE-L for summarization context).
- **Rate R(D)**: minimum tokens the section needs to preserve acceptable quality.

For a Gaussian approximation (normalized semantic variance σ² = 1):

```
R(D) = ½ log₂(1 / D_acceptable)   [bits; convert to tokens via log₂(vocab_size) bits/token]
```

**Procedure.**

1. For each section, run a truncation sweep: measure quality loss at 25%, 50%, 75%, and 100% of the section's natural length.
2. Identify the token count where quality drops past the acceptable distortion threshold — that is the section's R(D) floor.
3. Allocate tokens in priority order: system instructions first (distortion floor highest), then highest-MI retrieved context, then history (highest-redundancy; most compressible), then user turn.
4. Any remaining budget is slack; do not backfill with low-MI content.

**Example.** A RAG prompt with 8 192-token ceiling, four sections:

| Section | Natural length | Distortion floor | R(D) floor | Priority |
|---------|---------------|-----------------|-----------|----------|
| System instructions | 420 | D ≤ 0.05 | 420 (near-lossless) | 1 |
| Retrieved passages | 6 000 | D ≤ 0.20 | 1 800 | 2 |
| Conversation history | 2 000 | D ≤ 0.30 | 600 | 3 |
| User turn | 200 | D ≤ 0.02 | 200 (near-lossless) | 4 |

Total floor = 3 020 tokens; slack = 5 172. Assign slack to retrieved passages first, then history. Do not bloat system instructions past their natural length.

**Failure mode.** Using the same distortion tolerance for all sections. System instructions tolerate near-zero distortion; conversation history tolerates high distortion. Treating them uniformly wastes budget on low-value verbosity.

---

### P2 Redundancy Detection in Prompts via Repeated-Content Entropy

**Anchor:** Primitive #11 — [Redundancy and Compression](../../foundations-information-theory/assets/templates/information-theory/11-redundancy-compression.md)

**Problem.** Long prompts accumulate redundancy: the same constraint restated three ways, boilerplate preamble that repeats downstream instructions, or retrieved chunks that overlap heavily. Redundancy inflates token cost without adding information.

**Framing.** Redundancy R = log M − H(X). For prompt chunks, the analog is: a chunk whose content is predictable from the rest of the prompt carries R bits of redundancy per token. The Normalized Compression Distance (NCD) operationalizes this without estimating H directly:

```
NCD(chunk_i, chunk_j) = [C(chunk_i + chunk_j) − min(C(chunk_i), C(chunk_j))] / max(C(chunk_i), C(chunk_j))
```

NCD ≈ 0 means the two chunks compress well together (high shared content = high redundancy). NCD ≈ 1 means they are informationally independent.

**Procedure.**

1. Split the prompt into logical chunks (sections delimited by headers, or semantic paragraphs of ~100 tokens).
2. Compute pairwise NCD using a fast compressor (zstd or bzip2). Flag pairs with NCD < 0.20 as high-redundancy.
3. For the flagged pair, keep the chunk with higher MI to the task output (→ see P3 for MI estimation) and remove the other.
4. Re-run output quality check after removal. Stop when removing any remaining chunk degrades quality.

**Example.** A 1 400-token instruction prompt for a classification task:

```
Chunk A (lines 1–40):   "You are a classification assistant. Your job is to classify..."
Chunk B (lines 80–120): "Remember, your role is to act as a classifier that assigns..."
Chunk C (lines 200–240): Retrieved policy text (unique content)

NCD(A, B) = 0.11  → near-duplicate; remove B (lower MI with gold labels)
NCD(A, C) = 0.84  → independent; keep both
NCD(B, C) = 0.79  → independent (moot; B already removed)
```

Result: 1 400 tokens → ~1 000 tokens, no quality loss on held-out eval.

---

### P3 Few-Shot Selection by Mutual Information

**Anchor:** Primitive #2 — [Mutual Information](../../foundations-information-theory/assets/templates/information-theory/02-mutual-information.md)

**Problem.** A candidate pool of 50 labeled examples exists for a few-shot classification prompt. Selecting k = 5 examples by random sampling or by similarity to the test input ignores the information each example provides about the target label distribution.

**Framing.** For few-shot selection, define:

- X = the example (input text + label)
- Y = model output quality on the target task (e.g., correct classification or match to gold extraction)

The MI criterion selects the k examples that maximize I(selected set ; Y) while minimizing redundancy within the set.

By the chain rule for MI:

```
I(X₁, ..., Xₖ ; Y) = Σᵢ I(Xᵢ ; Y | X₁, ..., Xᵢ₋₁)
```

Each additional example contributes its conditional MI given already-selected examples. Near-duplicate examples contribute near-zero conditional MI.

**Procedure.**

1. Draw a small eval set (30–50 labeled inputs) from the target distribution.
2. For each candidate example e, measure the quality gain when e is added to an empty prompt vs. a prompt already containing the current selection (greedy marginal MI estimate).
3. Select greedily: at each step, add the example with the highest marginal quality gain.
4. Stop at budget k or when the next marginal gain drops below a threshold.
5. Ablate: remove each selected example one at a time; confirm all contribute non-trivially.

**Example.** Classification task, 10 candidates, budget k = 3:

| Example | Marginal quality gain (F1 delta) | Notes |
|---------|----------------------------------|-------|
| e₃ | +0.14 | First pick |
| e₇ | +0.09 | Second pick; covers underrepresented label |
| e₁ | +0.07 | Third pick |
| e₂ | +0.01 | Near-duplicate of e₃; skip |
| e₉ | +0.00 | Redundant given e₃ + e₇ |

Random selection hit +0.11 on average across 100 trials; MI-greedy selection hit +0.21 — a 90% relative gain from 3 examples.

**Note.** This is an empirical approximation of MI using quality gain as a proxy. Direct MI estimation between tokenized example texts and output distributions requires a larger evaluation set (≥200) for reliable estimates; see Primitive #2 failure modes on sample bias.

---

### P4 KL-Based Prompt-Version Drift Detection

**Anchor:** Primitive #3 — [KL Divergence](../../foundations-information-theory/assets/templates/information-theory/03-kl-divergence.md)

**Problem.** Prompt v2 is shipped as a "minor wording fix," but the output distribution has shifted in ways that eval metrics don't immediately surface — different distribution over response lengths, changed label frequencies, altered refusal rates.

**Framing.** For a shared set of n test inputs, collect output token distributions from prompt v1 (P) and prompt v2 (Q). Compute:

```
D_KL(P ‖ Q) = Σ_token p(token) log [ p(token) / q(token) ]
```

Use forward KL (v1 as reference, v2 as approximation): penalizes v2 for missing probability mass that v1 places on certain outputs. A high forward KL means v2 is producing outputs v1 would consider unlikely.

For a symmetric view — appropriate when neither version is the ground truth — use Jensen-Shannon divergence:

```
JSD(P, Q) = ½ D_KL(P ‖ M) + ½ D_KL(Q ‖ M)   where M = ½(P + Q)
JSD ∈ [0, log 2]
```

**Practical thresholds (starting points; tune to your task):**

| JSD | Interpretation |
|-----|----------------|
| < 0.05 | Negligible drift; safe to ship |
| 0.05 – 0.15 | Moderate drift; inspect changed outputs |
| > 0.15 | Significant drift; mandatory human review before shipping |

**Example.** A sentiment classification prompt. v1 → v2 was a phrasing change in the instruction clause.

```
D_KL(v1 ‖ v2) = 0.22 bits   → v2 places mass on outputs v1 never produced
JSD(v1, v2)   = 0.18         → above 0.15 threshold; human review triggered
```

Review found: v2's phrasing caused the model to output "neutral" for 12% of previously "negative" inputs. The eval F1 metric was insensitive because the test set was balanced — JSD caught what F1 missed.

**Direction discipline.** Always state direction explicitly. D_KL(v1‖v2) asks: "how surprised would v1 be by v2's outputs?" D_KL(v2‖v1) asks the reverse. In a CI/CD prompt gate, use JSD as the primary scalar unless the regression direction matters asymmetrically (e.g., false-negative increases are more costly than false-positive increases).

---

### P5 Information-Bottleneck Framing for Prompt Compression

**Anchor:** Primitive #8 — [Information Bottleneck](../../foundations-information-theory/assets/templates/information-theory/08-information-bottleneck.md)

**Problem.** A 600-token system prompt was written incrementally and contains explanatory context, motivational framing, and edge-case elaboration that made sense during development but may be irrelevant to production outputs. Cutting tokens blindly risks removing task-critical signal.

**Framing.** Apply IB: find a compressed prompt T of length L ≤ budget that preserves I(T; output) while minimizing I(T; original prompt) — i.e., discard only what is irrelevant to what the model actually outputs.

```
min_T [ I(original_prompt ; T) − β · I(T ; output) ]
```

High β → preserve output fidelity (compress conservatively). Low β → compress aggressively, accepting output change.

**Procedure.**

1. Collect 200+ (prompt, output) pairs from the current production prompt.
2. Systematically ablate prompt sections: run the same inputs with each section removed. Measure I(T; output) proxy = output distribution similarity (JSD or quality metric delta).
3. Plot the IB curve: x-axis = tokens retained (I(T; original_prompt) proxy), y-axis = I(T; output) proxy.
4. Identify the knee of the curve — the compression level past which I(T; output) drops steeply. Set the token budget at the knee, not at the hard minimum.
5. Sections that fall below the curve (removing them costs little in I(T; output)) are safe to drop.

**Example.** From the Primitive #8 worked example applied to prompts:

| Tokens retained | I(T; output) retention |
|-----------------|------------------------|
| 600 (full) | 100% |
| 400 | 97% |
| 250 | 91% |
| 150 | 78% |
| 80 | 51% |

Knee is at ~250 tokens: 58% compression at 9% output change. Below 150 tokens, fidelity collapses. Set budget to 250, not 150.

---

### P6 MDL Principle for Prompt-Template Choice

**Anchor:** Primitive #7 — [MDL Principle](../../foundations-information-theory/assets/templates/information-theory/07-mdl-principle.md)

**Problem.** Two prompt templates produce similar quality on a held-out eval. Template A is 800 tokens; Template B is 340 tokens. A common mistake is to keep A because it feels "more thorough" or because its development cost was higher.

**Framing.** MDL: the better model is the one with the shortest total description length — model complexity plus the residual data description cost. In prompt terms:

```
MDL(template) = L(template) + L(output_errors | template)
```

- L(template) = token count (proxy for description cost)
- L(output_errors | template) = negative log-likelihood of errors on the eval set given the template (or equivalently, the cross-entropy loss)

If Template B achieves the same output quality as Template A with 460 fewer tokens, Template B has a lower MDL score — it explains the task equally well at lower cost. Prefer B.

**When A beats B despite being longer.** If Template A produces measurably lower error rates, its L(output_errors | template) term offsets its higher L(template). Compute both terms before deciding.

**Procedure.**

1. For each candidate template, record: token count (L(template)) and cross-entropy loss on a held-out eval set (L(output_errors | template), in nats or bits).
2. Sum: MDL score = token_count × weight_factor + cross_entropy × scale_factor. (The relative weighting is task-specific; start with equal weight after normalizing both terms to [0,1].)
3. Select the template with the minimum MDL score.
4. Break ties in favor of the shorter template (lower maintenance burden, lower cost per call).

**Example.**

| Template | Tokens | CE loss (bits) | MDL score (normalized) |
|----------|--------|---------------|------------------------|
| A | 800 | 0.31 | 0.67 |
| B | 340 | 0.34 | 0.43 |
| C | 120 | 0.61 | 0.52 |

Template B wins: smaller MDL score than A despite slightly higher CE loss. Template C is too terse; its CE loss penalty dominates.

---

### P7 Cross-Tokenizer Perplexity Caveats

**Anchor:** Primitive #4 — [Cross-Entropy and Perplexity](../../foundations-information-theory/assets/templates/information-theory/04-cross-entropy.md)

**Problem.** A team benchmarks prompt quality by perplexity across two providers: Provider A (GPT-4o, tiktoken cl100k vocabulary, 100 257 tokens) and Provider B (Claude 3.7, BPE vocabulary of ~200 000 merge rules). Provider A returns perplexity 14.2; Provider B returns 22.7. The team concludes Provider A's prompt is better.

**Why this is wrong.** Perplexity = exp(H(P, Q)) is defined over a specific vocabulary and tokenization. A model with a larger vocabulary typically tokenizes text into fewer tokens; each token carries more information. Fewer tokens = lower sequence-level perplexity, for reasons unrelated to prompt quality or model capability.

**Fix.** Normalize to bits-per-byte (BPB):

```
BPB = H(P, Q) / (bytes of text)
```

BPB is vocabulary-agnostic. Both providers, evaluated on the same byte stream, produce comparable BPB scores regardless of tokenizer.

**In prompt eval practice.** When comparing prompt v1 vs. v2 on the same provider and tokenizer, raw perplexity is valid as a relative metric. When comparing across providers — for example, choosing whether to port a Claude prompt to GPT-4o — use BPB or task-specific quality metrics, never raw perplexity.

**Additional caveat: prompt content influences token count.** A prompt with many rare technical terms tokenizes into more tokens than a plain-language equivalent. Higher token count inflates the sequence perplexity even at identical BPB. When reporting eval results, always state: tokenizer, token count, and whether scores are per-token or per-byte.

---

### P8 Output-Entropy as an Underspecification Signal

**Anchor:** Primitive #1 — [Shannon Entropy](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md), Primitive #9 — [Fano's Inequality](../../foundations-information-theory/assets/templates/information-theory/09-fano-inequality.md)

**Problem.** A prompt produces high output variance across runs on identical inputs (temperature > 0), or produces different answers when paraphrased inputs are given. The team diagnoses this as "model instability" when the real cause is an underspecified prompt.

**Framing.** Measure H(output | prompt) empirically:

1. Run the same prompt on N = 20–50 identical inputs with sampling (temperature 0.7 or as deployed).
2. Discretize outputs into bins (e.g., by response category, label, or length bucket).
3. Estimate the output entropy: H(output | prompt) = −Σ p̂(oᵢ) log p̂(oᵢ).

A well-specified prompt for a classification task should produce H ≈ 0 (deterministic). For a creative task H > 0 is expected. The signal is how H changes as prompt constraints are added:

- High H on a task that should be deterministic = underspecified prompt. Add output schema, explicit constraints, or worked examples.
- H drops < 0.2 bits after adding constraints = the constraint is effective.
- H stays high despite constraints = the remaining variance is model-intrinsic, not prompt-correctable.

**Fano's Inequality lower bound.** If H(output | prompt) = h bits and the output has k classes, Fano bounds the minimum achievable classification error:

```
P_e ≥ (h − 1) / log₂ k
```

For a binary classification prompt with H(output | prompt) = 0.8 bits:

```
P_e ≥ (0.8 − 1) / 1 = −0.2 → bound is vacuous (clipped to 0)
```

For H = 1.5 bits with k = 4 classes (log₂ 4 = 2 bits):

```
P_e ≥ (1.5 − 1) / 2 = 0.25   → at least 25% error is unavoidable given this residual entropy
```

This tells you: before investing in model fine-tuning or eval infrastructure, fix the prompt's residual entropy first.

---

## Anti-Patterns

### A1 KL Asymmetry Misuse

**Anchor:** Primitive #3

**Trap.** Computing D_KL(P ‖ Q) and D_KL(Q ‖ P) interchangeably when measuring output distribution similarity between prompt versions, then drawing the same conclusion from both.

**Why it fails.** D_KL is not symmetric. D_KL(v1 ‖ v2) = 0.4 bits means v2's outputs include sequences v1 never produced (v2 is more spread or shifted). D_KL(v2 ‖ v1) = 0.4 bits means v1's outputs include sequences v2 never produces (v1 is the broader distribution). These are different failure modes requiring different remedies.

**Fix.** Always state direction explicitly in eval reports. Use JSD for symmetric prompt comparison. Use forward D_KL(v_old ‖ v_new) when the old prompt is the reference; use reverse D_KL(v_new ‖ v_old) when you care about v_new covering all behaviors v_old exhibited. Report both when direction is ambiguous.

---

### A2 Adding Examples Without Checking Redundancy

**Anchor:** Primitive #2, Primitive #11

**Trap.** Quality is below target. The default response is to add more few-shot examples. Five examples become eight, then twelve. Token budget inflates; quality plateaus.

**Why it fails.** Each new example contributes I(Xᵢ ; Y | X₁,...,Xᵢ₋₁) — its marginal MI given examples already selected. Near-duplicate examples (same label, similar input style) contribute near-zero conditional MI while consuming tokens. Adding them is redundancy-padding, not information addition.

**Fix.** Before adding example k+1, compute its NCD against the existing k examples. If NCD < 0.25 against any existing example, it is redundant. Replace it with a diverse example that covers a different input distribution or label boundary instead.

---

### A3 Cross-Tokenizer Perplexity Comparison

**Anchor:** Primitive #4

**Trap.** Selecting a provider or model by comparing perplexity scores from different tokenizers as if they are on a common scale.

**Why it fails.** A model with a 100k-token vocabulary tokenizes the same text into fewer tokens than a 32k-token vocabulary model. Fewer tokens, each carrying more information, produces lower per-token perplexity even at equal BPB. The raw perplexity difference reflects tokenizer granularity, not model quality. See P7 for the full example where this inverts the ranking.

**Fix.** Normalize to BPB for any cross-provider or cross-tokenizer comparison. Use task F1, BLEU, or EM for downstream quality; use BPB only when comparing language modeling capability specifically.

---

### A4 Padding Prompts with Politeness Preamble

**Anchor:** Primitive #2, Primitive #7

**Trap.** Prompts begin with: "You are an extremely helpful, thoughtful, and meticulous assistant who always tries your hardest to..." followed by 80 tokens of motivational framing before the actual task instruction.

**Why it fails.** This preamble has I(preamble ; task_output) ≈ 0: it contributes near-zero mutual information with the target output. By MDL, it increases L(template) with no reduction in L(output_errors | template). It costs tokens, contributes latency (proportional to context length in prefill), and provides no signal.

**Fix.** Apply the MDL test: remove the preamble and measure eval quality. If quality is unchanged (as it nearly always is for well-specified task instructions), remove permanently. Keep only the constraints and context that carry MI with the output.

---

### A5 Small-Eval Cross-Entropy as Unbiased Prompt Comparison

**Anchor:** Primitive #4, Primitive #2

**Trap.** A 20-item eval set is used to compare two prompt variants by cross-entropy loss. Prompt v2 wins by 0.08 bits. The team ships v2.

**Why it fails.** Cross-entropy on a small eval set is a noisy estimator. At n = 20, the standard error of the mean CE is O(1/√20) ≈ 0.22 bits for typical LLM output distributions — larger than the 0.08-bit measured difference. The result is not statistically significant; either prompt could be better.

Additionally, cross-entropy conflates irreducible data entropy H(P) with model approximation D_KL(P ‖ Q). A prompt that reduces output variance (lowers H(P) by narrowing the task) will show lower CE even without improving model accuracy.

**Fix.** Use at least 100 eval inputs for CE comparisons. Report confidence intervals. Decompose CE = H(P) + KL to distinguish prompt-induced variance reduction from genuine quality improvement. Supplement CE with task metrics (F1, exact match, human preference) on a separate held-out set.

---

## Recipes

### R1 Redundancy-Aware Prompt Diet

**Goal:** Iteratively compress a long prompt while preserving output quality.

**Anchors:** Primitive #11 (redundancy, NCD), Primitive #2 (MI), Primitive #8 (IB framing)

**Inputs:**
- Current prompt (text, any length)
- Eval set: 50–200 (input, gold_output) pairs
- Quality threshold: minimum acceptable quality score (e.g., F1 ≥ 0.82)
- Budget: target token count or cost reduction target

**Steps:**

```
1. CHUNK: Split prompt into logical sections (header delimiters or ~100-token paragraphs).

2. PAIRWISE NCD: For each pair of chunks (i, j), compute:
     NCD(i, j) = [C(i + j) - min(C(i), C(j))] / max(C(i), C(j))
   using zstd or bzip2. Flag pairs with NCD < 0.25 as redundant candidates.

3. MI TRIAGE: For each flagged redundant pair, estimate which chunk carries higher MI
   with the task output:
     - Run eval with chunk_i removed; record quality_without_i
     - Run eval with chunk_j removed; record quality_without_j
     - Keep the chunk whose removal causes larger quality drop (higher MI)
     - Mark the other as a removal candidate

4. REMOVE: Drop the marked chunk from the prompt.

5. EVAL: Re-run the full eval set on the trimmed prompt. Check quality ≥ threshold.
     - If quality holds: commit removal, return to step 1
     - If quality drops: restore the chunk; it is not redundant despite high NCD

6. TERMINATE: Stop when no more redundant pairs exist or budget is reached.
```

**Expected outcome:** 20–40% token reduction for prompts written incrementally over multiple iterations, with < 2% quality loss. Prompts written tightly from scratch typically yield < 10% reduction.

**Pitfall:** NCD detects surface-level textual redundancy. Two chunks can have NCD ≈ 1 (no textual overlap) yet still be informationally redundant if they both serve to activate the same model behavior. Always confirm with the eval step; never remove by NCD alone.

---

### R2 Few-Shot Selection by MI

**Goal:** Select the k most informative few-shot examples from a candidate pool, subject to a token budget.

**Anchors:** Primitive #2 (MI, chain rule), Primitive #11 (redundancy), Primitive #1 (entropy)

**Inputs:**
- Candidate pool: N labeled examples (N = 20–100 typical)
- Small eval set: 30–60 labeled inputs from the target distribution
- Budget: k examples and/or maximum token count for examples section

**Steps:**

```
1. BASELINE: Run eval with zero examples. Record baseline quality Q₀.

2. MARGINAL GAIN (first example):
   For each candidate eᵢ in the pool:
     - Build a prompt containing only eᵢ as the single few-shot example
     - Run eval; record Qᵢ
     - Marginal gain₁(eᵢ) = Qᵢ - Q₀
   Select e* = argmax marginal_gain₁; add to selected set S = {e*}

3. MARGINAL GAIN (subsequent examples):
   For each remaining candidate eᵢ:
     - Build a prompt containing S ∪ {eᵢ}
     - Run eval; record Q(S ∪ {eᵢ})
     - Marginal gain(eᵢ | S) = Q(S ∪ {eᵢ}) - Q(S)
   Select e* = argmax marginal_gain(eᵢ | S); add to S if gain > threshold

4. REPEAT step 3 until:
   - |S| = k (budget reached), or
   - The best marginal gain < 0.01 (diminishing returns), or
   - Token budget for examples section is exhausted

5. ABLATE: For each eᵢ ∈ S, test quality with eᵢ removed. If removal causes < 0.005 quality
   drop, eᵢ is redundant — remove it and replace with the next-best candidate.

6. VALIDATE: Run the final selected set on a separate held-out eval (not used in steps 1–5)
   to detect overfitting to the eval set.
```

**Expected outcome:** For k = 5, MI-greedy selection typically outperforms random selection by 10–25% relative quality gain, with 30–50% fewer examples than a naive "more examples is better" approach.

**Cost note.** Step 3 requires N eval runs per selection step, totaling O(N × k) evals. For large N and small k, cap at k = 5–8 unless the eval is cheap. For N > 50 and tight compute budgets, pre-filter candidates by textual diversity (NCD > 0.6 against each other) before running MI steps.

---

### R3 Prompt-Version Drift Gate

**Goal:** Automatically flag prompt versions that have shifted the output distribution beyond a safe threshold, blocking silent regressions from shipping.

**Anchors:** Primitive #3 (KL divergence, JSD), Primitive #4 (cross-entropy), Primitive #1 (entropy)

**Inputs:**
- Prompt v_old (current production version)
- Prompt v_new (candidate version)
- Shared input set: 50–200 inputs drawn from production traffic (same inputs for both versions)
- Tolerance threshold: JSD_max (suggested starting point: 0.10 for low-stakes tasks, 0.05 for high-stakes tasks)

**Steps:**

```
1. COLLECT OUTPUTS:
   For each input xᵢ in the shared set:
     - Run v_old → collect output o_old_i
     - Run v_new → collect output o_new_i
   (Use the same temperature and sampling parameters for both)

2. BUILD DISTRIBUTIONS:
   For label-output tasks (classification, routing):
     - P = empirical distribution over labels from v_old outputs
     - Q = empirical distribution over labels from v_new outputs

   For free-text tasks (summarization, generation):
     - Discretize by: output length bucket, presence of key phrases, or semantic cluster
     - P, Q = empirical distributions over discretized outputs

3. COMPUTE DIVERGENCE:
   JSD(P, Q) = ½ D_KL(P ‖ M) + ½ D_KL(Q ‖ M)   where M = ½(P + Q)
   D_KL(P ‖ Q)   [forward KL: v_old as reference]

4. GATE:
   if JSD > JSD_max:
     BLOCK release; trigger human review
     Log: which output categories shifted most (top-3 by |P(oᵢ) - Q(oᵢ)|)
   else if 0.05 < JSD ≤ JSD_max:
     FLAG for review; allow release with annotation
   else:
     PASS; release approved

5. REVIEW PROTOCOL (when blocked):
   - Inspect the top-3 shifted output categories
   - Check whether the shift is intentional (v_new was supposed to change this behavior)
     → If intentional: update baseline P to v_new; re-gate against future versions
     → If unintentional: revert v_new change or fix and re-run gate

6. BASELINE UPDATE: After v_new ships, promote v_new outputs as the new P baseline
   for the next comparison cycle.
```

**Example run:**

```
Input set: 100 support-ticket classifications
v_old label distribution: {positive: 0.42, neutral: 0.38, negative: 0.20}
v_new label distribution: {positive: 0.31, neutral: 0.42, negative: 0.27}

D_KL(v_old ‖ v_new) = 0.19 bits
JSD(v_old, v_new)   = 0.14

JSD > 0.10 threshold → BLOCKED for high-stakes task
Top shifted category: "negative" class (+7 pp); "positive" class (-11 pp)
Investigation: v_new's phrasing change inadvertently increased negativity detection sensitivity
Resolution: roll back phrasing; re-run gate → JSD = 0.03 → PASS
```

**Integration point.** This gate fits inside a prompt CI/CD pipeline alongside regression eval (see [prompt-testing-ci-cd.md](prompt-testing-ci-cd.md)). JSD is computed cheaply from pre-existing eval runs — no additional model calls needed beyond the eval suite already required for quality checks.

---

## Composition

When multiple patterns apply to the same prompt work:

| Workflow | Primitives Used | Recommended Order |
|----------|-----------------|-------------------|
| New prompt from scratch | P6 (MDL), P8 (output entropy), P3 (few-shot MI) | Choose template by MDL first; tune examples by MI; verify with output entropy |
| Prompt cost reduction | P1 (rate-distortion), R1 (redundancy diet), P5 (IB) | Budget by R-D first; remove redundancy; apply IB to find the compression knee |
| Prompt regression testing | R3 (drift gate), A5 (eval size), P4 (KL direction) | Gate on JSD; confirm eval set is large enough; choose KL direction intentionally |
| Few-shot quality debug | P3 (MI), A2 (redundancy), P8 (output entropy) | Check output entropy first (is the prompt underspecified?); then run MI selection; check for redundant examples |
| Cross-provider migration | P7 (BPB), R3 (drift gate), A3 (perplexity) | Normalize to BPB; run drift gate on migrated outputs; never compare raw perplexity |

The full information-theory composition recipes (context window budgeting, retrieval reranking, prompt complexity diagnosis) are in the [foundations-information-theory SKILL.md](../../foundations-information-theory/SKILL.md#composition-recipes).

**Primitives not directly instantiated here but relevant at the margins:**

- **Channel Capacity — Primitive #5**: bounds how much information a prompt can reliably convey to the model per token given the effective noise introduced by stochastic decoding and context compression. Use Primitive #5 as a ceiling argument when a prompt designer claims "more instructions always help" — the channel has a finite capacity.
- **Typical Sets / AEP — Primitive #10**: informs how many eval samples are needed for a prompt evaluation to land in the typical set of output sequences and thus produce reliable entropy estimates. The AEP result — that roughly 2^{nH} typical sequences require n samples to observe — justifies the ≥100-input eval set recommendation in A5 and R3.

---

## Sources

- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed. Wiley. — Primary reference for all 11 primitives.
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*. Cambridge. — Accessible derivations; free PDF at inference.org.uk.
- Tishby, N., Pereira, F. C. & Bialek, W. (2000). The information bottleneck method. *arXiv:physics/0004057*. — P5 (IB framing for compression).
- Saxe, A. M. et al. (2018). On the information bottleneck theory of deep learning. *ICLR 2019, arXiv:1805.05815*. — IB rebuttal; do not assert IB explains DNN generalization.
- Cilibrasi, R. & Vitányi, P. M. B. (2005). Clustering by compression. *IEEE Transactions on Information Theory*, 51(4). — NCD used in P2 and R1.
- Stiennon, N. et al. (2020). Learning to summarize with human feedback. *NeurIPS 2020*. — KL direction discipline (P4, A1) in RLHF context.
- Grünwald, P. (2007). *The Minimum Description Length Principle*. MIT Press. — P6 (MDL for template choice).
- Paninski, L. (2003). Estimation of entropy and mutual information. *Neural Computation*, 15(6). — MI estimation bias; P3 note on sample requirements.

_Per-primitive playbooks: [../../foundations-information-theory/assets/templates/information-theory/](../../foundations-information-theory/assets/templates/information-theory/)_
