# iOS Craft and Feel

How elite iOS apps win on craft. This is the layer above HIG compliance — the spring physics, haptic choreography, SF Symbol craft, and editorial polish that distinguishes Things, Linear, Reeder, Apollo, Halide, Procreate, Streaks, and the best of Apple's own apps from generic SwiftUI work.

If a screen "follows HIG" but feels lifeless, this reference is the gap.

---

## Table of Contents

- [The Feel Bar](#the-feel-bar)
- [Spring Physics and Timing](#spring-physics-and-timing)
- [Haptic Choreography](#haptic-choreography)
- [SF Symbol Craft](#sf-symbol-craft)
- [Transition Choreography](#transition-choreography)
- [Editorial Number and Unit Polish](#editorial-number-and-unit-polish)
- [Pull-to-Refresh, Drag, and Scrub](#pull-to-refresh-drag-and-scrub)
- [Press, Hover, Long-Press](#press-hover-long-press)
- [Live Activities, Widgets, Lock Screen](#live-activities-widgets-lock-screen)
- [Camera and Photo Picker Craft](#camera-and-photo-picker-craft)
- [Anti-Patterns](#anti-patterns)
- [Sources](#sources)

---

## The Feel Bar

Use this checklist for every interactive surface. Apple's own apps fail rows here; aspire higher.

| Dimension | Pass | Fail |
|-----------|------|------|
| **Press feedback** | Every tappable element has a visible press state | `.buttonStyle(.plain)` everywhere |
| **Haptic on commit** | Discrete success actions trigger `.success` sensory feedback | Silent saves and sends |
| **Spring not duration** | Animations use `.spring`, not `.easeInOut(duration:)` | Every animation 0.3s ease |
| **Matched geometry** | Detail expansion uses `matchedGeometryEffect` or `glassEffectID` morph | Cross-fade modal pop |
| **Symbol effect** | State changes animate the SF Symbol (bounce, replace, scale) | Hard symbol swaps |
| **Scrub feedback** | Sliders, scrubbers, pickers have haptic snap and detent | Linear silent drag |
| **Pull-to-refresh** | Custom refresh signal beyond default spinner | Default refresh control |
| **Numbers** | Tabular monospace where alignment matters | Default font in lists with stats |
| **Selection** | Selection state has color + bold + symbol weight change | Color change only |
| **Empty state polish** | Composed state with illustration + verb CTA + microcopy | "No items yet" |
| **Reduce Motion** | Tested at AX setting; alternates ship | Bouncy springs unsuppressed |
| **Live Activity / Widget** | If app has active session, exists | Background-only app |

A "feels like Apple" iOS app passes 10+ rows.

---

## Spring Physics and Timing

The dominant animation primitive on iOS is the spring, not the duration curve. Springs feel alive because they decelerate by physics, not by interpolation.

### When to use which spring

```swift
// SwiftUI spring presets (iOS 17+)
.spring                                 // default — slightly bouncy
.snappy                                 // quick, almost no overshoot — UI commits
.bouncy                                 // playful — celebrations, delight moments
.smooth                                 // calm, no overshoot — major layout transitions
.interactiveSpring                      // tracks gestures
```

### Token mapping (use these, not raw durations)

| Intent | Spring | When |
|--------|--------|------|
| commit (save, confirm, send) | `.snappy(duration: 0.25)` | discrete action with success haptic |
| navigation transition | `.smooth(duration: 0.4)` | push, sheet, route change |
| detail expansion | `.spring(duration: 0.45, bounce: 0.15)` | matchedGeometry expansion |
| celebration | `.bouncy(duration: 0.6, extraBounce: 0.2)` | first-success delight |
| micro-interaction (toggle, like) | `.snappy(duration: 0.15)` | high-frequency UI |
| gesture-following | `.interactiveSpring(response: 0.2, dampingFraction: 0.85)` | drag, scrub |

Avoid `.easeInOut(duration: 0.3)` — it's the SwiftUI equivalent of Times New Roman. Recognisably default.

### Timing rules

- Sub-100ms: instant; no animation needed
- 100–300ms: feels responsive; use snappy
- 300–500ms: feels intentional; use smooth or spring with bounce 0.1–0.2
- 500ms+: feels dramatic; reserve for celebrations and route changes

### Reduce Motion fallback

```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion

withAnimation(reduceMotion ? .smooth(duration: 0) : .spring) {
    expanded.toggle()
}
```

For matched-geometry morphs, the Reduce Motion alternative is a cross-fade with the same duration, not an instant cut — instant cuts trigger their own discomfort.

---

## Haptic Choreography

Haptics on iOS are an *expressive language*. Treat them with the same intent as motion: every haptic answers a question the user is asking with their finger.

### The vocabulary

```swift
.sensoryFeedback(.success, trigger: didComplete)         // commit succeeded
.sensoryFeedback(.warning, trigger: didWarn)             // soft caution
.sensoryFeedback(.error, trigger: didFail)               // hard fail
.sensoryFeedback(.selection, trigger: selectedID)        // value change in picker, segmented control
.sensoryFeedback(.impact(weight: .light), trigger: x)    // micro-confirm: like, archive, snap
.sensoryFeedback(.impact(weight: .medium), trigger: x)   // commit: send, save
.sensoryFeedback(.impact(weight: .heavy), trigger: x)    // weighty action: delete confirm
.sensoryFeedback(.start, trigger: didStartScrub)         // gesture engaged
.sensoryFeedback(.stop, trigger: didEndScrub)            // gesture released
.sensoryFeedback(.alignment, trigger: snappedToGrid)     // snap to detent
.sensoryFeedback(.levelChange, trigger: pageIndex)       // crossing a threshold
```

### Choreography by flow

A polished iOS app uses 3–6 haptic events per main flow. Examples:

**Send a message**
1. `.start` when long-press to record voice
2. `.alignment` when waveform crosses 1s mark
3. `.success` on send
4. `.impact(.light)` when delivered (cross-axis)

**Save a note**
1. `.selection` when toggling formatting
2. `.success` on autosave commit (only on first save in session, not on every keystroke)
3. `.impact(.light)` when lock-screen widget updates

**Onboarding first action**
1. `.impact(.medium)` on tap of first CTA
2. `.success` on completion
3. `.bouncy` visual + no haptic overlap on celebration (haptic during celebration animation feels noisy)

### Anti-patterns

- haptic on every tap (fatiguing within 30s of use)
- haptic without a visible state change (ambiguous interpretation)
- error haptic on validation failures *during* typing (use only on submit)
- ignoring `accessibilityVoiceOverEnabled` — haptics matter more here, but choreography simplifies; redundant haptics confuse

---

## SF Symbol Craft

SF Symbols are the typographic system of iOS UI. Used craftily, they carry state, animation, and meaning. Used lazily, they look stock.

### Choosing the right variant

- **Filled vs outline**: outline for inactive/default, filled for selected/active. Avoid mixing within a row of icons.
- **Hierarchical** rendering (`.symbolRenderingMode(.hierarchical)`): for icons with internal structure (e.g., `chart.bar.xaxis`) — gives depth without color noise.
- **Multicolor**: only when the color is *meaningful* (red heart, yellow star, brand color). Never for decoration.
- **Palette**: when you control the color of each layer — useful for status icons (e.g., a battery with red fill at low level).
- **Variable** (`.symbolVariant(.fill)` + `value:` parameter): reflects continuous state (battery, signal, volume).
- **Weight + scale matched to type**: a `.headline`-adjacent icon is `.semibold` weight, `.medium` scale. A `.body`-adjacent icon is `.regular`/`.medium`.

### Symbol effects (iOS 17+)

```swift
Image(systemName: "heart.fill")
    .symbolEffect(.bounce, value: likedCount)        // bounce on count change
    .symbolEffect(.pulse)                            // recurring breathing
    .symbolEffect(.scale.up, isActive: isHovered)    // discrete state
    .contentTransition(.symbolEffect(.replace))      // morph between symbols
```

The `.replace` content transition is the iOS-native way to animate `play` → `pause`, `bookmark` → `bookmark.fill`, `arrow.up` → `checkmark`. Use it for any binary state toggle.

### SF Symbols 7 (iOS 26 — current shipping baseline)

- **Draw animations**: symbols can stroke-on as if hand-drawn. Use for first-discovery moments and long-loading completions, not on every appearance.
- **Gradient rendering**: hierarchical and palette modes accept gradients. Reserve for hero or status icons.
- **Custom symbols** with the SF Symbols app: export `.symbolSet`, drop into the asset catalog. Custom symbols inherit Dynamic Type, weight, and rendering modes for free.
- **Forward note**: SF Symbols 8 was previewed at WWDC26 (June 2026) alongside Icon Composer 2, expanding the symbol library for iOS 27. It is beta-only as of this validation pass — build against SF Symbols 7 / iOS 26 for anything shipping today, and re-verify SF Symbols 8's GA status before adopting it.

### Symbol pairings

Common combinations that read well in lists:

| Action | Default | Selected/Active |
|--------|---------|-----------------|
| play / pause | `play.fill` | `pause.fill` (with `.replace` transition) |
| bookmark | `bookmark` | `bookmark.fill` |
| like | `heart` | `heart.fill` (multicolor red, with `.bounce`) |
| archive | `archivebox` | `archivebox.fill` |
| share | `square.and.arrow.up` | (no selected state — discrete action) |
| delete | `trash` | (confirm via haptic + animation, not symbol change) |
| follow | `person.badge.plus` | `person.fill.checkmark` |
| notification | `bell` | `bell.fill` (variable for badge count) |

---

## Transition Choreography

The way one screen becomes another is craft. Cross-fade is the lazy default; iOS gives you better tools.

### `matchedGeometryEffect` use cases

- list row → detail screen (shared image expands, title slides into place)
- thumbnail → fullscreen photo
- card → modal sheet
- collapsed → expanded state within a screen

```swift
@Namespace private var ns

if expanded {
    DetailView(image: image)
        .matchedGeometryEffect(id: image.id, in: ns)
} else {
    ThumbnailView(image: image)
        .matchedGeometryEffect(id: image.id, in: ns)
        .onTapGesture { withAnimation(.spring) { expanded = true } }
}
```

The matched element must exist in *both* states with the same ID. The transition reads as one element morphing rather than two elements cross-fading.

### Liquid Glass morph (iOS 26)

```swift
GlassEffectContainer(spacing: 16) {
    ForEach(visibleControls) { control in
        ControlButton(control)
            .glassEffectID(control.id, in: glassNS)
    }
}
.animation(.smooth, value: visibleControls)
```

When `visibleControls` changes, glass elements morph between IDs rather than fading. See `ios26-liquid-glass.md`.

### Hero animation rules

1. The hero element must remain visually identifiable through the transition (same shape family, same color core).
2. Complete the hero motion before starting secondary motion. A 1.5x stagger feels like a director's cut; simultaneous motion feels chaotic.
3. Reverse the choreography on dismiss — exact reversal, same timing. Asymmetric transitions feel broken.
4. Test with Reduce Motion: cross-fade replacement should still complete in the same duration.

---

## Editorial Number and Unit Polish

Numbers in iOS apps are content. Editorial polish here is what separates a stat from a glance.

### Tabular numbers

```swift
Text("1,247")
    .font(.system(.body, design: .default).monospacedDigit())
// or
.font(.body.monospacedDigit())
```

Use monospaced digits for any column-aligned number, score, time, or counter. Without it, `1` is narrower than `8` and the column wobbles as values change.

### Locale-aware formatters

```swift
let amount: Decimal = 1247.50
amount.formatted(.currency(code: "USD"))                  // "$1,247.50"
amount.formatted(.currency(code: "EUR").locale(.init(identifier: "de_DE")))  // "1.247,50 €"

let date = Date.now
date.formatted(.relative(presentation: .named))           // "just now", "yesterday"
date.formatted(date: .abbreviated, time: .shortened)      // "Apr 28, 3:14 PM"

let duration = Duration.seconds(8174)
duration.formatted(.units(allowed: [.hours, .minutes], width: .abbreviated))  // "2h 16m"

let count = 12
count.formatted(.number.notation(.compactName))           // "12"; for 12_000 → "12K"
```

Never hand-format a number with `String(format:)` for user-facing copy.

### Editorial rounding

- Stats in scrolling lists: round aggressively. `$1.2K` beats `$1,247`. `2h 14m` beats `134 minutes`.
- Detail screens: full precision available, but lead with the rounded form.
- Percentages: round to 0–1 decimal in lists; 2 in detail. "47%" not "47.382%".
- Currency: only show cents in receipts, transaction details, or where the cents matter (gas, fractional shares). Round to whole units in summaries.
- Time: relative until 7 days, then absolute. Never "23 minutes ago" alongside "Apr 28, 2024" in the same list.

### Units with values

- "$24" not "USD 24" or "24 USD"
- "12 km" with non-breaking space (use `Text("12\u{00A0}km")` or `Measurement` formatters)
- "2h 14m" not "2 hours 14 minutes" in dense UI
- "5/10" or "5 of 10" never "five out of ten" in UI; spell out only in onboarding prose

---

## Pull-to-Refresh, Drag, and Scrub

These are the gestures where iOS feel is decided. Default behaviors are functional but unmemorable.

### Pull-to-refresh

Default `.refreshable` is fine. Polished apps customize:

- **Replace the spinner** with a custom progress indicator that *teases* the content (Apollo's emoji bounce, Reeder's icon).
- **Haptic on threshold cross**: `.impact(.light)` when the user drags past the trigger point.
- **Haptic on commit**: `.success` when refresh completes.
- **Stagger arriving content** by 30–60ms per row, only on pull-refresh — feels like the data is arriving.

### Drag-and-drop in lists

- Long-press lifts the row (haptic `.start`, slight scale + shadow).
- Drag updates with `.interactiveSpring` so the row tracks the finger.
- Drop with `.snappy` animation and `.success` haptic.
- During drag, other rows reflow with `.spring(duration: 0.3, bounce: 0.1)`.

### Scrubbing (sliders, value pickers)

- `.sensoryFeedback(.alignment, trigger:)` on detents (5%, 10%, 25% etc.) gives the slider a "feel" of grooves.
- Mid-drag value display pops up above the thumb finger with a `.spring` entry.
- Release haptic `.stop`, value commits with `.success` only if value actually changed.

### Carousel / paging

- `.scrollTargetBehavior(.paging)` (iOS 17+) for true page snapping.
- `.scrollTransition` for parallax effects on adjacent pages — siblings shrink/fade slightly.
- Page indicator: a custom indicator that responds to scroll progress (continuous, not discrete) feels alive.

---

## Press, Hover, Long-Press

Every interactive element should have at least three states: rest, press, success.

### Press states

```swift
struct CraftedButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.97 : 1.0)
            .opacity(configuration.isPressed ? 0.85 : 1.0)
            .animation(.snappy(duration: 0.15), value: configuration.isPressed)
    }
}
```

Rules:
- press scale: 0.96–0.98 (more is goofy, less is invisible)
- press opacity: 0.80–0.90
- press feedback animates *in* on touch-down, *out* slowly on touch-up (180ms in, 250ms out feels balanced)
- never `.buttonStyle(.plain)` on tappable surfaces without a custom style

### Hover (iPad with pointer, Mac Catalyst)

`.hoverEffect(.lift)` is iOS's default and works well. Custom hover effects use `.hoverEffect(.highlight)` or compose from `onContinuousHover`.

### Long-press

Long-press is a power-user accelerator on iOS. Common patterns:
- preview (Apollo Reddit, Mail) — peek at content without committing
- context menu (`.contextMenu { ... }`) — actions for the item
- drag start (lists, photos)
- record-while-held (voice messages, camera)

Long-press must always have a tap alternative. Never make it the only path.

### `.contextMenu` craft

```swift
.contextMenu {
    Button("Copy", systemImage: "doc.on.doc") { copy() }
    Button("Share", systemImage: "square.and.arrow.up") { share() }
    Divider()
    Button("Delete", systemImage: "trash", role: .destructive) { delete() }
} preview: {
    DetailPreview(item)
        .frame(width: 280, height: 200)
}
```

The `preview:` parameter elevates the menu from "right-click" to "Apple Photos preview" — use for any item with rich content.

---

## Live Activities, Widgets, Lock Screen

A consumer iOS app that doesn't ship a widget or Live Activity has left craft on the table.

### Live Activities

For any in-progress, time-bound user activity: ride pickup, food delivery, workout, timer, ride-share, sports, video call, audio playback. iOS 26 and the Dynamic Island place these front-and-center; Lock Screen is a primary surface.

Craft considerations:
- Compact leading + trailing must read in one eye-fixation (≤4 chars or 1 icon each)
- Expanded view: 3 zones max, each a glanceable fact
- Updates throttled to ≤1/sec; Apple rate-limits aggressively
- End the Live Activity when complete — leaving stale activities is broken behavior

### Widgets

WidgetKit + AppIntents for interactive widgets (iOS 17+). For consumer apps:

- small widget: one fact, one tap target
- medium widget: status + 2–3 actions (mark done, log, start)
- large widget: digest, multi-item list (top 3 + "see all")
- accessory inline / circular / rectangular for Lock Screen and StandBy

Tappable widget regions must look tappable — outlined or chip-shaped affordances, not bare text.

### Lock Screen

Live Activities and widgets share Lock Screen real estate. Ensure your app's surface remains useful in:
- always-on display (low refresh)
- StandBy mode (iPhone charging horizontal)
- CarPlay (where applicable)

---

## Camera and Photo Picker Craft

Camera and photo flows are where craft is most visible because they replace Apple's own apps.

### `PhotosPicker` (iOS 16+)

```swift
PhotosPicker(selection: $items,
             maxSelectionCount: 5,
             matching: .images,
             preferredItemEncoding: .compatible) {
    Label("Select photos", systemImage: "photo.on.rectangle")
}
.photosPickerStyle(.inline)             // inline picker, no sheet
```

The inline picker style (iOS 17+) feels native for any "add photo" flow — no sheet break.

### Camera (`AVFoundation` or Vision)

If you ship a custom camera (Halide, VSCO, Procreate Pocket):

- Pre-warm the capture session before the screen mounts (1–2s reduction in shutter readiness).
- Capture button uses heavy haptic on press, success haptic on shutter.
- Show captured image *immediately* with a fast-cropped thumbnail, then refine in the background.
- Volume button shutter: respect user expectation; `MPVolumeView` workarounds are fragile but expected.
- Live Photo / RAW support if your audience cares.

---

## Anti-Patterns

- **Default `.easeInOut(duration: 0.3)` everywhere** — recognisably stock SwiftUI.
- **`.buttonStyle(.plain)` on every tap target** — no press feedback; feels broken.
- **No haptic anywhere** — silent commits. Consumer apps are judged for this.
- **Haptic on every tap** — fatiguing.
- **Cross-fade transitions for hero content** — replace with matched geometry.
- **Hard symbol swaps** for state changes — use `.contentTransition(.symbolEffect(.replace))`.
- **Default refresh spinner** in flagship apps — invest in a branded indicator.
- **Default fonts on numbers in stats lists** — wobbles when values change. Use `.monospacedDigit()`.
- **Generic empty states** — "No items yet" + grey illustration. See [../../software-ui-ux-design/references/consumer-craft-patterns.md](../../software-ui-ux-design/references/consumer-craft-patterns.md).
- **Settings screen with 47 toggles** — group, search, defaults.
- **Modal sheets for single-field edits** — inline edit instead.
- **Long-press as the only path** to a function — accelerator, not gateway.
- **Live Activity that doesn't end** when the activity ends.
- **Widget that's just a logo + count** — interactive widgets are a primary surface, not an afterthought.
- **Skipping Reduce Motion** — bouncy springs unsuppressed.
- **Custom-camera UI that obscures the framing** — controls must hide on capture intent.

---

## Sources

- [Apple HIG — Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Apple HIG — Feedback](https://developer.apple.com/design/human-interface-guidelines/feedback)
- [Apple HIG — Sensory feedback](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
- [Apple HIG — SF Symbols](https://developer.apple.com/design/human-interface-guidelines/sf-symbols)
- [WWDC23 — Animate symbols in your app](https://developer.apple.com/videos/play/wwdc2023/10257/)
- [WWDC23 — Build great game experiences with haptics](https://developer.apple.com/videos/play/wwdc2023/10079/)
- [WWDC25 — Meet Liquid Glass](https://developer.apple.com/videos/) (session 219)
- [Things 3 design notes — Federico Viticci, MacStories](https://www.macstories.net/)
- [Hacking with Swift — SwiftUI animation](https://www.hackingwithswift.com/quick-start/swiftui)
- [Donny Wals — SwiftUI animation craft](https://www.donnywals.com/)
- [Sebastiaan de With — iOS design writing](https://stories.lux.camera/)
