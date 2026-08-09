# Abstention Recipe — "Insufficient Evidence Found"

When retrieval cannot support a grounded answer, the system must refuse — not invent. This is stage 7 of the canonical RAG pipeline: the confidence gate between scoring and generation.

The job of this recipe: decide *when* to abstain, *how* to phrase the abstention, and *what to log* so the corpus can be improved.

A correct abstention is a feature, not a failure. Silent fallback to a low-quality answer is the failure.

## Table of Contents

- [When to use](#when-to-use)
- [The decision](#the-decision)
- [Decision-theoretic framing](#decision-theoretic-framing)
- [How to phrase the abstention](#how-to-phrase-the-abstention)
- [Partial answers - handle carefully](#partial-answers--handle-carefully)
- [Patterns](#patterns)
- [Anti-patterns](#anti-patterns)
- [Reference flow](#reference-flow)
- [Evaluation](#evaluation)
- [Related](#related)

---

## When to use

- Any user-facing surface where a wrong cited answer is worse than no answer (compliance, finance, legal, medical adjacent, security advice).
- Multi-tenant RAG where one tenant's missing content must not be patched with another tenant's content.
- Agent loops where a hallucinated answer would propagate to downstream tool calls.

Skip — i.e. tolerate best-effort answers — for ideation surfaces, brainstorming, internal dev assistants where the human verifies. State the surface stance explicitly in the system prompt; do not let it drift.

---

## The decision

Abstain when **any** of these is true:

1. **Confidence floor breached.** Mean confidence of the top-N retrieved chunks `< T_abstain` (default `0.45`, calibrated per surface — see [confidence-scoring.md](confidence-scoring.md)).
2. **Empty retrieval.** Top-K is empty after filters, or all top-K were dropped by confidence threshold.
3. **Contradiction.** Top-N chunks split into clusters with directly contradictory claims (no plurality). Detect with NLI model or cluster-disagreement heuristic.
4. **Out-of-scope query.** Classifier or rule says the query is outside the corpus's declared scope (e.g. user asks "how do I file taxes" against a product manual corpus).
5. **Freshness floor breached.** All top-N chunks older than the corpus-declared staleness threshold *and* the query is time-sensitive (current pricing, current policy, current API).

Use **any-of**, not all-of. Each condition independently justifies refusal. Compounding them produces silent failures.

---

## Decision-theoretic framing

This is a Value-of-Information / minimax-regret call. See `foundations-decision-theory` primitives 4 (VoI) and 3 (minimax regret).

- Cost of wrong answer (`C_wrong`): user makes a bad decision based on hallucinated cite. Often high in compliance, low in brainstorming.
- Cost of refusal (`C_refuse`): user friction, perceived system weakness. Mitigated by *helpful* refusal text (see template).
- Refuse when `P(wrong | answer) × C_wrong > C_refuse`.

In practice the threshold `T_abstain` is the operational proxy for this calculus. Calibrate it per surface — `C_wrong` differs by 10x between compliance and ideation.

---

## How to phrase the abstention

The refusal text is part of the product. Generic "I don't know" is anti-pattern A-AB-3. Use this structure:

```text
1. State what was searched.       (transparency)
2. State what was not found.      (specificity)
3. Offer a next action.           (utility)
4. Optionally, surface the closest partial match — clearly labeled.
```

### Template

```text
I couldn't find authoritative information about [paraphrased query] in
[corpus name, e.g. "the company handbook"].

The closest match I found is [doc title, dated YYYY-MM-DD], which covers
[related but not answering topic]. That isn't enough to answer your question.

You could:
- Ask [domain owner / channel]
- Check [adjacent system, e.g. "the policy archive in Notion"]
- Rephrase the question — I searched for [actual query terms used]
```

### What to never do

- Do not silently degrade to general-knowledge answer ("from what I know about taxes…").
- Do not fabricate a citation that did not appear in retrieval.
- Do not refuse without telling the user what was searched. Opacity destroys trust.

---

## Partial answers — handle carefully

If `K_pass = number of chunks above confidence floor` is small but nonzero (typically 1–2), you have a choice:

| `K_pass` | Action |
|---|---|
| 0 | Full abstention. Use template above. |
| 1 | Answer **only what that one chunk supports**, cite it, and explicitly bound the answer: "Based on a single source from [date], …". Flag low corroboration. |
| 2+ | Normal grounded answer with citations. |

Pattern: a partial answer must say it is partial. Hidden uncertainty is the failure mode.

---

## Patterns

### P-AB-1 — Two-tier threshold

One threshold for "drop this chunk from context" (stage 5), a stricter threshold for "abstain entirely" (stage 7). Default: `T_drop = 0.55`, `T_abstain = 0.45`. The gap lets borderline chunks inform the answer without forcing a refusal.

### P-AB-2 — Per-surface stance, declared in system prompt

```text
ANSWERING STANCE: strict-grounded
- You may only answer from retrieved chunks.
- If retrieved chunks do not support an answer, output the refusal template.
- Never use prior knowledge. Never invent citations.
```

Variants: `strict-grounded` (compliance), `grounded-preferred` (support), `best-effort` (ideation). Pick one per surface and bake it into the system prompt — do not negotiate it per turn.

### P-AB-3 — Refusal logging is corpus telemetry

Every refusal is a signal: either the corpus has a gap, or the query was out of scope. Log:

```json
{
  "query": "...",
  "query_class": "policy|how-to|definitional|...",
  "reason": "confidence_floor|empty|contradiction|oos|stale",
  "top_k_passed": 0,
  "mean_confidence": 0.32,
  "closest_chunk_id": "doc-123#42",
  "ts": "..."
}
```

Aggregate weekly. The top refusal clusters are your prioritized corpus-improvement backlog. This closes the loop with stage 8 (continuous evals).

### P-AB-4 — Contradiction detection

When top-N chunks contradict each other (e.g. two policy versions, one outdated), the model should not "average" them. Either:

- Pick the higher-authority + fresher chunk and cite it as the current source of truth, **or**
- Surface both and refuse to choose: "Sources disagree. [Doc A, 2024-03-12] says X; [Doc B, 2026-01-04] says Y. Confirm with [owner]."

The second option is correct when authority ties are real (two equally authoritative sources truly disagree — a corpus-curation problem).

### P-AB-5 — Out-of-scope guardrail

A small router/classifier runs before retrieval: "Is this query within the corpus's scope?" If no, abstain *before* burning retrieval cost. Especially valuable for tenant-scoped or domain-scoped corpora.

---

## Anti-patterns

- **A-AB-1 — Silent fallback to general knowledge.** Worst possible failure mode: the model "helpfully" answers from training data and calls it grounded. Mitigate with explicit system-prompt stance (P-AB-2) and eval-set probes that include OOS queries.
- **A-AB-2 — Single global threshold.** A `T_abstain = 0.45` good for the handbook surface is too strict for the dev-tools surface. Per-surface, calibrated.
- **A-AB-3 — Generic refusal text.** "I don't have information about that" trains users to bypass the system. State what was searched, what was missing, where to go next.
- **A-AB-4 — Refuse without logging.** Refusals are the most valuable corpus-improvement signal you have. A refusal that is not logged is wasted.
- **A-AB-5 — Refuse after answering.** Some systems generate the answer, then run a confidence check and prepend a disclaimer. The model has already conditioned the user on the wrong answer. Gate *before* generation.
- **A-AB-6 — Hide contradictions.** Picking one side of a contradiction without surfacing it is silent failure. See P-AB-4.
- **A-AB-7 — Confuse "no high-confidence chunks" with "no chunks."** These produce different refusals. Empty retrieval suggests OOS or corpus gap; low-confidence retrieval suggests stale or low-authority sources. Log them distinctly.

---

## Reference flow

```text
top-K chunks + confidence scores ──┐
                                   ▼
                  ┌──────────────────────────────┐
                  │ Abstention gate              │
                  │                              │
                  │ 1. K_pass = chunks ≥ T_drop  │
                  │ 2. mean_conf = mean(K_pass)  │
                  │ 3. contradiction = NLI(...)  │
                  │ 4. oos = classifier(query)   │
                  │ 5. stale = all(c.age > τ)    │
                  └────────────┬─────────────────┘
                               │
              any failure? ────┼──── no
                               │     │
                               ▼     ▼
                   refusal template   constrained generation
                               │
                               ▼
                       log to telemetry
                       (P-AB-3)
```

---

## Evaluation

Two metrics on a labeled eval set with planted OOS and unanswerable queries:

1. **Refusal correctness** — of queries the system refused, what fraction were genuinely unanswerable from the corpus? Target ≥ 0.7. Below this, over-refusal.
2. **Coverage** — of queries the corpus *can* answer, what fraction were answered (not refused)? Target ≥ 0.85. Below this, also over-refusal.

There is a real tradeoff. If you push refusal correctness to 0.95, coverage usually drops below 0.7. Pick the operating point per surface. Re-run on every corpus refresh.

Bake ≥20% OOS / unanswerable queries into the eval set — without them, you cannot measure refusal at all.

---

## Related

- [confidence-scoring.md](confidence-scoring.md) — what feeds the gate
- [grounding-checklists.md](grounding-checklists.md) — citation discipline for the answer path
- [rag-evaluation-guide.md](rag-evaluation-guide.md) — eval harness, including OOS sets
- [user-feedback-learning.md](user-feedback-learning.md) — closing the loop on logged refusals
- `foundations-decision-theory` — VoI, minimax-regret, expected-cost framing for `T_abstain`
- `ai-context-layer` — refusal patterns at the context layer (system-prompt stance)
