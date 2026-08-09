# Eval By Corpus Type

Do not reuse one generic recall gate for every brain. Each corpus has a different failure mode.

## Minimum Eval Set

Start small but real:

- repo/codebase: 50 labeled queries
- docs hub: 50 labeled queries
- compliance/policy: 75 labeled queries, including negative and effective-time cases

Hand-label expected evidence IDs. Synthetic evals are useful for bootstrapping, but they do not replace domain review.

## Corpus Metrics

| Corpus | Primary Metric | Secondary Metrics | Why |
|---|---|---|---|
| Repo/codebase | symbol or path exact-match recall@5 | file recall@10, stale-commit detection, negative-query refusal | Engineers often need the exact file, symbol, migration, or test |
| Docs hub | recall@10 + faithfulness | citation coverage, canonical-source preference, freshness warnings | Paraphrase queries dominate, and duplicate docs cause drift |
| Compliance/policy | citation precision + refusal correctness | effective-time correctness, authority ranking, conflict detection | Wrong or stale citations create legal and audit risk |
| Guide/manual | hit-rate@5 + answer relevancy | section-link accuracy, task completion | Users need the right section and usable steps |
| Support KB | deflection rate + escalation correctness | answer faithfulness, policy compliance, customer effort | Business outcome and escalation safety matter |
| Note vault | recall@k + temporal freshness | personal/source attribution, contradiction handling | Recency and provenance often matter more than polished citation |

V1 implements repo/codebase, docs hub, and compliance/policy. Other rows define future playbook targets.

## JSONL Shape

```jsonl
{"id":"docs-001","query":"Where is the onboarding architecture described?","expected_evidence_ids":["chunk_123"],"metric_focus":"recall@10"}
{"id":"policy-001","query":"What policy version applied on 2026-02-01?","expected_evidence_ids":["policy_aml_v3_4_s4_2"],"as_of":"2026-02-01","metric_focus":"effective_time"}
{"id":"repo-001","query":"Where is the checkout webhook handler?","expected_paths":["src/webhooks/checkout.ts"],"metric_focus":"path_recall@5"}
```

## Release Gates

Before changing chunking, backend, embedding model, hybrid SQL, filters, or reranker:

- run retrieval evals
- compare to previous corpus version
- inspect failures manually
- update the manifest if behavior changes

Suggested starting gates:

- repo/codebase: path recall@5 >= 0.85 for labeled exact-location queries
- docs hub: recall@10 >= 0.85 and citation coverage >= 0.9
- compliance/policy: citation precision >= 0.95, refusal correctness >= 0.9, effective-time correctness >= 0.95

Adjust gates based on corpus risk and user impact.

