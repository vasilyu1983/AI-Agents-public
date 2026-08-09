# SwiftUI Composer Integration

## Table of Contents

- [The shared contract](#the-shared-contract)
- [The composer protocol](#the-composer-protocol)
- [The composer chain](#the-composer-chain)
- [Wiring composers at construction](#wiring-composers-at-construction)
- [Capability detection](#capability-detection)
- [Regenerate (user taps Retry)](#regenerate-user-taps-retry)
- [The screen shape](#the-screen-shape)
- [Typing indicator and perceived latency](#typing-indicator-and-perceived-latency)
- [Parallel pre-computation](#parallel-pre-computation-optional-optimization)
- [Error surface in UI](#error-surface-in-ui)
- [Observability per turn](#observability-per-turn)

How to wire Options A, B, and C into a single iOS chat/ask surface behind one protocol, with capability gates, a deterministic fallback chain, and per-turn observability. Code samples are illustrative SwiftUI / Swift 6 — adapt to the project's concurrency model and DI layer.

## The shared contract

All composers emit the same struct:

```swift
struct GroundedAnswer: Codable, Equatable, Sendable {
    let answer: String                 // 40–70 words, flowing prose
    let grounding: String              // "Grounded in your …" one-liner, ≤ 140 chars
    let followUp: String?              // one natural follow-up, ≤ 120 chars
    let archetype: Archetype           // echoes Tier 0 decision
    let composerUsed: ComposerID       // .foundationModels | .sentenceBank | .retrievalStitch
    let confidence: Confidence         // .high | .medium | .low
    let anchorsNamed: [AnchorRef]      // structured, used for validation + UI
}

enum ComposerID: String, Codable, Sendable {
    case foundationModels
    case sentenceBank
    case retrievalStitch
}
```

The UI renders from `GroundedAnswer`. It must not branch on `composerUsed` — the whole point of the shared contract is that the UI doesn't know (or care) which composer ran. Expose `composerUsed` to telemetry, not layout.

## The composer protocol

```swift
protocol GroundedAnswerComposer: Sendable {
    var id: ComposerID { get }

    /// Returns nil if this composer cannot handle the request
    /// (e.g. Foundation Models unavailable, sentence bank doesn't cover the condition).
    /// A nil return means "pass to the next composer in the chain,"
    /// NOT "emit a reject card."
    func compose(
        bundle: EvidenceBundle,
        tier0: Tier0Output,
        regenerate: Bool
    ) async throws -> GroundedAnswer?
}
```

Three concrete implementations: `FoundationModelsComposer`, `SentenceBankComposer`, `RetrievalStitchComposer`. Each is ~200–500 lines, isolated, testable.

## The composer chain

Chain-of-responsibility with explicit ordering:

```swift
actor ComposerChain {
    private let composers: [any GroundedAnswerComposer]
    private let validator: AnchorValidator
    private let safetyFallback: SafetyFallbackComposer

    init(composers: [any GroundedAnswerComposer]) {
        self.composers = composers  // e.g. [A, B, C]
    }

    func compose(
        bundle: EvidenceBundle,
        tier0: Tier0Output,
        regenerate: Bool
    ) async -> GroundedAnswer {
        // Crisis short-circuit — no composer runs.
        if tier0.safetyBoundary == .crisisRedirect {
            return safetyFallback.crisisResponse(locale: tier0.locale)
        }

        for composer in composers {
            do {
                guard let candidate = try await composer.compose(
                    bundle: bundle,
                    tier0: tier0,
                    regenerate: regenerate
                ) else {
                    continue  // composer declined
                }

                switch validator.validate(candidate, bundle: bundle) {
                case .ok:
                    return candidate
                case .failed(let reason):
                    log.warning("composer=\(composer.id) failed: \(reason)")
                    continue
                }
            } catch {
                log.error("composer=\(composer.id) threw: \(error)")
                continue
            }
        }

        // Every composer declined or failed. This is a bug — sentence bank
        // must always produce *something*. Emit a last-ditch safety copy.
        return safetyFallback.genericSupportive(locale: tier0.locale)
    }
}
```

Key properties:

- **Crisis bypass is independent of the chain** — it runs before any composer.
- **Nil return = decline**, distinct from throw. Declines are normal (e.g. Foundation Models unavailable). Throws are failures (log + investigate).
- **Validation happens inside the chain**, not inside each composer — one validator, consistent rules across A/B/C.
- **Last-ditch fallback** when the entire chain exhausts. This should be rare-to-never in practice; if it fires, the sentence bank has a coverage gap.

## Wiring composers at construction

```swift
// In your DI container:
func makeComposerChain() -> ComposerChain {
    var composers: [any GroundedAnswerComposer] = []

    if FoundationModelsAvailability.isAvailable {
        composers.append(FoundationModelsComposer(...))
    }
    composers.append(SentenceBankComposer(...))
    composers.append(RetrievalStitchComposer(...))

    return ComposerChain(composers: composers)
}
```

Availability is checked before chain construction and again before Option A composes, because:

- Apple Intelligence availability can vary by device eligibility, user setting, language/region, and model asset readiness.
- `.modelNotReady` is transient; if it flips to `.available`, recreate or refresh the chain the next time the user enters the screen.
- A small wrapper keeps call sites consistent and prevents stale DI state from hiding an available or unavailable model.

## Capability detection

```swift
import FoundationModels

enum FoundationModelsAvailability {
    static var isAvailable: Bool {
        switch SystemLanguageModel.default.availability {
        case .available:
            return true
        case .unavailable:
            return false
        @unknown default:
            return false
        }
    }
}
```

Keep this wrapper small. Anywhere else in the codebase that asks "can we run on-device inference" must go through this — do not scatter `SystemLanguageModel.default.availability` checks across the app.

## Regenerate (user taps Retry)

The composer chain exposes `regenerate: Bool`. Each composer interprets it:

- **FoundationModelsComposer**: start a fresh `LanguageModelSession` (distinct sampling).
- **SentenceBankComposer**: pass to ranker so cooldowns and anti-repetition pick different fragments.
- **RetrievalStitchComposer**: drop previously-picked chunk IDs from the candidate pool.

The UI emits `regenerate = true` only on Retry; first-load is `regenerate = false`.

## The screen shape

Keep the surface thin — the composer chain does all the work.

```swift
@MainActor
@Observable
final class AskChatStore {
    private let router: Tier0Router
    private let chain: ComposerChain

    var turns: [AskTurn] = []
    var isComposing: Bool = false

    func ask(_ question: String) async {
        isComposing = true
        defer { isComposing = false }

        let tier0 = await router.route(question: question)
        let bundle = await router.assembleBundle(for: tier0)
        let answer = await chain.compose(
            bundle: bundle,
            tier0: tier0,
            regenerate: false
        )

        turns.append(.user(question))
        turns.append(.assistant(answer))

        telemetry.emit(
            .answerComposed,
            archetype: answer.archetype,
            composerUsed: answer.composerUsed,
            anchorCount: answer.anchorsNamed.count,
            wordCount: answer.wordCount,
            latencyMs: ...
        )
    }

    func regenerate(turnId: AskTurn.ID) async {
        // same as ask() but with `regenerate: true`
    }
}
```

The view layer reads `turns`, renders a bubble per assistant turn using the shared `GroundedAnswer` struct. No composer-specific branching in views.

## Typing indicator and perceived latency

Foundation Models p50 is 80–250 ms for short answers; users see "instant." But:

- First call in the process: 400–900 ms (session warmup).
- Thermal throttled / device busy: up to 2 s.

Show a typing indicator after 300 ms, not immediately — premature indicators make fast answers feel slow. Cancel the indicator the moment the answer resolves.

For Option B alone (<5 ms), skip the indicator entirely — it flashes and looks like a bug.

## Parallel pre-computation (optional optimization)

If the device has Foundation Models and you're willing to spend a little compute, kick off Options A and B in parallel, take whichever validates first. Useful for turns where A has historically failed validation; B warms up as a race. Adds complexity; only worth it if telemetry shows A validation failures ≥ 5%.

## Error surface in UI

Errors from the chain never reach the UI — the chain always returns something. What can reach the UI:

- **Network failure assembling the bundle** (retrieval offline): show a retriable error bubble ("Couldn't load your current context — tap to retry"). Don't compose against a stale bundle silently.
- **Tier 0 regex / classifier crash** (hard bug): fail to a generic "Something went wrong, try again in a moment" copy. Log and page.
- **`ComposerChain.compose` threw** (it shouldn't): log, present generic copy. This is a coverage bug, not a user-visible feature.

The UI's job is to render a `GroundedAnswer`. Anything else is plumbing.

## Observability per turn

Emit one structured event per composed answer:

```
answer_composed
  archetype=reflect
  composerUsed=foundation_models
  anchorCount=3
  wordCount=54
  latencyMs=187
  safetyBoundary=supportive_non_clinical
  emotionalIntent=true
  tierBand=premium
  locale=en
  validatorResult=ok
  regenerate=false
  retrievalTopKScores=[0.81, 0.74, 0.62, ...]
```

Dashboards:

- Composer selection rate (should match expected distribution — if A never runs on iOS-26 devices, availability is broken).
- Per-composer validator failure rate.
- Per-archetype answer quality trends (grounding score proxy + user feedback).
- Fall-through rate (A → B, B → C, C → safety copy).
- Regenerate rate per archetype (high regen on `guide` signals decision-answer quality issues).

## Accessibility

Apply the patterns from [`software-ios-design`](../../software-ios-design/SKILL.md):

- `GroundedAnswer`'s answer + grounding line combine as one VoiceOver element with `.accessibilityElement(children: .combine)`.
- Action row icons announce individually; use `.accessibilityLabel` on each.
- Follow-up chips announce as buttons with hint "Ask this follow-up."
- The typing indicator gets `.accessibilityLabel("Composing answer")` so VoiceOver users get feedback.
- Dynamic Type AX5 must not truncate the answer — test every composer's output at the largest size.

## Localization

Every user-facing string in the surface (follow-up chip labels, retry button, typing indicator, safety-fallback copy) is l10n-keyed. The composer output is already localized by the composer (see per-option references).

Don't try to render a `GroundedAnswer` in a different locale than the one that composed it — the grounding line and follow-up will mismatch. If the user switches locale mid-session, re-compose from the new locale.

## Testing

- **Unit tests per composer** — pure functions over bundles and tier0 outputs, snapshot-tested.
- **Integration tests over the chain** — given availability = false for A, chain returns B's output. Given A throws, chain returns B. Given both A and B decline, chain returns C.
- **Fuzz tests on the validator** — random bundle + random composer output → validator never crashes, always returns `.ok` or `.failed(reason)`.
- **UI tests on the screen** — at least one per archetype × happy path, one per crisis redirect, one per A-unavailable path.

## Launch checklist

Before enabling Data-first composition in prod:

- [ ] Shared `GroundedAnswer` type is the only thing the UI reads.
- [ ] Composer chain order is explicit in one place; no conditional logic scattered.
- [ ] Foundation Models availability gated at DI time only.
- [ ] Crisis bypass runs before any composer.
- [ ] Validator runs on every candidate before it reaches UI.
- [ ] Sentence bank catalog covers every archetype's top 5 condition bundles.
- [ ] Regenerate path is tested for each composer.
- [ ] Telemetry event emits once per answer with all fields populated.
- [ ] L10n verified in at least 3 locales (en + long-string + non-Latin).
- [ ] Accessibility verified at Dynamic Type AX5 with VoiceOver on.
- [ ] Cloud pill is visually distinct from Data-first pill; cloud usage counter is surfaced; no silent fallback from Tier 1 to Tier 2.

## Common pitfalls

- **Branching view code on `composerUsed`.** Kills the shared contract and leaks composition into UI.
- **Running the validator inside each composer.** You'll end up with three slightly-different validators that drift.
- **Using the composer chain as an agent loop.** One pass per turn; never recurse.
- **Throwing for "composer declined."** Use `nil`. Throws must mean bugs.
- **Keeping Foundation Models sessions in a global singleton.** Retry sends the same session back; output repeats. Session lifetime = conversation lifetime unless regenerate.
- **Rendering latency-visible typing indicators for B** (which returns in <5 ms). The indicator flashes and looks broken.
- **Emitting telemetry per composer attempt, not per answer.** You lose the "which composer won" signal in the noise.
- **Assuming availability never changes.** The user can disable Apple Intelligence in Settings; the chain must recover on the next screen entry.
