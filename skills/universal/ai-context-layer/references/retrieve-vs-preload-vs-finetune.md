# Retrieve vs Preload vs Fine-Tune — The Context-Brain Decision Rubric

Three production paths exist for getting knowledge to a model: **retrieve at query time** (RAG), **preload into context** (CAG / long-context), or **bake into weights** (fine-tune). Most teams default to RAG because it is the loudest pattern. That is often the wrong choice.

This file is the entry point for the decision. The deep references for each path are siblings.

---

## Table of Contents

- [The three paths](#the-three-paths)
- [The decision tree](#the-decision-tree)
- [The 3-question filter](#the-3-question-filter)
- [Composition — the common production answer](#composition--the-common-production-answer)
- [Anti-patterns](#anti-patterns)
- [Related](#related)

---

## The three paths

| Path | What it is | Owns | When it wins |
|---|---|---|---|
| **Retrieve** | RAG: query → retrieve → ground → answer | `ai-rag` + `ai-vector-brain` | Large corpus, fast-changing, citations required |
| **Preload** | CAG / long-context: load corpus once, query directly | [cache-augmented-generation.md](cache-augmented-generation.md), [long-context-first-architecture.md](long-context-first-architecture.md) | Small, stable corpus that fits in context |
| **Fine-tune** | Bake patterns into weights via SFT / DPO / LoRA | `ai-llm/references/fine-tuning-recipes.md` + [fine-tune-for-behavior-not-facts.md](fine-tune-for-behavior-not-facts.md) | Stable **behavior, form, style, refusal** — never volatile facts |

The fourth path is **composition** — almost every production system blends two or three (fine-tune behavior + preload core docs + retrieve volatile facts).

---

## The decision tree

```text
Q1: Does the answer depend on facts that change weekly or faster?
  YES → Retrieve (RAG, H1–H7).
        Fine-tune cannot keep up. Preload would need re-caching at every change.
  NO  → continue ↓

Q2: Does the entire corpus fit in the model's context window
     (with headroom for query + answer + system prompt)?
  YES → Preload (CAG or long-context, I1 / I2).
        Then run economics check ↓
  NO  → Retrieve. Skip to Q4.

Q3: Economics check — is prompt-cache cost < equivalent vector-DB cost
     at your query volume and corpus refresh cadence?
  YES → Preload. Done.
  NO  → Retrieve.

Q4: Independent of facts — do you need consistent behavior,
     persona, output format, or refusal style?
  YES → Fine-tune (I3) ON TOP of whichever path above.
        Fine-tune for FORM, never for FACTS.
  NO  → System prompt is enough.
```

A common production answer is: **Q1 = no for some, yes for others** → preload stable + retrieve volatile + fine-tune behavior. See [Composition](#composition--the-common-production-answer).

---

## The 3-question filter

If any answer is YES, you probably should not be using RAG (or not RAG alone):

1. **Is the corpus < 200K tokens and refreshes less than weekly?** → CAG candidate.
2. **Does every query need the whole corpus** (e.g. cross-document comparison, document QA)? → long-context candidate.
3. **Are users frustrated by inconsistent persona / format / refusal style across answers?** → fine-tune-for-behavior candidate.

Conversely, if all three are NO, RAG is the right default.

---

## Composition — the common production answer

The common enterprise composition is:

```text
Fine-tune layer  →  behavior, persona, structured output, refusal style
Preload layer    →  stable evergreen content (policies, schemas, ontology, glossary)
Retrieve layer   →  volatile facts (current data, recent tickets, latest docs)
```

This is **RA-CB-1** below. It is what teams converge on after trying each path in isolation and discovering each one fails alone:

- Fine-tune alone → stale facts, expensive retrains.
- Preload alone → cannot accommodate change or scale.
- Retrieve alone → inconsistent voice, no shared base, retrieval errors leak through.

### RA-CB-1 — Composed context brain

```text
              ┌───────────────────────────────────┐
              │  Fine-tuned base                  │   form, refusal, persona
              │  (behavior, not facts)            │   re-train quarterly
              └─────────────┬─────────────────────┘
                            │
              ┌─────────────▼─────────────────────┐
              │  Preloaded context (CAG)          │   stable evergreen
              │  Glossary, ontology, key policies │   refresh on doc change
              │  (cached KV prefix)               │
              └─────────────┬─────────────────────┘
                            │
              ┌─────────────▼─────────────────────┐
              │  Retrieved chunks (RAG H1–H7)     │   volatile facts
              │  Confidence-scored, cited         │   live retrieval
              └─────────────┬─────────────────────┘
                            │
                            ▼
                       Final answer
```

Composes with: any RAG scenario (H1–H7), [cache-augmented-generation.md](cache-augmented-generation.md), [long-context-first-architecture.md](long-context-first-architecture.md), [fine-tune-for-behavior-not-facts.md](fine-tune-for-behavior-not-facts.md).

---

## Anti-patterns

- **A-CB-1 — Default to RAG without running Q1–Q4.** Most common failure mode. A 50K-token product handbook does not need a vector DB; it needs prompt caching. Teams burn weeks building RAG pipelines for corpora CAG would have served in a day.
- **A-CB-2 — Fine-tune to inject facts.** "Fine-tune for form, not facts." Fine-tuning to teach a model your current pricing or current API surface produces a stale model the day after training. Use retrieve or preload.
- **A-CB-3 — Preload a fast-changing corpus.** If the corpus changes faster than you can re-cache, KV cache invalidation eats the speed gain. Re-evaluate Q1.
- **A-CB-4 — Mix everything without ownership boundaries.** "Some facts in fine-tune, some in preload, some in retrieve" with no rule for what goes where → cross-source contradictions and audit nightmare. Pick the rule (RA-CB-1) and enforce it.
- **A-CB-5 — Skip the economics check.** Preload looks free until token-per-query × queries-per-day × cache miss rate adds up. Always check prompt-cache cost vs vector-DB cost at your real volume.
- **A-CB-6 — Treat fine-tune as one-time.** Behavior drifts as base models update. Re-train cadence is part of the fine-tune contract, not an afterthought.

---

## Related

- [cache-augmented-generation.md](cache-augmented-generation.md) — Preload pattern, KV-cache lifecycle (I1)
- [long-context-first-architecture.md](long-context-first-architecture.md) — Whole-corpus prompting at 1M+ tokens (I2)
- [fine-tune-for-behavior-not-facts.md](fine-tune-for-behavior-not-facts.md) — Form-not-facts rule (I3)
- [patterns-catalog.md](patterns-catalog.md) — P1–P25 context patterns
- [reference-architectures.md](reference-architectures.md) — RA1–RA13
- `ai-rag/SKILL.md` — when retrieval is the right path
- `ai-llm/references/fine-tuning-recipes.md` — SFT / DPO / LoRA mechanics
- `ai-llm-inference` — prompt-cache mechanics that power CAG and long-context
- `foundations-decision-theory` — VoI framing for the retrieve-vs-preload economics check
