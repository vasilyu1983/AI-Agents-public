# Data Ablation Method Reference

Canonical source: [ai-data-curation-pretraining/SKILL.md](../SKILL.md)

## Table of Contents

- [What a Data Ablation Is](#what-a-data-ablation-is)
- [One Change Per Run — The Core Discipline](#one-change-per-run--the-core-discipline)
- [Proxy Model Setup](#proxy-model-setup)
- [Compute Budget Protocol](#compute-budget-protocol)
- [Standard Ablation Runs A–E](#standard-ablation-runs-ae)
- [Evaluation Suite](#evaluation-suite)
- [Metric Collection and Reporting](#metric-collection-and-reporting)
- [Decontamination Before Each Run](#decontamination-before-each-run)
- [Datasheet Template (Gebru et al.)](#datasheet-template-gebru-et-al)
- [Common Ablation Failures](#common-ablation-failures)

---

## What a Data Ablation Is

A data ablation is a controlled experiment that isolates the effect of a single data pipeline change on downstream model quality. The research output is the eval delta: how much does a specific curation decision move benchmark performance at fixed compute?

Data ablations are the primary empirical method for data curation research. FineWeb, Dolma, RedPajama v2, and SlimPajama all used ablations to justify their pipeline choices.

**Not a data ablation**: training with different architectures, different learning rates, or different tokenizers in the same comparison. Changes to non-data variables confound the data signal.

---

## One Change Per Run — The Core Discipline

Every ablation run must differ from its comparison by exactly one variable:

- Same model architecture
- Same model size
- Same total training compute (tokens × FLOPs per token)
- Same learning rate schedule
- Same tokenizer
- Same evaluation suite and prompt format

If two variables change between runs, you cannot attribute the eval delta to either one. This is the most common ablation failure in published work.

---

## Proxy Model Setup

Train at small scale to make ablations feasible. Full-scale training costs make ablations impractical for most research settings.

**Recommended proxy model sizes**:
- 125M–350M parameters: fast iteration (< 4 GPU-hours per run), coarse signal
- 1B parameters: standard proxy; good correlation with 7B/13B behavior on most benchmarks
- 3B parameters: use when 1B shows high variance or when the benchmark requires more capacity

**Architecture**: use a standard decoder-only transformer. Match the architecture family you plan to scale to (e.g., LLaMA architecture if targeting LLaMA-family). Do not change architecture between ablation runs.

**Tokenizer**: use the production tokenizer. Changing tokenizers invalidates cross-run comparisons because token counts differ.

**Training framework**: nanotron (HuggingFace), GPT-NeoX, or any framework that produces deterministic checkpoints given the same seed. Log the random seed for reproducibility.

---

## Compute Budget Protocol

Fix total compute across all ablation runs. Compute = tokens × parameters × 6 (for a standard dense transformer, FLOPs ≈ 6 × N × D where N = params, D = tokens).

**Chinchilla-optimal ratio as a starting point**: for a 1B parameter proxy model, Chinchilla-optimal is approximately 20B tokens. This is a reasonable ablation budget.

**Practical approach**:
1. Set a token budget (e.g., 20B tokens for a 1B proxy model).
2. Sample this token count from each corpus variant.
3. Train to exactly this token count.
4. Do not stop early or extend based on loss — fixed compute is the control variable.

If the filtered corpus has fewer than 20B tokens after curation, either reduce the token budget for all runs or upsample the filtered corpus (document epoch > 1). Document which approach you used.

---

## Standard Ablation Runs A–E

| Run | Corpus Description | Key Variable | Purpose |
|-----|--------------------|--------------|---------|
| A | Raw CC extraction (no filter beyond extraction) | Baseline | Establishes noisy ceiling; quantifies what filtering removes |
| B | + Heuristic filter (Gopher + C4) + MinHash near-dedup | Heuristic filter + dedup | Measures combined heuristic + dedup value |
| C | + Classifier-based quality filter (edu-score or domain classifier) | Classifier filter | Measures uplift of classifier over heuristics alone |
| D | + Synthetic data at 10% mix | Synthetic mixture | Measures synthetic uplift on target domain |
| E | Mixing-ratio sweep (vary domain proportions) | Domain mix ratios | Identifies optimal mix for target task profile |

Run B and C without synthetic data. Run D on top of C's best checkpoint corpus. Run E as a hyperparameter sweep: 3–5 ratio variants, evaluate each.

**Set the mix with a method, not by hand.** A blind 3–5 point sweep is a weak way to find domain weights. Use a principled mixing method to set the prior, then confirm with Run E:

- **DoReMi** (arXiv 2305.10429): group-DRO on a small proxy finds weights minimizing worst-case excess loss; transfer to the full run.
- **Data Mixing Laws** (arXiv 2403.16952): fit a scaling-law surface over ratios from cheap proxy runs and extrapolate the optimum before spending full compute.
- **RegMix** (arXiv 2407.01492): regress performance over many random small-model mixtures; pick the predicted-best ratio. Compute-cheaper than DoReMi.

These methods choose the candidate ratios for Run E; the ablation validates them under your exact eval suite. The one-change discipline still holds — vary only the mixture between Run E variants.

**Reporting**: always report A as the baseline. Report absolute numbers, not only deltas. Include standard deviation across seeds (run each ablation with 3 seeds if compute allows).

---

## Evaluation Suite

Use lm-evaluation-harness (EleutherAI) for all evaluation runs. Fix the evaluation commit hash at the start of the ablation study and do not update it during the study.

**Core benchmarks for general ablations**:

| Benchmark | Task Type | Why Include |
|-----------|-----------|-------------|
| HellaSwag | Sentence completion | Sensitive to web-text quality |
| ARC-Easy + ARC-Challenge | Multiple choice reasoning | Sensitive to knowledge density |
| MMLU (0-shot) | Knowledge, multiple choice | Broad knowledge coverage |
| WinoGrande | Coreference resolution | Sensitive to syntactic diversity |
| TriviaQA | Open-domain QA | Factual recall |

**Domain-specific additions**:
- Code: HumanEval pass@1, MBPP
- Math: GSM8K, MATH (requires 3B+ proxy)
- Science: SciQ, ARC-Challenge

**Prompt format**: lock the prompt format for each benchmark at the start. Changing prompt format between runs produces confounded results.

---

## Metric Collection and Reporting

Collect and report:

1. **Eval accuracy per benchmark** — absolute score, not only delta.
2. **Perplexity on held-out validation set** — use the same validation set (e.g., a 100M-token held-out slice of filtered CC) across all runs.
3. **Training loss curve** — log at every 1000 steps. Loss curves that diverge early indicate a data quality issue, not a training issue.
4. **Corpus statistics** — token count, document count, unique URL count, language distribution, domain distribution (by URL pattern or classifier).
5. **Drop rates** — fraction removed at each pipeline stage.

**Variance**: report mean ± std across 3 seeds. A delta smaller than 1 std is not conclusive evidence of effect.

**Do not cherry-pick benchmarks** after seeing results. Pre-register the benchmark suite before running ablations.

---

## Decontamination Before Each Run

Decontaminate each corpus variant independently before training. Do not assume that decontaminating run A's corpus also covers run D's corpus — synthetic data can introduce new contamination.

**Protocol**:
1. Extract 13-grams from all benchmarks you plan to evaluate on (train and test splits).
2. Hash and store in a Bloom filter or exact hash set.
3. For each document in the corpus variant, extract 13-grams and check against the hash set.
4. Remove documents with any match. Log removed documents.
5. Record the decontamination date and the benchmark version (commit hash or download date).

**Include this in the datasheet**: list every benchmark you decontaminated against and the n-gram threshold used.

---

## Datasheet Template (Gebru et al.)

A datasheet must accompany any corpus released publicly or handed to another team. Gebru et al. (arXiv 1803.09010) defines the standard.

**Required sections**:

**Motivation**
- For what purpose was the dataset created?
- Who created it and on whose behalf?
- Who funded the creation?

**Composition**
- What are the instances? (documents, tokens, languages)
- How many instances are there?
- Does the dataset contain all possible instances or a sample?
- Is there a label or target associated with each instance?
- Is any information missing from individual instances?
- Are there recommended data splits?

**Collection Process**
- How was the data acquired?
- What mechanisms or procedures were used?
- Who was involved in the data collection process?
- Over what timeframe was the data collected?

**Preprocessing / Cleaning / Labeling**
- Was any preprocessing or cleaning done? If so, what?
- Was the raw data saved? Is it accessible?
- Is the software used for preprocessing available?

**Uses**
- Has the dataset been used already?
- What tasks could the dataset be used for?
- Is there anything about the composition that might affect future uses?
- Are there tasks for which the dataset should not be used?

**Distribution**
- Will the dataset be distributed? Under what license?
- When will it be distributed?
- Will the dataset be maintained?

**Maintenance**
- Who is supporting/hosting/maintaining the dataset?
- How can the owner be contacted?
- Will the dataset be updated?
- Are there applicable limits on dataset retention?

**Ablation Notes** (addition for pretraining corpora):
- What ablation runs were conducted?
- What was the proxy model configuration?
- What was the compute budget per run?
- Which benchmarks were evaluated?
- Were results decontaminated?

---

## Common Ablation Failures

1. **Two variables change between runs** — cannot attribute the eval delta. Fix: enforce the one-change rule before starting.

2. **Token budget not held constant** — run D has more tokens because synthetic data boosted the count. Fix: sample to a fixed token target.

3. **Evaluation benchmarks changed mid-study** — a new lm-evaluation-harness version changed the prompt format. Fix: lock the harness commit hash.

4. **Decontamination skipped for synthetic runs** — synthetic data from a web-trained generator may contain benchmark content. Fix: decontaminate every corpus variant independently.

5. **Results reported without error bars** — a 0.5-point improvement on HellaSwag with a 1B model and one seed is within noise. Fix: run 3 seeds; report mean ± std.

6. **Cherry-picked benchmarks** — benchmarks were selected after seeing results to make the finding look stronger. Fix: pre-register the benchmark suite.
