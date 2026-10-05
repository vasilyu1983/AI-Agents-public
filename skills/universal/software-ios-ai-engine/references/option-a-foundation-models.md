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

**Currency note:** everything below describes the shipped framework surface: the availability API, `@Generable` structured output, and runtime context-size queries. Apple revises the model lineup, device eligibility, input modalities, and provider options with OS releases. Before planning against anything newer, check Apple's current Foundation Models documentation and release notes, and treat anything still in beta as roadmap rather than an API surface to ship against.

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

    @Guide(description: "Max 140 chars. 2–3 concrete anchors from the evidence bundle, joined by ' · '. Example: 'Resting HR 58 · 7-day sleep avg 6.1 h · Recovery day'.")
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
        You are a supportive fitness and recovery coach writing to a reader
        whose training data you already know. Write like a thoughtful friend —
        specific, grounded, warm, brief.

        Rules:
        1. 40–70 words. Flowing prose. No headers. No bullets.
        2. Use at least two concrete anchors from the evidence block.
        3. Never mention a metric, workout, goal, or plan attribute that is not
           in the evidence block.
        4. For emotional-intent questions, acknowledge the feeling in the first
           sentence before any training advice.
        5. Never start with "As a [runner]…" — the reader knows their profile.
        6. No "trust the process," no "you've got this," no generic closers.
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

Budget the complete session: instructions, prompts, tool definitions and results, `@Generable` schemas/guides, attachments where supported, responses, and retained transcript. The selected model and runtime determine capacity; do not store an OS-to-token-limit constant table.

| Target OS / build SDK | Capacity and token lookup | Overflow handling |
|---|---|---|
| iOS 26.0–26.3 | A newer SDK exposes `contextSize` with back-deployment before 26.4. Confirm the installed SDK interface; if building with an older SDK, use [TN3193](https://developer.apple.com/documentation/technotes/tn3193-managing-the-on-device-foundation-model-s-context-window) and Instruments to establish a tested budget for that runtime. `tokenCount(for:)` is unavailable on these OS versions. | `LanguageModelSession.GenerationError.exceededContextWindowSize(_:)` |
| iOS 26.4+ within 26 | Read `SystemLanguageModel.default.contextSize`; use the appropriate async, throwing `tokenCount(for:)` overloads for instructions, prompts, tools, schema and transcript. | Same `GenerationError`; prepare a smaller/new session or B fallback. |
| iOS 27+ | Query capacity and token usage for the actual provider; do not carry the older system model's limit into a new OS or PCC/custom-model session. | `LanguageModelError.contextSizeExceeded(_:)`; inspect `contextSize` and `tokenCount`. |

[Capacity API](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/contextsize) and [token-count API](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/tokenCount(for:)) document different availability boundaries. Guard `tokenCount(for:)` with `#available(iOS 26.4, *)`; guard the iOS 27 error types separately. An OS guard does not replace `SystemLanguageModel.default.availability` or `supportsLocale(_:)` checks. Fail to B if measurement or capability lookup fails; do not guess a larger budget.

Keep the schema small and select only evidence needed for the answer. Pre-fetch required app data instead of registering a tool when the model has no meaningful tool-selection decision. Registered tool schemas count even if no tool runs. Reserve measured response headroom and condense into a new session before overflow; retain instructions and relevant evidence when condensing.

Overflow is recoverable once with a smaller session, then B. Use `maximumResponseTokens` for runaway protection rather than prose quality: [Apple warns](https://developer.apple.com/documentation/foundationmodels/generationoptions) that strict caps can produce partial or malformed responses.

## Anchor validation (glass box around the black box)

Even with `@Generable`, the model can still mention a metric or workout that isn't in the bundle. Every answer runs through a validator before reaching the UI:

```swift
struct AnchorValidator {
    let bundle: EvidenceBundle

    func validate(_ answer: GroundedAnswer) -> ValidationResult {
        let mentioned = extractDomainEntities(answer.answer)
        let allowed = bundle.allAnchorStrings() // metrics, workouts, goals, plan day, phase

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

Either way, **run the output validator in the user's locale** — entity extraction for "Recovery day" in English is different from the same term in Chinese or Arabic. Localize the allowed-anchor list alongside.

## Streaming vs one-shot

For a short 40–70 word answer, one-shot is fine. Streaming makes sense when:

- You want to show a typing indicator → first-token → progressive reveal.
- You're running a longer answer (Tier 2 cloud-escalation path) where perceived latency matters.

For local-first Tier 1, one-shot with `@Generable` keeps validation simple; stream only after you've proven anchor quality is stable.

## Error taxonomy

Normalize these SDK errors to app-owned reasons behind availability guards. With a 27 SDK and a 26 deployment target, keep `GenerationError` handling for iOS 26 and catch the separate model/system/session types on iOS 27; do not refer to 27-only symbols in an unguarded path.

| Failure | iOS 26 `LanguageModelSession.GenerationError` | iOS 27 API | App handling / fields |
|---|---|---|---|
| Context overflow | `.exceededContextWindowSize(Context)` | `LanguageModelError.contextSizeExceeded(ContextSizeExceeded)` | Smaller/new session once, then B. New payload reports `contextSize`, `tokenCount`; old `Context` has `debugDescription`, not those counters. |
| Rate limit | `.rateLimited(Context)` | `LanguageModelError.rateLimited(RateLimited)` | B for this turn; respect `resetDate` when provided instead of immediate retry loops. |
| Refusal / safety | `.refusal(Refusal, Context)` / `.guardrailViolation(Context)` | `LanguageModelError.refusal(Refusal)` / `.guardrailViolation(GuardrailViolation)` | Reviewed static safe copy; do not rephrase repeatedly to bypass a guardrail. |
| Unsupported locale | `.unsupportedLanguageOrLocale(Context)` | `LanguageModelError.unsupportedLanguageOrLocale(UnsupportedLanguageOrLocale)` | Check `supportsLocale(_:)`; use localized deterministic output. |
| Guide unsupported | `.unsupportedGuide(Context)` | `LanguageModelError.unsupportedGenerationGuide(UnsupportedGenerationGuide)` | Fix or remove the unsupported guide; B until the schema is tested. |
| Assets unavailable | `.assetsUnavailable(Context)` | `SystemLanguageModel.Error.assetsUnavailable(AssetsUnavailable)` | Availability may change after the preflight; B now, recheck later. `.modelNotReady` is an availability reason, not a generation-error case. |
| Concurrent use | `.concurrentRequests(Context)` | `LanguageModelSession.Error.concurrentRequests` / `.transcriptMutationWhileResponding` | Serialize a session's requests and transcript mutations; cancellation or a new independent session avoids racing. |
| Timeout | No dedicated timeout case documented | `LanguageModelError.timeout(Timeout)` | App deadline/cancellation on either OS; B, record reason. Never infer thermal causation from timeout alone. |
| Capability / content unsupported | No equivalent dedicated cases documented | `LanguageModelError.unsupportedCapability(UnsupportedCapability)` / `.unsupportedTranscriptContent(UnsupportedTranscriptContent)` | Check provider capabilities and attachment support; use a supported text/extraction path. Inspect `capability` for unsupported capability. |
| Decode or validation failure | `.decodingFailure(Context)`; app validator errors | Handle the selected decoding/conversion path separately; no one-for-one `LanguageModelError.decodingFailure` case is documented | Revise once only for a correctable non-safety failure, then B. Log a reason code rather than raw debug text or model content. |

Sources: [26 generation errors](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/generationerror), [27 model errors](https://developer.apple.com/documentation/foundationmodels/languagemodelerror), [system errors](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/error), [session errors](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/error). New model-error payloads carry diagnostic `debugDescription` and `metadata`; neither is automatically safe to publish in telemetry. Unknown cases select the fallback and preserve an internal reason code.

## Determinism and Retry

A request ID is telemetry identity, not a sampling control. Apple's [SamplingMode](https://developer.apple.com/documentation/foundationmodels/generationoptions/samplingmode-swift.struct) supports greedy selection and random sampling with an optional seed. Choose the supported option for the build SDK; a fresh session isolates transcript state but does not guarantee different text. For Retry, vary the seed when using seeded random sampling and evaluate actual variation. For replay, retain model/OS, prompt, options and responses; a fixed seed cannot promise identical output after a system model update.

## Performance budget

No measured timing baseline is bundled here. Use [Apple's Foundation Models instrument](https://developer.apple.com/documentation/foundationmodels/analyzing-the-runtime-performance-of-your-foundation-models-app) to measure cold/warm calls, first-token and completion latency, token use, tool time, memory and thermal pressure on physical target devices. Derive the app deadline and typing-indicator delay from those measurements, record cancellations/fallbacks, and evaluate `prewarm()` where repeated use warrants it. Do not describe illustrative budgets as vendor latency guarantees.

## Privacy posture

- Inference runs on-device. No health data, mood, or question text leaves the phone on this path.
- If you were previously streaming user questions to a cloud LLM for the local-first path, Option A lets you stop — update your privacy policy and copy ("answers composed on your device").
- Apple's [Acceptable Use Requirements for the Foundation Models framework](https://developer.apple.com/apple-intelligence/acceptable-use-requirements-for-the-foundation-models-framework/) restrict how framework output may be reused (including training other models); re-read the live terms before wiring framework output into any eval or fine-tuning pipeline — this is an eval-pipeline consideration, not a product one.

## Common pitfalls

- **Calling before checking availability** — unavailable assets or model state can fail a request; still catch errors after the check because availability can change.
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
- [ ] Output validator runs on every answer; correctable failures retry at most once, refusals/guardrail violations do not retry.
- [ ] Whole-session budget and response headroom are checked with APIs supported by the oldest target OS.
- [ ] Per-locale QA in at least en + one long-string (de/ru) + one non-Latin (ja/ar).
- [ ] Retry variation is evaluated; replay records options and model/OS rather than assuming a session or request ID seeds sampling.
- [ ] Measured latency distributions fit the product deadline on target physical devices; timeout and cancellation fall back.
- [ ] Privacy copy reflects on-device composition.
- [ ] Telemetry emits `{ composerUsed: "foundation_models", latencyMs, anchorCount, validatorResult }` per turn.
