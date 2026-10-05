# Design Craft Patterns

Battle-tested patterns for building high-end, precise iOS interfaces. These are practical fixes for common design problems, not abstract principles.

## Table of Contents

- [Detail Sheet Pattern](#detail-sheet-pattern)
- [Design Token Discipline](#design-token-discipline)
- [Data Containment](#data-containment)
- [Visual Anchoring](#visual-anchoring)
- [Card Hierarchy](#card-hierarchy)
- [Dark Theme Patterns](#dark-theme-patterns)
- [Competitor Pattern Analysis](#competitor-pattern-analysis)
- [Symmetric Card Pairs](#symmetric-card-pairs)
- [Localization Visual Audit](#localization-visual-audit)

## Detail Sheet Pattern

### The Rule

All secondary detail content uses a consistent "popup from the bottom" interaction. Never show deep detail inline in a scroll view — it clutters the screen and breaks scannability.

### How It Works

1. **Compact tappable row** in a `List(.insetGrouped)`:
   ```swift
   Button { selectedSection = .sky } label: {
       LabeledContent {
           HStack(spacing: 6) {
               Text(summaryValue)
               Image(systemName: "chevron.right")
                   .font(.caption2)
                   .foregroundStyle(.secondary)
           }
       } label: {
           Label("Your sky", systemImage: "sparkles")
       }
   }
   .buttonStyle(.plain)
   ```

2. **Native `.sheet`** triggered by selection:
   ```swift
   .sheet(item: $selectedSection) { section in
       NavigationStack {
           List { /* full detail content */ }
               .listStyle(.insetGrouped)
               .scrollContentBackground(.hidden)
               .navigationTitle(section.title)
               .navigationBarTitleDisplayMode(.inline)
       }
       .presentationDetents([.medium, .large])
       .presentationDragIndicator(.visible)
   }
   ```

3. **Hero content stays inline** — headlines, summaries, key metrics that define the screen's purpose remain in the main scroll. Only secondary detail (lists of items, expanded data) moves into sheets.

### When to Use Sheets vs Inline

| Content | Treatment |
|---------|-----------|
| 1-2 key values (date, status) | Inline `LabeledContent` |
| Summary text (1 paragraph) | Inline in section |
| List of 3+ items | Compact row → sheet |
| Expandable data (long nested content, activity history) | Compact row → sheet |
| Charts and visualizations | Inline (hero visual) |
| Upgrade/locked prompts | Inline |

### Expandable Section Pattern (Alternative to Sheets)

For data-dense reports with 5+ sections (analysis views, multi-section summaries), expandable sections can be better than sheets — they keep context visible while reducing initial scroll depth:

```swift
VStack(alignment: .leading, spacing: 0) {
    Button { withAnimation(.spring(duration: 0.35)) { toggle(key) } } label: {
        HStack {
            Image(systemName: symbol).foregroundStyle(tint)
            Text(title).font(.headline)
            Spacer()
            Image(systemName: "chevron.right")
                .rotationEffect(.degrees(isExpanded ? 90 : 0))
        }
        .padding(20)
    }
    .sensoryFeedback(.impact(flexibility: .soft, intensity: 0.4), trigger: isExpanded)

    if isExpanded {
        content
            .padding(.horizontal, 20).padding(.bottom, 20)
            .transition(.opacity.combined(with: .move(edge: .top)))
    }
}
.background(panelBackground, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
```

Use expandable sections when:
- The report has 5+ distinct data sections
- Users typically scan 2-3 sections, not all of them
- The content is supplementary rather than primary (keep the primary content, e.g., score and summary, inline and uncollapsed)

### Anti-Patterns

- DisclosureGroup for deep content — hard to scan, expands inline, pushes content below the fold
- Inline cards with full detail — steals vertical space from other sections
- NavigationLink push for simple detail — too heavy for data that doesn't need its own screen
- Showing all items when only a count matters — show count + chevron, full list in sheet
- Flat list of all sections with equal weight — use animated score rings and radar charts as hero content, push secondary content into expandable sections

## Design Token Discipline

### The Rule

Every magic number in a screen file should trace back to a named token in the design system. If a value appears in two places, it needs a name.

### What to Tokenize

| Category | Examples | Why |
|----------|----------|-----|
| Spacing | Screen padding, card internal padding, section gaps, control gaps | Prevents drift between screens |
| Typography | Card eyebrow font, icon label font, hero display font — any `.font(.system(size:weight:))` repeated 3+ times | One change updates every section header |
| Tracking (letter-spacing) | Screen-level eyebrows vs card-level eyebrows vs labels | Documents intentional hierarchy |
| Corner radii | Panel, card, control, row, compact cell | Ensures consistent shape language |
| Colors | All surfaces, text levels, accents, status colors | Single source of truth for theming |
| UIColor bridge | Tab bar, navigation bar appearance via UIKit | Prevents UIColor literals from drifting from SwiftUI palette |

### Token Hierarchy Pattern

Name tokens by semantic role, not by value:

```
screenEyebrow (1.2) > heroEyebrow (1.1) > cardEyebrow (0.9) > label (0.8)
cardContentHero (24) > cardContentCompact (22) > cardContent (20) > listRowContent (16)
```

This makes the hierarchy self-documenting. A developer reading `Tracking.heroEyebrow` immediately understands the intent.

### Common Anti-Pattern: Hardcoded Values

Audit for these patterns in screen files:
- `.padding(22)` — should be a named spacing token
- `.tracking(0.8)` — should be a named tracking token
- `.font(.system(size: 10, weight: .bold))` — if repeated 3+ times, extract to a typography token
- `UIColor(red: 0.90, green: 0.75, ...)` — should bridge from the SwiftUI color palette

Run `grep -E '\.padding\(\d\d\)|\.tracking\(\d|\.font\(\.system\(size:|UIColor\(red:' Features/` to find violations.

## Data Containment

### The Problem

Data that "floats" in a card — label-value rows with no visual boundaries — looks mechanical and undesigned. Fixed-width label columns create uneven whitespace when labels vary in length.

### The Fix: Grid Cells

For compact, scannable data (placements, stats, ratings), use contained cells in a grid:

```swift
VStack(alignment: .leading, spacing: 6) {
    HStack(spacing: 5) {
        Image(systemName: symbol)
            .font(.system(size: 10, weight: .semibold))
            .foregroundStyle(tint)
        Text(label.uppercased())
            .font(.caption.weight(.semibold))
            .foregroundStyle(tint)
    }
    Text(value)
        .font(.subheadline)
        .foregroundStyle(primaryTextColor)
        .lineLimit(1)
        .minimumScaleFactor(0.8)
}
.frame(maxWidth: .infinity, alignment: .leading)
.padding(.horizontal, 12)
.padding(.vertical, 10)
.background(subtleSurfaceColor)
.clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
```

Arrange 3 cells in an `HStack(spacing: 8)` for compact data grids. For wider content, use 2 cells per row.

### The Fix: Contained Action Rows

For actionable items (Do/Don't, Best move/Avoid), use a vertical layout with a background:

```swift
VStack(alignment: .leading, spacing: 6) {
    HStack(spacing: 6) {
        Circle()
            .fill(tint)
            .frame(width: 6, height: 6)
        Text(label.uppercased())
            .font(.caption.weight(.semibold))
            .foregroundStyle(tint)
    }
    Text(description)
        .font(.subheadline)
        .foregroundStyle(secondaryTextColor)
        .fixedSize(horizontal: false, vertical: true)
}
.padding(16)
.frame(maxWidth: .infinity, alignment: .leading)
.background(insetSurfaceColor)
.clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
```

### When NOT to Contain

- Short, homogeneous key-value pairs in a compact list (settings rows) — use native `List` or simple `VStack`
- Single-line metadata — containment adds visual noise without benefit

## Visual Anchoring

### The Problem

Screens that are 100% text feel flat, even with good typography. Well-designed apps add visual focal points — illustrations, icons, phase strips, small thematic graphics — that create scannable anchor points.

### SF Symbol Anchoring

Add small SF Symbols to data labels for faster scanning:

- Status → `checkmark.circle.fill`
- Rating → `chart.bar.fill`
- Location → `mappin.and.ellipse`
- Time → `clock.fill`
- Category label → a domain-appropriate symbol (e.g., `briefcase.fill` for work, `heart.fill` for health)

Keep icons at 10-12pt, same weight as label text, tinted to match the label color. The icon should support the label, not compete with it.

### Colored Dot Indicators

For categorized lists (Do/Mindful, Go/Caution), add a 6pt colored circle before the label. This creates instant visual categorization without reading the text:

- Green dot → positive/do items
- Orange dot → caution/mindful items
- Red dot → avoid items

### What NOT to Add

- Decorative icons that don't convey meaning
- Icons on every single text element (visual noise)
- Large illustrations in data-heavy screens (competes with content)

## Card Hierarchy

### The Pattern

Not all cards should look the same. A dashboard needs visual hierarchy between cards:

| Level | Treatment | Example |
|-------|-----------|---------|
| Hero | Larger corner radius (28), more internal padding (24), full panel treatment | Today's headline card |
| Primary | Standard card radius (24), standard padding (22), panel background | Sky data, Guidance |
| Secondary | Inset surface background, tighter padding (16), control radius (18) | Action rows within cards, decision cards |

### Card Separation

When a card contains two distinct content types (e.g., data grid + action rows), separate them with a thin divider:

```swift
Rectangle()
    .fill(strokeColor)
    .frame(height: 1)
```

This is cheaper than splitting into two cards and keeps the card count manageable (HIG heuristic: 5-6 visible cards is a warning threshold).

## Dark Theme Patterns

### Surface Layering

Build depth with subtle opacity differences, not separate RGB values for each layer:

```
Background:     RGB(0.04, 0.05, 0.09) — near-black
Surface:        RGB(0.10, 0.12, 0.19) @ 88% — card background
Surface Strong: RGB(0.13, 0.15, 0.23) @ 96% — prominent card
Surface Inset:  RGB(0.16, 0.18, 0.27) @ 95% — nested container
Surface Soft:   White @ 6% — minimal, for grid cells
```

Each layer is slightly lighter than the previous, creating physical depth.

### Text Hierarchy in Dark

Three text levels are sufficient:

```
Primary:   RGB(0.97, 0.96, 0.94) — warm off-white, not pure white
Secondary: White @ 72% — supporting text
Muted:     White @ 52% — disabled/tertiary
```

Pure white (#FFFFFF) is harsh on dark backgrounds. Use warm off-white for primary text.

### Accent Strategy

Reserve accent colors for interactive elements and categorization, not decoration:

- Primary accent (warm gold) → CTAs, active states, primary labels
- Secondary accent (cool blue) → alternative actions, secondary data
- Status colors (green/orange/red) → semantic meaning only

### Glow and Atmosphere

For atmospheric themes (wellness, mood, ambient-first apps), add subtle atmospheric glows behind the content layer:

- Top-left: Purple/blue blurred circle (320px, blur 56, ~22% opacity)
- Bottom-right: Orange/warm blurred circle (280px, blur 64, ~18% opacity)

Keep these behind all content. They should create mood, not interfere with readability.

## Competitor Pattern Analysis

### Methodology

When studying competitor apps:

1. Focus on the **home/daily screen** first — this is where design quality matters most
2. Study their **data display patterns** — how do they show placements, ratings, guidance?
3. Note their **visual anchoring** — what creates the focal point?
4. Look at their **containment** — do items float or have clear boundaries?
5. Check their **information density** — how many items compete above the fold?

### Patterns Worth Studying (examples from best-in-class iOS apps)

- **Editorial sparsity**: One big centered headline, minimal chrome (useful when the screen's primary job is emotional/narrative, not data)
- **Terse paired columns**: Do/Don't-style columns with 1–3-word items, no containment needed because content is short
- **Inline summaries**: Compact single-line summaries with symbol + label + value on one row (e.g., the Weather app's daily summary pill)
- **Category chips**: Horizontal row of short-word categories acting as a high-level router above content
- **Icon-labeled activity indicators**: Every data point gets a small SF Symbol for faster scanning
- **Visual strips**: Horizontal row of phase/progress/time icons as scannable visual anchors
- **Illustrated hero cards**: Rich visuals for feature entry points where the visual *is* the affordance
- **Horizontal card rails**: For discovery browsing of peer items — avoid for primary navigation

### When to Borrow

Borrow a pattern when:
- It solves a **specific visual problem** you have (floating text, flat hierarchy)
- It works with **your content density** (a sparse style breaks with long text; a dense grid breaks with short copy)
- It can be implemented with **standard SwiftUI** (no custom rendering engine)

Do not borrow:
- Entire visual identities (keep your own brand)
- Patterns that require different content structure than you have
- Effects that are purely decorative

## Symmetric Card Pairs

### The Problem

Side-by-side cards with different-length text create uneven heights, breaking visual symmetry. One card dominates, making the pair feel unbalanced.

### The Fix

Enforce identical geometry with `minHeight` and `lineLimit`:

```swift
HStack(spacing: 12) {
    guidanceCard(type: .bestMove, headline: shortText)
    guidanceCard(type: .avoid, headline: longerText)
}

// Inside guidanceCard:
.frame(maxWidth: .infinity, minHeight: 90, alignment: .topLeading)
.lineLimit(3)  // Cap inline text; full content in detail sheet
```

Rules:
- Both cards share the same `minHeight` — cards stretch to equal size
- Use `lineLimit` to prevent one card from growing unbounded
- Move full content to a tap-to-expand sheet
- Color each card with its semantic tint at low opacity (6%) for instant categorization
- Never use different structures (e.g., one card with an icon and one without)

### When to Use

- Do/Don't, Best Move/Avoid, Pro/Con pairs
- Any two cards that are conceptual opposites and should feel balanced
- Comparison cards (You vs Friend, Before vs After)

## Localization Visual Audit

### The Rule

Every user-facing string must go through the localization system, even placeholder text. This is not just about translation — it ensures:

- Future language support works without code changes
- Arabic RTL layout can be tested
- Longer translated strings don't break fixed-width layouts

### Fixed-Width Label Anti-Pattern

Never use `frame(width: 84)` for labels that will be translated. "Sun" is 3 characters in English but "Soleil" is 6 in French and "الشمس" is RTL in Arabic.

Use flexible layouts instead:
- Grid cells that expand to fill available width
- VStack layouts where label sits above value
- `minimumScaleFactor` for tight spaces

### Localization Smoke Test Languages

Spot-check layouts with at least these three scenarios:
- **German** (+30-50% string length) — exposes truncation and label overflow
- **Arabic** (RTL) — exposes hardcoded leading/trailing assumptions and mirroring gaps
- **Japanese/Chinese** (CJK) — exposes fixed-height assumptions and proportional metrics differences

