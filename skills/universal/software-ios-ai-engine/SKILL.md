---
name: software-ios-ai-engine
description: "Design local AI engines for iOS. Use when wiring Apple Foundation Models, local classifiers, extraction, summarization, grounded answers, and cloud fallbacks."
version: "1.2"
last_validated: 2026-07-11
---

# Local AI Engine on iOS

Use this skill when an iOS app should run useful AI behavior locally before spending cloud quota: Apple Foundation Models, deterministic local NLG, local retrieval stitching, local classifiers, extraction, summarization, tagging, rewrite helpers, and tool calls into app state. The common constraint is not "make chat smarter"; it is **pick the right local engine, shape the data contract, gate capability correctly, and keep cloud as an explicit upgrade or fallback**.

A major scenario is a rich, per-user structured context bundle (profile data, planning cache, knowledge chunks, activity ratings, journal themes, mood/energy, etc.) that needs to produce a real answer without cloud quota. In that case, the fix is never "make the reject card nicer." The fix is adding a local **Composer** tier between intent routing and cloud fallback.

This skill is for iOS product surfaces and local app-engine design. For pure retrieval/chunking/grounding strategy upstream of the local engine, route to `ai-rag`. For model serving/quantization tradeoffs beyond Apple platform APIs, route to `ai-llm-inference`. For evaluation of generated or extracted output, route to `ai-evals-observer`.

## Quick Reference

### Local Engine Patterns

| Pattern | Local engine | Best for | Fallback |
|---|---|---|---|
| **Structured generation** | Apple Foundation Models + `@Generable` | Short prose, extraction, classification, tagging, typed transformations | Deterministic local logic or cloud opt-in |
| **Deterministic NLG** | Sentence bank / templates / rules | Auditable answers, safety copy, older devices, per-locale consistency | Retrieval stitch or cloud opt-in |
| **Retrieval stitch** | Local top-k chunks + wrappers | Grounded explanations from existing knowledge chunks | Sentence bank or cloud opt-in |
| **Local classifier** | Regex, NaturalLanguage, embeddings, FM enum output | Routing, intent, entity extraction, safety boundaries | Conservative default route |
| **Tool-backed local model** | FM tool calling into app state | Model decides when it needs app data | Pre-fetch compact data if tool overhead is too high |
| **Reusable app AI foundation** | `LocalAIEngine` facade + deterministic fallback + optional Foundation Models | New iOS app skeletons that need AI-ready architecture before the first AI feature ships | No-op or sentence-bank engine |
| **Local semantic/vector search** | Natural Language embeddings, local vector table, or bundled retrieval units | User notes, settings, local knowledge, short document sets, app help, offline search | Server vector brain when corpus or sharing exceeds device scope |

For non-answer tasks, use [references/local-ai-task-patterns.md](references/local-ai-task-patterns.md) before reaching for the answer-composer references.
For reusable app foundations, use [references/foundation-models-app-skeleton.md](references/foundation-models-app-skeleton.md) and [references/on-device-vector-retrieval-ios.md](references/on-device-vector-retrieval-ios.md).

### The Three-Tier Architecture for Answer Surfaces

| Tier | Engine | Responsibility | Cost / latency |
|---|---|---|---|
| **0. Intent router** | Deterministic regex + lightweight classifier | Detect archetype (`reflect` / `interpret` / `guide` / `clarify` / `check_in`), extract slots, assemble evidence bundle | Measure routing and retrieval separately; local compute |
| **1. Composer** | One of: Foundation Models (A), sentence bank (B), retrieval stitch (C) | Render the bundle into prose within the product word budget | Measure cold/warm device latency; local compute |
| **2. Cloud LLM** | Any cloud model your backend calls, chosen per product policy (not this skill's concern) | Deeper synthesis, multi-turn reasoning, novel question types | Measure end-to-end latency; check provider quota/pricing |

Local-first mode owns Tiers 0 + 1. The explicit cloud-escalation control is Tier 2. If Tier 0 routes correctly but Tier 1 does not exist, a genuine question becomes a rejection card instead of an answer — that gap is what the Composer tier exists to close. See [references/three-tier-architecture.md](references/three-tier-architecture.md).

### Pick the Composer Strategy

Three engines. You usually ship more than one, with a fallback chain.

| | Option A — Foundation Models | Option B — Sentence Bank | Option C — Retrieval Stitch |
|---|---|---|---|
| **Engine** | Apple `FoundationModels` system model (iOS 26+) | Hand-curated prose fragments keyed by `(archetype, anchor, mood)` | Top-k retrieval over your knowledge chunks + boilerplate wrappers |
| **Voice quality** | Natural, conversational, feels personal | Curated, brand-consistent, can feel patterned over time | Mechanical, readable, "summary-ish" |
| **Delivery dependency** | Prompt, capability and regression evaluation | Fragment coverage and localization | Existing retrieval and source quality |
| **Deterministic** | No — sampling | Yes — fully auditable | Mostly — retrieval is stable |
| **Offline** | Yes | Yes | Yes if retrieval is local |
| **API billing** | No cloud API charge for on-device inference | None | None if retrieval is local |
| **Localization** | Needs multilingual prompt + per-locale QA | Per-locale fragment files (standard l10n flow) | Depends on knowledge chunks' language coverage |
| **Device requirement** | Check runtime availability and active locale; avoid hardware allowlists | Any supported app device | Any supported app device |
| **Risk** | Hallucination if prompt underconstrained | Repetition; "feels canned" after N sessions | Chunk quality leaks into answer quality |
| **Deep dive** | [references/option-a-foundation-models.md](references/option-a-foundation-models.md) | [references/option-b-sentence-bank.md](references/option-b-sentence-bank.md) | [references/option-c-retrieval-stitch.md](references/option-c-retrieval-stitch.md) |

**Default recommendation for consumer iOS apps:** Ship a deterministic local baseline plus Apple Foundation Models as an upgrade on capable devices. For answer surfaces, that usually means **B + A together, with B as universal fallback.** B closes the reject-card bug immediately; A then upgrades voice quality on iOS 26+ devices using the same bundle and the same `{ answer, grounding }` output shape. C is useful as a last-chance Tier-1 before falling through to Tier 2 or to deterministic safety copy. Rationale: [references/three-tier-architecture.md](references/three-tier-architecture.md#default-deployment).

### On-Device vs. Server: the Judgment Call

Don't default to "on-device because it's private" or "cloud because it's smarter" — decide per feature against four axes, in this order:

1. **Privacy ceiling.** If the promise is "your data never leaves the device," keep inference and retrieval local. Private Cloud Compute (PCC) is off-device too; allow it only within the product's disclosed transmission policy and consent flow.
2. **Capability ceiling.** Evaluate the system model on the actual task before choosing cloud. For longer context or stronger reasoning, iOS 27 adds `PrivateCloudComputeLanguageModel` and the `LanguageModel` provider protocol. PCC requires eligibility and a managed entitlement; read [Apple's PCC guide](https://developer.apple.com/documentation/foundationmodels/adding-server-side-intelligence-with-private-cloud-compute) and [access terms](https://developer.apple.com/private-cloud-compute/) before adoption, and inspect `quotaUsage` at runtime. Do not count it as unlimited capacity.
3. **Latency and cost.** Measure cold/warm completion, first-token latency, retrieval and thermal pressure on target devices. Choose a product deadline from those results; on-device inference consumes energy and memory even without cloud API billing. Cloud needs separate network, quota and pricing measurements.
4. **Device-fleet reality.** Measure model availability by OS, locale and device cohort. Keep a deterministic fallback for unavailable, disabled, downloading and unsupported-language states rather than predicting capability from RAM or chip names.

For image attachments, system tools, Core ML and MLX choices, load [the engine decision paths](references/local-ai-task-patterns.md#engine-and-modality-decision-paths) at workflow step 2. For OS-specific context queries and error handling, load [Option A](references/option-a-foundation-models.md#context-window-budgeting) before implementation.

**Thermal and battery reality.** Profile under load and cancel calls that exceed the app's measured deadline. Select Option B instead of leaving the UI waiting; a deadline expiry is an app decision, not a universal Foundation Models timing guarantee.

**Graceful degradation is not optional.** Every feature that uses Option A needs a tested B/C path for: OS below 26, Apple Intelligence disabled, region/language not yet supported, model asset still downloading, and thermal/latency ceiling exceeded. Ship the fallback first; layer A on top.

### Non-Negotiables (apply to every local AI engine)

- **Typed output contract.** The UI or caller reads a Swift value, not raw model prose. For answer composers that means `{ answer, grounding, followUps[], safetyBoundary }`; for extraction/classification it means a typed enum/struct.
- **Capability gate before use.** Apple Foundation Models requires `SystemLanguageModel.default.availability == .available`; local fallbacks must work when the model is unavailable, disabled, not ready, or unsupported for the active language.
- **Context-window budget is real.** Read runtime capacity and count the whole session with APIs available on the target OS; follow the [OS-specific lookup](references/option-a-foundation-models.md#context-window-budgeting), with measured response headroom.
- **Local does not mean unvalidated.** Run post-processors or validators after model output: schema, anchors, enum membership, safety boundaries, word count, locale, and forbidden phrases as applicable.
- **Cloud is explicit unless product policy says otherwise.** Do not silently spend quota or transmit sensitive context after promising local-first/offline behavior.
- **Do not make AI own deterministic chrome.** Fixed labels, diagram/chart controls, category or field names, and help-sheet UI copy belong in the app localization pipeline, not in runtime model output. The engine can return structured facts or prose; SwiftUI still owns localized fixed UI and visual inspection behavior.

For answer composers specifically:

- **Answer shape is the same contract across A / B / C.** The UI reads `{ answer, grounding, followUps[], safetyBoundary }` — composers differ only in how they fill it.
- **Grounding line is mandatory and concrete.** "Grounded in your Week 3 progress · Tuesday journal entry · Goal: consistency" — names the actual anchors, not section labels like "Progress data · Plan snapshot."
- **Feel acknowledgment must land before interpretation.** For any archetype whose Tier 0 intent is `emotional_support`, the first sentence acknowledges the user's stated feeling before any framework-specific framing. No composer is allowed to skip this.
- **No invented facts.** The composer can only reference entities, numbers, themes, or chunks that appear in the evidence bundle. A composer that references a data point not present in the bundle is broken — this applies equally to Foundation Models, sentence banks, and retrieval stitchers.
- **Safety boundary overrides everything.** Crisis-pattern detection in Tier 0 redirects to a static supportive message with help-line resources; no composer runs. Clinical-adjacent language downgrades tone but does not bypass the domain interpretation. See [references/intent-router-patterns.md](references/intent-router-patterns.md#safety-routing).
- **Word budget is explicit.** A 40–70-word chat bubble is an illustrative product default; configure and validate the answer surface's actual budget. Classification and extraction use their typed-field limits instead.
- **Grounded observability.** Every composed answer emits a structured trace: which archetype routed, which evidence refs were selected, which composer ran, confidence, latency. Required for eval-observer regression gates.
- **Structured visualization contract.** If the answer surface feeds a deterministic diagram, return typed anchors and explanation IDs separately from prose. Do not ask the composer to decide zoom, filters, chart labels, or localized UI strings; those are native UI responsibilities with their own tests.

Foundation Models begins at iOS 26; newer provider, attachment and error APIs require iOS 27 guards as well as model availability checks. Do not infer third-party access from an Apple research model announcement. Test prompts on each supported OS/model revision because system model updates can change behavior.

## App Store Review For AI-Generated Content

A local AI engine generates user-facing content, which puts the app inside several App Store Review Guidelines that have nothing to do with model quality. Treat these as build-time constraints, not a pre-submission afterthought. Full pass/fail map: [../software-ios-design/references/app-review-guidelines-map.md](../software-ios-design/references/app-review-guidelines-map.md).

- **4.3(b) saturated-category gate — run this before scoping the engine.** Apple's Guideline 4.3(b) names saturated categories it rejects "unless they offer a meaningfully different or improved experience" (the named list includes dating, flashlight, sound effects, wallpaper, simple timers, and fortune telling among others — check the live guideline, since the named list changes). Adding AI does **not** clear this bar; it raises it. Do **not** propose, and do not let an operator ship, an app whose pitch reduces to "an AI wrapper on a commodity category" with generic output and a Day-1 paywall. To pass: ship genuinely interactive, personalized, native functionality (accurate domain computation, on-device interpretation grounded in the user's own data, history/journaling, data-tied notifications), give substantial free value before any paywall, and differentiate from category clones in a way a reviewer sees in 30 seconds. If the app's category is named in 4.3(b)'s saturated list, say so up front and state the meaningfully-different-experience requirement before proposing features.
- **1.2 governs UGC/social surfaces.** Shared generated content needs the applicable filtering, reporting, user blocking and contact mechanisms in [the live guideline](https://developer.apple.com/app-store/review/guidelines/#user-generated-content). Do not attribute a blanket private-generation requirement to 1.2. Keep reviewed static crisis/refusal copy as the engine's safety design.
- **2.5.2 — downloads and behavior.** Apple prohibits downloaded executable code that introduces or changes app functionality. [Core ML supports runtime model downloads](https://developer.apple.com/documentation/coreml/downloading-and-compiling-a-model-on-the-user-s-device), but that is not blanket review approval for every weights/prompt/schema update. Keep executable schemas in the app bundle and review content/model updates against the app's disclosed functionality.
- **5.1.1 — generated content is still data.** If generated answers are stored or transmitted (cloud Tier 2), the App Privacy labels and permission strings must reflect it, and account-bearing apps need in-app account deletion (5.1.1(v)).
- **5.1.2(i) — disclose third-party AI, including your own Tier 2.** Apple's guidelines require clear disclosure, and explicit permission, before sharing personal data with third parties — a category that explicitly names third-party AI. If Tier 2 forwards the evidence bundle or question text to any cloud model (yours or a vendor's), the consent flow and privacy copy must say so before the first send, not just in a buried privacy-policy paragraph.

## Patterns, Anti-Patterns, Known Traps, and Scenarios

Full catalog (P1–P28, A1–A22, T1–T25, S1–S13) in [references/patterns-antipatterns-traps-scenarios.md](references/patterns-antipatterns-traps-scenarios.md). Key entries inline:

**Architecture (P1–P6, A4–A7):** every composer emits a single shared Swift value type; compose from a typed `EvidenceBundle`, never raw text; run the universal post-processor (anchor validator → word-count trimmer → forbidden-phrase filter) after every composer including Option A.

**Option A (P13–P17, P27–P28):** use OS guards for API symbols, runtime gates for model capability, and the dual-SDK context/error map in Option A. Write a bundle-specific prompt rather than porting a cloud prompt unchanged.

**Safety (P23–P24, A2, A16):** crisis patterns bypass all composers; cloud Tier 2 is an explicit user-visible CTA, never a silent fallback; safety routing is a Tier-0 decision, not a prompt instruction to the FM.

**Persistence (A21–A22):** persist composer identity and grounding with the answer in whichever store the app uses. Verify write → reload preserves the shared contract; transient transport metadata is insufficient.

**Top traps by day-cost:** T2 (simulator lies about FM availability — always test on physical device); T6a (tool/schema overhead omitted from the measured token budget); T13 (trimmer removes grounding line); T19 (fallback-chain silent regression when feature flag flips); T25 (cohort ramp built before any users exist).

## Core Workflow

1. **Name the local task.** Is it classification, extraction, summarization, rewrite, tagging, grounded answer composition, or tool-backed action planning? Do not start with "chat" unless the user-facing surface is actually chat.
2. **Choose the smallest reliable local engine.** Regex/rules for high-precision routing, NaturalLanguage/embeddings for lightweight semantic matching, sentence bank for audited prose, retrieval stitch for existing knowledge chunks, Apple Foundation Models for structured generation or natural language synthesis. Use [engine and modality decision paths](references/local-ai-task-patterns.md#engine-and-modality-decision-paths) when custom models or images are required.
   - For reusable app skeletons, create the `LocalAIEngine` interface and deterministic fallback even if Foundation Models ships later.
3. **Lock the typed contract.** Write the Swift struct / enum the caller consumes. Use `@Generable` for Foundation Models where the model should emit the type directly; use deterministic structs for rule/template paths. For non-answer examples, see [references/local-ai-task-patterns.md](references/local-ai-task-patterns.md).
4. **Build routing and bundle assembly first.** Classifier, slot extraction, evidence bundler, safety boundary, and locale run unchanged whether A / B / C composes. [references/intent-router-patterns.md](references/intent-router-patterns.md).
5. **Ship a deterministic local fallback.** Even if Apple Foundation Models is primary, local rules/sentence bank/retrieval stitch must cover unavailable devices, model-not-ready states, validation failures, and older OS versions.
6. **Layer Apple Foundation Models on capable devices.** Same input bundle, same output contract, availability gated by `SystemLanguageModel.default.availability`. [references/option-a-foundation-models.md](references/option-a-foundation-models.md).
7. **Use retrieval stitch where knowledge already exists.** For long-tail interpretation or documentation-backed answers, prefer local top-k chunks plus wrappers over asking the model to invent missing knowledge. [references/option-c-retrieval-stitch.md](references/option-c-retrieval-stitch.md).
8. **Wire cloud as explicit opt-in or documented policy fallback.** Tier 2 spend/transmission must be visible when local-first/offline is a product promise.
9. **Instrument the eval loop.** Per local task: engine used, latency, validation result, fallback reason, safety boundary, locale, and task-specific quality metrics.

## Craft Checklist

Before marking a local AI engine pass as complete, verify:

1. **Contract conformance** — output matches the locked Swift type; no composer-specific fields leak into the UI.
2. **Anchor count** — every answer names at least 2 concrete anchors from the evidence bundle (a specific data point, phase, metric, or knowledge chunk). No generic filler that could apply to anyone.
3. **Feel-first for emotional intent** — first sentence acknowledges the stated mood before any domain-specific framing.
4. **Ordinal formatting** — any ordinal shown to the user (e.g. "1st / 2nd / 3rd / 4th") never renders "1th / 21th". Centralize via a single `formatOrdinal` helper (server *and* client); invariant-test it.
5. **No forbidden phrases** — blocklist vague reassurance stock phrases ("trust the process," "it will all work out") and any composer-specific stock phrasing that shows up too often in logs.
6. **No invented facts** — assert the answer text only mentions entities, numbers, or attributes present in the bundle. An offline validator should catch this before the text reaches the UI.
7. **Configured word budget** — for answer surfaces, validate the chosen length (40–70 words is an illustrative default); reject or revise without trimming away anchors. Non-answer tasks validate their field-specific limits.
8. **Locale cleanliness** — every user-facing string goes through l10n. Composer output generated in the user's locale (not translated post-hoc).
9. **Retry and replay** — request IDs identify traces, not sampling. Choose supported seeded sampling for same-model replay; use a new seed for Retry when variation is desired, then evaluate variation. A fresh session alone guarantees neither a new answer nor cross-OS reproducibility.
10. **Safety routes mapped** — crisis patterns bypass all composers; clinical patterns soften tone; emotional patterns trigger the feel-first rule.
11. **Grounding line passes the "anchor test"** — if you strip it out of the answer, could a careful reader reconstruct "which two or three facts this was based on"? If it's ambiguous ("your overall energy"), it fails.
12. **Accessibility** — answer bubble + grounding line combine as one VoiceOver element; action row items announce individually; follow-up chips announce as buttons with hint. See [software-ios-design](../software-ios-design/SKILL.md) craft patterns.
13. **Replay in tests** — deterministic composers accept injected time/randomness; model-backed composers use recorded responses for unit tests plus live per-OS regression cases. Keep UI integration separate from validation.
14. **Non-answer task coverage** — classification, extraction, summarization, tagging, rewrite, search, and tool-backed actions use the smallest reliable local engine, typed outputs, validators, and fallback rules from [local-ai-task-patterns.md](references/local-ai-task-patterns.md).
15. **Persistence parity** — save and reload output fields, composer identity, schema version and grounding/source references in the app's chosen store; test every composer and migration rather than only the immediate response.

16. **Availability and budget** — exercise unavailable-model, unsupported-locale, context overflow and timeout paths on the oldest supported OS and iOS 27. Use the dual-SDK error map; validate complete session budgets, not just prompts.
17. **Safety, consent and trace** — test crisis routing before composition and explicit cloud transmission; trace `{ archetype, composerUsed, anchorCount, wordCount, latencyMs, groundingScore, fallbackReason?, refusalReason? }` without raw sensitive input.
18. **Local-first fallback** — verify the target local-first path answers an emotional / open question with real prose, not a reject card; the "cloud upgrade" affordance is explicit.
19. **Runtime evidence** — record OS, device, Xcode and physical-device/simulator status for regressions. Check current Apple docs when changing language, context, tools or error handling; treat community claims as hypotheses until reproduced. Run live quality cases after each supported OS/model update.

## Route Elsewhere

- [`software-ios-design`](../software-ios-design/SKILL.md) — for the *surface* that renders the answer (bubble, grounding line, action row, follow-up chips, detents).
- [`software-ios-native`](../software-ios-native/SKILL.md) — for broader SwiftUI architecture, Observation, concurrency, and release gates around the composer layer.
- [`ai-rag`](../ai-rag/SKILL.md) — for the retrieval stage feeding the evidence bundle (chunking, hybrid search, reranking, freshness).
- [`ai-context-layer`](../ai-context-layer/SKILL.md) — for the durable per-user context store that assembles the bundle.
- [`ai-prompt-engineering`](../ai-prompt-engineering/SKILL.md) — for the prompt contract inside Option A (voice, anchor rules, anti-hallucination).
- [`ai-llm-inference`](../ai-llm-inference/SKILL.md) — for deeper model-choice tradeoffs (Apple FM vs an MLX-served open-weight model vs cloud), tokenization, and inference perf.
- `ai-evals-observer` agent/team — for regression gates and trace grading of composer output when available.
- [`software-ios-runtime-debugging`](../software-ios-runtime-debugging/SKILL.md) — when composer output doesn't match source after a build (stale install, not a composer bug).

## Navigation

### Architecture

- [references/patterns-antipatterns-traps-scenarios.md](references/patterns-antipatterns-traps-scenarios.md) — full pattern catalog (P1–P28), anti-patterns (A1–A22), known traps (T1–T25 as decision tables), and scenarios (S1–S13)
- [references/local-ai-task-patterns.md](references/local-ai-task-patterns.md) — non-answer local AI tasks: classification, extraction, summarization, tagging, rewrite helpers, semantic search, tool-backed actions, traps, and scenarios
- [references/three-tier-architecture.md](references/three-tier-architecture.md) — Tier 0 / 1 / 2 decision framework, fallback chain, cost model, default deployment
- [references/intent-router-patterns.md](references/intent-router-patterns.md) — archetype classification, slot extraction, evidence bundling, safety routing
- [references/composition-with-rag-context-vector.md](references/composition-with-rag-context-vector.md) — end-to-end composition with `ai-rag` + `ai-context-layer` + `ai-vector-brain` for natural conversational surfaces, Path A (Apple Foundation Models) and Path B (vector-DB-only) for three generic domain shapes (consumer reflection, regulated copilot, multi-turn emotional companion)
- [references/foundation-models-app-skeleton.md](references/foundation-models-app-skeleton.md) — reusable `LocalAIEngine` facade, Foundation Models service, typed contracts, fallback behavior, and App Intents/tool-call boundaries for generic iOS apps
- [references/on-device-vector-retrieval-ios.md](references/on-device-vector-retrieval-ios.md) — local semantic search and vector retrieval options for iOS: Natural Language embeddings, SQLite/vector tables, bundle mirrors, eval gates, and when to route to `ai-vector-brain`

### Composer Options

- [references/option-a-foundation-models.md](references/option-a-foundation-models.md) — Apple `FoundationModels` framework composer, `@Generable` output, availability gating, guardrails
- [references/option-b-sentence-bank.md](references/option-b-sentence-bank.md) — deterministic fragment composer, authoring workflow, l10n, anti-repetition
- [references/option-c-retrieval-stitch.md](references/option-c-retrieval-stitch.md) — glass-box retrieval-stitching composer, scoring, safety wrappers

### Integration

- [references/swiftui-composer-integration.md](references/swiftui-composer-integration.md) — wiring composers behind a shared protocol, fallback chain, capability gates, observability

### Templates

- [assets/template-foundation-models-service.md](assets/template-foundation-models-service.md) — capability-gated Foundation Models service behind a deterministic fallback
- [assets/template-local-retrieval-tool.md](assets/template-local-retrieval-tool.md) — local retrieval service/tool contract for semantic search and Foundation Models tool calls

### Foundations

- [references/nlg-fundamentals.md](references/nlg-fundamentals.md) — content determination → sentence planning → surface realization, why templates alone fail, why LLM alone over-invents

### Data

- [data/sources.json](data/sources.json) — primary research + vendor-doc sources backing this skill

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
