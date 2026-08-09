# Multi-Metric LLM Evaluation Template

*Purpose: Scaffold for evaluating LLM, RAG, or agentic systems on all critical dimensions (accuracy, faithfulness, latency, safety, cost, format, etc)—usable for pre-prod validation, regression, or ongoing LLMOps.*

---

## When to Use

Use this template when:

- Validating any new model, RAG pipeline, prompt, or agent release before production
- Monitoring ongoing system quality (hallucination, latency, cost, safety)
- Comparing different models, prompts, or RAG configs (A/B testing)
- Running regression after code/prompt/data/model changes

---

## Structure

This template has 4 main sections:

1. **Metric Selection** – define all required metrics for system/goal
2. **Test Suite** – build gold set (QA pairs, edge/adversarial cases, format/abuse checks)
3. **Evaluation Run** – execute automated and/or human-in-the-loop evals
4. **Results & Quality Gates** – compare to thresholds, block release if any fail

---

# TEMPLATE STARTS HERE

## 1. Metric Selection

| Metric         | Target/Threshold  | Applies to         |
|----------------|------------------|--------------------|
| Accuracy       | >95%              | All LLM, RAG       |
| Faithfulness   | >97%              | RAG, grounded LLM  |
| Hallucination  | <3%               | All outputs        |
| Latency        | <2s p95           | Production         |
| Cost           | Within budget     | Production         |
| Format         | 100% compliance   | Structured output  |
| Safety/Abuse   | 0 critical        | All prod outputs   |

Add others as needed: bias, toxicity, recall, F1, etc.

## 2. Test Suite

- Gold Q/A pairs with known correct answers
- Context-grounded test cases for faithfulness/hallucination
- Adversarial/edge cases (prompt injection, ambiguous queries)
- Format checks (valid JSON, table, etc)
- Abuse/toxicity samples (to trigger filters)
- Regression set from previous release

## 3. Evaluation Run

- Automated scoring:
  - Compute accuracy, format, latency, cost from test batch
  - Use faithfulness/hallucination checker (rule-based or LLM-powered)
- Human review:
  - Sample N outputs for subjective criteria (helpfulness, style, unclear context)
  - Mark pass/fail or rate by metric
- Log all results, compare to previous/baseline

## 4. Results & Quality Gates

- Pass if **ALL** critical metrics meet threshold (see table above)
- If any fail: block release, trigger bugfix/patch/rollback
- Store evaluation logs and metrics for audit and ongoing monitoring

---

# COMPLETE EXAMPLE

**Eval Script (Python-like pseudocode):**

```python
metrics = {
  "accuracy": [],
  "faithfulness": [],
  "latency": [],
  "cost": [],
  "format": [],
  "safety": []
}
for test in test_suite:
    result = run_llm(test.input)
    metrics["accuracy"].append(score_accuracy(result, test.gold))
    metrics["faithfulness"].append(score_faithful(result, test.context))
    metrics["latency"].append(result.latency)
    metrics["cost"].append(result.cost)
    metrics["format"].append(validate_format(result.output))
    metrics["safety"].append(scan_for_abuse(result.output))
# Compute means, compare to thresholds, print/pass/fail summary
```

---

## Quality Checklist

Before finalizing:

- [ ] All metrics relevant to your system tracked and validated
- [ ] Test suite covers gold, edge, format, and safety cases
- [ ] Automated AND human-in-the-loop reviews where needed
- [ ] Results compared to clear thresholds (block on fail)
- [ ] All eval runs, metrics, and test cases versioned for audit

---

*For live monitoring and incident playbooks, see [references/eval-patterns.md]. For deployment/rollback, see [deployment/].*
