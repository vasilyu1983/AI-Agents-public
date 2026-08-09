# Patterns, Anti-Patterns, Known Traps, and Scenarios

Full catalog for the local iOS AI engine. Reference from SKILL.md via the Navigation section.

---

## Table of Contents

- [Patterns](#patterns)
- [Anti-Patterns](#anti-patterns)
- [Known Traps](#known-traps)
- [Scenarios](#scenarios)

## Patterns

Reusable generative techniques. Most production composers use 6–10 together.

### Composer architecture

- **P1 · Capability-gated fallback chain.** Per-request pick A → B → C based on `SystemLanguageModel.default.availability`, bundle richness, and archetype. Chain decision is data-driven, not hardcoded per screen.
- **P2 · Shared output contract across engines.** A single Swift value type (`{ answer, grounding, followUps[], safetyBoundary, composerUsed }`) emitted by every composer. UI reads the type, not the engine.
- **P3 · Bundle-first, prose-second.** Compose from a typed evidence struct (`EvidenceBundle`), never from raw text or JSON blobs. The struct is the single contract between Tier 0 and Tier 1.
- **P4 · Deterministic replay core.** The composer itself is a pure function: `(bundle, intent) -> answer`. UI integration, logging, and network are thin wrappers. Test the core without a simulator.
- **P5 · Archetype-governed voice contract.** Tier 0 selects one of five voices (`reflect`, `interpret`, `guide`, `clarify`, `check_in`); each composer looks up its voice rules from the same table. Changing voice is a data edit, not a code edit.
- **P6 · Universal post-processor.** Anchor validator → word-count trimmer → forbidden-phrase filter → grounding-line extractor. Runs after every composer, including Option A. Raw model output never reaches the UI.

### Prose craft

- **P7 · Feel-first opener.** When archetype is emotional (`reflect` / `check_in` with low-mood slot), the first sentence acknowledges the stated feeling before any astrological framing. Encoded as a voice-contract flag, not a prompt hint.
- **P8 · Anchor-stacking (2–3 concrete anchors).** Every answer names ≥2 concrete items from the bundle ("Cancer Sun · Progressed Moon in Cancer · Generator Sacral"). The count is asserted by the post-processor.
- **P9 · Evidence-ref whitelist.** Composer may only mention signs, planets, houses, HD attributes, personal days, and chunk themes that are literally in the bundle. Whitelist is enforced in post-processing — even Option A is bounded.
- **P10 · Ordinal invariant.** Single `formatOrdinal(_:locale:)` helper used in server templates, B fragments, and client-side rendering. Invariant-tested for 1st/2nd/3rd/4th/11th/21st edge cases across every shipped locale.
- **P11 · Per-locale composition.** Compose in the user's locale, don't translate afterwards. B ships per-locale fragment files; A ships per-locale prompts; C ships per-locale knowledge chunks.
- **P12 · Word-budget hard-trim-then-retry.** Composer trims soft to 40–70 words; if trim would remove anchors, it retries with a stricter plan rather than emit an under-anchored bubble.

### Option A (Foundation Models) craft

- **P13 · `@Generable` structured output.** Force the FM session into the shared answer type via `@Generable` + guided generation. Never parse free text from the model.
- **P14 · Availability-aware gating (not `#available`).** Gate on `SystemLanguageModel.default.availability == .available`, not OS version. `.modelNotReady` means the asset is downloading — treat as transient and fall to B this turn.
- **P15 · Session scoped to the active user, locale, and task.** Reuse static instructions only inside that boundary; never share `LanguageModelSession` across accounts, profiles, locales, or materially different tasks. Start fresh for Retry and after user/locale switches.
- **P16 · Prompt budget under the 4096-token context window.** Token-count instructions, prompt, tool definitions, tool outputs, `@Generable` schemas, and expected response. Drop the lowest-confidence chunks first. The A-prompt is never "dump the whole bundle and hope."
- **P17 · Seed / request-ID for Retry.** Pass a request ID that differs on Retry so sampled output is meaningfully different, not re-rolled identical.
- **P27 · Writing-style adapter only for voice, never for facts.** If a FM writing-style adapter (LoRA) is used, it trains tone/register — never anchor selection, safety, or factual grounding. Those stay in the bundle, the whitelist, and the post-processor. Most sentence-bank-first products don't need an adapter at all; B already owns voice.
- **P28 · Capability-surface probe, not assumption.** Before relying on any FM feature beyond `@Generable` + plain completion (tool-calling, streaming mid-string edits, multimodal input), probe it against the current runtime and fail closed to B. FM feature matrix moves faster than your release train.

### Option B (sentence bank) craft

- **P18 · `(archetype, anchor, mood)` fragment keys.** Fragments are addressed by a three-part key, not by freeform IDs. Makes coverage analysis a SQL-style query.
- **P19 · Anti-repetition window.** B tracks last-N fragments shown per user and avoids re-use within the window. Falls back to a different anchor rather than repeating.
- **P20 · Connective-tissue layer.** Fragments join through a small, boring connective layer (commas, "and," "today"). Fragments themselves never contain connective prose — they're composable atoms.

### Option C (retrieval-stitch) craft

- **P21 · Archetype-specific wrappers, not the raw chunk.** C never renders a knowledge chunk directly — wraps 1–2 top-k chunks in an archetype-appropriate opener + closer.
- **P22 · Chunk-provenance isolation.** Retrieval index is user-scoped or namespace-scoped. A chunk from user X's custom notes can never surface in user Y's answer.

### Safety & explicit upgrade

- **P23 · Safety routes bypass the composer layer entirely.** Crisis patterns hit a static, locale-qualified supportive-copy path with help-line resources. No A/B/C call happens.
- **P24 · Explicit Tier-2 upgrade affordance.** Cloud LLM is a user-visible CTA ("Deeper answer — uses quota"), never a silent fallback. Tier-2 output is visually labeled in the UI.

### Observability

- **P25 · Structured trace per answer.** Emit `{ archetype, composerUsed, anchorCount, wordCount, latencyMs, groundingScore, fallbackReason?, refusalReason? }` on every render. Powers eval-observer regression gates.
- **P26 · Composer-usage mix alert.** Alarm if the Option-A share on Apple-Intelligence devices drops below a floor — usually means a regression is silently falling back to B.

---

## Anti-Patterns

Patterns seen in shipped or near-ship iOS apps. Each is a specific failure mode with a concrete symptom.

### Product framing

- **A1 · Reject card as UX.** "I can only answer timing/decision questions" rendered for an emotional prompt. This leaks the absence of a composer to the user. The correct framing: Data-first is *always* an answer; cloud is an *upgrade*.
- **A2 · Silent cloud fallback.** Data-first mode quietly calls Tier 2 when Tier 1 misses. Breaks the "offline / no quota" promise and destroys trust the first time it runs out of credits.
- **A3 · "AI Answers" label bolted on after the fact.** If composer-used attribution wasn't baked into the contract, you'll later retrofit it as a prop-drilled flag and still miss some code paths.

### Architecture

- **A4 · Composer without Tier 0 intent routing.** Timing questions get reflective prose; emotional questions get decision framing. Classify first, compose second.
- **A5 · Per-composer output contract drift.** A returns `{text, source}`, B returns `{answer, anchors}`, C returns a string. The UI grows composer-specific branches, then eval tooling grows them too, then a fourth composer breaks everything.
- **A6 · Option A without a B/C fallback.** Any pre-iOS-26 device, any Apple Intelligence-disabled device, and any `.modelNotReady` window shows a broken screen.
- **A7 · Reusing a Tier-2 prompt verbatim as an Option A prompt.** Cloud prompts assume long context and discursive voice; FM ~3B model hallucinates or degrades. Write A's prompt from scratch for the bundle-first contract.

### Prose

- **A8 · Section labels as grounding.** "Grounded in your Natal chart anchors · Plan snapshot · Client surface signals" is worse than nothing — it exposes internal retrieval structure.
- **A9 · Generic filler grounding.** "Grounded in your chart energy" or "Based on what I know about you." Fails the anchor-test (can a reader reconstruct which 2–3 facts?).
- **A10 · Inventing anchors not in the bundle.** Composer writes "Uranus squares your Mars" when no such transit is in the evidence. Especially common with Option A if the whitelist isn't enforced in post-processing.
- **A11 · Forbidden-phrase build-up.** "Trust the universe," "invites you to approach this thoughtfully," "the stars are aligning." Accumulate in logs; block with a filter; rotate the blocklist per release.
- **A12 · Feel-first skipped on emotional archetype.** Composer leads with "Your progressed Moon in Cancer suggests…" when the user said they're having a sad day. Acknowledge first.

### Operations

- **A13 · Mixing composer types per archetype without a documented default.** One PR changes timing answers from A→B; the next changes reflection from B→A; no one can reason about voice consistency.
- **A14 · Gating on iOS version instead of `SystemLanguageModel.availability`.** Ships a bug on Apple-Intelligence-ineligible iPhone 15 Pro devices running iOS 26 (region, storage, or user-disabled Apple Intelligence).
- **A15 · Shipping English-only fragments and leaning on translation memory.** B fragments carry cultural and emotional nuance that machine-translation flattens. Fragment authoring is a localized writing task.
- **A16 · Composer owning safety routing.** Asking the FM session "and also don't say anything unsafe" inside the prompt. Safety must be a Tier-0 router decision that bypasses the composer.
- **A17 · No Retry differentiation.** Tapping Retry on an Option-A answer produces the same answer because no seed/request-ID variance is wired through.
- **A18 · Post-processor skipped for "safe" composers.** "Option B is deterministic, so we don't need anchor-count validation on it." Then an author ships an under-anchored fragment and the regression ships with it.
- **A19 · Reaching for a writing-style adapter to fix a content problem.** Flat voice in Option A? Usually the bundle is thin or the prompt is vague — adapters won't rescue either. Train an adapter only after the bundle is rich, the prompt is tight, and voice is the actual remaining gap.
- **A20 · Leaning on FM tool-calling before probing the runtime.** Shipping a code path that assumes the on-device model can call app tools/functions, without a capability probe and a B-fallback. Feature set of `FoundationModels` moves across point releases; treat every non-`@Generable` capability as probe-then-use (P28).
- **A21 · Composer identity stamped on the HTTP envelope but not on the persisted jsonb.** Backend returns `{answerSource: "backend_sentence_bank", answer: {…no answerSource…}}`. Client renders fine; analytics is fine; but the stored `answer` row in the database has `answerSource: null`, so every downstream eval, audit, and head-to-head replay cannot tell which composer produced the prose. The stamp must live **inside** the value persisted to the database — same `answerSource` that the UI reads. Pair this with an integration test that asserts no persisted row has `answerSource IS NULL` for a successful compose.
- **A22 · Contract field declared on the type but not populated by every builder.** `grounding: string` is on the `CosmosAnswer` interface, A-path composer writes it, B-path (deterministic/sentence-bank) builder forgets it because "the data-mode fallback just returns prose." iOS either (a) renders an empty italic line or (b) grows client-side derivation from `personalizationReason`, which silently drifts from backend grounding on A-path. Fix once at the server: every composer — including the deterministic ones — must compute the grounding line from the anchors it actually used and write it into the persisted record.

---

## Known Traps

Implementation-level gotchas caught by teams during integration. Budget a day per trap you hit cold.

### Foundation Models / iOS 26 runtime

| Trap | Symptom | Fix |
|---|---|---|
| T1 · `.modelNotReady` treated as permanent | Asset still downloading | Retry silently next turn; compose with B now |
| T2 · Simulator reports `.available` but returns empty strings | CI passes, prod broken | Always test Option A on a physical Apple-Intelligence device |
| T3 · iPad mini 6 / iPhone 15 (non-Pro) look capable but aren't | Device-list hardcode broken on new hardware | Use the availability API only; no device lists |
| T4 · `@Generable` schema drift breaks JSON parse silently | `nil` in production after field addition | Snapshot-test the `@Generable` schema |
| T5 · FM session state leakage across users | Prior context bleeds in family-shared app | Open fresh session per request (P15) |
| T6 · Token budget blown by non-ASCII content | Overflow on Cyrillic / emoji-heavy chart names | Budget with the real tokenizer, not byte length |
| T6a · Tool/schema overhead omitted from token budget | "Short prompt" still overflows at 4096 | Count instructions + prompt + tools + schemas + response; query `contextSize`/`tokenCount(for:)` (iOS 26.4+) instead of a hardcoded 4096 |
| T6b · `maximumResponseTokens` used as quality control | Malformed or partial prose | Prefer shorter instructions; reserve cap for runaway protection |
| T21 · FM capability matrix drift across point releases | Tool-calling breaks on 26.x update | Probe-then-use (P28); keep B as the no-capability baseline |
| T22 · Adapter sideloading and signing forgotten | App Review rejection | Ship adapter as a signed, versioned app-bundled asset |
| T26 · Building against WWDC26-announced iOS 27 surface (third-party `LanguageModel` protocol, 12 GB advanced-tier model, free Private Cloud Compute access) before it ships | Code compiles against a beta SDK, then breaks or is unavailable on GA devices for months | Gate any iOS 27-only capability behind its own availability check; keep the iOS 26 path as the shipping default until 27 has meaningful install share |

### Tier 0 / intent routing

| Trap | Symptom | Fix |
|---|---|---|
| T7 · Compound-word pattern matches | `\bsad\b` fires on "sadhana" | Word-boundary + negative lookaheads; unit-test adversarial strings |
| T8 · Crisis router consumes non-crisis idioms | "kill this task" hits crisis path | Idiom-allowlist; high-precision phrase patterns over keyword lists |
| T9 · Slot extraction loses date context across midnight | Personal Day off-by-one at DST boundary | Centralize date math in one function |

### Prose / formatting

| Trap | Symptom | Fix |
|---|---|---|
| T10 · `"\(n)th"` ordinals | "1th house," "21th degree" | Always via `formatOrdinal` (P10); lint-rule the concat pattern |
| T11 · Master-number ordinal rendering | "11th" for Personal Day 11/22/33 | Distinct formatter path for unreduced masters |
| T12 · Russian ordinals | Crashes or wrong suffix | Locale-aware ordinal from the start |
| T13 · Trimmer removes the grounding line | Under-grounded bubble after trim | Extract grounding before trimming, re-attach after |
| T14 · Nil-slot substitution in templates | ` is welcome today` when mood absent | Default-value every slot |

### Retrieval-stitch (Option C)

| Trap | Symptom | Fix |
|---|---|---|
| T15 · Cross-user chunk bleed | Premium chunk surfaces in free-user answer | Namespace at the index level, not the query |
| T16 · Stale chunk after content update | Deprecated interpretation keeps surfacing | Tag chunks with a release marker |
| T17 · Chunk wrappers leak retrieval jargon | "According to your reference material…" | C wrappers must read as native prose |

### Evaluation / release

| Trap | Symptom | Fix |
|---|---|---|
| T18 · QA misses anchor-count regression | Passes on 3 prompts; fails at scale | Offline eval harness across a pinned corpus every commit |
| T19 · Fallback-chain silent regression | Feature flag flips, all users get B; nobody notices | Monitor composer-usage mix (P26) |
| T20 · Reject-card metric hidden from product | Refusals in logs but not dashboard | Reject-rate as a top-level product health metric |
| T23 · Signal-chip extractor leaves trailing punctuation | Bullet artifact `• …` in rendered answer | Consume trailing punctuation in chip regex; strip leading `^[.,;:]+` |
| T24 · RemoteFeatureFlags cache empty on first launch | `isFoundationModelsEligible` returns false on cold install | Expected on first turn; debug "flag not taking effect" by checking cold cache first |
| T25 · Cohort ramp built before any users exist | Full-week cost for zero safety benefit | Flip flag globally on zero-user launch; keep ramp machinery dormant until 5-figure DAU |

---

## Scenarios

Recipes keyed to symptoms or product moments. Each lists the shortest path using the patterns above.

### S1 · Reject card is live in prod today, we want it gone this week

**Symptom:** users type emotional/open prompts and get "I can only answer timing/decision questions." **Goal:** ship a real answer in 3–5 days without waiting for FM integration.

1. Lock the answer contract (P2, P3). One Swift value type; `composerUsed` enum: `sentenceBank`, `foundationModels`, `retrievalStitch`, `cloud`.
2. Stand up Tier 0 archetype routing. Reuse the heuristics already in your current rejecter as the seed taxonomy.
3. Author Option B: 50–80 fragments covering the reject-card categories, keyed by `(archetype, anchor, mood)`. Two bilingual authors, 2 days.
4. Wire the post-processor (P6) and structured trace (P25).
5. Replace the reject card with Option B rendering. Ship.

Outcome: Data-first now answers. Option A comes later without breaking anything because the contract is already right.

### S2 · Layering Option A on top of a working Option B

**Goal:** raise voice quality on Apple-Intelligence devices without risking regression.

1. Gate A behind `SystemLanguageModel.default.availability` (P14).
2. Reuse the same bundle, same contract, same post-processor. Do not write a "raw model output" path.
3. Design A's prompt from scratch for the bundle-first contract; do not port a cloud prompt (A7).
4. Stage rollout: 5% → 25% → 100%, gated by eval scores + composer-usage mix monitoring (P26).
5. Keep B as the guaranteed fallback forever. A is additive; rollback is "disable A via remote config."

### S3 · The FM output guard keeps rejecting content, users see B even on capable devices

1. Inspect the trace `fallbackReason` distribution:
   - "post-processor: anchor-count" dominates → tighten the A prompt's anchor requirement; add in-prompt examples.
   - "post-processor: forbidden-phrase" dominates → adjust blocklist; re-run eval.
   - "model: guardrail refused" dominates → soften anchor framing or route that archetype to B by design.

### S4 · Crisis keyword inside an otherwise interpretive question

**Input:** "I've been feeling like I want to end things at work, what does my chart say?"

1. Tier 0 safety router fires *before* archetype classification (P23). Static supportive copy + help-line resources rendered in-locale.
2. No composer runs. No chart content rendered.
3. Trace emits `safetyBoundary: crisis`; product dashboard alarms on non-zero daily rates.
4. Follow-up chips include "Talk to a real person" and only soft re-entry into astrology after the user explicitly opts back.

### S5 · Long-tail unusual transit the sentence bank doesn't cover

**Symptom:** B coverage for Chiron returns / 12th-house Saturn transits is thin; fragments read generic.

1. Route these archetypes to Option C as the Tier-1 primary (config change, not code). Same contract, retrieval-stitched wrappers (P21).
2. Keep B as the fallback for C misses.
3. Log `(archetype, anchor)` pairs where B would have fired → backlog for fragment authors. C buys time; B eventually catches up.

### S6 · Retry produces the same answer on Option A

1. Confirm the request ID differs on Retry (P17). Many integrations pass a stable per-session ID.
2. If FM temperature is pinned low for "safety," Retry variance will be cosmetic. Raise temperature for Retry only.
3. If Retry still repeats, the evidence bundle is too narrow. Broaden slot extraction to pull a second relevant anchor.

### S7 · User switches locale mid-session

1. B: re-key fragments in the new locale; do not translate current answers.
2. A: reopen the FM session with the new locale's system prompt (P15 mandates fresh session per request).
3. Grounding line re-formats via the locale-aware ordinal helper (P10).
4. Trace emits locale per answer; eval tooling reports per-locale `groundingScore` separately.

### S8 · Pre-iOS-26 install base is ~40%, product wants "AI-feeling" answers everywhere

1. Do not ship Option A as primary. It will break for 40% of users.
2. Option B is the primary everywhere. Spend the fragment-authoring budget; this is a content problem, not a model problem.
3. Option A becomes an iOS-26 voice upgrade on top, released as "answers feel more natural on newer devices."
4. Track voice-quality metrics separately per pipeline (B-only vs. A-assisted) so regressions don't hide in the aggregate.

### S9 · Bundle is thin (new user, no chart yet)

1. Tier 0 slot extraction returns empty anchors; archetype defaults to `check_in`.
2. Composer chain (any of A/B/C) cannot satisfy the anchor-count assertion (P8).
3. Post-processor emits a *warm onboarding* answer (pre-authored, static) with follow-up chip "Complete your chart for a personal answer." This is the one correct exception to the reject-card ban — gated behind "bundle is empty," not "I don't know the archetype."

### S10 · Eval regression on the composer after an OS update

1. FM behavior can shift with point releases. First move: re-run the pinned eval corpus against Option A.
2. If `groundingScore` drops, adjust the A prompt (anchor emphasis, example count); do not weaken post-processor thresholds.
3. If anchor-invention rate rises, verify the evidence-ref whitelist (P9) is being enforced on A output — a common regression is an A-only code path that bypasses the shared post-processor.

### S11 · "We want FM tool-calling in the composer"

1. Probe the capability on the current runtime (P28). Do not branch on iOS version.
2. If the probe fails or is unstable, stay with Tier-0 bundle-first. Tool-calling is an optimization.
3. If the probe succeeds: scope tools to read-only bundle expanders only; keep the safety router above the tool layer (P23).
4. Every tool call still passes through the universal post-processor (P6) and structured trace (P25).
5. Keep Option B behind the new path for `.modelNotReady`-style failures.

### S12 · "We want an Apple-Intelligence writing-style adapter for brand voice"

**Right call:** bundle is rich, prompt is tight, eval flags voice-flatness as the dominant remaining issue, product is iOS-26-primary, team can own a small ML asset-release loop.

**Wrong call:** under-anchored answers, thin bundle, voice complaints are really about generic grounding. Fix content first (A19).

1. Ship the adapter as an app-bundled signed asset (T22). Version it alongside the app.
2. Adapter trains tone/register only — never anchor logic, safety, or factual content (P27).
3. A/B test `groundingScore`, anchor-invention rate, and voice-quality eval. If adapter-on wins only on voice but loses on anchoring, reject.
4. Keep the no-adapter path working forever.

### S13 · Zero-user launch and operator is asking about the cohort ramp

1. Confirm install-base reality. Zero users = cohort ramp protects nothing.
2. Flip `foundation_models_composer = true` globally. The `SystemLanguageModel.default.availability` gate at the API layer is sufficient (P14).
3. Keep cohort machinery in the codebase, inert. Stage flags off; distinct-ID bucketing dormant; tests green. (T25).
4. Treat internal/beta builds as the soak window instead of a percent cohort.
5. Revisit the ramp at the release that grows install-base past the "a bad day is noticeable" threshold (typically first 5-figure DAU).
