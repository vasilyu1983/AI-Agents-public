# Data Ablation Method Reference

Canonical source: [ai-data-curation-pretraining/SKILL.md](../SKILL.md)

## Table of Contents

- [What a Data Ablation Is](#what-a-data-ablation-is)
- [One Change Per Run — The Core Discipline](#one-change-per-run--the-core-discipline)
- [Proxy Model Setup](#proxy-model-setup)
- [Compute Budget Protocol](#compute-budget-protocol)
- [Standard Ablation Runs A–F](#standard-ablation-runs-af)
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
- 125M–350M parameters: fast iteration, coarse signal; estimate runtime on the actual hardware before budgeting
- ~1B parameters: common proxy (FineWeb used 1.71B including embeddings, ≈28B tokens). Correlation with larger-model behavior is benchmark-dependent; check it rather than assume it
- 3B parameters: use when 1B shows high variance or when the benchmark requires more capacity

**Architecture**: use a standard decoder-only transformer. Match the architecture family you plan to scale to (e.g., LLaMA architecture if targeting LLaMA-family). Do not change architecture between ablation runs.

**Tokenizer**: use the production tokenizer. Changing tokenizers invalidates cross-run comparisons because token counts differ.

**Training framework**: nanotron (HuggingFace), GPT-NeoX, or any framework that produces deterministic checkpoints given the same seed. Log the random seed for reproducibility.

---

## Compute Budget Protocol

Fix total compute across all ablation runs. Compute = tokens × parameters × 6 (for a standard dense transformer, FLOPs ≈ 6 × N × D where N = params, D = tokens).

**Token budget**: set one budget that every corpus variant can supply and that your hardware can complete. A model-to-token scaling-law ratio is a planning input, not a universal ablation budget; record the chosen horizon and any repeated epochs.

**Practical approach**:
1. Set a token budget that all variants can meet.
2. Sample this token count from each corpus variant.
3. Train to exactly this token count.
4. Do not stop early or extend based on loss — fixed compute is the control variable.

If the filtered corpus is smaller than that budget, either reduce the budget for all runs or upsample the filtered corpus. Document the resulting epoch count.

---

## Standard Ablation Runs A–F

| Run | Corpus Description | Key Variable | Purpose |
|-----|--------------------|--------------|---------|
| A | Raw CC extraction (no filter beyond extraction) | Baseline | Establishes noisy ceiling; quantifies what filtering removes |
| B | A + heuristic filter (Gopher + C4) | Heuristic filter | Measures filtering at fixed compute |
| C | B + MinHash near-dedup | Dedup scope and threshold held fixed within the run | Measures dedup effect at fixed compute |
| D | C + classifier-based quality filter | Classifier filter | Measures classifier effect over heuristics and dedup |
| E | D + one synthetic-data share | Synthetic mixture | Measures synthetic effect on target tasks and diversity |
| F | E + mixing-ratio sweep | Domain weights, with synthetic share fixed | Identifies candidate mix for target task profile |

Run B through D without synthetic data. Train each variant from the same model initialization and compute budget; changing only the corpus avoids attributing a continued-training effect to the data. Run F as a ratio sweep with the evaluation suite held fixed.

**Set the mix with a method, not by hand.** Use a principled mixing method to set the prior, then confirm with Run F:

- **DoReMi** (arXiv 2305.10429): group-DRO on a small proxy finds weights minimizing worst-case excess loss; transfer to the full run.
- **Data Mixing Laws** (arXiv 2403.16952): fit a scaling-law surface over ratios from cheap proxy runs and extrapolate the optimum before spending full compute.
- **RegMix** (arXiv 2407.01492): regress performance over many random small-model mixtures; pick the predicted-best ratio. Compute-cheaper than DoReMi.

These methods choose candidate ratios for Run F; the ablation validates them under your exact eval suite. The one-change discipline still holds — vary only the domain weights between Run F variants.

**Reporting**: always report A as the baseline. Report absolute numbers, not only deltas. Include standard deviation across seeds (run each ablation with 3 seeds if compute allows).

---

## Evaluation Suite

Use lm-evaluation-harness (EleutherAI) for all evaluation runs. Fix the evaluation commit hash at the start of the ablation study and do not update it during the study.

**Benchmark selection rule (FineWeb's criteria).** Keep a benchmark only if, at proxy scale, it has low score variance across runs on different random subsets of the same data, improves monotonically (or nearly) during training, and scores above random. Train at least 2 seeds or data subsets per variant.

**Core benchmarks for general ablations**:

| Benchmark | Task Type | Why Include |
|-----------|-----------|-------------|
| HellaSwag | Sentence completion | Sensitive to web-text quality |
| ARC-Easy + ARC-Challenge | Multiple choice reasoning | Sensitive to knowledge density |
| MMLU (0-shot) | Knowledge, multiple choice | Broad knowledge coverage; include only if the proxy clears the 25% chance level in your prompt format |
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

Decontaminate each corpus variant independently before training. Do not assume that decontaminating run A's corpus also covers run E's corpus — synthetic data can introduce new contamination.

**Protocol**:
1. Extract n-grams from all benchmarks you plan to evaluate on (train and test splits), choosing n per benchmark item length (13 in the GPT-3 lineage; Llama 3 scored 8-grams).
2. Hash and store in a Bloom filter or exact hash set.
3. For each document in the corpus variant, extract the same n-grams and check against the hash set.
4. Remove or flag matching documents; log them and the per-benchmark overlap rate.
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

2. **Token budget not held constant** — run E has more tokens because synthetic data boosted the count. Fix: sample to a fixed token target.

3. **Evaluation benchmarks changed mid-study** — a new lm-evaluation-harness version changed the prompt format. Fix: lock the harness commit hash.

4. **Decontamination skipped for synthetic runs** — synthetic data from a web-trained generator may contain benchmark content. Fix: decontaminate every corpus variant independently.

5. **Results reported without error bars** — a 0.5-point improvement on HellaSwag with a 1B model and one seed is within noise. Fix: run 3 seeds; report mean ± std.

6. **Cherry-picked benchmarks** — benchmarks were selected after seeing results to make the finding look stronger. Fix: pre-register the benchmark suite.
