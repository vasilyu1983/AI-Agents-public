# iOS 26 Liquid Glass

## Table of Contents

- [The Core Rule](#the-core-rule)
- [The Four Apple Rules](#the-four-apple-rules)
- [APIs](#apis)
- [When to Use Glass vs Standard Materials vs Plain](#when-to-use-glass-vs-standard-materials-vs-plain)
- [Fallback for pre-iOS 26](#fallback-for-pre-ios-26)
- [Standard Chrome Carries Glass Automatically](#standard-chrome-carries-glass-automatically)
- [WWDC26 / iOS 27 Update (Announced, Not Shipped)](#wwdc26--ios-27-update-announced-not-shipped)
- [Anti-Patterns](#anti-patterns)
- [Accessibility Interactions](#accessibility-interactions)
- [Verification](#verification)
- [Source of Truth](#source-of-truth)

Use this reference when designing with Apple's Liquid Glass material (introduced WWDC25 / iOS 26). It is not a generic "translucent card" effect — it has specific rules and specific APIs.

## The Core Rule

**Liquid Glass belongs to the navigation and control layer. Content sits underneath.** Do not wrap your cards, list rows, or data surfaces in glass. Glass is for the chrome users reach through to interact with content — tab bars, toolbars, sheets, sidebars, floating buttons.

If you find yourself putting `.glassEffect()` on every card, you are already misusing it.

## The Four Apple Rules

1. **Glass is navigation, not content.** Tab bars, toolbars, nav bars, sheets, sidebars, Dynamic Island, floating action buttons.
2. **Glass cannot sample other glass.** Two adjacent `.glassEffect()` views produce muddy, incorrect blur. Group them in a `GlassEffectContainer`.
3. **Apply `.glassEffect()` last.** It must be the final modifier in the chain so the material sees the full rendered content behind it.
4. **Dim content before glass.** If glass sits over busy imagery, add a subtle dimming layer (`.black.opacity(0.15)` or similar) below the glass so text stays legible.

## APIs

### `.glassEffect(_:in:)`

Applies a Liquid Glass material to a view in a given shape.

```swift
import SwiftUI

if #available(iOS 26, *) {
    Button("Play") { play() }
        .padding(.horizontal, 20)
        .padding(.vertical, 12)
        .glassEffect(.regular, in: Capsule())
}
```

Variants (chained on a `Glass` value, not as standalone arguments):
- `.regular` — default; adapts to light/dark automatically
- `.clear` — pair with an explicit dimming layer behind the glass for contrast
- `.regular.interactive()` / `.clear.interactive()` — `interactive()` is a modifier on `Glass` that makes the material respond to touch and motion. Reserve for primary CTAs. Do **not** write `.glassEffect(.interactive(), …)` — that won't compile against the shipping API.
- `.regular.tint(Color.purple.opacity(0.8))` — colour-tinted glass for branded surfaces; use sparingly. The shipping API is `.tint(Color)` chained on `Glass`, not `.tinted(Color)`.

Shape must be a closed `InsettableShape` (Capsule, RoundedRectangle, Circle). Never pass a free-form Path — rendering is undefined.

### `GlassButtonStyle` and `.buttonStyle(.glass)`

For buttons specifically, prefer the dedicated button styles over manual `.glassEffect()`:

```swift
if #available(iOS 26, *) {
    Button("Play") { play() }
        .buttonStyle(.glass)               // Liquid Glass effect based on context
    Button("Subscribe") { subscribe() }
        .buttonStyle(.glassProminent)      // prominent glass border
}
```

These styles inherit context (toolbar vs floating, light vs dark, Reduce Transparency) automatically and pick the right shape, padding, and hit target for the placement. Reach for `.glassEffect()` directly only when designing a non-button glass surface (a custom toolbar, badge, or pill).

### `GlassEffectContainer`

Groups nearby glass views so their blurs blend correctly and can morph between each other.

```swift
@Namespace private var glassNS

GlassEffectContainer(spacing: 16) {
    HStack(spacing: 10) {
        Button { /* ... */ } label: { Label("Play", systemImage: "play.fill") }
            .glassEffect(.regular, in: Capsule())
            .glassEffectID("play", in: glassNS)

        Button { /* ... */ } label: { Label("Queue", systemImage: "text.badge.plus") }
            .glassEffect(.regular, in: Capsule())
            .glassEffectID("queue", in: glassNS)
    }
}
```

The `spacing:` argument is a proximity threshold: elements closer than this distance visually merge and morph through transitions. The `Namespace` + matching `glassEffectID` values enable smooth morphing when the set of elements changes.

### `glassEffectTransition`

Controls how a glass element animates when added, removed, or re-identified:

```swift
.glassEffect(.regular, in: Capsule())
.glassEffectTransition(.matchedGeometry)
```

Use `.matchedGeometry` when morphing between two glass elements sharing a `glassEffectID`. Use `.identity` to suppress morph animations (rarely needed).

## When to Use Glass vs Standard Materials vs Plain

| Layer | Material | Why |
|---|---|---|
| Navigation chrome (tab bar, toolbar, sheet, sidebar, nav bar) | Liquid Glass (standard controls carry it automatically) | Apple's target use case |
| Floating action button / custom toolbar | `.glassEffect(.regular, in: Capsule())` | Chrome that floats over content |
| Dynamic-disclosure badges, pills over imagery | Glass — if content behind needs to show through | Reinforces spatial layering |
| Content cards, list rows, data panels | `.ultraThinMaterial` / `.regularMaterial` / plain fill | Not navigation; glass is wrong here |
| Settings rows, forms, text-dense surfaces | Plain semantic background (`Color(.systemBackground)`, `Color(.secondarySystemGroupedBackground)`) | Readability beats style |

## Fallback for pre-iOS 26

```swift
extension View {
    @ViewBuilder
    func appChromeBackground<S: InsettableShape>(in shape: S) -> some View {
        if #available(iOS 26, *) {
            self.glassEffect(.regular, in: shape)
        } else {
            self
                .background(.ultraThinMaterial, in: shape)
                .overlay(shape.stroke(Color.white.opacity(0.12), lineWidth: 0.5))
        }
    }
}
```

Wrap this in your app's design system so feature code is version-neutral. Do **not** sprinkle `#available(iOS 26, *)` checks through screens.

## Standard Chrome Carries Glass Automatically

You rarely need to call `.glassEffect()` yourself. Stock SwiftUI chrome picks up Liquid Glass on iOS 26 when you use the defaults:

- `TabView` with `.tabViewStyle(.sidebarAdaptable)` or default tabs
- `NavigationStack` + `.toolbar { ... }` (toolbars, search, inline titles)
- `.sheet { ... }` with `.presentationDetents(...)`
- `NavigationSplitView` sidebars
- `Menu` overflow buttons

If you are reaching for a custom glass surface, ask first: can the same user goal be served by a stock toolbar button, a sheet, or a menu? If yes, use that — you inherit glass for free and get accessibility, Dynamic Type, and Dark Mode behavior for free.

## WWDC26 / iOS 27 Update (Announced, Not Shipped)

At WWDC26 (June 2026) Apple previewed further Liquid Glass revisions for iOS/iPadOS/macOS 27 — **these are beta-only as of this validation pass; do not present them as current shipping behavior**, and re-verify GA status before relying on them:

- **Reduced default transparency** and a darkened edge/border around glass elements, intended to directly answer the contrast criticism above.
- **A system-level Clear ↔ Tinted appearance control**, built into Settings rather than the iOS 26.1 in-app-adjacent slider — a first-class user preference, not a hidden accessibility toggle.
- **Brighter specular highlights** and improved diffusion of complex content behind glass, aimed at readability over busy backgrounds.
- **Search moves back into the tab bar** on iOS 27, reversing the iOS 26 change that placed it as a separate bottom-right affordance — plan for this if a design currently special-cases the iOS 26 search placement.
- **Icon Composer 2** (companion tool) adds refraction and layered specular-highlight controls for app icons; **SF Symbols 8** ships alongside with an expanded symbol set.

Treat every bullet above as provisional. Label it "iOS 27 (WWDC26, not yet GA)" in any review output, and confirm current beta/GA status via [../data/sources.json](../data/sources.json) or a fresh Apple Developer / WWDC26 session lookup before shipping guidance against it.

## Anti-Patterns

- **Glass on content cards** — muddies the hierarchy and steals attention from data. Use plain surfaces for cards.
- **Adjacent `.glassEffect()` without a container** — produces doubled blur and wrong lensing. Always wrap in `GlassEffectContainer`.
- **`.glassEffect()` not applied last** — modifiers after glass don't see the material, and padding/clipShape ordering silently breaks the shape.
- **Glass over plain white/black backgrounds** — glass needs something interesting behind it to refract. Over a solid color, it's just an expensive tint.
- **Tinted glass for every accent color** — `.tinted(.red)`, `.tinted(.blue)` etc. produces visual chaos. Use `.tinted` sparingly, usually only for a single signature element.
- **Glass on text-heavy forms** — materials reduce contrast. Switch to opaque semantic backgrounds for forms and dense settings.
- **Custom "glassmorphism" with `.ultraThinMaterial` + blur stacks** trying to mimic Liquid Glass on iOS 26 — you get double blur and lose the native lensing/highlights. Use the real API.
- **Forgetting Reduce Transparency** — when the user enables this accessibility toggle, glass should degrade to an opaque semantic background. Standard chrome handles this automatically; custom glass surfaces must check `@Environment(\.accessibilityReduceTransparency)` and substitute an opaque surface.
- **Glass over photographic or video content (high-severity contrast trap)** — Nielsen Norman Group's iOS 26 usability audit ("Liquid Glass Is Cracked," nngroup.com) reported translucent controls measuring as low as ~1.5:1 against busy backgrounds, far below WCAG AA's 4.5:1 floor, and found shrunken tab bars with touch-target spacing below the 0.4cm minimum. Treat the specific ratio as a reported field measurement, not an Apple-published spec — re-measure your own surface with the Accessibility Inspector rather than citing the number as universal. If your design places glass over user photos, video, maps, or any non-static imagery, budget time to test contrast — it is a common failure mode, not an edge case. Treatments: switch to `.regular` (not `.clear`), add a darker scrim, or use opaque chrome. Never accept "looks fine on Apple's marketing screenshots" as evidence — those screenshots are curated.
- **Treating Reduce Transparency as binary in iOS 26.1+** — iOS 26.1 (October 2025) added a system-wide Liquid Glass *opacity slider* (Clear ↔ Tinted) alongside the existing Reduce Transparency toggle. Custom glass surfaces that only branch on `@Environment(\.accessibilityReduceTransparency)` (binary) will render incorrectly under intermediate slider settings. Test at the 0%, 50%, and 100% slider positions. Also note: iOS 26.1 shipped with a reported bug pairing Reduce Transparency + Dark Mode that could leave text unreadable (e.g., black-on-black in Photos) — verify visually on-device rather than trusting the simulator, and re-check after each point release since Apple continued adjusting default opacity through iOS 26.2.

## Accessibility Interactions

Glass is invisible to VoiceOver (a visual layer, not a control), but its visibility changes with system settings:

| Setting | Effect | Design response |
|---|---|---|
| Reduce Transparency | Glass falls back to opaque semantic surfaces | Confirm text contrast in the opaque state |
| Increase Contrast | Apple darkens/lightens glass edges | Re-verify border/stroke visibility |
| Reduce Motion | Glass morphing transitions are suppressed | Matched-geometry morph should fall back to cross-fade |
| Larger Dynamic Type | Content below glass chrome may reflow into the glass area | Add bottom safe-area padding so content clears the chrome at AX5 |

## Verification

Before shipping any Liquid Glass surface:

1. Test with Reduce Transparency enabled — confirm legibility in the opaque fallback.
2. Test at Dynamic Type AX3 and AX5 — confirm content doesn't disappear behind glass chrome.
3. Test in both Light and Dark Mode over varied content (imagery + flat color + text) — glass over flat white is a smell.
4. Run the Accessibility Inspector's contrast audit on any text sitting over glass.
5. Screenshot the glass surface on a real device if possible — simulator renders Liquid Glass differently from hardware due to motion/lensing.

## Source of Truth

- Apple: [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/SwiftUI/Applying-Liquid-Glass-to-custom-views)
- Apple: [glassEffect(_:in:)](https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:))
- Apple: [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- WWDC25 session 219 — "Meet Liquid Glass"
- WWDC25 session 323 — "Build a SwiftUI app with the new design"
- WWDC26 (June 2026) — Liquid Glass revisions for iOS/iPadOS/macOS 27, Icon Composer 2, SF Symbols 8 (beta as of this validation pass; verify GA before citing)
- Nielsen Norman Group: "Liquid Glass Is Cracked, and Usability Suffers in iOS 26" (nngroup.com) — independent contrast/usability audit, not an Apple source

When in doubt, consult Apple documentation; community write-ups can lag the API shape.
