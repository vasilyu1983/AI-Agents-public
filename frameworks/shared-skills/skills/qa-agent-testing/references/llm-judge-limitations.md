# LLM-as-Judge Limitations

Comprehensive documentation of biases and limitations when using LLMs to assess other LLMs.

## Contents

- [Overview](#overview)
- [Known Biases](#known-biases)
- [Fundamental Limitations](#fundamental-limitations)
- [When to Use LLM-as-Judge](#when-to-use-llm-as-judge)
- [Mitigation Strategies](#mitigation-strategies)
- [Checklist](#checklist)
- [References](#references)
- [Related](#related)

## Overview

LLM-as-judge is increasingly used to scale assessments, but carries significant biases that can distort results. This reference documents known issues and mitigations.

## Known Biases

### Position Bias

LLM judges show inconsistent preferences based on response order in pairwise comparisons.

| Finding                     | Impact                         | Source           |
|-----------------------------|--------------------------------|------------------|
| 40% inconsistency rate      | Same responses, different order = different winner | GPT-4 pairwise tests |
| First-position preference   | Response A favored when listed first | Multiple studies |
| Severity varies by model    | Some judges more biased than others | arXiv 2411.15594 |

Mitigation:

```python
# Randomize response order and aggregate
def unbiased_pairwise_assessment(judge, response_a, response_b, n_trials=5):
    wins = {"A": 0, "B": 0, "tie": 0}
    for _ in range(n_trials):
        if random.random() > 0.5:
            result = judge.compare(response_a, response_b)
        else:
            result = judge.compare(response_b, response_a)
            result = flip_result(result)
        wins[result] += 1
    return max(wins, key=wins.get)
```

### Verbosity Bias

Longer responses receive higher scores regardless of quality.

| Finding                     | Impact                         |
|-----------------------------|--------------------------------|
| ~15% score inflation        | For responses 2x longer        |
| Quality != length           | Concise answers penalized      |
| Affects helpfulness ratings | More text seems more helpful   |

Mitigation:

```python
def length_normalized_score(raw_score: float, word_count: int, baseline: int = 200) -> float:
    """Normalize score to account for verbosity bias."""
    length_factor = min(word_count / baseline, 2.0)  # Cap at 2x
    adjustment = (length_factor - 1.0) * 0.15  # 15% bias per 2x length
    return raw_score - adjustment
```

### Self-Preferencing Bias

Models favor outputs from their own family.

| Judge Model   | Prefers          | Bias Strength |
|---------------|------------------|---------------|
| GPT-4         | GPT-4 outputs    | Moderate      |
| Claude        | Claude outputs   | Moderate      |
| Llama         | Llama outputs    | Strong        |

Mitigation:

- Use judge from different model family than assessed model
- Use ensemble of judges from multiple families
- Weight results by known bias factors

### Expert Domain Gap

LLM judges disagree significantly with subject matter experts in specialized domains.

| Domain       | SME Agreement Rate | Gap                |
|--------------|--------------------|--------------------|
| Dietetics    | 68%                | 32% disagreement   |
| Mental health| 64%                | 36% disagreement   |
| Legal        | ~60%               | ~40% disagreement  |
| Medical      | ~55%               | ~45% disagreement  |

Source: [ACM IUI 2025](https://dl.acm.org/doi/10.1145/3708359.3712091)

Mitigation:

- Never use LLM judges alone for expert domain assessment
- Always include SME validation for high-stakes decisions
- Use LLM judges for screening, humans for final decisions

### Multilingual Inconsistency

LLM judges perform inconsistently across languages.

| Finding                     | Impact                         |
|-----------------------------|--------------------------------|
| Judgment inconsistency      | Same quality content judged differently by language |
| English bias                | Higher scores for English responses |
| Low-resource language gap   | Much worse performance for rare languages |

Source: [EMNLP 2025](https://aclanthology.org/2025.findings-emnlp.587.pdf)

## Fundamental Limitations

### Frontier Model Paradox

When the judge is no more accurate than the model being assessed, no debiasing method can decrease required ground truth labels by more than half.

Implication: LLM-as-judge breaks down at the frontier where you're assessing models that may be better than the judge.

Source: [arXiv 2410.13341](https://arxiv.org/abs/2410.13341)

### Adversarial Vulnerabilities

LLM judges are susceptible to manipulation:

| Attack Type        | Description                              |
|--------------------|------------------------------------------|
| Prompt injection   | Hidden instructions in assessed content  |
| Flattery attacks   | Self-praising language inflates scores   |
| Format hacking     | Specific formats that trigger higher ratings |
| Authority claims   | "Experts agree..." boosts perceived quality |

### Reproducibility Issues

API-based judges suffer from opacity:

- Model versions change without notice
- Temperature/sampling variations
- Undocumented system prompt changes
- Rate limiting affects consistency

## When to Use LLM-as-Judge

### Appropriate Use Cases

| Use Case                | Rationale                              |
|-------------------------|----------------------------------------|
| Initial screening       | Filter obvious failures before human review |
| Bulk ranking            | Order large sets for human top-k review |
| Regression detection    | Flag quality drops for investigation   |
| Style/format checks     | Objective criteria LLMs handle well    |
| A/B testing at scale    | Statistical power compensates for noise |

### Inappropriate Use Cases

| Use Case                | Why Problematic                        |
|-------------------------|----------------------------------------|
| Expert domain assessment | 32-45% SME disagreement               |
| High-stakes decisions   | Bias can cause real harm               |
| Frontier model tests    | Judge may be worse than assessed model |
| Single-instance judgment| Need statistical aggregation           |
| Compliance/legal        | Liability requires human accountability |

## Mitigation Strategies

### Strategy 1: Diverse Judge Panel

```python
JUDGES = [
    {"model": "gpt-4", "weight": 0.35},
    {"model": "claude-3", "weight": 0.35},
    {"model": "gemini-pro", "weight": 0.30}
]

def ensemble_judge(response: str, criteria: str) -> float:
    scores = []
    for judge in JUDGES:
        score = get_judgment(judge["model"], response, criteria)
        scores.append(score * judge["weight"])
    return sum(scores)
```

### Strategy 2: Structured Rubrics

Force judges to assess specific criteria rather than holistic judgment:

```python
RUBRIC = {
    "factual_accuracy": "Are all stated facts correct?",
    "relevance": "Does the response address the question?",
    "completeness": "Are all aspects of the question covered?",
    "clarity": "Is the response easy to understand?"
}

def rubric_based_assessment(judge, response, question):
    scores = {}
    for dimension, prompt in RUBRIC.items():
        scores[dimension] = judge.assess(response, question, prompt)
    return scores
```

### Strategy 3: Calibration Sets

Maintain labeled examples to detect judge drift:

```python
CALIBRATION_SET = [
    {"response": "...", "ground_truth_score": 0.9},
    {"response": "...", "ground_truth_score": 0.3},
    # ... 20-50 examples covering score range
]

def calibrated_judge(judge, response):
    # First, validate judge on calibration set
    cal_scores = [judge.score(ex["response"]) for ex in CALIBRATION_SET]
    gt_scores = [ex["ground_truth_score"] for ex in CALIBRATION_SET]

    correlation = pearsonr(cal_scores, gt_scores)
    if correlation < 0.8:
        raise JudgeCalibrationError(f"Judge drift detected: r={correlation}")

    # If calibrated, use judge
    return judge.score(response)
```

### Strategy 4: Human-in-the-Loop

Reserve human review for edge cases:

```python
def hybrid_assessment(response, judge_score):
    if 0.4 < judge_score < 0.7:  # Uncertain zone
        return human_review(response)
    elif judge_score >= 0.7:
        return "pass"
    else:
        return "fail"
```

## Checklist

When using LLM-as-judge:

- [ ] Position bias addressed (randomize order, aggregate trials)
- [ ] Verbosity bias mitigated (length normalization)
- [ ] Judge from different family than assessed model
- [ ] Expert domains validated by SMEs
- [ ] Structured rubric used instead of holistic judgment
- [ ] Calibration set maintained to detect drift
- [ ] Human review for uncertain/high-stakes cases
- [ ] Judge model version logged for reproducibility
- [ ] Adversarial robustness considered

## References

- [Survey on LLM-as-a-Judge (arXiv 2411.15594)](https://arxiv.org/abs/2411.15594)
- [Limits to Scalable Assessment (arXiv 2410.13341)](https://arxiv.org/abs/2410.13341)
- [Expert Domain Limitations (ACM IUI 2025)](https://dl.acm.org/doi/10.1145/3708359.3712091)
- [Multilingual Reliability (EMNLP 2025)](https://aclanthology.org/2025.findings-emnlp.587.pdf)

## Related

- [SKILL.md](../SKILL.md) - Main skill overview
- [scoring-rubric.md](scoring-rubric.md) - Scoring methodology
