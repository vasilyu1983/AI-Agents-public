# Option C — Retrieval-Stitch Composer

## Table of Contents

- [When to pick it](#when-to-pick-it)
- [When to skip it](#when-to-skip-it)
- [How it differs from Option A](#how-it-differs-from-option-a)
- [Structure](#structure)
- [Scoring for selection](#scoring-for-selection)
- [Boilerplate layer](#boilerplate-layer)
- [Grounding line from chunks](#grounding-line-from-chunks)
- [Locale coverage](#locale-coverage)
- [Verification](#verification)

Pick the top-k knowledge chunks from the evidence bundle, wrap them with archetype-specific boilerplate, and emit the result as a composed answer. Glass-box RAG without an LLM.

## When to pick it

- You already have a retrieval layer producing high-quality scored chunks (6+ on-topic chunks per bundle is a healthy floor).
- You have **thin sentence-bank coverage** for long-tail archetypes (unusual transits, rare chart shapes, edge-case HD profiles) — authoring fragments for every case is more work than writing a stitcher.
- You need a composer that "reads like the knowledge base" — educational, reference-grade prose.
- Option A is unavailable and Option B would require 5×+ fragment investment to reach the query tail.

## When to skip it

- Chunks are short phrases or headlines — retrieval stitching needs full-sentence chunks to read naturally.
- Chunks are written in a different voice from the product (formal textbook language inside a chatty app looks spliced).
- The knowledge base has inconsistent per-chunk length; stitched output flips between terse and verbose.
- Archetype requires emotional acknowledgment (feel-first rule) — the retrieval tier doesn't know about the user's mood; a stitched answer that skips acknowledgment and dives into interpretation is exactly the UX problem this skill exists to fix.

Good rule of thumb: **Option C is best for `interpret` archetype, rarely for `reflect` or `guide`.**

## How it differs from Option A

Option A asks an on-device LLM to *compose* over the bundle; Option C *reuses* the bundle as the composition. There is no generation step — the output is a deterministic function of retrieval scores + boilerplate.

This trades voice quality for:
- **Determinism** — byte-identical output for identical inputs.
- **Traceability** — each sentence in the answer maps to a chunk in the knowledge base.
- **Zero hallucination risk** — nothing in the answer is generated; everything was written by a human author in the knowledge base.

## Structure

Four pieces:

1. **Retrieval stage** — already upstream; produces scored chunks keyed to the question + bundle. See [ai-rag](../../ai-rag/SKILL.md).
2. **Stitcher** — picks top-k (usually 2) chunks based on score + archetype relevance, selects one boilerplate opener, one boilerplate closer, one grounding line.
3. **Connective polish** — joins chunks with archetype-specific transitions, normalizes punctuation, collapses whitespace.
4. **Quality guard** — same as Option B: word count, anchor count, forbidden phrases.

## Scoring for selection

Retrieval returns chunks with similarity scores. The stitcher adds archetype-specific reweighting:

```
final_score(chunk) =
    0.60 * cosine(question_embedding, chunk_embedding)
  + 0.25 * archetype_affinity(chunk.tags, archetype)
  + 0.10 * anchor_coverage(chunk, bundle)
  + 0.05 * freshness(chunk.updated_at)
```

- **`archetype_affinity`** — chunks tagged `action` score high for `guide`, chunks tagged `interpretation` score high for `interpret`, etc. Without this weighting, an interpretation chunk lands in a decision answer.
- **`anchor_coverage`** — favor chunks that mention anchors present in the user's bundle (the user's sun sign, HD type, personal day). A chunk about Cancer Sun scores higher for a Cancer-Sun user than a generic chunk.
- **`freshness`** — minor weight; avoids surfacing chunks that haven't been updated in years when a newer version exists.

Pick top-2. Going above 2 usually blows the 70-word budget.

## Boilerplate layer

The openers and closers are Option-B-style fragments, but tiny — one sentence each, archetype-keyed, locale-aware:

```
archetype=interpret, opener: "Here's what your chart says about this:"
archetype=interpret, closer: "Read that alongside what's happening for you right now."
archetype=guide, opener: "Timing-wise, here's the shape of it:"
archetype=guide, closer: "If that doesn't fit your gut, trust your gut."
```

Keep the boilerplate bank small and varied (5–10 openers per archetype, same for closers). The boilerplate carries archetype voice; the chunk carries content.

## Grounding line from chunks

For Option C, the grounding line names **the chunks used** (in human terms, not chunk IDs):

```
"Grounded in 'Stuckness needs a precise cause' · 'Personal Day gives a light daily action tone'"
```

or, if you'd rather present anchors from the bundle rather than chunk titles:

```
"Grounded in your Cancer Sun · Personal Day 6 · Generator Sacral"
```

Pick one convention and stick to it across A/B/C for UI consistency. Chunk-title grounding reads more "library-ish"; bundle-anchor grounding reads more "about you." Most consumer apps pick bundle-anchor.

## Locale coverage

Retrieval-stitch's locale quality equals the knowledge base's locale quality. If your chunks are English-only, the output is English-only — even if the user is browsing in French.

Mitigations:

- **Translate chunks, not stitched output.** Per-locale chunk embeddings + per-locale translations, same chunk IDs across locales.
- **Don't machine-translate stitched output at runtime.** Users notice the seam between the translated opener and the translated chunk.
- **Fall through to B or a safety copy** in locales with < 60% chunk coverage, rather than showing a partial-English answer.

## Safety integration

Unlike Option B (curated per safety boundary), Option C's chunks are usually authored for general interpretation. Safety handling:

- **Crisis boundary** — bypass composer entirely, show static safety copy (same as A and B).
- **Clinical boundary** — filter out chunks tagged `diagnostic` or `prescriptive`; prefer chunks tagged `reflective` or `educational`.
- **Emotional-support intent** — usually a poor fit for Option C. If the router flags emotional intent and Option B is thin, prefer a conservative Option-B safety-net answer over a stitched interpretation that may feel clinical.

## Quality guard

Same as Options A and B, plus one extra Option-C-specific check:

- **Chunk-duplicate phrases** — two chunks that both use the same filler phrase ("As a general principle…") produce visible repetition in a stitched answer. Dedupe within-answer at the phrase level; if dedupe would strip more than 20% of a chunk, drop the chunk and pick the next ranked one.

## When to fall through to Option B

- Top-1 chunk score is below a threshold (e.g., cosine < 0.55) — retrieval didn't find anything relevant; stitching would produce noise.
- Fewer than 2 chunks pass archetype affinity filter.
- Stitched answer would exceed 85 words even after trimming.
- Anchor count in stitched answer is < 2.

## Testing

Pure function → snapshot tests work well. Fixture bundles with known chunk scores, assert specific chunks get picked, assert stitched prose matches a snapshot.

```swift
func testStitch_interpret_careerQuestion_saturnTransit() {
    let bundle = EvidenceBundle.fixture(...)
    let chunks = RetrievalResult.fixture([
        (id: "saturn_10th_career_pressure", score: 0.81, tags: ["interpretation", "saturn"]),
        (id: "jupiter_11th_expansion",      score: 0.62, tags: ["interpretation", "jupiter"]),
        (id: "generic_career_advice",       score: 0.74, tags: ["action", "career"]),
    ])
    let tier0 = Tier0Output(archetype: .interpret, ...)

    let answer = stitcher.compose(bundle: bundle, chunks: chunks, tier0: tier0, seed: 42)

    XCTAssertEqual(answer.composerUsed, .retrievalStitch)
    XCTAssertTrue(answer.answer.contains("Saturn"))
    XCTAssertFalse(answer.answer.contains("generic_career_advice"))
}
```

## Instrumentation

Per answer:

- `composerUsed: "retrieval_stitch"`
- `chunkIds: [top-2 selected]`
- `chunkScores: [floats]`
- `archetypeAffinityWeights: [...]` — useful for tuning reweighting
- `anchorCoverage: float` — how many bundle anchors the picked chunks mentioned
- `fallthroughToB: bool` — if guard rejected; diagnostic
- `wordCount`, `anchorCount` (same as A/B)

Over time, chunk-selection telemetry is the best signal for knowledge-base gaps — chunks that never get picked are dead weight; queries that always trigger fallthrough indicate missing coverage.

## Common pitfalls

- **Stitching three chunks because "more anchors = better."** Blown word budget, seam fatigue. Two chunks is the sweet spot.
- **Not reweighting by archetype.** Interpretation chunks show up in decision answers; action chunks show up in reflection answers. Raw cosine similarity is not enough.
- **Static opener/closer pool of size 1.** Every Option-C answer opens with the same sentence. Matters especially because chunks are already shared across users — opener repetition compounds.
- **Allowing chunks with templated placeholders** (`{sun_sign}` literally in the stored chunk) to reach the stitcher without substitution. Run the slot substituter over chunks at retrieval time, not at stitch time.
- **Skipping the grounding line.** The grounding line is the trust mechanism; Option C without it feels like an autogenerated FAQ answer.
- **Mixing chunks from incompatible voice registers.** "Mars Retrograde demands introspection" paired with "chill for a week and touch grass" reads like two different authors. Tag chunks with `voice_register` and prefer within-register picks.

## Verification

Before shipping Option C:

- [ ] Retrieval produces ≥ 2 chunks per typical bundle for `interpret` archetype queries.
- [ ] Archetype affinity reweighting is applied and unit-tested.
- [ ] Boilerplate bank has ≥ 5 openers and ≥ 5 closers per archetype, localized.
- [ ] Chunk-duplicate phrase dedupe runs before emit.
- [ ] Safety boundaries filter chunks appropriately; emotional-intent bundles prefer B.
- [ ] Fall-through to B is instrumented and rate < 15% on production bundles.
- [ ] Snapshot tests cover `interpret` + `guide` hot paths.
- [ ] Chunks are locale-matched; no cross-locale answer stitched at runtime.
