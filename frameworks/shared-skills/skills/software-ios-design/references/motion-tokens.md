# Motion Tokens

Animation curves, durations, and intents as a shared token set. Like spacing and typography, motion needs named tokens so timing stays consistent across screens and `DisclosureGroup`s don't feel faster than sheets.

## Token Table

| Intent | Curve | Duration | Example |
|---|---|---|---|
| Tap press (scale in) | `.easeOut` | 80–100 ms | `ButtonStyle` scaleEffect on `.isPressed` |
| Tap release (scale out) | `.spring(response: 0.25, dampingFraction: 0.75)` | — | ButtonStyle on release |
| Sheet detent change | `.spring(response: 0.45, dampingFraction: 0.82)` | — | Peek → medium transition |
| Section expand/collapse | `.spring(duration: 0.35, bounce: 0.2)` | 350 ms | DisclosureGroup, expandable card |
| List row insert/delete | `.easeInOut` | 250 ms | Matches default `List` row animation |
| Numeric counter | `.contentTransition(.numericText)` | system | Score counters, counts |
| Symbol bounce | `.symbolEffect(.bounce)` | system | SF Symbol tap confirmation |
| Scroll reveal | `.easeOut` | 350 ms | `.scrollTransition` opacity/scale fades |
| Sheet morph (Liquid Glass) | `.glassEffectTransition(.matchedGeometry)` | system | Glass IDs transitioning |
| Modal crossfade | `.easeInOut` | 200 ms | State switches inside a sheet |
| Hero transition | `.spring(response: 0.5, dampingFraction: 0.85)` | — | `matchedGeometryEffect` between screens |
| Pull-to-refresh | system default | — | `.refreshable` — don't override |
| Error shake | `.easeInOut` (3 cycles × 80 ms) | 240 ms total | Sign-in failure on form |
| Micro-celebrate (success) | `.spring(response: 0.3, dampingFraction: 0.5)` (over-damped to cause bounce) | — | Checkmark confirm, receipt saved |

## Naming

Name motion tokens by intent, not by curve. A `motion.tap` token hides the implementation; if Apple changes spring tuning in iOS 27, one file updates, not 200.

```swift
enum Motion {
    static let tap = Animation.easeOut(duration: 0.1)
    static let sheet = Animation.spring(response: 0.45, dampingFraction: 0.82)
    static let sectionExpand = Animation.spring(duration: 0.35, bounce: 0.2)
    static let scrollReveal = Animation.easeOut(duration: 0.35)
    static let heroTransition = Animation.spring(response: 0.5, dampingFraction: 0.85)
}

// Usage
.animation(Motion.sectionExpand, value: isExpanded)
withAnimation(Motion.sheet) { detent = .medium }
```

## Consistency Audit

Walk through every interactive surface and verify same-intent motions share the token:

- Every `Button` press uses `Motion.tap`
- Every expand/collapse uses `Motion.sectionExpand` (not a mix of `.spring` and `.easeInOut`)
- Every sheet detent change feels identical
- Every `.scrollTransition` uses `Motion.scrollReveal`

Inconsistency reads as "cheap" even when individual animations are polished. A screen with three distinct spring curves feels unfinished.

## Reduce Motion Behavior

See [ios-accessibility-patterns.md](ios-accessibility-patterns.md#reduce-motion) for the global modifier pattern. Summary: every motion token should return `nil` or a reduced variant under `@Environment(\.accessibilityReduceMotion)`.

```swift
enum Motion {
    @MainActor
    static func tap(reduceMotion: Bool) -> Animation? {
        reduceMotion ? nil : .easeOut(duration: 0.1)
    }
}
```

A simpler global approach: wrap the app root in `.motionSensitive()` and let the transaction-killer cancel animations globally — tokens can stay simple non-conditional values.

## Anti-Patterns

- Using `.default` or no animation value — SwiftUI picks for you, result is inconsistent
- Stacking animations: `.animation(.spring, value: a).animation(.easeInOut, value: b)` — outer usually wins, behavior surprising
- Changing a curve mid-flight: start with `.spring`, interrupt with `.easeOut` — produces jank
- Durations below 80 ms — user can't perceive them; they register as "no animation" (which is fine, but then just skip the animation)
- Durations above 500 ms for primary interactions — feels slow; users start tapping again thinking nothing happened
- Mixing `.linear` with other curves for the same intent — looks cheap
- Default parallax/motion on the Home screen hero — triggers motion-sensitivity complaints
