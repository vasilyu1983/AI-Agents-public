# iOS Component Patterns

Use this reference when choosing native iOS structures and standard component behavior.

## Table of Contents

- [Tab Views](#tab-views)
- [Navigation Stacks](#navigation-stacks)
- [Sheets and Full-Screen Covers](#sheets-and-full-screen-covers) — persistent bottom sheets, sheet peek overlap, multiple sheets, grid cell stretching
- [Lists](#lists)
- [Cards](#cards)
- [Canvas-Based Data Visualizations](#canvas-based-data-visualizations) — radar/spider charts, score rings, gradient bars, gauges, quadrant compass, multi-layer Canvas
- [Interactive Scroll and Animation Patterns](#interactive-scroll-and-animation-patterns) — scroll transitions, expandable sections, sensory feedback, SF Symbol effects
- [Buttons and Actions](#buttons-and-actions)
- [Search, Filters, and Secondary Controls](#search-filters-and-secondary-controls)
- [FlowLayout (Wrapping Pills)](#flowlayout-wrapping-pills)
- [Immersive Visualization Screen](#immersive-visualization-screen) — structure, controls strip, visualization-specific layout, map patterns

## Tab Views

- Use tab views for top-level peer sections of the app.
- Keep tab count to five or fewer.
- Give each tab a clear label and symbol.
- Keep navigation history scoped to each tab instead of sharing one stack across the entire app.

## Navigation Stacks

- Use navigation stacks for drill-down flows.
- Prefer large titles at root destinations and inline titles deeper in the stack.
- Keep primary actions in the toolbar when they are screen-level, not embedded into the content by default.

## Sheets and Full-Screen Covers

- Use sheets for focused work that temporarily interrupts the current context.
- Use full-screen covers only when the experience truly replaces the surrounding context.
- Make dismissal and completion obvious; do not rely only on gestures.

### Persistent Bottom Sheet (Immersive Visualization Detail)

For immersive screens where the visualization fills the screen and detail content lives in an always-present sheet:

```swift
.sheet(isPresented: $showPanel) {
    DetailPanel(model: model)
        .presentationDetents([.customPeek, .medium, .large], selection: $panelDetent)
        .presentationBackgroundInteraction(.enabled(upThrough: .medium))
        .presentationDragIndicator(.visible)
        .interactiveDismissDisabled(true)
        .presentationCornerRadius(28)
}
.onAppear { showPanel = true }
```

Key differences from temporary sheets:
- **Always present** — `.interactiveDismissDisabled(true)` + `.onAppear { showPanel = true }`
- **Custom peek detent** — `PresentationDetent.height(100)` shows summary header at rest
- **Background interaction** — `.presentationBackgroundInteraction(.enabled(upThrough: .medium))` allows gestures on the visualization (pan, pinch, tap) when sheet is at peek or medium
- **Selection-driven expansion** — tapping a data point sets `panelDetent = .medium` to spring the sheet up with detail

When to use persistent sheets vs temporary `.sheet(item:)`:
- **Persistent**: immersive screens where detail supplements a full-bleed visualization (charts, 3D scenes, maps)
- **Temporary**: hub/list screens where detail replaces focus temporarily

### Sheet Peek Overlap Fix

When controls sit between a visualization and a persistent sheet peek, the sheet overlaps the controls. Fix by adding bottom padding equal to the peek height:

```swift
VStack(spacing: 10) {
    visualization        // fills available space
    controlsStrip        // segmented picker + body row
    timelineSlider
        .padding(.bottom, 104)  // >= sheet peek height (100pt)
}
.sheet(isPresented: $showPanel) { ... }
```

### Multiple Sheets on One View

SwiftUI (iOS 16.4+) supports multiple `.sheet` modifiers on the same view. Each sheet should be gated by its own `Optional` property so only one presents at a time:

```swift
.sheet(isPresented: Binding(
    get: { model.selectedRetrograde != nil },
    set: { if !$0 { model.selectedRetrograde = nil } }
)) { ... }
.sheet(isPresented: Binding(
    get: { model.selectedEclipse != nil },
    set: { if !$0 { model.selectedEclipse = nil } }
)) { ... }
```

This is cleaner than an enum-based approach when sheets are conceptually independent (each section "owns" its own detail). For 4+ sheets, verify only one `Optional` is non-nil at a time.

### Grid Cell Stretching

`LazyVGrid` with `.flexible()` columns gives each cell equal space, but content inside doesn't stretch automatically. Always add `.frame(maxWidth: .infinity, alignment: .leading)` to grid cell content:

```swift
// Without: cells hug content width → unequal column widths
// With: cells fill their grid column → visually aligned
VStack(alignment: .leading) { ... }
    .frame(maxWidth: .infinity, alignment: .leading)
    .background(surfaceColor)
    .clipShape(RoundedRectangle(cornerRadius: radius, style: .continuous))
```

Do not use `.clipShape(Capsule())` for grid cells that stretch wide — capsules pinch at wide aspect ratios. Use `RoundedRectangle` instead.

## Lists

- Use lists for settings, inbox-like flows, transactions, and other row-driven collections.
- Prefer native list affordances such as disclosure, swipe actions, edit mode, and search when they fit.
- Avoid rebuilding list behavior with custom stacks unless the visual need is real.

## Cards

- Use cards for overview surfaces, mixed content, or small grouped summaries.
- Make the entire card tappable only when the whole surface has one action.
- Do not make every card equal in visual weight if some items are clearly secondary.
- Material-backed cards are optional; use them only when they improve hierarchy and context.

## Canvas-Based Data Visualizations

Canvas is the SwiftUI equivalent of HTML5 Canvas or SVG — GPU-accelerated 2D drawing for custom visualizations that standard controls can't express. Use it for data-rich views that need precise geometric control.

### When to Use Canvas

- **Chart wheels and radial layouts** — radar/spider charts, circular progress, compass views
- **Dense tick marks and grid lines** — degree scales, ruler overlays
- **Custom data plots** — anything requiring precise polar or Cartesian positioning
- **Layered rendering** — when elements must draw in a specific Z-order (background grid → data → labels)

### Radar/Spider Chart Pattern

A 5-axis polygon chart for multi-dimensional scores (skill profiles, fitness metrics, multi-factor ratings):

```swift
Canvas { ctx, size in
    let center = CGPoint(x: size.width / 2, y: size.height / 2)
    let radius = min(size.width, size.height) / 2 - 30

    // 1. Grid rings at 25/50/75/100%
    // 2. Axis lines from center to each vertex
    // 3. Filled data polygon (animated via @State)
    // 4. Data point dots at each vertex
    // 5. Labels at each axis tip
}
.frame(height: 260)
.overlay {
    // Invisible tap targets for each axis — enables drill-down per dimension
    ForEach(0..<5, id: \.self) { i in
        Circle().fill(.clear).frame(width: 60, height: 60)
            .position(/* vertex position */)
            .onTapGesture { selectedDimension = dimensions[i] }
    }
}
```

Key techniques:
- Animate the polygon fill with `@State var appear = false` and `.onAppear { withAnimation(.spring) { appear = true } }`
- Overlay invisible tap targets for interactivity — Canvas itself doesn't handle gestures
- Use `.sensoryFeedback(.impact)` on the animation trigger for haptic confirmation

### Animated Score Ring Pattern

A circular progress indicator with counting animation:

```swift
ZStack {
    Circle().stroke(backgroundTint, lineWidth: 10)
    Circle()
        .trim(from: 0, to: animatedScore / 100)
        .stroke(
            AngularGradient(colors: [color.opacity(0.6), color, color.opacity(0.8)],
                            center: .center, startAngle: .degrees(-90), endAngle: .degrees(270)),
            style: StrokeStyle(lineWidth: 10, lineCap: .round)
        )
        .rotationEffect(.degrees(-90))

    Text("\(Int(animatedScore))%")
        .contentTransition(.numericText(value: animatedScore))
}
.onAppear {
    withAnimation(.spring(duration: 1.2, bounce: 0.15).delay(0.2)) {
        animatedScore = targetScore
    }
}
```

Key techniques:
- `AngularGradient` creates a color sweep along the ring, more premium than flat color
- `.contentTransition(.numericText)` smoothly morphs digits as the counter counts up (iOS 17+)
- `.symbolEffect(.bounce)` on an accompanying SF Symbol label for extra polish

### Gradient Score Bars

Dynamic bar color based on value for instant visual categorization:

```swift
private var barGradient: LinearGradient {
    if value >= 75 { return LinearGradient(colors: [green.opacity(0.8), green], ...) }
    else if value >= 55 { return LinearGradient(colors: [gold.opacity(0.8), gold], ...) }
    else { return LinearGradient(colors: [orange.opacity(0.8), orange], ...) }
}
```

### Semicircular Gauge with Gradient

A traffic-light gauge for ratings/energy levels using `AngularGradient`:

```swift
ZStack(alignment: .bottom) {
    // Smooth red → yellow → green gradient arc
    Circle()
        .trim(from: 0, to: 0.5)
        .stroke(
            AngularGradient(
                colors: [.red, .orange, .yellow, .yellowGreen, .green],
                center: .center,
                startAngle: .degrees(180),
                endAngle: .degrees(0)
            ),
            style: StrokeStyle(lineWidth: 16, lineCap: .round)
        )
        .rotationEffect(.degrees(180))

    // Animated needle (Canvas overlay)
    Canvas { ctx, size in
        let center = CGPoint(x: size.width / 2, y: size.height - 2)
        let angle = 180 - (animatedValue / 100 * 180)
        // ... draw needle line + center dot
    }
}
```

Key rules:
- Use `AngularGradient` for smooth color transitions — never use discrete colored segments (looks blocky)
- Animate the needle with `.spring()` for a satisfying sweep
- Show the rating label and description below the gauge
- Map text ratings to numeric values: "excellent" → 90, "good" → 65, "challenging" → 35

### Quadrant Compass Chart

A 4-quadrant circular chart for multi-dimensional daily scores (Energy, Love, Work, Growth):

```swift
Canvas { ctx, size in
    // Background circle + cross lines dividing quadrants
    // 4 filled arcs, each proportional to its score
    // Center circle with overall rating text
    // Quadrant labels + SF Symbol icons at midpoints
}
```

Each quadrant arc fills from center outward based on its score. The visual density communicates "how your day looks" at a glance. Overlay SF Symbol icons (bolt, heart, briefcase, leaf) for instant identification.

### Multi-Layer Canvas (Complex Charts)

For complex radial or multi-layer visualizations (dashboards, multi-ring progress, richly labeled compasses), structure as sequential layer functions:

```swift
Canvas { ctx, _ in
    drawDegreeTicks(ctx, center: center, half: half)   // 360 tick marks
    drawZodiacBand(ctx, center: center, half: half)    // 12-segment ring
    drawHouseCusps(ctx, center: center, half: half)    // Radial dividers
    drawAspectLines(ctx, center: center, half: half)   // Data connections
    drawCenterCircle(ctx, center: center, half: half)  // Center anchor
    drawPlanets(ctx, center: center, half: half)       // Data points
    drawAngles(ctx, center: center, half: half)        // Axis labels
}
```

Each layer function receives the `GraphicsContext` and shared geometry. This keeps the Canvas body readable while supporting 500+ drawing operations in a single GPU pass.

### Comparison Cards with Material Background

Side-by-side comparison using `.ultraThinMaterial`:

```swift
HStack(spacing: 0) {
    comparisonColumn(label: "You", value: userValue)
    Divider()
    comparisonColumn(label: "Other", value: otherValue)
}
.background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
.overlay(RoundedRectangle(cornerRadius: 16).stroke(borderColor, lineWidth: 1))
```

## Interactive Scroll and Animation Patterns

### Scroll Transitions (iOS 17+)

Make sections reveal as they enter the viewport:

```swift
.scrollTransition { content, phase in
    content
        .opacity(phase.isIdentity ? 1 : 0.3)
        .scaleEffect(phase.isIdentity ? 1 : 0.95)
        .offset(y: phase.isIdentity ? 0 : 20)
}
```

Use `.opacity` for subtle reveals, add `.scaleEffect` for hero sections, add `.offset` for cards. Don't combine all three on every element — reserve the most dramatic transitions for key content.

### Expandable Sections with Spring Animation

For content-heavy reports, collapsible sections reduce cognitive load:

```swift
Button {
    withAnimation(.spring(duration: 0.35)) {
        expandedSections.toggle(key)
    }
} label: {
    HStack {
        Image(systemName: symbol).foregroundStyle(tint)
        Text(title)
        Spacer()
        Image(systemName: "chevron.right")
            .rotationEffect(.degrees(isExpanded ? 90 : 0))
    }
}
.sensoryFeedback(.impact(flexibility: .soft, intensity: 0.4), trigger: isExpanded)
```

### Sensory Feedback (iOS 17+)

Add haptics to meaningful interactions — not every tap:

```swift
// Score ring completes animation
.sensoryFeedback(.impact(flexibility: .soft), trigger: appear)

// Section expands/collapses
.sensoryFeedback(.impact(flexibility: .soft, intensity: 0.4), trigger: isExpanded)
```

### SF Symbol Effects (iOS 17+)

Animate SF Symbols for bond types, achievements, or status changes:

```swift
Image(systemName: "sparkles")
    .symbolEffect(.bounce, value: showLabel)
```

## Buttons and Actions

- Keep one clearly primary action per screen where possible.
- Use toolbar actions, menus, and swipe actions to reduce clutter in dense layouts.
- Avoid turning every action into a filled button.
- On iOS 26, prefer `.buttonStyle(.glass)` and `.buttonStyle(.glassProminent)` over manual `.glassEffect()` for buttons (see `ios26-liquid-glass.md`).

## Floating Action Buttons (FABs) — iOS 26

iOS 26 introduced FABs as a first-class iOS pattern, not a Material-only convention (e.g. the compose button in Reminders). Use a FAB when:

- there is exactly one persistent primary action that must be reachable from every list/scroll position
- the action creates *new* content (compose, capture, add) — not navigation, not destructive

Placement and spec:
- bottom-trailing of the safe area, ~16 pt inset from edges, clear of the tab bar
- glass surface: `Button { … }.buttonStyle(.glass)` inside a Capsule or Circle, sized 56–60 pt for the touch target
- on scroll edge, the system applies an automatic blur — don't fight it with manual gradients
- always include a VoiceOver label and SF Symbol; never label-less
- never add a second FAB or a stacked FAB cluster — that breaks the one-primary-action rule

Anti-pattern: using a FAB for navigation, settings, or filters. If it isn't a creation action, use a toolbar button.

## Action Sheets — iOS 26 placement change

`.confirmationDialog` and Apple's `Menu` now anchor near the triggering control rather than at the bottom of the screen. Design specs that assume bottom-anchored sheets need updating:
- the menu/sheet appears next to the source button on iPhone (still bottom-aligned on smallest sizes)
- ensure the source button is positioned where there is room above and below for the menu to fan out
- destructive actions remain at the bottom of the menu; do not reorder

## Search, Filters, and Secondary Controls

- Prefer standard search placement and native filter presentation. iOS 26 canonicalised the *bottom* search bar for apps without a tab bar (Settings-style, NavigationSplitView on iPhone). Use `.searchable(text:placement:.toolbar)` with the iOS 26 default placement and trust the system.
- Use segmented controls for small peer switches within one screen, not for whole-app navigation.
- Use inspectors, sidebars, or split view on larger devices when the extra structure is genuinely helpful.

## iOS 26 Pattern Updates (non-glass)

Beyond Liquid Glass, iOS 26 changed several pattern defaults. Update specs accordingly:

| Pattern | iOS 25 default | iOS 26 default |
|---------|----------------|----------------|
| List section headers | ALL CAPS | Sentence case, larger size |
| Alert text | Center-aligned | Left-aligned |
| Toolbar title | Title only | Title + optional subtitle (left-aligned) |
| Search placement (no tab bar) | Top of nav | Bottom of nav |
| Action sheet anchor | Bottom of screen | Near triggering control |
| Scroll edge | Hard chrome boundary | Automatic blur on scroll-edge content |
| Back button | "< Back" with label | Glyph-only by default (Apple removed labels in many first-party apps; NN/g flagged this as an anti-pattern for unfamiliar destinations — keep the label when destination naming is non-obvious) |

**Forward note (announced, not shipped):** WWDC26 (June 2026) previewed iOS 27 reversing the search-placement row above — search moves back into the tab bar rather than sitting as a separate bottom-right affordance. Treat this as beta-only guidance until iOS 27 ships; design specs targeting current iOS 26 should keep the bottom-of-nav placement above.

## FlowLayout (Wrapping Pills)

iOS has no built-in wrapping layout. Use the `Layout` protocol (iOS 16+) for centered-row keyword pills, tags, or chip collections:

```swift
struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let rows = computeRows(proposal: proposal, subviews: subviews)
        let height = rows.reduce(CGFloat(0)) { total, row in
            total + row.height + (total > 0 ? spacing : 0)
        }
        return CGSize(width: proposal.width ?? 0, height: height)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let rows = computeRows(proposal: proposal, subviews: subviews)
        var y = bounds.minY
        for row in rows {
            let totalWidth = row.sizes.reduce(CGFloat(0)) { $0 + $1.width }
                + CGFloat(row.sizes.count - 1) * spacing
            var x = bounds.midX - totalWidth / 2
            for (index, size) in row.sizes.enumerated() {
                subviews[row.startIndex + index]
                    .place(at: CGPoint(x: x, y: y), proposal: ProposedViewSize(size))
                x += size.width + spacing
            }
            y += row.height + spacing
        }
    }

    private struct Row {
        var startIndex: Int
        var sizes: [CGSize]
        var height: CGFloat { sizes.map(\.height).max() ?? 0 }
    }

    private func computeRows(proposal: ProposedViewSize, subviews: Subviews) -> [Row] {
        let maxWidth = proposal.width ?? .infinity
        var rows: [Row] = []
        var currentRow = Row(startIndex: 0, sizes: [])
        var currentWidth: CGFloat = 0

        for (index, subview) in subviews.enumerated() {
            let size = subview.sizeThatFits(.unspecified)
            let needed = currentRow.sizes.isEmpty ? size.width : size.width + spacing
            if currentWidth + needed > maxWidth, !currentRow.sizes.isEmpty {
                rows.append(currentRow)
                currentRow = Row(startIndex: index, sizes: [size])
                currentWidth = size.width
            } else {
                currentRow.sizes.append(size)
                currentWidth += needed
            }
        }
        if !currentRow.sizes.isEmpty { rows.append(currentRow) }
        return rows
    }
}
```

Usage with `.fixedSize()` on each child to prevent line-breaking inside pills:

```swift
FlowLayout(spacing: 8) {
    ForEach(keywords, id: \.self) { keyword in
        Text(keyword)
            .font(.caption)
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(surfaceColor)
            .clipShape(Capsule())
            .fixedSize()
    }
}
```

Key detail: without `.fixedSize()`, multi-word pills (e.g., "recently added") will line-break inside their capsule instead of wrapping to the next row.

## Immersive Visualization Screen

A third screen archetype alongside dashboards and narrative readings. Used when the visualization IS the experience — radial dashboards, 3D scenes, map-based data, generative canvases.

### Structure

```
ZStack {
    AtmosphericBackground()         // full-bleed atmospheric background
    VStack(spacing: 8-10) {
        ZStack {
            Visualization(...)      // Canvas, SceneKit, MapKit — no height constraint, fills space
            infoBadge               // floating glass capsule (top-leading)
        }
        controlsStrip               // native Picker(.segmented) + body selector row
        timelineSlider              // inline, compact — NOT in sheet
            .padding(.bottom, peekHeight)
    }
    .sheet(isPresented: $showPanel) {
        DetailPanel(...)
            .presentationDetents([.customPeek, .medium, .large])
            .presentationBackgroundInteraction(.enabled(upThrough: .medium))
            .interactiveDismissDisabled(true)
    }
    .onAppear { showPanel = true }
}
.navigationBarTitleDisplayMode(.inline)
.toolbarColorScheme(.dark, for: .navigationBar)
.toolbarBackground(.hidden, for: .navigationBar)
```

### Key Principles

1. **No card wrappers** — visualization renders edge-to-edge, no outer card, panel, or scroll-screen chrome
2. **No scroll** — the screen is a fixed viewport with floating overlays, not a scrollable document
3. **Native controls for mode switching** — `Picker(.segmented)` for primary modes, `Menu` for overflow actions. Not custom material-backed buttons
4. **Shared ButtonStyle for selector cells** — reusable `ButtonStyle` with active/inactive states, press scale (0.92), accent glow. Consistent across all immersive screens
5. **Temporal controls stay visible** — timeline sliders, scrubbers, and playback controls belong in the main layout, not hidden in sheets
6. **Persistent sheet for detail** — always-present bottom sheet with custom peek detent for summary, medium for full detail
7. **Haptics on every meaningful interaction** — `.sensoryFeedback(.selection, trigger:)` on mode changes, selections, toggles

### Controls Strip Pattern

```swift
VStack(spacing: 8) {
    // Row 1: Segmented mode picker + overflow menu
    HStack(spacing: 8) {
        Picker("Mode", selection: $mode) {
            Text("Option A").tag(Mode.a)
            Text("Option B").tag(Mode.b)
            Text("Option C").tag(Mode.c)
        }
        .pickerStyle(.segmented)

        Menu { /* overflow actions */ } label: {
            Image(systemName: contextualIcon)
                .frame(width: 36, height: 36)
        }
    }

    // Row 2: Scrollable body/entity selector
    ScrollView(.horizontal, showsIndicators: false) {
        HStack(spacing: 5) {
            ForEach(items) { item in
                Button { select(item) } label: {
                    Text(item.symbol).frame(width: 36, height: 36)
                }
                .buttonStyle(EntityCellButtonStyle(isActive: item == selected))
                .sensoryFeedback(.selection, trigger: item == selected)
            }
        }
    }
}
```

### When to Use

| Screen | Archetype | Why |
|--------|-----------|-----|
| Radial dashboard / chart wheel | Immersive | Complex Canvas radial visualization needs full screen |
| Solar 3D | Immersive | SceneKit scene needs edge-to-edge depth |
| Astrocartography map | Immersive | MapKit needs full viewport for spatial context |
| Best Days calendar | Dashboard | Grid + terrain are content, not the entire experience |
| Horoscope reading | Guidance | Editorial prose flow, not a single visualization |
| Settings | Dashboard | Standard iOS list structure |

### Visualization-Specific Layout Considerations

Different visualizations have different sizing and interaction needs within the immersive archetype:

| Visualization | Aspect ratio | Zoom buttons | Controls strip role |
|---|---|---|---|
| Radial chart (dashboard/compass) | `1:1` (square, `.aspectRatio(1, contentMode: .fit)`) | In controls strip (zoom +/−) | Focus mode + entity selection + zoom |
| 3D scene | Fills available space | In overflow menu (reset only) | Camera preset + playback + entity selection |
| Map | `1.4:1` (landscape, `.aspectRatio(1.4, contentMode: .fit)`) | Built-in overlay on the map (top-trailing) | Data filters + search |

#### Map-Specific Patterns

Maps differ from charts and 3D scenes because they are spatial navigation experiences (like Apple Maps), not static diagrams to inspect:

- **Grid lines extend full-bleed** — draw from `0` to `size.width`/`size.height`, not from `padding` to `size - padding`. Stopping at a padding boundary creates a visible rectangular "border" that breaks edge-to-edge immersion.
- **Built-in zoom buttons overlay the map** — the standard map pattern (MapKit, Apple Maps, Google Maps) places +/−/reset controls top-trailing inside the map view, not in the external controls strip. This keeps spatial navigation self-contained.
- **Map views own zoom/pan state internally** — continuous pinch-zoom and pan need zero-latency gesture response. A `@Binding` round-trip adds perceptible lag. The parent uses a reset token to trigger resets without lifting all state. See `software-ios-native` → `swiftui-observation-concurrency.md` → "Visualization state ownership" for the full decision tree.
- **Controls strip filters data, not view** — for maps, the segmented picker and body cells toggle what data is shown (layers, categories), not how the view is displayed (zoom, pan). This is the opposite of chart screens where the controls strip manipulates view state.
- **Search field in the controls strip** — maps uniquely need location search. Add a search row above the segmented picker, styled with the same `cornerRadius` and fill as the body cells so it reads as part of the strip, not a foreign element.
- **Suggestion dropdown as floating overlay** — search suggestions overlay the map via a `ZStack`, using `.ultraThinMaterial` background. Do not push suggestions into the scroll content or the sheet.
