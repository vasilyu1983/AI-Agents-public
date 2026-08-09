# AI-Assisted Design Review

Use this reference when reviewing an iOS screen from screenshots, simulator output, or a running app.

## Review Inputs

Prefer these inputs, in order:

1. A current simulator screenshot
2. A second screenshot from the opposite appearance or a different device size
3. The affected SwiftUI view code
4. Relevant logs or UI snapshot output

## Good Prompt Shapes

- "Audit this SwiftUI screen against current iOS design guidance. Focus on hierarchy, typography, and navigation."
- "Review this screen for Liquid Glass misuse. Call out where standard controls or materials would be more native."
- "Check whether this dashboard feels overloaded on iPhone. Recommend a more native overview structure."
- "Compare these before/after screenshots and tell me whether the layout actually improved."

Avoid:

- "Make it prettier"
- "Review everything"
- "Redesign the app from scratch"

## What to Evaluate

### Hierarchy

- Is the screen’s primary task obvious within a few seconds?
- Is one area clearly dominant, with secondary content demoted?
- Are headings, values, metadata, and actions visually distinct?

### Native Structure

- Is the screen using the right native container: list, tab view, navigation stack, sheet, inspector, or split view?
- Are toolbars, search, and actions placed where iOS users expect them?
- Is any custom navigation solving a problem that standard structure already solves?

### Typography and Color

- Do text styles scale with Dynamic Type?
- Are semantic colors and materials doing the work instead of hardcoded colors?
- Does contrast hold in both appearances?

### Liquid Glass

- Are standard bars and controls carrying most of the glass treatment?
- Do custom materials support context and depth without reducing readability?
- Is the screen using materials intentionally rather than as decoration?

## Review Checklist

### Structure
- Dynamic Type instead of fixed text sizes
- Semantic backgrounds instead of manual light/dark colors
- Native navigation rather than custom tab or segmented app structure
- Cards and sections prioritized instead of equally weighted
- Touch targets and scrolling still usable on smaller phones

### Design Token Audit
- No hardcoded `.padding()` values in screen files — all through named tokens
- No hardcoded `.tracking()` values — all through named tracking tokens
- No raw `UIColor(red:green:blue:)` literals — bridged from the SwiftUI palette
- No hardcoded English strings — all through localization system with fallbacks
- Tab bar and navigation bar appearance references named color constants

### Data Containment
- Data values live in visually bounded containers (cells, rows), not floating in card space
- Label-value pairs use vertical layout (label above value) or flexible widths, not fixed-width columns
- Related data groups use grid cells or stat pills for compact scanning
- Action items (Do/Don't, Best/Avoid) have background containment and colored indicators
- Different content types within one card are separated by thin dividers

### Visual Anchoring
- Data labels include small SF Symbol icons for scannability
- Categorized lists use colored dot indicators for instant visual grouping
- The screen has at least one non-text visual element as a focal point
- Icons are small (10-12pt), same weight as labels, and support meaning (not decoration)

## Evidence Expectations

If the review results in code changes, prefer:

- one screenshot before
- one screenshot after
- the specific SwiftUI files changed
- one short note describing what was fixed and why it is more native
