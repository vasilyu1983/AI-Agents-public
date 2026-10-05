# Android Dashboard Design

## Table of Contents

- [Dashboard Principles](#dashboard-principles)
- [A Practical Hierarchy](#a-practical-hierarchy)
- [Useful Heuristics](#useful-heuristics)
- [Horizontal Collections](#horizontal-collections)
- [Compact Data Grids](#compact-data-grids)
- [Contained Action Rows](#contained-action-rows)
- [What NOT to Do](#what-not-to-do)
- [Card Hierarchy on Dashboards](#card-hierarchy-on-dashboards)
- [Dual-View Dashboard Pattern](#dual-view-dashboard-pattern)
- [Visual Guidance Cards](#visual-guidance-cards)
- [Domain Notes](#domain-notes)

Use this reference for overview screens that summarize multiple content types or decisions.

## Dashboard Principles

- Make one thing win first attention.
- Show summaries first and let users drill into detail.
- Keep the first viewport scannable; if everything above the fold competes equally, the dashboard is not prioritized enough.
- Prefer Material 3 structure over novelty. A dashboard can still feel Android-native if it uses standard navigation, type scale, actions, and surface hierarchy carefully.

## A Practical Hierarchy

- Hero: the most important thing right now
- Primary context: two or three supporting items
- Secondary context: recommendations, history, or quick actions
- Tertiary detail: deeper data that can live below the fold or in a separate destination

## Useful Heuristics

- Treat 5-6 visible cards on a phone as a warning threshold for overview screens, not a hard limit.
- If two cards say almost the same thing, merge them.
- If a "quick action" is rarely used, move it to a menu or secondary destination.
- If multiple modules are equally large, one of them is probably missing a demotion.

## Horizontal Collections

Use `LazyRow` when several peer items deserve equal weight and users may browse them:

```kotlin
LazyRow(
    contentPadding = PaddingValues(horizontal = 16.dp),
    horizontalArrangement = Arrangement.spacedBy(12.dp)
) {
    items(items) { item ->
        Card(modifier = Modifier.width(280.dp)) {
            // Card content
        }
    }
}
```

Rules:
- Show enough of the next item to signal that the row scrolls (use `width` that leaves partial visibility)
- Add `contentPadding` for edge alignment with the rest of the screen
- Avoid horizontal collections when items are text-heavy or need comparison

## Compact Data Grids

For 3-5 related values (counts, statistics), use contained cells in a `LazyVerticalGrid` or `Row`:

```kotlin
Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
    StatCell("Battery", "High", Icons.Rounded.BatteryFull, tint = green, modifier = Modifier.weight(1f))
    StatCell("Status", "Ready", Icons.Rounded.CheckCircle, tint = blue, modifier = Modifier.weight(1f))
    StatCell("Throughput", "Rising", Icons.Rounded.TrendingUp, tint = gold, modifier = Modifier.weight(1f))
}
```

Or for larger grids:

```kotlin
LazyVerticalGrid(
    columns = GridCells.Fixed(3),
    horizontalArrangement = Arrangement.spacedBy(8.dp),
    verticalArrangement = Arrangement.spacedBy(8.dp),
    contentPadding = PaddingValues(horizontal = 16.dp)
) {
    items(stats) { stat -> StatCell(stat) }
}
```

Each cell: icon + label on top, value below, `surfaceContainerLow` background, rounded corners via `MaterialTheme.shapes.small`.

## Contained Action Rows

For recommended and blocked actions, use `Column` layout with surface background:

- Colored dot + uppercase label on top
- Description text below
- `surfaceContainerLow` background with `MaterialTheme.shapes.large` corners
- Reuse one composable for all action rows across cards

## What NOT to Do

- Fixed-width label columns (`Modifier.width(84.dp)`) — creates uneven whitespace when labels vary
- Bare `Row` label-value pairs without visual boundaries — data floats
- Mixing different row patterns in the same card without visual separation

## Card Hierarchy on Dashboards

- **Hero card**: `ElevatedCard` with `extraLarge` shape, more padding, one per screen
- **Primary cards**: `Card` with `large` shape, standard padding, 2-3 per screen
- **Inset rows within cards**: Tighter padding, `surfaceContainerLow` surface, for nested data
- Use thin `HorizontalDivider` to separate content types within a single card instead of splitting into more cards

## Dual-View Dashboard Pattern

For data-rich apps (health, finance, productivity, analytics), offer two dashboard views via `SegmentedButton` or `TabRow` at the top. Each view shows the same data with different information density:

- **Detail view**: individual metrics, action summaries, and status labels for inspection.
- **Overview view**: one labeled summary visualization for a quick scan.

```kotlin
SingleChoiceSegmentedButtonRow {
    DashboardViewMode.entries.forEachIndexed { index, mode ->
        SegmentedButton(
            selected = selectedMode == mode,
            onClick = { selectedMode = mode },
            shape = SegmentedButtonDefaults.itemShape(index, DashboardViewMode.entries.size)
        ) { Text(mode.label) }
    }
}
```

Or with `TabRow`:

```kotlin
TabRow(selectedTabIndex = selectedMode.ordinal) {
    DashboardViewMode.entries.forEach { mode ->
        Tab(
            selected = selectedMode == mode,
            onClick = { selectedMode = mode },
            text = { Text(mode.label) }
        )
    }
}
```

Rules:
- Shared elements (quick links, social card) appear below both views
- Each view computes from the same snapshot — no separate API calls
- Name the views by function ("Details" / "Overview")

## Visual Guidance Cards

### Symmetric Action Card Pairs (Pro / Con)

When showing two comparison cards side-by-side, enforce identical geometry:

```kotlin
@Composable
fun ComparisonCard(type: ComparisonType, headline: String, modifier: Modifier = Modifier) {
    OutlinedCard(
        modifier = modifier.fillMaxHeight(),
        colors = CardDefaults.outlinedCardColors(
            containerColor = type.tint.copy(alpha = 0.06f)
        ),
        border = BorderStroke(1.dp, type.tint.copy(alpha = 0.15f))
    ) {
        Column(Modifier.padding(20.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(type.icon, contentDescription = null, tint = type.tint, modifier = Modifier.size(16.dp))
                Text(type.label.uppercase(), style = MaterialTheme.typography.labelSmall, color = type.tint)
            }
            Spacer(Modifier.height(10.dp))
            Text(headline, maxLines = 3, overflow = TextOverflow.Ellipsis, style = MaterialTheme.typography.bodyMedium)
        }
    }
}

Row(
    horizontalArrangement = Arrangement.spacedBy(12.dp),
    modifier = Modifier.height(IntrinsicSize.Max)
) {
    ComparisonCard(ComparisonType.PRO, shortText, Modifier.weight(1f))
    ComparisonCard(ComparisonType.CON, longerText, Modifier.weight(1f))
}
```

Key rules:
- Use `IntrinsicSize.Max` to enforce equal card height regardless of text length
- Use `maxLines = 3` to cap text — detail goes in the tap-to-expand sheet
- Color the card background with the action tint at low opacity (6%) for instant visual categorization
- Both cards are tappable -> open detail sheet with full item lists

### Data Visualization on Dashboards

#### Gauge with Gradient Arc

For labeled rating gauges, use a smooth `Brush.sweepGradient` from red to yellow to green:

```kotlin
Canvas(modifier = Modifier.size(width = 200.dp, height = 110.dp)) {
    drawArc(
        brush = Brush.sweepGradient(
            colorStops = arrayOf(
                0.0f to Color.Red,
                0.125f to Color(0xFFFF9800),
                0.25f to Color.Yellow,
                0.375f to Color(0xFFCDDC39),
                0.5f to Color.Green
            )
        ),
        startAngle = 180f,
        sweepAngle = 180f,
        useCenter = false,
        style = Stroke(width = 16.dp.toPx(), cap = StrokeCap.Round)
    )
    // Animated needle overlay
}
```

#### Score Ring

```kotlin
Canvas(modifier = Modifier.size(100.dp)) {
    drawArc(background, -90f, 360f, false, Stroke(10.dp.toPx(), cap = StrokeCap.Round))
    drawArc(accentBrush, -90f, 360f * (animatedScore / maxScore), false, Stroke(10.dp.toPx(), cap = StrokeCap.Round))
}
```

#### Quadrant Chart

A 4-quadrant circular chart for multi-dimensional measurements:

```kotlin
Canvas(modifier = Modifier.size(200.dp)) {
    // Background circle + cross lines dividing quadrants
    // 4 filled arcs, each proportional to its score
    // Center circle with overall rating text
    // Quadrant labels + icon overlays at midpoints
}
```

### Score Scale Detection

Read the scale and units from the API contract; a value of 8 alone cannot distinguish 8/10 from 8/100. Do not infer the maximum from the value. Validate a positive maximum and normalize against it; show an unavailable state for malformed measurements.

## Domain Notes

- Content-heavy apps such as wellness, finance, or news often accumulate too many overview modules.
- In those apps, the main design job is prioritization, not decoration.
- Prefer compact summary rows, a single hero panel, and clearer destinations over a stack of equally styled cards.
- Every visualization should answer a user question and expose its values through labels and accessibility semantics.
