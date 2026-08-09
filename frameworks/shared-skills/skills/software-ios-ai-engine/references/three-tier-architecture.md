# Three-Tier Architecture

## Table of Contents

- [Why three tiers, not two](#why-three-tiers-not-two)
- [Tier 0 — Intent Router](#tier-0--intent-router)
- [Tier 1 — Composer](#tier-1--composer)
- [Tier 2 — Cloud LLM](#tier-2--cloud-llm)
- [The fallback chain](#the-fallback-chain)
- [Cost model](#cost-model)
- [Default deployment](#default-deployment)

The decision framework for answering a user question grounded in a rich per-user context bundle, without defaulting to a cloud LLM on every turn.

## Why three tiers, not two

The common product failure is a binary split: "local heuristics" for a narrow set of structured questions, "cloud LLM" for everything else. The seam is visible: users type an open question ("I have a sad day"), the heuristic layer can't match, and the UI either falls through to the cloud silently (burning quota, breaking the offline promise) or shows a reject card (telling the user the feature is limited).

The fix is to insert a **Composer** tier between intent routing and cloud fallback. Tier 0 decides *what* the answer is about, Tier 1 renders it from local evidence, Tier 2 is an explicit upgrade path for genuinely open synthesis. This mirrors the classic NLG pipeline (content determination → sentence planning → surface realization) but makes the sentence-planning/realization stage pluggable across deterministic and neural engines.

## Tier 0 — Intent Router

**Input:** raw user question + persistent context (chart, HD, plan, mood/energy, locale).
**Output:** `{ archetype, slots, evidenceRefs[], safetyBoundary }`.

Responsibilities:

- **Archetype classification.** One of `reflect` / `interpret` / `guide` / `clarify` / `check_in`. This governs the voice contract the composer will use. Route emotional-support keywords to `reflect` even when the question is phrased as a decision question.
- **Slot extraction.** Named entities relevant to the question (date, person, topic, life area) so the composer knows what to anchor on.
- **Evidence bundling.** Call retrieval; assemble the top-N chunks + the current-moment snapshot (transits, personal day, progressed moon, activity ratings, dream themes) into a typed bundle. Cap tokens/size per tier band.
- **Safety routing.** Crisis patterns → static supportive response, composer skipped. Clinical patterns → softened tone flag passed to composer. Emotional patterns → feel-first flag. See [intent-router-patterns.md](intent-router-patterns.md).

Tier 0 is **deterministic**, **fast** (~1 ms), and **fully testable** as a pure function. If this tier misroutes, every downstream composer misfires — get it right before touching Tier 1.

## Tier 1 — Composer

**Input:** the structured output from Tier 0.
**Output:** `{ answer, grounding, followUps[], composerUsed }`.

Three engine choices, picked per-request via a capability gate and a fallback chain:

1. **Option A — Apple Foundation Models** (iOS 26+, Apple Intelligence-capable device). On-device ~3B LLM. Natural prose. Private. No quota. [option-a-foundation-models.md](option-a-foundation-models.md).
2. **Option B — Sentence bank.** Hand-curated prose fragments keyed by `(archetype, anchor, mood)`. Deterministic, auditable, always available. [option-b-sentence-bank.md](option-b-sentence-bank.md).
3. **Option C — Retrieval stitch.** Top-k knowledge chunks wrapped by archetype-specific boilerplate. Useful for long-tail interpretation questions. [option-c-retrieval-stitch.md](option-c-retrieval-stitch.md).

Tier 1 **never** produces raw model output. Every composer runs through the same post-processor: anchor-count validation, word-count trim, forbidden-phrase filter, grounding-line extraction.

## Tier 2 — Cloud LLM

**Input:** the same Tier 0 output + a richer prompt template optimized for cloud model voice.
**Output:** same answer contract as Tier 1.

Reserved for:

- Multi-turn reasoning chains where the user has explicitly asked "tell me more."
- Novel question types the router doesn't yet have an archetype for.
- Deep synthesis the user opted into by tapping the cloud pill.

Tier 2 is **never** silent fallback. Every Tier-2 invocation is an explicit user choice, either by the pill default being set to cloud or by tapping a "Deeper answer" CTA after a Tier-1 bubble.

## The fallback chain

```
Tier 0 classifies → bundle assembled
         │
         ▼
Try Option A (Foundation Models)
  ├── device unavailable ─────────────┐
  ├── model availability != available ┤
  ├── output fails anchor/length guard┤
  └── user Retry after A already ran ─┤
                                      ▼
                                  Option B (sentence bank)
                                      │
                                      ├── archetype has thin fragment coverage
                                      │   AND Option C is enabled
                                      ▼
                                  Option C (retrieval stitch)
                                      │
                                      └── composer chain exhausted
                                           │
                                           ▼
                                 Static safety copy (reject frame
                                 replaced with supportive line + CTA to cloud pill)
```

**Cloud Tier 2 is not in the Data-first fallback chain.** It's a sibling path, invoked only when the cloud pill is active or when the user explicitly upgrades a bubble. Mixing Tier 2 into Tier 1's fallback silently undermines the "Data-first doesn't spend AI quota" promise.

## Cost model

| Tier | User-perceived latency | Per-answer cost (2026) | Quota |
|---|---|---|---|
| 0 | ~1 ms | ~0 | none |
| 1A (Foundation Models) | 80–250 ms on-device | 0 (free inference) | none |
| 1B (sentence bank) | <5 ms | 0 | none |
| 1C (retrieval stitch) | 20–80 ms (existing retrieval) | 0 | none |
| 2 (cloud LLM) | 600–1200 ms | $0.002–$0.02 per answer | counts against free/paid tier |

This is why Tier 1 matters: the composer layer is the difference between a free feature and a unit-cost feature. For free-tier users capped at 1 cloud answer/week, Tiers 0 + 1 *must* carry everyday engagement; Tier 2 is an upsell hook, not a default.

## Default deployment

Ship in this order:

1. **Week 1 — Tier 0 + Option B.** Converts every reject card into a real answer. Not perfect voice, but factually grounded and always available.
2. **Week 2 — Option A on capable devices.** Same bundle, same contract. Gate behind `SystemLanguageModel.default.availability`. Option B remains the fallback.
3. **Week 3 — Option C for thin-coverage archetypes.** Interpretation questions where B's fragments would repeat too often.
4. **Ongoing — Tier 2 surfaced as explicit "Deeper answer" CTA.** Never silent.

This ordering is load-bearing:

- Shipping A without B leaves pre-iOS-26 / non-AI-capable devices broken.
- Shipping C without A/B produces correct but robotic voice — users downgrade to "feels like a search result."
- Shipping Tier 2 as silent fallback quietly breaks the quota story and erodes trust the first time a power user notices.

## Why not one big tier with everything

Three temptations to collapse tiers, and why to resist each:

**"Just let the LLM call tools and it'll handle routing + composition."** The tool-calling-agent pattern is right for agents that *act* (book a flight, send an email). For a consumer answer surface where 95% of queries need a single composed paragraph, the agent overhead burns latency and tokens on every turn and surfaces more ways to fail. Keep routing deterministic; let composers be pluggable.

**"Sentence bank is enough — skip the LLM entirely."** Works for 6–12 months, then users see repetition across sessions and the novelty wears off. Pair it with Option A so voice quality grows without changing the bundle pipeline.

**"Cloud LLM is 800 ms, no one cares about the latency difference with on-device."** They care about the **quota**. Cloud-only means free-tier users see "you've used your 1 answer this week" after every ASK tap, and the product feels gated. On-device composition is the reason Data-first can be generous without burning margin.

## What this tier split enables

- Free tier is meaningfully usable (unlimited Tier 1 answers).
- Paid tier feels like an upgrade (cloud depth on demand, not "we turned the feature on").
- Retention metrics stop conflating "user ran out of quota" with "user lost interest."
- Eval and regression gates become possible — each tier has a narrow, testable contract.
- Offline mode works for the first time: Tier 0 + 1 require no network.

## Common mistakes

- **Gating Tier 1 by question type** (rejecting emotional questions because "that's an AI Answer use case") — every archetype must have a Tier-1 path.
- **Letting Tier 1 pick different output shapes per composer** — UI becomes a branching mess; every composer must emit the same `{ answer, grounding, followUps }` contract.
- **Running Tier 0 in the composer** — if the composer decides the archetype, testing is impossible and two composers will disagree on voice.
- **Sharing prompt templates between A and B** — the sentence bank is already realized prose; the Foundation Models prompt is a voice contract + a fact bundle. Conflating them produces either flat A output or hallucinating B.
- **Using the grounding line as an afterthought** — the grounding line is the trust signal; if it's generic, users assume the answer is too.

## When to reassess the split

- If Tier 0 misroutes more than 2% of questions, the router needs a model upgrade (embedding classifier instead of regex + keywords) — not a composer change.
- If Tier 1 output is flat across composers, check whether the evidence bundle is too sparse — the composer can only work with what it's given.
- If Tier 2 conversion falls below expected when cloud pill is offered as an upgrade, the Tier 1 answer is probably already good enough and the cloud CTA needs better framing (deeper lookup, multi-day synthesis, partner chart, etc.), not lower-quality Tier 1.
