# Android Component Patterns

Use this reference when choosing native Android structures and standard Material 3 component behavior.

## Table of Contents

- [Navigation Components](#navigation-components)
- [TopAppBar Variants](#topappbar-variants)
- [Scaffold and Adaptive Scaffolds](#scaffold-and-adaptive-scaffolds)
- [Bottom Sheets](#bottom-sheets)
- [FAB Variants](#fab-variants)
- [Cards](#cards)
- [Chips](#chips)
- [Dialogs](#dialogs)
- [Lists and LazyColumn](#lists-and-lazycolumn)
- [Menus](#menus)
- [Snackbar](#snackbar)
- [Canvas Visualizations](#canvas-visualizations) — radar/spider charts, animated score rings, gradient bars, semicircular gauges, multi-layer Canvas
- [Interactive Animations](#interactive-animations) — AnimatedVisibility, animateContentSize, spring, container transforms, M3 Expressive motion
- [Buttons](#buttons)
- [Search](#search)
- [FlowRow (Wrapping Chips)](#flowrow-wrapping-chips)
- [Immersive Visualization Screen](#immersive-visualization-screen)

## Navigation Components

### NavigationBar (Bottom Navigation)

Use for 3-5 top-level peer destinations on compact screens:

```kotlin
NavigationBar {
    destinations.forEach { dest ->
        NavigationBarItem(
            selected = currentRoute == dest.route,
            onClick = { navigate(dest.route) },
            icon = { Icon(dest.icon, contentDescription = dest.label) },
            label = { Text(dest.label) }
        )
    }
}
```

Rules:
- 3-5 items maximum
- Each item gets a clear label and icon
- Selected state uses filled icon variant; unselected uses outlined
- Keep navigation history scoped to each destination

### NavigationRail

Use for medium-width screens (foldables, small tablets):

```kotlin
NavigationRail {
    destinations.forEach { dest ->
        NavigationRailItem(
            selected = currentRoute == dest.route,
            onClick = { navigate(dest.route) },
            icon = { Icon(dest.icon, contentDescription = dest.label) },
            label = { Text(dest.label) }
        )
    }
}
```

Place at the start edge. Optionally include a FAB at the top of the rail.

### NavigationDrawer

Use for expanded-width screens (tablets, desktop):

```kotlin
PermanentNavigationDrawer(
    drawerContent = {
        PermanentDrawerSheet {
            destinations.forEach { dest ->
                NavigationDrawerItem(
                    selected = currentRoute == dest.route,
                    onClick = { navigate(dest.route) },
                    icon = { Icon(dest.icon, contentDescription = dest.label) },
                    label = { Text(dest.label) }
                )
            }
        }
    }
) { content() }
```

### NavigationSuiteScaffold

Automatically switches between Bar, Rail, and Drawer by WindowSizeClass:

```kotlin
NavigationSuiteScaffold(
    navigationSuiteItems = {
        destinations.forEach { dest ->
            item(
                selected = currentRoute == dest.route,
                onClick = { navigate(dest.route) },
                icon = { Icon(dest.icon, contentDescription = dest.label) },
                label = { Text(dest.label) }
            )
        }
    }
) { content() }
```

Prefer this over building manual WindowSizeClass switching unless the navigation structure requires custom breakpoints.

## TopAppBar Variants

| Variant | When | Scroll behavior |
|---------|------|-----------------|
| `TopAppBar` | Simple screens, inline title | `pinnedScrollBehavior()` |
| `CenterAlignedTopAppBar` | Branded root screens | `pinnedScrollBehavior()` |
| `MediumTopAppBar` | Screens with headline that collapses | `exitUntilCollapsedScrollBehavior()` |
| `LargeTopAppBar` | Prominent titles on detail screens | `exitUntilCollapsedScrollBehavior()` |

Connect scroll behavior to content:

```kotlin
val scrollBehavior = TopAppBarDefaults.exitUntilCollapsedScrollBehavior()

Scaffold(
    topBar = {
        LargeTopAppBar(
            title = { Text("Your Reading") },
            scrollBehavior = scrollBehavior,
            navigationIcon = { IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Rounded.ArrowBack, "Back") } }
        )
    },
    modifier = Modifier.nestedScroll(scrollBehavior.nestedScrollConnection)
) { ... }
```

## Scaffold and Adaptive Scaffolds

### Standard Scaffold

```kotlin
Scaffold(
    topBar = { TopAppBar(title = { Text("Dashboard") }) },
    bottomBar = { NavigationBar { ... } },
    floatingActionButton = { FloatingActionButton(onClick = { }) { Icon(...) } },
    snackbarHost = { SnackbarHost(snackbarHostState) }
) { innerPadding ->
    Content(modifier = Modifier.padding(innerPadding))
}
```

### ListDetailPaneScaffold

For list-detail patterns (email, settings) that adapt across screen sizes:

```kotlin
val navigator = rememberListDetailPaneScaffoldNavigator<ItemId>()

ListDetailPaneScaffold(
    directive = navigator.scaffoldDirective,
    value = navigator.scaffoldValue,
    listPane = { ListContent(onItemClick = { navigator.navigateTo(ListDetailPaneScaffoldRole.Detail, it) }) },
    detailPane = { DetailContent(navigator.currentDestination?.content) }
)
```

On compact: navigates between panes. On expanded: shows side-by-side.

### SupportingPaneScaffold

For main content with a supplementary side panel:

```kotlin
SupportingPaneScaffold(
    directive = navigator.scaffoldDirective,
    value = navigator.scaffoldValue,
    mainPane = { MainContent() },
    supportingPane = { SupportingContent() }
)
```

## Bottom Sheets

### ModalBottomSheet

For secondary detail that temporarily interrupts context:

```kotlin
var showSheet by remember { mutableStateOf(false) }

if (showSheet) {
    ModalBottomSheet(
        onDismissRequest = { showSheet = false },
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = false)
    ) {
        Column(Modifier.padding(horizontal = 16.dp, vertical = 24.dp)) {
            // Sheet content
        }
    }
}
```

### BottomSheetScaffold

For persistent bottom sheets where the sheet is always present at a peek height:

```kotlin
val scaffoldState = rememberBottomSheetScaffoldState(
    bottomSheetState = rememberStandardBottomSheetState(initialValue = SheetValue.PartiallyExpanded)
)

BottomSheetScaffold(
    scaffoldState = scaffoldState,
    sheetPeekHeight = 100.dp,
    sheetContent = { DetailPanel() }
) { innerPadding ->
    VisualizationContent(modifier = Modifier.padding(innerPadding))
}
```

Use `BottomSheetScaffold` for immersive visualization screens where the sheet supplements a full-bleed Canvas or map.

## FAB Variants

| Variant | Size | When |
|---------|------|------|
| `FloatingActionButton` | 56dp | Primary screen-level action |
| `SmallFloatingActionButton` | 40dp | Secondary or compact contexts |
| `LargeFloatingActionButton` | 96dp | Most prominent action (rare) |
| `ExtendedFloatingActionButton` | auto | Action needs a label for clarity |

Place FABs in `Scaffold(floatingActionButton = { })` for correct positioning relative to NavigationBar and Snackbar.

## Cards

### Card (Filled)

Primary content cards with tonal surface:

```kotlin
Card(
    modifier = Modifier.fillMaxWidth(),
    shape = MaterialTheme.shapes.large,
    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerLow)
) { ... }
```

### ElevatedCard

Hero-level cards with shadow + tonal elevation:

```kotlin
ElevatedCard(
    modifier = Modifier.fillMaxWidth(),
    shape = MaterialTheme.shapes.extraLarge,
    elevation = CardDefaults.elevatedCardElevation(defaultElevation = 3.dp)
) { ... }
```

### OutlinedCard

Secondary cards with border:

```kotlin
OutlinedCard(
    modifier = Modifier.fillMaxWidth(),
    shape = MaterialTheme.shapes.medium
) { ... }
```

### Card Interaction

Make cards clickable when the entire surface has one action:

```kotlin
ElevatedCard(onClick = { showDetail() }) { ... }
```

Do not make the entire card clickable when it contains multiple independent actions (buttons, toggles, links).

## Chips

### Chip Types

| Type | When | Example |
|------|------|---------|
| `AssistChip` | Suggest an action | "Open in Maps" |
| `FilterChip` | Toggle a filter on/off | Category filters |
| `InputChip` | Represent user input | Selected contact |
| `SuggestionChip` | Suggest a response | Quick reply options |

### FlowRow for Chip Groups

```kotlin
FlowRow(
    horizontalArrangement = Arrangement.spacedBy(8.dp),
    verticalArrangement = Arrangement.spacedBy(8.dp)
) {
    keywords.forEach { keyword ->
        FilterChip(
            selected = keyword in selectedKeywords,
            onClick = { toggleKeyword(keyword) },
            label = { Text(keyword) }
        )
    }
}
```

## Dialogs

### AlertDialog

```kotlin
AlertDialog(
    onDismissRequest = { dismiss() },
    title = { Text("Confirm action") },
    text = { Text("This will reset your preferences.") },
    confirmButton = { TextButton(onClick = confirm) { Text("Reset") } },
    dismissButton = { TextButton(onClick = dismiss) { Text("Cancel") } }
)
```

### DatePicker / TimePicker

Use `DatePickerDialog` and `TimePickerDialog` for date and time selection. They follow Material 3 patterns automatically.

## Lists and LazyColumn

### ListItem

```kotlin
ListItem(
    headlineContent = { Text("Energy Level") },
    supportingContent = { Text("Today's guided reflection") },
    leadingContent = { Icon(Icons.Rounded.Bolt, contentDescription = null) },
    trailingContent = { Text("High", color = MaterialTheme.colorScheme.primary) }
)
```

### SwipeToDismissBox

```kotlin
SwipeToDismissBox(
    state = dismissState,
    backgroundContent = {
        Box(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.errorContainer)) {
            Icon(Icons.Rounded.Delete, "Delete", modifier = Modifier.align(Alignment.CenterEnd).padding(16.dp))
        }
    }
) {
    ListItem(headlineContent = { Text("Item") })
}
```

## Menus

### DropdownMenu

```kotlin
var expanded by remember { mutableStateOf(false) }

Box {
    IconButton(onClick = { expanded = true }) { Icon(Icons.Rounded.MoreVert, "More options") }
    DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
        DropdownMenuItem(text = { Text("Edit") }, onClick = { edit(); expanded = false })
        DropdownMenuItem(text = { Text("Delete") }, onClick = { delete(); expanded = false })
    }
}
```

### ExposedDropdownMenuBox

For dropdown selection fields that look like text fields:

```kotlin
ExposedDropdownMenuBox(expanded = expanded, onExpandedChange = { expanded = it }) {
    OutlinedTextField(
        value = selectedOption,
        onValueChange = {},
        readOnly = true,
        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded) },
        modifier = Modifier.menuAnchor()
    )
    ExposedDropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
        options.forEach { option ->
            DropdownMenuItem(text = { Text(option) }, onClick = { select(option); expanded = false })
        }
    }
}
```

## Snackbar

```kotlin
val snackbarHostState = remember { SnackbarHostState() }

Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) { ... }

// Show from a coroutine:
scope.launch {
    snackbarHostState.showSnackbar(
        message = "Item deleted",
        actionLabel = "Undo",
        duration = SnackbarDuration.Short
    )
}
```

## Canvas Visualizations

Canvas is the Compose equivalent of HTML5 Canvas or SVG — GPU-accelerated 2D drawing for custom visualizations that standard components cannot express. Use it for data-rich views that need precise geometric control.

### When to Use Canvas

- **Radar/spider charts** — multi-dimensional score polygons
- **Score rings and gauges** — circular progress with gradient sweeps
- **Dense tick marks and grid lines** — degree scales, ruler overlays
- **Custom data plots** — anything requiring precise polar or Cartesian positioning
- **Layered rendering** — elements that must draw in a specific Z-order (background grid -> data -> labels)

### Radar/Spider Chart Pattern

A 5-axis polygon chart for multi-dimensional scores:

```kotlin
Canvas(modifier = Modifier.size(260.dp)) {
    val center = Offset(size.width / 2, size.height / 2)
    val radius = size.minDimension / 2 - 30.dp.toPx()

    // 1. Grid rings at 25/50/75/100%
    listOf(0.25f, 0.5f, 0.75f, 1f).forEach { fraction ->
        drawPath(
            polygonPath(center, radius * fraction, 5),
            color = outlineColor.copy(alpha = 0.15f),
            style = Stroke(width = 1.dp.toPx())
        )
    }

    // 2. Axis lines from center to each vertex
    // 3. Filled data polygon (animated via progress state)
    val dataPath = polygonPath(center, values.mapIndexed { i, v ->
        radius * v * animatedProgress
    }, 5)
    drawPath(dataPath, brush = Brush.radialGradient(...), style = Fill)

    // 4. Data point dots at each vertex
    // 5. Labels at each axis tip (via drawText with TextMeasurer)
}
```

Key techniques:
- Animate the polygon fill with `animateFloatAsState(targetValue = 1f, animationSpec = spring())`
- Overlay invisible tap targets for interactivity — Canvas itself does not handle gestures:

```kotlin
Box {
    Canvas(modifier = Modifier.size(260.dp)) { ... }
    // Invisible tap targets for each axis
    dimensions.forEachIndexed { i, dim ->
        Box(
            modifier = Modifier
                .size(48.dp)
                .offset { vertexOffset(i) }
                .clickable { selectedDimension = dim }
        )
    }
}
```

### Animated Score Ring Pattern

A circular progress indicator with sweep gradient:

```kotlin
val animatedScore by animateFloatAsState(
    targetValue = targetScore,
    animationSpec = spring(dampingRatio = 0.6f, stiffness = 200f)
)

Canvas(modifier = Modifier.size(120.dp)) {
    // Background ring
    drawArc(
        color = backgroundColor,
        startAngle = -90f, sweepAngle = 360f,
        useCenter = false,
        style = Stroke(width = 10.dp.toPx(), cap = StrokeCap.Round)
    )

    // Progress arc with sweep gradient
    drawArc(
        brush = Brush.sweepGradient(
            listOf(accentColor.copy(alpha = 0.6f), accentColor, accentColor.copy(alpha = 0.8f))
        ),
        startAngle = -90f,
        sweepAngle = 360f * (animatedScore / 100f),
        useCenter = false,
        style = Stroke(width = 10.dp.toPx(), cap = StrokeCap.Round)
    )
}

// Center text as overlay
Text(
    "${animatedScore.toInt()}%",
    style = MaterialTheme.typography.headlineMedium,
    modifier = Modifier.align(Alignment.Center)
)
```

Key techniques:
- `Brush.sweepGradient` creates a color sweep along the ring, more premium than flat color
- `spring()` animation with low damping for a satisfying bounce at the end
- Center text as a sibling in a `Box`, not drawn inside Canvas (better accessibility)

### Gradient Score Bars

Dynamic bar color based on value for instant visual categorization:

```kotlin
private fun barBrush(value: Int): Brush = when {
    value >= 75 -> Brush.horizontalGradient(listOf(green.copy(alpha = 0.8f), green))
    value >= 55 -> Brush.horizontalGradient(listOf(gold.copy(alpha = 0.8f), gold))
    else -> Brush.horizontalGradient(listOf(orange.copy(alpha = 0.8f), orange))
}
```

### Semicircular Gauge with Gradient

A traffic-light gauge for ratings/energy levels:

```kotlin
Canvas(modifier = Modifier.size(width = 200.dp, height = 110.dp)) {
    // Smooth red -> yellow -> green gradient arc
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

    // Animated needle
    val needleAngle = 180f - (animatedValue / 100f * 180f)
    val needleRadians = Math.toRadians(needleAngle.toDouble())
    val needleLength = size.width / 2 - 20.dp.toPx()
    val needleEnd = Offset(
        x = center.x + (needleLength * cos(needleRadians)).toFloat(),
        y = size.height - 2.dp.toPx() + (needleLength * sin(needleRadians)).toFloat()
    )
    drawLine(color = onSurface, start = Offset(center.x, size.height - 2.dp.toPx()), end = needleEnd, strokeWidth = 2.dp.toPx())
    drawCircle(color = onSurface, radius = 4.dp.toPx(), center = Offset(center.x, size.height - 2.dp.toPx()))
}
```

Key rules:
- Use `Brush.sweepGradient` for smooth color transitions — never use discrete colored segments (looks blocky)
- Animate the needle with `spring()` for a satisfying sweep
- Show the rating label and description below the gauge
- Map text ratings to numeric values: "excellent" -> 90, "good" -> 65, "challenging" -> 35

### Multi-Layer Canvas (Complex Charts)

For complex visualizations like radial chart wheels, structure as sequential layer functions:

```kotlin
Canvas(modifier = Modifier.fillMaxSize()) {
    drawGridRings(center, radius)       // Background grid
    drawSegmentBand(center, radius)     // 12-segment ring
    drawDividers(center, radius)        // Radial dividers
    drawConnections(center, radius)     // Data connections
    drawCenterCircle(center, radius)    // Center anchor
    drawDataPoints(center, radius)      // Data points
    drawLabels(center, radius, textMeasurer)  // Axis labels via TextMeasurer
}
```

Each layer function is a `DrawScope` extension. This keeps the Canvas body readable while supporting 500+ drawing operations in a single GPU pass.

### Invisible Tap Targets

Canvas does not handle gestures natively. Overlay invisible clickable boxes using `pointerInput` on the Canvas modifier or sibling `Box` elements:

```kotlin
Canvas(
    modifier = Modifier
        .fillMaxSize()
        .pointerInput(Unit) {
            detectTapGestures { offset ->
                val tappedIndex = hitTestDataPoint(offset, dataPoints)
                if (tappedIndex >= 0) selectedIndex = tappedIndex
            }
        }
) { ... }
```

For complex hit testing, compute distance from tap point to each data point and select the nearest within a 24dp threshold.

## Interactive Animations

### AnimatedVisibility

Make sections reveal with entrance animations:

```kotlin
AnimatedVisibility(
    visible = isVisible,
    enter = fadeIn(spring(stiffness = Spring.StiffnessLow)) + expandVertically(),
    exit = fadeOut() + shrinkVertically()
) {
    content()
}
```

Use for:
- Section reveals on data load
- Expandable sections
- Conditional content that appears based on user action

### animateContentSize

For containers whose content changes size:

```kotlin
Column(modifier = Modifier.animateContentSize(spring(stiffness = Spring.StiffnessLow))) {
    Text(title)
    if (expanded) { detailContent() }
}
```

### Spring Animations

Prefer `spring()` over `tween()` for physical, interruptible animations:

```kotlin
val scale by animateFloatAsState(
    targetValue = if (pressed) 0.94f else 1f,
    animationSpec = spring(dampingRatio = 0.6f, stiffness = 500f)
)
```

### Container Transforms (M3 Expressive Motion)

Material 3 Expressive emphasizes shared element transitions and container transforms:

```kotlin
SharedTransitionLayout {
    AnimatedContent(targetState = showDetail) { isDetail ->
        if (isDetail) {
            DetailScreen(
                modifier = Modifier.sharedBounds(
                    sharedContentState = rememberSharedContentState(key = "card-$id"),
                    animatedVisibilityScope = this@AnimatedContent
                )
            )
        } else {
            CardRow(
                modifier = Modifier.sharedBounds(
                    sharedContentState = rememberSharedContentState(key = "card-$id"),
                    animatedVisibilityScope = this@AnimatedContent
                )
            )
        }
    }
}
```

### Press Feedback

Add scale feedback to tappable surfaces:

```kotlin
val interactionSource = remember { MutableInteractionSource() }
val isPressed by interactionSource.collectIsPressedAsState()
val scale by animateFloatAsState(if (isPressed) 0.94f else 1f, spring())

Card(
    modifier = Modifier
        .graphicsLayer { scaleX = scale; scaleY = scale }
        .clickable(interactionSource = interactionSource, indication = ripple()) { onClick() }
) { ... }
```

## Buttons

| Variant | When |
|---------|------|
| `Button` (Filled) | Primary action, highest emphasis |
| `ElevatedButton` | Important but not primary |
| `FilledTonalButton` | Medium emphasis, softer than filled |
| `OutlinedButton` | Secondary action |
| `TextButton` | Lowest emphasis, tertiary actions |
| `IconButton` | Icon-only action (needs `contentDescription`) |

Keep one clearly primary action per screen where possible. Use toolbar actions, menus, and `DropdownMenu` to reduce clutter.

## Search

### SearchBar / DockedSearchBar

```kotlin
var query by remember { mutableStateOf("") }
var active by remember { mutableStateOf(false) }

SearchBar(
    query = query,
    onQueryChange = { query = it },
    onSearch = { performSearch(query); active = false },
    active = active,
    onActiveChange = { active = it },
    leadingIcon = { Icon(Icons.Rounded.Search, contentDescription = null) },
    placeholder = { Text("Search") }
) {
    // Suggestion content when active
}
```

Use `DockedSearchBar` when the search should remain anchored (e.g., below a TopAppBar) rather than expanding full-screen.

## FlowRow (Wrapping Chips)

Compose Foundation provides `FlowRow` for wrapping chip layouts:

```kotlin
FlowRow(
    horizontalArrangement = Arrangement.spacedBy(8.dp),
    verticalArrangement = Arrangement.spacedBy(8.dp)
) {
    keywords.forEach { keyword ->
        SuggestionChip(
            onClick = { select(keyword) },
            label = { Text(keyword) }
        )
    }
}
```

`FlowRow` handles wrapping automatically — no custom `Layout` needed (unlike iOS). Use it for keyword tags, filter chips, and theme pills.

## Immersive Visualization Screen

A third screen archetype alongside dashboards and guidance readings. Used when the visualization IS the experience — chart wheels, 3D scenes, maps.

### Structure

```kotlin
BottomSheetScaffold(
    sheetPeekHeight = 100.dp,
    sheetContent = { DetailPanel(model) }
) { innerPadding ->
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(innerPadding)
    ) {
        // Full-bleed atmospheric background
        AtmosphericBackground()

        Column(modifier = Modifier.fillMaxSize()) {
            // Visualization fills available space
            Box(modifier = Modifier.weight(1f)) {
                Visualization(modifier = Modifier.fillMaxSize())
                // Floating info badge (top-start)
                InfoBadge(modifier = Modifier.align(Alignment.TopStart).padding(16.dp))
            }

            // Controls strip
            ControlsStrip(modifier = Modifier.padding(horizontal = 16.dp))

            // Timeline slider — NOT in sheet
            TimelineSlider(modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp))
        }
    }
}
```

### Key Principles

1. **No card wrappers** — visualization renders edge-to-edge, no Card containers around the main visual
2. **No scroll** — the screen is a fixed viewport with floating overlays, not a scrollable document
3. **Native controls for mode switching** — `SegmentedButton` for primary modes, `DropdownMenu` for overflow. Not custom surface-backed buttons
4. **Temporal controls stay visible** — timeline sliders, scrubbers, and playback controls belong in the main layout, not hidden in sheets
5. **Persistent sheet for detail** — `BottomSheetScaffold` with custom peek height for summary, expanded for full detail
6. **Haptics on meaningful interactions** — use `HapticFeedback` via `LocalHapticFeedback.current` on mode changes, selections, toggles

### Controls Strip Pattern

```kotlin
Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
    // Row 1: Segmented mode picker + overflow menu
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        SingleChoiceSegmentedButtonRow(modifier = Modifier.weight(1f)) {
            modes.forEachIndexed { index, mode ->
                SegmentedButton(
                    selected = selectedMode == mode,
                    onClick = { selectedMode = mode },
                    shape = SegmentedButtonDefaults.itemShape(index, modes.size)
                ) { Text(mode.label) }
            }
        }

        Box {
            IconButton(onClick = { menuExpanded = true }) { Icon(Icons.Rounded.MoreVert, "More") }
            DropdownMenu(expanded = menuExpanded, onDismissRequest = { menuExpanded = false }) { ... }
        }
    }

    // Row 2: Scrollable entity selector
    LazyRow(horizontalArrangement = Arrangement.spacedBy(5.dp)) {
        items(entities) { entity ->
            FilterChip(
                selected = entity == selectedEntity,
                onClick = { selectedEntity = entity },
                label = { Text(entity.symbol) }
            )
        }
    }
}
```

### When to Use

| Screen | Archetype | Why |
|--------|-----------|-----|
| Radial chart wheel | Immersive | Complex Canvas visualization needs full screen |
| 3D scene | Immersive | GLSurfaceView/SceneView needs edge-to-edge depth |
| Map visualization | Immersive | MapView needs full viewport for spatial context |
| Best Days calendar | Dashboard | Grid + terrain are content, not the entire experience |
| Horoscope reading | Guidance | Editorial prose flow, not a single visualization |
| Settings | Dashboard | Standard Material list structure |
