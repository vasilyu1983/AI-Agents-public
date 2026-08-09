# RAG Evaluation Guide

## Table of Contents

- [Minimum Evaluation Stack](#minimum-evaluation-stack)
- [Required Dataset Slices](#required-dataset-slices)
- [Recommended Workflow](#recommended-workflow)
- [Golden Eval Pack](#golden-eval-pack)
- [Exact Baseline Before ANN](#exact-baseline-before-ann)
- [Tooling Guidance](#tooling-guidance)
- [LLM-Judge Faithfulness: Worked Example](#llm-judge-faithfulness-worked-example)
- [Verification Checklist](#verification-checklist)
- [March 2026 Note](#march-2026-note)

Evaluate retrieval systems on two planes:

1. **Retrieval quality**: did the system fetch the right evidence?
2. **Answer quality**: did the system use that evidence correctly?

## Minimum Evaluation Stack

### Retrieval Metrics

- recall@k
- MRR
- nDCG
- empty-result rate
- P50 and P95 latency

### Answer Metrics

- correctness
- groundedness / faithfulness
- citation validity
- refusal correctness
- cost per request

## Required Dataset Slices

- easy vs hard
- answerable vs unanswerable
- fresh vs stale-sensitive
- multilingual when relevant
- PDF / table / image-heavy when relevant
- tenant or ACL-sensitive cases when relevant

## Recommended Workflow

1. Freeze the current baseline.
2. Change one retrieval variable at a time.
3. Re-run the same slice set.
4. Record both retrieval and answer regressions.
5. Keep raw results, not just aggregate scores.

## Golden Eval Pack

For production work, maintain a small golden suite in JSONL:

- query or task text
- expected evidence IDs
- graded relevance for partial-credit evidence
- tags for slices such as `policy`, `code`, `pdf`, `acl`, `unanswerable`,
  `lexical_required`, `multilingual`, and `staleness`
- failure label to make regressions explainable

Start from `assets/eval/golden-retrieval-cases.jsonl`. Backend runs should emit
prediction files with `expected_ids` and `retrieved_ids`, then pass through
`scripts/retrieval_eval.py`.

```bash
python3 scripts/retrieval_eval.py assets/eval/golden-retrieval-predictions.example.jsonl --k 5,10
```

The golden suite should stay generic in shared skills. Copy it into a project
and replace evidence IDs with that project's real source anchors.

## Exact Baseline Before ANN

Before tuning HNSW, IVF, managed vector search, or rerankers, prove that exact
search over the same embeddings can retrieve the expected evidence.

```bash
python3 scripts/exact_search_baseline.py docs.jsonl queries.jsonl > predictions.jsonl
python3 scripts/retrieval_eval.py predictions.jsonl --k 5,10
```

If exact search fails, fix source selection, retrieval units, preprocessing, or
embedding model before changing index parameters.

## Tooling Guidance

- Ragas: useful for RAG evaluation and synthetic testset workflows
- DeepEval: useful for debuggable CI-oriented evaluation workflows
- TruLens: useful for instrumentation and production feedback loops
- Langfuse: open-source production tracing and cost tracking; complements RAGAS/DeepEval in production RAG stacks
- Custom scripts: useful for deterministic retrieval metrics and citation-structure checks
- **CCRS** (arXiv 2506.20128): zero-shot LLM-as-judge RAG evaluation framework; no labeled data required; verify against your own corpus before production use
- **Patronus Lynx**: hallucination detection model; useful as a lightweight always-on hallucination gate complementing LLM-judge faithfulness evaluation

Do not make one evaluation framework the whole strategy. Keep deterministic retrieval metrics and versioned test cases outside any single vendor tool.

## LLM-Judge Faithfulness: Worked Example

Faithfulness/groundedness is usually graded by an LLM judge. Make the judge
deterministic and auditable, not a vibe call. A minimal faithfulness judge:

```text
SYSTEM: You grade whether an ANSWER is fully supported by the EVIDENCE.
A claim is supported only if it can be traced to a specific evidence chunk.
Return strict JSON: {"supported": <int 0-N>, "unsupported": <int>,
"verdict": "grounded" | "partial" | "hallucinated", "unsupported_claims": [...]}

USER:
EVIDENCE:
[1] <chunk text>  [2] <chunk text> ...
ANSWER:
<answer text>
```

Run it per (query, answer, evidence) triple, store the raw JSON, and compute a
faithfulness rate over the slice — never accept a single aggregate number
without the per-case verdicts behind it.

### Judge bias and cost (must control)

- **Position bias**: when the judge compares two answers, it favors the first.
  Run both orderings; require agreement.
- **Self-preference**: do not grade faithfulness with the same model that wrote
  the answer; it overrates its own output.
- **Length bias**: longer answers look more "supported." Score per-claim
  support, not overall plausibility.
- **Judge cost**: an LLM judge on every request is expensive. Use deterministic
  citation-support checks (`scripts/check_citation_support.py`) as the cheap
  always-on gate and reserve the LLM judge for a sampled slice or for cases the
  deterministic check flags as ambiguous.

For the full judge-bias taxonomy and calibration mechanics, see the
`ai-evals` skill.

### Testset leakage (named trap)

If synthetic testset queries were generated from the same documents you tuned
chunking/reranking on, your eval scores are inflated. Hold out a slice of source
docs that never touches tuning, and confirm gold queries are not verbatim
substrings of indexed chunks before trusting recall numbers.

## Verification Checklist

- [ ] Expected evidence IDs recorded for test cases
- [ ] Unanswerable cases included
- [ ] Citation-support checks run
- [ ] Retrieval regressions blocked before answer tuning starts
- [ ] Cost and latency tracked with quality metrics

## March 2026 Note

Framework capabilities evolve quickly. Verify current framework features, APIs, and integration guidance from official docs before recommending one as the default.
