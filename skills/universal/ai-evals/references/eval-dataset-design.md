# Evaluation Dataset Design

Designing representative, unbiased evaluation datasets with statistical rigor and long-term maintainability.

This file owns dataset *composition*: task distribution, difficulty, sampling, annotation, versioning, contamination, bias audits, and golden vs dynamic sets. Its companion [dataset-construction.md](dataset-construction.md) owns sourcing, ideal-answer authoring, and the run→compare→tune loop. Sample sizing lives in [eval-statistics.md](eval-statistics.md#paired-binary-sizing-mcnemar) and agreement (kappa) bands in [threshold-derivation.md](threshold-derivation.md#measure-judge-human-agreement). For agent-harness specifics (tool-requiring task mix, real-failure regression packs), see [qa-agent-testing agent-eval-datasets.md](../../qa-agent-testing/references/agent-eval-datasets.md).

---

## Contents

- [Dataset Composition Principles](#dataset-composition-principles)
- [Task Distribution Planning](#task-distribution-planning)
- [Difficulty Calibration](#difficulty-calibration)
- [Sampling Strategies](#sampling-strategies)
- [Annotation Guidelines](#annotation-guidelines)
- [Inter-Annotator Agreement](#inter-annotator-agreement)
- [Dataset Versioning and Maintenance](#dataset-versioning-and-maintenance)
- [Contamination Prevention](#contamination-prevention)
- [Evaluation Overfitting (Goodhart's Law)](#evaluation-overfitting-goodharts-law)
- [Bias Detection in Datasets](#bias-detection-in-datasets)
- [Golden Sets vs Dynamic Sets](#golden-sets-vs-dynamic-sets)
- [Dataset Size Planning](#dataset-size-planning)
- [Synthetic Data Augmentation](#synthetic-data-augmentation)
- [Dataset Quality Checklist](#dataset-quality-checklist)
- [Related Resources](#related-resources)

---

## Dataset Composition Principles

A representative evaluation dataset must reflect real usage while including adversarial cases that stress-test boundaries.

| Principle | Description | Anti-Pattern |
|-----------|-------------|-------------|
| Coverage | All agent capabilities have test cases | Testing only the happy path |
| Proportionality | Task mix reflects production distribution | Over-indexing on easy queries |
| Edge inclusion | Boundary cases explicitly represented | Only testing "normal" inputs |
| Temporal validity | Data reflects current real-world state | Stale facts or outdated formats |
| Domain balance | All supported domains represented | Bias toward one content type |
| Difficulty gradient | Easy, medium, hard, adversarial cases | All examples at one difficulty |

### Dataset Record Schema

```json
{
  "id": "eval_0042",
  "query": "What are the side effects of ibuprofen?",
  "context": "[Retrieved document text if RAG...]",
  "reference_answer": "Common side effects include...",
  "metadata": {
    "domain": "medical",
    "difficulty": "medium",
    "task_type": "factual_qa",
    "requires_tools": ["knowledge_base"],
    "edge_case": false,
    "created_date": "2025-01-15",
    "annotator": "annotator_02",
    "source": "production_sample_2025q1"
  },
  "evaluation_criteria": {
    "factual_accuracy": true,
    "citation_required": true,
    "hedging_expected": true,
    "acceptable_answers": ["list of valid answer variants"]
  }
}
```

---

## Task Distribution Planning

### Step 1: Analyze Production Traffic

```python
import json
from collections import Counter

def analyze_production_distribution(logs_path: str) -> dict:
    """Analyze task type distribution from production logs."""
    task_types = Counter()
    domains = Counter()
    difficulties = Counter()

    with open(logs_path) as f:
        for line in f:
            entry = json.loads(line)
            task_types[entry["task_type"]] += 1
            domains[entry["domain"]] += 1
            difficulties[entry["estimated_difficulty"]] += 1

    total = sum(task_types.values())
    return {
        "task_distribution": {k: round(v / total, 3) for k, v in task_types.most_common()},
        "domain_distribution": {k: round(v / total, 3) for k, v in domains.most_common()},
        "difficulty_distribution": {k: round(v / total, 3) for k, v in difficulties.most_common()},
        "total_samples": total,
    }
```

### Step 2: Define Target Distribution

| Task Type | Production % | Eval Dataset % | Rationale |
|-----------|-------------|----------------|-----------|
| Factual QA | 40% | 30% | Well-covered, reduce slightly |
| Summarization | 20% | 20% | Keep proportional |
| Multi-step reasoning | 10% | 15% | Under-tested, increase |
| Tool usage | 15% | 15% | Keep proportional |
| Edge cases / adversarial | 2% | 15% | Critically under-represented |
| Refusal scenarios | 3% | 5% | Important safety coverage |
| Ambiguous queries | 10% | -- | Folded into difficulty levels |

**Rule of thumb:** Over-sample rare but high-impact categories. Under-sample commodity tasks.

---

## Difficulty Calibration

### Difficulty Levels

```text
LEVEL 1 - Easy
  - Single-hop factual lookup
  - Clear, unambiguous query
  - Answer directly in provided context
  - Example: "What is the capital of France?"

LEVEL 2 - Medium
  - Requires synthesis across 2-3 sources
  - Some ambiguity in query
  - Answer requires inference from context
  - Example: "Compare the revenue trends of Company A and Company B."

LEVEL 3 - Hard
  - Multi-hop reasoning (3+ steps)
  - Requires tool usage or computation
  - Partial information in context (agent must acknowledge gaps)
  - Example: "Based on the financial data, which division should be divested?"

LEVEL 4 - Adversarial
  - Designed to trigger known failure modes
  - Contains misleading context or trick questions
  - Tests refusal behavior on unanswerable queries
  - Example: "Using the 2024 data (context only has 2023), project growth."
```

### Calibration Procedure

```python
def calibrate_difficulty(
    dataset: list[dict],
    agent_client,
    n_runs: int = 3,
) -> list[dict]:
    """Empirically calibrate difficulty by running against the agent."""
    for item in dataset:
        scores = []
        for _ in range(n_runs):
            response = agent_client.send_message(item["query"])
            score = evaluate_response(response.text, item["reference_answer"])
            scores.append(score)

        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)

        # Assign empirical difficulty
        if avg_score > 0.9 and variance < 0.01:
            item["empirical_difficulty"] = "easy"
        elif avg_score > 0.7:
            item["empirical_difficulty"] = "medium"
        elif avg_score > 0.4:
            item["empirical_difficulty"] = "hard"
        else:
            item["empirical_difficulty"] = "adversarial"

        item["pass_rate"] = avg_score
        item["score_variance"] = variance

    return dataset
```

---

## Sampling Strategies

### Stratified Sampling from Production

```python
import random
from collections import defaultdict

def stratified_sample(
    production_logs: list[dict],
    target_size: int,
    strata_key: str = "task_type",
    min_per_stratum: int = 10,
) -> list[dict]:
    """Sample from production data maintaining distribution."""
    strata = defaultdict(list)
    for entry in production_logs:
        strata[entry[strata_key]].append(entry)

    total = len(production_logs)
    sampled = []

    for stratum, items in strata.items():
        proportion = len(items) / total
        n_samples = max(min_per_stratum, int(target_size * proportion))
        n_samples = min(n_samples, len(items))
        sampled.extend(random.sample(items, n_samples))

    return sampled
```

### Sampling Strategy Decision Table

| Strategy | When to Use | Pros | Cons |
|----------|------------|------|------|
| Stratified random | General eval sets | Proportional coverage | May miss rare cases |
| Oversampled minorities | Safety-critical domains | Better edge coverage | Distribution skew |
| Cluster sampling | Multi-domain agents | Efficient for large domains | Inter-cluster variance |
| Adversarial targeted | Red-team testing | Finds weaknesses | Not representative |
| Temporal sampling | Drift detection | Catches temporal shifts | Requires timestamps |

---

## Annotation Guidelines

### Annotator Instructions Template

```markdown
## Task: Evaluate Agent Response Quality

For each (query, context, response) triple, assess:

1. **Factual Accuracy** (1-5): Are all facts in the response correct?
   - 5: All facts verified correct
   - 3: Minor inaccuracies that don't change meaning
   - 1: Major factual errors

2. **Completeness** (1-5): Does the response fully answer the query?
   - 5: Comprehensive answer
   - 3: Partial answer, missing some aspects
   - 1: Does not address the query

3. **Faithfulness** (1-5): Is the response faithful to the provided context?
   - 5: Every claim traceable to context
   - 3: Some unsupported but plausible additions
   - 1: Contradicts or fabricates relative to context

4. **Appropriate Refusal** (yes/no/na): If the query should be refused,
   did the agent refuse appropriately?

## Rules
- Annotate based ONLY on the provided context, not your personal knowledge
- Flag ambiguous cases with [AMBIGUOUS] tag for review
- Minimum time per annotation: 2 minutes (to prevent rushed labels)
```

### Annotation Quality Controls

- [ ] Annotators complete a calibration set before starting (10 pre-labeled examples)
- [ ] Each item annotated by at least 2 independent annotators
- [ ] Disagreements resolved by a third senior annotator
- [ ] Annotator accuracy tracked against gold standard
- [ ] Regular calibration sessions (weekly for active annotation)

---

## Inter-Annotator Agreement

Compute Cohen's kappa for two raters (Fleiss' kappa or Krippendorff's alpha for
more) with a standard stats library, alongside raw exact agreement. What a
kappa value permits — diagnostic, non-blocking signal, or blocking gate — is
decided by the single set of bands in
[threshold-derivation.md](threshold-derivation.md#measure-judge-human-agreement);
do not use generic "fair/good" labels to decide gate use. If agreement is too low
to gate on, revise the annotation guidelines before labeling more.

---

## Dataset Versioning and Maintenance

### Version Control Strategy

```text
eval_datasets/
  v1.0.0/
    dataset.jsonl
    metadata.json          # Schema, annotator info, creation date
    annotation_guide.md
    CHANGELOG.md
  v1.1.0/
    dataset.jsonl
    metadata.json
    diff_from_v1.0.0.json  # What changed and why
    CHANGELOG.md
```

### Semantic Versioning for Datasets

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Add examples (same schema) | Patch (1.0.x) | Add 20 new edge cases |
| Update labels/references | Minor (1.x.0) | Fix incorrect reference answers |
| Schema change or domain shift | Major (x.0.0) | Add new evaluation criteria |

### Maintenance Schedule

- [ ] Monthly: Review flagged ambiguous cases
- [ ] Quarterly: Check for stale facts (temporal decay)
- [ ] Per release: Add test cases for new capabilities
- [ ] Annually: Full dataset audit and revalidation

---

## Contamination Prevention

### Contamination Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| Training data overlap | Eval examples appear in fine-tuning data | Hash-based deduplication |
| Prompt leakage | Eval prompts used during development | Separate eval-only repo |
| Human memory | Developers memorize eval cases | Rotating eval subsets |
| LLM-generated eval | Model evaluates its own training data | Use held-out human-written data |

### Deduplication

- Hash a normalized form (case, whitespace, punctuation) of each eval query plus
  context and reject exact matches against any training, fine-tuning, or
  prompt-example data.
- Add a near-duplicate check with the similarity measure your stack already has;
  set its threshold by inspecting flagged pairs, not by a copied constant.
- Record the check and its result with the dataset version.

---

## Evaluation Overfitting (Goodhart's Law)

A static eval suite is a target, and any target that stays fixed long enough while people optimize against it stops measuring the thing it was built to measure. This is distinct from contamination above (where eval content leaks into training data) — overfitting can happen even with a perfectly clean, uncontaminated eval set, purely through repeated iteration against it.

Concretely, this happens in three ways:

- **Prompt-tuning to the suite.** A team iterates a prompt against the same 20-50 regression cases for months. The prompt gets very good at those specific cases and stops improving (or quietly regresses) on the production distribution the cases were meant to sample.
- **Judge-prompt tuning to the suite.** The grader prompt gets adjusted whenever it disagrees with a human on a specific case, without checking whether the adjustment generalizes. After enough rounds, the judge is calibrated to agree with your team's past judgment calls on your past cases, not to measure quality independently.
- **Benchmark-chasing.** Teams sometimes discover that a specific benchmark's task distribution has quirks (certain phrasing patterns, certain tool-call shapes) that can be gamed without improving the underlying capability. See [qa-agent-testing agentic-benchmarks.md](../../qa-agent-testing/references/agentic-benchmarks.md) for the published, ABC-documented version of this at the public-benchmark level (SWE-bench Verified, TAU-bench).

**Mitigations, roughly in order of leverage:**

1. Keep a held-out slice of the golden set that is never used for prompt iteration — only for periodic release-gate checks. If performance on the held-out slice diverges from the iteration slice, you are overfitting.
2. Refresh the dynamic/production-sampled set on a cadence (see Golden Sets vs Dynamic Sets below) so the target keeps moving with real usage.
3. Periodically re-derive difficulty and task-distribution assumptions from fresh production logs rather than assuming last quarter's distribution still holds.
4. Treat a suite-level score that has been stable for a long time with mild suspicion, not just satisfaction — verify it against a fresh sample before treating "no regressions" as "no problems."

---

## Bias Detection in Datasets

### Bias Audit Dimensions

- [ ] **Demographic balance**: Names, locations, cultural references not skewed
- [ ] **Topic coverage**: No domain over-represented beyond intended distribution
- [ ] **Difficulty balance**: Not clustered at one difficulty level
- [ ] **Answer length bias**: Reference answers vary in expected length
- [ ] **Language complexity**: Queries use varied vocabulary and syntax
- [ ] **Temporal bias**: Not all examples from one time period

### Automated Bias Checks

```python
def audit_dataset_bias(dataset: list[dict]) -> dict:
    """Run automated bias checks on dataset."""
    report = {}

    # Domain distribution
    domains = Counter(item["metadata"]["domain"] for item in dataset)
    report["domain_distribution"] = dict(domains)
    report["domain_entropy"] = compute_entropy(domains)

    # Difficulty distribution
    difficulties = Counter(item["metadata"]["difficulty"] for item in dataset)
    report["difficulty_distribution"] = dict(difficulties)

    # Answer length distribution
    lengths = [len(item["reference_answer"].split()) for item in dataset]
    report["answer_length"] = {
        "mean": round(sum(lengths) / len(lengths), 1),
        "min": min(lengths),
        "max": max(lengths),
        "std": round(np.std(lengths), 1),
    }

    # Query lexical diversity
    all_words = [w for item in dataset for w in item["query"].lower().split()]
    report["lexical_diversity"] = len(set(all_words)) / len(all_words)

    return report
```

---

## Golden Sets vs Dynamic Sets

| Aspect | Golden Set | Dynamic Set |
|--------|-----------|-------------|
| Purpose | Stable regression baseline | Detect drift and new failures |
| Size | Sized by the claim (see Dataset Size Planning) | Large enough to show drift per slice |
| Maintenance | Manual curation, versioned | Automated sampling pipeline |
| Freshness | Updated quarterly | Updated weekly/daily |
| Contamination risk | Higher (static, may leak) | Lower (rotating samples) |
| Statistical stability | High (same examples each run) | Lower (variance between runs) |
| Best for | Release gating, A/B comparison | Continuous monitoring |

**Recommendation:** Use both. Golden set for release gates. Dynamic set for production monitoring.

---

## Dataset Size Planning

Size to the claim you intend to make, and keep two set names distinct:

- **Smoke/regression pack** — about 15-25 cases from real failures. It answers
  "did anything obviously break"; it cannot detect a small effect.
- **Statistical comparison set** — sized by a power calculation for the
  smallest effect you must detect. Agent A/B runs on one suite are *paired*:
  size them with the McNemar formula in
  [eval-statistics.md](eval-statistics.md#paired-binary-sizing-mcnemar)
  (e.g. 312 pairs at 10% discordance for a 5-point difference), not with an
  unpaired two-proportion formula (906 per arm for 85% → 80%), which only fits
  arms run on different cases.
- Power is per slice: a gate on each slice needs each slice sized.

---

## Synthetic Data Augmentation

### Augmentation Strategies

```python
def augment_with_paraphrases(
    dataset: list[dict],
    paraphrase_model,
    n_variants: int = 3,
) -> list[dict]:
    """Generate paraphrased variants of existing eval examples."""
    augmented = []
    for item in dataset:
        augmented.append(item)  # Keep original

        for i in range(n_variants):
            variant = item.copy()
            variant["id"] = f"{item['id']}_para_{i}"
            variant["query"] = paraphrase_model.paraphrase(item["query"])
            variant["metadata"] = {
                **item["metadata"],
                "is_synthetic": True,
                "source_id": item["id"],
                "augmentation": "paraphrase",
            }
            augmented.append(variant)

    return augmented
```

### Synthetic Data Quality Gates

- [ ] Synthetic examples reviewed by human annotator (sample 10%)
- [ ] Label preservation verified (paraphrase does not change expected answer)
- [ ] Synthetic proportion capped at 40% of total dataset
- [ ] Synthetic examples flagged in metadata for separate analysis
- [ ] Deduplication run post-augmentation

---

## Dataset Quality Checklist

- [ ] Schema documented and validated (JSON Schema or Pydantic)
- [ ] Task distribution matches production or intended coverage
- [ ] Difficulty levels empirically calibrated
- [ ] All examples annotated by 2+ annotators
- [ ] Inter-annotator agreement inside the ai-evals kappa band required for the intended use
- [ ] Contamination check against training data completed
- [ ] Bias audit completed across all dimensions
- [ ] Dataset versioned with changelog
- [ ] Sample size sufficient for intended statistical analysis
- [ ] Synthetic examples (if any) quality-checked and flagged
- [ ] Maintenance schedule established
- [ ] Access controls limit dataset exposure to prevent leakage

---

## Related Resources

- **[dataset-construction.md](dataset-construction.md)** - Sourcing, ideal answers, run→compare→tune loop
- **[eval-statistics.md](eval-statistics.md)** - Paired sizing, CIs, significance
- **[threshold-derivation.md](threshold-derivation.md)** - Kappa bands and gate design
- **[hallucination-eval.md](hallucination-eval.md)** - Hallucination eval using datasets
- **[qa-agent-testing agent-eval-datasets.md](../../qa-agent-testing/references/agent-eval-datasets.md)** - Agent-harness dataset specifics
- **[SKILL.md](../SKILL.md)** - AI Evals skill overview
