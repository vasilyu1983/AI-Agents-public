# Source Confidence Scoring

Score each retrieved chunk *before* generation so the prompt can filter, rerank, or abstain. Lives between the reranker and constrained generation (stage 4 in the canonical RAG pipeline).

A confidence score answers one question: **how much should the model trust this chunk to answer this query?** It is not a relevance score — relevance says "this chunk talks about the query," confidence says "this chunk is worth citing."

## Table of Contents

- [When to use](#when-to-use)
- [The four signals](#the-four-signals)
- [Combining signals](#combining-signals)
- [Patterns](#patterns)
- [Anti-patterns](#anti-patterns)
- [Recipe: minimal scorer](#recipe-minimal-scorer)
- [Evaluation](#evaluation)
- [Related](#related)

---

## When to use

- Production RAG over a corpus with mixed freshness (wikis, repos, support tickets, archived docs).
- Multi-tenant or multi-source retrieval where some sources are authoritative and some are user-generated.
- Compliance-adjacent answers where a wrong citation is worse than a refusal — pair with [abstention-recipe.md](abstention-recipe.md).
- Any pipeline where the reranker returns top-K but K includes plausible-but-stale or off-domain chunks.

Skip if the corpus is uniform (single-source, version-controlled, low-churn) — relevance from a cross-encoder is enough.

---

## The four signals

Pick a subset. Most production pipelines use 3 of 4. Adding more without measuring noise is anti-pattern A-CS-3 below.

### 1. Freshness — `f`

How recently was the chunk written or last reviewed?

- Repo corpus: `git log -1 --format=%ct <file>` → seconds since epoch. Stale code is a real hallucination source.
- Wiki/notes corpus: `updated_at` from the CMS or filesystem `mtime`. Notes drift fast.
- Decay: `f = exp(-Δt / τ)` where `τ` is the half-life. Default `τ = 180 days` for wikis, `τ = 90 days` for code, `τ = 30 days` for support content.

Edge case: some chunks are timeless (RFC text, regulation §X.Y, mathematical definitions). Tag them at ingest with `evergreen=true` and skip freshness decay.

### 2. Authority / Trust — `a`

Is the source authoritative for this query type?

- Repo: `main` branch > feature branch > `.archive/`. README > inline comment. Test file > generated doc.
- Wiki: official handbook page > meeting notes > Slack export. Owner-reviewed > orphaned.
- Per-source weights assigned at ingest in a small JSON table — see fixture below.

Authority is **per query type**, not global. A policy chunk has high authority for "what is our refund policy" and low authority for "how do we implement refunds in code."

Two ways to keep `a` current as feedback arrives: a static per-source table refreshed by batch review (P-CS-1 below), or a per-element streaming update applied at feedback time (P-CS-5). Neither is universally correct — pick based on how fast trust actually needs to move and whether you can tolerate a rebuild step.

### 3. Overlap with other retrieved chunks — `o`

Does this chunk agree with the other top-K chunks?

- Cluster the top-K by embedding cosine similarity at threshold ~0.75.
- A chunk in the largest cluster gets `o = 1`. A solo chunk gets `o = 1/K`.
- High overlap = corroboration. Low overlap = contradiction or topic drift.

Important caveat: overlap also rewards duplication. Pair with strong dedup at ingest (stage 1) or this signal inflates trivially.

### 4. Retrieval consistency — `c`

Did this chunk come from both retrievers (BM25 ∧ vector), or just one?

- Both → `c = 1.0`
- Vector only → `c = 0.7`
- BM25 only → `c = 0.6`
- Reranker-promoted only (was past top-K in neither) → `c = 0.4`

Consistency catches the failure mode where one retriever finds a chunk by coincidence (lexical near-miss, embedding artifact) and the reranker happens to score it high.

---

## Combining signals

### Default: weighted geometric mean

```text
confidence = (f^wf × a^wa × o^wo × c^wc) ^ (1/(wf+wa+wo+wc))
```

Geometric — not arithmetic — because **any** signal near zero should kill the score (a fresh, authoritative, retrieved-twice chunk that contradicts every other retrieved chunk is suspect, not above-average). Default weights: `wf=1, wa=2, wo=1, wc=1`. Tune from eval set, not from intuition.

### Threshold

Set one threshold per surface, not globally:

| Surface | Threshold | Rationale |
|---|---|---|
| User-facing answer with citations | 0.55 | Below → drop chunk from context |
| Refusal gate (stage 7) | mean(top-N confidence) < 0.45 | Below → abstain. See [abstention-recipe.md](abstention-recipe.md) |
| Internal agent / dev use | 0.35 | Tolerate lower-confidence chunks for ideation |

Calibrate against a labeled eval set of ~200 query-chunk pairs. Without calibration, every threshold is a guess.

---

## Patterns

### P-CS-1 — Per-source authority table

Keep authority weights in a small versioned file, not in code:

```yaml
# data/source-authority.yaml
sources:
  - id: handbook
    paths: ["docs/handbook/**"]
    weight: 1.0
    evergreen_paths: ["docs/handbook/policies/**"]
  - id: code-main
    paths: ["src/**"]
    branch: main
    weight: 0.9
  - id: meeting-notes
    paths: ["notes/meetings/**"]
    weight: 0.4
  - id: archive
    paths: [".archive/**", "**/deprecated/**"]
    weight: 0.1
```

Why versioned: when you bump `meeting-notes` from 0.4 → 0.6, you want git blame to show the date and the eval delta.

### P-CS-2 — Cross-encoder calibration

The reranker score (e.g. MiniLM, BGE) is not a confidence score — it's a relevance ordering. Use it as one input to `confidence`, not as the output. Cross-encoders are well-known to be over-confident on out-of-domain queries.

### P-CS-3 — Two-stage filter

Cheap signals first, expensive last:

1. `c` (retrieval consistency) — free, already known from stage 2.
2. `f` (freshness) — one timestamp lookup per chunk.
3. `a` (authority) — one JSON lookup per chunk.
4. `o` (overlap) — requires clustering top-K. Compute only on chunks that passed steps 1–3.

This matters at K=50+. At K=10 just compute everything.

### P-CS-4 — Per-query-type weights

A "policy" query weights authority and freshness highly; a "how do I implement" query weights authority less and overlap more. Classify the query at ingest of the *query* (cheap LLM call or rule-based) and pick a weight profile.

### P-CS-5 — Streaming trust update (per-element EMA, no retrain)

P-CS-1's authority table is edited by hand and reviewed in batches — fine for slow-moving per-source trust, wrong for per-chunk or per-graph-element trust that should move on every piece of feedback without waiting for a review cycle or a reindex.

The alternative: keep authority as a per-element score (per chunk, per graph node/edge — not per source) and update it in place with an exponential moving average each time a feedback event lands, instead of batching feedback into a periodic retrain:

```text
updated_score = previous_score + alpha * (observed_rating - previous_score)
final_score = clip(updated_score, 0, 1)
```

- `alpha` controls the tradeoff: higher alpha reacts to recent feedback faster but is noisier (one bad rating swings the score more); lower alpha is smoother but slower to reflect a real change in source quality. There is no universal correct value — it is a per-workload calibration, not a constant to copy.
- Each update touches exactly one element's stored score and does O(1) work regardless of corpus size — no rebuild, no retrain pass, no rescoring of unrelated chunks. This is the property that matters operationally: authority can move continuously alongside production feedback traffic instead of only refreshing on the next batch cycle (P-CS-1) or the next reranker training run (see `user-feedback-learning.md` Pattern 4).
- Clip to a fixed range (e.g. `[0, 1]`) so a run of extreme feedback can't push the score outside the range the rest of the confidence formula expects.
- This changes *authority* (`a`), not relevance ranking — pair it with the existing signals in "Combining signals" above, the same as any other authority source.

**When to use**: authority needs to track fine-grained, frequently-updated feedback (per-chunk or per-graph-element trust in an agent-memory or graph-RAG system with a live feedback stream). **When to skip**: authority is a small, slow-moving, human-curated set of sources (P-CS-1's table is simpler and more auditable) — don't add a streaming update path until batch review has demonstrably lagged the feedback rate.

**Source**: pattern observed in [topoteretes/cognee](https://github.com/topoteretes/cognee) `cognee/tasks/memify/apply_feedback_weights.py` (`stream_update_weight`, default `alpha=0.1`) at commit [`a148eab`](https://github.com/topoteretes/cognee/blob/a148eab58eb2f9769585f10da5486543c9ece457/cognee/tasks/memify/apply_feedback_weights.py), Apache-2.0, extracted 2026-08-09. cognee applies this to per-node/per-edge "feedback weights" on its knowledge graph, consumed downstream in retrieval scoring (`cognee/modules/retrieval/utils/brute_force_triplet_search.py`); `alpha=0.1` is cognee's own calibration for its workload, not a value to copy without testing on your own feedback distribution.

---

## Anti-patterns

- **A-CS-1 — Use cross-encoder score as confidence.** Cross-encoders are uncalibrated and over-confident on OOD. Always combine with freshness/authority/consistency. See P-CS-2.
- **A-CS-2 — Threshold-on-the-fly.** Threshold tuning without an eval set produces a number that drifts with corpus changes. Pin it to a labeled set and re-run on every corpus refresh.
- **A-CS-3 — More signals = better.** Six signals on a 200-query eval set means you are fitting noise. Start with 3, add a 4th only if it moves recall@K or hallucination rate on the eval set.
- **A-CS-4 — Linear combination.** Arithmetic mean lets a high signal mask a zero signal. Use geometric mean or min-of-signals for the abstain decision.
- **A-CS-5 — Overlap without dedup.** Without ingest-time dedup, overlap rewards duplicate chunks and inflates confidence on the most-duplicated content in the corpus. Fix dedup before adding overlap.
- **A-CS-6 — One global threshold.** A 0.6 threshold that works for compliance answers is wrong for internal dev queries. Per-surface thresholds (see table above).

---

## Recipe: minimal scorer

```python
import math
from dataclasses import dataclass

@dataclass
class Chunk:
    id: str
    text: str
    source_id: str
    updated_at: float           # epoch seconds
    evergreen: bool
    came_from_bm25: bool
    came_from_vector: bool
    rerank_score: float
    embedding: list[float]      # for overlap clustering

def freshness(c: Chunk, now: float, half_life_days: int = 180) -> float:
    if c.evergreen:
        return 1.0
    tau = half_life_days * 86400
    return math.exp(-(now - c.updated_at) / tau)

def consistency(c: Chunk) -> float:
    if c.came_from_bm25 and c.came_from_vector: return 1.0
    if c.came_from_vector: return 0.7
    if c.came_from_bm25:   return 0.6
    return 0.4

def confidence(c: Chunk, authority: dict, overlap: float, now: float,
               weights=(1, 2, 1, 1)) -> float:
    f = freshness(c, now)
    a = authority.get(c.source_id, 0.5)
    o = overlap
    s = consistency(c)
    wf, wa, wo, wc = weights
    # Geometric mean — any near-zero signal dominates.
    return (f**wf * a**wa * o**wo * s**wc) ** (1/(wf+wa+wo+wc))
```

Overlap (`o`) requires clustering top-K — compute once per query, share across chunks.

---

## Evaluation

Confidence scoring is judged by two metrics on a labeled eval set:

1. **Precision @ threshold** — of chunks that pass the threshold, what fraction are truly answer-supporting? Target ≥ 0.85.
2. **Refusal correctness** — of queries where the system abstains (mean confidence < 0.45), what fraction are genuinely unanswerable from the corpus? Target ≥ 0.7. Below this, the system over-refuses.

Build the eval set once per quarter from real production queries. Sample 200, label by hand or with LLM-as-judge + spot check. See [rag-evaluation-guide.md](rag-evaluation-guide.md) for harness setup.

---

## Related

- [hybrid-fusion-patterns.md](hybrid-fusion-patterns.md) — where `c` (consistency) comes from
- [ranking-pipeline-guide.md](ranking-pipeline-guide.md) — what feeds the scorer
- [grounding-checklists.md](grounding-checklists.md) — what consumes the scorer downstream
- [abstention-recipe.md](abstention-recipe.md) — what to do when confidence is low
- [rag-evaluation-guide.md](rag-evaluation-guide.md) — calibration harness
- [user-feedback-learning.md](user-feedback-learning.md) Pattern 4 — batch reranker retraining; contrast with P-CS-5's streaming per-element update
- `foundations-information-theory` — MI/redundancy framing for the overlap signal
