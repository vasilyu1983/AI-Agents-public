# Composing Natural Conversational iOS Experiences

> **For non-iOS surfaces (Android, web browser, Telegram/Discord/WhatsApp/Slack bots, voice, backend) see the platform-neutral master:** [`ai-context-layer/references/conversational-surfaces-cross-platform.md`](../../ai-context-layer/references/conversational-surfaces-cross-platform.md). This file is the iOS-specific deep dive.

How `software-ios-ai-engine`, `ai-rag`, `ai-context-layer`, and `ai-vector-brain` snap together to ship an iOS conversational surface that feels like talking to a person — with Apple Foundation Models (Path A) **or** with a vector-DB-only fallback (Path B). Each is reachable from the same `EvidenceBundle` and the same answer contract.

July 2026 baseline (shipped iOS 26.x): `LanguageModelSession` with stateful instructions + snapshot streaming + tool-calling on iOS 26+ (Apple Intelligence devices, 8 GB+ unified memory); sqlite-vec or ObjectBox HNSW for the on-device retrieval index when FM is unavailable; ai-context-layer's RA13 voice-tier split for sub-300 ms turns. WWDC26 (June 2026) previewed a `LanguageModel` protocol letting third-party cloud providers back the same `LanguageModelSession`, plus a larger 12 GB+ on-device tier — both scoped to iOS/iPadOS/macOS 27, in developer beta only as of this writing; don't design Path A/B around them until 27 ships.

## Contents

- [The Four-Skill Composition](#the-four-skill-composition)
- [The Linking Cheat-Sheet](#the-linking-cheat-sheet)
- [ASCII Flow — iOS Capability Gate and Session Lifecycle](#ascii-flow--ios-capability-gate-and-session-lifecycle)
- [ASCII Flow — LanguageModelSession Lifecycle](#ascii-flow--languagemodelsession-lifecycle)
- [ASCII Flow — Tool-Calling Boundary (Model Narrates, Code Computes)](#ascii-flow--tool-calling-boundary-model-narrates-code-computes)
- [Scenario 1 — Consumer Reflection / Daily Check-in Companion](#scenario-1--consumer-reflection--daily-check-in-companion)
- [Scenario 2 — Regulated-Domain Copilot (Tax, Compliance, Medical, Legal)](#scenario-2--regulated-domain-copilot-tax-compliance-medical-legal)
- [Scenario 3 — Multi-Turn Emotional Companion (Journaling, Coaching, Wellbeing)](#scenario-3--multi-turn-emotional-companion-journaling-coaching-wellbeing)
- [Cross-Scenario Patterns](#cross-scenario-patterns)
- [Anti-Patterns Specific to This Composition](#anti-patterns-specific-to-this-composition)
- [Quick Selector](#quick-selector)
- [Verification Gate for Composed Builds](#verification-gate-for-composed-builds)
- [Sources](#sources)

## The Four-Skill Composition

```
┌─────────────────────── software-ios-ai-engine ───────────────────────┐
│  Tier 0  Intent router + slot extraction + safety gate (Swift)       │
│  Tier 1  Composer  ──┬── Option A: FoundationModels @Generable      │
│                      ├── Option B: sentence bank                     │
│                      └── Option C: retrieval-stitch  ◄──────────┐    │
│  Tier 2  Cloud LLM (explicit opt-in only)                       │    │
└──────────────────────────────────────────────────────────────────┼───┘
                  ▲                                                │
                  │ EvidenceBundle (typed Swift struct)            │
                  │                                                │
┌─────────── ai-context-layer ──────────┐  ┌────── ai-rag ────────┘
│  Per-user state, memory, mood,        │  │  Chunking strategy
│  cross-surface signals, voice-tier    │  │  Hybrid lexical+vector
│  hot/cold split (RA13)                │  │  Grounding contract
└───────────────────────────────────────┘  │  Refusal on missing evidence
                                           └──────────┬───────────┐
                                                      ▼           │
                                            ┌── ai-vector-brain ──┘
                                            │  Server: pgvector (master corpus)
                                            │  On-device: sqlite-vec / ObjectBox
                                            │  (per-user index, offline)
                                            └──────────────────────
```

**Load-bearing rule:** every composer reads from a single `EvidenceBundle` Swift struct. ai-rag designs how that bundle is filled; ai-context-layer owns the per-user state inside it; ai-vector-brain ships the chunks behind it; software-ios-ai-engine renders it as prose. Change retrieval strategy → only the bundle filler changes. Change composer (A↔B↔C) → only the renderer changes. UI never branches per composer.

## The Linking Cheat-Sheet

| Layer | Question to answer first | Owns | Skill |
|---|---|---|---|
| **What corpus?** | Volatile (regulations, prices) or stable (interpretations, symbols, lore)? Refresh cadence? | Backend choice, chunking, embedding-model pinning, on-device vs server split | `ai-vector-brain` |
| **What retrieval?** | Hybrid? Authority-weighted? Top-k? Refusal threshold? Per-user namespace? | Retrieval contract, grounding rules, eval gates | `ai-rag` |
| **What context?** | What per-user state flows in? What memory persists across surfaces? Voice latency tier? | `EvidenceBundle` shape, memory lifecycle, mood/signal flow, P14 consolidation | `ai-context-layer` |
| **What voice?** | Path A (FM) only, Path B (no FM) only, or both? Tier-0 archetypes? Safety routes? | Tier-0 router, composer A/B/C, post-processor, `LanguageModelSession` lifecycle, `@Generable` types, tool-calling boundary | `software-ios-ai-engine` |

---

## ASCII Flow — iOS Capability Gate and Session Lifecycle

```
            user message
                  │
                  ▼
   ┌──────────────────────────────────┐
   │  Tier 0 router (Swift, no model) │
   │  ▸ archetype                     │
   │  ▸ slots                         │
   │  ▸ safety pattern? ─► static copy + helplines, no composer
   │  ▸ locale                        │
   └────────────┬─────────────────────┘
                ▼
       EvidenceBundle struct
                │
                ▼
   ┌─────────────────────────────────────────────────┐
   │  SystemLanguageModel.default.availability       │
   │  switch on the value, NOT on #available         │
   └────┬──────────────────┬────────────────┬────────┘
        │                  │                │
   .available         .modelNotReady     .unavailable
        │             (asset downloading)   (region / storage /
        │                  │               user-disabled / older device)
        │                  │                │
        ▼                  ▼                ▼
   Composer A         Composer B         Composer B or C
   (FoundationModels) (sentence bank)    (sentence bank /
                      THIS TURN ONLY      retrieval stitch)
                      retry A next turn

   Trap T1: do not treat .modelNotReady as permanent — it's transient.
   Trap T3: do not hardcode device lists — iPhone 15 (non-Pro) reports
            .unavailable correctly via the API.
   Trap T2: simulator can report .available but return empty strings —
            physical-device test before claiming Path A works.
```

## ASCII Flow — LanguageModelSession Lifecycle

```
   user opens chat                       user switches user / locale
        │                                          │
        ▼                                          ▼
   open SESSION  ◄────── reuse ────── same user, same locale,
   with Instructions                   same task type
        │
        │  Instructions hold:
        │   ▸ persona / voice contract
        │   ▸ anchor rules
        │   ▸ word budget
        │   ▸ forbidden-phrase floor
        │
        ▼
   turn 1:  respond(prompt + bundle) ─► snapshot stream ─► @Generable type
        │
        ▼
   turn 2:  respond(prompt only)       ─► snapshot stream ─► @Generable type
            (bundle already in context;
             do NOT re-send)
        │
        ▼
   turn 3:  respond(prompt + delta bundle)
            (only changed slots; budget-aware)
        │
        ▼
   user taps Retry  ─► pass NEW requestID/seed (P17) ─► different sample
        │
        ▼
   user switches locale  OR  user switches profile
        │
        ▼
   CLOSE session, OPEN fresh session   (P15: never share session across
                                        accounts, profiles, locales, or
                                        materially different tasks)

   Trap T5: session reuse across users surfaces prior context.
   Trap T16: Retry without seed change yields identical output.
```

## ASCII Flow — Tool-Calling Boundary (Model Narrates, Code Computes)

```
   user: "How much will I owe this quarter?"
                  │
                  ▼
        Tier 0 router classifies: archetype = compute_query
                  │
                  ▼
        EvidenceBundle assembled
        (entity, ytd, lastSync — NO precomputed answer)
                  │
                  ▼
   ┌────────────────────────────────────────────────────────┐
   │ LanguageModelSession(tools: [ComputeImpactTool()])    │
   │ instructions: "ALWAYS call computeImpact for any £     │
   │  figure; never state a number that didn't come from    │
   │  the tool."                                            │
   └──────────┬─────────────────────────────────────────────┘
              │ model decides to call tool
              ▼
   ┌────────────────────────────────────────┐
   │ ComputeImpactTool.call(args)            │
   │                                         │
   │   ┌─────────────────────────────────┐  │
   │   │  Deterministic Swift engine     │  │ ◄── NO MODEL
   │   │  UKTaxEngine.compute(args)      │  │     pure function
   │   │  ──► TaxImpact(typed struct)    │  │     unit-testable
   │   └─────────────────────────────────┘  │
   │                                         │
   └──────────┬─────────────────────────────┘
              │ typed result back to model
              ▼
        model narrates with provenance:
        "Looks like about £842 more this quarter — mostly because
         your July invoices pushed you into the higher-rate band.
         (HMRC SAIM2110, effective 2026-04-06)"
              │
              ▼
        Post-processor:
         ▸ assert all £ figures came from a tool call
         ▸ assert provenance.clause_id appears in answer
         ▸ if assertions fail → fall to Composer B with the
           same TaxImpact struct, rendered through template.

   Same TaxImpact struct flows to both composer paths.
   UI never sees a £ figure that bypassed the deterministic engine.
```

## Scenario 1 — Consumer Reflection / Daily Check-in Companion

**Domain shape:** consumer iOS app with a personal-knowledge surface (mood, journal, profile-derived facts). "Data-first" product promise: no cloud quota by default. Stable interpretation corpus (a few thousand chunks). Light multi-turn.

**ai-vector-brain** ships the *interpretation corpus* twice:
- **Server**: pgvector master with `model_id`, `effective_from`, `content_hash` (operational defaults from `ai-vector-brain/SKILL.md`).
- **On-device**: a sqlite-vec mirror downloaded at install + delta updates. Same content_hashes so citations resolve identically across paths.

**ai-rag** owns the retrieval contract: hybrid FTS5 + `vec0` similarity with RRF, top-k=8, archetype-filtered. Wrappers (P21) keep raw chunks out of the UI.

**ai-context-layer** assembles `EvidenceBundle { profile, derivedFacts, recentSignals, todayDerived, lastMood, archetype }` from local stores. Mood from the last journal entry is a *cross-surface signal* (Stance #9) feeding the chat surface.

**software-ios-ai-engine** runs the composer.

### Path A — Apple Intelligence available

```swift
// One LanguageModelSession scoped to user+locale (P15)
let session = LanguageModelSession(
    instructions: Instructions("""
      You are a thoughtful, warm reflection companion.
      Always begin by acknowledging the user's stated feeling in one short clause.
      Reference 2–3 concrete anchors from the bundle — never invent.
      40–70 words. No bullet lists. No section headers.
      """)
)
let answer = try await session.respond(
    to: bundleToPrompt(evidence),
    generating: ReflectionAnswer.self  // @Generable type
)
```

Session is stateful — turn 2 ("tell me more about that") doesn't re-send the bundle. Snapshot streaming renders character-by-character so the bubble feels alive.

### Path B — no Apple Intelligence (older device, region, or user-disabled)

Composer C (retrieval stitch) wraps the top-2 chunks in a feel-first opener authored by Option B sentence bank:

```
"[feel-ack fragment by mood]. [archetype_wrapper(chunk_1)]. 
 [connective] [archetype_wrapper(chunk_2)]. 
 Grounded in your [anchor_1] · [anchor_2]."
```

No model sampling. Same `ReflectionAnswer` struct. Same UI. Anti-repetition window (P19) rotates fragments so the user doesn't feel the template after session 5.

### Why this feels natural in both paths

The user-perceived voice difference between A and B is small *because B owns voice authoring* and A is bounded by the same anchor whitelist (P9). Naturalness comes from Tier-0 feel-acknowledgment + 2–3 concrete personal anchors — both paths satisfy this.

---

## Scenario 2 — Regulated-Domain Copilot (Tax, Compliance, Medical, Legal)

**Domain shape:** numeric or regulatory accuracy is load-bearing. Wrong answers carry real cost. Knowledge corpus is volatile (laws change, rates change).

**ai-vector-brain** ships an **authority-aware policy brain** (RA11 from `ai-context-layer`): regulatory/standards chunks ingested with `normative_weight`, `effective_from/to`, `clause_id`, cross-reference graph. **Server-only** — too volatile to ship on-device. Reviewer approval before cutover.

**ai-rag** runs hybrid retrieval with an **authority override**: a regulation chunk always out-ranks a guideline chunk regardless of cosine score. **Refusal-on-no-evidence is mandatory** — never invent.

**ai-context-layer** holds `EvidenceBundle { entityProfile, computedState, history[], lastSync, confidenceScore }` from the user's local data sync. P12 just-in-time loading — receipts / records / cases only load when needed.

### Path A — Apple Intelligence available

**The FM is the narrator, never the calculator.** Numeric or regulatory determinations run in deterministic Swift; FM receives the *computed result* via tool-calling and explains it in plain language. This follows the "model for judgment, code for decisions" rule from `coding-behavior.md`.

```swift
struct ComputeImpactTool: Tool {
    let name = "computeImpact"
    let description = "Compute the regulated outcome for the user's current state."
    func call(arguments: ImpactQuery) async -> ImpactResult {
        return DomainEngine.shared.compute(arguments) // deterministic
    }
}

let session = LanguageModelSession(
    tools: [ComputeImpactTool()],
    instructions: """
      You explain {domain} outcomes in plain language.
      ALWAYS call computeImpact for any numeric or regulatory claim.
      Never state a figure or rule that didn't come from the tool.
      Cite the source clause from the bundle's `provenance` field.
      """
)
```

Sample turn (tax domain): "Looks like you'll owe about £842 more this quarter — mostly because your July invoices pushed you into the higher-rate band. (HMRC SAIM2110, effective 2026-04-06)." The £842 came from the tool; the warmth came from the FM.

### Path B — no Apple Intelligence

Composer B (sentence bank) renders the same `ImpactResult` struct through templated prose:

```
"You'll owe about {{amount}} more this quarter. 
 The main driver is {{driverLabel[locale]}}. 
 ({{provenance.clause_id}}, effective {{provenance.effective_from}})"
```

Less warm, equally accurate. Refusal path is identical — both composers emit "I can't tell from your data" when `bundle.confidence < threshold`, never invent.

### Why this scales to regulated domains

The FM never owns numbers or rules; it owns *empathy with the explanation*. Tool-calling is the bridge. Authority-weighted retrieval is the safety net. Refusal-on-no-evidence is the floor. Composer B is fully auditable for compliance review.

---

## Scenario 3 — Multi-Turn Emotional Companion (Journaling, Coaching, Wellbeing)

**Domain shape:** long multi-turn sessions, emotional surface, recurring themes across days/weeks. Naturalness *across sessions* matters more than naturalness *within a turn*.

**ai-vector-brain** ships an **on-device-only** sqlite-vec store: a few thousand domain-symbol or theme chunks bundled in the app. **No server retrieval ever** — fully local. ObjectBox is an alternative when HNSW recall matters at higher chunk counts.

**ai-rag** designs chunk shape: each symbol/theme has 2–3 chunks at different perspectives (classical, modern, somatic / cognitive, behavioral, narrative — pick the perspective axes for the domain) so retrieval can balance voice.

**ai-context-layer** carries **procedural memory** (Stance #16) — the user's *recurring themes* are derived memory written by a P14 sleep-time consolidator. Last-N entries feed retrieval as user-scoped context (P22 chunk-provenance isolation). This is what makes turn 1 on Tuesday feel like a continuation of Sunday.

### Path A — Apple Intelligence

`LanguageModelSession` persists across the entire exploration conversation. Instructions establish the persona once; turn 2/3/4 only send the new user input + a compact `recentThemes` summary (P12 just-in-time loading). Snapshot streaming gives the "thinking and speaking" rhythm research shows raises perceived empathy.

**Critical safety routing (P23):** if the user mentions self-harm during turn 4 of a normal session, **Tier 0 intercepts before the FM session sees it** — static supportive copy, locale-qualified help-line resources, current session is paused. The FM session does not own safety.

### Path B — no Apple Intelligence

Composer C (retrieval stitch) is **primary** here because themes are long-tail. Wrappers vary by archetype to avoid "templated" feel after 3 sessions:

```
reflective_opener[mood] + chunk_excerpt(theme_1, perspective=cognitive)
                       + connective + chunk_excerpt(theme_2, perspective=narrative)
                       + grounding_line(themes=[t1, t2])
```

The procedural-memory layer (recurring themes) is what makes B feel personal across sessions — turn 1 on Tuesday knows the user wrote about boundaries on Sunday and rest on Monday.

### Why this works in both paths

Continuity comes from `ai-context-layer` (recurring-theme memory + sleep-time consolidation), **not** from the composer. The composer just renders. Replacing FM with sentence-bank-over-retrieval downgrades voice fluidity, **not** relational continuity. Many production teams find Path B already produces strong perceived empathy if the theme memory is good.

---

## Cross-Scenario Patterns

These hold across all three scenarios above and any similar conversational surface:

### Pattern — Same bundle, swap composer

The single `EvidenceBundle` Swift struct is the contract between Tier 0 (intent + slot extraction) and Tier 1 (composer). A → B → C fallback is per-request, not per-screen. Capability gate: `SystemLanguageModel.default.availability == .available` (never `#available`).

### Pattern — FM owns voice, tools own truth

In any domain where wrong answers cost real money, real time, or real safety, the FM never computes the answer. It calls a deterministic Swift tool, receives a typed result, and narrates. This is the only way to get FM's natural voice without inheriting hallucination risk on facts.

### Pattern — Server-only / on-device-only / dual

Three corpus deployment shapes:

- **Server-only** (volatile regulatory/policy): RA11 authority-aware brain, reviewer approval gate.
- **On-device-only** (stable, privacy-critical, must work offline): sqlite-vec or ObjectBox bundled with the app, delta updates on release.
- **Dual** (server is master, on-device is mirror): sqlite-vec sync from pgvector with shared `content_hash` so citations resolve identically.

Pick before chunking — the deployment shape drives chunk-size and metadata decisions.

### Pattern — Naturalness comes from composition, not from the model

The four naturalness moves, in order of impact:

1. **Tier-0 feel-acknowledgment** — first sentence acknowledges the stated emotion before any content. Works equally well in A, B, C.
2. **2–3 concrete personal anchors per answer** — names actual facts from the bundle, not section labels.
3. **Cross-session memory** — the surface knows what the user said last week. ai-context-layer's P14 consolidation enables this.
4. **Stateful session + snapshot streaming (Path A only)** — character-by-character bubble feel. Adds polish on capable devices.

Teams that skip step 1 or step 2 and try to make up for it by upgrading the model always disappoint.

### Pattern — Refusal is a feature

Every composer (A, B, C) shares the same refusal threshold from ai-rag's grounding contract. When `bundle.anchorCount < 2` or `bundle.confidence < threshold`, the answer is a warm onboarding / data-gap message with a follow-up CTA to enrich the bundle. Never a reject card; never an invented answer.

### Pattern — Voice-tier split (RA13)

When latency budget is sub-300 ms (voice surface, animated chat, interactive coaching), split memory:

- **Foreground hot tier** — last-N turns, per-user cache, sub-millisecond access.
- **Background cold tier** — vector recall + pre-fetch + P14 consolidation, runs concurrent with the user speaking/typing.

Synchronous embedding lookup per turn overshoots human-conversation budget; the split keeps the surface feeling alive.

---

## Anti-Patterns Specific to This Composition

- **Stuffing the bundle into the prompt.** Violates P16 (token budget). Push it into tool-callable retrieval instead.
- **Letting the FM compute regulated outcomes.** Violates "model for judgment, code for decisions." Always route through a deterministic tool.
- **Different output contracts per composer.** A returns `{text, source}`, B returns `{answer, anchors}`, C returns a string — UI grows composer-specific branches and the integration test surface explodes. One Swift type for all three composers.
- **Treating B/C as "lite mode."** Many production teams ship B-primary forever and add A as polish. B-with-good-fragments outperforms A-with-bad-bundles every time.
- **Server-side retrieval for a "Data-first" promise.** Breaks the offline guarantee the first time the user opens the app on a flight. If the product promises offline, sqlite-vec on-device is mandatory.
- **No content_hash parity between server and on-device chunks.** Citations don't resolve on the path that doesn't own the source. Hash from source bytes; ship the hash with the chunk on both sides.

---

## Quick Selector

| If your app needs… | Start in | Then go to | Composer default |
|---|---|---|---|
| Stable corpus + light personal data + Data-first promise | `ai-vector-brain` (dual sqlite-vec + pgvector) | `ai-rag` (hybrid + per-user namespace) → `ai-context-layer` (RA1 reference) → iOS engine | A on capable, C on others |
| Regulated/volatile knowledge + numeric accuracy | `ai-vector-brain` (RA11 server policy brain) | `ai-rag` (authority-weighted + refusal-on-empty) → `ai-context-layer` (P12 JIT) → iOS engine with tool-calling | A on capable (narrator only), B on others |
| Long multi-turn emotional surface + cross-session memory | `ai-context-layer` (P14 + P15 procedural) | `ai-vector-brain` (on-device only) → `ai-rag` (perspective-balanced retrieval) → iOS engine | A on capable, C on others, B as floor |
| Sub-300 ms voice or interactive coaching | `ai-context-layer` (RA13 voice-tier split) | `ai-vector-brain` (on-device only) → `ai-rag` (pre-fetch) → iOS engine | A streaming on capable, B on others |

---

## Verification Gate for Composed Builds

Before shipping any conversational iOS surface composed from these four skills:

- The `EvidenceBundle` Swift type is one canonical struct; every composer (A/B/C) emits the same answer type.
- Capability gate is `SystemLanguageModel.default.availability`, not `#available` or device lists.
- Refusal threshold from ai-rag is enforced identically in A, B, and C.
- Every chunk row carries `content_hash`, `embedding_model`, `effective_from`, and (for multi-tenant) namespace.
- Tier-0 safety routing fires before any composer; clinical/crisis copy is locale-qualified and bypasses the FM session entirely.
- Cross-session memory writes happen in a P14 background job, not inside the synchronous compose path.
- Persistence parity: every UI-visible field (answerSource, grounding, anchors) is also persisted inside the row, not only in the HTTP envelope.
- Path B works on a brand-new install with no Apple Intelligence and no network. Run this as a CI integration test.

## Sources

- Apple — [Foundation Models framework newsroom](https://www.apple.com/newsroom/2025/09/apples-foundation-models-framework-unlocks-new-intelligent-app-experiences/) (Sept 2025)
- Apple Developer — [FoundationModels documentation](https://developer.apple.com/documentation/FoundationModels)
- WWDC25 — [Meet the Foundation Models framework](https://developer.apple.com/videos/play/wwdc2025/286/) (tool-calling, instructions)
- WWDC25 — [Deep dive into Foundation Models](https://developer.apple.com/videos/play/wwdc2025/301/) (snapshot streaming, session lifecycle)
- Apple ML Research — [On-Device and Server Foundation Models updates](https://machinelearning.apple.com/research/apple-foundation-models-2025-updates)
- Apple ML Research — [Introducing the Third Generation of Apple's Foundation Models](https://machinelearning.apple.com/research/introducing-third-generation-of-apple-foundation-models) (June 2026 — iOS/iPadOS/macOS 27, developer beta at time of writing)
- WWDC26 — [What's new in the Foundation Models framework](https://developer.apple.com/videos/play/wwdc2026/241/) (`LanguageModel` protocol, third-party providers, image input)
- Apple Security Research — [Private Cloud Compute](https://security.apple.com/blog/private-cloud-compute/) (guarantees: stateless computation, no privileged runtime access, non-targetability, verifiable transparency)
- [sqlite-vec](https://github.com/asg017/sqlite-vec) — vector search SQLite extension
- [sqlite-rag](https://github.com/sqliteai/sqlite-rag) — hybrid FTS + vector + RRF on SQLite
- [ObjectBox iOS](https://objectbox.io/swift-ios-on-device-vector-database-aka-semantic-index/) — first on-device vector DB for Swift
- [SVDB](https://github.com/Dripfarm/SVDB) — Swift Vector Database
- [NVIDIA PersonaPlex](https://research.nvidia.com/labs/adlr/personaplex/) — full-duplex conversational AI with persona/empathy
- [CHI 2026 — Breakdowns in Conversational AI: Interactional Failures](https://dl.acm.org/doi/10.1145/3772318.3791186)
