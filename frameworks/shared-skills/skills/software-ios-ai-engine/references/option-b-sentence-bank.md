# Option B — Sentence Bank Composer

## Table of Contents

- [When to pick it](#when-to-pick-it)
- [When to skip it](#when-to-skip-it)
- [Structure](#structure)
- [Fragment catalog shape](#fragment-catalog-shape)
- [Composer algorithm](#composer-algorithm)
- [Authoring workflow](#authoring-workflow)
- [Localization](#localization)
- [Anti-repetition](#anti-repetition)
- [Verification](#verification)

A glass-box Natural Language Generation pipeline: hand-curated prose fragments keyed by `(archetype, anchor, mood)` plus connective tissue. No neural model. Fully deterministic, fully auditable, fully localizable.

## When to pick it

- You need a Tier 1 composer **today** and the fragment-authoring cost is lower than a model-integration cost.
- You ship to pre-iOS-26 devices or cross-platform (Android, web) where Option A isn't available.
- You need byte-identical answers for compliance, legal audit, or "show me exactly which fragments were used" traceability.
- You're ok with patterning — your product either (a) is used infrequently enough that users don't see repetition or (b) rotates fragments aggressively.

Ship Option B **even if Option A is your primary composer.** B is the universal fallback for the fallback chain. Without B, the system has no answer when A is unavailable.

## When to skip it

- You need natural voice as a hard requirement and ship-time budget allows Option A immediately.
- Your content taxonomy is too wide to fragment-author (thousands of archetype × anchor combinations).
- The surface is high-engagement per user — daily-driver chat — where fragment repetition becomes visible within weeks.

## Structure

A sentence bank has four pieces:

1. **Fragment catalog** — short prose snippets (10–40 words each), each tagged with the conditions under which it can be used.
2. **Composer** — picks fragments based on the Tier 0 output, assembles them in archetype-specific order, applies transitions.
3. **Slot substituter** — replaces `{sun_sign}`, `{personal_day_number}`, `{hd_type}` with real values.
4. **Quality guard** — checks word count, anchor coverage, forbidden-phrase absence before the answer reaches the UI.

## Fragment catalog shape

Keep fragments in structured data (JSON / YAML / a typed Swift registry), not inline strings:

```json
{
  "id": "sad_day_opener.cancer_heavy",
  "archetype": "reflect",
  "slots_required": ["sun_sign"],
  "slots_optional": ["progressed_moon_sign"],
  "conditions": {
    "sun_sign_in": ["Cancer", "Pisces", "Scorpio"],
    "mood_in": ["low", "sad", "tender"],
    "safety_boundary": "supportive_non_clinical"
  },
  "anchors_named": ["sun_sign"],
  "text_template": {
    "en": "A sad day is allowed. Your {sun_sign} Sun runs deep on water days like this, and that's a feature, not a flaw.",
    "de": "Ein trauriger Tag ist in Ordnung. Deine {sun_sign}-Sonne läuft tief an Wassertagen wie diesem — das ist keine Schwäche, sondern ein Feature."
  },
  "role": "opener",
  "cooldown_days": 14
}
```

Key fields:

- **`conditions`** — the gate for when this fragment is eligible. Composer filters before ranking.
- **`anchors_named`** — which evidence anchors this fragment explicitly names. Composer uses this to guarantee ≥ 2 anchors across the whole answer.
- **`role`** — `opener` / `anchor_1` / `anchor_2` / `action` / `closer`. Composer assembles in this order for each archetype.
- **`cooldown_days`** — per-user cooldown; won't reuse within N days. Prevents obvious repetition.
- **`text_template`** — per-locale strings with slot placeholders. All locales required before shipping.

## Composer algorithm

```
for each archetype, define a role sequence:
  reflect:     [opener, anchor_emotion, anchor_action, closer]
  interpret:   [opener, anchor_chart_fact, anchor_context, bridge]
  guide:       [signal, anchor_timing, anchor_chart_fact, action]
  check_in:    [opener, anchor_chart_fact, action]
  clarify:     → emit clarifying question, skip composer

for each role in the sequence:
  candidates = fragments where role matches AND conditions satisfied AND cooldown expired
  rank by: specificity (more matched conditions = higher) + freshness (longer since last use)
  pick top-1
  substitute slots
  append to answer

post-process:
  join with archetype-specific transitions
  enforce word count 40–70 (trim or retry with shorter-variant fragments)
  assert anchors_named union ≥ 2
  emit grounding line from anchors_named
  emit followUp from followUp catalog keyed to archetype
```

## Authoring workflow

Fragments are **content**, not code. Authored by product + copywriter, reviewed by a domain expert (astrologer, HD practitioner, therapist-adjacent voice coach).

Authoring loop:

1. **Identify the archetype gap** — "we have thin coverage for `reflect` + water-sun + low-mood." Measure from telemetry: archetypes where B falls through to C more than 20% of the time.
2. **Write 3–5 variants per slot** for the target condition bundle. Variants matter — if only one fragment fits a common condition, every user in that condition sees the same sentence.
3. **Localize before merging.** All supported locales in one PR; English-only additions rot the fallback quality for non-English users.
4. **Domain review** — a real astrologer/HD practitioner signs off that the fragment is faithful to the tradition. "This Cancer reference is wrong" gets caught here, not in prod.
5. **Eval against stored bundles** — run the composer over the last N production bundles and eyeball 20 outputs. Regressions are blocked by eval-observer gates.

## Variability and anti-repetition

The biggest product risk is users noticing the same sentences across sessions. Mitigations, ranked by impact:

1. **Cooldowns.** Per-user, per-fragment, 7–30 days depending on distinctiveness of the sentence. Enforce at ranking time.
2. **Variant diversity.** Target 3–5 fragments per `(role, archetype, top-5 common conditions)`. Fewer variants = visible patterning.
3. **Slot randomization.** "A walk, a shower, a text to someone steady" is one form; the fragment can define alternates `["a walk", "a shower", "a call", "a small tidy"]` and pick one per turn.
4. **Connective tissue randomization.** The transitions between fragments are a distinct pool (`" — "`, `". "`, `", and "`, `". Notice that "`). Rotate per turn.
5. **Archetype-aware opening variety.** The opener is the highest-visibility fragment — users see it first, every time. Authoring budget should bias toward more opener variants.

## Localization

Unlike Option A (translation happens inside the model), Option B's translation quality is as good as the authoring investment. Consequences:

- **Locale parity is load-bearing.** Missing fragments in a locale silently make the composer fall through to C or the safety copy. Lint for missing locales in CI.
- **Don't translate post-hoc.** English-written-then-translated fragments lose voice. Author in each locale from the same brief, not from the English string.
- **Non-Latin locales change word count.** The 40–70 word budget is English-centric; Japanese characters vs. English words are not comparable. Set per-locale word/character budgets and measure.
- **Connective tissue localizes too.** Em dashes, ellipses, quotation marks differ per locale (`«»` in French/Russian, `「」` in Japanese). Rotation pools are per-locale.

See [software-ios-design](../../software-ios-design/SKILL.md) and the shared `ai-context-layer` skill for broader localization patterns.

## Safety integration

The sentence bank does **not** write its own safety copy. When Tier 0 flags `crisis_redirect`, the composer short-circuits: no fragment picking, a single static safety response is shown (with crisis-resource CTA) in the user's locale.

For `supportive_non_clinical`, the composer runs normally but filters fragments by `safety_boundary` condition — only `emotional-softened` fragments are eligible. For `emotional_support_intent`, the first-sentence rule adds an `opener.feel_acknowledging` role at the start of the sequence.

## Quality guard

Before the answer reaches the UI:

- **Word count in [40, 70]** — trim by dropping the last optional fragment if over; fall through to C if still over; hard fail at 85 words.
- **Anchor count ≥ 2** — union of `anchors_named` across picked fragments. Fail if ≤ 1.
- **Grounding line ≤ 140 chars** — truncate on whitespace, not mid-word.
- **Forbidden phrases** — "the stars align," "trust the universe," "timing unfolds naturally," plus any product-specific blocklist. Regex match, reject if present (usually a stale fragment that should be deprecated).
- **No double-negation slot failures** — if a slot substitution produced the literal string `"{sun_sign}"` (fragment tagged a slot but user bundle lacks it), reject. This is a catalog bug, log and fall through.

## Testing

Sentence bank composers are **gold for unit testing** because every step is a pure function.

```swift
func testComposer_sadDay_cancerSun_generatorSacral_personalDay6() {
    let bundle = EvidenceBundle.fixture(
        sunSign: "Cancer",
        hdType: "Generator",
        hdAuthority: "Sacral",
        personalDay: 6,
        progressedMoonSign: "Cancer"
    )
    let tier0 = Tier0Output(
        archetype: .reflect,
        safetyBoundary: .supportiveNonClinical,
        emotionalIntent: true,
        locale: "en"
    )

    let answer = composer.compose(bundle: bundle, tier0: tier0, seed: 42)

    XCTAssertEqual(answer.wordCount, in: 40...70)
    XCTAssertGreaterThanOrEqual(answer.anchorCount, 2)
    XCTAssertTrue(answer.answer.contains("Cancer"))
    XCTAssertTrue(answer.grounding.contains("Cancer Sun"))
    XCTAssertFalse(answer.answer.contains("the stars align"))
}
```

With a fixed seed, composer output is deterministic — snapshot-testable. Keep a ~50-case snapshot suite covering all archetype × top-10 condition combinations; a new fragment PR regressing any snapshot must update it explicitly.

## Graceful degradation when catalog coverage is thin

Every condition bundle must reach an answer. If filtering leaves zero candidates for a role, the fallback ladder is:

1. Drop the most specific condition (relax by one axis).
2. Fall back to archetype-default fragment for that role (always-eligible, low specificity).
3. Emit a "safety net" answer per archetype — curated, generic, never hallucinating, but lower anchor count.

Never emit a partial answer with a missing role. Either fully compose or fall through to Option C.

## Instrumentation

Per answer, emit:

- `composerUsed: "sentence_bank"`
- `fragmentIds: [...]` — full list of fragment ids used
- `anchorCount` — union size of `anchors_named`
- `cooldownHits: [...]` — fragments filtered out due to cooldown (spotting drought on common slots)
- `conditionMatchSpecificity` — how specifically the top fragments matched (low specificity = your catalog is thin for this condition)
- `wordCount` — final
- `fallthroughReason?` — if composer failed and handed off to C

These become the authoring backlog for the next sprint: which `(archetype, condition)` pairs see the most cooldown hits or low specificity is your priority fragment list.

## Common pitfalls

- **Inline string fragments in Swift code.** They never get localized, never get reviewed by the copy team, never get cooldown-tracked.
- **One fragment per role per condition.** Every user in that condition sees the same sentence forever. Minimum of 3 variants per hot path.
- **No cooldowns.** Users see "A sad day is allowed" every time they ask an emotional question. Three weeks and they're gone.
- **English-only authoring then translating.** Voice flattens, domain accuracy drops, and the translated fragment ships anyway because no one reviewed it.
- **Treating the sentence bank as a list of answers, not fragments.** Full-answer templates can't recombine with the bundle; the composer needs assembleable pieces.
- **Skipping the anchor-union check.** You emit "grounded" prose that mentions only one actual anchor and buries it in filler.
- **Not versioning the catalog.** When an answer is reported as wrong, you can't trace which fragment shipped at that time.

## Verification

Before shipping Option B:

- [ ] Catalog covers every archetype; no archetype falls through to safety copy under the default bundle conditions.
- [ ] Every supported locale has ≥ 80% parity with English (measured: fragments × locale coverage).
- [ ] Minimum 3 variants per `(archetype, role, top-5 common condition bundles)`.
- [ ] Cooldowns enforced; verified by composing 10 answers for the same test user bundle with time advance and asserting non-repetition.
- [ ] Forbidden-phrase filter runs; test fragment intentionally including a banned phrase triggers reject.
- [ ] Word count and anchor count guards are unit-tested.
- [ ] Snapshot suite covers all archetypes.
- [ ] Domain review signoff logged for every content PR.
