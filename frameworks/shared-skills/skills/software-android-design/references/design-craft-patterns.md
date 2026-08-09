# Design Craft Patterns

Battle-tested patterns for building high-end, precise Android interfaces. These are practical fixes for common design problems, not abstract principles.

## Table of Contents

- [Bottom Sheet Pattern](#bottom-sheet-pattern)
- [Design Token Discipline](#design-token-discipline)
- [Data Containment](#data-containment)
- [Visual Anchoring](#visual-anchoring)
- [Card Hierarchy](#card-hierarchy)
- [Dark Theme Patterns](#dark-theme-patterns)
- [Competitor Pattern Analysis](#competitor-pattern-analysis)
- [Symmetric Card Pairs](#symmetric-card-pairs)
- [Localization Visual Audit](#localization-visual-audit)
- [Guidance Reading Style](#guidance-reading-style)

## Bottom Sheet Pattern

### The Rule

All secondary detail content uses a consistent "popup from the bottom" interaction. Never show deep detail inline in a scroll view — it clutters the screen and breaks scannability.

### How It Works

1. **Compact tappable row** in a `LazyColumn` or `Column`:
   ```kotlin
   ListItem(
       headlineContent = { Text("Your sky") },
       supportingContent = { Text(summaryValue) },
       leadingContent = {
           Icon(Icons.Rounded.AutoAwesome, contentDescription = null, modifier = Modifier.size(20.dp))
       },
       trailingContent = {
           Icon(Icons.AutoMirrored.Rounded.KeyboardArrowRight, contentDescription = null)
       },
       modifier = Modifier.clickable { selectedSection = Section.SKY }
   )
   ```

2. **`ModalBottomSheet`** triggered by selection:
   ```kotlin
   if (selectedSection != null) {
       ModalBottomSheet(
           onDismissRequest = { selectedSection = null },
           sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = false)
       ) {
           LazyColumn(contentPadding = PaddingValues(horizontal = 16.dp, vertical = 24.dp)) {
               // Full detail content
           }
       }
   }
   ```

3. **Hero content stays inline** — headlines, summaries, key metrics that define the screen's purpose remain in the main scroll. Only secondary detail (lists of items, expanded data) moves into sheets.

### When to Use Sheets vs Inline

| Content | Treatment |
|---------|-----------|
| 1-2 key values (date, status) | Inline `ListItem` or `Row` |
| Summary text (1 paragraph) | Inline in section |
| List of 3+ items | Compact row -> sheet |
| Expandable data (month details, transit lists) | Compact row -> sheet |
| Charts and visualizations | Inline (hero visual) |
| Upgrade/locked prompts | Inline |

### Expandable Section Pattern (Alternative to Sheets)

For data-dense reports with 5+ sections (compatibility reports, chart analysis), expandable sections can be better than sheets — they keep context visible while reducing initial scroll depth:

```kotlin
var expanded by remember { mutableStateOf(false) }

ElevatedCard(
    shape = MaterialTheme.shapes.extraLarge,
    modifier = Modifier.fillMaxWidth()
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .clickable { expanded = !expanded }
            .padding(20.dp)
    ) {
        Icon(icon, contentDescription = null, tint = tint, modifier = Modifier.size(20.dp))
        Spacer(Modifier.width(12.dp))
        Text(title, style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.weight(1f))
        Icon(
            Icons.Rounded.ChevronRight,
            contentDescription = if (expanded) "Collapse" else "Expand",
            modifier = Modifier.rotate(animateFloatAsState(if (expanded) 90f else 0f, spring()).value)
        )
    }

    AnimatedVisibility(
        visible = expanded,
        enter = fadeIn() + expandVertically(),
        exit = fadeOut() + shrinkVertically()
    ) {
        Column(Modifier.padding(start = 20.dp, end = 20.dp, bottom = 20.dp)) {
            content()
        }
    }
}
```

Use expandable sections when:
- The report has 5+ distinct data sections
- Users typically scan 2-3 sections, not all of them
- The content is supplementary rather than primary

### Anti-Patterns

- Raw `Column` with `animateContentSize` for deep content — hard to scan, expands inline, pushes content below the fold
- Inline cards with full detail — steals vertical space from other sections
- Navigation push for simple detail — too heavy for data that does not need its own screen
- Showing all items when only a count matters — show count + chevron, full list in sheet
- Flat list of all sections with equal weight — use animated score rings and radar charts as hero content, push secondary content into expandable sections

## Design Token Discipline

### The Rule

Every magic number in a screen file should trace back to a named token in the design system. If a value appears in two places, it needs a name.

### What to Tokenize

| Category | Examples | Why |
|----------|----------|-----|
| Spacing | Screen padding, card internal padding, section gaps, control gaps | Prevents drift between screens |
| Typography | Card eyebrow style, icon label style, hero display style — any `TextStyle(fontSize, fontWeight)` repeated 3+ times | One change updates every section header |
| Elevation | Card tonalElevation, surface levels, FAB elevation | Documents intentional depth hierarchy |
| Corner radii | Panel, card, control, row, compact cell shapes | Ensures consistent shape language |
| Colors | All surface roles, text levels, accents, status colors via `MaterialTheme.colorScheme` | Single source of truth for theming |

### Token Hierarchy Pattern

Name tokens by semantic role, not by value:

```
Spacing: screenPadding (24.dp) > cardPadding (20.dp) > sectionGap (16.dp) > itemGap (8.dp)
Elevation: heroCard (level3) > primaryCard (level1) > secondaryCard (level0)
Shape: heroCard (28.dp) > primaryCard (16.dp) > controlElement (12.dp) > compactCell (8.dp)
```

This makes the hierarchy self-documenting. A developer reading `AppElevation.heroCard` immediately understands the intent.

### Common Anti-Pattern: Hardcoded Values

Audit for these patterns in screen files:
- `.padding(22.dp)` — should be a named spacing token
- `RoundedCornerShape(13.dp)` — should map to `MaterialTheme.shapes` or a named shape token
- `TextStyle(fontSize = 10.sp, fontWeight = FontWeight.Bold)` — if repeated 3+ times, extract to a typography token or use the Material type scale
- `Color(0xFF1A1A2E)` — should be a `MaterialTheme.colorScheme` role or a named palette token

## Data Containment

### The Problem

Data that "floats" in a `Column` — label-value rows with no visual boundaries — looks mechanical and undesigned. Fixed-width label columns create uneven whitespace when labels vary in length.

### The Fix: Card + Column Grid

For compact, scannable data (placements, stats, ratings), use contained cells in a grid:

```kotlin
Surface(
    color = MaterialTheme.colorScheme.surfaceContainerLow,
    shape = MaterialTheme.shapes.medium,
    modifier = Modifier.weight(1f)
) {
    Column(Modifier.padding(horizontal = 12.dp, vertical = 10.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(5.dp)) {
            Icon(icon, contentDescription = null, modifier = Modifier.size(14.dp), tint = tint)
            Text(
                label.uppercase(),
                style = MaterialTheme.typography.labelSmall,
                color = tint
            )
        }
        Spacer(Modifier.height(6.dp))
        Text(
            value,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis
        )
    }
}
```

Arrange 3 cells in a `Row(horizontalArrangement = Arrangement.spacedBy(8.dp))` with `Modifier.weight(1f)` on each for compact data grids. For wider content, use 2 cells per row.

### The Fix: Contained Action Rows

For actionable items (Do/Avoid, Best move/Skip), use a vertical layout with a background:

```kotlin
Surface(
    color = MaterialTheme.colorScheme.surfaceContainerLow,
    shape = MaterialTheme.shapes.large,
    modifier = Modifier.fillMaxWidth()
) {
    Column(Modifier.padding(16.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            Canvas(Modifier.size(6.dp)) { drawCircle(color = tint) }
            Text(label.uppercase(), style = MaterialTheme.typography.labelSmall, color = tint)
        }
        Spacer(Modifier.height(6.dp))
        Text(
            description,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
```

### When NOT to Contain

- Short, homogeneous key-value pairs in a settings list — use `ListItem` composables
- Single-line metadata — containment adds visual noise without benefit

## Visual Anchoring

### The Problem

Screens that are 100% text feel flat, even with good typography. Competitor apps add visual focal points — illustrations, icons, indicators — that create scannable anchor points.

### Material Icon Anchoring

Add small Material icons (18-20dp) to data labels for faster scanning:

- Energy level -> `Icons.Rounded.Bolt`
- Heart/relationship -> `Icons.Rounded.Favorite`
- Trend up -> `Icons.Rounded.TrendingUp`
- Calendar timing -> `Icons.Rounded.CalendarMonth`
- Rating/score -> `Icons.Rounded.BarChart`

Keep icons at 18-20dp, same visual weight as label text, tinted with `MaterialTheme.colorScheme.primary` or a semantic color. The icon should support the label, not compete with it.

### Colored Dot Indicators

For categorized lists (Do/Mindful, Go/Caution), draw a 6dp Canvas circle before the label. This creates instant visual categorization without reading the text:

```kotlin
Canvas(modifier = Modifier.size(6.dp)) {
    drawCircle(color = tint)
}
```

- Green dot -> positive/do items
- Orange dot -> caution/mindful items
- Red dot -> avoid items

### What NOT to Add

- Decorative icons that do not convey meaning
- Icons on every single text element (visual noise)
- Large illustrations in data-heavy screens (competes with content)

## Card Hierarchy

### The Pattern

Not all cards should look the same. A dashboard needs visual hierarchy between cards:

| Level | Treatment | Example |
|-------|-----------|---------|
| Hero | `ElevatedCard` with level 3 tonalElevation, 28dp corner shape, more internal padding (24dp) | Today's headline card |
| Primary | `Card` (filled) with level 1 tonalElevation, 16dp corner shape, standard padding (20dp) | Data section, Guidance |
| Secondary | `OutlinedCard` with 0 tonalElevation, 12dp corner shape, tighter padding (16dp) | Action rows, decision cards |

### Card Separation

When a card contains two distinct content types (e.g., data grid + action rows), separate them with a thin divider:

```kotlin
HorizontalDivider(
    color = MaterialTheme.colorScheme.outlineVariant,
    thickness = 1.dp
)
```

This is cheaper than splitting into two cards and keeps the card count manageable (heuristic: 5-6 visible cards on a phone is a warning threshold).

## Dark Theme Patterns

### Surface Layering with Tonal Elevation

Material 3 builds depth through tonal color overlays, not separate RGB values for each layer:

```
Level 0: colorScheme.surface — base background
Level 1: colorScheme.surfaceContainerLowest — slight tonal shift
Level 2: colorScheme.surfaceContainerLow — card background
Level 3: colorScheme.surfaceContainer — prominent card
Level 4: colorScheme.surfaceContainerHigh — elevated content
Level 5: colorScheme.surfaceContainerHighest — highest emphasis surface
```

Each level shifts the surface color toward `primary`, creating physical depth without manual opacity math.

### Text Hierarchy in Dark

Use Material color roles for text hierarchy:

```
Primary: colorScheme.onSurface — highest emphasis
Secondary: colorScheme.onSurfaceVariant — supporting text
Disabled: colorScheme.onSurface.copy(alpha = 0.38f) — disabled/tertiary
```

Never use `Color.White` or `Color.Black` directly — they do not adapt to dynamic color or theme changes.

### Accent Strategy

Reserve accent colors for interactive elements and categorization, not decoration:

- `colorScheme.primary` -> CTAs, active states, primary indicators
- `colorScheme.secondary` -> alternative actions, secondary data
- `colorScheme.tertiary` -> complementary accents, special features
- `colorScheme.error` -> destructive actions and error states only

### Atmospheric Effects

For spiritual-guidance or wellness themes, add subtle radial gradients behind the content layer:

```kotlin
Canvas(modifier = Modifier.fillMaxSize()) {
    drawCircle(
        brush = Brush.radialGradient(
            colors = listOf(Color(0x38673AB7), Color.Transparent),
            center = Offset(size.width * 0.2f, size.height * 0.15f),
            radius = size.width * 0.5f
        )
    )
}
```

Keep these behind all content. They should create mood, not interfere with readability.

## Competitor Pattern Analysis

### Methodology

When studying competitor apps:

1. Focus on the **home/daily screen** first — this is where design quality matters most
2. Study their **data display patterns** — how do they show summaries, ratings, guidance?
3. Note their **visual anchoring** — what creates the focal point?
4. Look at their **containment** — do items float or have clear boundaries?
5. Check their **information density** — how many items compete above the fold?

### Material Design Showcase Apps

Study Google's own Material 3 showcase apps for reference patterns:
- **Reply** — adaptive email client with NavigationSuiteScaffold
- **Jetchat** — conversation UI with Material 3 surfaces
- **Now in Android** — feed-based news reader with Card hierarchy and TopicChip patterns
- **Jetsnack** — commerce app with rich Canvas visuals and immersive transitions

### When to Borrow

Borrow a pattern when:
- It solves a **specific visual problem** you have (floating text, flat hierarchy)
- It works with **your content density** (sparse editorial style breaks with dense data)
- It can be implemented with **standard Compose Material 3** (no custom rendering engine)

Do not borrow:
- Entire visual identities (keep your own brand)
- Patterns that require different content structure than you have
- Effects that are purely decorative

## Symmetric Card Pairs

### The Problem

Side-by-side cards with different-length text create uneven heights, breaking visual symmetry. One card dominates, making the pair feel unbalanced.

### The Fix

Enforce identical geometry with `IntrinsicSize` and `weight`:

```kotlin
Row(
    horizontalArrangement = Arrangement.spacedBy(12.dp),
    modifier = Modifier.height(IntrinsicSize.Max)
) {
    GuidanceCard(type = GuidanceType.BEST_MOVE, headline = shortText, modifier = Modifier.weight(1f))
    GuidanceCard(type = GuidanceType.AVOID, headline = longerText, modifier = Modifier.weight(1f))
}

// Inside GuidanceCard:
OutlinedCard(
    modifier = modifier.fillMaxHeight(),
    colors = CardDefaults.outlinedCardColors(
        containerColor = tint.copy(alpha = 0.06f)
    )
) {
    Column(Modifier.padding(20.dp)) {
        // ... content
        Text(headline, maxLines = 3, overflow = TextOverflow.Ellipsis)
    }
}
```

Rules:
- Both cards share the same row with `IntrinsicSize.Max` — cards stretch to equal height
- Use `maxLines = 3` to prevent one card from growing unbounded
- Move full content to a tap-to-expand sheet
- Color each card with its semantic tint at low opacity (6%) for instant categorization
- Never use different structures (e.g., one card with an icon and one without)

### When to Use

- Do/Avoid, Best Move/Skip, Pro/Con pairs
- Any two cards that are conceptual opposites and should feel balanced
- Comparison cards (You vs Friend, Before vs After)

## Localization Visual Audit

### The Rule

Every user-facing string must go through `strings.xml`, even placeholder text. This is not just about translation — it ensures:

- Future language support works without code changes
- Arabic RTL layout can be tested via developer options
- Longer translated strings do not break fixed-width layouts

### Fixed-Width Label Anti-Pattern

Never use `Modifier.width(84.dp)` for labels that will be translated. "Sun" is 3 characters in English but "Soleil" is 6 in French and right-to-left in Arabic.

Use flexible layouts instead:
- Grid cells with `Modifier.weight(1f)` that expand to fill available width
- `Column` layouts where label sits above value
- `TextOverflow.Ellipsis` + `maxLines` for tight spaces

### Localization Smoke Test Languages

Spot-check layouts with at least these three scenarios:
- **German** (+30-50% string length) — exposes truncation and label overflow
- **Arabic** (RTL) — exposes hardcoded start/end assumptions and mirroring gaps. Use forced RTL in developer options.
- **Japanese/Chinese** (CJK) — exposes fixed-height assumptions and proportional metrics differences

## Guidance Reading Style

### The Problem

Data-heavy screens (numerology, horoscope, angel numbers) default to dashboard layouts — labeled rows, bar charts, `ListItem` grids. These look mechanical and do not match the editorial, contemplative tone of wellness/guidance apps.

### The Pattern

Guidance reading screens flow like a letter, not a spreadsheet. The number or symbol is a visual anchor, the meaning is the content.

Structure:
1. **Atmospheric scene-setter** — transit context or date at the top in small label caption. Sets the context before the reading begins.
2. **Hero symbol** — large (56-72sp) display number or icon, `MaterialTheme.colorScheme.primary`, centered. Spring scale animation on appear with `Animatable`.
3. **Title** — `MaterialTheme.typography.headlineMedium`, centered
4. **Hook** — `MaterialTheme.typography.bodyLarge`, `onSurfaceVariant`, centered. The editorial lede.
5. **Visual indicators** — energy orbs (circular rings with Material icon centers) instead of bar charts. Three orbs side-by-side for multi-dimensional ratings.
6. **Theme chips** — keyword capsules in `FlowRow` with accent-tinted surface, positioned between hook and deep reading. Shows "what this is about" at a glance.
7. **Divider** — thin centered `HorizontalDivider(modifier = Modifier.width(40.dp))` as visual pause before the deep reading.
8. **The reading** — `MaterialTheme.typography.bodyLarge` with `lineHeight` override, start-aligned. Flows like editorial prose.
9. **Charm/Lucky card** — `ElevatedCard` with sparkle icon and action-oriented text ("Wear teal", "Lucky 4").

### Energy Orbs (vs Bar Charts)

For multi-dimensional ratings (Love/Career/Wellness, 1-5 scale), use circular ring indicators instead of horizontal bars:

```kotlin
@Composable
fun EnergyOrb(value: Int, maxValue: Int = 5, icon: ImageVector, tint: Color) {
    val progress by animateFloatAsState(
        targetValue = value.toFloat() / maxValue,
        animationSpec = spring(dampingRatio = 0.6f, stiffness = 200f)
    )

    Box(contentAlignment = Alignment.Center, modifier = Modifier.size(52.dp)) {
        Canvas(Modifier.fillMaxSize()) {
            drawArc(
                color = tint.copy(alpha = 0.15f),
                startAngle = -90f, sweepAngle = 360f,
                useCenter = false,
                style = Stroke(width = 3.dp.toPx(), cap = StrokeCap.Round)
            )
            drawArc(
                brush = Brush.sweepGradient(
                    listOf(tint.copy(alpha = 0.3f), tint, tint.copy(alpha = 0.6f))
                ),
                startAngle = -90f, sweepAngle = 360f * progress,
                useCenter = false,
                style = Stroke(width = 3.dp.toPx(), cap = StrokeCap.Round)
            )
        }
        Icon(icon, contentDescription = null, modifier = Modifier.size(16.dp), tint = tint)
    }
}
```

Orbs are better than bars for guidance screens because:
- They feel contemplative, not metric-driven
- The icon center communicates the category without a label
- The sweep gradient creates visual depth
- They animate naturally with spring timing

### When to Use Guidance vs Dashboard

| Content | Use Guidance | Use Dashboard |
|---------|-------------|---------------|
| Horoscope reading | Yes | |
| Numerology profile | Yes | |
| Angel number meaning | Yes | |
| Best days calendar | | Yes |
| Settings/preferences | | Yes |
| Friend list | | Yes |
| Chart placements (data) | | Yes |
| Transit context + meaning | Yes | |

### Anti-Patterns

- `ListItem(headlineContent = { Text("Life Path") }, trailingContent = { Text("4") })` — mechanical, not editorial
- `LinearProgressIndicator` for ratings — looks like a loading bar
- Section headers for every data point — over-structured, kills flow
- Hardcoded "X/5" text next to bars — dashboard metric language
