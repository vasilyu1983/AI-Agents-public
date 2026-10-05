---
name: software-ios-design
description: "Designs and audits native iOS interfaces. Use when reviewing or refining SwiftUI layout, typography, Liquid Glass, navigation, or dashboards on a freshly verified build."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Native iOS Design

Use this skill for visual design decisions and design-focused audits in any native iOS app. Prefer it when the user needs HIG-aligned screen structure, current Apple-native visual defaults, or a screenshot-to-fix loop after a fresh verified build/install/launch. If the request is really about greenfield scaffolding, CLI build loops, scheme selection, or broader iOS implementation workflow, route to `software-ios-native` and return here once the question becomes visual structure or design quality.

## Quick Reference

### Foundations
- Start from the current Apple design system; do not invent custom chrome when a standard control solves it.
- Use system typography, Dynamic Type text styles, semantic colors, SF Symbols, and standard containers first.
- Treat Liquid Glass as the navigation-layer material on iOS 26. Standard chrome (tab bars, toolbars, nav bars, sheets, sidebars) already adopts it. See [references/ios26-liquid-glass.md](references/ios26-liquid-glass.md).
- Tokenize every spacing, tracking, radius, and color in screen files. No magic numbers.
- Enforce a 44 × 44 pt minimum tap target; expand hit area via `.contentShape()` when the visible glyph is smaller.

### Layout & Content
- Contain data in visual boundaries (grid cells, action rows). Never let values float in card space.
- Team default: anchor labels with small SF Symbol icons (10–12 pt as an initial token) and colored indicators; scale with text and retain a non-color cue.
- Prefer bottom sheets (`.sheet` + `.presentationDetents`) for detail over inline expansion.
- Prefer grids over horizontal carousels for any finite set of peer items — grids give spatial context.
- Use `ScrollView > LazyVStack` with `.scrollTransition` for narrative screens; reserve `List(.insetGrouped)` for settings-style hubs.
- Use expandable sections (spring animation) for data-dense reports instead of flat scroll dumps.
- For dense diagrams, charts, maps, and canvases, the visualization is the primary surface. Do not cover it with popups, floating summary cards, or bottom overlays; put summary points below the diagram or in a sheet that leaves the diagram inspectable.
- Do not add a decorative container around a full-bleed or inspection-focused diagram unless the frame improves legibility. A visible card can make the chart feel smaller and harder to inspect.
- Detail/help sheets with peer containers must use full-width rows (`.frame(maxWidth: .infinity, alignment: .leading)`) so short rows do not shrink beside longer rows.

### Interaction & Feedback
- Propagate press feedback at the **shared-component** level, not just individual call sites. Inspect the actual pressed state and hit area of shared rows. `PlainButtonStyle` can provide state feedback; its presence alone does not prove a dead tap.
- Use haptics for meaningful selection or commitment, and inspect the shared component so repeated taps do not produce redundant feedback.
- Centralize Reduce Motion handling for shared transitions, then verify gesture-driven and custom effects individually; a root transaction modifier does not cover every source of motion.
- Add SwiftUI `iOS 17+` polish: `.scrollTransition`, `.sensoryFeedback`, `.symbolEffect`, `.contentTransition(.numericText)`. Standardize scroll reveals into a shared `ViewModifier` (e.g., `.appScrollReveal()`).
- Team default for custom press feedback: `scaleEffect(0.94)` with 100 ms ease-out is a starting token, not an Apple requirement. Retain native feedback when it already conveys the action and respect Reduce Motion.
- For dense diagrams where labels or markers overlap, add native inspection controls before redesigning the geometry: zoom in/out/reset, pan/scroll when zoomed, and semantic filters for visible groups.
- Chart primitives should be tappable when they naturally carry meaning. Nodes, segments, connectors, and markers should open explanations; summary rows alone are not enough for an inspection surface.

### Navigation & Structure
- Merge related screens with segmented pickers to reduce navigation depth.
- Use `.presentationDetents([.medium, .large])` on sheets. Use `.presentationBackgroundInteraction(.enabled(upThrough:))` when the surface behind the sheet should stay interactive at peek height.
- For immersive visualization screens, use the full-bleed pattern: `ZStack { background; visualization; controls; .sheet(persistent) }` — no card wrappers, no scroll.
- For immersive controls, prefer native `Picker(.segmented)` + `Menu` overflow over custom material-backed button strips.
- **Tab bar vs sidebar-adaptive decision**: team starting point is `TabView` for 3–5 peer top-level sections on iPhone; verify fit and task structure. Reach for `NavigationSplitView` (sidebar-adaptive) when (a) the app is iPad/Mac-first and needs a persistent list-detail relationship, (b) there are 6+ top-level destinations that would force a tab-bar "More" overflow, or (c) the same information architecture must scale from iPhone compact width to iPad/Mac without a redesign. `NavigationSplitView` collapses to a stack on iPhone automatically — it is the correct default for adaptive multi-platform apps, not just a Mac/iPad nicety. Do not default to a custom hamburger-drawer sidebar on iPhone; it is not a system pattern and fails discoverability audits.

### Judgment: Following vs Diverging From Platform Convention
- Default posture is to follow the current Apple system pattern (tab bar behavior, sheet detents, glass materials) because it is free accessibility support, free Dynamic Type support, and matches user muscle memory.
- Diverge deliberately, and say so explicitly in the review, when: (a) the system default measurably regresses task completion for this app's core flow (e.g., a collapsing tab bar hides the primary action during the exact scroll state users are in most), (b) the app's category has an established, better-tested convention from a best-in-class competitor (e.g., camera apps keeping shutter controls fixed rather than following generic toolbar collapse), or (c) an accessibility setting is on and the system default itself is the accessibility bug (see Reduce Transparency contrast caveats in [references/ios26-liquid-glass.md](references/ios26-liquid-glass.md)).
- Never diverge silently. A divergence from HIG default must be called out as a deliberate, justified exception in the design review, not presented as if it were the platform default — this is what separates informed craft from "we didn't know the convention."

### Localization
This skill covers the visual audit only. Strings, plurals, catalog parity and the translation pipeline are owned by [software-localisation](../software-localisation/SKILL.md).

- Every user-facing string runs through l10n — including short labels. Test long translations, non-Latin line breaking, and RTL rather than assuming a fixed expansion percentage.
- Verify every localized surface in one long-string locale (de, ru) and one non-Latin locale (ja, ar) before "complete."
- When a screen mixes static UI strings and backend-generated prose, confirm BOTH paths are localized — half-localized screens read as bugged.
- Localized does not mean "key exists." If non-English catalogs contain English fallback text for new keys, the design is not ready for localized review.

### Accessibility
- Every screen must survive Dynamic Type AX5, Reduce Motion, Reduce Transparency, and VoiceOver ON. See [references/ios-accessibility-patterns.md](references/ios-accessibility-patterns.md).
- Every interactive element needs a meaningful `.accessibilityLabel`. Combine multi-element rows with `.accessibilityElement(children: .combine)`.
- Declare support only for accessibility features you actually ship — Accessibility Nutrition Labels are self-declared, not verified by App Store review; reviewers only follow up when a declaration is intentionally misleading or harmful.

## Runtime Proof Gate

- Do not trust screenshots until the installed bundle, build marker, and visible screen are tied to the current build. Reinstall without erasing data first; reset the container only when stale or migrated state is under test.
- If the on-screen UI appears older than source, suspect stale install first. Route to [../software-ios-runtime-debugging/SKILL.md](../software-ios-runtime-debugging/SKILL.md).
- If install or launch is failing, stop design iteration and fix runtime truth before continuing.
- Use XcodeBuildMCP when it is callable and its commands match upstream docs. Otherwise use Apple CLI (`set -o pipefail; xcodebuild ... 2>&1 | xcbeautify`) plus `simctl`; preserve the build exit status. Route packaging or simulator-health issues to the runtime-debugging skill. See [references/xcodebuildmcp-design-loop.md](references/xcodebuildmcp-design-loop.md) for setup and commands.
- When reviewing notification surfaces, verify banners, lock-screen cards, Notification Center, and the post-tap open experience on a physically proven build — simulator screenshots do not prove iPhone notification UX.

## Core Workflow

1. Define the screen's primary job and the one or two pieces of content that must win first attention.
2. Choose the native structure: tab view, navigation stack, list, sheet, inspector, or split view.
3. Apply typography, spacing, and semantic color using system defaults before inventing a custom scale.
4. Adopt Liquid Glass through standard controls and materials, then audit readability in both appearances.
5. Apply the Runtime Proof Gate, capture the target states, inspect, fix, and compare before/after evidence.

For every changed surface, select states by risk rather than presenting one ideal screenshot: populated, loading, empty, error, permission-denied, offline, and destructive-action states where applicable. Cross them with the smallest configuration set that can reveal the change's failure mode: smallest and largest supported width, AX Dynamic Type for layout changes, light/dark plus Increase Contrast or Reduce Transparency for material changes, and VoiceOver focus/announcement order for semantic changes. Record unreachable states and why.

## Feel Bar

Use the Feel Bar as a team review rubric, selecting applicable rows for the screen. The three-failure debt threshold is a team default, not a platform rule; decorative motion or haptics are not required to pass. Pass/fail rows are in [references/ios-craft-and-feel.md → The Feel Bar](references/ios-craft-and-feel.md#the-feel-bar).

## Design Craft Checklist

Before writing or reviewing screen code, check these patterns from [references/design-craft-patterns.md](references/design-craft-patterns.md):

1. **Token discipline**: Every spacing, tracking, radius, color, and repeated font value traces to a named token. No magic numbers in screen files.
2. **Data containment**: Values live in grid cells or action rows with visual boundaries, not floating in card space.
3. **Visual anchoring**: Data labels include SF Symbol icons. Categorized lists use colored dot indicators.
4. **Card hierarchy**: Hero card is visually distinct from secondary cards (larger radius, more padding). Mixed content within one card uses thin dividers.
5. **Data visualization**: Use Canvas for custom charts (radar, wheels, rings); use animated score rings with `.contentTransition(.numericText)`; use gradient score bars. See [references/ios-component-patterns.md](references/ios-component-patterns.md#canvas-based-data-visualizations).
6. **Interactive polish**: Press feedback (shared `ButtonStyle`), haptics (`.sensoryFeedback`), SF Symbol animation (`.symbolEffect(.bounce)`), expandable sections, entrance animations on sheets.
7. **Localization readiness**: All user-facing strings through l10n. Verify keys exist in every locale JSON — silent fallback is the bug that hides until someone switches locale.
8. **Competitor awareness**: Borrow containment and anchoring patterns, not brand identities.
9. **Control density**: When labels wrap on iPhone, switch segmented controls to a horizontally scrollable pill rail; move reset/status actions out of the primary rail.
10. **Readable depth**: For radial or information-dense charts, use subtle parallax, layered depth, and focus states before attempting literal 3D.
11. **Disclosure control**: If repeated polish still feels noisy, lower simultaneous disclosure and introduce mode filters.
12. **Accessibility on interactive elements**: Sheet-triggering buttons need `.accessibilityHint`. Multi-element rows use `.accessibilityElement(children: .combine)`. Navigation chevrons need explicit labels. See [references/ios-accessibility-patterns.md](references/ios-accessibility-patterns.md).
13. **Design verification tests**: Choose snapshots or UI interaction tests by the failure being checked; a label-presence check does not prove accessibility. Use [../qa-testing-ios/SKILL.md](../qa-testing-ios/SKILL.md) for test selection and runtime accessibility audits.

## Design Review Loop

Apply the Runtime Proof Gate before reviewing. Compare before/after screenshots alongside Dynamic Type, appearance, and device-width evidence. If images cannot explain the failure, capture focused layout, appearance, or accessibility logs after launch; use [references/ai-design-review.md](references/ai-design-review.md) for the review prompt and proof shape.

## Route Elsewhere

- Use [../software-ios-native/SKILL.md](../software-ios-native/SKILL.md) for SwiftUI architecture, Observation, concurrency, release gates, or general iOS implementation strategy.
- Use [../software-ios-runtime-debugging/SKILL.md](../software-ios-runtime-debugging/SKILL.md) for stale builds, simulator drift, install failures, or any case where the screenshot may not reflect the current build.
- Use [../software-mobile/SKILL.md](../software-mobile/SKILL.md) for platform-selection or cross-platform decisions.
- Use [../software-ui-ux-design/SKILL.md](../software-ui-ux-design/SKILL.md) for generic product UX patterns that are not iOS-specific.
- Use [../software-accessibility/SKILL.md](../software-accessibility/SKILL.md) for broader accessibility remediation beyond iOS-native visual design defaults.

Widgets, Live Activities, Control Center custom controls, and Lock-screen surfaces are first-class iOS design surfaces. This skill's patterns apply (typography, Dynamic Type, materials, touch targets, accessibility) but the platform constraints differ — widget timelines, size families, interactive affordance rules. Load [references/ios-surfaces-reference.md](references/ios-surfaces-reference.md) for widget rendering modes, `ControlWidget` templates, Live Activity presentations, and Icon Composer decisions. Look up target-OS and SDK availability at the surface before specifying it.

## Navigation

### Foundations

- [references/hig-typography-color.md](references/hig-typography-color.md) — San Francisco, Dynamic Type scale, semantic color, contrast targets, materials, Dark Mode pitfalls
- [references/hig-layout-spacing.md](references/hig-layout-spacing.md) — touch targets, safe areas, spacing scale, thumb zones, keyboard avoidance, layout adaptivity
- [references/ios26-liquid-glass.md](references/ios26-liquid-glass.md) — `glassEffect`, `GlassEffectContainer`, morphing, fallback for pre-iOS 26, accessibility interactions
- [references/ios-accessibility-patterns.md](references/ios-accessibility-patterns.md) — VoiceOver, Dynamic Type, Reduce Motion, Reduce Transparency, Nutrition Labels, haptics

### Patterns

- [references/ios-component-patterns.md](references/ios-component-patterns.md) — tab views, navigation stacks, sheets, cards, lists, toolbars, FlowLayout, immersive visualization
- [references/ios-dashboard-design.md](references/ios-dashboard-design.md) — overview-screen hierarchy, data display patterns, card hierarchy, dual-view dashboards
- [references/visual-guidance-patterns.md](references/visual-guidance-patterns.md) — narrative/guidance screen archetype, Canvas visualizations, opportunity framing, progress rings
- [references/design-craft-patterns.md](references/design-craft-patterns.md) — token discipline, data containment, visual anchoring, dark theme, competitor analysis
- [references/motion-tokens.md](references/motion-tokens.md) — motion intents, curves, durations, Reduce Motion handling
- [references/swiftui-design-antipatterns.md](references/swiftui-design-antipatterns.md) — state/identity, navigation, layout, color/Dark Mode, animations, controls, sheets, data display anti-patterns
- [references/ios-craft-and-feel.md](references/ios-craft-and-feel.md) — spring physics, haptic choreography, SF Symbol craft, transition continuity, editorial number polish, Live Activities
- [references/ios-pro-craft-scenarios.md](references/ios-pro-craft-scenarios.md) — onboarding, IAP/paywall, settings, search, photo viewer, media player, focused-input, daily-habit, camera, charts, inbox, App Intents
- [references/ios-surfaces-reference.md](references/ios-surfaces-reference.md) — Swift Charts vs Canvas, Dynamic Island stages, widgets, App Clips, App Intents, Transferable, ShareLink, NavigationSplitView, swipe actions, Live Activities, multitasking
- [references/ios-shipping-antipatterns.md](references/ios-shipping-antipatterns.md) — permission and paywall UX, toolbar density, destructive actions, navigation gestures, and screenshot accuracy

### Review & Tooling

- [references/app-review-guidelines-map.md](references/app-review-guidelines-map.md) — design-facing policy checks for moderation UI, privacy, purchases, screenshots, and concept differentiation
- [references/ai-design-review.md](references/ai-design-review.md) — screenshot prompts, review checklists, proof expectations
- [references/xcodebuildmcp-design-loop.md](references/xcodebuildmcp-design-loop.md) — current XcodeBuildMCP setup and simulator verification flow
- [data/sources.json](data/sources.json) — primary Apple sources and freshness-check targets

### Scripts

Optional helpers for a proven-build design loop. If the project uses a `Makefile`, `make` can replace the individual scripts. If the app cannot build/install/launch cleanly, route to [../software-ios-runtime-debugging/SKILL.md](../software-ios-runtime-debugging/SKILL.md).

- [scripts/bootstrap-xcodebuildmcp.sh](scripts/bootstrap-xcodebuildmcp.sh) — verify CLI availability and scaffold a repo-local `.xcodebuildmcp/config.yaml`
- [scripts/build-ios.sh](scripts/build-ios.sh) — compile-only simulator build wrapper
- [scripts/run-ios.sh](scripts/run-ios.sh) — build-and-run wrapper for iterative design work
- [scripts/test-ios.sh](scripts/test-ios.sh) — simulator test wrapper with optional extra args
- [scripts/capture-screenshot.sh](scripts/capture-screenshot.sh) — save a simulator screenshot for review loops

## Anti-Patterns

For the full anti-pattern catalog — SwiftUI state/identity, navigation, layout, color/Dark Mode, animations, controls, sheets, data display, Canvas, and runtime footguns — see [references/swiftui-design-antipatterns.md](references/swiftui-design-antipatterns.md).

## Verification Gate

| Check | Pass condition | Fail condition |
|---|---|---|
| Standard structure | Recommendation maps to a standard iOS pattern | Custom pattern used without justification |
| Screenshot origin | Freshly installed and launched build | Screenshot from a prior install or simulator session not tied to current build |
| Typography | Dynamic Type text styles throughout | Fixed-size design tokens |
| Color and materials | Contrast and hierarchy preserved in light and dark mode | Material or color breaks in one appearance |
| Touch targets | ≥ 44 × 44 pt; `.contentShape()` used where glyph is smaller | Target below minimum; dead taps on tappable rows |
| Notification surface | Verified on real iPhone in correct APNs environment | Simulator-only screenshots for notification UX |
| Dashboard heuristics | Labeled as team default, not platform rule | Presented as HIG requirement without citation |
| XcodeBuildMCP guidance | Verified against upstream docs | Repeated from memory or prior session |
| System surfaces | Widget rendering modes, controls, and icon appearances verified for target OS | Only a full-color in-app screenshot supplied |

## Platform Lookup

At structure selection, read [Apple Developer Releases](https://developer.apple.com/news/releases/) and the target component's HIG page from [data/sources.json](data/sources.json). Design for the shipped target OS; separately test the minimum deployment target. At symbol, icon, or system-surface selection, use the lookup in its reference rather than inferring availability from a tool release. At runtime verification, check upstream XcodeBuildMCP command/configuration docs before invoking the wrappers.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
