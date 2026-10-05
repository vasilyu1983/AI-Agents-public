# iOS 26 Liquid Glass

## Table of Contents

- [The Core Rule](#the-core-rule)
- [Glass design and ordering](#glass-design-and-ordering)
- [APIs](#apis)
- [When to Use Glass vs Standard Materials vs Plain](#when-to-use-glass-vs-standard-materials-vs-plain)
- [Fallback for pre-iOS 26](#fallback-for-pre-ios-26)
- [Standard Chrome Carries Glass Automatically](#standard-chrome-carries-glass-automatically)
- [OS and tool lookup](#os-and-tool-lookup)
- [Anti-Patterns](#anti-patterns)
- [Accessibility Interactions](#accessibility-interactions)
- [Verification](#verification)
- [Source of Truth](#source-of-truth)

Use this reference when designing with Apple's Liquid Glass material (introduced WWDC25 / iOS 26). It is not a generic "translucent card" effect — it has specific rules and specific APIs.

## The Core Rule

**Liquid Glass belongs to the navigation and control layer. Content sits underneath.** Do not wrap your cards, list rows, or data surfaces in glass. Glass is for the chrome users reach through to interact with content — tab bars, toolbars, sheets, sidebars, floating buttons.

If you find yourself putting `.glassEffect()` on every card, you are already misusing it.

## Glass design and ordering

1. **Glass is navigation, not content.** Tab bars, toolbars, nav bars, sheets, sidebars, Dynamic Island, floating action buttons.
2. **Glass cannot sample other glass.** Two adjacent `.glassEffect()` views produce muddy, incorrect blur. Group them in a `GlassEffectContainer`.
3. **Order appearance modifiers before glass.** Apply `.glassEffect()` after modifiers that affect the view's appearance, as Apple's custom-view guide specifies; not every modifier must precede it.
4. **Measure contrast over actual content.** A scrim such as `.black.opacity(0.15)` is a team starting example, not a universal Apple opacity requirement; adjust the treatment based on measured readability.

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

Choose a shape suited to the control, commonly Capsule, RoundedRectangle, or Circle. Check `glassEffect(_:in:)`'s `Shape` parameter in the installed SDK rather than assuming an `InsettableShape` constraint.

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

## OS and tool lookup

At a design change, read [Apple Developer Releases](https://developer.apple.com/news/releases/) and the target component's HIG/documentation to distinguish shipped behavior from previews. Check the app on both the shipped target OS and its minimum deployment target. Re-review chrome on an OS update and an SDK relink; do not assume either preserves appearance, or that every existing binary automatically adopts all new chrome.

Inspect the target OS's actual glass appearance settings and combine them with Reduce Transparency and Dark Mode. Test each offered choice; if a graded control exists, include its ends and midpoint. Do not infer one OS's control shape from another's announcement.

Use `Tab(role: .search)` where appropriate and let the system place it; before specifying a fixed search position, check the target HIG and actual behavior. Read [Icon Composer](https://developer.apple.com/icon-composer/) and [SF Symbols](https://developer.apple.com/sf-symbols/) at asset selection. The [system-surfaces reference](ios-surfaces-reference.md#app-icons-and-icon-composer) covers icon decisions without assuming numbered tool editions.

## Anti-Patterns

- **Glass on content cards** — muddies the hierarchy and steals attention from data. Use plain surfaces for cards.
- **Adjacent `.glassEffect()` without a container** — produces doubled blur and wrong lensing. Always wrap in `GlassEffectContainer`.
- **Incorrect appearance-modifier order** — apply padding and other appearance modifiers before glass so the captured bounds and content match the intended surface.
- **Glass over plain white/black backgrounds** — glass needs something interesting behind it to refract. Over a solid color, it's just an expensive tint.
- **Tinted glass for every accent color** — `.regular.tint(.red)` and `.regular.tint(.blue)` can compete for attention. Use tint to communicate prominence rather than decorate every control.
- **Glass on text-heavy forms** — materials reduce contrast. Switch to opaque semantic backgrounds for forms and dense settings.
- **Custom "glassmorphism" with `.ultraThinMaterial` + blur stacks** trying to mimic Liquid Glass on iOS 26 — you get double blur and lose the native lensing/highlights. Use the real API.
- **Forgetting Reduce Transparency** — when the user enables this accessibility toggle, glass should degrade to an opaque semantic background. Standard chrome handles this automatically; custom glass surfaces must check `@Environment(\.accessibilityReduceTransparency)` and substitute an opaque surface.
- **Glass over photographic or video content (high-severity contrast trap)** — Nielsen Norman Group's iOS 26 usability audit ("Liquid Glass Is Cracked," nngroup.com) found shrunken tab bars with touch-target spacing below the 0.4cm minimum and reported low contrast for translucent controls against busy backgrounds. Measure your own surface against WCAG AA's 4.5:1 text floor with the Accessibility Inspector rather than citing any published ratio as universal. If your design places glass over user photos, video, maps, or any non-static imagery, budget time to test contrast — it is a common failure mode, not an edge case. Treatments: switch to `.regular` (not `.clear`), add a darker scrim, or use opaque chrome. Never accept "looks fine on Apple's marketing screenshots" as evidence — those screenshots are curated.
- **Conflating glass appearance with Reduce Transparency** — appearance choices and the accessibility toggle are separate inputs. Follow the target-OS matrix in [OS and tool lookup](#os-and-tool-lookup), including combined Dark Mode states on device.

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
- Apple: [Icon Composer](https://developer.apple.com/icon-composer/) and [SF Symbols](https://developer.apple.com/sf-symbols/) — tool capability and availability lookup
- Nielsen Norman Group: "Liquid Glass Is Cracked, and Usability Suffers in iOS 26" (nngroup.com) — independent contrast/usability audit, not an Apple source

When in doubt, consult Apple documentation; community write-ups can lag the API shape.
