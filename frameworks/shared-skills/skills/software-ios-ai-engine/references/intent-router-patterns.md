# Intent Router Patterns (Tier 0)

## Table of Contents

- [Responsibility](#responsibility)
- [Archetype taxonomy](#archetype-taxonomy)
- [Classification approach](#classification-approach)
- [Slot extraction](#slot-extraction)
- [Evidence bundle assembly](#evidence-bundle-assembly)
- [Safety](#safety)
- [Testing](#testing)
- [Known traps](#known-traps)

The stage that runs before any composer. Classifies the user's question, extracts slots, assembles the evidence bundle, and sets safety flags. Every downstream composer (A / B / C) reads from this output; misrouting here is the most expensive bug in the system.

## Responsibility

```
Tier 0 input:
  { question: String, userContext: PersistentContext, locale: String }

Tier 0 output:
  {
    archetype: Archetype,           // reflect | interpret | guide | clarify | check_in
    slots: Slots,                   // extracted entities: date, person, topic, life-area
    evidenceBundle: EvidenceBundle, // the structured bundle for composers to read
    safetyBoundary: SafetyBoundary, // none | supportive_non_clinical | crisis_redirect
    emotionalIntent: Bool,          // triggers feel-first rule downstream
    locale: String
  }
```

Tier 0 is a **pure function** of inputs. No network calls beyond retrieval (which itself caches). No composer logic. No prose generation.

## Archetype taxonomy

Pick a small, exhaustive set. Start with five:

| Archetype | When it fires | Composer voice |
|---|---|---|
| `reflect` | Emotional check-ins, "how am I," "I feel X" | Feel-first, tender, short, grounding |
| `interpret` | "What does my Moon mean," "why am I," chart-meaning questions | Educational, specific, anchor-heavy |
| `guide` | Timing, decision, "should I," "when should I," "is this a good week" | Directional, signal-led, single clear action |
| `clarify` | Too vague to answer without one follow-up | Single question, no other content |
| `check_in` | Short open prompts where the user just wants a read ("what's up today") | Warm, compact, one chart fact + one action |

Don't pile on archetypes for fine-grained distinctions; the composers can adjust voice within a single archetype. More archetypes = more edge cases.

## Classification approach

Three escalating strategies — **use them in this order**, only moving up when the one below isn't enough:

### 1. Regex + keyword (fast, deterministic, covers 70% of prod traffic)

```swift
let patterns: [Archetype: [NSRegularExpression]] = [
    .reflect: [
        /\b(i (feel|am feeling|felt)|i\'?m feeling|feeling (sad|low|lost|stuck))\b/,
        /\b(a sad day|bad day|tough day|rough day)\b/,
        ...
    ],
    .guide: [
        /\b(should i|when (is|to|should)|is (this|today|tomorrow) a good)\b/,
        /\b(best time to|timing|window)\b/,
        ...
    ],
    ...
]
```

Score across all archetypes, pick the argmax. Keep regexes in data, not code — they're tunable per language and per product iteration.

### 2. Lightweight embedding classifier (adds 50–150 ms, covers the ambiguous middle)

For questions that score ambiguously across regex bands, embed the question (on-device `NaturalLanguage` or `MLEmbedding`, not a cloud call) and nearest-neighbor against a small archetype-anchored set of 20–50 exemplar phrases per archetype.

Only invoke this for ambiguous questions (regex confidence < 0.6). Running it on every query is unnecessary cost for 70% of the traffic that regex handles fine.

### 3. Small on-device LM as classifier (last resort)

Apple's Foundation Models framework can be used as a classifier too — ask it to pick from `["reflect", "interpret", "guide", "clarify", "check_in"]`. Reserve for the long tail where both regex and embedding disagree.

**Do not use the same LM instance for classification and composition in the same turn** — pay the session start cost twice, fight instruction-cache reuse, and create a circular dependency where the composer availability affects routing.

## Slot extraction

After archetype is set, extract entities relevant to the archetype:

- `guide` → time expression, partner/person mention, life area
- `interpret` → chart element mentioned (planet, sign, house), life area
- `reflect` → explicit feeling word (used to tune voice flags)
- `check_in` → rarely slot-heavy; defaults to "today"

Use the iOS `NaturalLanguage` framework's `NLTagger` for PERSON / LOCATION / DATE tags on-device. For chart elements (planet names, sign names), a hand-curated entity list matched case-insensitively is simpler and more robust than a learned tagger.

Slots inform retrieval **filters**, not retrieval scores directly. A `guide` question mentioning "next week" should filter the evidence bundle to transits active in the next 7 days.

## Evidence bundle assembly

The bundle is a typed value type the composer reads. Shape:

```swift
struct EvidenceBundle {
    let natalChart: NatalChart?       // sun, moon, rising, mars, etc.
    let currentTransits: [Transit]     // active within the question's time frame
    let moonPhase: MoonPhase
    let progressedMoon: ProgressedMoon?
    let personalDay: PersonalDayNumber?
    let personalYear: PersonalYearNumber?
    let lifePath: LifePathNumber?
    let humanDesign: HumanDesignProfile?
    let knowledgeChunks: [ScoredChunk] // top-N relevant chunks
    let crossSurface: CrossSurfaceSignals // mood, energy, dream themes, ratings
    let learnedPreferences: [LearnedPreference]
    let cachedPlan: CachedPlanSnapshot?
}
```

Key principles:

- **Everything is typed**, not stringly-encoded. The composer doesn't parse text to find the sun sign.
- **Optionality is honest.** If the user hasn't granted birth time, the bundle has no `humanDesign`; composers must handle this without fabricating.
- **Freshness is explicit.** Each subsection carries `asOf: Date`. Stale subsections are dropped at bundle time, not at composer time.
- **Size budget is per tier band.** Free-tier bundles may omit heavy sections (progressed charts, Human Design detail). Paid-tier gets the full bundle. The composer reads whatever is present; it doesn't know about tier.

Bundle assembly is where retrieval joins the structured-data layer. Route retrieval concerns (chunking, ranking, freshness, reranking) to [ai-rag](../../ai-rag/SKILL.md); Tier 0 just orchestrates the call.

## Safety routing

Two independent gates, both run before archetype classification:

### Crisis redirect

Regex over crisis patterns:

```
kill myself | end my life | suicide | suicidal | self-harm | hurt myself
i (do not | don't) want to live | want to die
hopeless | in crisis | can'?t go on | no way out
abuse | assault | domestic violence | being threatened
```

Any match → `safetyBoundary = crisis_redirect`, `shouldBypassComposer = true`. The UI shows a static, localized supportive message with regionally-appropriate crisis-resource links. **No composer runs.** No astrology content. No chart reference. This is not the place for Data-first prose — it's the place for a single reliable message.

### Clinical adjacency

Softer regex:

```
diagnose | diagnosis | clinical depression | bipolar | ptsd | ocd | adhd | panic attack
therapist | therapy | medication | psychiatrist | mental illness
```

Any match → `safetyBoundary = supportive_non_clinical`. Composer still runs, but:

- Voice softens ("reflective psychology language, not clinical certainty").
- Option B filters to fragments tagged `reflective`, excludes `prescriptive` / `diagnostic`.
- Option A's instructions include "do not diagnose, treat, or imply clinical certainty."
- Option C filters chunks tagged `diagnostic`.

### Emotional-support intent (not a safety gate, a voice gate)

Softer still — everyday emotional language:

```
(sad | down | low | blue | lonely | anxious | scared | afraid | worried)
(stuck | overwhelm(ed)? | burnt?-?out | exhausted | drained)
(hurt | broken | heartbroken | lost | empty | numb)
(confidence | self-?worth | not enough | not good enough)
(i feel | i'?m feeling | feeling (like | so | really))
```

Match → `emotionalIntent = true`. The archetype router biases toward `reflect` (an "I feel lost should I take the job" question becomes `reflect` with a `guide` sub-flag, not pure `guide`). The composer is told to acknowledge the feeling in the first sentence before any astrological framing.

## Voice flags downstream of Tier 0

The composer receives, in addition to archetype + bundle:

- `emotionalIntent: Bool` — feel-first rule.
- `safetyBoundary: SafetyBoundary` — voice softening, chunk filtering.
- `tierBand: TierBand` — controls answer depth (free-tier shorter than paid).
- `timingSensitive: Bool` — set when a `guide` archetype has an active transit in the next 7 days; tells the composer it can lead with a timing signal.
- `archetypeConfidence: Float` — when low, the composer biases toward shorter / safer fragments.

These are **flags**, not instructions. The composer decides how to honor them per option — A interprets them as prompt hints, B reads them as fragment conditions, C uses them as chunk filters. The router doesn't know or care which composer runs.

## Locale detection

For polyglot users, the question's *language* is more reliable than the profile's stored locale preference:

1. Detect language from the question via `NLLanguageRecognizer` with confidence threshold.
2. If confidence ≥ 0.75, respond in the detected language.
3. If confidence < 0.75, fall back to user's stored locale.
4. If stored locale is also ambiguous, English default.

Pass the resolved locale to every composer. Don't let the composer language-detect on its own — inconsistent behavior between A/B/C.

## Testing

Router is a pure function: easy to unit-test.

- **Regex smoke tests** — one per archetype, per key keyword.
- **Safety gate tests** — every crisis pattern triggers `crisis_redirect` and `shouldBypassComposer`.
- **Emotional gate tests** — "I have a sad day" triggers `emotionalIntent`, archetype is `reflect` (not `check_in`).
- **Ambiguity tests** — "should I be sad about this" fires BOTH `guide` intent and `emotionalIntent`; archetype should route to `reflect` because emotional intent wins.
- **Locale tests** — same question in 3 locales routes to the same archetype.
- **Slot extraction tests** — "is next Friday a good day to sign the contract" extracts `date` and `life_area=work`.

## Instrumentation

Per question:

- `archetype`
- `archetypeConfidence`
- `slotsExtracted: [...]`
- `safetyBoundary`
- `emotionalIntent`
- `bundleSize` (bytes or token-equivalent)
- `bundleSections: [present-sections]`
- `retrievalTopKScores: [...]`
- `routerLatencyMs`

High emotional-intent rate with `archetype = guide` signals a router bug (you're ignoring the feel-first signal). Low `archetypeConfidence` rate signals the regex layer needs tuning. High `crisis_redirect` rate relative to session count signals either a real user-support issue (triage) or a false-positive pattern (tune).

## Common pitfalls

- **Letting the composer decide archetype.** Testing disappears; two composers disagree; voice becomes unpredictable.
- **Not gating safety before routing.** A "should I sign this week" question with "I feel hopeless" in the same message should route to crisis, not guide. Safety runs first.
- **Running retrieval before safety gate.** Wasted cost on crisis-redirect turns.
- **Hardcoding English regex in a multilingual product.** Safety patterns must be per-locale; port them from the primary locale explicitly, don't machine-translate.
- **Mixing router state across turns.** Tier 0 is per-turn stateless. Conversation history lives at the composer or session layer, not the router.
- **Stringly-typed output.** `archetype: String` invites typos; use an enum, fail-closed on unknown.
- **Not versioning the router.** When composer behavior changes, you need to know which router version produced the flag set that fed it.

## Verification

Before shipping Tier 0:

- [ ] Archetype taxonomy is documented and every value maps to a composer path.
- [ ] Safety gates run before archetype classification.
- [ ] Crisis patterns have locale parity; emotional patterns have locale parity.
- [ ] Regex confidence thresholds are tuned with a labeled test set (≥ 100 examples).
- [ ] Slot extraction handles the 3 most common slot types per archetype.
- [ ] Evidence bundle assembly drops stale subsections by `asOf`.
- [ ] Tier band gates which bundle sections attach; free-tier bundle size is capped.
- [ ] Router emits structured telemetry per turn.
- [ ] Router is a pure function; no global state, no network beyond retrieval.
