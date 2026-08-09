# HIG Layout and Spacing

Use this reference for layout, spacing, and touch-target decisions that should feel native on iPhone and iPad.

## Table of Contents

- [Touch Targets](#touch-targets)
- [Safe Areas and Edges](#safe-areas-and-edges)
- [Spacing Scale](#spacing-scale)
- [Thumb Zones](#thumb-zones)
- [Keyboard Avoidance](#keyboard-avoidance)
- [Layout Adaptivity](#layout-adaptivity)
- [Lists vs Cards vs Stacks](#lists-vs-cards-vs-stacks)
- [Common Smells](#common-smells)

## Touch Targets

Apple's rule: **minimum 44 × 44 points** for every tappable element. This is non-negotiable — sub-minimum targets measurably raise tap error rates (treat "meaningfully worse" as the durable claim rather than a fixed percentage, since the exact error-rate delta varies by study and context) and fail accessibility audits.

Common violators:

- Custom close "X" buttons shrunk to 20pt in corner overlays
- Chevron-only row tails with no hit expansion
- Segmented-picker-style pills at 28–32pt tall
- Icon-only toolbar buttons using `.font(.caption)` to size the icon — the button shrinks with the glyph

Fixes:

```swift
Button { dismiss() } label: {
    Image(systemName: "xmark")
        .font(.headline)
}
.frame(minWidth: 44, minHeight: 44)      // enforce hit area
.contentShape(Rectangle())                // expand tappable region if glyph is small
```

For rows where the visual control is intentionally compact, use `.contentShape(Rectangle())` on the whole row so the row itself is tappable at 44pt+ even if the visible control is smaller.

**Exception:** a grid of related items (e.g., 7-day week picker) can use slightly smaller cells (36–40pt) *if* horizontal spacing leaves 8pt+ between targets. Isolated tap targets always stay ≥44pt.

### Touch Target Audit Table

| Element | Min hit area | Min visible glyph |
|---|---|---|
| Primary buttons | 44 × 44 pt | — (size by label) |
| Icon-only buttons | 44 × 44 pt | 17–22pt SF Symbol |
| Close / dismiss | 44 × 44 pt | 17pt SF Symbol |
| List row (entire row) | row height × full width | — |
| List row disclosure chevron | 44 × 44 pt (on row, not chevron) | 12–14pt chevron |
| Segmented picker cells | 36 × 44 pt | label at `.subheadline` |
| Tab bar items | 44 × 44 pt each | 22–28pt glyph |
| Toolbar items | 44 × 44 pt (enforced by system) | 17–22pt glyph |

## Safe Areas and Edges

- **Backgrounds and imagery** can extend under system areas intentionally — use `.ignoresSafeArea(edges: .top)` or `.ignoresSafeArea(edges: [.top, .bottom])`.
- **Interactive content** (buttons, fields, tappable cards) must stay inside safe areas.
- Check clearance on: notched phones, Dynamic Island, home-indicator devices, devices with physical Home button, iPad (toolbar inset differs from iPhone).

```swift
// Background extends; content respects safe area
ZStack {
    BackgroundGradient()
        .ignoresSafeArea()        // background edge-to-edge

    ScrollView {
        content                    // scroll content stays inside safe area
    }
    .safeAreaInset(edge: .bottom) {
        PrimaryCTA()                // sits above home indicator
            .padding()
    }
}
```

Use `.safeAreaInset(edge:)` to add floating chrome that doesn't scroll with content but still respects the home indicator — the scroll view automatically adds padding so its content never disappears behind it.

**Dynamic Island clearance:** the top safe area already accounts for it. Do not manually add `.padding(.top, 44)` — that double-pads on older devices.

## Spacing Scale

A small, repeatable scale beats one-off magic numbers. Most Apple-native apps sit on an 8-point-derived scale, but optical balance matters more than literal multiples.

| Token | Value | Use |
|---|---|---|
| xxs | 2 | Icon-to-label gaps |
| xs | 4 | Inline hairline separations |
| sm | 8 | Compact control gaps |
| md | 12 | Default row/inside-card gaps |
| lg | 16 | Section internal padding |
| xl | 20 | Standard screen padding |
| xxl | 24 | Hero card padding |
| xxxl | 32 | Between sections |
| xxxxl | 40+ | Above primary headings |

Rules:

- Keep **tighter spacing inside a group** than between groups. "Inside-group 8pt, between-group 24pt" is a safe default.
- Use section spacing to signal hierarchy rather than decorative dividers.
- Don't use uniform spacing everywhere — it flattens hierarchy.
- If two screens feel inconsistent, check their spacing tokens first.

### Dynamic Type-Aware Spacing

For layouts that break at larger type sizes, use `@ScaledMetric` so vertical rhythm scales with type:

```swift
@ScaledMetric(relativeTo: .body) private var cardPadding: CGFloat = 20
@ScaledMetric(relativeTo: .headline) private var rowHeight: CGFloat = 56

VStack { ... }
    .padding(cardPadding)
    .frame(minHeight: rowHeight)
```

`@ScaledMetric` scales with Dynamic Type exactly as the related text style does, so spacing grows in lockstep with type.

## Thumb Zones

On a 6.7" phone, the top-left corner is unreachable one-handed. Place primary actions accordingly:

| Zone | Reachability | Use for |
|---|---|---|
| Bottom third | Easy | Primary CTAs, tab bar, main actions |
| Middle third | OK | Content, secondary actions |
| Top third | Hard (thumb stretch) | Navigation chrome (nav bar, titles), search, infrequent actions |

Rules:

- Destination/primary action → bottom-aligned CTA or sheet, not a top-right nav bar button.
- Navigation back / title → top is correct (system expectation).
- Reachability mode: if a user double-taps home/swipes down on indicator, iOS slides UI down. Don't break this by placing interactive content at fixed screen coords.

## Keyboard Avoidance

SwiftUI auto-shifts `ScrollView` content above the keyboard, but these patterns still bite:

- **Content under a fixed CTA disappears** — when the keyboard appears, the CTA covers the field. Solution: use `.scrollDismissesKeyboard(.interactively)` and keep CTAs inside scrollable content, or move CTAs to `.safeAreaInset(edge: .bottom)` so the system manages their position.
- **TextField in a sheet with custom detents** — keyboard lifts the whole sheet above the detent; user can't tap outside to dismiss. Use `.presentationContentInteraction(.scrolls)` and `@FocusState` with a toolbar "Done" button.
- **Auto-advancing focus** — chain `@FocusState` values for multi-field forms:

```swift
enum Field: Hashable { case name, email, phone }

@FocusState private var focused: Field?

TextField("Name", text: $name)
    .focused($focused, equals: .name)
    .submitLabel(.next)
    .onSubmit { focused = .email }

TextField("Email", text: $email)
    .focused($focused, equals: .email)
    .submitLabel(.next)
    .onSubmit { focused = .phone }
```

- **Toolbar "Done" button on the keyboard**:

```swift
TextField(...)
    .toolbar {
        ToolbarItemGroup(placement: .keyboard) {
            Spacer()
            Button("Done") { focused = nil }
        }
    }
```

## Layout Adaptivity

- Prefer **single-column layouts** on compact-width phones for content-heavy screens.
- Use multiple columns only when content is lightweight enough to scan comfortably (e.g., photo grids, icon pickers).
- Re-check long titles, localized strings, and accessibility sizes on the **smallest currently-sold phone**. Apple discontinued the iPhone SE (and with it, sub-6.1" and 4.7" displays) in February 2025 — the iPhone 16e is now the smallest current model at 6.1". Re-verify this figure each session; Apple's lineup shifts yearly and a design that only tests against 6.1"+ may still need to gracefully degrade for the large installed base of older 4.7"/5.4" devices still in the field. If a screen works at 6.1" compact width with AX5 Dynamic Type, it works on every larger current device.
- Use `NavigationSplitView`, `.inspector`, and sidebars on iPad only when larger devices materially benefit — don't shove a phone layout into a regular-width iPad and call it done.
- Use `ViewThatFits` to pick between layouts by available space:

```swift
ViewThatFits(in: .horizontal) {
    HStack { wideLayout }
    VStack { narrowLayout }
}
```

- Use `@Environment(\.horizontalSizeClass)` to branch layouts for compact vs. regular widths. Never branch on device model — size class is the correct abstraction.

## Lists vs Cards vs Stacks

| Container | Use | Avoid |
|---|---|---|
| `List` (plain, inset, insetGrouped, grouped) | Homogeneous rows, settings, inboxes, transactions, long collections | Rebuilding list behavior with custom `VStack` for no reason |
| `LazyVStack` in `ScrollView` | Mixed-content feeds, sections needing custom visuals | Long homogeneous lists (use `List` for free performance and swipes) |
| `LazyVGrid` / `LazyHGrid` | Tiled content, photo grids, icon pickers | Forcing a grid when a list with detail rows scans better |
| Cards | Overview surfaces, mixed-content summaries, visual grouping of heterogeneous data | Making every surface a card — it flattens hierarchy |

Rules:

- If content exceeds one viewport, decide whether it should **scroll, paginate, collapse, or move to a secondary destination**. Scrolling is a default, not a plan.
- Lists give you free swipe actions, edit mode, search, and section headers. Don't reinvent them.
- For overview screens, treat **5–6 visible cards on a phone as a warning threshold, not a hard limit**. If more content competes above the fold, hierarchy is usually weak.
- Use thin 1px dividers inside a card to separate content types, instead of splitting into more cards.

## Common Smells

- Content pressed against screen edges (no `.padding()` from screen margin)
- Equal spacing between everything — no hierarchy signal
- Cards used where a list would scan better
- Multiple columns on a phone for content that really wants one column
- Fixed heights that break under large Dynamic Type (`.frame(height: 44)` when it should be `.frame(minHeight: 44)`)
- Manual `.padding(.top, 44)` for the notch/Dynamic Island — safe area already covers this
- Primary CTA in top-right instead of bottom — thumb-unfriendly
- Forms without a keyboard toolbar Done button
- Touch targets < 44pt without `.contentShape()` expansion
- Absolute pixel positions on `ZStack` that break on smaller phones
- Hardcoded screen-width assumptions (390pt etc.) instead of `GeometryReader` or size classes
