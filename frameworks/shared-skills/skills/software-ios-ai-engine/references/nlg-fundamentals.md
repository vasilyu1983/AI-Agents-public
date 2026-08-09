# NLG Fundamentals

## Table of Contents

- [The classical NLG pipeline](#the-classical-nlg-pipeline)
- [How this skill's tiers map to the pipeline](#how-this-skills-tiers-map-to-the-pipeline)
- [Why pure templates fail](#why-pure-templates-fail)
- [Why pure LLM prompting fails](#why-pure-llm-prompting-fails)
- [The "glass box" vs "black box" distinction](#the-glass-box-vs-black-box-distinction)
- [Structured output as the glass-box/black-box bridge](#structured-output-as-the-glass-boxblack-box-bridge)

Why this skill's three-tier / three-composer split mirrors the classical Natural Language Generation pipeline, and why neither "pure templates" nor "pure LLM" is enough on its own.

## The classical NLG pipeline

Since Reiter & Dale (1997), NLG systems have split the generation task into three stages:

1. **Content determination** — deciding *what* to say (which facts, which focus, which exclusions).
2. **Sentence planning** — deciding *how* to structure it (ordering, aggregation, connective choice).
3. **Surface realization** — picking the specific words and rendering grammatical output.

Each stage has distinct inputs, outputs, and failure modes. Collapsing them into one step (as early template systems and recent one-shot LLM prompts both do) hides the failures until they surface as bugs in production.

## How this skill's tiers map to the pipeline

| Pipeline stage | Skill tier | Why |
|---|---|---|
| Content determination | Tier 0 (router + bundle assembly) | What the answer will be about is decided here, deterministically. Archetype + slots + bundle = "here are the facts relevant to this question." |
| Sentence planning | Tier 1 (composer options) | The composer decides role sequence (opener → anchor → action → closer), ordering, and connective style. |
| Surface realization | Tier 1 (same composer, realization step) | The composer substitutes slots, picks actual words, formats ordinals, punctuates. Option A does it neurally; Options B/C do it via templates + realizer rules. |
| *(meta)* quality guard | Cross-tier validator | Not part of classical NLG; added because both LLM and template paths can emit unacceptable output that the renderer shouldn't be responsible for catching. |

The reason to keep these stages visibly separate is testability and swap-ability. Option A and Option B can coexist because they share content determination (Tier 0) — only the sentence-planning + realization bits differ.

## Why pure templates fail

Template-based NLG — the pre-LLM default — has known limits:

- **Cannot adapt outside predefined use cases.** A template for "Your Sun in {sign} makes you {trait}" cannot answer "I have a sad day."
- **Combinatorial authoring cost.** N archetypes × M chart conditions × K moods × L locales grows faster than any content team.
- **Repetition becomes visible.** Users in the same condition bundle see the same sentence every time.
- **No graceful degradation.** Missing a slot or a condition means no template matches; the system falls through to a generic answer or a reject card.

Templates stay valuable for:

- **Deterministic facts** where byte-identical output is a feature, not a bug (billing messages, compliance copy, confirmations).
- **Short structural phrases** inside a larger composed answer (grounding line, follow-up chip).
- **Safety copy** where the content must be exactly what was reviewed.

This is why the sentence-bank composer (Option B) is assembled from *fragments*, not full-answer templates. Fragments recombine; full templates don't.

## Why pure LLM prompting fails

The failure pattern from the production diagnosis that sparked this skill:

- **Invented facts.** "Uranus influences your Mars" appears in the answer when no such transit exists in the evidence.
- **Form-filling over synthesis.** Given schema fields `answer / whyThisMatters / nextStep / guidance[]`, the model fills each slot independently, often restating the same idea across slots.
- **Templated voice.** Without strong anchor rules, the model falls back on generic phrasings ("invites you to approach this thoughtfully," "trust the universe") — the same output shape emerges for semantically distinct questions.
- **Grounding signal unused.** 14 on-topic evidence refs assembled, 0 cited in the answer, grounding score 20/100. The bundle was present; the prompt didn't consume it.
- **Ordinal / concat bugs.** Template assembly happens around the prompt, not inside it ("This touches your 1th house themes…"), and small bugs compound when the composer isn't audited.

LLMs stay valuable for:

- **Natural voice** in open-ended turns where a fragment catalog can't anticipate every phrasing.
- **Multi-turn reasoning** where context chains matter more than single-answer realization.
- **Novel questions** outside any archetype the router has.

Hybrid is the settled consensus because each failure mode of pure-template / pure-LLM is the strength of the other.

## The "glass box" vs "black box" distinction

The research literature splits NLG systems two ways:

- **Black box** — a model takes content + planning implicit, produces realized text. You see input and output; you don't see which facts it used or why.
- **Glass box** — every intermediate decision is observable. You can trace "this sentence came from fragment X, this anchor came from bundle field Y."

Neither is universally better. Trade-offs:

| | Glass box (B, C) | Black box (A, Tier 2) |
|---|---|---|
| Traceability | Full | Partial (structured outputs help) |
| Auditability | Every token has provenance | Statistical |
| Voice quality | Depends on authoring | Natural by default |
| Novel situations | Needs new fragments / chunks | Adapts |
| Regression testing | Straightforward (snapshot) | Requires eval harness |
| Compliance fit | Strong (approved copy) | Weaker (requires post-hoc review) |

For consumer assistant surfaces in trust-sensitive domains (finance, health, astrology-as-guidance, legal-adjacent), the rule of thumb is **prefer glass-box at the outer layer, allow black-box at the inner realization layer**. That's exactly what this skill's three-tier structure does: glass-box Tier 0 routing, glass-box Tier 1 sentence-bank composer as the always-available baseline, black-box (Option A, Tier 2) models as upgrades for voice quality or deep synthesis.

## Structured output as the glass-box/black-box bridge

The modern innovation — visible in Apple's Foundation Models `@Generable` and in OpenAI's structured JSON outputs — is constraining a black-box model to emit a fixed schema. This doesn't make the model glass-box, but it lets a glass-box validator wrap it:

```
model emits: { answer: "...", grounding: "...", anchorsNamed: [...] }
                       │
                       ▼
              anchor-validator:
                every anchor mentioned in `answer` must appear in the evidence bundle.
                       │
                       ├── ok → render
                       └── failed → retry once / fall through to B
```

This is the pattern Option A uses. It's why `@Generable` matters more than "the model is good at JSON" — the schema constrains the **content determination** independently of the realization, letting the validator check the first without parsing the second.

## Why separate the grounding line from the answer

A subtle but load-bearing design choice. The grounding line:

- Is generated from the same anchors the answer used — but explicitly, not implicitly.
- Lives in a distinct UI slot so users can see "what this was based on" at a glance.
- Is easier to validate independently ("did the composer name anchors from the bundle?") than auditing prose.
- Acts as a trust mechanism — specific anchors signal personalization; generic grounding ("your chart") signals template output.

If you collapse the grounding line back into the answer ("As a Cancer Sun with Sagittarius Moon in the 11th..."), you get lectures instead of conversation and lose the audit affordance. Keep them distinct.

## When to revisit the pipeline split

- **If the composers can't be tested without the router** — the router is doing too much; pull some of its logic into explicit contracts the composer reads.
- **If the same fact appears in both router output and composer output with different representations** — you have duplicate state; pick one authoritative place (usually the router / bundle).
- **If a new answer kind doesn't fit any archetype** — don't jam it into an existing archetype; add a new one and route to it explicitly.
- **If voice quality stops improving despite composer upgrades** — the bundle may be too thin. Go upstream to retrieval ([ai-rag](../../ai-rag/SKILL.md)) before investing more in composers.

## Further reading

- Reiter & Dale, *Building Natural Language Generation Systems* (1997) — canonical pipeline definition.
- Accelerated-Text's [awesome-nlg](https://github.com/accelerated-text/awesome-nlg) list — curated NLG resources, including realizers.
- RAGFlow's [2025 year-end review: from RAG to Context](https://ragflow.io/blog/rag-review-2025-from-rag-to-context) — the industry's current consensus on hybrid retrieval + composition.
- Apple Foundation Models [developer documentation](https://developer.apple.com/documentation/FoundationModels) — `@Generable` and constrained decoding patterns.
