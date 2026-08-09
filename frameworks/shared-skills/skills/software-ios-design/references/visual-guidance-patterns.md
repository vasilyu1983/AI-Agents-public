# Visual Guidance Patterns

## Table of Contents

- [Principle: Visual Guidance, Not a Data Dashboard](#principle-visual-guidance-not-a-data-dashboard)
- [Screen Archetypes](#screen-archetypes)
- [Canvas Terrain (Temporal Energy / Flow)](#canvas-terrain-temporal-energy--flow)
- [Canvas Ring (Annual / Cyclical Flow)](#canvas-ring-annual--cyclical-flow)
- [Opportunity Framing](#opportunity-framing)
- [Narrative Scroll Flow](#narrative-scroll-flow)
- [Bottom Sheet for Detail](#bottom-sheet-for-detail)
- [Canvas Gantt / Timeline](#canvas-gantt--timeline)
- [Vertical Dot Timeline](#vertical-dot-timeline)
- [Do / Mindful Guidance Cards](#do--mindful-guidance-cards)
- [Narrative Reading Style](#narrative-reading-style)

Patterns for screens that communicate *guidance* or *narrative state* rather than analytical data. Think of surfaces that answer "what does this mean for me?" or "what should I do?" rather than "what are the numbers?"

Applies broadly to weather, wellness, meditation, finance-coaching, habit, health-summary, and any "editorial dashboard" app.

## Principle: Visual Guidance, Not a Data Dashboard

The screen should read like a forecast, not a spreadsheet. Answer "what does this feel like?" before "what are the numbers?"

## Screen Archetypes

Three distinct screen types serve different content:

| Archetype | When | Structure |
|---|---|---|
| Dashboard | Hub screens, settings, data lists | `List(.insetGrouped)` or a scroll of cards |
| Narrative / Guidance Reading | Long-form summaries, daily briefings, recommendations | Scroll with hero symbol, serif text, ring/orb indicators |
| Immersive Visualization | Radial charts, 3D scenes, maps | Full-bleed rendering + floating controls + persistent sheet |

For the immersive visualization pattern, see [ios-component-patterns.md](ios-component-patterns.md#immersive-visualization-screen).

## Canvas Terrain (Temporal Energy / Flow)

Use a `Canvas`-drawn mountain/wave terrain instead of a calendar grid when the user should perceive *flow* over time (energy, mood, workload, intensity) rather than discrete day-by-day values:

- X axis: time (days 1…N), Y axis: value 0–10 via Catmull-Rom spline for smooth curvature
- Color each column by quality tier (gradient heat-map effect — cooler at low values, warmer at high)
- "TODAY" (or equivalent anchor) as a gold dashed vertical marker
- `DragGesture` for scrubbing with `.sensoryFeedback(.selection)` on each boundary crossing
- Preview/locked days at 20% opacity (shape visible, detail locked behind upgrade)

Pair with a calendar grid below for precise selection — grids beat carousels for spatial context.

## Canvas Ring (Annual / Cyclical Flow)

Use a 12-segment annular ring instead of a bar chart for yearly or cyclical value:

- Each segment represents a period (month, week, cycle)
- Fill radius proportional to value
- Color by tier
- Event markers on the outer ring edge for key dates
- Period label or number centered
- Tap/drag to select period with haptic feedback

## Opportunity Framing

Reframe clinical tiers with empowering language. This applies to any screen where numeric ratings or neutral-clinical terms would feel cold:

| Clinical | Opportunity | Frame |
|---|---|---|
| Best / High | Peak Energy | Opportunity window |
| Great | High Flow | Momentum |
| Good | Steady Current | Grounded action |
| Neutral | Quiet Period | Steady presence |
| Challenging | Growth Period | Inner strength |
| Avoid / Low | Reflection Period | Rest and recharge |

Principle: map numeric ranges to qualitative labels in gauges, compasses, and score indicators. "Strong" beats "90", "Rising" beats "72", "Steady" beats "55". Numbers still appear for users who want precision, but the dominant reading is the word.

### Phase / State Framing

Apply the same principle to any state progression (lifecycle stages, status indicators, multi-step processes):

| Clinical | Guidance | Tone |
|---|---|---|
| Paused / Halted | Reflection Period | Pause, review, revisit |
| Pre-start | Preparing | Prepare, back up, clarify |
| Cooldown | Integration Phase | Lessons settling, momentum returns |
| Active / Running | Clear Path | Forward motion, initiate |

For phases without inherent user action, group them into a compact summary (e.g., "Three items — Clear Path") instead of giving each its own card. Reserve individual guidance cards for phases that need user attention.

## Narrative Scroll Flow

Use `ScrollView > LazyVStack` with `.scrollTransition` for guidance screens:

1. Hero header (eyebrow + summary narrative)
2. Canvas visualization (terrain or ring)
3. Selector control (calendar grid or period chips)
4. Guidance card (selected item detail as bottom sheet)
5. Highlight pills (key events in horizontal scroll)
6. Premium gate (if applicable)

Reserve `List(.insetGrouped)` for settings-style hub screens.

## Bottom Sheet for Detail

Day/period detail should pop up from bottom (`.presentationDetents([.medium, .large])`), not expand inline:

- Users expect detail to be a focused, dismissible view
- Inline expansion pushes content below the fold unpredictably
- Bottom sheets support both quick glance (.medium) and deep dive (.large)

## Canvas Gantt / Timeline

Use a `Canvas`-drawn Gantt chart for showing temporal phases across multiple entities (project timelines, subscription periods, multi-stream status tracking):

- Left column: entity labels drawn via `context.draw(resolvedText, at:)` (monospaced, abbreviated)
- Right area: time-based grid with period/week headers and vertical hairlines at boundaries
- Per-entity row: rounded rect phase bars drawn as `Path` fills, colored by phase type
- "NOW" marker: gold dashed vertical line spanning full chart height (`StrokeStyle(lineWidth:, dash:)`)
- Animated entrance: bars grow from left via `animatedProgress` multiplier on bar widths (spring animation)
- `DragGesture` overlay for period scrubbing with `.sensoryFeedback(.selection)` on boundary crossings
- `SpatialTapGesture` for entity row selection — compute row index from y-coordinate against known row height
- Opportunity-framed legend labels (use guidance tone, not clinical terminology)

The Gantt beats a table when the user needs to see temporal overlap and density across entities.

## Vertical Dot Timeline

Use a vertical connected-dot timeline for showing progression through sequential phases:

- Each phase: colored `Circle` (10pt default, 14pt for current) + label + date
- Current phase: larger dot with glowing ring overlay (`Circle().stroke(color.opacity(0.4), lineWidth: 3)`)
- Connecting line: 1pt `Rectangle` between dots in card stroke color
- Container: panel or card background for visual containment
- Phase labels use guidance framing (not clinical terminology)

Use `Identifiable` phase structs instead of tuple arrays — tuples with `ForEach(Array(enumerated()), id: \.offset)` crash the Swift type checker in complex view bodies.

## Do / Mindful Guidance Cards

Two-column layout for actionable guidance:

- DO column: `checkmark.circle.fill` + green tint
- MINDFUL column: `exclamationmark.circle.fill` + orange tint
- Content from the model's `doAction` / `mindfulAction` fields
- Full item list available in an expandable "Why?" section below

## Narrative Reading Style

Data-heavy screens default to dashboard layouts — labeled rows, bar charts, LabeledContent grids. These look mechanical and don't match an editorial, contemplative tone.

### The Pattern

Narrative reading screens flow like a letter, not a spreadsheet. The hero glyph or number is a visual anchor; the meaning is the content.

Structure:

1. **Atmospheric scene-setter** — context string (time, location, state) at the top in small serif caption
2. **Hero symbol** — large (56–72pt) serif number or SF Symbol, accent-colored, centered. Spring scale animation on appear
3. **Title** — serif section title, centered
4. **Hook** — italic serif summary, secondary color, centered. The editorial lede
5. **Visual indicators** — energy rings (circular rings with SF Symbol centers) instead of bar charts; three side-by-side for multi-dimensional ratings
6. **Theme pills** — keyword capsules in accent-tinted FlowLayout, positioned between hook and deep reading — shows "what this is about" at a glance
7. **Divider** — thin centered line (40pt wide, 1pt tall) as visual pause before the deep reading
8. **The reading** — serif subheadline with 6pt line spacing, left-aligned. Flows like editorial prose
9. **Action / takeaway card** — small panel with a sparkle or bookmark icon and action-oriented short text (e.g., "Save for later", "Try this week")

### Energy Rings (vs Bar Charts)

For multi-dimensional ratings (e.g., Energy / Focus / Recovery on a 1–5 scale), use circular ring indicators instead of horizontal bars:

```swift
ZStack {
    Circle()
        .stroke(backgroundTint, lineWidth: 3)
        .frame(width: 52, height: 52)
    Circle()
        .trim(from: 0, to: appear ? CGFloat(value) / 5.0 : 0)
        .stroke(
            AngularGradient(
                colors: [tint.opacity(0.3), tint, tint.opacity(0.6)],
                center: .center,
                startAngle: .degrees(-90),
                endAngle: .degrees(270)
            ),
            style: StrokeStyle(lineWidth: 3, lineCap: .round)
        )
        .rotationEffect(.degrees(-90))
        .frame(width: 52, height: 52)
    Image(systemName: symbol)
        .font(.system(size: 16))
        .foregroundStyle(tint)
}
```

Rings beat bars for guidance screens because:

- They feel contemplative, not metric-driven
- The SF Symbol center communicates category without a label
- The `AngularGradient` sweep creates visual depth
- They animate naturally with spring timing

### When to Use Narrative vs Dashboard

| Content | Narrative | Dashboard |
|---|---|---|
| Daily briefing / reading | Yes | |
| Long-form interpretation | Yes | |
| Weekly summary | Yes | |
| Events calendar | | Yes |
| Settings / preferences | | Yes |
| Friend / contact list | | Yes |
| Raw data / measurements | | Yes |
| Contextual meaning + recommendation | Yes | |

### Anti-Patterns

- `LabeledContent("Score", value: "4")` on a narrative screen — mechanical, not editorial
- `ProgressView(value:)` for ratings — looks like a loading bar
- Section headers for every data point — over-structured, kills flow
- Hardcoded "X/5" text next to bars — dashboard metric language
- Bar charts for multi-dimensional qualitative ratings — use rings or pips
