# Visual Guidance Patterns — Android

## Table of Contents

- [Principle: Visual Guidance, Not a Data Dashboard](#principle-visual-guidance-not-a-data-dashboard)
- [Canvas Terrain (Daily Energy)](#canvas-terrain-daily-energy)
- [Canvas Ring (Yearly Energy)](#canvas-ring-yearly-energy)
- [Opportunity Framing](#opportunity-framing)
- [Screen Archetypes](#screen-archetypes)
- [Narrative Scroll Flow](#narrative-scroll-flow)
- [Bottom Sheet for Detail](#bottom-sheet-for-detail)
- [Canvas Gantt / Timeline](#canvas-gantt--timeline)
- [Vertical Dot Timeline](#vertical-dot-timeline)
- [DO/MINDFUL Guidance Cards](#domindful-guidance-cards)

Patterns for screens that communicate guidance and emotional context rather than analytical data.

## Principle: Visual Guidance, Not a Data Dashboard

The screen should read like a weather forecast, not a spreadsheet. Answer "what does this feel like?" before "what are the numbers?"

## Canvas Terrain (Daily Energy)

Use a `Canvas`-drawn mountain/wave terrain instead of a calendar grid for showing energy flow over a month:

```kotlin
Canvas(modifier = Modifier
    .fillMaxWidth()
    .height(180.dp)
    .pointerInput(Unit) {
        detectHorizontalDragGestures { change, _ ->
            val dayIndex = (change.position.x / (size.width / dayCount)).toInt().coerceIn(0, dayCount - 1)
            selectedDay = dayIndex
            hapticFeedback.performHapticFeedback(HapticFeedbackType.TextHandleMove)
        }
    }
) {
    val points = energyValues.mapIndexed { i, v ->
        Offset(
            x = size.width * i / (energyValues.size - 1).coerceAtLeast(1),
            y = size.height * (1f - v / 10f)
        )
    }

    // Catmull-Rom spline through points
    val path = Path().apply {
        moveTo(points.first().x, points.first().y)
        // cubicTo for each segment...
    }

    // Fill with gradient
    drawPath(path, brush = Brush.verticalGradient(listOf(accentColor.copy(alpha = 0.4f), Color.Transparent)))
    // Stroke the line
    drawPath(path, color = accentColor, style = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round))

    // "TODAY" gold dashed vertical marker
    val todayX = size.width * todayIndex / (energyValues.size - 1)
    drawLine(
        color = gold,
        start = Offset(todayX, 0f),
        end = Offset(todayX, size.height),
        strokeWidth = 1.dp.toPx(),
        pathEffect = PathEffect.dashPathEffect(floatArrayOf(8f, 6f))
    )
}
```

- X axis: days 1...N, Y axis: energy 0-10 via Catmull-Rom spline
- Color each day column by quality tier (gradient heat-map effect)
- "TODAY" gold dashed vertical marker
- `detectHorizontalDragGestures` for scrubbing with haptic feedback on each day boundary
- Free/preview days at 20% opacity (shape visible, detail locked)

Pair with a calendar grid below for precise day selection (grids beat carousels for spatial context).

## Canvas Ring (Yearly Energy)

Use a 12-segment annular ring instead of a bar chart for yearly energy:

```kotlin
Canvas(modifier = Modifier
    .size(240.dp)
    .pointerInput(Unit) {
        detectTapGestures { offset ->
            val angle = atan2(offset.y - center.y, offset.x - center.x)
            val monthIndex = ((Math.toDegrees(angle.toDouble()) + 90 + 360) % 360 / 30).toInt()
            selectedMonth = monthIndex
        }
    }
) {
    val center = Offset(size.width / 2, size.height / 2)
    val outerRadius = size.minDimension / 2 - 16.dp.toPx()
    val innerRadius = outerRadius * 0.55f

    monthEnergies.forEachIndexed { i, energy ->
        val startAngle = -90f + i * 30f
        val fillRadius = innerRadius + (outerRadius - innerRadius) * (energy / maxEnergy)

        drawArc(
            color = tierColor(energy),
            startAngle = startAngle + 1f,
            sweepAngle = 28f,
            useCenter = true,
            topLeft = Offset(center.x - fillRadius, center.y - fillRadius),
            size = Size(fillRadius * 2, fillRadius * 2)
        )
    }

    // Center year label via TextMeasurer
    val yearText = textMeasurer.measure("2026", style = displayStyle)
    drawText(yearText, topLeft = Offset(center.x - yearText.size.width / 2, center.y - yearText.size.height / 2))
}
```

- Each month is a wedge, fill radius proportional to energy level
- Color from energy tier (gold/green/teal/gray/orange)
- Year number centered via `TextMeasurer`
- Tap to select month with haptic feedback

## Opportunity Framing

Reframe clinical quality tiers with empowering language:

| Clinical | Opportunity | Frame |
|----------|------------|-------|
| Best | Peak Energy | Opportunity window |
| Great | High Flow | Momentum |
| Good | Steady Current | Grounded action |
| Neutral | Quiet Day | Steady presence |
| Challenging | Growth Day | Inner strength |
| Avoid | Reflection Day | Rest and recharge |

### Phase/State Framing

Apply the same principle to any state progression (lifecycle stages, status indicators):

| Clinical | Guidance | Tone |
|----------|----------|------|
| Retrograde | Reflection Period | Pause, review, revisit |
| Pre-shadow | Slowing Down | Prepare, back up, clarify |
| Post-shadow | Integration Phase | Lessons settling, momentum returns |
| Direct | Clear Path | Forward motion, initiate |

For phases without inherent user action, group them into a compact summary (e.g., "Venus, Mars, Jupiter — Clear Path") instead of giving each its own card. Reserve individual guidance cards for phases that need user attention.

## Screen Archetypes

Three distinct screen types serve different content:

| Archetype | When | Structure |
|-----------|------|-----------|
| Dashboard | Hub screens, settings, data lists | `Scaffold` + `LazyColumn` with Cards |
| Guidance Reading | Horoscope, numerology, angel numbers | Narrative scroll with hero symbol, editorial text, energy orbs |
| Immersive Visualization | Chart wheel, 3D scene, map view | Full-bleed rendering + floating controls + `BottomSheetScaffold` |

For the immersive visualization pattern, see [android-component-patterns.md](android-component-patterns.md#immersive-visualization-screen).

## Narrative Scroll Flow

Use `LazyColumn` with `AnimatedVisibility` for guidance screens:

```kotlin
LazyColumn(
    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 24.dp),
    verticalArrangement = Arrangement.spacedBy(20.dp)
) {
    item { HeroHeader(eyebrow = context, summary = narrative) }
    item { CanvasVisualization(terrain = energyData) }
    item { SelectorControl(grid = calendarData) }
    item { HighlightPills(events = keyEvents) }
    item { PremiumGate() }
}
```

Each item uses `AnimatedVisibility` with `fadeIn() + slideInVertically()` for viewport entrance reveals.

Reserve `ListItem`-based lists for settings-style hub screens.

## Bottom Sheet for Detail

Day/month detail should pop up from the bottom (`ModalBottomSheet`), not expand inline:
- Users expect the detail to be a focused, dismissible view
- Inline expansion pushes content below the fold unpredictably
- `ModalBottomSheet` supports both quick glance (partial) and deep dive (expanded)

## Canvas Gantt / Timeline

Use a `Canvas`-drawn Gantt chart for showing temporal phases across multiple entities (retrograde cycles, subscription periods, project timelines):

```kotlin
Canvas(modifier = Modifier
    .fillMaxWidth()
    .height((rowCount * rowHeight + headerHeight).dp)
    .pointerInput(Unit) {
        detectHorizontalDragGestures { change, _ ->
            val monthIndex = (change.position.x / monthWidth).toInt()
            selectedMonth = monthIndex
            hapticFeedback.performHapticFeedback(HapticFeedbackType.TextHandleMove)
        }
        detectTapGestures { offset ->
            val rowIndex = ((offset.y - headerHeight) / rowHeight).toInt()
            if (rowIndex in 0 until rowCount) selectedEntity = entities[rowIndex]
        }
    }
) {
    // Left column: entity labels via TextMeasurer
    entities.forEachIndexed { i, entity ->
        val label = textMeasurer.measure(entity.abbreviation, style = labelStyle)
        drawText(label, topLeft = Offset(8.dp.toPx(), headerHeight + i * rowHeight + (rowHeight - label.size.height) / 2))
    }

    // Month/week header with vertical hairlines
    months.forEachIndexed { i, month ->
        val x = labelColumnWidth + i * monthWidth
        drawLine(outlineColor, Offset(x, 0f), Offset(x, size.height), strokeWidth = 0.5.dp.toPx())
        val header = textMeasurer.measure(month.abbreviation, style = labelSmallStyle)
        drawText(header, topLeft = Offset(x + 4.dp.toPx(), 4.dp.toPx()))
    }

    // Phase bars as rounded rects
    phases.forEach { phase ->
        val rect = phaseRect(phase)
        drawRoundRect(
            color = phaseColor(phase.type),
            topLeft = rect.topLeft,
            size = rect.size * animatedProgress,
            cornerRadius = CornerRadius(4.dp.toPx())
        )
    }

    // "NOW" marker: gold dashed vertical line
    val nowX = labelColumnWidth + nowOffset
    drawLine(
        color = gold,
        start = Offset(nowX, 0f),
        end = Offset(nowX, size.height),
        strokeWidth = 1.dp.toPx(),
        pathEffect = PathEffect.dashPathEffect(floatArrayOf(8f, 6f))
    )
}
```

The Gantt is better than a table when the user needs to see temporal overlap and density across entities.

## Vertical Dot Timeline

Use a vertical connected-dot timeline for showing progression through sequential phases:

```kotlin
@Composable
fun DotTimeline(phases: List<Phase>, currentIndex: Int) {
    Column(
        modifier = Modifier.padding(16.dp)
    ) {
        phases.forEachIndexed { index, phase ->
            Row(verticalAlignment = Alignment.Top) {
                // Dot column
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    val dotSize = if (index == currentIndex) 14.dp else 10.dp
                    val dotColor = phaseColor(phase)

                    Canvas(Modifier.size(dotSize)) {
                        drawCircle(color = dotColor)
                        if (index == currentIndex) {
                            drawCircle(
                                color = dotColor.copy(alpha = 0.4f),
                                radius = size.minDimension / 2 + 3.dp.toPx(),
                                style = Stroke(width = 3.dp.toPx())
                            )
                        }
                    }

                    // Connecting line (except after last)
                    if (index < phases.lastIndex) {
                        Spacer(
                            Modifier
                                .width(1.dp)
                                .height(32.dp)
                                .background(MaterialTheme.colorScheme.outlineVariant)
                        )
                    }
                }

                Spacer(Modifier.width(12.dp))

                // Label + date
                Column {
                    Text(phase.guidanceLabel, style = MaterialTheme.typography.titleSmall)
                    Text(phase.dateRange, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
    }
}
```

- Each phase: colored `Canvas` circle (10dp default, 14dp for current) + label + date
- Current phase: larger dot with glowing ring overlay
- Connecting line: 1dp `Spacer` with `outlineVariant` between dots
- Container: `ElevatedCard` or `Card` for visual containment
- Phase labels use guidance framing (not clinical terminology)

## DO/MINDFUL Guidance Cards

Two-column layout for actionable guidance:

```kotlin
Row(
    horizontalArrangement = Arrangement.spacedBy(12.dp),
    modifier = Modifier.height(IntrinsicSize.Max)
) {
    GuidanceCard(
        type = GuidanceType.DO,
        icon = Icons.Rounded.CheckCircle,
        tint = MaterialTheme.colorScheme.primary,
        items = doActions,
        modifier = Modifier.weight(1f)
    )
    GuidanceCard(
        type = GuidanceType.MINDFUL,
        icon = Icons.Rounded.Info,
        tint = MaterialTheme.colorScheme.tertiary,
        items = avoidActions,
        modifier = Modifier.weight(1f)
    )
}
```

- DO column: `CheckCircle` icon + primary tint
- MINDFUL column: `Info` icon + tertiary tint
- Full item lists available in expandable "Why?" section below or in a sheet
