# Evaluation Dataset Design

Designing representative, unbiased evaluation datasets for systematic agent testing with statistical rigor and long-term maintainability.

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

### Computing Agreement

```python
from sklearn.metrics import cohen_kappa_score
import numpy as np

def compute_agreement(
    annotations_a: list[int],
    annotations_b: list[int],
) -> dict:
    """Compute inter-annotator agreement metrics."""
    kappa = cohen_kappa_score(annotations_a, annotations_b)
    exact_agreement = sum(
        a == b for a, b in zip(annotations_a, annotations_b)
    ) / len(annotations_a)

    # Adjacent agreement (within 1 point on 5-point scale)
    adjacent = sum(
        abs(a - b) <= 1 for a, b in zip(annotations_a, annotations_b)
    ) / len(annotations_a)

    return {
        "cohens_kappa": round(kappa, 3),
        "exact_agreement": round(exact_agreement, 3),
        "adjacent_agreement": round(adjacent, 3),
    }
```

### Agreement Thresholds

| Metric | Poor | Fair | Good | Excellent |
|--------|------|------|------|-----------|
| Cohen's kappa | < 0.20 | 0.20 - 0.40 | 0.40 - 0.60 | > 0.60 |
| Exact agreement | < 0.50 | 0.50 - 0.70 | 0.70 - 0.85 | > 0.85 |
| Adjacent agreement | < 0.70 | 0.70 - 0.85 | 0.85 - 0.95 | > 0.95 |

**Action:** If kappa < 0.40, revise annotation guidelines before proceeding.

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

### Deduplication Pipeline

```python
import hashlib

def check_contamination(
    eval_dataset: list[dict],
    training_data: list[dict],
    threshold: float = 0.85,
) -> list[dict]:
    """Check for contamination between eval and training sets."""
    training_hashes = set()
    for item in training_data:
        text = normalize_text(item["query"] + item.get("context", ""))
        training_hashes.add(hashlib.sha256(text.encode()).hexdigest())

    contaminated = []
    for item in eval_dataset:
        text = normalize_text(item["query"] + item.get("context", ""))
        item_hash = hashlib.sha256(text.encode()).hexdigest()

        if item_hash in training_hashes:
            contaminated.append({
                "id": item["id"],
                "type": "exact_match",
            })
            continue

        # Fuzzy matching for near-duplicates
        for train_item in training_data:
            similarity = compute_similarity(item["query"], train_item["query"])
            if similarity > threshold:
                contaminated.append({
                    "id": item["id"],
                    "type": "near_duplicate",
                    "similarity": similarity,
                })
                break

    return contaminated
```

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
| Size | 100-500 carefully curated examples | 1000+ auto-refreshed examples |
| Maintenance | Manual curation, versioned | Automated sampling pipeline |
| Freshness | Updated quarterly | Updated weekly/daily |
| Contamination risk | Higher (static, may leak) | Lower (rotating samples) |
| Statistical stability | High (same examples each run) | Lower (variance between runs) |
| Best for | Release gating, A/B comparison | Continuous monitoring |

**Recommendation:** Use both. Golden set for release gates. Dynamic set for production monitoring.

---

## Dataset Size Planning

### Statistical Power Calculation

```python
import math

def required_sample_size(
    baseline_accuracy: float,
    minimum_detectable_effect: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """
    Calculate minimum dataset size to detect a given effect size.

    Args:
        baseline_accuracy: Current expected accuracy (e.g., 0.85)
        minimum_detectable_effect: Smallest difference to detect (e.g., 0.05)
        alpha: Significance level (default 0.05)
        power: Statistical power (default 0.80)
    """
    from scipy import stats

    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    p1 = baseline_accuracy
    p2 = baseline_accuracy - minimum_detectable_effect
    p_avg = (p1 + p2) / 2

    n = ((z_alpha * math.sqrt(2 * p_avg * (1 - p_avg)) +
          z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) /
         minimum_detectable_effect) ** 2

    return math.ceil(n)

# Example: detect 5% accuracy drop from 85% baseline
n = required_sample_size(0.85, 0.05)
# n ~ 356 samples needed per condition
```

### Size Guidelines

| Use Case | Minimum Size | Recommended Size |
|----------|-------------|-----------------|
| Quick smoke test | 25-50 | 50-100 |
| Feature evaluation | 100-200 | 200-500 |
| Release gate (golden set) | 200-500 | 500-1000 |
| Statistical comparison (A/B) | 350+ per group | 500+ per group |
| Domain-specific evaluation | 50+ per domain | 100+ per domain |

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
- [ ] Inter-annotator agreement above threshold (kappa > 0.40)
- [ ] Contamination check against training data completed
- [ ] Bias audit completed across all dimensions
- [ ] Dataset versioned with changelog
- [ ] Sample size sufficient for intended statistical analysis
- [ ] Synthetic examples (if any) quality-checked and flagged
- [ ] Maintenance schedule established
- [ ] Access controls limit dataset exposure to prevent leakage

---

## Related Resources

- **[hallucination-detection.md](hallucination-detection.md)** - Hallucination eval using datasets
- **[scoring-rubric.md](scoring-rubric.md)** - Rubrics for annotation
- **[llm-judge-limitations.md](llm-judge-limitations.md)** - Automated judging caveats
- **[test-case-design.md](test-case-design.md)** - Individual test case design
- **[SKILL.md](../SKILL.md)** - QA Agent Testing skill overview
