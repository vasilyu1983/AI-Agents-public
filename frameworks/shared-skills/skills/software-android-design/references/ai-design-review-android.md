# AI-Assisted Design Review — Android

## Table of Contents

- [Review Inputs](#review-inputs)
- [Good Prompt Shapes](#good-prompt-shapes)
- [What to Evaluate](#what-to-evaluate)
- [Material Compliance Checks](#material-compliance-checks)
- [Review Checklist](#review-checklist)
- [Evidence Expectations](#evidence-expectations)

Use this reference when reviewing an Android screen from emulator screenshots, Layout Inspector output, or a running app.

## Review Inputs

Prefer these inputs, in order:

1. A current emulator screenshot (via `adb exec-out screencap -p`)
2. A second screenshot from the opposite theme or a different WindowSizeClass
3. The affected Compose code (screen-level `@Composable` functions)
4. Layout Inspector XML or uiautomator dump output

## Good Prompt Shapes

- "Audit this Compose screen against current Material 3 design guidance. Focus on hierarchy, typography, and navigation."
- "Review this screen for incorrect color role usage. Call out where `MaterialTheme.colorScheme` roles would be more correct."
- "Check whether this dashboard feels overloaded on a compact phone. Recommend a more Material structure."
- "Compare these before/after screenshots and tell me whether the layout actually improved."

Avoid:

- "Make it prettier"
- "Review everything"
- "Redesign the app from scratch"

## What to Evaluate

### Hierarchy

- Is the screen's primary task obvious within a few seconds?
- Is one area clearly dominant, with secondary content demoted?
- Are headings, values, metadata, and actions visually distinct?

### Material Structure

- Is the screen using the right Material structure: `NavigationBar`, `NavigationRail`, `Scaffold`, `TopAppBar`, `ModalBottomSheet`, `ListDetailPaneScaffold`?
- Are toolbar actions, FABs, and menus placed where Android users expect them?
- Is any custom navigation solving a problem that standard Material structure already solves?

### Typography and Color

- Does the type scale use `MaterialTheme.typography` roles?
- Are `MaterialTheme.colorScheme` roles doing the work instead of hardcoded `Color()` values?
- Does contrast hold in both light and dark themes?

### Shape and Elevation

- Are shapes from `MaterialTheme.shapes` or at least consistent?
- Is elevation expressed through tonal surfaces rather than only shadow?
- Are interactive surfaces using ripple indication?

### Adaptive Behavior

- Does the layout adapt to medium and expanded WindowSizeClass?
- Is `NavigationSuiteScaffold` or manual switching used for navigation?
- Is content constrained to a readable width on expanded screens?

## Material Compliance Checks

| Check | What to verify |
|-------|---------------|
| Color roles | `primary`, `surface`, `onSurface`, `outline` used correctly — not hardcoded hex |
| Type scale | Roles from `MaterialTheme.typography` — not raw `TextStyle(fontSize = N.sp)` |
| Shape tokens | `MaterialTheme.shapes` scale — not ad-hoc `RoundedCornerShape(N.dp)` |
| Elevation | `tonalElevation` for surface hierarchy — not shadow-only depth |
| Touch targets | All interactive elements >= 48dp |
| Dynamic color | Enabled on 12+ with static seed fallback |
| WindowSizeClass | Navigation and layout adapt across compact / medium / expanded |

## Review Checklist

### Structure
- Material type scale instead of fixed text sizes
- `MaterialTheme.colorScheme` roles instead of manual light/dark colors
- Standard Material navigation rather than custom tab or segmented app structure
- Cards and sections prioritized instead of equally weighted
- Touch targets and scrolling still usable on compact phones
- Edge-to-edge with proper WindowInsets consumption

### Design Token Audit
- No hardcoded `.padding(N.dp)` magic numbers in screen files — all through named tokens
- No hardcoded `Color(0xFF...)` literals — all through `MaterialTheme.colorScheme` or named palette
- No raw `TextStyle(fontSize, fontWeight)` outside the Material type scale — use `MaterialTheme.typography`
- No hardcoded English strings — all through `strings.xml` with proper plurals
- `TopAppBar`, `NavigationBar` colors come from Material defaults, not manual overrides

### Data Containment
- Data values live in visually bounded containers (Cards, `ListItem`, grid cells), not floating in `Column` space
- Label-value pairs use vertical layout (label above value) or flexible widths, not fixed-width columns
- Related data groups use grid cells or stat surfaces for compact scanning
- Action items (Do/Avoid, Best/Skip) have surface containment and colored indicators
- Different content types within one card are separated by `HorizontalDivider`

### Visual Anchoring
- Data labels include small Material icons (18-20dp) for scannability
- Categorized lists use colored dot indicators (6dp Canvas circles) for instant visual grouping
- The screen has at least one non-text visual element as a focal point
- Icons are small, same visual weight as labels, and support meaning (not decoration)

## Evidence Expectations

If the review results in code changes, prefer:

- one screenshot before
- one screenshot after
- the specific Compose files changed
- one short note describing what was fixed and why it is more Material-native
