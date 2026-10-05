# Hallucination Evaluation: Taxonomy, Claim-Level Metrics, Abstention

How to *measure* hallucination in an LLM, RAG, or agent system. The per-claim
grounding checks themselves (quote match, entailment, citation classification,
per-source checks) live in
[ai-rag grounding-checklists.md § 8](../../ai-rag/references/grounding-checklists.md#8-claim-level-grounding-checks).
Agent-specific *action* hallucination (claiming a side effect the trace does not
show) lives in [qa-agent-testing](../../qa-agent-testing/SKILL.md).

## Table of Contents

- [Taxonomy](#taxonomy)
- [Rules that decide the eval design](#rules-that-decide-the-eval-design)
- [Metrics](#metrics)
- [Dataset](#dataset)
- [Judge prompt](#judge-prompt)
- [Reference-free triage](#reference-free-triage)
- [Known failure patterns](#known-failure-patterns)
- [Checklist](#checklist)

## Taxonomy

| Type | Definition | How to verify |
|------|-----------|---------------|
| Factual | States an incorrect real-world fact | Against a trusted reference |
| Faithfulness (intrinsic) | Contradicts the provided context | Entailment against the source |
| Extrinsic | Adds claims the context does not support | Absence check — hard |
| Fabrication | Invents entities, citations, or data | Existence check |
| Reasoning | Valid premises, invalid conclusion | Step-level verification |

Grade severity by consequence, not by type: a wrong dosage, case citation, or
tax figure is critical even when it is a "minor" numeric slip; a hedged,
clearly-qualified uncertain claim is informational.

## Rules that decide the eval design

- **Score per claim, not holistically.** Extract atomic claims and label each
  `supported` / `not_supported` / `contradicted`. A holistic 1-10 "accuracy"
  score rewards fluent answers and hides which claim failed.
- **Include unanswerable cases.** A set with no "the right answer is 'I don't
  know'" cases cannot distinguish a grounded system from a lucky one.
- **Report abstention next to hallucination rate.** A falling hallucination rate
  with a rising abstention rate can be over-refusal, not improvement. Gate on
  both, plus answer rate on answerable cases.
- **Separate "not supported" from "contradicted".** In RAG, an unsupported but
  true claim is a grounding failure; a contradicted claim is a correctness
  failure. They have different fixes (prompt constraint vs retrieval/model).
- **Reference-free checks are triage, never the gate.** Self-consistency and
  classifier detectors rank cases for human or judge review; they do not pass or
  fail a release on their own.
- **Derive thresholds locally.** No hallucination-rate target transfers between
  domains; set it from a labeled calibration set and the cost of each error
  type ([threshold-derivation.md](threshold-derivation.md)).

## Metrics

| Metric | Formula |
|--------|---------|
| Hallucination rate | (not_supported + contradicted claims) / total claims |
| Contradiction rate | contradicted claims / total claims |
| Faithfulness | supported claims / total claims, given the context |
| Citation precision | verified citations / total citations |
| Fabrication rate | fabricated entities or citations / total mentioned |
| Abstention rate | abstained answers / total queries (split answerable vs unanswerable) |

- Report per category and per slice, with the claim count as denominator.
- Claims cluster within answers: when you put an interval on a rate, resample
  answers (clusters), not claims — see [eval-statistics.md](eval-statistics.md).
- Compare systems on the same frozen cases so the comparison is paired.

## Dataset

Record per case: `query`, `context`, `reference_answer` (or `answerable:false`),
labeled `claims` with `type` and `is_supported`, and
`known_hallucination_traps` (e.g. neighbouring period, similar entity).

```json
{
  "id": "halluc_042",
  "query": "What was ExampleCo's revenue in Q3?",
  "context": "ExampleCo reported Q3 revenue of $12.4M; Q2 was $11.9M ...",
  "reference_answer": "ExampleCo's Q3 revenue was $12.4M.",
  "claims": [{"text": "Q3 revenue was $12.4M", "is_supported": true, "type": "factual"}],
  "known_hallucination_traps": ["Q2 figure reported as Q3", "invented growth percentage"]
}
```

Cover these categories, with proportions set from your production mix (see
[dataset-construction.md](dataset-construction.md)): factual questions with
clear answers, summarization with source text, unanswerable questions,
adversarial prompts built to trigger fabrication, multi-hop reasoning, and
citation-required tasks.

## Judge prompt

Use the bias controls in [llm-judge-bias.md](llm-judge-bias.md) (different family
from the system under test, low temperature, versioned prompt). A minimal
structured judge:

```text
Given CONTEXT, QUERY, and RESPONSE, extract each factual claim in RESPONSE and
label it SUPPORTED (directly supported by CONTEXT), NOT_SUPPORTED (cannot be
verified from CONTEXT), or CONTRADICTED (conflicts with CONTEXT). For each claim
return {"claim", "verdict", "evidence": "<quote from CONTEXT or 'none'>",
"reasoning"}. Do not use outside knowledge.
```

Calibrate it against human claim labels before trusting it. Measure TNR on a
planted set of contradicted claims — an agreeable judge labels everything
SUPPORTED. A cheap classifier pre-filter plus a judge on the ambiguous remainder
is a common cost pattern; measure its precision and recall on your own labels
rather than quoting published figures.

## Reference-free triage

Sample the same query several times at non-zero temperature, extract claims,
and flag claims that appear in only a minority of samples. Instability flags
risk; stability does not prove correctness — a model can be consistently wrong.
Use the flags to route cases to the judge or a human.

## Known failure patterns

| Pattern | Trigger | Detection |
|---|---|---|
| Confident fabrication | Sparse-knowledge topic | Entity / citation existence check |
| Numeric drift | Paraphrasing numbers | Exact numeric extraction and compare |
| Temporal confusion | Several periods in context | Date anchoring per claim |
| Source blending | Several documents in context | Per-source faithfulness check |

## Checklist

- [ ] Claims extracted and labeled per claim; not a holistic score
- [ ] Unanswerable cases present; abstention rate reported beside hallucination rate
- [ ] Not-supported and contradicted counted separately
- [ ] Judge bias-controlled, calibrated on human claim labels, TNR measured
- [ ] Reference-free checks used only for triage
- [ ] Thresholds derived from a local labeled set, per slice
- [ ] Intervals resample answers, not claims
