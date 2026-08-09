# Option A — Apple Foundation Models Composer

## Table of Contents

- [When to pick it](#when-to-pick-it)
- [When to skip it](#when-to-skip-it)
- [Availability and capability gating](#availability-and-capability-gating)
- [The composer contract](#the-composer-contract)
- [The session shape](#the-session-shape)
- [Context-window budgeting](#context-window-budgeting)
- [Anchor validation](#anchor-validation-glass-box-around-the-black-box)
- [Locale handling](#locale-handling)
- [Streaming vs one-shot](#streaming-vs-one-shot)
- [Error taxonomy](#error-taxonomy)
- [Determinism and Retry](#determinism-and-retry)
- [Performance budget](#performance-budget)
- [Privacy posture](#privacy-posture)
- [Common pitfalls](#common-pitfalls)
- [Verification](#verification)

On-device ~3B LLM (`AFM Core`) shipped with iOS 26 / iPadOS 26 / macOS 26 as the Foundation Models framework. Free inference, offline, private. This is the composer you want as the primary Tier 1 engine on Apple-Intelligence-capable devices.

**Currency note (July 2026):** everything below describes the shipped iOS 26.x framework. At WWDC26 (June 2026) Apple previewed a third-generation lineup for **iOS/iPadOS/macOS 27** — still in developer beta, not yet on users' devices — adding a larger sparse `AFM Core Advanced` (20B total, 1–4B active parameters, gated to devices with 12 GB+ unified memory), a `LanguageModel` protocol that lets third-party providers back a `LanguageModelSession`, image/Vision input, and free Private Cloud Compute for smaller developers. None of it changes the ~3B model, the availability API, or the token budget described here; treat it as roadmap to plan for, not an API surface to ship against, until 27 GAs.

## When to pick it

- Target audience is on iOS 26+ and the product is iPhone-primary.
- You need natural, conversational voice — not a retrieved snippet, not a realized template.
- You want a composer whose output changes meaningfully on "Retry" without round-tripping to a server.
- You don't want to pay per-answer inference cost and you don't want an AI-quota story intruding on everyday use.
- The product is single-turn or short-multi-turn; you're not building an agent that takes tool calls across minutes.

## When to skip it

- Pre-iOS-26 install base matters (Option B is your fallback; A is additive, not foundational).
- Compliance forbids any neural output in user-facing text (you need Option B's auditability).
- The answer must be byte-identical on every Retry (sampling makes this non-deterministic).
- You need a single composer to run identically across iOS, Android, and web — ship B or C instead.

## Availability and capability gating

```swift
import FoundationModels

let availability = SystemLanguageModel.default.availability

switch availability {
case .available:
    // Primary path — Option A composes.
case .unavailable(.deviceNotEligible),
     .unavailable(.appleIntelligenceNotEnabled),
     .unavailable(.modelNotReady):
    // Fall through to Option B immediately.
@unknown default:
    // Treat as unavailable; Option B composes.
}
```

Never call the framework without the check — `SystemLanguageModel.default.availability` is the only contract that survives across OS updates. `.modelNotReady` is transient (model asset is still downloading); your composer chain should treat it as "use B for now, retry A silently on the next turn."

## The composer contract

Every composer in this skill — A, B, C — emits the same output shape. For Option A, express it as `@Generable`:

```swift
@Generable
struct GroundedAnswer: Codable {
    @Guide(description: "40–70 words of flowing prose. No headers, no bullets.")
    let answer: String

    @Guide(description: "Max 140 chars. 2–3 concrete anchors from the evidence bundle, joined by ' · '. Example: 'Cancer Sun · Progressed Moon in Cancer · Generator Sacral'.")
    let grounding: String

    @Guide(description: "One natural follow-up question in the user's locale, ≤ 120 chars.")
    let followUp: String

    @Guide(description: "One of: reflect, interpret, guide, clarify, check_in. Must match the archetype the router passed in.")
    let archetype: String
}
```

`@Generable` + `@Guide` on the struct is how you get **structured output** out of the on-device model without post-hoc JSON parsing — the framework constrains decoding to match the schema. Don't try to post-parse a free-text completion; you'll lose anchor discipline.

## The session shape

```swift
let session = LanguageModelSession(
    instructions: Instructions {
        """
        You are a supportive astrology and Human Design expert writing to a reader
        whose chart you already know. Write like a thoughtful friend — specific,
        grounded, warm, brief.

        Rules:
        1. 40–70 words. Flowing prose. No headers. No bullets.
        2. Use at least two concrete anchors from the evidence block.
        3. Never mention a sign, planet, house, or HD attribute that is not in
           the evidence block.
        4. For emotional-intent questions, acknowledge the feeling in the first
           sentence before any astrological framing.
        5. Never start with "As a [Sun sign]…" — the reader knows their sign.
        6. No "trust the universe," no "the stars are aligning," no generic closers.
        """
    }
)
```

Then per-turn:

```swift
let response = try await session.respond(
    generating: GroundedAnswer.self,
    options: GenerationOptions(temperature: 0.6)
) {
    Prompt {
        """
        Archetype: \(tier0Output.archetype)
        Locale: \(tier0Output.locale)
        Question: "\(question)"

        Evidence bundle:
        \(bundle.asPromptBlock())

        Safety boundary: \(tier0Output.safetyBoundary)

        Produce a GroundedAnswer.
        """
    }
}

let composed = response.content  // typed GroundedAnswer, not a string
```

Keep instructions static (cached across turns) and put per-turn variables in the prompt. On short-multi-turn sessions the framework caches the instructions KV, so subsequent turns are faster.

## Context-window budgeting

Apple documents the on-device foundation model context window as 4096 tokens per `LanguageModelSession` as of iOS 26 — Apple has stated this ceiling has no near-term path to change, so budget for it, don't wait for it to grow. Budget the whole session, not only the visible user prompt:

- instructions and all prompts
- tool definitions, parameter guides, tool inputs, and tool outputs
- `@Generable` schemas and `@Guide` descriptions
- all model responses in the session transcript

**Don't hardcode `4096`.** Since iOS 26.4, `SystemLanguageModel` exposes a `contextSize` property (available context capacity) and a `tokenCount(for:)` method to measure how many tokens a given prompt/instructions/schema will consume — both are `@backDeployed` to every OS version that ships the framework, so there's no reason to keep a magic-number budget check anywhere in the codebase. Query `contextSize` and `tokenCount(for:)` at the point where you assemble the prompt, and treat `.exceededContextWindowSize` as the safety net, not the primary guard.

For grounded answer bubbles, keep the Option A schema small and feed only the 2-5 highest-value evidence items. If you always need data from retrieval or app state, run that code before the model call and pass the compact result in the prompt instead of exposing it as a tool. Use tool calling only when the model must decide whether or how to call the tool. Remember that tool definitions (name, description, argument schema) are serialized and counted against the same budget the moment a tool is registered on the session — a "short prompt" with three tools can already be tight before the first token generates.

Handle `.exceededContextWindowSize` as a recoverable composer failure: start a new session with a smaller bundle, or fall through to Option B. Do not use `maximumResponseTokens` as the main quality guard; strict caps can produce malformed or partial text.

## Anchor validation (glass box around the black box)

Even with `@Generable`, the model can still mention a placement that isn't in the bundle. Every answer runs through a validator before reaching the UI:

```swift
struct AnchorValidator {
    let bundle: EvidenceBundle

    func validate(_ answer: GroundedAnswer) -> ValidationResult {
        let mentioned = extractAstrologicalEntities(answer.answer)
        let allowed = bundle.allAnchorStrings() // signs, planets, HD attrs, personal day, phase

        let invented = mentioned.subtracting(allowed)
        guard invented.isEmpty else {
            return .failed(reason: .inventedAnchors(Array(invented)))
        }

        guard answer.answerWordCount.isBetween(35, 78) else {
            return .failed(reason: .wordCountOutOfBounds(answer.answerWordCount))
        }

        guard answer.anchorCount >= 2 else {
            return .failed(reason: .tooFewAnchors(answer.anchorCount))
        }

        return .ok
    }
}
```

On `.failed`, the composer chain has three options (pick one explicitly — don't silently retry forever):

1. **Retry A once** with a "Revise: you referenced X which is not in the evidence block" note appended. One retry only.
2. **Fall through to Option B** for this turn, log the failure, surface nothing to the user.
3. **Accept** if the failure is "too few anchors" and the bundle is genuinely sparse; mark confidence low.

## Locale handling

Foundation Models generates in the user's active language *if you pass the question and instructions in that language*. Two patterns work:

1. **Translate the voice contract once per locale** and cache. Pros: lower per-turn overhead. Cons: N versions to maintain.
2. **Keep instructions in English, write the per-turn prompt in the user's locale, and include "Respond in \(localeDisplayName)" as the last instruction line.** Works well for the ~3B model's instruction-following; verify per-locale in eval.

Either way, **run the output validator in the user's locale** — entity extraction for "Cancer" in English is different from "巨蟹座" in Chinese or "رطان" in Arabic. Localize the allowed-anchor list alongside.

## Streaming vs one-shot

For a short 40–70 word answer, one-shot is fine. Streaming makes sense when:

- You want to show a typing indicator → first-token → progressive reveal.
- You're running a longer answer (Tier 2 cloud pill path) where perceived latency matters.

For Data-first Tier 1, one-shot with `@Generable` keeps validation simple; stream only after you've proven anchor quality is stable.

## Error taxonomy

| Error | Cause | Handling |
|---|---|---|
| `.modelNotReady` at session start | Model assets still downloading | Tier 1 falls through to Option B; retry A on next turn |
| Generation timeout (>2s) | Thermal throttling / background pressure | Log, fall through to B, don't block UI |
| `@Generable` decode failure | Model emitted text outside the schema | Retry once with a stricter instruction; then B |
| Output guardrail rejection | Apple's safety filter trimmed content | Fall through to B's static safety copy; don't retry A |
| Anchor validation `.failed` | Invented / missing anchors | Retry once with revision note; then B |
| `availability != .available` at call site | OS updated / user disabled Apple Intelligence | Permanent fallback to B until availability flips |

Instrument every branch — you'll want the rates visible in eval.

## Determinism and Retry

Foundation Models sampling is seeded per-session; repeated calls within the same session with the same input trend toward similar output. If you want Retry to produce a meaningfully different answer, start a **new session** rather than calling `respond` again on the same one. Convention:

```swift
func compose(for request: ComposeRequest, regenerate: Bool = false) async throws -> GroundedAnswer {
    let session = if regenerate {
        LanguageModelSession(instructions: Self.staticInstructions) // fresh
    } else {
        cachedSession ?? makeSession()
    }
    // ...
}
```

This matches user expectation: first tap uses the cached session (fast), Retry starts fresh (different output).

## Performance budget

Typical timings on A17 Pro / M2 iPad:

- First call in process: 400–900 ms (session + first token).
- Subsequent calls same session: 80–250 ms for 40–70 words.
- First call after cold launch, model asset cold: 1–3 s (rare; one-time).

Budget 300 ms for the happy path, with a 1200 ms ceiling before you consider visible latency mitigation (typing indicator, pre-render Option B in parallel, etc.).

## Privacy posture

- Inference runs on-device. No chart, mood, or question text leaves the phone on this path.
- If you were previously streaming user questions to a cloud LLM for the Data-first path, Option A lets you stop — update your privacy policy and copy ("answers composed on your device").
- Apple's [Acceptable Use Requirements for the Foundation Models framework](https://developer.apple.com/apple-intelligence/acceptable-use-requirements-for-the-foundation-models-framework/) restrict how framework output may be reused (including training other models); re-read the live terms before wiring framework output into any eval or fine-tuning pipeline — this is an eval-pipeline consideration, not a product one.

## Common pitfalls

- **Calling the framework before checking availability** — hard crash on non-Apple-Intelligence devices.
- **Putting per-user data in `Instructions`** — instructions are meant to be static; per-turn variables go in `Prompt`. Mixing them breaks instruction-cache reuse.
- **Treating `GenerationOptions(temperature:)` as global** — it's per-request; tune per-archetype if needed (lower for `guide`, slightly higher for `reflect`).
- **Overusing `@Guide` descriptions** — guides consume context-window tokens. Start with clear property names and add short guides only where output quality needs them.
- **Letting `@Generable` answers render without validation** — the model can still invent anchors even with schema constraints. Always validate post-decode.
- **Not localizing the validator** — an English-locale anchor list will falsely reject a correctly-composed non-English answer.
- **Reusing a session across users, locales, or tasks** — you can leak context and pollute grounding. Reuse only within the active user + locale + task boundary; start fresh for Retry.
- **Shipping Option A as the only composer** — pre-iOS-26 devices and users with Apple Intelligence disabled will see the reject card or crash. Option B is a prerequisite, not an option.

## Verification

Before shipping Option A:

- [ ] `SystemLanguageModel.default.availability` is checked on every entry.
- [ ] Unavailable cases fall through cleanly to Option B.
- [ ] `@Generable` schema matches the shared composer contract exactly.
- [ ] Output validator runs on every answer; failures log and retry exactly once.
- [ ] Prompt + schema + tools fit the 4096-token session window with headroom.
- [ ] Per-locale QA in at least en + one long-string (de/ru) + one non-Latin (ja/ar).
- [ ] Retry produces a materially different answer (fresh session).
- [ ] Latency p50 < 300 ms, p95 < 900 ms on target device.
- [ ] Privacy copy reflects on-device composition.
- [ ] Telemetry emits `{ composerUsed: "foundation_models", latencyMs, anchorCount, validatorResult }` per turn.
