# iOS Dashboard Design

## Table of Contents

- [Dashboard Principles](#dashboard-principles)
- [A Practical Hierarchy](#a-practical-hierarchy)
- [Useful Heuristics](#useful-heuristics)
- [When to Use Horizontal Collections](#when-to-use-horizontal-collections)
- [Data Display Patterns](#data-display-patterns)
- [Card Hierarchy on Dashboards](#card-hierarchy-on-dashboards)
- [Dual-View Dashboard Pattern](#dual-view-dashboard-pattern)
- [Visual Guidance Cards](#visual-guidance-cards)
- [Domain Notes](#domain-notes)

Use this reference for overview screens that summarize multiple content types or decisions.

## Dashboard Principles

- Make one thing win first attention.
- Show summaries first and let users drill into detail.
- Keep the first viewport scannable; if everything above the fold competes equally, the dashboard is not prioritized enough.
- Prefer native structure over novelty. A dashboard can still feel iOS-native if it uses standard navigation, text styles, actions, and materials carefully.

## A Practical Hierarchy

- Hero: the most important thing right now
- Primary context: two or three supporting items
- Secondary context: recommendations, history, or quick actions
- Tertiary detail: deeper data that can live below the fold or in a separate destination

## Useful Heuristics

- Treat 5-6 visible cards on a phone as a warning threshold for overview screens, not a hard limit.
- If two cards say almost the same thing, merge them.
- If a “quick action” is rarely used, move it to a menu or secondary destination.
- If multiple modules are equally large, one of them is probably missing a demotion.

## When to Use Horizontal Collections

- Use a horizontal row when several peer items deserve equal weight and users may browse them.
- Show enough of the next item to signal that the row scrolls.
- Avoid horizontal collections when the items are text-heavy or need comparison.

## Data Display Patterns

### Compact Data Grids

For 3-5 related values (placements, stats), use contained cells in a horizontal grid rather than label-value rows:

- 3-column grid for short values (Sun/Moon/Rising)
- 2-column grid for wider values (Overall rating, Timing)
- Each cell: icon + label on top, value below, subtle background, rounded corners
- `minimumScaleFactor(0.8)` handles occasional long values; prefer reflowing the layout over scaling text aggressively

### Contained Action Rows

For actionable guidance (Do/Don't, Best move/Avoid), use VStack layout with background:

- Colored dot + uppercase label on top
- Description text below
- `surfaceInset` background with rounded corners
- Reuse one component for all action rows across cards

### What NOT to Do

- Fixed-width label columns (`frame(width: 84)`) — creates uneven whitespace when labels vary
- Bare HStack label-value rows without visual boundaries — data floats
- Mixing different row patterns in the same card without visual separation

## Card Hierarchy on Dashboards

- **Hero card**: Larger radius, more padding, one per screen
- **Primary cards**: Standard radius, standard padding, 2-3 per screen
- **Inset rows within cards**: Tighter padding, inset surface, for nested data
- Use thin 1px dividers to separate content types within a single card instead of splitting into more cards

## Dual-View Dashboard Pattern

For data-rich apps (health, finance, productivity, analytics), offer two dashboard views via a segmented picker at the top. Each view shows the same data with different information density:

- **Guide view** (detail-oriented): individual cards for each data element — moon phase, energy gauge, guidance cards, decision signals. Users who plan their day prefer this.
- **Compass view** (glanceable): one hero Canvas visualization that encodes multiple dimensions into a single chart. Users who check quickly prefer this.

```swift
Picker("View", selection: $viewMode) {
    ForEach(DashboardViewMode.allCases) { Text($0.rawValue).tag($0) }
}
.pickerStyle(.segmented)
```

Rules:
- Shared elements (quick links, social card) appear below both views
- Each view computes from the same `snapshot` — no separate API calls
- Name the views by function ("Guide" / "Compass"), not by technology ("Weather" / "Chart")

## Visual Guidance Cards

### Symmetric Action Card Pairs (Do / Avoid)

When showing two opposing guidance cards side-by-side, enforce identical geometry:

```swift
func guidanceCard(type: GuidanceType, headline: String) -> some View {
    VStack(alignment: .leading, spacing: 10) {
        HStack(spacing: 8) {
            Image(systemName: type.symbol).foregroundStyle(type.tint)
            Text(type.label.uppercased()).font(.eyebrow).foregroundStyle(type.tint)
            Spacer()
        }
        Text(headline).lineLimit(3).fixedSize(horizontal: false, vertical: true)
    }
    .frame(maxWidth: .infinity, minHeight: 90, alignment: .topLeading)
    .padding(20)
    .background(type.tint.opacity(0.06))
    .overlay(RoundedRectangle(...).stroke(type.tint.opacity(0.15)))
}
```

Key rules:
- Use `minHeight` to enforce equal card size regardless of text length
- Use `lineLimit(3)` to cap text — detail goes in the tap-to-expand sheet
- Color the card background with the action tint at low opacity (6%) for instant visual categorization
- Both cards are tappable → open detail sheet with full item lists

### Prefer SF Symbols for Stateful Glyphs

Before drawing custom Canvas glyphs for stateful indicators (phases, battery states, weather conditions, signal bars, directions), check SF Symbols first. Apple ships pixel-perfect multi-state symbols that scale and tint correctly:

```swift
Image(systemName: stateSymbol)         // e.g., "wifi", "wifi.slash", "battery.50"
    .font(.system(size: 56))
    .foregroundStyle(.secondary)
    .symbolRenderingMode(.hierarchical)
```

Use `symbolRenderingMode(.hierarchical)`, `.palette`, or `.multicolor` for richer states without custom drawing. Canvas is for visualizations SF Symbols cannot express (custom radial charts, data terrain, multi-layer plots) — not for single glyphs.

### Gauge with Gradient Arc

For energy/rating gauges, use a smooth `AngularGradient` from red → yellow → green instead of discrete colored segments:

```swift
Circle()
    .trim(from: 0, to: 0.5)
    .stroke(
        AngularGradient(
            colors: [.red, .orange, .yellow, .yellowGreen, .green],
            center: .center, startAngle: .degrees(180), endAngle: .degrees(0)
        ),
        style: StrokeStyle(lineWidth: 16, lineCap: .round)
    )
    .rotationEffect(.degrees(180))
```

Overlay a Canvas needle that animates with `.spring()`. Show the rating label below with color matching the needle's position on the gradient.

### Score Scale Detection

APIs may return scores on different scales (0-10 vs 0-100). Auto-detect:

```swift
let maxScore: Double = score > 10 ? 100 : 10
Circle().trim(from: 0, to: animatedScore / maxScore)
```

## Domain Notes

- Content-heavy apps (health, finance, productivity, wellness) often accumulate too many overview modules.
- In those apps, the main design job is prioritization, not decoration.
- Prefer compact summary rows, a single hero panel, and clearer destinations over a stack of equally styled cards.
- For dashboards where users need direction rather than raw data, frame outputs as **guidance** (what to do, what to avoid) expressed **visually**, not as a data dump. Every visual element should answer a question the user has.
