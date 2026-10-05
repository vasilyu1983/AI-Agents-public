# Evaluating Retrieval, KB, and Memory Systems

Load when the system under test retrieves from a corpus, knowledge base, or
agent memory, or is a multi-stage pipeline. Generic set construction stays in
[dataset-construction.md](dataset-construction.md); this file adds what changes
when the builder also wrote the eval. Memory-specific case templates live in
[ai-context-layer](../../ai-context-layer/references/memory-responsibilities-audit.md).

## Contents

- [1. Independent held-out set](#1-independent-held-out-set)
- [2. Per-stage evaluation for multi-stage pipelines](#2-per-stage-evaluation-for-multi-stage-pipelines)
- [3. Regression gate on change](#3-regression-gate-on-change)
- [4. State-maintenance scoring](#4-state-maintenance-scoring)
- [5. Cross-tenant leakage slice](#5-cross-tenant-leakage-slice)
- [6. Learned and procedural memory](#6-learned-and-procedural-memory)
- [7. Reading vendor memory benchmarks](#7-reading-vendor-memory-benchmarks)

## 1. Independent held-out set

Builder-written evals inflate. In one in-house policy-KB build the builders' own
eval reported a much higher answer rate than an independent held-out set
(observed once, not a benchmark; the gap is the lesson). The builder writes questions in the corpus's vocabulary, from documents
they already know are indexed, and tunes until those pass.

- **Author**: someone who did not build or tune the system, from real user
  questions where they exist (search logs, support tickets, chat history). If
  only the builder is available, write questions from user-need prompts before
  reading the corpus, and label the set `builder-written`; never report it as held-out.
- **Freeze**: version the set, hash it, and never tune retrieval, prompts,
  stopwords, or thresholds against it. A failure found here becomes a new case
  in the tuning set, not an edit to the frozen one. Refresh with a new frozen
  set when it has been seen too often (see eval-dataset-design overfitting).

### Slices and floors

| Slice | Catches | Floor |
|-------|---------|-------|
| keyword / exact identifier | lexical regressions | per-slice, from a labeled calibration set |
| paraphrase | lexical-only retrieval | per-slice |
| acronym / alias | glossary and expansion gaps | per-slice |
| multilingual | embedding/language coverage | per-slice |
| fact / table | extraction losses (tables, images) | per-slice |
| unanswerable | abstain gate | per-slice |
| hard negatives (look-alike docs, other scope or entity, superseded versions) | confident-wrong answers, scope leaks | 100%: any miss blocks |

Derive each non-hard-negative floor per [threshold-derivation.md](threshold-derivation.md);
do not copy targets.

### Report

- Answer rate, abstain rate, and **confident-wrong rate** (answered, cited, and
  wrong) side by side. Confident-wrong is the first-class safety metric: raising
  the answer rate by lowering the abstain gate trades it for exactly that.
- Small slices (tens of cases) get Wilson intervals, not the normal
  approximation, which collapses near 0 or 1:

  `centre = (p + z²/2n) / (1 + z²/n)`, `half = z·sqrt(p(1−p)/n + z²/4n²) / (1 + z²/n)`

  A floor check passes on the interval's lower bound only when the slice is
  sized for it ([eval-statistics.md](eval-statistics.md)); otherwise report
  `inconclusive`. Hard negatives with a 100% floor are counts, not intervals.
- Citation support: for answered cases, check that the cited passage supports
  the claim (deterministic span or entailment check before an LLM judge).

## 2. Per-stage evaluation for multi-stage pipelines

An end-to-end score cannot say which stage failed. Test each stage in isolation
on gold inputs, then end-to-end; a stage's isolated score is an upper bound on
what it contributes. Memory pipelines map as:

| Stage | Isolated test | Metric |
|-------|---------------|--------|
| Admission | gold event set with should-store / should-ignore labels | recall of should-store; false-admit rate |
| Encoding | gold events with expected facts or typed objects | schema validity; extraction precision/recall; stable-ID and `effective_from` correctness |
| Persistence | write then read back; restart; delete | round-trip equality; provenance (source-episode IDs) present |
| Maintenance | scripted sequences of contradiction, duplicate, expiry, deletion | exact resulting state (see §4); deletion cascades to indexes |
| Retrieval | question to gold evidence IDs | recall@k per slice; scope-filter leaks |
| Post-retrieval | fixed retrieved set to selected/computed/synthesised output | citation support; computed-result exactness; dedup |
| Materialisation | memory to each output format | schema validation of machine outputs |

Pick the cheapest grader per row (deterministic before judge). A pipeline with
fewer stages uses the rows that exist.

**Extraction judging.** Judge each extracted field against its source span, not
the whole record. In a vendor-published study (small n), a decomposed per-field
judge separated right from wrong extractions far better than a whole-record
judge ([method](https://xmemory.ai/jev-per-field-extraction-judge/)). Use the
per-field scores to escalate only flagged records to a slower extractor or a
human, and fit the escalation threshold on held-out records, not the tuning set.

## 3. Regression gate on change

Re-run the frozen suite, held-out set included, when any of these change: the
model, the embedding model, a prompt, or index/query/ingestion code. Required:

- Fail on any slice-floor breach or hard-negative miss, not only on the aggregate.
- Gate on the pinned versions: record model IDs, index fingerprint, and suite
  hash in the result so a pass is attributable.
- **Exercise the shipped default path.** Run the real entry point with shipped
  config and the real index, no overrides. If the index is stale, missing, or
  its fingerprint does not match the code, the eval must fail, not fall back to
  a weaker path. Observed: editing query code changed the index fingerprint and
  the eval silently scored an in-memory fallback. A degraded run reports
  `inconclusive`, never a pass (see Release Decision Gate in SKILL.md).
- Per-stage model swaps (a cheaper model for one stage) need that stage's
  isolated test re-run, not just the end-to-end score.
- A newer model is not exempt. One study reports a newer model scoring below
  its predecessor on an enterprise text-to-SQL memory dataset (arXiv 2605.26394,
  abstract only), so every model upgrade re-runs the full suite.
- Field descriptions and extraction prompts are code: editing one changes what
  gets stored without a code diff. Version them and trigger the suite on change.

## 4. State-maintenance scoring

Updates, renames, relationship changes, deletions, and point-in-time queries
("who owned X at 09:05?") have one right state. Score them as exact-state
correctness (field values, IDs, validity interval, absence after deletion), not
semantic similarity: a plausible-sounding stale answer scores high on similarity
and is wrong. Use an LLM judge only for synthesised free-text answers, and
calibrate it per [llm-judge-bias.md](llm-judge-bias.md). Case templates:
[ai-context-layer memory responsibilities audit](../../ai-context-layer/references/memory-responsibilities-audit.md).

The core categories and a running incident example live in
[ai-context-layer state-maintenance eval](../../ai-context-layer/references/evals-and-operations.md#state-maintenance-eval):
update, rename, relationship change, tombstone, supersession, point-in-time,
duplicate event, out-of-order backfill, stale secondary source, role confusion,
and read-side scope leakage. Add the cases below, which that set omits. They are
engine-neutral; run them on your own data whichever engine you adopt, and do
not substitute a vendor's benchmark for them.

| Test | Scenario | Pass condition |
|---|---|---|
| Write diff (extends update) | any write | the write returns old → new values, matching the stored change; a no-op write returns an empty diff |
| Old name (extends rename) | query by the pre-rename name | resolves to the same entity ID or is retired explicitly; never a second entity |
| Field clearance | "X no longer has a deadline" | the field reads as cleared, not the stale value, and cleared is distinguishable from never recorded |
| Absence | ask for a fact that was never written | explicit unknown or abstain; no plausible value |
| Negative exclusion | "which X are not Y", including a case whose answer is empty | the exact set; an empty answer is returned as empty |
| Entity deletion cascade | delete a parent entity | dependants cascaded or nulled per policy; no answer cites the deleted entity |
| Missing-key collapse | two writes without the primary key | two records or a rejection, never a silent merge onto one record |
| Scoped write | a write scoped to record A mentions record B | B unchanged, and the skip is reported |
| Partial aggregate | scoped aggregate with one record missing | the response flags the missing record; never a silent total over what was found |
| Query audit | any natural-language read | the generated query (SQL or equivalent) is logged and replays to the same answer |

Missing-key collapse, scoped write, and partial aggregate fail silently, so
treat them like hard negatives: any miss blocks. A Postgres reference schema
that covers update, backfill, duplicate, clearance, and as-of cases is in
[ai-vector-brain bitemporal state facts](../../ai-vector-brain/references/postgres-pgvector-default.md#bitemporal-state-facts).

## 5. Cross-tenant leakage slice

The isolation patterns and the single-pair canary test live in
[tenant-isolation-patterns.md](../../ai-context-layer/references/tenant-isolation-patterns.md).
The eval slice generalises that test:

- **Seed** at least two canary tenants, each holding unique sentinel facts
  (random tokens that cannot occur naturally) in every store the system reads:
  chunks, typed facts, graph edges, summaries, caches, and learned memories.
- **Query** from every other tenant, real and canary, with the sentinel's exact
  token, a paraphrase of the fact, and the shared entity name.
- **Pass**: zero sentinel hits at any k. Retrieve at the largest k the system
  can ever request, and also check the final answer and tool outputs. This is a
  count, not a rate: one hit blocks release, and no interval applies.
- **Negative control**: with the scope filter removed, the sentinels must be
  found. Otherwise the slice cannot detect a leak.
- **When**: per engine and per index or leg (lexical, vector, graph, cache), and
  after every index rebuild, embedding migration, or filter or cache-key
  change. A rebuild that drops a partition or filter predicate leaks without
  any code diff in the query path.

## 6. Learned and procedural memory

A learned skill, consolidated note, playbook delta, or self-written memory entry
changes the system, so gate it like a code change:

- **Baselines.** Run the same agent on the same held-out tasks with no memory,
  with full context or raw episodes, and with the learned memory. The tasks are
  ones the memory was not learned from. Memory must beat no-memory on task
  success, and match full context (where the history fits) at lower cost. A
  vendor's own table put full context above its memory system on accuracy, with
  the memory's win in latency and tokens (arXiv 2504.19413).
- **Guard set.** Use tasks the agent already passes without memory; any
  regression blocks. Repeated consolidation is reported to raise utility and
  then push it below the no-memory baseline, with an episodic-only control
  staying competitive (arXiv 2605.12978, abstract). So keep the raw episodes,
  run consolidation on a schedule, and promote its output only through this
  eval, never after every interaction.
- **Verified admission.** Store a skill only after an external success signal,
  such as tests or environment state. Verification is the gate: removing the
  self-verification critic had the largest ablation effect in Voyager (arXiv
  2305.16291). The judge itself can still be wrong, so check its false
  positives: Reflexion's self-written tests can pass wrong code (arXiv
  2303.11366), and judge-labelled workflows can be mislabelled (arXiv
  2409.07429).
- **Poison persistence.** Plant a bad skill, let the agent run, then remove the
  skill. Pass means no copy or derivative survives; one study reports poisoned
  copies persisting after the planted skills were removed (arXiv 2608.25776).
- **Transfer.** Test on another task family or role, because a skill can
  specialise and lose effectiveness under transfer (arXiv 2606.23127, abstract).
- **Rollback.** Every self-written change carries a diff, provenance, and
  version, and a failed gate restores the last accepted version. Exercise the
  rollback once; a rollback path that has never run is not one.

Promoting a note into an instruction file is the same gate with a narrower
test: [agents-memory memory-discipline](../../agents-memory/references/memory-discipline.md#promoting-notes-into-instruction-files).

## 7. Reading vendor memory benchmarks

Which public benchmarks measure what is covered in
[agent-memory-benchmarks.md](../../ai-context-layer/references/agent-memory-benchmarks.md).
Count a vendor's memory-benchmark claim as evidence only when it states all of
these:

- the dataset and version, with n per category;
- the metric and grader, including the judge model and prompt;
- **baseline configuration parity**: each baseline got the same domain
  configuration (schema, ontology, instructions) as the vendor's system;
- runs and confidence intervals;
- a reproducible runner, including the baseline adapters;
- cost and latency next to accuracy.

A claim missing any of these is directional. When the vendor wrote both the
schema and the questions, the result shows fit to those questions, not an
engine ranking. Re-run on your data before citing the claim.
